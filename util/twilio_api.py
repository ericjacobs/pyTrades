#
#  Utilities to connect with the Twilio API.
#
#  Basic usage:
#      from twilio_api import client_messages
#
#      twilio_api.client_messages.create(...)
#

import gevent.local
import sys
import termcolor

from twilio.rest import Client
from apikeys import twilio_api_account, twilio_api_token


class ProxyClient(object):
    """This is a proxy for twilio.rest.Client which allocates to each
    greenlet its own API connection.
    """

    def __init__(self):
        self._local = gevent.local.local()

    def __getattr__(self, attr):
        if not hasattr(self._local, 'baseClient'):
            self._local.baseClient = Client(twilio_api_account, twilio_api_token)

        if hasattr(self._local.baseClient.messages, attr):
            return (lambda *args, **kw:
                self._perform(attr,
                    lambda: getattr(self._local.baseClient.messages, attr)(*args, **kw), args, kw))
        raise AttributeError(attr)

    def _perform(self, funcName, func, args, kw):
        try:
            result = func()
        except Exception, e:
            print termcolor.colored('EXCEPTION %s' % e, 'red')
            print 'when calling', funcName, args, kw
            raise e
        return result


client_messages = ProxyClient()
