import pandas as pd
from datetime import datetime
from datetime import timedelta
from pandas.core.frame import DataFrame

from sklearn.preprocessing import MinMaxScaler as scaler_

first_date = datetime(2021,6,28)

def timetoint(time,interval_min=3):
    try:
        dtime = datetime.strptime(time,'%Y-%m-%d %H:%M:%S')
    except:
        dtime =datetime.strptime(time,'%Y-%m-%d')
    deltatime=dtime-first_date
    conv=(deltatime.seconds/60+deltatime.days*1440)/interval_min
    return conv

def inttotime(time,interval_min=3):
    mins = time*interval_min
    orig = timedelta(days=int(mins/1440),seconds=(mins%1440)*60)
    return first_date+orig

class DATAIO_6to1():
    def __init__(self,tickers,data_path,exten,in_size=1000,pred_size=20) -> None:
        # fix
        self.data_path = data_path
        self.exten = exten
        self.tickers = tickers
        self.train_size = in_size+pred_size
        self.size = in_size
        self.pred_size = pred_size
        self.scaler = scaler_()
        
        self.lasts = {}
        for i in range(len(tickers)):
            self.lasts[i] = 0
        if not self.set_first(0):
            print('Need more data')
    
    def set_first(self,index):
        first_date = inttotime(self.lasts[index])
        temp_date = first_date
        self.table = pd.DataFrame()
        self.index = index
        # enough data from first_date
        try:
            while len(self.table)<=self.train_size:
                df = pd.read_csv(self.data_path+self.tickers[index]+'/'+temp_date.strftime('%Y-%m-%d')+self.exten)
                df = df.iloc[:,:-1]                                     # delete later
                df['date'] = df['date'].map(timetoint)
                self.table = pd.concat([self.table,df],ignore_index=True)
                temp_date = temp_date+timedelta(days=1)
            self.last_date = temp_date

            # data after lasts              <--- need to modify because of time cost
            data_first = self.table['date'] >= self.lasts[index]
            self.table = self.table[data_first]

            return True
        except:
            print('there is not enough data'+self.tickers[self.index])
            return False

    def append_table(self):
        # append table
        try:
            self.last_date = self.last_date+timedelta(days=1)
            df = pd.read_csv(self.data_path+self.tickers[self.index]+'/'+self.last_date.strftime('%Y-%m-%d')+self.exten)
            df = df.iloc[:,:-1]                                            # delete later
            df['date'] = df['date'].map(timetoint)
            self.table = pd.concat([self.table,df],ignore_index=True)
            return True
        # there is no data to append
        except:
            return False

    def set_next_train(self):
        self.table = self.table.iloc[1:,:]
        if self.index == len(self.tickers):
            if self.set_first(0):
                return True
            else:
                self.index = len(self.tickers)
                return False
        if len(self.table)<self.train_size:
            if self.append_table():
                return True
            self.lasts[self.index] = self.table.iloc[0][0]
            while self.index+1<len(self.tickers):
                if self.set_first(self.index+1):
                    return True
            self.index = len(self.tickers)
            return False
        else:
            return True

    def set_init(self):
        for i in range(len(self.tickers)):
            self.lasts[i] = 0
        self.index = 0
        self.set_first(0)


    def get_train_data(self):
        result = self.set_table_diff()
        train = result.iloc[:self.size,:]
        ans = result.iloc[self.size:self.train_size,:]
        return train, ans

    def get_scaled_train_data(self):
        result = self.set_table_diff()
        result = result.iloc[:self.train_size,:]
        result = self.scaler.fit_transform(result)
        ans = result[self.size:self.train_size,5:6]
        result = result[:self.size,:]
        return result,ans

    def get_inverse(self, scaled_data):
        return self.scaler.inverse_transform(scaled_data)

    def set_table_diff(self):
        result = self.table['date'].iloc[1:]
        df = self.table.diff()
        result = pd.concat([result,df.iloc[1:,1:]],axis=1)
        return result

    def test_set(self):
        for i in range(len(self.tickers)):
            self.set_init(i)
            result = self.table[:-1000,:]
            print(result)