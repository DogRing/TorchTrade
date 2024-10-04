from local_values import raw_datas, datas
import indicators as idc
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
    if config.get('EMA'):
        for scope in config.get('EMA'):
            idx='EMA'+str(scope)
            df[idx]=idc.EMA(df,scope)
            df_c=df[idx].shift()
            df[idx]=df[idx]-df_c
            df[idx]=idc.skStdN(df[[idx]])
    if config.get('BB'):
        for scope in config.get('BB'):
            BW_idx='BW'+str(scope)
            BP_idx='BP'+str(scope)
            (df[BW_idx],df[BP_idx]),(_)=idc.BB(df,scope)
            df[BW_idx]=idc.skRobN(df[[BW_idx]])
            df[BP_idx]=idc.skMinMaxN(df[[BP_idx]])
    if config.get('dis'):
        for scope in config.get('dis'):
            idx='dis'+str(scope)
            df[idx]=idc.disparity(df,scope)
            df[idx]=idc.skStdN(df[[idx]])
    if config.get('Mmt'):
        for scope in config.get('Mmt'):
            idx='Mmt'+str(scope)
            df[idx]=idc.Mmt(df,scope)
            df[idx]=idc.skStdN(df[[idx]])
    if config.get('RSI'):
        for scope in config.get('RSI'):
            idx='RSI'+str(scope)
            df[idx]=idc.RSI(df,scope).values / 100
            df[idx]=idc.skMinMaxN(df[[idx]])
    if config.get('MACD'):
        df['MACD'],_=idc.MACD(df)
        df['MACD']=idc.skStdN(df[['MACD']])
    df_c = df['close'].shift()
    df['close']=df['close']-df_c
    df['close']=idc.skMinMaxN(df[['close']])
    df['value']=idc.skStdN(df[['value']])
    print(f"file {file} length : {len(df)}")
    df.to_csv(file)
