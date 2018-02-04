"""
  Utilities for dealing with market data.

  Examples:
    Get current price -
        >>> market.price('BNB', 'USDT')

    Retrieve a historical price -
        >>> market.price('BNB', 'USDT', minsAgo=5)

"""

import bintrees
import decimal
import datetime
import time

from binance_api import client


class PriceMemo(object):
    """Stores historical price data in memory."""
    def __init__(self):
        self.tree = bintrees.RBTree()

    def getPriceAt(self, when):
        if when in self.tree:
            return self.tree[when]
        else:
            try:
                floorKey = self.tree.floor_key(when)
                ceilKey = self.tree.ceiling_key(when)
                
                # Linear interpolation if time requested is between two
                # data points.
                ceilFrac = decimal.Decimal((when - floorKey).total_seconds() / 
                                            (ceilKey - floorKey).total_seconds())
                floorFrac = 1 - ceilFrac

                return (self.tree[floorKey] * floorFrac + 
                        self.tree[ceilKey] * ceilFrac)

            except KeyError:
                return None

    def hasPriceAt(self, when):
        return self.getPriceAt(when) is not None

    def add(self, when, price):
        self.tree[when] = price


# Map from (asset, quoteAsset) to PriceMemo
assetMemos = {}

def getMemo(asset, quoteAsset, create=False):
    key = (asset, quoteAsset)
    if key in assetMemos:
        return assetMemos[key]
    elif create:
        assetMemo = PriceMemo()
        assetMemos[key] = assetMemo
        return assetMemo
    else:
        return None


def price(asset, quoteAsset, daysAgo=0, hoursAgo=0, minsAgo=0, secsAgo=0):
    """Return the price of 'asset' in units of 'quoteAsset'. Specify
    daysAgo, hoursAgo, minsAgo, and/or secsAgo to retrieve historical
    prices. Otherwise, returns the current price.
    """
    symbol = asset + quoteAsset
    assetMemo = getMemo(asset, quoteAsset, create=True)

    timeAgo = datetime.timedelta(daysAgo, secsAgo + 60*(minsAgo + hoursAgo*60))
    assetTime = datetime.datetime.now() - timeAgo

    if not timeAgo:
        # Get current price.
        currentPrice = client.get_ticker(symbol=symbol)
        currentPrice = decimal.Decimal(currentPrice['lastPrice'])
        assetMemo.add(datetime.datetime.now(), currentPrice)
        return currentPrice
    else:
        # Check if we have this data in memo.
        fromId = None
        while not assetMemo.hasPriceAt(assetTime):
            trades = client.get_historical_trades(symbol=symbol, limit=500,
                                                  fromId=fromId)
            if not trades:
                break
            else:
                fromId = trades[0]['id'] - 500
            for trade in trades:
                assetMemo.add(datetime.datetime.fromtimestamp(trade['time']/1000.0),
                              decimal.Decimal(trade['price']))

        currentPrice = assetMemo.getPriceAt(assetTime)
        return currentPrice


