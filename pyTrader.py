import sys

#sys.path.insert(0, './app')

from termcolor import colored



from binance.client import Client


from apikeys import api_key, api_secret

import math
import time


class Strategy:

    def trades(self):
        client = Client(api_key, api_secret)
        # Change this to change the asset you're buying
        asset = "BNB"
        # Change this to change the asset you're paying with
        otherasset = "USDT"

        # Calculate pair you're trading
        symbol = asset + otherasset

        balance= (client.get_asset_balance(asset))
        balance = float(balance['free'])
        startBalance=(client.get_asset_balance(asset))
        startBalance= float(startBalance['free'])
        #lastPrice = float(Orders.get_ticker(symbol)['lastPrice'])
        currentPrice = client.get_ticker(symbol =symbol)
        currentPrice=float(currentPrice['lastPrice'])
        #MANUALLY CHANGE LINE 37 TO WHAT YOU WANT
        firstBuyPrice = 13.5

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
        balances = client.get_account()

        # How much of asset we want to work with.
        wantedBalance = 8

        buyLevel1 = firstBuyPrice * 0.995	# 0.5%
        buyLevel2 = firstBuyPrice * 0.99	# 1.0%
        buyLevel3 = firstBuyPrice * 0.985	# 1.5%

        buyAmount1 = wantedBalance * 0.25	# How much to buy at buyLevel1 price.
        buyAmount2 = wantedBalance * 0.35	# How much to buy at buyLevel2 price.
        buyAmount3 = wantedBalance * 0.50	# How much to buy at buyLevel3 price.


        # TODO: Remove Certainty processing.
        lowCertainty = firstBuyPrice * .02
        highCertainty = firstBuyPrice * .03
        sellLevel = firstBuyPrice * 1.002

        buylowCertainty= float(round((balance * 0.05)/currentPrice))
        buyhighCertainty= float(round((balance * 0.10)/currentPrice))
        sellhighAmount= float(round(balance * 0.95))

        lowCounter= 0
        highCounter= 0
        sellcounter = 0

        cycle = 0
        actions = []

        otherbalance= (client.get_asset_balance(otherasset))
        otherbalance = float(otherbalance['free'])

        if balance < wantedBalance:

            print colored('Auto Trading with binance', "cyan")
            print colored('Waiting to buy at', "blue"), buyLevel1, buyLevel2, buyLevel3
            print colored('Waiting to sell at', "blue"), sellLevel

            while balance < wantedBalance:

                time.sleep(5)
                currentPrice = client.get_ticker(symbol=symbol)
                currentPrice = float(currentPrice['lastPrice'])

                print 'balance=', balance, asset, '  otherbalance=', otherbalance, otherasset
                print 'currentPrice=', currentPrice, ' buyLevels=', buyLevel1, buyLevel2, buyLevel3

                canBuy = round(otherbalance / currentPrice, lotSizeStepNumDigits)
                print 'We can now buy (up to)', canBuy, 'of', asset

                if currentPrice <= buyLevel3:
                    qty = min(canBuy, wantedBalance * 0.50)
                    print 'Hit buyLevel3', qty

                    order = client.create_order(
                        symbol=symbol,
                        side= Client.SIDE_BUY,
                        type=Client.ORDER_TYPE_MARKET,
                        quantity=qty
                    )
                    buyLevel3 = 0

                    balance = (client.get_asset_balance(asset))
                    balance = float(balance['free'])
                    otherbalance = (client.get_asset_balance(otherasset))
                    otherbalance = float(otherbalance['free'])
                    break

                elif currentPrice <= buyLevel2:
                    qty = min(canBuy, wantedBalance * 0.35)
                    print 'Hit buyLevel2', qty

                    order = client.create_order(
                        symbol=symbol,
                        side= Client.SIDE_BUY,
                        type=Client.ORDER_TYPE_MARKET,
                        quantity=qty
                    )
                    buyLevel2 = 0

                elif currentPrice <= buyLevel1:
                    qty = min(canBuy, wantedBalance * 0.25)
                    print 'Hit buyLevel1', qty

                    order = client.create_order(
                        symbol=symbol,
                        side= Client.SIDE_BUY,
                        type=Client.ORDER_TYPE_MARKET,
                        quantity=min(canBuy, wantedBalance * 0.25)
                    )
                    buyLevel1 = 0

                elif currentPrice >= sellLevel and balance > lotSizeMinQty:
                    qty = round(balance * 0.95, lotSizeStepNumDigits)

                    print colored('TEST-sellLevel exceeded', "blue"),
                    print qty
                    order = client.create_order(
                        symbol=symbol,
                        side= Client.SIDE_SELL,
                        type=Client.ORDER_TYPE_MARKET,
                        quantity=qty
                    )
                    print colored('sold at ' + str(currentPrice), "blue")
                    #increase count
                    sellcounter= sellcounter + 1

                balance = (client.get_asset_balance(asset))
                balance = float(balance['free'])
                otherbalance = (client.get_asset_balance(otherasset))
                otherbalance = float(otherbalance['free'])

        print colored('Auto Trading with binance', "cyan")
        print colored('Waiting to sell at', "blue")
        print sellLevel

        while balance>= (startBalance/2):

            time.sleep(5)
            currentPrice = client.get_ticker(symbol =symbol)
            currentPrice=float(currentPrice['lastPrice'])

            print 'balance=', balance
            print 'currentPrice=', currentPrice, '  sellLevel=', sellLevel

            #Line 61 is not getting triggered all other statements seem fine
            if currentPrice >= sellLevel:
                #it never prints this. WHY? Code has forsaken me!
                print colored('TEST', "blue")
                order = client.create_order(
                    symbol=symbol,
                    side= Client.SIDE_SELL,
                    type=Client.ORDER_TYPE_MARKET,
                    quantity=sellhighAmount
                )
                print colored('sold at ' + str(currentPrice), "blue")
                #increase count
                sellcounter= sellcounter + 1
                #recheck balance
                balance= (client.get_asset_balance(asset))
                balance = float(balance['free'])

            continue

            #
            # TODO: Convert remaining code in this block to new three-level
            # strategy.
            #

            #Checks to see if it should buy at low settings
            if lowCounter <= 1 and currentPrice< highCertainty:
                if currentPrice >= lowCertainty and currentPrice< highCertainty:
                    order = client.create_order(
                    symbol=symbol,
                    side= Client.SIDE_BUY,
                    type=Client.ORDER_TYPE_MARKET,
                    quantity=buylowCertainty
                )
                    firstBuyPrice = currentPrice
                    print colored('bought at low certainty', "blue")
                    #recheck the balance
                    balance= (client.get_asset_balance(asset))
                    balance = float(balance['free'])
                    #increase count
                    lowCounter= lowCounter +1
                    print colored('Bought at', "green")
                    print  firstBuyPrice
                    print colored('Waiting to sell at', "blue")
                    print  sellLevel

             #Checks to see if it should buy at high settings
            elif currentPrice>= highCertainty and currentPrice < sellLevel and highCounter < 1:
                order = client.create_order(
                symbol='BTCUSDT',
                side= Client.SIDE_BUY,
                type=Client.ORDER_TYPE_MARKET,
                quantity=buyhighCertainty
            )
                firstBuyPrice = currentPrice
                print colored('bought at high certainty', "blue")
                #increase counter
                highCounter = highCounter + 1
                #recheck balance
                balance= (client.get_asset_balance(asset))
                balance = float(balance['free'])
                print colored('Bought at', "green")
                print  firstBuyPrice
                print colored('Waiting to sell at', "blue")
                print  sellLevel

            #Also tried selling here. Damn thing not working.
            elif currentPrice >= sellLevel:
                order =client.order_limit_sell(
                   symbol='BTCUSDT',
                   quantity=20
                )
                print colored('sold at high certainty', "blue")
                #increase counter
                sellcounter= sellcounter + 1
                #reset balance
                balance= (client.get_asset_balance(asset))
                balance = float(balance['free'])

strat = Strategy()
strat.trades()
