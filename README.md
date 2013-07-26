cMon
========

#### curl monitor - Nagios/Zenoss plugin for measuing http in all its forms ####
(WIP) Python zenoss/nagios plugin utilizing [python.re](http://docs.python.org/2/library/re.html), [lxml.etree](http://lxml.de/1.3/tutorial.html) and [libcurl](http://curl.haxx.se/libcurl/libcurl) intended for effective http measurement and monitoring that check_http wasn't designed to do:


1. Support for Xpath and value extraction
2. Support for regex, regex subgroups and value extractions
3. Multiple request measurements
4. Single error performance variable
5. Easy support for hostnames, http, https and ports
6. Supports Basic Auth
7. Custom Header Support (cookies, host, anything)
8. Custom User Agents
9. Proxy support


### Install ###
```
$ apt-get instal libxml2 libxml2-dev python-dev curl libcurl python-setuptools
$ easy_install pycurl lxml
$ git clone https://github.com/kmcminn/cmon.git
$ cmon/cmon/nagios/check_cmon.py -u www.google.com
SUCCESS cMon OK | curl_error=0;;  time_total=0.172406;;  time_dns=0.022489;;  time_connect=0.040115;;  size_download=101303.0;;  http_code=200;;
```
# Usage #
The plugin can be used as command line tool or a python module for getting measurements.

### commandline ###
```
$ cmon/nagios/check_cmon.py -h
usage: check_cmon.py [-h] [-u URL] [-p PROXY] [-a AGENT] [-v VERBOSE]
                     [--header HEADER [HEADER ...]] [-t TIMEOUT] [-l LOG]
                     [--nosslcheck] [--cookiejar COOKIEJAR] [--name-0 NAME_0]
                     [--regex-0 REGEX_0] [--xpath-0 XPATH_0] [--name-1 NAME_1]
                     [--regex-1 REGEX_1] [--xpath-1 XPATH_1] [--name-2 NAME_2]
                     [--regex-2 REGEX_2] [--xpath-2 XPATH_2] [--name-3 NAME_3]
                     [--regex-3 REGEX_3] [--xpath-3 XPATH_3] [--name-4 NAME_4]
                     [--regex-4 REGEX_4] [--xpath-4 XPATH_4]

optional arguments:
  -h, --help            show this help message and exit
  -u URL, --url URL     Hostname[:port] to connect to and check. Supports ssl.
                        Supports strings with and without http[s]://. Https
                        will error if server certificate is invalid. Supports
                        basic http auth i.e. http://user:pass@foo.com:8080/bar
  -p PROXY, --proxy PROXY
                        Proxy to connect through, default proxy port is 1080.
                        Supports protocols specifications (socks5://, etc and
                        and user, password and port embedding in the url
  -a AGENT, --agent AGENT
                        Browser agent to use for query. Default = chrome23.
                        Codes for other User Agents: [ ie6, ie7, ie8, ie9,
                        ie10, chrome23, firefox15, ios5, firefox3, safari,
                        opera ]
  -v VERBOSE, --verbose VERBOSE
                        Enable debugging output, currently does nothing
  --header HEADER [HEADER ...]
                        Add one or more HTTP header(s) to the request. Headers
                        can be removed by passing a header with a value of '.'
  -t TIMEOUT, --timeout TIMEOUT
                        Set a timeout for request
  -l LOG, --log LOG     Optionally write parse commands to a file
  --nosslcheck          disable ssl cert and host validation
  --cookiejar COOKIEJAR
                        reuse a curl cookie jar FILEPATH
  --name-0 NAME_0       Variable name to use when returning results in the
                        performance results
  --regex-0 REGEX_0     String regex to test. use groups to extract int values
  --xpath-0 XPATH_0     Xpath string to parse. requires http resource to
                        return xml
  --name-1 NAME_1       Variable name to use when returning results in the
                        performance results
  --regex-1 REGEX_1     String regex to test. use groups to extract int values
  --xpath-1 XPATH_1     Xpath string to parse. requires http resource to
                        return xml
  --name-2 NAME_2       Variable name to use when returning results in the
                        performance results
  --regex-2 REGEX_2     String regex to test. use groups to extract int values
  --xpath-2 XPATH_2     Xpath string to parse. requires http resource to
                        return xml
  --name-3 NAME_3       Variable name to use when returning results in the
                        performance results
  --regex-3 REGEX_3     String regex to test. use groups to extract int values
  --xpath-3 XPATH_3     Xpath string to parse. requires http resource to
                        return xml
  --name-4 NAME_4       Variable name to use when returning results in the
                        performance results
  --regex-4 REGEX_4     String regex to test. use groups to extract int values
  --xpath-4 XPATH_4     Xpath string to parse. requires http resource to
                        return xml

```

### module ###
```python
$ python
Python 2.7.3 (default, Aug  1 2012, 05:14:39)
[GCC 4.6.3] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> import check_cmon as cmon
>>> results = cmon.parse('www.google.com')
>>> results
[('curl_error', 0), ('time_total', '0.122839'), ('time_dns', '0.003245'), ('time_connect', '0.017699'), ('size_download', 94817.0), ('http_code', 200)]
```


### nagios ###
The plugin lacks warning and critical threshold abilities. Don't have a need for them at the moment.

### zenoss3 ###
cmon/cmon/zenoss3 is a non-developer mode zenpack that was last tested in zenoss3. See notes for zenoss4 for using as a command datasource.

### zenoss4 ###
use just the plugin as a command datasource in your monitoring templates. Performance variables are GAUGE types and in zenoss the datapoint name needs to match the performance variable name in the output of the script. You'd typically install this in $ZENHOME/bin

### Notes ###
The nagios plugin's regex and xpath logic has been well vetted in large production environments. If you see any improvements, please let me know. The code is a bit rough around the edges but largely effective for the audiences that will use and maintain it. The zenoss3 zenpack has a twisted daemon that bolts into a zenoss collector which will save you cycles on spawning a python shell with every invocation and is fairly fast. 

The plugin was initially written for zenoss2. In zenoss, thresholds are handled externally to a plugin. Returnning integers and floats regardless of what goes wrong is crucial to keeping things like graphs happy and thresholds working correctly. 

### Todo ###
* Optimize for use in nagios environments, namely passing warn and crit thresholds
* Write some tests
