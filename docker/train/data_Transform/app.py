from local_values import raw_datas, datas
import indicators as idc
import numpy as np
import pandas as pd

for file,raw_file in zip(datas,raw_datas):
    df=pd.read_csv(raw_file,parse_dates=[0],index_col=[0])
    df=df.resample(rule='min').first()
    df[['volume','value']]=df[['volume','value']].fillna(0)
    df=df.interpolate()
    df['EMA5'] = idc.EMA(df,5)
    df['EMA30'] = idc.EMA(df,30)
    df['EMA60'] = idc.EMA(df,60)
    (df['BW'],df['BP']), (_) = idc.BB(df,20)
    df['dis'] = idc.disparity(df, 20)
    df['Mmt'] = idc.Mmt(df,20)
    df['RSI'] = idc.RSI(df,14).values / 100
    df['MACD'], _ = idc.MACD(df)
    df_c = df['close'].shift()
    for i in ['close','EMA5','EMA30','EMA60']:
        df[i] = (df[i] - df_c) / df_c
        df[i] = idc.skRobN(df[[i]])
    for i in ['value','BW','dis','Mmt','RSI']:
        df[i] = idc.skRobN(df[[i]])
    for i in ['BP','MACD']:
        df[i] = df[i] / df[i].abs().max()
    df = df[['close','EMA5','EMA30','EMA60','value','BW','BP','dis','Mmt','RSI','MACD']]
    df = (df - df.mean())/df.std()
    print(f"file {file} length : {len(df)}")
    df.to_csv(file)