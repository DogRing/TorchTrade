import numpy as np
import pandas as pd

from numpy.ctypeslib import ndpointer
import ctypes

def pred_per(x, per, ohlc=True):
    _dll = ctypes.CDLL('setPred.dll')
    _doublepp = ndpointer(dtype=np.uintp, ndim=1, flags='C')

    _pred = _dll.pred_period
    _pred.argtypes = [ctypes.c_float, ctypes.c_int, ctypes.c_bool, _doublepp, _doublepp]
    _pred.restype = None

    y =  np.zeros_like(x[['close']], dtype = int)
    ypp = (y.__array_interface__['data'][0]
        + np.arange(y.shape[0])*y.strides[0]).astype(np.uintp)

    if ohlc:
        x_np = x[['open','high','low','close']].to_numpy(dtype =int)

        xpp = (x_np.__array_interface__['data'][0]
            + np.arange(x_np.shape[0])*x_np.strides[0]).astype(np.uintp)

        d_m = ctypes.c_int(x.shape[0])
        
        _pred(per, d_m, True ,xpp, ypp)


    else:
        x_np = x[['close']].to_numpy(dtype=int)

        xpp = (x_np.__array_interface__['data'][0]
            + np.arange(x_np.shape[0])*x_np.strides[0]).astype(np.uintp)
        
        d_m = ctypes.c_int(x.shape[0])

        _pred(per,d_m,False,xpp,ypp)

    return y