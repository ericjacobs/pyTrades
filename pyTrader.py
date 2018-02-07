
import sys
import math
import time

from decimal import Decimal as _d
from binance.client import Client
from termcolor import colored

from binance_api import client
import market


class Strategy:

    def trades(self):
        # Change this to change the asset you're buying
        asset = "LTC"
        # Change this to change the asset you're paying with
        otherasset = "BTC"

        # Calculate pair you're trading
        symbol = asset + otherasset

        balance= (client.get_asset_balance(asset))
        balance = float(balance['free'])
        startBalance=(client.get_asset_balance(asset))
        startBalance= float(startBalance['free'])
        #lastPrice = float(Orders.get_ticker(symbol)['lastPrice'])
        currentPrice = client.get_ticker(symbol =symbol)
        currentPrice=float(currentPrice['lastPrice'])

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

        numberOfBuys = 0
        otherbalance = (client.get_asset_balance(otherasset))
        otherbalance = _d(otherbalance['free'])

        # How much of otherasset (e.g. BTC) we want to work with, expressed as
        # fraction of the current balance of otherasset.
        baseBalanceFraction = _d(0.2)       # 20% of current balance
        baseBalance = otherbalance * baseBalanceFraction

        cycle = 0
        actions = []
        openBuys = {}

        print colored('Auto Trading with binance', "cyan")
        print 'Trading with', baseBalance, 'of', otherasset

        while True:
            buyPrice = market.price(asset, otherasset, minsAgo=5)

            buyLevel1 = buyPrice * _d(0.995)
            buyLevel2 = buyPrice * _d(0.99)
            buyLevel3 = buyPrice * _d(0.985)

            buySpend1 = baseBalance * _d(0.20)	# How much to spend at buyLevel1 price.
            buySpend2 = baseBalance * _d(0.30)	# How much to spend at buyLevel2 price.
            buySpend3 = baseBalance * _d(0.50)	# How much to spend at buyLevel3 price.

            sellLevel = buyPrice * _d(1.005)

            sellLevel = round(sellLevel, 10)
            print colored('Waiting to buy at', "blue"), buyLevel1, buyLevel2, buyLevel3

            time.sleep(3)
            currentPrice = market.price(asset, otherasset)
            print symbol, '=', currentPrice, '   (', currentPrice / buyPrice, ' since 5 mins ago)'
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


strat = Strategy()
strat.trades()
