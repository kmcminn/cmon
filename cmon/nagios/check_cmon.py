#!/usr/bin/env python
# check_cmon.py - advanced curl based nagios plugin

import sys
import re
import pycurl
import StringIO
import time
from lxml import etree


MAX_CHECKS = 20
PREFIXES = ("name", "regex", "xpath")
AGENTS = {
    None: 'Mozilla/5.0 (Windows NT 5.1; rv:15.0)' +
          ' Gecko/20100101 Firefox/15.0',
    'ie6': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0;' +
           'Mercury SiteScope)',
    'ie7': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1;' +
           ' GTB5; .NET CLR 2.0.50727)',
    'opera': 'Opera/9.62 (Windows NT 5.1; U; pt-BR) Presto/2.1.1',
    'firefox15': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US;' +
                 ' rv:1.8.0.12) Gecko/20070508 Firefox/1.5.0.12',
    'firefox3': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US;' +
                ' rv:1.9.0.6) Gecko/2009011913 Firefox/3.0.6',
    'mobile': 'Mozilla/5.0 (iPhone; CPU iPhone OS 5_0 like Mac OS X)' +
              ' AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1' +
              ' Mobile/9A334 Safari/7534.48.3'
}


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
    sys.stdout.write("Success | ")

    for name, value in results:

        sys.stdout.write("%s=%s;; " % (name, value))

        if 'curl_error' in name:

            try:
                exitcode = int(value)
            except:
                exitcode = 250

    sys.stdout.write("\n")
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


def curlConfig(write, url, timeout, agent, proxy, header):

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

    return c


def parse(url, contentMatches=[], agent=None,
          proxy=None, header=None, timeout=10):

    timeout = int(timeout)
    agent = AGENTS.get(agent, AGENTS.get(None))
    b = StringIO.StringIO()

    curl = curlConfig(b.write, url, timeout, agent, proxy, header)

    try:
        curl.perform()
    except pycurl.error, pce:
        return (('curl_error', pce[0]), ('time_total', 0),
                ('time_dns', 0), ('time_connect', 0), ('size_download', 0))

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

                    # if initial xpath found a single element
                    # attribute or value it will be str and we can catch it
                    if isinstance(xpathresult[0], str):
                            matches.append(xpathresult[0])

                    # on xml that doesn't have carriage returns we need to use
                    # this xpath class to get simple element or attribute value
                    else:
                        xpathvalue = etree.XPath(value)(root)[0].text
                        if xpathvalue is not None:
                                matches.append(float(xpathvalue[0]))
            except:
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
                        # can threshold this reliably
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

    return results


if __name__ == "__main__":

    if len(sys.argv) is 1:
        print "for help use: ", sys.argv[0], ' -h'
        sys.exit(1)

    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument("-u", "--url", dest="url",
                        help="Hostname[:port] to connect to and check. Supports " +
                             "ssl. Supports strings with http[s]:// or without. " +
                             "https will error if server certificate is invalid")
    parser.add_argument("-p", "--proxy", dest="proxy",
                        help="Proxy to connect through")
    parser.add_argument("-a", "--agent", dest="agent",
                        help="Browser agent to use for query, " +
                        "default firefox 15 strings, agent codes [ ie6, ie7, firefox15, " +
                        " mobile, firefox3, opera")
    parser.add_argument("-v", "--verbose", dest="verbose",
                        help="enables debugging output, currently does nothing")
    parser.add_argument("--header", nargs="+", dest="header",
                        help="set a <string> header. suitable for setting")
    parser.add_argument("-t", "--timeout", dest="timeout", default=10,
                        help="timeout for the tcp connection")
    parser.add_argument("-l", "--log", dest="log",
                        help="write to <filename>")

    expandXpathRegexOptions(parser, PREFIXES, MAX_CHECKS)

    options = parser.parse_args()

    contentMatches = parseContentMatches(options)

    results = parse(options.url, contentMatches, options.agent,
                    options.proxy, options.header, options.timeout)

    if options.log:

        logResultsToFile(options.log)

    nagiosStdoutExit(results)
