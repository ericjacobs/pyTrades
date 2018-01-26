
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
        
        #lastPrice = float(Orders.get_ticker(symbol)['lastPrice'])
        currentPrice = client.get_ticker(symbol='BNBBTC')
        currentPrice=float(currentPrice['lastPrice'])
        firstBuyPrice = 10

        numberOfBuys =0
        balances = client.get_account()

        lowCertainty = firstBuyPrice * 0.95
        highCertainty = firstBuyPrice * 1.1

        buylowCertainty= float(round((balance* 0.05)/currentPrice))
        buyhighCertainty= float(round((balance * 0.10)/currentPrice))
        sellhighCertainty= float(round(balance * 0.95))
 

        cycle = 0
        actions = []

        

        print colored('Auto Trading with binance', "cyan")
  

        while balance >0:

            if currentPrice <= lowCertainty:
                order = client.create_order(
                symbol='BNBBTC',
                side= Client.SIDE_BUY,
                type=Client.ORDER_TYPE_MARKET,
                quantity=buylowCertainty
            )
                firstBuyPrice = currentPrice
          
            elif currentPrice>= highCertainty:
                order = client.create_order(
                symbol='BNBBTC',
                side= Client.SIDE_BUY,
                type=Client.ORDER_TYPE_MARKET,
                quantity=buylowCertainty
            )
                firstBuyPrice = currentPrice
   


        while (balance > 0):

            startTime = time.time()

            self.action(symbol)

            endTime = time.time()

            if endTime - startTime < self.wait_time:

               time.sleep(self.wait_time - (endTime - startTime))

               # 0 = Unlimited loop
               #if self.option.loop > 0:
                #   cycle = cycle + 1

strat = Strategy()
strat.trades()
