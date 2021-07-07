import pandas as pd
from datetime import datetime
from datetime import timedelta
import matplotlib.pyplot as plt

import torch
import torch.nn as nn
from torch.autograd import Variable
from torch.nn.modules.rnn import LSTM 

data_path = './datas/'
exten = '.csv'
tickers = ['KRW-BTC','KRW-XRP','KRW-DOGE','KRW-TFUEL','KRW-ETH','KRW-ETC','KRW-SBD','KRW-STRK']
first_date = datetime(2021,6,28)

# set device
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")  # device

# 예측할 data 수
N = 300

# 데이터 불러오기 
df1 = pd.read_csv(data_path+tickers[0]+'/'+first_date.strftime('%Y-%m-%d')+exten,index_col='date')
second_date = first_date + timedelta(days=1)
df2 = pd.read_csv(data_path+tickers[0]+'/'+second_date.strftime('%Y-%m-%d')+exten,index_col='date')
df=pd.concat([df1,df2])

# 필요한 data만 꺼내기
df = df.drop(columns='value')
X = df.iloc[:-N,:]
Y = df.iloc[N:,:]
Y = Y.drop(columns='volume')

# data 정규화
from sklearn.preprocessing import MinMaxScaler
mm = MinMaxScaler()
X_mm = mm.fit_transform(X)
Y_mm = mm.fit_transform(Y)

# train data와 test data 나누기 => 실제론 필요 없다
X_train = X_mm[:888,:]
Y_train = Y_mm[:888,:]
X_test = X_mm[888:,:]
Y_test = Y_mm[888:,:]

# torch 형태로 바꾸기 
X_train_tensors = Variable(torch.Tensor(X_train))
Y_train_tensors = Variable(torch.Tensor(Y_train))
X_test_tensors = Variable(torch.Tensor(X_test))
Y_test_tensors = Variable(torch.Tensor(Y_test))

X_train_tensors_final = torch.reshape(X_train_tensors,   (X_train_tensors.shape[0], 1, X_train_tensors.shape[1]))
X_test_tensors_final = torch.reshape(X_test_tensors,  (X_test_tensors.shape[0], 1, X_test_tensors.shape[1])) 

class LSTM1(nn.Module):
  def __init__(self, num_classes,input_size,hidden_size,num_layers,seq_length):
    super(LSTM1,self).__init__()
    self.num_classes = num_classes
    self.num_layers = num_layers
    self.input_isze = input_size
    self.hidden_size = hidden_size
    self.seq_length = seq_length

    self.lstm = nn.LSTM(
      input_size=input_size,hidden_size=hidden_size,num_layers=num_layers,batch_first=True)
    self.fc_1 = nn.Linear(hidden_size,128)
    self.fc = nn.Linear(128,num_classes)

    self.relu = nn.ReLU()

  def forward(self,x):
    h_0 = Variable(torch.zeros(self.num_layers,x.size(0),self.hidden_size)).to(device)
    c_0 = Variable(torch.zeros(self.num_layers,x.size(0),self.hidden_size)).to(device)

    output, (hn, cn) = self.lstm(x,(h_0,c_0))

    hn = hn.view(-1,self.hidden_size)
    out = self.relu(hn)
    out = self.fc_1(out)
    out = self.relu(out)
    out = self.fc(out)

    return out

num_epochs = 30000
lr = 0.0001

input_size = 5
hidden_size = 1
num_layers = 1

num_classes = 4

lstm1 = LSTM1(num_classes,input_size,hidden_size,num_layers,X_train_tensors.shape[1]).to(device)

loss_function = torch.nn.MSELoss()
optimizer = torch.optim.Adam(lstm1.parameters(), lr=lr)

# 학습
for epoch in range(num_epochs):
  outputs = lstm1.forward(X_train_tensors_final.to(device))
  optimizer.zero_grad()
  loss = loss_function(outputs, Y_train_tensors.to(device))
  loss.backward()
  optimizer.step()
  if epoch %100 ==0:
    print("Epoch : %d, loss : %1.6f" % (epoch,loss.item()))

# 학습한 걸로 예측하기
X = df.iloc[:-N,:]
Y = df.iloc[N:,:]
Y = Y.drop(columns='volume')
df_X_mm = mm.fit_transform(X)
df_Y_mm = mm.fit_transform(Y)
df_X_mm = Variable(torch.Tensor(df_X_mm)) #converting to Tensors
df_Y_mm = Variable(torch.Tensor(df_Y_mm))
df_X_mm = torch.reshape(df_X_mm, (df_X_mm.shape[0], 1, df_X_mm.shape[1]))

train_predict = lstm1(df_X_mm.to(device))#forward pass
data_predict = train_predict.data.detach().cpu().numpy() #numpy conversion
dataY_plot = df_Y_mm.data.numpy()

data_predict = mm.inverse_transform(data_predict) #reverse transformation
dataY_plot = mm.inverse_transform(dataY_plot)
plt.figure(figsize=(10,6)) #plotting
plt.axvline(x=888, c='r', linestyle='--') #size of the training set

y_index = Y.iloc[:,0:1]
datap = pd.DataFrame(dataY_plot)
predp = pd.DataFrame(data_predict)

y_close = Y.iloc[:,3:4]
p_close = data_predict[:,3:4]
plt.plot(y_close, label='Actuall Data') #actual plot
plt.plot(p_close, label='Predicted Data') #predicted plot
plt.title('Time-Series Prediction')
plt.legend()
plt.show() 
