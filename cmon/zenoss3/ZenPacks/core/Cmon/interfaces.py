from Products.Zuul.interfaces import IRRDDataSourceInfo
from Products.Zuul.form import schema
from Products.Zuul.utils import ZuulMessageFactory as _t


class ICmonDataSourceInfo(IRRDDataSourceInfo):
    url = schema.Text(title=_t(u"URL"), group=0)
    cycletime = schema.Int(title=_t(u'Cycle Time (seconds)'), group=0)
    timeout = schema.Int(title=_t(u'Timeout (seconds)'), group=0)
    proxy = schema.Text(title=_t(u'Proxy Host'), group=0)
    agent = schema.Text(title=_t(u'Agent Key'), group=0)
    log = schema.Text(title=_t(u'Log Path'), group=0)
    hostheader = schema.Text(title=_t(u'Host Header'), group=0)

    name_1 = schema.Text(title=_t(u"Name"), group=1)
    regex_1 = schema.Text(title=_t(u"Regex"), group=1)
    xpath_1 = schema.Text(title=_t(u"Xpath"), group=1)

    name_2 = schema.Text(title=_t(u"Name"), group=2)
    regex_2 = schema.Text(title=_t(u"Regex"), group=2)
    xpath_2 = schema.Text(title=_t(u"Xpath"), group=2)
    
    name_3 = schema.Text(title=_t(u"Name"), group=3)
    regex_3 = schema.Text(title=_t(u"Regex"), group=3)
    xpath_3 = schema.Text(title=_t(u"Xpath"), group=3)

    name_4 = schema.Text(title=_t(u"Name"), group=4)
    regex_4 = schema.Text(title=_t(u"Regex"), group=4)
    xpath_4 = schema.Text(title=_t(u"Xpath"), group=4)

    name_5 = schema.Text(title=_t(u"Name"), group=5)
    regex_5 = schema.Text(title=_t(u"Regex 5"), group=5)
    xpath_5 = schema.Text(title=_t(u"Xpath 5"), group=5)

    name_6 = schema.Text(title=_t(u"Name"), group=6)
    regex_6 = schema.Text(title=_t(u"Regex"), group=6)
    xpath_6 = schema.Text(title=_t(u"Xpath"), group=6)

    name_7 = schema.Text(title=_t(u"Name"), group=7)
    regex_7 = schema.Text(title=_t(u"Regex"), group=7)
    xpath_7 = schema.Text(title=_t(u"Xpath"), group=7)

    name_8 = schema.Text(title=_t(u"Name"), group=8)
    regex_8 = schema.Text(title=_t(u"Regex"), group=8)
    xpath_8 = schema.Text(title=_t(u"Xpath"), group=8)

    name_9 = schema.Text(title=_t(u"Name"), group=9)
    regex_9 = schema.Text(title=_t(u"Regex"), group=9)
    xpath_9 = schema.Text(title=_t(u"Xpath"), group=9)

    name_10 = schema.Text(title=_t(u"Name"), group=10)
    regex_10 = schema.Text(title=_t(u"Regex"), group=10)
    xpath_10 = schema.Text(title=_t(u"Xpath"), group=10)

    name_11 = schema.Text(title=_t(u"Name"), group=11)
    regex_11 = schema.Text(title=_t(u"Regex"), group=11)
    xpath_11 = schema.Text(title=_t(u"Xpath"), group=11)

    name_12 = schema.Text(title=_t(u"Name"), group=12)
    regex_12 = schema.Text(title=_t(u"Regex"), group=12)
    xpath_12 = schema.Text(title=_t(u"Xpath"), group=12)

    name_13 = schema.Text(title=_t(u"Name"), group=13)
    regex_13 = schema.Text(title=_t(u"Regex"), group=13)
    xpath_13 = schema.Text(title=_t(u"Xpath"), group=13)

    name_14 = schema.Text(title=_t(u"Name"), group=14)
    regex_14 = schema.Text(title=_t(u"Regex"), group=14)
    xpath_14 = schema.Text(title=_t(u"Xpath"), group=14)

    name_15 = schema.Text(title=_t(u"Name"), group=15)
    regex_15 = schema.Text(title=_t(u"Regex"), group=15)
    xpath_15 = schema.Text(title=_t(u"Xpath"), group=15)

    name_16 = schema.Text(title=_t(u"Name"), group=16)
    regex_16 = schema.Text(title=_t(u"Regex"), group=16)
    xpath_16 = schema.Text(title=_t(u"Xpath"), group=16)

    name_17 = schema.Text(title=_t(u"Name"), group=17)
    regex_17 = schema.Text(title=_t(u"Regex"), group=17)
    xpath_17 = schema.Text(title=_t(u"Xpath"), group=17)

    name_18 = schema.Text(title=_t(u"Name"), group=18)
    regex_18 = schema.Text(title=_t(u"Regex"), group=18)
    xpath_18 = schema.Text(title=_t(u"Xpath"), group=18)

    name_19 = schema.Text(title=_t(u"Name"), group=19)
    regex_19 = schema.Text(title=_t(u"Regex"), group=19)
    xpath_19 = schema.Text(title=_t(u"Xpath"), group=19)

    name_20 = schema.Text(title=_t(u"Name"), group=20)
    regex_20 = schema.Text(title=_t(u"Regex"), group=20)
    xpath_20 = schema.Text(title=_t(u"Xpath"), group=20)
