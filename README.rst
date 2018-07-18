====================
Xymon Python Library
====================

This library allows basic communication with a Xymon server directly from a Python script. It works with Python 2.6, 2.7, and 3. It can be used on a system with no Xymon client installed.

Some basic examples are shown here. See ``help(Xymon)`` for details.

Installation
------------

.. code-block:: bash

    $ pip install Xymon

Getting Started
---------------

Get an instance of the ``Xymon`` class to talk to the server.

.. code-block:: pycon

    >>> from xymon import Xymon
    >>> server = Xymon('xymon.domain.tld', 1984)

The server name and port number are optional. The server name will default to the ``$XYMSRV`` environment variable if your script is being run by a Xymon client, or ``localhost`` if the variable isn't set. The port defaults to ``1984``.

Reporting
---------

Report a status to the server:

.. code-block:: pycon

    >>> server.report('webserver01', 'https', 'yellow', 'slow HTTP response')

Querying
--------

Getting status data:

.. code-block:: pycon

    >>> server.appfeed(host='ldap.*', test='ldaps')
    {'ldap01':
        {'ldaps':
            {'status': 'green',
             'changed': 1396294952,
             'time': 1396462829,
             'url': 'https://xymon.domain.tld/xymon-cgi/svcstatus.sh?HOST=ldap01&SERVICE=ldaps',
             'summary': 'green Wed Apr  2 14:19:56 2014 ldaps ok '}
        },
    'ldap02':
        {'ldaps':
            {'status': 'green',
             'changed': 1396294952,
             'time': 1396462829,
             'url': 'https://xymon.domain.tld/xymon-cgi/svcstatus.sh?HOST=ldap02&SERVICE=ldaps',
             'summary': 'green Wed Apr  2 14:19:56 2014 ldaps ok '}
        }
    }

This communicates with the server using its ``appfeed.cgi`` interface. If called with no arguments, ``appfeed()`` will return data for all tests on all hosts. Results can be limited by host, test, page, and color.

Note that ``host`` can be a pattern as described in `Xymon's documentation`_.

To just get the status of a single service on a single host as a string, use ``status()``:

.. code-block:: pycon

    >>> server.status('ldap01', 'ldaps')
    'green'

If you want data for more than one host/test, it's probably more efficient to get all the data using ``appfeed()`` and pull out what you want.

.. _Xymon's Documentation: http://www.xymon.com/xymon/help/manpages/man1/appfeed.cgi.1.html
