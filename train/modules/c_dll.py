import os
import ctypes

file_name=__file__.split('/')[-1]
dir=__file__.split(file_name)[0] + 'object/'

if not os.path.exists(dir):
    os.mkdir(dir)

object_name=file_name.split('.py')[0]
file_c=dir+object_name+'.c'
file_o=dir+object_name+'.o'
file_so=dir+object_name+'.so'

with open(file_c,'w') as c:
    c.write("""
            #include <stdio.h>

            void pred_period(const float per, const int len, int* x, int* y)
            {
                unsigned long upper, lower;
                for (int i=0;i<len;i++){
                    upper = (unsigned long)(x[i] * (1+per));
                    lower = (unsigned long)(x[i] * (1-per));

                    for (int j=i;j<len;j++){
                        if (upper < x[j]){
                            y[i]=j-i;
                            break;
                        }
                        else if (lower > x[j]){
                            y[i]=i-j;
                            break;
                        }
                    }
                }
            }
            """)
    
os.system('gcc -c '+file_c+' -o '+file_o)
os.system('gcc -shared '+file_o+' -o '+file_so)

def pred_period(period, x):
    import numpy as np

    _dll=ctypes.cdll.LoadLibrary(file_so)
    x_len=len(x)

    y=np.zeros(x_len, dtype=np.int32)
    y=np.ctypeslib.as_ctypes(y)
    
    x=x.to_numpy(dtype=np.int32, copy=True).flatten()
    x=x.ctypes.data_as(ctypes.POINTER(ctypes.c_long))
    x_len=ctypes.c_int(x_len)
    c_period=ctypes.c_float(period)

    _dll.pred_period(c_period,x_len,x,y)

    return y