import numpy as np
import pandas as pd

import torch
from torch.utils.data import Dataset

device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

class OHLCDataset(Dataset):
    def __init__(self, t_df ,pred ,seq_length, ohlc=True):
        super(OHLCDataset, self).__init__()
        self.seq_length = seq_length
        self.start = (seq_length+1)*1440
        self.ohlc = ohlc
        
        self.df_T = torch.FloatTensor(self.sampling_range(t_df, 'T').T.values).to(device)
        self.df_10T = torch.FloatTensor(self.sampling_range(t_df, '15T').T.values).to(device)
        self.df_H = torch.FloatTensor(self.sampling_range(t_df, '60T').T.values).to(device)
        self.df_D = torch.FloatTensor(self.sampling_range(t_df, '1440T').T.values).to(device)
        
        self.y = torch.FloatTensor(y).to(device)
        
    def __getitem__(self,index):
        index = index + self.start        
        
        self.x_data = torch.stack((self.df_T[:,index - self.seq_length : index],
                                self.df_10T[:,index//15 - self.seq_length : index//15],
                                self.df_H[:,index//60 - self.seq_length : index//60],
                                self.df_D[:,index//1440 - self.seq_length : index//1440]))

        self.y_data = self.y[index]
        
        return self.x_data, self.y_data
        
    def __len__(self):
        return len(self.df_T.T) - self.start


    def sampling_range(self, df, T_range):
        df_sample = pd.DataFrame()
        if self.ohlc:
            df_sample['open'] = df['open'].resample(T_range).first()
            df_sample['high'] = df['high'].resample(T_range).max()
            df_sample['volume'] = df['volume'].resample(T_range).sum()
            df_sample['low'] = df['low'].resample(T_range).min()

        df_sample['close'] = df['close'].resample(T_range).last()
        
        df_c = df_sample['close'].shift()
        
        if self.ohlc:
            for i in ['open','high','low']:
                df_sample[i] = (df_sample[i] - df_c) / df_c

        df_sample['close'] = (df_sample['close'] - df_c) / df_c

        for i in df_sample:
            df_sample[i] = df_sample[i] / df_sample[i].abs().max()
        
        return df_sample