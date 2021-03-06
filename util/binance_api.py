#
#  Utilities to connect with the Binance API.
#
#  Basic usage:
#      from binance_api import client
#

import gevent.local
import sys
import termcolor

from binance.client import Client
from apikeys import binance_api_key, binance_api_secret


class ProxyClient(object):
    """This is a proxy for binance.client.Client which allocates to each
    greenlet its own API connection.
    """

    def __init__(self):
        self._local = gevent.local.local()

    def __getattr__(self, attr):
        if not hasattr(self._local, 'baseClient'):
            self._local.baseClient = Client(binance_api_key, binance_api_secret, {'timeout': 99999})

        if hasattr(self._local.baseClient, attr):
            return (lambda *args, **kw:
                self._perform(attr,
                    lambda: getattr(self._local.baseClient, attr)(*args, **kw), args, kw))
        raise AttributeError(attr)

    def _perform(self, funcName, func, args, kw):
        try:
            result = func()
        except Exception, e:
            print termcolor.colored('EXCEPTION %s' % e, 'red')
            print 'when calling', funcName, args, kw
            if e.code == -1021:
                raise e
            sys.exit(1)
        return result


client = ProxyClient()
