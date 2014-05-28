#!/usr/bin/env python

import os
import sys
import socket
from time import ctime
from collections import defaultdict
from xml.etree import ElementTree
if sys.version_info[0] == 2:
    ## Python 2.x
    from urllib import urlopen, urlencode
else:
    ## Python 3.x
    from urllib.request import urlopen
    from urllib.parse import urlencode


__version__ = '1.1.0'


class Xymon(object):
    """Communicate with a Xymon server

    server: Hostname or IP address of a Xymon server. Defaults to $XYMSRV
            if set, or 'localhost' if not.
    port:   The port number the server listens on. Defaults to 1984.
    """
    def __init__(self, server=None, port=1984):
        if server is None:
            server = os.environ.get('XYMSRV', 'localhost')
        self.server = server
        self.port = port

    def report(self, host, test, color, message, interval='30m'):
        """Report status to a Xymon server

        host:     The hostname to associate the report with.
        test:     The name of the test or service.
        color:    The color to set. Can be 'green', 'yellow', 'red', or 'clear'
        message:  Details about the current state.
        interval: An optional interval between tests. The status will change
                  to purple if no further reports are sent in this time.
        """
        args = {
            'host': host,
            'test': test,
            'color': color,
            'message': message,
            'interval': interval,
            'date': ctime(),
        }
        report = '''status+{interval} {host}.{test} {color} {date}
{message}'''.format(**args)
        self.send_message(report)

    def data(self, host, test, raw_data):
        """Report data to a Xymon server

        host:     The hostname to associate the report with.
        test:     The name of the test or service.
        data:     The RRD data.
        """
        args = {
            'host': host,
            'test': test,
            'data': raw_data,
        }
        report = '''data {host}.{test}\n{data}'''.format(**args)
        self.send_message(report)

    def send_message(self, message):
        """Report arbitrary information to the server

        See the xymon(1) man page for message syntax.
        """
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error as msg:
            ## socket creation failed
            return False
        try:
            server_ip = socket.gethostbyname(self.server)
        except socket.gaierror:
            ## DNS lookup error
            return False
        try:
            message = message + '\n'
            s.connect((server_ip, self.port))
            s.sendall(message.encode())
            return True
        except socket.error as msg:
            ## connection refused
            return False
        finally:
            s.close()

    def appfeed(self, host=None, test=None, color=None, cgi=None, ssl=True):
        """Query a Xymon server for the current status of tests

        Returns a dictionary of status information by host, then by test.
        Suitable for conversion to JSON, YAML, etc.

        host:  Limit the results to a specific host or pattern
        test:  Limit the results to a specific test
        color: Limit the results to specific colors (comma separated).
               Includes all colors by default.
        cgi:   The directory prefix for appfeed.cgi. Defaults to
               $XYMONSERVERCGIURL if set, or '/xymon-cgi' if not.
        ssl:   Uses HTTPS if True (default), HTTP if False

        If called without arguments, all data for all tests is returned.

        See http://www.xymon.com/xymon/help/manpages/man1/appfeed.cgi.1.html
        """
        ## default value
        err_host = host if host else 'nohost'
        err_test = test if test else 'notest'
        statuses = {
            err_host: {
                err_test: {
                    'status': 'unknown',
                    'summary': 'data never retrieved',
                }
            }
        }
        proto = ('http', 'https')[bool(ssl)]
        if cgi is None:
            cgi = os.environ.get('XYMONSERVERCGIURL', '/xymon-cgi')
        if color is None:
            color = 'blue,purple,clear,yellow,green,red'
        test_filter = 'color={0}'.format(color)
        if test is not None:
            test_filter = 'test={0} {1}'.format(test, test_filter)
        if host is not None:
            test_filter = 'host={0} {1}'.format(host, test_filter)
        url_params = urlencode({'filter': test_filter})
        base = '{0}://{1}'.format(proto, self.server)
        appfeed = '{0}{1}/appfeed.sh'.format(base, cgi)
        url = appfeed + '?' + url_params
        try:
            remote = urlopen(url)
            status_xml = remote.read()
            remote.close()
            try:
                root = ElementTree.fromstring(status_xml)
                statuses = defaultdict(dict)
                for status_element in root.getiterator('ServerStatus'):
                    hostname = status_element.find('Servername').text
                    service = status_element.find('Type').text
                    status = {
                        'status': status_element.find('Status').text,
                        'summary': status_element.find('MessageSummary').text,
                        'url': base + status_element.find('DetailURL').text,
                        'time': int(status_element.find('LogTime').text),
                        'changed': int(status_element.find('LastChange').text),
                    }
                    if status['status'] == 'blue':
                        status['disabled'] = \
                            status_element.find('DisableText').text.strip()
                        status['by'] = \
                            status_element.find('DisabledBy').text
                    statuses[hostname][service] = status
                if len(statuses) == 0:
                    statuses = {
                        err_host: {
                            err_test: {
                                'status': 'unmonitored',
                                'summary': 'no data for {0}.{1}'.format(
                                    err_host, err_test
                                ),
                            }
                        }
                    }
                else:
                    ## convert defaultdict to a normal dictionary
                    statuses = dict(statuses)
            except:
                statuses = {
                    err_host: {
                        err_test: {
                            'status': 'unknown',
                            'summary': 'Error parsing XML from Xymon',
                        }
                    }
                }
        except:
            statuses = {
                err_host: {
                    err_test: {
                        'status': 'unknown',
                        'summary': 'Error getting data from ' + appfeed,
                    }
                }
            }
        return statuses

    def status(self, host, test):
        """Return only the status of a single host/service as a string"""
        result = self.appfeed(host=host, test=test)
        if host in result and test in result[host]:
            return result[host][test]['status']
        else:
            return 'unknown'
