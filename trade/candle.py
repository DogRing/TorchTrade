from sys import maxsize
import numpy as np
import pandas as pd
from datetime import timedelta
from datetime import datetime
import multiprocessing as mp

from ttorch import pred_per
import indicators as idc
from bitsocket import update_data
import pyupbit

ticker = "KRW-ETC"
vol_mean, vol_std = 1230.9927118679511, 5741.353215181925
ohlc_abs_max = [0.0925, 0.16279069767441862, 0.12020138451856513, 0.16279069767441862]
BB_max = 0.4280650199268169
min_list = [-0.5898003255280515, -1835.7891845988452, 78.7547991205714]
max_list = [2.1799716769280266, 4081.9179989251625, 36.789791671746016]
access_key = ""
secret_key = ""

upbit = pyupbit.Upbit(access_key, secret_key)

class MyWindow():
    def __init__(self, q, interval=4):
        super().__init__()
        self.q = q
        self.interval = interval
        self.now_buy = False
        self.dist = timedelta(minutes=1)
        self.den = 90
        self.df_data = pd.DataFrame(np.zeros((self.den*interval, 5), dtype=int), columns=['open','high','low','close','volume'])

        now = datetime.now().replace(second=0, microsecond=0) + timedelta(minutes=1)
        self.intervals = []
        for i in range(1,interval+1):
            self.intervals.append(now + self.dist/interval*i)
        self.mData = np.zeros((interval,5), dtype=float)

        # wait data
        while self.q.empty(): pass 
        price, ttms, volume = self.q.get()
        
        for i in range(interval):
            while ttms < self.intervals[i]:
                if not i == 0 and self.mData[i-1][0] == 0:
                    self.mData[i-1][0] = price
                    self.mData[i-1][1] = price

                for j in range(i):
                    if self.mData[j][1] > price: self.mData[j][1] = price
                    if self.mData[j][2] < price: self.mData[j][2] = price
                    self.mData[j][3] = price
                    self.mData[j][4] += volume
                price, ttms, volume = self.q.get()
            self.intervals[i] += self.dist

        for c in range(self.interval):
            if self.mData[c,0] == 0:
                self.mData[c,:3] = price
            if self.mData[c,1] > price:
                self.mData[c,1] = price
            if self.mData[c,2] < price:
                self.mData[c,2] = price
        self.mData[:,3] = price
        self.mData[:,4] += volume
        print("set mData")

        for t in range(self.den-1):
            for i in range(self.interval):
                while datetime.now() < self.intervals[i]:
                    if not self.q.empty():
                        price, ttms, volume = self.q.get()
                        for c in range(self.interval):
                            if self.mData[c,0] == 0:
                                self.mData[c,:3] = price
                            if self.mData[c,1] > price:
                                self.mData[c,1] = price
                            if self.mData[c,2] < price:
                                self.mData[c,2] = price
                        self.mData[:,3] = price
                        self.mData[:,4] += volume

                if self.mData[i,0] == 0:
                    for r in range(5):
                        self.df_data.iat[self.den*i+t,r] = self.df_data.iat[self.den*i+t-1,r]
                else:
                    for r in range(5):
                        self.df_data.iat[self.den*i+t,r] = self.mData[i,r]
                # print(self.df_data[self.den*i:self.den*(i+1)])
                self.mData[i,:5] = 0
                self.intervals[i] += self.dist
            print(f'set df_data {t+1}')
        print(self.df_data)
        # self.df_data.to_csv("./testcsv.csv")
        # self.df_data = pd.read_csv("./testcsv.csv", index_col=[0])
        # print(self.df_data)

        feature_n = 64
        self.x_data = np.zeros((14,feature_n*self.interval))
        for t in range(feature_n):
            for i in range(self.interval):
                while datetime.now() < self.intervals[i]:
                    if not self.q.empty():
                        price, ttms, volume = self.q.get()
                        for c in range(self.interval):
                            if self.mData[c,0] == 0:
                                self.mData[c,:3] = price
                            if self.mData[c,1] > price:
                                self.mData[c,1] = price
                            if self.mData[c,2] < price:
                                self.mData[c,2] = price
                        self.mData[:,3] = price
                        self.mData[:,4] += volume


                if self.mData[i,0] == 0:
                    for r in range(5):
                        self.df_data.iat[self.den*(i+1)-1,r] = self.df_data.iat[self.den*(i+1)-2,r]
                else:
                    for r in range(5):
                        self.df_data.iat[self.den*(i+1)-1,r] = self.mData[i,r]
                self.mData[i,:5] = 0
                self.intervals[i] += self.dist
                
                d_idx = self.den*(i+1)
                f_idx = feature_n*i+t
                for s in range(4):
                    self.x_data[s,f_idx] = ((self.df_data.iat[d_idx-1,s] - self.df_data.iat[d_idx-2,3]) / self.df_data.iat[d_idx-2,3]) / ohlc_abs_max[s]
                self.x_data[4,f_idx] = (self.df_data.iat[d_idx-1,4] - vol_mean) / vol_std
                self.x_data[5,f_idx] = idc.RSI(self.df_data[d_idx-14:d_idx],14)
                self.x_data[6,f_idx], self.x_data[7,f_idx] = idc.BB(self.df_data[d_idx-20:d_idx],20)
                self.x_data[8,f_idx],_ = idc.MACD(self.df_data[d_idx-27:d_idx])
                self.x_data[9,f_idx] = idc.disparity(self.df_data[d_idx-20:d_idx],20).iat[-1]
                self.x_data[10,f_idx] = idc.EMA(self.df_data[d_idx-5:d_idx],5).iat[-1]
                self.x_data[11,f_idx] = idc.EMA(self.df_data[d_idx-30:d_idx],30).iat[-1]
                self.x_data[12,f_idx] = idc.EMA(self.df_data[d_idx-60:d_idx],60).iat[-1]
                self.x_data[13,f_idx] = idc.EMA(self.df_data[d_idx-90:d_idx],90).iat[-1]

                self.x_data[6, feature_n*i+t] /= BB_max
                for f_id in range(3):
                    self.x_data[f_id+7,f_idx] -= min_list[f_id]
                    self.x_data[f_id+7,f_idx] /= max_list[f_id]
            print(f'set x_data {t+1}')
            self.df_data = self.df_data.shift(-1)

    def operating(self):
        self.max_p = 0
        while True:
            self.x_data = np.roll(self.x_data, -1, axis=1)
            for i in range(self.interval):
                last_x = 64*(i+1) -1
                last_df = self.den*(i+1) -1
                while datetime.now() < self.intervals[i]:
                    if not self.q.empty():
                        price, ttms, volume = self.q.get()
                        for c in range(self.interval):
                            if self.mData[c,0] == 0:
                                self.mData[c,:3] = price
                            if self.mData[c,1] > price:
                                self.mData[c,1] = price
                            if self.mData[c,2] < price:
                                self.mData[c,2] = price
                        self.mData[:,3] = price
                        self.mData[:,4] += volume


                if self.mData[i,0] == 0:
                    for r in range(5):
                        self.df_data.iat[last_df,r] = self.df_data.iat[last_df-1,r]
                else:
                    for r in range(5):
                        self.df_data.iat[last_df,r] = self.mData[i,r]
                self.mData[i,:] = 0
                self.intervals[i] += self.dist
                
                for s in range(4):
                    self.x_data[s,last_x] = ((self.df_data.iat[last_df,s] - self.df_data.iat[last_df-1,3]) / self.df_data.iat[last_df-1,3]) / ohlc_abs_max[s]
                self.x_data[4,last_x] = (self.df_data.iat[last_df,4] - vol_mean) / vol_std
                self.x_data[5,last_x] = idc.RSI(self.df_data[last_df-14:last_df+1],14)
                self.x_data[6,last_x], self.x_data[7,last_x] = idc.BB(self.df_data[last_df-19:last_df+1],20)
                self.x_data[8,last_x], _ = idc.MACD(self.df_data[last_df-26:last_df+1])
                self.x_data[9,last_x] = idc.disparity(self.df_data[last_df-19:last_df+1],20).iat[-1]
                self.x_data[10,last_x] = idc.EMA(self.df_data[last_df-4:last_df+1],5).iat[-1]
                self.x_data[11,last_x] = idc.EMA(self.df_data[last_df-29:last_df+1],30).iat[-1]
                self.x_data[12,last_x] = idc.EMA(self.df_data[last_df-59:last_df+1],60).iat[-1]
                self.x_data[12,last_x] = idc.EMA(self.df_data[last_df-89:last_df+1],90).iat[-1]
                
                self.x_data[6, last_x] /= BB_max
                for f_id in range(3):
                    self.x_data[f_id+7,last_x] -= min_list[f_id]
                    self.x_data[f_id+7,last_x] /= max_list[f_id]
                
                self.do_something(self.x_data[:,64*i:64*i+64])
            self.df_data = self.df_data.shift(-1)
    
    def do_something(self,x):
        prob = pred_per(x[:,-64:])
        print(datetime.now(), prob)

        if prob > 0.46252 and not self.now_buy:
            print(upbit.buy_market_order(ticker, upbit.get_balance("KRW")*0.985))
            self.now_buy = True
            print("buy", self.df_data.iat[-1,3])
        elif self.now_buy:
            if prob > self.max_p:
                self.max_p = prob
            if prob < (self.max_p - 0.0779):
                print(upbit.sell_market_order(ticker, upbit.get_balance(ticker)*0.985))
                self.now_buy = False
                print("sell", self.df_data.iat[-1,3])
                self.max_p = 0
        # elif prob < 0.42431 and self.now_buy:
        #     print(upbit.sell_market_order(ticker, upbit.get_balance(ticker)*0.985))
        #     self.now_buy = False
        #     print("sell", self.df_data.iat[-1,3])
            
if __name__ == "__main__":
    q = mp.Queue()
    p = mp.Process(name="Producer", target=update_data, args=(q,ticker,), daemon=True)
    p.start()

    mywindow = MyWindow(q)
    mywindow.operating()
