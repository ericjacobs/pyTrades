
#
# This file contains a bot that will reports on the trades that the
# strategy bots make.
#

import time

from gevent import queue
from pyTrades.util import twilio_api
from pyTrades.settings import MY_PHONE_NUMBER, SMS_TO_NUMBER


reportQueue = queue.Queue()

def reportBuy(asset, quoteAsset, qty, sellLevel, currentPrice, oldPrice, buyLevel):
    reportQueue.put((asset, quoteAsset, qty, sellLevel, currentPrice, oldPrice, buyLevel))


def reporterBot():
    while True:
        (asset, quoteAsset, qty, sellLevel, currentPrice, oldPrice, buyLevel) = reportQueue.get()
        message = '%s %s-%s buy %s sell for %s (saw %s, was %s) buyLevel%s' % (
            (time.ctime(),
             asset, quoteAsset, qty, '{:0.{}f}'.format(sellLevel, 10), currentPrice,
                                     '{:0.{}f}'.format(oldPrice, 10), buyLevel))

        twilio_api.client_messages.create(
           to=SMS_TO_NUMBER,
           from_=MY_PHONE_NUMBER,
           body=message)
          
        time.sleep(2)
