
#
# Main entry point for pyTrader.
#


import os
import sys
<<<<<<< HEAD
sys.path.append(r'c:\')
=======
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
>>>>>>> 2bdb76476511d6dbe1193fda73c3359705eb2524

import math
import time
import gevent
import gevent.monkey

gevent.monkey.patch_all()

from decimal import Decimal as _d
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
