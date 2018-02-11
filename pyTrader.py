
#
# Main entry point for pyTrader.
#


import os
import sys
sys.path.append(r'c:\')

import math
import time
import gevent
import gevent.monkey

gevent.monkey.patch_all()

from decimal import Decimal as _d
from binance.client import Client
from termcolor import colored

from pyTrades.util import binance_api
from pyTrades.util import binance_ws
from pyTrades.util import task


# Start a bot that will pull in current prices from the Binance
# WebSocket stream.
task.TaskGreenlet(binance_ws.streamBot, name='streamBot').start()

# Start trading bots.
from pyTrades.strats.strat1 import Strategy1

# Add other trading bots here...
#from pyTrades.strats.strat1 import Strategy1


# Main loop.
gevent.wait()
