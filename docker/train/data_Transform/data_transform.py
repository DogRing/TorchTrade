from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
import indicators as idc
import pandas as pd
import joblib
import os

scaler_path = os.environ.get('SCALER_PATH','/data/data/scaler/')
scalers = {
    "standard_scaler": StandardScaler(),
    "minmax_scaler": MinMaxScaler(),
    "robust_scaler": RobustScaler()
}

def save_scaler(scaler, filename):
    joblib.dump(scaler, filename)

def load_scaler(filename):
    return joblib.load(filename)

def apply_scaling(df, columns, scaler, save_name=None):
    df[columns] = scaler.fit_transform(df[columns])
    if save_name:
        save_scaler(scaler, f"{scaler_path}{save_name}.pkl")
    return df

def data_transform(df,config):
    if config.get('EMA'):
        ema_columns = []
        for scope in config.get('EMA'):
            idx=f'EMA{scope}'
            df[idx]=idc.EMA(df,scope)
            df[idx]=df[idx].diff()
            ema_columns.append(idx)
        df=apply_scaling(df,ema_columns,scalers["standard_scaler"],save_name="ema_std")
    if config.get('BB'):
        bw_columns = []
        bp_columns = []
        for scope in config.get('BB'):
            BW_idx=f'BW{scope}'
            BP_idx=f'BP{scope}'
            (df[BW_idx],df[BP_idx]),(_)=idc.BB(df,scope)
            bw_columns.append(BW_idx)
            bp_columns.append(BP_idx)
        df = apply_scaling(df,bw_columns,scalers["robust_scaler"],save_name="bb_rob")
        df = apply_scaling(df,bp_columns,scalers["minmax_scaler"],save_name="bb_mm")
    if config.get('dis'):
        dis_columns = []
        for scope in config.get('dis'):
            idx=f'dis{scope}'
            df[idx]=idc.disparity(df,scope)
            dis_columns.append(idx)
        df = apply_scaling(df,dis_columns,scalers["standard_scaler"],save_name="dis_std")
    if config.get('Mmt'):
        mmt_columns = []
        for scope in config.get('Mmt'):
            idx=f'Mmt{scope}'
            df[idx]=idc.Mmt(df,scope)
            mmt_columns.append(idx)
        df = apply_scaling(df,mmt_columns,scalers["standard_scaler"],save_name="mmt_std")
    if config.get('RSI'):
        rsi_columns = []
        for scope in config.get('RSI'):
            idx=f'RSI{scope}'
            df[idx]=idc.RSI(df, scope).values / 100
            rsi_columns.append(idx)
        df=apply_scaling(df,rsi_columns,scalers["minmax_scaler"],save_name="rsi_mm")
    if config.get('MACD'):
        df['MACD'],_=idc.MACD(df)
        df=apply_scaling(df,['MACD'],scalers["standard_scaler"],save_name="macd_std")
    df['close'] = df['close'].diff()
    df=apply_scaling(df,['close'],scalers["minmax_scaler"],save_name="close_mm")
    df=apply_scaling(df,['value'],scalers["standard_scaler"],save_name="value_std")
    return df