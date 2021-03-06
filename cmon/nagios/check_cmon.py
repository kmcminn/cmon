#!/usr/bin/env python
# check_cmon.py - advanced curl based nagios plugin

import sys
import re
import pycurl
import StringIO
import time
from lxml import etree


MAX_CHECKS = 5
PREFIXES = ("name", "regex", "xpath")
AGENTS = {
    None: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) ' +
          'AppleWebKit/537.11 (KHTML, like Gecko) ' +
          'Chrome/23.0.1271.6 Safari/537.11',
    'ie6': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0;' +
           'Mercury SiteScope)',
    'ie7': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1;' +
           ' GTB5; .NET CLR 2.0.50727)',
    'ie8': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0)',
    'ie9': 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)',
    'ie10': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)',
    'opera': 'Opera/9.62 (Windows NT 5.1; U; pt-BR) Presto/2.1.1',
    'safari': 'Mozilla/5.0 (iPad; CPU OS 6_0 like Mac OS X) AppleWebKit/536.26 ' +
              '(KHTML, like Gecko) Version/6.0 Mobile/10A5355d Safari/8536.25',
    'firefox15': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US;' +
                 ' rv:1.8.0.12) Gecko/20070508 Firefox/1.5.0.12',
    'firefox3': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US;' +
                ' rv:1.9.0.6) Gecko/2009011913 Firefox/3.0.6',
    'chrome23': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) ' +
                'AppleWebKit/537.11 (KHTML, like Gecko) ' +
                'Chrome/23.0.1271.6 Safari/537.11',
    'ios5': 'Mozilla/5.0 (iPhone; CPU iPhone OS 5_0 like Mac OS X)' +
              ' AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1' +
              ' Mobile/9A334 Safari/7534.48.3'
}
pycurl.COOKIESESSION = 96

def _getResultType(result):
    _ = result[0]
    return 'lxml' if 'lxml' in str(type(_)) else 'result'


def _findValue(result):
    """ returns none if not a sensible list-type object or str else the value """
    value = None
    if isinstance(result, list):
        value = result[0] if len(result) >= 1 else None
    elif isinstance(result, basestring):
        value = result if len >= 1 else None
    elif isinstance(result, float) or isinstance(result, int):
        value = result
    else:
        pass
    return value

def expandXpathRegexOptions(argp, prefixes, total):
    """
    iterates and makes alot of regex and xpath parser args
    """

    regex_help = "String regex to test. use groups to extract int values"
    xpath_help = "Xpath string to parse. requires http resource to " \
                 + "return xml"
    name_help = "Variable name to use when returning results in the " \
                + "performance results"

    for i in range(0, total):

        for prefix in prefixes:

            name = "%s-%d" % (prefix, i)
            dest = "%s_%d" % (prefix, i)

            if 'name' in prefix:
                argp.add_argument("--%s" % name, dest=dest, help=name_help)

            elif 'regex' in prefix:
                argp.add_argument("--%s" % name, dest=dest, help=regex_help)

            elif 'xpath' in prefix:
                argp.add_argument("--%s" % name, dest=dest, help=xpath_help)

            else:
                argp.add_argument("--%s" % name, dest=dest)


def nagiosStdoutExit(results):
    """
    spit out stdout
    """
    perf_stdout = []
    result_stdout = ['SUCCESS']


    for name, value in results:

        if 'result_message' not in name:
            perf_stdout.append("%s=%s;; " % (name, value))
        else:
            result_stdout.append(value)
            result_stdout.append('|')

        if 'curl_error' in name:

            try:
                exitcode = int(value)
            except:
                exitcode = 250

    sys.stdout.write(' '.join(result_stdout) + ' ' + ' '.join(perf_stdout) + "\n")
    sys.exit(exitcode)


def logResultsToFile(filename):

    import time

    try:
        f = open(options.log, 'a')
        logFmt = "%s | %s \n"
        msg = logFmt % (time.time(), ' '.join(sys.argv))
        f.write(msg)
        f.close()

    except Exception, e:

        print "Error writing to file: ", e


def parseContentMatches(cfg, start=0, length=MAX_CHECKS):
    """
    parses name/regex/xpath_N properties
    """

    contentMatches = []
    for i in range(start, length):
        i = str(i)
        name = getattr(cfg, "name_" + i)
        xpath = getattr(cfg, "xpath_" + i)
        regex = getattr(cfg, "regex_" + i)

        if not name:
            continue

        if xpath and regex:
            raise Exception("Content match %s defines xpath and regex." +
                            "The two are mutually exclusive." % i)

        if xpath:
            typex = "xpath"
            value = xpath
        else:
            typex = "regex"
            value = regex

        contentMatches.append((name, typex, value))

    return contentMatches


def parseWithConfig(cfg, start=0, length=MAX_CHECKS):
    """
    parses using a passed in config. typically from
    zenoss in daemon mode
    """

    url = cfg.url
    contentMatches = parseContentMatches(cfg, start, length)
    agent = cfg.agent
    proxy = cfg.proxy
    header = cfg.header
    log = cfg.log
    timeout = cfg.timeout

    results = parse(url, contentMatches, agent, proxy, header, timeout)
    return results


def formatNumber(num, precision=4):
    """
    returns a number supressing formatting exceptions
    """

    try:

        num = float(num)

    except:
        return 0

    return ('%f' % (num))


def curlConfig(write, url, timeout, agent, proxy, header, issl, icookie):

    c = pycurl.Curl()
    c.setopt(pycurl.WRITEFUNCTION, write)
    c.setopt(pycurl.URL, url)
    c.setopt(pycurl.TIMEOUT, timeout)
    c.setopt(pycurl.USERAGENT, agent)
    c.setopt(pycurl.FOLLOWLOCATION, 1)
    c.setopt(pycurl.MAXREDIRS, 5)
    c.setopt(pycurl.CONNECTTIMEOUT, 100)
    c.setopt(pycurl.NOSIGNAL, 1)
    c.setopt(pycurl.HTTPPROXYTUNNEL, 0)

    if proxy:
        c.setopt(pycurl.PROXY, proxy)

    if header:
        c.setopt(pycurl.HTTPHEADER, header)

    if issl:
        c.setopt(pycurl.SSL_VERIFYHOST, 0)
        c.setopt(pycurl.SSL_VERIFYPEER, 0)

    if icookie:
        c.setopt(pycurl.COOKIESESSION, 0)
        c.setopt(pycurl.COOKIEFILE, icookie)
        c.setopt(pycurl.COOKIEJAR, icookie)


    return c


def parse(url, contentMatches=[], agent=None,
          proxy=None, header=None, timeout=10, ssl=None, cookiejar=None):

    timeout = int(timeout)
    agent = AGENTS.get(agent, AGENTS.get(None))
    b = StringIO.StringIO()

    curl = curlConfig(b.write, url, timeout, agent, proxy, header, ssl, cookiejar)

    try:
        curl.perform()

    except Exception, pce:

        try:
            cerror = int(pce[0])
        except:
            cerror = 250

        return (('curl_error', cerror), ('time_total', 0),
                ('time_dns', 0), ('time_connect', 0), ('size_download', 0), ('result_message', pce[1]))

    body = b.getvalue()
    root = None

    results = []
    results.append(('curl_error', 0))
    results.append(('time_total', formatNumber(curl.getinfo(curl.TOTAL_TIME))))
    results.append(('time_dns', formatNumber(curl.getinfo(curl.NAMELOOKUP_TIME))))
    results.append(('time_connect', formatNumber(curl.getinfo(curl.CONNECT_TIME))))
    results.append(('size_download', curl.getinfo(curl.SIZE_DOWNLOAD)))
    results.append(('http_code', curl.getinfo(curl.RESPONSE_CODE)))

    for (name, typex, value) in contentMatches:

        matches = []
        failed = 1

        if typex == "xpath":

            # first check if this is the first iteration
            if root is None:

                try:
                    # using fromstring to avoid any complaints
                    # from poorly formed documents
                    root = etree.fromstring(body)

                except:
                    pass

            try:
                # query xml doc, element(s) matches fill the result list
                xpathresult = root.xpath(value)

                if len(xpathresult) > 0:

                    # match successful
                    failed = 0
                    xpathvalue = xpathresult

                    # result not fully extracted, seen on xml with no line breaks
                    if 'lxml' in _getResultType(xpathresult):
                        xpathvalue = etree.XPath(value)(root)[0].text

                    # extract and append the value to matches
                    matches.append(_findValue(xpathvalue))

            except Exception:
                pass
                

        elif typex == "regex":

            try:
                # compile and re.search
                result = re.compile(value, re.DOTALL).search(body)

                # match?
                if result is not None or result.groups()[0] is not None:

                    # match was successful
                    failed = 0

                    # try to pull content returned
                    if len(result.groups()) > 0:

                        matches.extend(result.groups())

                        # throw out whitespace and alpha so we
                        # can threshold perf data reliably
                        matches[0] = re.sub("[\s,a-z,A-Z]", "", matches[0])

            except:
                pass

        # gather matches
        if len(matches) > 0:

            try:
                results.append((name, float(matches[0])))

            except (ValueError, TypeError):
                pass

        # append to the results list
        results.append(('%s_match_failed' % name, failed))

    results.append(('result_message', 'cMon OK'))

    return results


if __name__ == "__main__":

    if len(sys.argv) is 1:
        print "for help use: ", sys.argv[0], ' -h'
        sys.exit(1)

    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument("-u", "--url", dest="url",
                        help="Hostname[:port] to connect to and check. Supports " +
                             "ssl. Supports strings with and without http[s]://. " +
                             "Https will error if server certificate is invalid. " +
                             "Supports basic http auth i.e. http://user:pass@foo.com:8080/bar")
    parser.add_argument("-p", "--proxy", dest="proxy",
                        help="Proxy to connect through, default proxy port is 1080. " +
                             "Supports protocols specifications (socks5://, etc and " +
                             "and user, password and port embedding in the url")
    parser.add_argument("-a", "--agent", dest="agent",
                        help="Browser agent to use for query. " +
                        "Default = chrome23. Codes for other User Agents: [ ie6, ie7, " +
                        " ie8, ie9, ie10, chrome23, firefox15, " +
                        " ios5, firefox3, safari, opera ]")
    parser.add_argument("-v", "--verbose", dest="verbose",
                        help="Enable debugging output, currently does nothing")
    parser.add_argument("--header", nargs="+", dest="header",
                        help="Add one or more HTTP header(s) to the request. Headers can be " +
                             " removed by passing a header with a value of '.'")
    parser.add_argument("-t", "--timeout", dest="timeout", default=10,
                        help="Set a timeout for request")
    parser.add_argument("-l", "--log", dest="log",
                        help="Optionally write parse commands to a file")
    parser.add_argument("--nosslcheck", action="store_true",
                        help="disable ssl cert and host validation ")
    parser.add_argument("--cookiejar", dest="cookiejar", default=False,
                        help="reuse a curl cookie jar FILEPATH")

    expandXpathRegexOptions(parser, PREFIXES, MAX_CHECKS)

    options = parser.parse_args()

    contentMatches = parseContentMatches(options)

    results = parse(options.url, contentMatches, options.agent,
                    options.proxy, options.header, options.timeout,
                    options.nosslcheck, options.cookiejar)

    if options.log:

        logResultsToFile(options.log)

    nagiosStdoutExit(results)
