#!/usr/bin/env python
# CmonUrlCheck.py - advanced curl based nagios plugin

import sys
import re
import pycurl
import StringIO
import time
from lxml import etree

MAX_CHECKS = 20
PREFIXES = ("name", "regex", "xpath")
AGENTS = {
	None:'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0; Mercury SiteScope)',
	'ie6':'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0; Mercury SiteScope)',
	'ie7':'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; GTB5; .NET CLR 2.0.50727)',
	'opera':'Opera/9.62 (Windows NT 5.1; U; pt-BR) Presto/2.1.1',
	'firefox15':'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.0.12) Gecko/20070508 Firefox/1.5.0.12',
	'firefox3':'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.6) Gecko/2009011913 Firefox/3.0.6',
	'mobile':'Mozilla/5.0 (iPhone; U; CPU like Mac OS X; en) AppleWebKit/420 (KHTML, like Gecko) Version/3.0 Mobile/1C28 Safari/419.3',
}

def parseContentMatches(cfg, start=0, length=MAX_CHECKS):
	# parse out options from ZenHub config *or* optparse.Options (anything with name/regex/xpath_N properties)
	contentMatches = []
	for i in range(start, length):
		i = str(i)
		name = getattr(cfg, "name_" + i)
		xpath = getattr(cfg, "xpath_" + i)
		regex = getattr(cfg, "regex_" + i)

		if not name:
			continue

		if xpath and regex:
			raise  Exception("Content match %s defines xpath and regex. The two are mutually exclusive." % i)

		if xpath:
			type = "xpath"
			value = xpath
		else:
			type = "regex"
			value = regex

		contentMatches.append((name, type, value))

	return contentMatches

def parseWithConfig(cfg, start=0, length=MAX_CHECKS):
	url = cfg.url
	contentMatches = parseContentMatches(cfg, start, length)
	agent = cfg.agent
	proxy = cfg.proxy
	hostheader = cfg.hostheader
	log = cfg.log
	timeout = cfg.timeout

	results = parse(url, contentMatches, agent, proxy, hostheader, timeout)
	return results

def parse(url, contentMatches=[], agent=None, proxy=None, hostheader=None, timeout=10):
	timeout = int(timeout)
	agent = AGENTS.get(agent, AGENTS.get(None))

	b = StringIO.StringIO()
	c = pycurl.Curl()
	c.setopt(pycurl.WRITEFUNCTION, b.write)
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
	if hostheader:
		c.setopt(pycurl.HTTPHEADER, ["Host:" + hostheader])

	try:
		c.perform()
	except pycurl.error, pce:
		return (('curl_error', pce[0]), ('time_total', 0), ('time_dns', 0), ('time_connect', 0), ('size_download', 0))

	body = b.getvalue()
	root = None

	results = []
	results.append(('curl_error', 0))
	results.append(('time_total', c.getinfo(c.TOTAL_TIME)))
	results.append(('time_dns', c.getinfo(c.NAMELOOKUP_TIME)))
	results.append(('time_connect', c.getinfo(c.CONNECT_TIME)))
	results.append(('size_download', c.getinfo(c.SIZE_DOWNLOAD)))
	results.append(('http_code', c.getinfo(c.RESPONSE_CODE)))

	# main content match block
	for (name, type, value) in contentMatches:

		# empty the matches list and set default match condition to failed
		matches = []
		failed = 1
		
		if type == "xpath":

			# first check if this is the first iteration 
			if root is None:

				try:
					# using fromstring to avoid any complaints from poorly formed documents
					root = etree.fromstring(body)

				except:
					# suppress exceptions
					pass

			# execute xpath and test
			try:
				# query xml doc, element(s) matches fill the result list
				xpathresult = root.xpath(value)

				# look for non-empty list
				if len(xpathresult) > 0:
					
					# match successful
					failed = 0	

					# if initial xpath found a single element, attribute or value it will be str and we can catch it
					if isinstance(xpathresult[0], str):
							matches.append(xpathresult[0])

					# on xml that doesn't have carriage returns we need to use this xpath class to get simple element or attribute value
					else:
						xpathvalue = etree.XPath(value)(root)[0].text
						if xpathvalue is not None:
								matches.append(float(xpathvalue[0]))
			# ignore exceptions
			except:
				pass

		elif type == "regex":
			try:
				# compile and run regex, result will be None if the match failed or a match object if successful
				result = re.compile(value, re.DOTALL).search(body)

				# test regex result comprehensively
				if result is not None or result.groups()[0] is not None:

					# match was successful
					failed = 0

					# groups() returns all subgroup matches, we only want one match
					if len(result.groups()) > 0:

						# using list.extend() to iterate the return tuple
						matches.extend(result.groups())

						# throw out whitespace and alpha
						matches[0] = re.sub("[\s,a-z,A-Z]","",matches[0])

			# ignoring exceptions
			except:
				pass

		# append the matches to the results
		if len(matches) > 0:

			# cast to float
			try:
				results.append((name, float(matches[0])))

			# catch value and type errors and ignore them
			except (ValueError, TypeError):
				pass

		# append to the results list
		results.append(('%s_match_failed' % name, failed))

	return results

if __name__ == "__main__":
	from optparse import OptionParser

	parser = OptionParser()
	parser.add_option("--url", dest="url")
	parser.add_option("--proxy", dest="proxy")
	parser.add_option("--agent", dest="agent")
	parser.add_option("--verbose", dest="verbose")
	parser.add_option("--hostheader", dest="hostheader")
	parser.add_option("--timeout", dest="timeout", default=10)
	parser.add_option("--log", dest="log")
	for i in range(0, MAX_CHECKS):
		for prefix in PREFIXES:
			name = "%s-%d" % (prefix, i)
			dest = "%s_%d" % (prefix, i)
			parser.add_option("--%s" % name, dest=dest)

	(options, args) = parser.parse_args()

	contentMatches = parseContentMatches(options)

	results = parse(options.url, contentMatches, options.agent, options.proxy, options.hostheader, options.timeout)

	print  "Success|",
	for name, value in results:
		#print "%s=%s;;;0" % (name, value),
		print "%s=%s" % (name, value),
	print

	log = options.log
	if log:
		try:
			f = open(log, 'a')
			logFmt = "%s | %s \n"
			msg = logFmt % (time.time(), ' '.join(sys.argv))
			f.write(msg)
			f.close()
		except:
			print "error writing to file"

