
#
# Main entry point for pyTrader.
#


import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

import math
import time
import gevent
import gevent.monkey

gevent.monkey.patch_all()

from decimal import Decimal as _d
from termcolor import colored

from pyTrades.util import binance_api
from pyTrades.util import binance_ws
from pyTrades.util import reporter
from pyTrades.util import task


# Start a bot that will pull in current prices from the Binance
# WebSocket stream.
task.TaskGreenlet(binance_ws.streamBot, name='streamBot').start()

# Start a bot that will send trade reports via SMS.
task.TaskGreenlet(reporter.reporterBot, name='reporterBot').start()


# Start trading bots.
from pyTrades.strats.strat1btc import Strategy1BTC
from pyTrades.strats.strat1eth import Strategy1ETH
from pyTrades.strats.strat1bnb import Strategy1BNB

# Add other trading bots here...
#from pyTrades.strats.strat1 import Strategy1


# Main loop.
gevent.wait()
