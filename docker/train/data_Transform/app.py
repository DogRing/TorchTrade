from local_values import raw_datas, datas
from data_transform import data_transform
import pandas as pd
import json
import os

config_file=os.environ.get('DATA_CONFIG','/etc/config/transform.json')
with open(config_file,'r') as f:
    config=json.load(f)

for file,raw_file in zip(datas,raw_datas):
    df=pd.read_csv(raw_file,parse_dates=[0],index_col=[0])
    df=df.resample(rule='min').first()
    df[['volume','value']]=df[['volume','value']].fillna(0)
    df=df.interpolate()
    df=data_transform(df,config)
    print(f"file {file} length : {len(df)}")
    df.to_csv(file)
