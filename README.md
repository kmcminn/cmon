cMon
========

#### curl monitor - Nagios/Zenoss plugin for measuing http ####
Work in progress, based on a python nagios plugin utilizing lxml, libcurl and regex to do effective and simple httpd measurement and monitoring.

### Install ###
```
$ apt-get instal libxml2 libxml2-dev python-dev curl libcurl python-setuptools
$ easy_install pycurl lxml
$ git clone https://github.com/kmcminn/cmon.git
```
# Usage #
The plugin can be used as command line tool or a python module for getting measurements.

### commandline ###
```
$ cmon/nagios/check_cmon.py -h
usage: check_cmon.py [-h] [-u URL] [-p PROXY] [-a AGENT] [-v VERBOSE]
                     [--header HEADER [HEADER ...]] [-t TIMEOUT] [-l LOG]
                     [--name-0 NAME_0] [--regex-0 REGEX_0] [--xpath-0 XPATH_0]
                     [--name-1 NAME_1] [--regex-1 REGEX_1] [--xpath-1 XPATH_1]
                     [--name-2 NAME_2] [--regex-2 REGEX_2] [--xpath-2 XPATH_2]
                     [--name-3 NAME_3] [--regex-3 REGEX_3] [--xpath-3 XPATH_3]
                     [--name-4 NAME_4] [--regex-4 REGEX_4] [--xpath-4 XPATH_4]

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
The plugin lacks warning and critical threshold abilities. Add it to your plugins directory and get hacking!

### zenoss3 ###
cmon/zenoss3 is non-developer mode zenpack that was last tested in zenoss3. Alternately you can use the nagios plugin as a command in zenoss3.

### zenoss4 ###
use as a command datasource and call it directly on the command line. add datapoints manually.
