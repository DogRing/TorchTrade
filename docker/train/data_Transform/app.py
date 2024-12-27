from local_values import tickers,raw_folder,data_folder
from data_transform import data_transform,data_scale
import pandas as pd
import json
import os

indicator_config_file=os.environ.get('INDICATOR_CONFIG',f'{data_folder}indicator.json')
scaler_config_file=os.environ.get('SCALER_CONFIG',f'{data_folder}scaler.json')
scaler_path = os.environ.get('SCALER_PATH',f'{data_folder}scaler/')
data_length = int(os.environ.get('DATA_LEN','0'))

print(f'INDICATOR_CONFIG: {indicator_config_file}')
print(f'SCALER_CONFIG: {scaler_config_file}')
print(f'SCALER_PATH: {scaler_path}')
print(f'DATA_LENGTH: {data_length}')

with open(indicator_config_file,'r') as f:
    tf_config=json.load(f)
with open(scaler_config_file,'r') as f:
    sc_config=json.load(f)

print("")
for tick in tickers:
    raw_file = raw_folder+tick+'.csv'
    print(f'READ CSV file "{tick}" on "{raw_file}"')
    df=pd.read_csv(raw_file,parse_dates=[0],index_col=[0])
    if data_length:
        print(f'\tData {len(df)}')
        df=df[-data_length:]
    print("\tresample, fillna, interpolate")
    df=df.resample(rule='min').first()
    df[['volume','value']]=df[['volume','value']].fillna(0)
    df=df.interpolate()
    print("\t Transform data as INDICATOR_CONFIG")
    df=data_transform(df,tf_config)
    print(f"\ttransformed file {tick} length : {len(df)}")
    df=data_scale(df,sc_config,save=True,path=scaler_path)
    target_file = data_folder+tick+'.csv'
    print(f'Save as {target_file}')
    df.to_csv(target_file)