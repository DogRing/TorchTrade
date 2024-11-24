from local_values import tickers,raw_folder,data_folder
from data_transform import data_transform,data_scale
import pandas as pd
import json
import os

indicator_config_file=os.environ.get('INDICATOR_CONFIG','/etc/config/indicator.json')
scaler_config_file=os.environ.get('SCALER_CONFIG','/etc/config/scaler.json')
scaler_path = os.environ.get('SCALER_PATH','/data/scaler/')
data_length = int(os.environ.get(,'0'))
other_file_paths = os.environ['FILE_PATHS'].split(',')

with open(indicator_config_file,'r') as f:
    idc_config=json.load(f)
with open(scaler_config_file,'r') as f:
    sc_config=json.load(f)

for tick in tickers:
    df=pd.read_csv(raw_folder+tick+'.csv',parse_dates=[0],index_col=[0])
    if data_length:
        df=df[-data_length:]
    df=df.resample(rule='min').first()
    df[['volume','value']]=df[['volume','value']].fillna(0)
    df=df.interpolate()
    df=data_transform(df,idc_config)
    print(f"file {tick} length : {len(df)}")
    df=data_scale(df,sc_config,save=True,path=scaler_path)
    df.to_csv(data_folder+tick+'.csv')
    for path in other_file_paths:
        df.to_csv(path+tick+'.csv')