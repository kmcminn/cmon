from zope.interface import implements
from Products.Zuul.infos import ProxyProperty
from Products.Zuul.infos.template import RRDDataSourceInfo
from ZenPacks.core.Cmon.interfaces import ICmonDataSourceInfo

class CmonDataSourceInfo(RRDDataSourceInfo):
    implements(ICmonDataSourceInfo)
    url = ProxyProperty('url')
    cycletime = ProxyProperty('cycletime')
    timeout = ProxyProperty('timeout')
    proxy = ProxyProperty('proxy')
    agent = ProxyProperty('agent')
    log = ProxyProperty('log')
    hostheader = ProxyProperty('hostheader')

    name_1 = ProxyProperty('name_1')
    regex_1 = ProxyProperty('regex_1')
    xpath_1 = ProxyProperty('xpath_1')

    name_2 = ProxyProperty('name_2')
    regex_2 = ProxyProperty('regex_2')
    xpath_2 = ProxyProperty('xpath_2')

    name_3 = ProxyProperty('name_3')
    regex_3 = ProxyProperty('regex_3')
    xpath_3 = ProxyProperty('xpath_3')

    name_4 = ProxyProperty('name_4')
    regex_4 = ProxyProperty('regex_4')
    xpath_4 = ProxyProperty('xpath_4')

    name_5 = ProxyProperty('name_5')
    regex_5 = ProxyProperty('regex_5')
    xpath_5 = ProxyProperty('xpath_5')

    name_6 = ProxyProperty('name_6')
    regex_6 = ProxyProperty('regex_6')
    xpath_6 = ProxyProperty('xpath_6')

    name_7 = ProxyProperty('name_7')
    regex_7 = ProxyProperty('regex_7')
    xpath_7 = ProxyProperty('xpath_7')

    name_8 = ProxyProperty('name_8')
    regex_8 = ProxyProperty('regex_8')
    xpath_8 = ProxyProperty('xpath_8')

    name_9 = ProxyProperty('name_9')
    regex_9 = ProxyProperty('regex_9')
    xpath_9 = ProxyProperty('xpath_9')

    name_10 = ProxyProperty('name_10')
    regex_10 = ProxyProperty('regex_10')
    xpath_10 = ProxyProperty('xpath_10')

    name_11 = ProxyProperty('name_11')
    regex_11 = ProxyProperty('regex_11')
    xpath_11 = ProxyProperty('xpath_11')

    name_12 = ProxyProperty('name_12')
    regex_12 = ProxyProperty('regex_12')
    xpath_12 = ProxyProperty('xpath_12')

    name_13 = ProxyProperty('name_13')
    regex_13 = ProxyProperty('regex_13')
    xpath_13 = ProxyProperty('xpath_13')

    name_14 = ProxyProperty('name_14')
    regex_14 = ProxyProperty('regex_14')
    xpath_14 = ProxyProperty('xpath_14')

    name_15 = ProxyProperty('name_15')
    regex_15 = ProxyProperty('regex_15')
    xpath_15 = ProxyProperty('xpath_15')

    name_16 = ProxyProperty('name_16')
    regex_16 = ProxyProperty('regex_16')
    xpath_16 = ProxyProperty('xpath_16')

    name_17 = ProxyProperty('name_17')
    regex_17 = ProxyProperty('regex_17')
    xpath_17 = ProxyProperty('xpath_17')

    name_18 = ProxyProperty('name_18')
    regex_18 = ProxyProperty('regex_18')
    xpath_18 = ProxyProperty('xpath_18')

    name_19 = ProxyProperty('name_19')
    regex_19 = ProxyProperty('regex_19')
    xpath_19 = ProxyProperty('xpath_19')

    name_20 = ProxyProperty('name_20')
    regex_20 = ProxyProperty('regex_20')
    xpath_20 = ProxyProperty('xpath_20')



    @property
    def testable(self):
        """
        We can NOT test this datsource against a specific device
        """
        return False
