
#
# Abstract definition of a trading strategy.
#

from pyTrades.util import task


class AbstractStrategy(object):

    # Change this to change the asset you're buying
    asset = None

    # Change this to change the asset you're paying with
    otherasset = None

    def start(self):
        """Start this trading bot."""
        task.TaskGreenlet(self.trades,
                          name='%s%s Bot' % (self.asset, self.otherasset)
        ).start()
