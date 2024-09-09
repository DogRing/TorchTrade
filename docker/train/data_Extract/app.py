from local_values import raw_datas,tickers,raw_folder
from datetime import datetime, timedelta
import pandas as pd
import requests
import time
import json
import os

def request_data(tick,to_time='',count=200):
    headers={"accept":"application/json"}
    url=f'https://api.upbit.com/v1/candles/minutes/1?market={tick}&count={count}{to_time}'
    contents=json.loads(requests.get(url,headers=headers).text)
    contents = pd.DataFrame(contents,columns=[
                                'candle_date_time_kst','opening_price','high_price','low_price',
                                'trade_price','candle_acc_trade_volume','candle_acc_trade_price'])
    contents = contents.set_index('candle_date_time_kst')
    contents.index=pd.to_datetime(contents.index)
    return contents

def get_last_time(file_name):
    try: 
        with open(file_name, "rb") as f:
            f.seek(-2,os.SEEK_END)
            while f.read(1)!=b'\n':
                f.seek(-2,os.SEEK_CUR)
            last_line = f.readline().decode()
        line=last_line.strip().split(",")
        return datetime.strptime(line[0],'%Y-%m-%d %H:%M:%S')
    except OSError:
        print("empty file:", file_name)
        return datetime.now()

if os.path.exists(raw_folder)==False:
    print("No Folder")
else:
    for tick in tickers:
        file_name=raw_folder+tick+'.csv'
        if os.path.exists(file_name)==False:
            print(f"No File {file_name}")
        else:
            print(f"Start tick {tick}")
            contents=pd.DataFrame()
            end_time = get_last_time(file_name)+timedelta(minutes=1)
            response=request_data(tick)
            while True:
                response=response[:end_time]
                if (response.shape[0] == 0):
                    break
                contents=pd.concat([contents,response])
                to_time=(response.index[-1]-timedelta(hours=9)).strftime('%Y-%m-%dT%H:%M:%S')
                time.sleep(0.65)
                response=request_data(tick,'&to='+to_time)
            contents.sort_index().to_csv(file_name,mode='a',header=False)
            print(f"update {tick} from {contents.index[0]} to {contents.index[-1]}")
