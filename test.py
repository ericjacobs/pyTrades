
import sys

sys.path.insert(0, './app')

from termcolor import colored


import config
from binance.client import Client
from BinanceAPI import BinanceAPI
from Database import Database
from Orders import Orders
from Tools import Tools

api_key = 'WBBcJ2miX5E9etn4Y9PxtujEoe8BDb4r3bPvwuoU7zkrFzMGPXvogeGPy7mLJ2vR'
api_secret = '8boaOQWfqBr8ptjpFTurdJUwswyGcqRmP2UUOUb98Q8Uw5Is7bh363O0zpaZ0tA1'

class Strategy:

    def trades(self):
        client = Client(api_key, api_secret)
        asset = "BNB"
        balance= (client.get_asset_balance('BTC'))
        balance = float(balance['free'])
        startBalance=(client.get_asset_balance('BTC'))
        startBalance= float(startBalance['free'])
        #lastPrice = float(Orders.get_ticker(symbol)['lastPrice'])
        currentPrice = client.get_ticker(symbol='BNBBTC')
        currentPrice=float(currentPrice['lastPrice'])
        firstBuyPrice = .00118

        numberOfBuys =0
        balances = client.get_account()
       

        lowCertainty = firstBuyPrice * 0.95
        highCertainty = firstBuyPrice * 1.0
        sellCertainty = firstBuyPrice * 1.1

        buylowCertainty= float(round((balance* 0.05)/currentPrice))
        buyhighCertainty= float(round((balance * 0.10)/currentPrice))
        sellhighCertainty= float(round(balance * 0.95))

        lowCounter= 0
        highCounter= 0
        sellcounter = 0

        cycle = 0
        actions = []

        

        print colored('Auto Trading with binance', "cyan")
  

        
        while balance>= (startBalance/2):
            if lowCounter < 1:
                if currentPrice >= lowCertainty and currentPrice< highCertainty:
                    order = client.create_order(
                    symbol='BNBBTC',
                    side= Client.SIDE_BUY,
                    type=Client.ORDER_TYPE_MARKET,
                    quantity=buylowCertainty
                )
                    firstBuyPrice = currentPrice
                    print colored('bought at low certainty', "blue")
                    balance= (client.get_asset_balance('BTC'))
                    balance = float(balance['free'])
                    lowCounter= lowCounter +1
            elif highCounter < 1:
                elif currentPrice >= highCertainty:
                    order = client.create_order(
                    symbol='BNBBTC',
                    side= Client.SIDE_BUY,
                    type=Client.ORDER_TYPE_MARKET,
                    quantity=buyhighCertainty
                    )
                    firstBuyPrice = currentPrice
                    print colored('bought at high certainty', "blue")
                    highCounter = highCounter + 1
                    balance= (client.get_asset_balance('BTC'))
                    balance = float(balance['free'])
                elif currentPrice >= sellCertainty:
                    order = client.order_market_sell(
                    symbol='BNBBTC',
                    quantity=sellhighCertainty)
                    print colored('sold at high certainty', "blue")
                    sellcounter= sellcounter + 1
                    balance= (client.get_asset_balance('BTC'))
                    balance = float(balance['free'])
strat = Strategy()
strat.trades()
