import os
import time
import traceback
from sets import Set

import Globals
from Products.ZenRRD.RRDDaemon import RRDDaemon as Base
from Products.ZenRRD.RRDUtil import RRDUtil
from Products.ZenUtils.Driver import drive
from Products.ZenRRD.Thresholds import Thresholds
from Products.ZenModel.RRDDataPoint import SEPARATOR
from Products.ZenEvents import Event
from Products.ZenEvents.MySqlSendEvent import MySqlSendEventMixin as eventSend

from twisted.python import failure
from twisted.internet import defer, reactor, error, threads

from ZenPacks.core.Cmon.CmonConfigService import CmonConfig

ReactorException = None
CmonException = None
CmonImportException = None

try:
    from ZenPacks.core.Cmon.libexec.CmonUrlCheck import parseWithConfig
except:
    CmonImportException = traceback.format_exc()
    pass


Status_Web = '/Status/Web'

DEFAULT_HEARTBEAT_TIME = 500



class ParseCmonTask:
    def __init__(self, cfg):
        self.cfg = cfg

    def startCheck(self):
        global ReactorException
        self.d = defer.Deferred()
        try:
            reactor.callLater(0, self.doCheck)
        except:
            ReactorException = traceback.format_exc()
            pass
        return self.d

    def doCheck(self):
        global CmonException
        try:
            self.d.callback((self.cfg, parseWithConfig(self.cfg, start=1)))
        except:
            CmonException = traceback.format_exc()
            pass


class cmonperf(Base):
    initialServices = Base.initialServices + [
        'ZenPacks.core.Cmon.CmonConfigService'
    ]

    def __init__(self):
        Base.__init__(self, 'cmonperf')
        self.config = []
        self.thresholds = Thresholds()
        try:
            os.nice(self.options.nice)
        except:
            self.log.info("Unable to nice.")
            self.sendEvent(dict(
                device='cmondaemon',
                severity='5',
                summary='CMON daemon init exception',
                message='Unable to nice() myself',
                component='cmonperf'
            ))

    def remote_deleteDevice(self, doomed):
        self.log.debug("zenhub requested us to delete"
                       " device %s -- ignoring" % doomed)

    def remote_updateDeviceConfig(self, config):
        self.log.debug("Configuration device update from zenhub")
        self.updateConfig(config)

    def updateConfig(self, newconfig):
        if isinstance(newconfig, failure.Failure):
            self.log.error("Received configuration failure (%s) from zenhub" % (
                           str(newconfig)))
            return
        self.log.debug("Received %d configuration updates from zenhub" % (
                       len(newconfig)))
        orig = {}
        for obj in self.config:
            orig[obj.key()] = obj

        for obj in newconfig:
            deviceName = obj.key()[0]
            if hasattr(self.options, 'device') and \
                self.options.device != '' and \
                self.options.device != deviceName:
                self.log.debug("Skipping update for %s as we're" \
                               " only looking for %s updates" % (
                               deviceName, self.options.device))
                continue

            if hasattr(self.options, 'url') and \
                self.options.url != '' and \
                self.options.url != obj.url:
                    self.log.debug("Skipping %s as we're only looking for %s" % (obj.url, self.options.url))
                    continue

            self.log.debug("Configuration object for %s/%s found" % obj.key())
            old = orig.get(obj.key(), None)
            if old is None:
                obj.ignoreIds = Set()
                self.config.append(obj)
            else:
                old.update(obj)
            self.log.debug("CONFIG: %s" % obj.url)
            self.thresholds.updateList(obj.thresholds)

    def processDevices(self, result = None):

        if CmonImportException is not None:
            self.sendEvent(dict(
                device='cmondaemon',
                severity='5',
                summary='CMON Exception at parse method import',
                message=CmonImportException,
                eventClass=Status_Web,
                component='cmonperf'
            ))  
                
        if CmonException is not None:
            self.sendEvent(dict(
                device='cmondaemon',
                severity='5',
                summary='CMON Exception while parsing',
                message=CmonException,
                eventClass=Status_Web,
                component='cmonperf'
            ))

        if ReactorException is not None:
            self.sendEvent(dict(
                device='cmondaemon',
                severity='5',
                summary='CMON Reactor Exception',
                message=ReactorException,
                eventClass=Status_Web,
                component='cmonperf'
            ))

        if isinstance(result, failure.Failure):
            if not isinstance(result.value, error.TimeoutError):
                self.log.error(str(result.value))

        reactor.callLater(self.options.cycletime, self.processDevices)
        for cfg in self.config:
            def inner(driver):
                cfg.lastRun = time.time()
                try:
                    self.log.info("Polling %s", cfg.url)
                    task = ParseCmonTask(cfg)
                    yield task.startCheck()
                    results = driver.next()
                    self.postResults(results)
                except Exception, ex:
                    self.log.exception(ex)
                    dsdev, ds = cfg.key()
                    self.sendEvent(dict(
                        device="cmondaemon",
                        component='cmonperf',
                        severity='5',
                        summary="CMON Exception while while parsing " + cfg.device,
                        message=traceback.format_exc(),
                        eventGroup="cmon",
                        dataSource=ds,
                        eventClass=Status_Web,
                    ))
                    pass

            if cfg.lastRun + cfg.cycletime < time.time():
                d = drive(inner)
            else:
                self.log.debug("Skipping %s because lastRun(%s) + cycletime(%s) > now(%s)" % (cfg.device, cfg.lastRun, cfg.cycletime, time.time()))

    def postResults(self, results):
        (cfg, results) = results
        self.log.info("Got results for %s" % cfg.url)
        self.log.debug("Results for %s: %s" % (cfg.url, results))
        for name, value in results:
            dpName = '%s%c%s' % (cfg.name, SEPARATOR, name)
            try:
                rrdConfig = cfg.rrdConfig[dpName]
            except:
                self.log.debug("Got an unexpected dp back: %s" % dpName)
                continue
            path = os.path.join('Devices', cfg.device, dpName)
            value = self.rrd.save(path, value, rrdConfig.rrdtype,
                                  rrdConfig.command, cfg.cycletime,
                                  rrdConfig.min, rrdConfig.max)

            for evt in self.thresholds.check(path, time.time(), value):
                self.sendThresholdEvent(**evt)

        dsdev, ds = cfg.key()
        self.sendEvent(dict(
            device=cfg.device, component='cmonperf', severity=Event.Clear,
            summary="Successfully completed transaction",
            eventGroup="", dataSource=ds, eventClass=Status_Web,
        ))


    def heartbeat(self, *unused):
        Base.heartbeat(self)
        reactor.callLater(self.heartbeatTimeout / 3, self.heartbeat)


    def connected(self):
        self.log.debug("Gathering information from zenhub")
        Base.heartbeat(self)
        def inner(driver):
            try:
                now = time.time()

                self.log.info("Fetching default RRDCreateCommand")
                yield self.model().callRemote('getDefaultRRDCreateCommand')
                createCommand = driver.next()
                self.rrd = RRDUtil(createCommand, DEFAULT_HEARTBEAT_TIME)

                self.log.info("Getting Threshold Classes")
                yield self.model().callRemote('getThresholdClasses')
                self.remote_updateThresholdClasses(driver.next())

                self.log.info("Retrieving configuration from zenhub...")
                yield self.model().callRemote('getConfig')
                self.updateConfig(driver.next())

                self.log.info("Starting CMON tests")
                self.processDevices()
                driver.next()

                self.log.info("Processed %d CMON checks in %0.2f seconds",
                              len(self.config),
                              time.time() - now)
            except Exception, ex:
                self.log.exception(ex)
                self.sendEvent(dict(
                    device='cmondaemon',
                    severity='5',
                    summary='CMON Inner Driver Exception',
                    message=traceback.format_exc(),
                    eventClass=Status_Web,
                    component='cmonperf'
                ))
                pass
        d = drive(inner)
        d.addCallbacks(self.heartbeat, self.errorStop)

    def buildOptions(self):
        Base.buildOptions(self)
        self.parser.add_option('--cycletime', dest='cycletime',
            type='int', default=30,
            help="Cycle interval in seconds.")
        self.parser.add_option("--nice", dest="nice", type="int", default=-4, help="nice priority of process.")
        self.parser.add_option("--url", dest="url", type="string", help="Restring URLs to this", default="")

if __name__ == '__main__':
    cmon = cmonperf()
    cmon.run()
