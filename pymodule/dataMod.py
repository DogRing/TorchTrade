import numpy as np
import pandas as pd

import torch
from torch.utils.data import Dataset

device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

class OHLCDataset(Dataset):
    def __init__(self, t_df ,pred ,seq_length, ohlc=True):
        super(OHLCDataset, self).__init__()
        self.seq_length = seq_length
        self.start = seq_length*1440
        self.ohlc = ohlc
        
        self.df_T = torch.FloatTensor(self.sampling_range(t_df, 'T').values).to(device)
        self.df_10T = torch.FloatTensor(self.sampling_range(t_df, '15T').values).to(device)
        self.df_H = torch.FloatTensor(self.sampling_range(t_df, '60T').values).to(device)
        self.df_D = torch.FloatTensor(self.sampling_range(t_df, '1440T').values).to(device)
        
        y = np.array(pred, dtype=np.float32)
        y = np.reciprocal(y)
        y[y == np.inf] = 0
        self.y = torch.FloatTensor(y).to(device)
        
    def __getitem__(self,index):
        index = index + self.start        
        
        self.x_data = torch.stack((self.df_T[index - self.seq_length : index],
                                self.df_10T[index//10 - self.seq_length : index//10],
                                self.df_H[index//60 - self.seq_length : index//60],
                                self.df_D[index//1440 - self.seq_length : index//1440]))

        self.y_data = self.y[index]
        
        return self.x_data, self.y_data
        
    def __len__(self):
        return len(self.df_T) - self.start


    def sampling_range(self, df, T_range):
        if self.ohlc:
            df_sample = pd.DataFrame(df['open'].resample(T_range).first())
            df_sample['high'] = df['high'].resample(T_range).max()
            df_sample['volume'] = df['volume'].resample(T_range).sum()
            df_sample['low'] = df['low'].resample(T_range).min()
            for i in ['open','high','low']:
                df_sample[i] = df_sample[i] * 100 / df.close
        
        df_sample['close'] = df['close'].resample(T_range).last()
        df_sample['close'] = df_sample['close'] * 100 / df.close

        for i in df_sample:
            df_sample[i] = df_sample[i] / df_sample[i].abs().max()
        
        return df_sample