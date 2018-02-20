
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


class Strategy1BTC(abstract.AbstractStrategy):

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
        precision = int(symbolInfo['quotePrecision']) - 1

        priceFilter = symbolFilters.get('PRICE_FILTER', {})
        tickSize = float(priceFilter.get('tickSize', 0.0))

        # This is the number of digits we should round to in order
        # to conform to the lot's stepSize restriction.
        lotSizeStepNumDigits = int(round(-math.log(lotSizeStep, 10)))
        tickSizeNumDigits = int(round(-math.log(tickSize, 10)))

        # Do a random wait to avoid slamming the server on startup.
        time.sleep(random.randrange(2, 200))

        print colored('Initializing - step 3', "cyan")

        numberOfBuys = 0
        otherbalance = (client.get_asset_balance(otherasset))
        otherbalance = _d(otherbalance['free'])

        # How much of otherasset (e.g. BTC) we want to work with, expressed as
        # fraction of the current balance of otherasset.
        baseBalanceFraction = _d(0.9)
        baseBalance = otherbalance * baseBalanceFraction

        cycle = 0
        actions = []
        openBuys = {}

        print colored('Auto Trading with binance', "cyan")
        print 'Trading with', baseBalance, 'of', otherasset

        while True:
            # Memory cleanup.
            market.deleteOlderThan(asset, otherasset, minsAgo=10)

            buyPrice = market.price(asset, otherasset, minsAgo=1)
            movingAvg = market.movingAverage(asset, otherasset, mins=7)

            buyLevel1 = buyPrice * _d(0.985)
            buyLevel2 = buyPrice * _d(0.975)
            buyLevel3 = buyPrice * _d(0.96)

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
                sellLevel = currentPrice * _d(1.015)
                sellLevel = round(_d(sellLevel), tickSizeNumDigits)

                qty = round(_d(wantQty), lotSizeStepNumDigits)
                if qty < lotSizeMinQty:
                    print colored('Not buying %s due to being less than min qty %s' % (qty, lotSizeMinQty), 'yellow')
                    continue
                if (qty * sellLevel) < minNotional:
                    print colored('Not buying %s due to being less than min notional %s' % (qty, minNotional), 'yellow')
                    continue

                print 'Buying', qty, 'of', asset, 'to sell for', sellLevel
                
                try:
                    order = client.create_order(
                        symbol=symbol,
                        side=Client.SIDE_BUY,
                        type=Client.ORDER_TYPE_MARKET,
                        quantity=float(qty)
                    )
                except Exception, e:
                    print 'Exception', e
                    time.sleep(1)
                    continue

                print colored('Will sell at', "blue"), '{0:f}'.format(sellLevel)
                time.sleep(5)
                
                order = client.create_order(
                    symbol=symbol,
                    side=Client.SIDE_SELL,
                    type=Client.ORDER_TYPE_LIMIT,
                    timeInForce='GTC',
                    price='{:0.0{}f}'.format(sellLevel, precision),
                    quantity='{0:f}'.format(qty)
                )
                
                openBuys[buyLevel] = sellLevel
                reporter.reportBuy(asset, otherasset, qty, sellLevel, currentPrice, buyPrice, buyLevel)

                balance = (client.get_asset_balance(asset))
                balance = float(balance['free'])
                otherbalance = (client.get_asset_balance(otherasset))
                otherbalance = float(otherbalance['free'])


for n, assetPair in enumerate([
        (u'LTC', u'BTC'),
        (u'BNB', u'BTC'),
        (u'NEO', u'BTC'),
        (u'BCC', u'BTC'),
        (u'GAS', u'BTC'),
        (u'HSR', u'BTC'),
        (u'MCO', u'BTC'),
        (u'WTC', u'BTC'),
        (u'LRC', u'BTC'),
        (u'QTUM', u'BTC'),
        (u'YOYO', u'BTC'),
        (u'OMG', u'BTC'),
        (u'ZRX', u'BTC'),
        (u'STRAT', u'BTC'),
        (u'SNGLS', u'BTC'),
        (u'BQX', u'BTC'),
        (u'KNC', u'BTC'),
        (u'FUN', u'BTC'),
        (u'SNM', u'BTC'),
        (u'IOTA', u'BTC'),
        (u'LINK', u'BTC'),
        (u'XVG', u'BTC'),
        (u'CTR', u'BTC'),
        (u'SALT', u'BTC'),
        (u'MDA', u'BTC'),
        (u'MTL', u'BTC'),
        (u'SUB', u'BTC'),
        (u'EOS', u'BTC'),
        (u'SNT', u'BTC'),
        (u'ETC', u'BTC'),
        (u'MTH', u'BTC'),
        (u'ENG', u'BTC'),
        (u'DNT', u'BTC'),
        (u'ZEC', u'BTC'),
        (u'BNT', u'BTC'),
        (u'AST', u'BTC'),
        (u'DASH', u'BTC'),
        (u'OAX', u'BTC'),
        (u'ICN', u'BTC'),
        (u'BTG', u'BTC'),
        (u'EVX', u'BTC'),
        (u'REQ', u'BTC'),
        (u'VIB', u'BTC'),
        (u'TRX', u'BTC'),
        (u'POWR', u'BTC'),
        (u'ARK', u'BTC'),
        (u'XRP', u'BTC'),
        (u'MOD', u'BTC'),
        (u'ENJ', u'BTC'),
        (u'STORJ', u'BTC'),
        (u'VEN', u'BTC'),
        (u'KMD', u'BTC'),
        (u'RCN', u'BTC'),
        (u'NULS', u'BTC'),
        (u'RDN', u'BTC'),
        (u'XMR', u'BTC'),
        (u'DLT', u'BTC'),
        (u'AMB', u'BTC'),
        (u'BAT', u'BTC'),
        (u'BCPT', u'BTC'),
        (u'ARN', u'BTC'),
        (u'GVT', u'BTC'),
        (u'CDT', u'BTC'),
        (u'GXS', u'BTC'),
        (u'POE', u'BTC'),
        (u'QSP', u'BTC'),
        (u'BTS', u'BTC'),
        (u'XZC', u'BTC'),
        (u'LSK', u'BTC'),
        (u'TNT', u'BTC'),
        (u'FUEL', u'BTC'),
        (u'MANA', u'BTC'),
        (u'BCD', u'BTC'),
        (u'DGD', u'BTC'),
        (u'ADX', u'BTC'),
        (u'ADA', u'BTC'),
        (u'PPT', u'BTC'),
        (u'CMT', u'BTC'),
        (u'XLM', u'BTC'),
        (u'CND', u'BTC'),
        (u'LEND', u'BTC'),
        (u'WABI', u'BTC'),
        (u'TNB', u'BTC'),
        (u'WAVES', u'BTC'),
        (u'GTO', u'BTC'),
        (u'ICX', u'BTC'),
        (u'OST', u'BTC'),
        (u'ELF', u'BTC'),
        (u'AION', u'BTC'),
        (u'NEBL', u'BTC'),
        (u'BRD', u'BTC'),
        (u'EDO', u'BTC'),
        (u'WINGS', u'BTC'),
        (u'NAV', u'BTC'),
        (u'LUN', u'BTC'),
        (u'TRIG', u'BTC'),
        (u'APPC', u'BTC'),
        (u'VIBE', u'BTC'),
        (u'RLC', u'BTC'),
        (u'INS', u'BTC'),
        (u'PIVX', u'BTC'),
        (u'IOST', u'BTC'),
        (u'CHAT', u'BTC'),
        (u'STEEM', u'BTC'),
        (u'NANO', u'BTC'),
        (u'VIA', u'BTC'),
        (u'BLZ', u'BTC'),
        (u'AE', u'BTC'),
        (u'RPX', u'BTC')
    ]):

    strat = Strategy1BTC()
    strat.asset = assetPair[0]
    strat.otherasset = assetPair[1]
    strat.start(delayTime=n * 4)
