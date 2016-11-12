__author__ = 'paulcao'

import pandas as pd
import PandasBarFeed
from pyalgotrade import barfeed

df = pd.read_csv("my_csv4.csv", parse_dates=['DateType'])
feed = PandasBarFeed(df, "SPX", barfeed.Frequency.DAY)
bars = feed.getNextBars()

print bars