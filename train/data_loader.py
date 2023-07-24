import pandas as pd
import pyupbit
import os
from datetime import datetime
from datetime import timedelta
import time

# tickers = ['KRW-BTC', 'KRW-ETH', 'KRW-XRP', 'KRW-SOL', 'KRW-AVAX', 'KRW-DOGE','KRW-ETC']

clearConsole = lambda: os.system('cls' if os.name in ('nt', 'dos') else 'clear')

# start_times = {}
# for ticker in tickers:
#     start_times[ticker] = pd.read_csv(ticker+'.csv', index_col=0, parse_dates=[0], usecols=[0]).index[0]

# lens = {}
# while True:
#     for ticker in tickers:
#         interval_datas = pyupbit.get_ohlcv(ticker, interval='minute1',to = start_times[ticker])
#         start_times[ticker] = interval_datas.index[0]
#         interval_datas.to_csv(ticker+'.csv', mode='a', header=False)
#         lens[ticker] += 200
#         time.sleep(4)    

#     clearConsole()
#     for ticker in tickers:
#         print(f'{ticker} {start_times[ticker]} ~ {lens[ticker]} length')

tick = 'SOL'

lens = 0
start_time = datetime.now()
while True:
    interval_datas = pyupbit.get_ohlcv('KRW-'+tick,interval='minute1',to = start_time)
    start_time = interval_datas.index[0]
    interval_datas.to_csv(tick+'-MIN.csv',mode='a',header=False)
    lens += 200
    time.sleep(5)

    clearConsole()
    print(f'{tick}-MIN.csv update {start_time} ~ {lens} length')