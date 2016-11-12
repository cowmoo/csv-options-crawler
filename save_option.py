__author__ = 'paulcao'

from pandas_datareader import Options
import time
import sys

def save_option(symbols, filename):
    f = open(filename, 'w')
    f.write("UnderlyingSymbol,UnderlyingPrice,Exchange,OptionRoot,OptionExt,Type,Expiration,DataDate,Strike,Last,Bid,Ask,Volume,OpenInterest,T1OpenInterest\n")
    symbols = sorted(symbols)

    for symbol in symbols:
        print "Crawling " + symbol + "..."
        option = Options(symbol, 'yahoo')
        try:
            df = option.get_all_data()
            append_to_csv(df, filename)
        except Exception as e:
            print e

def append_to_csv(df, filename):
    f = open(filename,'a')

    it = df.iterrows()

    try:
        while True:
            [index, row] = next(it)

            expirationDate = index[1]
            expirationDateStr = expirationDate.strftime("%d/%m/%Y")
            quoteDate = row["Quote_Time"]
            quoteDateStr = quoteDate.strftime("%d/%m/%Y")
            strikePrice = index[0]
            optionType = index[2][0:-1]
            optionSymbol = index[3]

            f.write(row["Underlying"] + "," + str(row["Underlying_Price"]) + ",*," + optionSymbol + ",," + optionType + "," + expirationDateStr + "," + quoteDateStr + "," + str(strikePrice) + "," + str(row["Last"]) + "," + str(row["Bid"]) + "," + str(row["Ask"]) + "," + str(row["JSON"]["volume"]) + "," + str(row["JSON"]["openInterest"]) + "," + str(row["JSON"]["openInterest"]) + "\n")

    except StopIteration:
        pass

def load_symbols(filename):
    symbols = []

    with open(filename, 'r') as f:
        for line in f:
            symbols.append(line.rstrip())

    return symbols

prefix = sys.argv[2]
symbol_list_file = sys.argv[1]

symbol_csv_file = prefix + time.strftime("%Y%m%d") + ".csv"
symbol_arr = load_symbols(symbol_list_file)
save_option(symbol_arr, symbol_csv_file)
