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
from apikeys import api_key, api_secret


class ProxyClient(object):
    """This is a proxy for binance.client.Client which allocates to each
    greenlet its own API connection.
    """

    def __init__(self):
        self._local = gevent.local.local()

    def __getattr__(self, attr):
        if not hasattr(self._local, 'baseClient'):
            self._local.baseClient = Client(api_key, api_secret, {'timeout': 99999})

        if hasattr(self._local.baseClient, attr):
            return (lambda *args, **kw:
                self._perform(attr,
                    lambda: getattr(self._local.baseClient, attr)(*args, **kw)))
        raise AttributeError(attr)

    def _perform(self, funcName, func):
        try:
            result = func()
        except Exception, e:
            print termcolor.colored('EXCEPTION %s' % e, 'red')
            if e.code in (-1003, -1015, -1016):
                sys.exit(1)
            raise e
        return result


client = ProxyClient()
