
#
# This file contains a bot that will read the Binance WebSocket stream and
# update the market data as data comes in,
#


import datetime
import decimal
import gevent
import ujson
import termcolor

from ws4py.client import geventclient

from pyTrades.util import market


def streamBot():
    print termcolor.colored('Connecting to WebSocket', 'blue')

    ws = geventclient.WebSocketClient('wss://stream.binance.com:9443/ws/!ticker@arr')
    ws.connect()

    while True:
        m = ws.receive()
        if m is not None:
            symbolList = []

            for symbol in ujson.loads(m.data):
                symbolName, curPrice = symbol['s'].upper(), symbol['c']
                symbolList.append(symbolName)

                market.getMemo(symbolName, create=True).add(
                    datetime.datetime.now(),
                    decimal.Decimal(curPrice))

            print 'Received stream data (%d assets)' % len(symbolList)
        else:
            break
