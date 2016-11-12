__author__ = 'paulcao'

from more_itertools import peekable
from pyalgotrade.bar import Bar
from pyalgotrade import barfeed
from PandasBars import PandasBars
from PandasBar import PandasBar

class PandasBarFeed(barfeed.BaseBarFeed):
    def __init__(self, dataframe, instrument, frequency):
        super(PandasBarFeed, self).__init__(frequency)
        self.registerInstrument(instrument)
        self.__df = dataframe
        self.__instrument = instrument
        self.__next = 0
        self.started = False

        groups = self.__df.groupby(["DataDate","OptionRoot"]).groups
        timestamp_dict = {}
        bars_dict = {}

        def loadBars(timestamp, symbol, index):
            if timestamp not in timestamp_dict:
                timestamp_dict[timestamp] = {}
                bars_dict[timestamp] = PandasBars(self.__df, timestamp)

            timestamp_dict[timestamp][symbol] = PandasBar(self.__df, index, bars_dict[timestamp])

        map(lambda ((timestamp, symbol),index):loadBars(timestamp, symbol, index), groups.iteritems())
        map(lambda (timestamp, bars):bars.set_bars_dict(timestamp_dict[timestamp]), bars_dict.iteritems())

        dates = sorted(timestamp_dict.keys())
        self.bars = map(lambda d:bars_dict[d], dates)
        self.bar_iter = peekable(self.bars)

    def reset(self):
        super(PandasBarFeed, self).reset()
        self.bar_iter = peekable(self.bars)
        self.started = False

    def peekDateTime(self):
        return self.getCurrentDateTime()

    def getCurrentDateTime(self):
        try:
            return self.bar_iter.peek().date
        except StopIteration:
            return None

    def barsHaveAdjClose(self):
        return True

    def getNextBars(self):
        try:
            return self.bar_iter.next()
        except StopIteration:
            return None

    def start(self):
        #super(PandasBarFeed, self).start()
        self.__started = True

    def stop(self):
        pass

    def join(self):
        pass

    def eof(self):
        try:
            if self.bar_iter.peek() and not self.bar_iter.peek() == self.bars[-1]:
                return False
            else:
                return True
        except StopIteration:
            return True

    def getCurrentBars(self):
        try:
            return self.bar_iter.peek()
        except StopIteration:
            return None

    def getNextValuesAndUpdateDS(self):
        dateTime, values = self.getNextValues()
        if dateTime is not None:
            for key, value in values.items():
                pass
                # Get or create the datseries for each key.
                #try:
                #    ds = self.__ds[key]
                #except KeyError:
                #    ds = self.createDataSeries(key, self.__maxLen)
                #    self.__ds[key] = ds
                #ds.appendWithDateTime(dateTime, value)
        return (dateTime, values)