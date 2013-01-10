import Globals

from Products.ZenHub.services.PerformanceConfig import PerformanceConfig

Status_Web = '/Status/Web'

from Products.ZenUtils.ZenTales import talesEval

from twisted.spread import pb
class RRDConfig(pb.Copyable, pb.RemoteCopy):
    def __init__(self, dp):
        self.command = dp.createCmd
        self.min = dp.rrdmin
        self.max = dp.rrdmax
        self.rrdtype = dp.rrdtype

pb.setUnjellyableForClass(RRDConfig, RRDConfig)
    

class CmonConfig(pb.Copyable, pb.RemoteCopy):
    "Carries the config from ZenHub over to the cmonperf collector"

    lastRun = 0

    def __init__(self, device, template, datasource):
        self.device = device.id
        self.name = datasource.id
        self.copyProperties(device, datasource)
        self.rrdConfig = {}
        for dp in datasource.datapoints():
            self.rrdConfig[dp.name()] = RRDConfig(dp)
        self.thresholds = []
        for thresh in template.thresholds():
            self.thresholds.append(thresh.createThresholdInstance(device))


    def copyProperties(self, device, ds):
        for prop in [p['id'] for p in ds._properties]:
            try:
                value = getattr(ds, prop)
            except AttributeError:
                continue
            if str(value).find('$') >= 0:
                value = talesEval('string:%s' % (value,), device, {'dev': device})
            setattr(self, prop, value)

    def key(self):
        return self.device, self.name

    def update(self, value):
        self.__dict__.update(value.__dict__)

pb.setUnjellyableForClass(CmonConfig, CmonConfig)

class CmonConfigService(PerformanceConfig):
    """ZenHub service for getting cmonperf configuration
    from the object database"""

    def getDeviceConfig(self, device):
        result = []
        for template in device.getRRDTemplates():
            for ds in template.getRRDDataSources():
                if ds.sourcetype == 'Cmon' and ds.enabled:
                    result.append(CmonConfig(device, template, ds))
        return result


    def sendDeviceConfig(self, listener, config):
        return listener.callRemote('updateDeviceConfig', config)


    def remote_getConfig(self):
        result = []
        for d in self.config.devices():
            result.extend(self.getDeviceConfig(d.primaryAq()))
        return result


    def remote_getStatus(self):
        where = "eventClass = '%s'" % (Status_Web)
        issues = self.zem.getDeviceIssues(where=where, severity=3)
        return [d
                for d, count, total in issues
                if getattr(self.config.devices, d, None)]

if __name__ == '__main__':
    from Products.ZenUtils.ZCmdBase import ZCmdBase
    dmd = ZCmdBase().dmd
    c = CmonConfigService(dmd, 'localhost')
    print c.remote_getStatus()
    print [cfg.url for cfg in c.remote_getConfig()]
