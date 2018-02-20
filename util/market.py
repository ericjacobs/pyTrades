#
# Utilities for dealing with market data.
#
#  Example use:
#    Get current price -
#        >>> market.price('BNB', 'USDT')
#
#    Retrieve a historical price -
#        >>> market.price('BNB', 'USDT', minsAgo=5)
#

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

    def getLatestPrice(self):
        when, price = self.tree.max_item()
        return price, when

    def isEmpty(self):
        return len(self.tree) == 0

    def add(self, when, price):
        self.tree[when] = price
    
    def averageByMinute(self, whenFrom, whenTo):
        """Returns the price averaged by each minute in the given time
        range.
        
        Returns:
          iterator of (when, price)
        """
        when = whenFrom
        incr = datetime.timedelta(minutes=1)

        while when < whenTo:
            totalPrice = decimal.Decimal(0)
            numPrices = 0
            for price in self.tree[when:when + incr].values():
                totalPrice += price
                numPrices += 1
            
            if numPrices > 0:
                yield when, (totalPrice / numPrices)
            when += incr

            
# Map from (asset, quoteAsset) to PriceMemo
assetMemos = {}

def getMemo(asset, quoteAsset=None, create=False):
    key = asset
    if quoteAsset:
        key = key + quoteAsset
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
        while True:
            if not assetMemo.isEmpty():
                price, whenPrice = assetMemo.getLatestPrice()
                agePrice = datetime.datetime.now() - whenPrice
                if agePrice.total_seconds() <= 5:
                    # Last known data is fresh enough.
                    return price

            # Wait for the stream bot to give us our data.
            time.sleep(1)

    else:
        # Check if we have this data in memo.
        fromId = None
        while not assetMemo.hasPriceAt(assetTime):

            # If not, page back through the history on the server until we
            # find it.
            time.sleep(1)
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


def movingAverage(asset, quoteAsset, days=0, hours=0, mins=0, secs=0):
    """Return the current simple moving average of 'asset' in 'quoteAsset' for
    the specified time period.
    """
    startPrice = price(asset, quoteAsset, days, hours, mins, secs)
    
    timeAgo = datetime.timedelta(days, secs + 60*(mins + hours*60))
    assetTime = datetime.datetime.now() - timeAgo
    assetMemo = getMemo(asset, quoteAsset)
    
    totalPrice = decimal.Decimal(0)
    numPrices = 0
    for when, avgPrice in assetMemo.averageByMinute(assetTime, datetime.datetime.now()):
        totalPrice += avgPrice
        numPrices += 1
    
    return totalPrice / numPrices


def deleteOlderThan(asset, quoteAsset, daysAgo=0, hoursAgo=0, minsAgo=0, secsAgo=0):
    """Delete market data of 'asset' in 'quoteAsset' older than the specified
    time period.
    """
    timeAgo = datetime.timedelta(daysAgo, secsAgo + 60*(minsAgo + hoursAgo*60))
    assetTime = datetime.datetime.now() - timeAgo

    assetMemo = getMemo(asset, quoteAsset)
    if assetMemo:
        del assetMemo.tree[:assetTime]
