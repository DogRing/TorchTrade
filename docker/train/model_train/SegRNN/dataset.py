from local_values import data_folder
import torch
from torch.utils.data import Dataset,DataLoader,ConcatDataset
import pandas as pd
import json
import os

num_workers = int(os.environ.get('NUM_WORKERS','4'))
config_file = os.environ.get('DATA_CONFIG','/model/dataset.json')
train_ratio=float(os.environ.get('TRAIN_RATIO','0.8'))
with open(config_file,'r') as f:
    config = json.load(f)

class Bit_Dataset(Dataset):
    def __init__(self,data):
        super(Bit_Dataset,self).__init__()
        self.data=data.iloc[60:]
        self.seq_len=config.get('seq_len')
        self.pred_len=config.get('pred_len')
        self.features=config.get('features')
        self.target=config.get('target')
        self.x=self.data.iloc[:-self.pred_len][self.features].values
        self.y=self.data.iloc[self.seq_len:][self.target].values
        self.len=len(self.y)-self.pred_len
    def __len__(self):
        return self.len
    def __getitem__(self,idx):
        return torch.FloatTensor(self.x[idx:idx+self.seq_len]),torch.FloatTensor(self.y[idx:idx+self.pred_len])

train_datasets=[]
test_datasets=[]
for tick in config.get('tickers'):
    df = pd.read_csv(data_folder+tick+'.csv', parse_dates=[0],index_col=[0])
    train_size=int(len(df)*train_ratio)
    train_data = df.iloc[:train_size]
    test_data = df.iloc[train_size:]
    train_datasets.append(Bit_Dataset(train_data))
    test_datasets.append(Bit_Dataset(test_data))

concat_train_dataset = ConcatDataset(train_datasets)
concat_test_dataset = ConcatDataset(test_datasets)
train_loader = DataLoader(concat_train_dataset, batch_size=128, shuffle=True, pin_memory=True, num_workers=num_workers)
test_loader = DataLoader(concat_test_dataset, batch_size=64, shuffle=False, pin_memory=True, num_workers=num_workers)
