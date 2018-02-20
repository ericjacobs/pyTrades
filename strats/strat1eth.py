
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
from pyTrades.util import reporter
from pyTrades.util import market
from pyTrades.strats import abstract


class Strategy1ETH(abstract.AbstractStrategy):

    # Asset will be set in the loop at the end of this file.
    asset = None

    # Asset you are buying with -- will be set in the loop at the end of
    # this file.
    otherasset = None

    def trades(self, delayTime):
        asset = self.asset
        otherasset = self.otherasset

        # Calculate pair you're trading
        symbol = asset + otherasset
        
        time.sleep(delayTime)
        print colored('Initializing', "cyan")

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

        notionalFilter = symbolFilters.get('MIN_NOTIONAL', {})
        minNotional = float(notionalFilter.get('minNotional', 0.0))

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
            movingAvg = market.movingAverage(asset, otherasset, mins=7)

            buyLevel1 = buyPrice * _d(0.97)
            buyLevel2 = buyPrice * _d(0.95)
            buyLevel3 = buyPrice * _d(0.93)

            buySpend1 = baseBalance * _d(0.20)	# How much to spend at buyLevel1 price.
            buySpend2 = baseBalance * _d(0.30)	# How much to spend at buyLevel2 price.
            buySpend3 = baseBalance * _d(0.50)	# How much to spend at buyLevel3 price.

            print colored('Waiting to buy at', "blue"), buyLevel1, buyLevel2, buyLevel3

            time.sleep(3)
            currentPrice = market.price(asset, otherasset)
            print symbol, '=', currentPrice, ' (7 min MA=', movingAvg, ')',
            if currentPrice > movingAvg:
                print '  skipping due to being above MA'
                continue

            print '   MA okay (', currentPrice / buyPrice, ' since 1 minute ago)'
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
                sellLevel = currentPrice * _d(1.03)
                sellLevel = round(sellLevel, 10)

                qty = round(_d(wantQty), lotSizeStepNumDigits)
                if qty < lotSizeMinQty:
                    print colored('Not buying %s due to being less than min qty %s' % (qty, lotSizeMinQty), 'yellow')
                    continue
                if (qty * sellLevel) < minNotional:
                    print colored('Not buying %s due to being less than min notional %s' % (qty, minNotional), 'yellow')
                    continue

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
                    price='{0:.10f}'.format(sellLevel),
                    quantity='{0:f}'.format(qty)
                )
                
                openBuys[buyLevel] = sellLevel
                reporter.reportBuy(asset, otherasset, qty, sellLevel, currentPrice, buyPrice, buyLevel)

                balance = (client.get_asset_balance(asset))
                balance = float(balance['free'])
                otherbalance = (client.get_asset_balance(otherasset))
                otherbalance = float(otherbalance['free'])


for n, assetPair in enumerate([
        (u'QTUM', u'ETH'),
        (u'EOS', u'ETH'),
        (u'SNT', u'ETH'),
        (u'BNT', u'ETH'),
        (u'BNB', u'ETH'),
        (u'OAX', u'ETH'),
        (u'DNT', u'ETH'),
        (u'MCO', u'ETH'),
        (u'ICN', u'ETH'),
        (u'WTC', u'ETH'),
        (u'LRC', u'ETH'),
        (u'OMG', u'ETH'),
        (u'ZRX', u'ETH'),
        (u'STRAT', u'ETH'),
        (u'SNGLS', u'ETH'),
        (u'BQX', u'ETH'),
        (u'KNC', u'ETH'),
        (u'FUN', u'ETH'),
        (u'SNM', u'ETH'),
        (u'NEO', u'ETH'),
        (u'IOTA', u'ETH'),
        (u'LINK', u'ETH'),
        (u'XVG', u'ETH'),
        (u'CTR', u'ETH'),
        (u'SALT', u'ETH'),
        (u'MDA', u'ETH'),
        (u'MTL', u'ETH'),
        (u'SUB', u'ETH'),
        (u'ETC', u'ETH'),
        (u'MTH', u'ETH'),
        (u'ENG', u'ETH'),
        (u'ZEC', u'ETH'),
        (u'AST', u'ETH'),
        (u'DASH', u'ETH'),
        (u'BTG', u'ETH'),
        (u'EVX', u'ETH'),
        (u'REQ', u'ETH'),
        (u'VIB', u'ETH'),
        (u'HSR', u'ETH'),
        (u'TRX', u'ETH'),
        (u'POWR', u'ETH'),
        (u'ARK', u'ETH'),
        (u'YOYO', u'ETH'),
        (u'XRP', u'ETH'),
        (u'MOD', u'ETH'),
        (u'ENJ', u'ETH'),
        (u'STORJ', u'ETH'),
        (u'VEN', u'ETH'),
        (u'KMD', u'ETH'),
        (u'RCN', u'ETH'),
        (u'NULS', u'ETH'),
        (u'RDN', u'ETH'),
        (u'XMR', u'ETH'),
        (u'DLT', u'ETH'),
        (u'AMB', u'ETH'),
        (u'BCC', u'ETH'),
        (u'BAT', u'ETH'),
        (u'BCPT', u'ETH'),
        (u'ARN', u'ETH'),
        (u'GVT', u'ETH'),
        (u'CDT', u'ETH'),
        (u'GXS', u'ETH'),
        (u'POE', u'ETH'),
        (u'QSP', u'ETH'),
        (u'BTS', u'ETH'),
        (u'XZC', u'ETH'),
        (u'LSK', u'ETH'),
        (u'TNT', u'ETH'),
        (u'FUEL', u'ETH'),
        (u'MANA', u'ETH'),
        (u'BCD', u'ETH'),
        (u'DGD', u'ETH'),
        (u'ADX', u'ETH'),
        (u'ADA', u'ETH'),
        (u'PPT', u'ETH'),
        (u'CMT', u'ETH'),
        (u'XLM', u'ETH'),
        (u'CND', u'ETH'),
        (u'LEND', u'ETH'),
        (u'WABI', u'ETH'),
        (u'LTC', u'ETH'),
        (u'TNB', u'ETH'),
        (u'WAVES', u'ETH'),
        (u'GTO', u'ETH'),
        (u'ICX', u'ETH'),
        (u'OST', u'ETH'),
        (u'ELF', u'ETH'),
        (u'AION', u'ETH'),
        (u'NEBL', u'ETH'),
        (u'BRD', u'ETH'),
        (u'EDO', u'ETH'),
        (u'WINGS', u'ETH'),
        (u'NAV', u'ETH'),
        (u'LUN', u'ETH'),
        (u'TRIG', u'ETH'),
        (u'APPC', u'ETH'),
        (u'VIBE', u'ETH'),
        (u'RLC', u'ETH'),
        (u'INS', u'ETH'),
        (u'PIVX', u'ETH'),
        (u'IOST', u'ETH'),
        (u'CHAT', u'ETH'),
        (u'STEEM', u'ETH'),
        (u'NANO', u'ETH'),
        (u'VIA', u'ETH'),
        (u'BLZ', u'ETH'),
        (u'AE', u'ETH'),
        (u'RPX', u'ETH')
    ]):

    strat = Strategy1ETH()
    strat.asset = assetPair[0]
    strat.otherasset = assetPair[1]
    strat.start(delayTime=1 + n * 4)
