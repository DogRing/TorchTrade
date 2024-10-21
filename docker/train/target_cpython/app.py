from local_values import tickers,raw_folder,target_folder
import ctypes
import pandas as pd
import numpy as np
import os

feature = os.environ.get('TARGET','close')
c_file = os.environ.get('C_FILE','./libtarget.so')
period = float(os.environ.get('PERIOD','0.0075'))
_dll = ctypes.cdll.LoadLibrary(c_file)

for tick in tickers:
    df = pd.read_csv(raw_folder+tick+'.csv',parse_dates=[0],index_col=[0])
    df = df.resample(rule='min').first()
    df = df.interpolate()

    x = df[feature]
    x_len = len(x)

    y = np.zeros(x_len,dtype=np.int32)
    x = x.to_numpy(dtype=np.int32,copy=True).flatten()

    c_period = ctypes.c_float(period)
    c_len = ctypes.c_int(x_len)
    c_y = np.ctypeslib.as_ctypes(y)
    c_x = x.ctypes.data_as(ctypes.POINTER(ctypes.c_long))

    _dll.pred_period(c_period,c_len,c_x,c_y)

    y = pd.DataFrame(list(c_y),columns=['period'])
    y.index = df.index

    y.to_csv(target_folder+tick+'.csv')