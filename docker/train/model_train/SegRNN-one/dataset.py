from local_values import data_folder,target_folder
import torch
from torch.utils.data import Dataset,DataLoader,ConcatDataset
import pandas as pd
import numpy as np
import json
import os

num_workers = int(os.environ.get('NUM_WORKERS','4'))
config_file = os.environ.get('DATA_CONFIG','/model/dataset.json')
train_ratio=float(os.environ.get('TRAIN_RATIO','0.8'))

with open(config_file,'r') as f:
    config = json.load(f)

class Bit_Dataset(Dataset):
    def __init__(self,data,target):
        super(Bit_Dataset,self).__init__()
        self.seq_len=config.get('seq_len')
        self.pred_len=config.get('pred_len')
        self.features=config.get('features')
        self.x=data.iloc[60:][self.features].values
        y=target.iloc[60:].values
        y=np.clip(y,-300,300)
        y=np.where(np.abs(y)<=30,((1-abs(y)/30)*np.sign(y)),y)
        self.y=np.where(np.abs(y)>30,((1-(abs(y)-15)/(300-15))*np.sign(y)*0.1),y)
        self.len=len(self.y)-self.seq_len 
    def __len__(self):
        return self.len
    def __getitem__(self,idx):
        return torch.FloatTensor(self.x[idx:idx+self.seq_len]),torch.FloatTensor(self.y[idx+self.seq_len-1])

train_datasets=[]
test_datasets=[]
for tick in config.get('tickers'):
    train_df = pd.read_csv(data_folder+tick+'.csv', parse_dates=[0],index_col=[0])
    target_df = pd.read_csv(target_folder+tick+'.csv',parse_dates=[0],index_col=[0])
    train_size=int(len(train_df)*train_ratio)
    target_df=target_df.loc[:train_df.index[-1]]
    train_data = train_df.iloc[:train_size]
    train_target = target_df.iloc[:train_size]
    test_data = train_df.iloc[train_size:]
    test_target = target_df.iloc[train_size:]
    train_datasets.append(Bit_Dataset(train_data,train_target))
    test_datasets.append(Bit_Dataset(test_data,test_target))

concat_train_dataset = ConcatDataset(train_datasets)
concat_test_dataset = ConcatDataset(test_datasets)
train_loader = DataLoader(concat_train_dataset, batch_size=64, shuffle=True, pin_memory=True, num_workers=num_workers)
test_loader = DataLoader(concat_test_dataset, batch_size=32, shuffle=False, pin_memory=True, num_workers=num_workers)
