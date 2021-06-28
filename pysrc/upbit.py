import pandas
from pandas.core.algorithms import mode
import pyupbit
import os
from datetime import datetime
from datetime import timedelta

# access_key = 'u31ykk40vZfScWxbVeyMfxctVzGgHU4htQbT9Iz9'
# secret_key = '3t4a10bumGFf7JtMRzO96C6huN7T4Axd2DthpUJc'

exten = '.csv'

def gettickers():
    return pyupbit.get_tickers("KRW")

def update_data(data_path,tickers,now,ticks=4):
    date = now.strftime('%Y-%m-%d')
    time = now.strftime('%H:%M:%S')
    yesterday = now-timedelta(days=1)
    yest_date = yesterday.strftime('%Y-%m-%d')
    
    for i in tickers:
        file_name = data_path+i+date+exten
        try:
            # bring datas
            interval_datas = pyupbit.get_ohlcv(i,interval = "minute3",count=ticks)
            try:
                # today data
                today_data = interval_datas.loc[date]
                # already have data => append
                if os.path.isfile(file_name):
                    bring_last = pandas.read_csv(file_name).iloc[-1][0]
                    need_data = today_data.loc[bring_last:]
                    if len(need_data)>2:
                        cut_data = need_data.iloc[1:]
                        cut_data.to_csv(file_name,mode='a',header=False)
                        print('update '+i+time)
                    else:
                        print('no data to update '+i+time)
                # there is no file => mk new
                else:
                    today_data.index.name="date"
                    today_data.to_csv(file_name)
                    print('make '+i+date)
                # no today data
            except:
                print('no data in '+i+time)

            try:
                # yesterday data
                yest_data = interval_datas.loc[yest_date] 
                file_name = data_path+i+yest_date+exten
                # append
                bring_last = pandas.read_csv(file_name).iloc[-1][0]
                need_data = yest_data.loc[bring_last:]
                if len(need_data)>2:
                    cut_data = need_data.iloc[1:]
                    cut_data.to_csv(file_name,mode='a',header=False)
                    print('update '+i+' yesterday')
                else:
                    print('no data to update '+i+' yesterday')
            except:
                pass
        except:
            # if pyupbit is dead
            return 200
    return 4

def setting(data_path,tickers,now):
    date = now.strftime('%Y-%m-%d')
    yesterday = now-timedelta(days=1)
    yest_date = yesterday.strftime('%Y-%m-%d')
    if not os.path.isdir(data_path):
        os.mkdir(data_path)

    for i in tickers:
        file_name = data_path+i+date+exten
        interval_datas = pyupbit.get_ohlcv(i,interval ="minute3",count = 200)
        today_data = interval_datas.loc[date]
        try:
            bring_last = pandas.read_csv(file_name).iloc[-1][0]
            need_data = today_data.loc[bring_last:]
            cut_data = need_data.iloc[1:]
            cut_data.to_csv(file_name,mode='a',header=False)
        except:
            today_data.index.name="date"
            today_data.to_csv(file_name)
        try:
            yest_data = interval_datas.loc[yest_date]
            file_name = date+i+yest_date+exten
            bring_last = pandas.read_csv(file_name).iloc[-1][0]
            need_data = yest_data.loc[bring_last:]
            if len(need_data)>2:
                cut_data = need_data.iloc[1:]
                cut_data.to_csv(file_name,mode='a',header=False)
        except:
            pass
    now = datetime.today()
    return now