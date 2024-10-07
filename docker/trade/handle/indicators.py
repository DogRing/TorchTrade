# 단순 이동평균
def SMA(df, window, min_periods=1):
    return df['close'].rolling(window=window, min_periods=min_periods).mean()

# 지수 이동평균 (최근의 값에 가중치)
def EMA(df, window):
    return df['close'].ewm(window).mean()

# 가중 이동평균 (최근값이 훨씬 중요)
def WMA(df, window):
    import numpy as np
    weights = np.arange(1,window+1)
    return df['close'].rolling(window).apply(lambda prices: np.dot(prices,weights)/weights.sum(), raw=True)

# 상대 강도지수 (기간동안 상승, 하강 변화량)
def RSI(df, window):
    import numpy as np
    import pandas as pd
    diff = df['close'] - df['close'].shift(1)
    rise = pd.DataFrame(np.where(diff >=0, diff, 0))
    fall = pd.DataFrame(np.where(diff < 0, diff.abs(), 0))
    
    AU = rise.ewm(alpha=1/window, min_periods=window).mean()
    AD = fall.ewm(alpha=1/window, min_periods=window).mean()
    return AU / (AU+AD) * 100

# 볼린저 밴드
# bw: 밴드폭, preb: 하한선 0, 상한선 1
def BB(df, window):
    middle = df['close'].rolling(window=window).mean()
    std = df['close'].rolling(window).std(ddof=0)
    upper = middle + 2 * std
    lower = middle - 2 * std
    bw = 4*std / middle
    perb = (df['close'] - lower) / 4*std
    return (bw, perb), (upper, middle, lower)

# 모멘텀
def Mmt(df, window):
    return (df['close'] / df['close'].shift(window)) * 100

# 추세지표
def MACD(df, short=12, long=26, signal=9):
    macd = df['close'].ewm(span=short).mean() - df['close'].ewm(span=long).mean()
    macd_signal = macd.ewm(span=signal).mean()
    macd_oscillator = macd - macd_signal
    return  macd_oscillator, (macd, macd_signal)

# 이격도
def disparity(df, window, min_periods=1):
    return 100*(df['open']/df['close'].rolling(window).mean())

def resample_T(df, T_range, ohlcv='ohlcv'):
    import pandas as pd
    df_sample = pd.DataFrame()
    for i in ohlcv:
        if   i == 'o' : df_sample['open'] = df['open'].resample(T_range).first()
        elif i == 'h' : df_sample['high'] = df['high'].resample(T_range).max()
        elif i == 'l' : df_sample['low'] = df['low'].resample(T_range).min()
        elif i == 'c' : df_sample['close'] = df['close'].resample(T_range).last()
        elif i == 'v' : df_sample['volume'] = df['volume'].resample(T_range).sum()
    return df_sample
                
##################################################################################
##################################################################################

def MinMaxN(df):
    df = (df - df.min()) / (df.max() - df.min())
    return df

def StdN(df):
    df = (df - df.mean()) / df.std()
    return df

def skMinMaxN(df):
    from sklearn.preprocessing import MinMaxScaler
    scaler = MinMaxScaler()
    scaler.fit(df)
    return scaler.transform(df)

def skStdN(df):
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler()
    scaler.fit(df)
    return scaler.transform(df)

def skRobN(df):
    from sklearn.preprocessing import RobustScaler
    scaler = RobustScaler()
    scaler = scaler.fit(df)
    return scaler.transform(df)