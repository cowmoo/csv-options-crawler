__author__ = 'paulcao'

import pandas as pd
from PandasBarFeed import PandasBarFeed
from pyalgotrade import barfeed
import datetime
import math
from vollib.black_scholes.implied_volatility import implied_volatility
from vollib.black_scholes import black_scholes
from statsmodels.nonparametric.kernel_regression import KernelReg
import sys

def get_chain(bars):
    def parse_option_symbol(symbol):
        try:
            opra_symbol = symbol[:-15]
            opra_expiry = datetime.datetime.strptime(symbol[-15:-9], '%y%m%d').date()
            opra_cp = symbol[-9]
            opra_price = int(symbol[-8:]) * .001

            return {"Symbol":opra_symbol, "Expiration":opra_expiry, "Type":opra_cp, "Price":opra_price, "OptionSymbol":symbol}
        except Exception as e:
            print e

    chain = []
    for symbol in bars.keys():
        if symbol == "^SPX" or symbol == "^SPXW":
            continue

        chain.append(parse_option_symbol(symbol))

    return chain

def calc_iv(filtered_option_chain, bars, t):
    chains = []

    for option in filtered_option_chain:
        price = float(bars[option['OptionSymbol']].getClose())
        cp = option['Type'].lower()
        K = float(option['Price'])
        S = float((bars[option['OptionSymbol']]).getUnderlyingPrice())
        r = 0.028

        iv = implied_volatility(price, S, K, t, r, str(cp))
        option["IV"] = iv
        chains.append(option)

    return chains

def write_iv_pred(filtered_option_chain, kr, t, underlyingPrice):
    i = 0
    chain = []
    for option in filtered_option_chain:
        flag = option['Type'].lower()
        K = float(option['Price'])
        S = underlyingPrice
        r = 0.028
        sigma = kr.fit([K])[0][0]

        option["IV_Pred"] = sigma
        option["SmoothedPrice"] = black_scholes(flag, S, K, t, r, sigma)
        chain.append(option)
        i = i + 1

    return chain

def get_all_expirations(chain):
    expiration_dates = map(lambda option:option['Expiration'], chain)
    unique_dates = set(expiration_dates)
    return unique_dates

def calc_smoothed_quotes(chain, underlying_price, t):
    filtered_chain = filter(lambda option: math.fabs(option['Price']-underlying_price)/underlying_price < 1.10 or math.fabs(option['Price']-underlying_price)/underlying_price > 0.90, chain) #filter by 45-Day Put Simile
    #filtered_chain = chain

    # convert to strikes and IV arrays for KernelReg
    iv_pair = map(lambda x:(x['Price'], x['IV']), chain)
    iv_pair = sorted(iv_pair, key=lambda x:x[0])

    strikes = map(lambda x:x[0], iv_pair)
    iv = map(lambda x:x[1], iv_pair)

    # run KernelReg
    kr = KernelReg(iv, strikes, 'c')
    #iv_pred, iv_std = kr.fit(strikes)

    # smooth the IV and prices
    write_iv_pred(filtered_chain, kr, t, underlying_price)

def calculate_smoothed_iv(chain, bars):
    unique_dates = get_all_expirations(chain)

    for date in unique_dates:
        current_chain = filter(lambda option:option['Expiration'] == date, chain)
        t = float(((date - bars.getDateTime().date()).total_seconds()) / (60 * 60 * 24 * 365))

        calc_iv(current_chain, bars, t)
        underlying_price = bars[bars.keys()[0]].getUnderlyingPrice()
        put_chain = filter(lambda option:option['Type'] == 'P', current_chain)
        call_chain = filter(lambda option:option['Type'] == 'C', current_chain)

        print "Processing for expiration date " + str(date) + ":"
        print "Calculating Put Chain..."
        if len(put_chain) > 0:
            calc_smoothed_quotes(put_chain, underlying_price, t)
        print "Calculating Call Chain..."
        if len(call_chain) > 0:
            calc_smoothed_quotes(call_chain, underlying_price, t)

def get_csv_str(option_bar, bars, underlying_symbol):
    underlyingPrice = (bars[option_bar['OptionSymbol']]).getUnderlyingPrice()
    optionSymbol = option_bar['OptionSymbol']
    optionType = 'put' if option_bar['Type'] == 'P' else 'call'
    expirationDateStr = (option_bar['Expiration']).strftime("%m/%d/%Y")
    quoteDateStr = (bars.getDateTime().date()).strftime("%m/%d/%Y")
    strikePrice = option_bar['Price']
    openInterest = (bars[option_bar['OptionSymbol']]).getOpenInterest()

    return underlying_symbol + "," + str(underlyingPrice) + ",*," + optionSymbol + ",," + optionType + "," + expirationDateStr + "," + quoteDateStr + "," + str(strikePrice) + "," + str(bars[optionSymbol].getClose()) + "," + str(bars[optionSymbol].getLow()) + "," + str(bars[optionSymbol].getHigh()) + "," + str(bars[optionSymbol].getVolume()) + "," + str(openInterest) + "," + str(openInterest)

def load_symbols(filename):
    symbols = []

    with open(filename, 'r') as f:
        for line in f:
            symbols.append(line.rstrip())

    return symbols

input_file = sys.argv[1]
output_file_name = sys.argv[2]
symbol_list_file = sys.argv[3]

symbol_arr = load_symbols(symbol_list_file)
df = pd.read_csv(input_file, parse_dates=['DataDate'])

output_file = open(output_file_name, "w")
output_file.write("UnderlyingSymbol,UnderlyingPrice,Exchange,OptionRoot,OptionExt,Type,Expiration,DataDate,Strike,Last,Bid,Ask,Volume,OpenInterest,T1OpenInterest\n")

for symbol in symbol_arr:
    print symbol
    feed = PandasBarFeed(df, symbol, barfeed.Frequency.DAY)
    bars = feed.getNextBars()

    chain = get_chain(bars)
    calculate_smoothed_iv(chain, bars)

    for current_item in chain:
        output_file.write(get_csv_str(current_item, bars, symbol) + "\n")

output_file.close()