from local_values import tickers,raw_folder,data_folder
from data_transform import data_transform
import pandas as pd
import json
import os

config_file=os.environ.get('DATA_CONFIG','/etc/config/transform.json')
scaler_path = os.environ.get('SCALER_PATH','/data/data/scaler/')
file_paths = os.environ['FILE_PATHS'].split(',')
with open(config_file,'r') as f:
    config=json.load(f)

for tick in tickers:
    df=pd.read_csv(raw_folder+tick+'.csv',parse_dates=[0],index_col=[0])
    df=df.resample(rule='min').first()
    df[['volume','value']]=df[['volume','value']].fillna(0)
    df=df.interpolate()
    df=data_transform(df,config,path=scaler_path,file_name=tick,save=True)
    print(f"file {tick} length : {len(df)}")
    df.to_csv(data_folder+tick+'.csv')
    for path in file_paths:
        df.to_csv(path+tick+'.csv')