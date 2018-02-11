
#
# Basic trading strategy impementation.
#


import sys
import math
import random
import time

from decimal import Decimal as _d
from binance.client import Client
from termcolor import colored

from pyTrades.util.binance_api import client
from pyTrades.util import market
from pyTrades.strats import abstract


class Strategy1(abstract.AbstractStrategy):

    # Asset will be set in the loop at the end of this file.
    asset = None

    # Change this to change the asset you're paying with
    otherasset = 'BTC'

    def trades(self):
        asset = self.asset
        otherasset = self.otherasset

        # Calculate pair you're trading
        symbol = asset + otherasset

        print colored('Initializing', "cyan")

        # Do a random wait to avoid slamming the server on startup.
        time.sleep(random.randrange(0, 200))

        balance= (client.get_asset_balance(asset))
        balance = float(balance['free'])
        startBalance=(client.get_asset_balance(asset))
        startBalance= float(startBalance['free'])
        #lastPrice = float(Orders.get_ticker(symbol)['lastPrice'])
        currentPrice = client.get_ticker(symbol =symbol)
        currentPrice=float(currentPrice['lastPrice'])

        # Do a random wait to avoid slamming the server on startup.
        time.sleep(random.randrange(2, 200))

        print colored('Initializing - step 2', "cyan")

        # Get the min and max quantity for trading under this symbol.
        symbolInfo = client.get_symbol_info(symbol)
        symbolFilters = {filt['filterType']: filt
                             for filt in symbolInfo['filters']}
        lotSizeFilter = symbolFilters.get('LOT_SIZE', {})
        lotSizeMinQty = float(lotSizeFilter.get('minQty', 0.0))
        lotSizeMaxQty = float(lotSizeFilter.get('maxQty', 0.0))
        lotSizeStep = float(lotSizeFilter.get('stepSize', 0.0))

        # This is the number of digits we should round to in order
        # to conform to the lot's stepSize restriction.
        lotSizeStepNumDigits = int(round(-math.log(lotSizeStep, 10)))

        # Do a random wait to avoid slamming the server on startup.
        time.sleep(random.randrange(2, 200))

        print colored('Initializing - step 3', "cyan")

        numberOfBuys = 0
        otherbalance = (client.get_asset_balance(otherasset))
        otherbalance = _d(otherbalance['free'])

        # How much of otherasset (e.g. BTC) we want to work with, expressed as
        # fraction of the current balance of otherasset.
        baseBalanceFraction = _d(0.7)       # 20% of current balance
        baseBalance = otherbalance * baseBalanceFraction

        cycle = 0
        actions = []
        openBuys = {}

        print colored('Auto Trading with binance', "cyan")
        print 'Trading with', baseBalance, 'of', otherasset

        while True:
            buyPrice = market.price(asset, otherasset, minsAgo=1)

            buyLevel1 = buyPrice * _d(0.95)
            buyLevel2 = buyPrice * _d(0.90)
            buyLevel3 = buyPrice * _d(0.85)

            buySpend1 = baseBalance * _d(0.20)	# How much to spend at buyLevel1 price.
            buySpend2 = baseBalance * _d(0.30)	# How much to spend at buyLevel2 price.
            buySpend3 = baseBalance * _d(0.50)	# How much to spend at buyLevel3 price.

            sellLevel = buyPrice * _d(1.05)

            sellLevel = round(sellLevel, 10)
            print colored('Waiting to buy at', "blue"), buyLevel1, buyLevel2, buyLevel3

            time.sleep(3)
            currentPrice = market.price(asset, otherasset)
            print symbol, '=', currentPrice, '   (', currentPrice / buyPrice, ' since 1 minute ago)'
            print 'Open buys:', openBuys

            for buyLevel, buyPrice in openBuys.items():
                if buyPrice > 0 and currentPrice >= buyPrice:
                    print 'Cleared buyLevel', buyLevel
                    openBuys[buyLevel] = 0

            wantQty = 0
            if currentPrice <= buyLevel3 and not openBuys.get(3):
                wantQty = buySpend3 / currentPrice
                print 'Hit buyLevel3', wantQty, asset
                buyLevel = 3

            elif currentPrice <= buyLevel2 and not openBuys.get(2):
                wantQty = buySpend2 / currentPrice
                print 'Hit buyLevel2', wantQty, asset
                buyLevel = 2

            elif currentPrice <= buyLevel1 and not openBuys.get(1):
                wantQty = buySpend1 / currentPrice
                print 'Hit buyLevel1', wantQty, asset
                buyLevel = 1

            if wantQty:
                qty = round(_d(wantQty), lotSizeStepNumDigits)
                print 'Buying', qty, 'of', asset, 'to sell for', sellLevel

                order = client.create_order(
                    symbol=symbol,
                    side=Client.SIDE_BUY,
                    type=Client.ORDER_TYPE_MARKET,
                    quantity=float(qty)
                )

                print colored('Will sell at', "blue"), '{0:f}'.format(sellLevel)
                time.sleep(5)

                order = client.create_order(
                    symbol=symbol,
                    side=Client.SIDE_SELL,
                    type=Client.ORDER_TYPE_LIMIT,
                    timeInForce='GTC',
                    price='{0:f}'.format(sellLevel),
                    quantity='{0:f}'.format(qty)
                )

                openBuys[buyLevel] = sellLevel

                balance = (client.get_asset_balance(asset))
                balance = float(balance['free'])
                otherbalance = (client.get_asset_balance(otherasset))
                otherbalance = float(otherbalance['free'])


for asset in ['ADA',
         'ADX',
         'AE',
         'AION',
         'AMB',
         'APPC',
         'ARK',
         'ARN',
         'AST',
         'BAT',
         'BCC',
         'BCD',
         'BCPT',
         'BLZ',
         'BNB',
         'BNT',
         'BQX',
         'BRD',
         'BTG',
         'BTS',
         'CDT',
         'CHAT',
         'CMT',
         'CND',
         'CTR',
         'DASH',
         'DGD',
         'DLT',
         'DNT',
         'EDO',
         'ELF',
         'ENG',
         'ENJ',
         'EOS',
         'ETC',
         'ETH',
         'EVX',
         'FUEL',
         'FUN',
         'GAS',
         'GTO',
         'GVT',
         'GXS',
         'HSR',
         'ICN',
         'ICX',
         'INS',
         'IOST',
         'IOTA',
         'KMD',
         'KNC',
         'LEND',
         'LINK',
         'LRC',
         'LSK',
         'LTC',
         'LUN',
         'MANA',
         'MCO',
         'MDA',
         'MOD',
         'MTH',
         'MTL',
         'NANO',
         'NAV',
         'NEBL',
         'NEO',
         'NULS',
         'OAX',
         'OMG',
         'OST',
         'PIVX',
         'POE',
         'POWR',
         'PPT',
         'QSP',
         'QTUM',
         'RCN',
         'RDN',
         'REQ',
         'RLC',
         'SALT',
         'SNGLS',
         'SNM',
         'SNT',
         'STEEM',
         'STORJ',
         'STRAT',
         'SUB',
         'TNB',
         'TNT',
         'TRIG',
         'TRX',
         'VEN',
         'VIA',
         'VIB',
         'VIBE',
         'WABI',
         'WAVES',
         'WINGS',
         'WTC',
         'XLM',
         'XMR',
         'XRP',
         'XVG',
         'XZC',
         'YOYO',
         'ZEC',
         'ZRX']:

    strat = Strategy1()
    strat.asset = asset
    strat.start()
