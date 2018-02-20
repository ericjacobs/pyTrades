
#
# This file contains a bot that will read the Binance WebSocket stream and
# update the market data as data comes in,
#


import datetime
import decimal
import gevent
import termcolor
import time

from ws4py.client import geventclient

from pyTrades.util import market
from pyTrades.util import json


def streamBot():
    while True:
        print termcolor.colored('Connecting to WebSocket', 'blue')

        ws = geventclient.WebSocketClient('wss://stream.binance.com:9443/ws/!ticker@arr')
        try:
            ws.connect()
        except Exception, e:
            print termcolor.colored('WebSocket exception. Waiting 10 seconds and retry', 'red')
            print e
            ws.close()
            time.sleep(10)
            break

        while True:
            m = ws.receive()
            if m is not None:
                symbolList = []

                for symbol in json.loads(m.data):
                    symbolName, curPrice = symbol['s'].upper(), symbol['c']
                    symbolList.append(symbolName)

                    market.getMemo(symbolName, create=True).add(
                        datetime.datetime.now(),
                        decimal.Decimal(curPrice))

                print 'Received stream data (%d assets)' % len(symbolList)
            else:
                print termcolor.colored('WebSocket hit end-of-stream. Waiting 10 seconds and reconnecting', 'red')
                ws.close()
                time.sleep(10)
                break
