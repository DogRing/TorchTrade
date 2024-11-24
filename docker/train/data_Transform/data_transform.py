def data_transform(df,config):
    import indicators as idc
    if config.get('EMA'):
        for scope in config.get('EMA'):
            idx=f'EMA{scope}'
            df[idx]=idc.EMA(df,scope)
            df[idx]=df[idx].diff()
    if config.get('BB'):
        for scope in config.get('BB'):
            BW_idx=f'BW{scope}'
            BP_idx=f'BP{scope}'
            (df[BW_idx],df[BP_idx]),(_)=idc.BB(df,scope)
    if config.get('dis'):
        for scope in config.get('dis'):
            idx=f'dis{scope}'
            df[idx]=idc.disparity(df,scope)
    if config.get('Mmt'):
        for scope in config.get('Mmt'):
            idx=f'Mmt{scope}'
            df[idx]=idc.Mmt(df,scope)
    if config.get('RSI'):
        for scope in config.get('RSI'):
            idx=f'RSI{scope}'
            df[idx]=idc.RSI(df, scope).values / 100
    if config.get('MACD'):
        df['MACD'],_=idc.MACD(df)
    return df

def save_scaler(scaler,filename):
    joblib.dump(scaler,filename)

def load_scaler(filename):
    return joblib.load(filename)

def apply_scaling(df,columns,scaler,save=True,save_name=None):
    import joblib
    if save:
        if "standard":
            from sklearn.preprocessing import StandardScaler
            scaler = StandardScaler()
            df[columns]=scaler.fit_transform(df[columns])
            save_scaler(scaler,f"{save_name}_STD.pkl")
        if "minmax":
            from sklearn.preprocessing import MinMaxScaler
            scaler = MinMaxScaler()
            df[columns]=scaler.fit_transform(df[columns])
            save_scaler(scaler,f"{save_name}_MM.pkl")
        if "robust":
            from sklearn.preprocessing import RobustScaler
            scaler = RobustScaler()
            df[columns]=scaler.fit_transform(df[columns])
            save_scaler(scaler,f"{save_name}_RB.pkl")
    else:
        scaler=load_scaler(f"{save_name}.pkl")
        df[columns]=scaler.transform(df[columns])
    return df

def data_scale(df,config,save=False,path=None):
    if config.get('MM'):
        df=apply_scaling(df,config.get('MM'),"minmax",True,path)
    if config.get('STD'):
        df=apply_scaling(df,config.get('STD'),"standard",True,path)
    if config.get('RB'):
        df=apply_scaling(df,config.get('RB'),"robust",True,path)
    return df