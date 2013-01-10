__doc__='''CmonDataSource.py

Defines a datasource for CmonUrlCheck.py
'''

from Globals import InitializeClass
import Products.ZenModel.RRDDataSource as RRDDataSource
from Products.ZenModel.ZenPackPersistence import ZenPackPersistence
from AccessControl import ClassSecurityInfo, Permissions
from Products.ZenUtils.ZenTales import talesCompile, getEngine

class CmonDataSource(ZenPackPersistence, RRDDataSource.RRDDataSource):
  """Simple datasource"""

  ZENPACKID = 'ZenPacks.core.Cmon'

  sourcetypes = ('Cmon',)
  sourcetype = 'Cmon'
  eventClass = '/Status/Web'
  component = 'CmonUrlCheck.py'

  # default datapoints we will create
  defaultDataPoints = ('http_code', 'time_total', 'time_dns',
    'time_connect', 'size_download', 'curl_error',)

  url = 'http://${dev/id}/'
  proxy = ''
  agent = ''
  hostheader = ''
  log = ''
  timeout = 10

  # Zope PropertyManager forces us to enumerate the following
  regex_1 = ''; xpath_1 = ''; name_1 = ''; regex_2 = ''; xpath_2 = ''; name_2 = ''
  regex_3 = ''; xpath_3 = ''; name_3 = ''; regex_4 = ''; xpath_4 = ''; name_4 = ''
  regex_5 = ''; xpath_5 = ''; name_5 = ''; regex_6 = ''; xpath_6 = ''; name_6 = ''
  regex_7 = ''; xpath_7 = ''; name_7 = ''; regex_8 = ''; xpath_8 = ''; name_8 = ''
  regex_9 = ''; xpath_9 = ''; name_9 = ''; regex_10 = ''; xpath_10 = ''; name_10 = ''
  regex_11 = ''; xpath_11 = ''; name_11 = ''; regex_12 = ''; xpath_12 = ''; name_12 = ''
  regex_13 = ''; xpath_13 = ''; name_13 = ''; regex_14 = ''; xpath_14 = ''; name_14 = ''
  regex_15 = ''; xpath_15 = ''; name_15 = ''; regex_16 = ''; xpath_16 = ''; name_16 = ''
  regex_17 = ''; xpath_17 = ''; name_17 = ''; regex_18 = ''; xpath_18 = ''; name_18 = ''
  regex_19 = ''; xpath_19 = ''; name_19 = ''; regex_20 = ''; xpath_20 = ''; name_20 = ''

  # _properties defines UI-editable values and their types
  _properties = RRDDataSource.RRDDataSource._properties + (
    {'id':'url', 'type':'string', 'mode':'w'},
    {'id':'agent', 'type':'string', 'mode':'w'},
    {'id':'hostheader', 'type':'string', 'mode':'w'},
    {'id':'proxy', 'type':'string', 'mode':'w'},
    {'id':'log', 'type':'string', 'mode':'w'},
    {'id':'timeout', 'type':'int', 'mode':'w'},
    )
  # concatenate regex_n, xpath_n, name_n dictionaries to _properties tuple
  _properties = _properties + tuple(
    [({'id':s+'_'+str(n), 'type':'string', 'mode':'w'}) for n in range(21) for s in ("regex", "xpath", "name")],
    )
    
  _relations = RRDDataSource.RRDDataSource._relations + (
    )

  # deprecated in zenoss 3 in exchange for zcml, other parts of ui still use this syntax though
  factory_type_information = (
    {
      'immediate_view' : 'editCmonDataSource',
      'actions'        :
      (
          { 'id'            : 'edit',
            'name'          : 'Data Source',
            'action'        : 'editCmonDataSource',
            'permissions'   : ( Permissions.view, ),
          },
      )
    },
  )

  security = ClassSecurityInfo()

  def __init__(self, id, title=None, buildRelations=True):
    RRDDataSource.RRDDataSource.__init__(self, id, title, buildRelations)
    self.addDataPoints()

  def getDescription(self):
    if self.sourcetype == 'Cmon':
      # tbd return content match conditions also?
      return self.url
    return RRDDataSource.RRDDataSource.getDescription(self)

  def useZenCommand(self):
    return True

  def getCommand(self, context):
    parts = ['CmonUrlCheck.py']
    parts.append('--url="%s"' % self.url)
    if self.timeout:
      parts.append('--timeout="%s"' % self.timeout)
    if len ( self.agent ) > 1:
      parts.append('--agent="%s"' % self.agent)
    if self.proxy:
      parts.append('--proxy="%s"' % self.proxy)
    if self.hostheader:
      parts.append('--hostheader="%s"' % self.hostheader) 
    if self.log:
      parts.append('--log="%s"' % self.log)

    # see above setattr comments for clarification of this bit
    for (r, x, n, num) in ((self.regex_1, self.xpath_1, self.name_1, 1),
        (self.regex_2, self.xpath_2, self.name_2, 2),
        (self.regex_3, self.xpath_3, self.name_3, 3),
        (self.regex_4, self.xpath_4, self.name_4, 4),
        (self.regex_5, self.xpath_5, self.name_5, 5),
        (self.regex_6, self.xpath_6, self.name_6, 6),
        (self.regex_7, self.xpath_7, self.name_7, 7),
        (self.regex_8, self.xpath_8, self.name_8, 8),
        (self.regex_9, self.xpath_9, self.name_9, 9),
        (self.regex_10, self.xpath_10, self.name_10, 10),
        (self.regex_11, self.xpath_11, self.name_11, 11),
        (self.regex_12, self.xpath_12, self.name_12, 12),
        (self.regex_13, self.xpath_13, self.name_13, 13),
        (self.regex_14, self.xpath_14, self.name_14, 14),
        (self.regex_15, self.xpath_15, self.name_15, 15),
        (self.regex_16, self.xpath_16, self.name_16, 16),
        (self.regex_17, self.xpath_17, self.name_17, 17),
        (self.regex_18, self.xpath_18, self.name_18, 18),
        (self.regex_19, self.xpath_19, self.name_19, 19),
        (self.regex_20, self.xpath_20, self.name_20, 20)):
      if r is not None and r != '':
        parts.append('--regex-%s="%s"' % (num, r))
      elif x is not None and x != '':
        parts.append('--xpath-%s="%s"' % (num, x))
      if n is not None and n != '':
        parts.append('--name-%s="%s"' % (num, n))

    cmd = ' '.join(parts)
    cmd = RRDDataSource.RRDDataSource.getCommand(self, context, cmd)
    return cmd

  def checkCommandPrefix(self, context, cmd):
    zp = self.getZenPack(context)
    return zp.path('libexec', cmd)

  """ deprecated in zenoss 3 """
  def zmanage_editProperties(self, REQUEST=None):
    """ required docstring """
    # this does not get called in zenoss 3.0+
    if REQUEST:
      self.addDataPoints() 
      #if not REQUEST.form.get('eventClass', None):
        #REQUEST.form['eventClass'] = self.__class__.eventClass
    return RRDDataSource.RRDDataSource.zmanage_editProperties(self, REQUEST)

  # add datapoints method adds only when optional datasource options are set
  def addDataPoints(self):
    for d in self.defaultDataPoints:
      # hasattr check does nothing since this is only called upon datasource creation
      if not hasattr(self.datapoints, d):
        self.manage_addRRDDataPoint(d)
  
  def updateDataPoints(self, dict):
    """ 
      update datapoints is called from Zuul/facades/templatefacade.py
      we try/except the method from there and then check it closely here
    """
    if dict:
      for k in dict.keys():
        if "name" in str(k):
          if not hasattr(self.datapoints, dict[k]):
            self.manage_addRRDDataPoint(str(dict[k]))
          if not hasattr(self.datapoints, dict[k] + "_match_failed"):
            self.manage_addRRDDataPoint(str(dict[k]) + "_match_failed")
    

InitializeClass(CmonDataSource)
