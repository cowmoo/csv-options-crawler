__author__ = 'paulcao'

from pyalgotrade.bar import Bar
from pyalgotrade import barfeed

class PandasBar(Bar):

    def __init__(self, df, ix, bars):
        self.df = df
        self.ix = ix
        self.bars = bars

    def getRow(self):
        rowkey = self.df.index[self.ix]
        return self.df.ix[rowkey]

    def getDateTime(self):
        """Returns the :class:`datetime.datetime`."""
        return self.bars.date

    def getOpen(self, adjusted=False):
        """Returns the opening price."""
        ret = ( float(self.getRow()["Ask"]) + float(self.getRow()["Bid"]) ) / 2
        if ret > 0:
            return ret
        else:
            return 0.01 #fix for worthless options

    def getHigh(self, adjusted=False):
        """Returns the highest price."""
        return float(self.getRow()["Ask"])

    def getLow(self, adjusted=False):
        """Returns the lowest price."""
        return float(self.getRow()["Bid"])

    def getClose(self, adjusted=False):
        """Returns the closing price."""
        return self.getOpen()

    def getVolume(self):
        """Returns the volume."""
        return 500000

    def getAdjClose(self):
        """Returns the adjusted closing price."""
        return self.getOpen()

    def getFrequency(self):
        """The bar's period."""
        return barfeed.Frequency.DAY

    def getPrice(self):
        """Returns the closing or adjusted closing price."""
        return self.getOpen()

    def setUseAdjustedValue(self, useAdjusted):
        pass

    def getUseAdjValue(self):
        return False

    def getUnderlyingPrice(self):
        """Returns the UnderlyingPrice."""
        return float(self.getRow()["UnderlyingPrice"])

    def getOpenInterest(self):
        """Returns the open interest."""
        if "OpenInterest" in self.getRow():
            return float(self.getRow()["OpenInterest"])
        else:
            return float(0)