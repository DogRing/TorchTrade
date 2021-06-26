import pandas
import pyupbit
import os
from datetime import datetime

# access_key = 'u31ykk40vZfScWxbVeyMfxctVzGgHU4htQbT9Iz9'
# secret_key = '3t4a10bumGFf7JtMRzO96C6huN7T4Axd2DthpUJc'

exten = '.csv'

def gettickers():
    return pyupbit.get_tickers("KRW")

def update_data(data_path,tickers,now):
    now = now.strftime('%Y-%m-%d %H:%M')
    now = now+':00'

    print(now)
    for i in tickers:
        try:
            interval_datas = pyupbit.get_ohlcv(i,interval = "minute3",count=4)
            bring_last = pandas.read_csv(data_path+i+exten).iloc[-1][0]
            need_data = interval_datas.loc[bring_last:]
            if len(need_data)>2:
                cut_data = need_data.iloc[1:]
                cut_data.to_csv(data_path+i+exten,mode='a',header=False)
            print('update '+i)
        except:
            print('unnecessary update'+i)

    now = datetime.today()
    return now

def setting(data_path,tickers,now):
    if not os.path.isdir(data_path):
        os.mkdir(data_path)

    for i in tickers:
        interval_datas = pyupbit.get_ohlcv(i,interval ="minute3",count = 200)
        try:
            bring_last = pandas.read_csv(data_path+i+exten).iloc[-1][0]
            need_data = interval_datas.loc[bring_last:]
            cut_data = need_data.iloc[1:]
            cut_data.to_csv(data_path+i+exten,mode='a',header=False)
        except:
            interval_datas.to_csv(data_path+i+exten)

    now = datetime.today()
    return now