from os import system
from torch.autograd.grad_mode import no_grad
from torch.nn.modules import loss
from torch_data import DATAIO_6to1
from datetime import datetime
from datetime import timedelta
import matplotlib.pyplot as plt

import torch
import torch.nn as nn
import torch.optim as optim
from torch.autograd import Variable
from torch.nn.modules.rnn import LSTM 
import torch.nn.functional as F

data_path = './datas/'
exten = '.csv'
tickers = ['KRW-BTC','KRW-XRP','KRW-DOGE','KRW-TFUEL','KRW-ETH','KRW-ETC','KRW-SBD','KRW-STRK']
first_date = datetime(2021,6,28)

# set device
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")  # device
seq_length = len(tickers)

dbio = DATAIO_6to1(tickers,data_path=data_path,exten=exten)

class LSTMPredictor(nn.Module):
    def __init__(self,n_hidden=51):
        super(LSTMPredictor,self).__init__()
        self.n_hidden = n_hidden
        # lstm1, lstm2 => cell, linear
        self.lstm1 = nn.LSTMCell(6000,self.n_hidden)
        self.lstm2 = nn.LSTMCell(self.n_hidden,self.n_hidden)
        self.linear = nn.Linear(self.n_hidden,20)

    def forward(self,x):
        n_samples = x.size(0)
        
        # lstm1
        h_0 = torch.zeros(n_samples,self.n_hidden)
        c_0 = torch.zeros(n_samples,self.n_hidden)
        # lstm2
        h_02 = torch.zeros(n_samples,self.n_hidden)
        c_02 = torch.zeros(n_samples,self.n_hidden)

        h_t,c_t = self.lstm1(x,(h_0,c_0))
        h_t2,c_t2 = self.lstm2(h_t,(h_02,c_02))
        output = self.linear(h_t2)

        return output

    
model = LSTMPredictor()
criterion = nn.MSELoss()
optimizer = optim.LBFGS(model.parameters(),lr=0.001)

n_steps = 1
epochs = 10

# for epoch in range(epochs):
try:
    for i in range(100000):
        before, after = dbio.get_scaled_train_data()

        train_x = Variable(torch.Tensor(before))
        train_y = Variable(torch.Tensor(after))

        train_x = train_x.view(1,6000)
        train_y = train_y.view(1,20)

        for i in range(n_steps):
            def closure():
                optimizer.zero_grad()
                out = model(train_x)
                loss = criterion(out,train_y)
                if i == n_steps-1:
                    print("loss",loss.item())
                loss.backward()
                return loss
            optimizer.step(closure)
        print(train_x[0])
        if not dbio.set_next_train():
            print('normal')
            break
        print("next set")
        print(i)

        # print("epoch",epoch)
        # dbio.set_init()
except:
    pass

tessss = dbio.table.iloc[-1001:,:]
from sklearn.preprocessing import MinMaxScaler as scaler_
import pandas as pd
scaleee = scaler_()

result = tessss['date'].iloc[1:]
df = tessss.diff()
result = pd.concat([result,df.iloc[1:,1:]],axis=1)
test_y = scaleee.fit_transform(result)

test_y = Variable(torch.Tensor(test_y))

test_y = test_y.reshape(1,6000)

with torch.no_grad():
    pred = model(test_y)
    y = pred.detach().numpy()
    print(y)
    res = scaleee.inverse_transform(y)

    print(res)