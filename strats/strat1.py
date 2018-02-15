
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

            buyLevel1 = buyPrice * _d(0.99)
            buyLevel2 = buyPrice * _d(0.98)
            buyLevel3 = buyPrice * _d(0.97)

            buySpend1 = baseBalance * _d(0.25)	# How much to spend at buyLevel1 price.
            buySpend2 = baseBalance * _d(0.50)	# How much to spend at buyLevel2 price.
            buySpend3 = baseBalance * _d(0.50)	# How much to spend at buyLevel3 price.

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
                sellLevel = currentPrice * _d(1.01)
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
                    price='{0:f}'.format(sellLevel),
                    quantity='{0:f}'.format(qty)
                )

                openBuys[buyLevel] = sellLevel

                balance = (client.get_asset_balance(asset))
                balance = float(balance['free'])
                otherbalance = (client.get_asset_balance(otherasset))
                otherbalance = float(otherbalance['free'])


for n, assetPair in enumerate([
        (u'LTC', u'BTC'),
        (u'BNB', u'BTC'),
        (u'NEO', u'BTC'),
        (u'QTUM', u'ETH'),
        (u'EOS', u'ETH'),
        (u'SNT', u'ETH'),
        (u'BNT', u'ETH'),
        (u'BCC', u'BTC'),
        (u'GAS', u'BTC'),
        (u'BNB', u'ETH'),
        (u'HSR', u'BTC'),
        (u'OAX', u'ETH'),
        (u'DNT', u'ETH'),
        (u'MCO', u'ETH'),
        (u'ICN', u'ETH'),
        (u'MCO', u'BTC'),
        (u'WTC', u'BTC'),
        (u'WTC', u'ETH'),
        (u'LRC', u'BTC'),
        (u'LRC', u'ETH'),
        (u'QTUM', u'BTC'),
        (u'YOYO', u'BTC'),
        (u'OMG', u'BTC'),
        (u'OMG', u'ETH'),
        (u'ZRX', u'BTC'),
        (u'ZRX', u'ETH'),
        (u'STRAT', u'BTC'),
        (u'STRAT', u'ETH'),
        (u'SNGLS', u'BTC'),
        (u'SNGLS', u'ETH'),
        (u'BQX', u'BTC'),
        (u'BQX', u'ETH'),
        (u'KNC', u'BTC'),
        (u'KNC', u'ETH'),
        (u'FUN', u'BTC'),
        (u'FUN', u'ETH'),
        (u'SNM', u'BTC'),
        (u'SNM', u'ETH'),
        (u'NEO', u'ETH'),
        (u'IOTA', u'BTC'),
        (u'IOTA', u'ETH'),
        (u'LINK', u'BTC'),
        (u'LINK', u'ETH'),
        (u'XVG', u'BTC'),
        (u'XVG', u'ETH'),
        (u'CTR', u'BTC'),
        (u'CTR', u'ETH'),
        (u'SALT', u'BTC'),
        (u'SALT', u'ETH'),
        (u'MDA', u'BTC'),
        (u'MDA', u'ETH'),
        (u'MTL', u'BTC'),
        (u'MTL', u'ETH'),
        (u'SUB', u'BTC'),
        (u'SUB', u'ETH'),
        (u'EOS', u'BTC'),
        (u'SNT', u'BTC'),
        (u'ETC', u'ETH'),
        (u'ETC', u'BTC'),
        (u'MTH', u'BTC'),
        (u'MTH', u'ETH'),
        (u'ENG', u'BTC'),
        (u'ENG', u'ETH'),
        (u'DNT', u'BTC'),
        (u'ZEC', u'BTC'),
        (u'ZEC', u'ETH'),
        (u'BNT', u'BTC'),
        (u'AST', u'BTC'),
        (u'AST', u'ETH'),
        (u'DASH', u'BTC'),
        (u'DASH', u'ETH'),
        (u'OAX', u'BTC'),
        (u'ICN', u'BTC'),
        (u'BTG', u'BTC'),
        (u'BTG', u'ETH'),
        (u'EVX', u'BTC'),
        (u'EVX', u'ETH'),
        (u'REQ', u'BTC'),
        (u'REQ', u'ETH'),
        (u'VIB', u'BTC'),
        (u'VIB', u'ETH'),
        (u'HSR', u'ETH'),
        (u'TRX', u'BTC'),
        (u'TRX', u'ETH'),
        (u'POWR', u'BTC'),
        (u'POWR', u'ETH'),
        (u'ARK', u'BTC'),
        (u'ARK', u'ETH'),
        (u'YOYO', u'ETH'),
        (u'XRP', u'BTC'),
        (u'XRP', u'ETH'),
        (u'MOD', u'BTC'),
        (u'MOD', u'ETH'),
        (u'ENJ', u'BTC'),
        (u'ENJ', u'ETH'),
        (u'STORJ', u'BTC'),
        (u'STORJ', u'ETH'),
        (u'VEN', u'BNB'),
        (u'YOYO', u'BNB'),
        (u'POWR', u'BNB'),
        (u'VEN', u'BTC'),
        (u'VEN', u'ETH'),
        (u'KMD', u'BTC'),
        (u'KMD', u'ETH'),
        (u'NULS', u'BNB'),
        (u'RCN', u'BTC'),
        (u'RCN', u'ETH'),
        (u'RCN', u'BNB'),
        (u'NULS', u'BTC'),
        (u'NULS', u'ETH'),
        (u'RDN', u'BTC'),
        (u'RDN', u'ETH'),
        (u'RDN', u'BNB'),
        (u'XMR', u'BTC'),
        (u'XMR', u'ETH'),
        (u'DLT', u'BNB'),
        (u'WTC', u'BNB'),
        (u'DLT', u'BTC'),
        (u'DLT', u'ETH'),
        (u'AMB', u'BTC'),
        (u'AMB', u'ETH'),
        (u'AMB', u'BNB'),
        (u'BCC', u'ETH'),
        (u'BCC', u'BNB'),
        (u'BAT', u'BTC'),
        (u'BAT', u'ETH'),
        (u'BAT', u'BNB'),
        (u'BCPT', u'BTC'),
        (u'BCPT', u'ETH'),
        (u'BCPT', u'BNB'),
        (u'ARN', u'BTC'),
        (u'ARN', u'ETH'),
        (u'GVT', u'BTC'),
        (u'GVT', u'ETH'),
        (u'CDT', u'BTC'),
        (u'CDT', u'ETH'),
        (u'GXS', u'BTC'),
        (u'GXS', u'ETH'),
        (u'NEO', u'BNB'),
        (u'POE', u'BTC'),
        (u'POE', u'ETH'),
        (u'QSP', u'BTC'),
        (u'QSP', u'ETH'),
        (u'QSP', u'BNB'),
        (u'BTS', u'BTC'),
        (u'BTS', u'ETH'),
        (u'BTS', u'BNB'),
        (u'XZC', u'BTC'),
        (u'XZC', u'ETH'),
        (u'XZC', u'BNB'),
        (u'LSK', u'BTC'),
        (u'LSK', u'ETH'),
        (u'LSK', u'BNB'),
        (u'TNT', u'BTC'),
        (u'TNT', u'ETH'),
        (u'FUEL', u'BTC'),
        (u'FUEL', u'ETH'),
        (u'MANA', u'BTC'),
        (u'MANA', u'ETH'),
        (u'BCD', u'BTC'),
        (u'BCD', u'ETH'),
        (u'DGD', u'BTC'),
        (u'DGD', u'ETH'),
        (u'IOTA', u'BNB'),
        (u'ADX', u'BTC'),
        (u'ADX', u'ETH'),
        (u'ADX', u'BNB'),
        (u'ADA', u'BTC'),
        (u'ADA', u'ETH'),
        (u'PPT', u'BTC'),
        (u'PPT', u'ETH'),
        (u'CMT', u'BTC'),
        (u'CMT', u'ETH'),
        (u'CMT', u'BNB'),
        (u'XLM', u'BTC'),
        (u'XLM', u'ETH'),
        (u'XLM', u'BNB'),
        (u'CND', u'BTC'),
        (u'CND', u'ETH'),
        (u'CND', u'BNB'),
        (u'LEND', u'BTC'),
        (u'LEND', u'ETH'),
        (u'WABI', u'BTC'),
        (u'WABI', u'ETH'),
        (u'WABI', u'BNB'),
        (u'LTC', u'ETH'),
        (u'LTC', u'BNB'),
        (u'TNB', u'BTC'),
        (u'TNB', u'ETH'),
        (u'WAVES', u'BTC'),
        (u'WAVES', u'ETH'),
        (u'WAVES', u'BNB'),
        (u'GTO', u'BTC'),
        (u'GTO', u'ETH'),
        (u'GTO', u'BNB'),
        (u'ICX', u'BTC'),
        (u'ICX', u'ETH'),
        (u'ICX', u'BNB'),
        (u'OST', u'BTC'),
        (u'OST', u'ETH'),
        (u'OST', u'BNB'),
        (u'ELF', u'BTC'),
        (u'ELF', u'ETH'),
        (u'AION', u'BTC'),
        (u'AION', u'ETH'),
        (u'AION', u'BNB'),
        (u'NEBL', u'BTC'),
        (u'NEBL', u'ETH'),
        (u'NEBL', u'BNB'),
        (u'BRD', u'BTC'),
        (u'BRD', u'ETH'),
        (u'BRD', u'BNB'),
        (u'MCO', u'BNB'),
        (u'EDO', u'BTC'),
        (u'EDO', u'ETH'),
        (u'WINGS', u'BTC'),
        (u'WINGS', u'ETH'),
        (u'NAV', u'BTC'),
        (u'NAV', u'ETH'),
        (u'NAV', u'BNB'),
        (u'LUN', u'BTC'),
        (u'LUN', u'ETH'),
        (u'TRIG', u'BTC'),
        (u'TRIG', u'ETH'),
        (u'TRIG', u'BNB'),
        (u'APPC', u'BTC'),
        (u'APPC', u'ETH'),
        (u'APPC', u'BNB'),
        (u'VIBE', u'BTC'),
        (u'VIBE', u'ETH'),
        (u'RLC', u'BTC'),
        (u'RLC', u'ETH'),
        (u'RLC', u'BNB'),
        (u'INS', u'BTC'),
        (u'INS', u'ETH'),
        (u'PIVX', u'BTC'),
        (u'PIVX', u'ETH'),
        (u'PIVX', u'BNB'),
        (u'IOST', u'BTC'),
        (u'IOST', u'ETH'),
        (u'CHAT', u'BTC'),
        (u'CHAT', u'ETH'),
        (u'STEEM', u'BTC'),
        (u'STEEM', u'ETH'),
        (u'STEEM', u'BNB'),
        (u'NANO', u'BTC'),
        (u'NANO', u'ETH'),
        (u'NANO', u'BNB'),
        (u'VIA', u'BTC'),
        (u'VIA', u'ETH'),
        (u'VIA', u'BNB'),
        (u'BLZ', u'BTC'),
        (u'BLZ', u'ETH'),
        (u'BLZ', u'BNB'),
        (u'AE', u'BTC'),
        (u'AE', u'ETH'),
        (u'AE', u'BNB'),
        (u'RPX', u'BTC'),
        (u'RPX', u'ETH'),
        (u'RPX', u'BNB')
    ]):

    strat = Strategy1()
    strat.asset = assetPair[0]
    strat.otherasset = assetPair[1]
    strat.start(delayTime=n * 4)
