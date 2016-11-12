__author__ = 'paulcao'

from PandasBar import PandasBar

class PandasBars(object):

    """A group of :class:`Bar` objects.
    :param barDict: A map of instrument to :class:`Bar` objects.
    :type barDict: map.
    .. note::
        All bars must have the same datetime.
    """

    def __init__(self, df, date, arr_ix=[]):
        self.date = date
        self.df = df
        self.arr_ix = arr_ix

        #key_val_arr = map(lambda ix: (df.ix[df.index[ix]]["Symbol"], PandasBar(df, ix, self)), self.arr_ix)
        #self.bar_dict = dict(key_val_arr)

    def set_bars_dict(self, bar_dict):
        self.bar_dict = bar_dict

    def keys(self):
        return self.bar_dict.keys()

    def __getitem__(self, instrument):
        """Returns the :class:`pyalgotrade.bar.Bar` for the given instrument.
        If the instrument is not found an exception is raised."""
        return self.bar_dict[instrument]

    def __contains__(self, instrument):
        """Returns True if a :class:`pyalgotrade.bar.Bar` for the given instrument is available."""
        return instrument in self.bar_dict

    def items(self):
        return self.bar_dict.items()

    def keys(self):
        return self.bar_dict.keys()

    def getInstruments(self):
        """Returns the instrument symbols."""
        return self.bar_dict.keys()

    def getDateTime(self):
        """Returns the :class:`datetime.datetime` for this set of bars."""
        return self.date

    def getBar(self, instrument):
        """Returns the :class:`pyalgotrade.bar.Bar` for the given instrument or None if the instrument is not found."""
        return self.bar_dict.get(instrument, None)