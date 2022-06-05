import torch
import torch.nn as nn

class sCNN(nn.Module):
    def __init__(self, hidden_size, num_layers,seq_length):
        super(sCNN, self).__init__()
        self.num_layers = num_layers
        self.hidden_size = hidden_size
        
        self.lstm1 = nn.LSTM(input_size = 5,hidden_size=hidden_size, num_layers=num_layers, batch_first=True, dropout=0.5)
        self.lstm2 = nn.LSTM(input_size = 5,hidden_size=hidden_size, num_layers=num_layers, batch_first=True, dropout=0.5)
        self.lstm3 = nn.LSTM(input_size = 5,hidden_size=hidden_size, num_layers=num_layers, batch_first=True, dropout=0.5)
        self.lstm4 = nn.LSTM(input_size = 5,hidden_size=hidden_size, num_layers=num_layers, batch_first=True, dropout=0.5)
        
        self.conv1 = nn.Conv1d(in_channels=hidden_size*4, out_channels=4, kernel_size=10, stride=2)
        self.conv2 = nn.Conv1d(in_channels=4, out_channels=1,kernel_size=3, stride=2)

        self.fc1 = nn.Linear((seq_length-10)//4,1)
                
    def forward(self, x):
        x = x.permute((1,0,2,3))
        
        x1, h1 = self.lstm1(x[3])
        x2, h2 = self.lstm2(x[2], h1)
        x3, h3 = self.lstm3(x[1], h2)
        x4, _ = self.lstm4(x[0], h3)
        
        x = torch.cat((x1,x2,x3,x4),2).permute((0,2,1))
        x = self.conv1(x)
        x = self.conv2(x)
        
        x = self.fc1(x.flatten(1))
        return x


class OLNN(nn.Module):
    def __init__(self, seq_length):
        super(OLNN, self).__init__()
        self.conv1 = nn.Conv1d(in_channels=5, out_channels=8, kernel_size=10)
        self.conv2 = nn.Conv1d(in_channels=5, out_channels=8, kernel_size=10)
        self.conv3 = nn.Conv1d(in_channels=5, out_channels=8, kernel_size=10)
        self.conv4 = nn.Conv1d(in_channels=5, out_channels=8, kernel_size=10)
        
        self.conv5 = nn.Conv1d(in_channels=32, out_channels=16, kernel_size=5)
        self.conv6 = nn.Conv1d(in_channels=16, out_channels=4,kernel_size=4)
        self.conv7 = nn.Conv1d(in_channels=4, out_channels=2,kernel_size=2)
        
        self.fc1 = nn.Linear((seq_length-17)*2,64)
        self.fc2 = nn.Linear(64,8)
        self.fc3 = nn.Linear(8,1)
        
    def forward(self, x):
        x = x.permute((1,0,3,2))
        
        x1 = self.conv1(x[0])
        x2 = self.conv2(x[1])
        x3 = self.conv3(x[2])
        x4 = self.conv4(x[3])
        
        x = torch.cat((x1,x2,x3,x4),1)
        x = self.conv5(x)
        x = self.conv6(x)
        x = self.conv7(x)

        x = self.fc1(x.flatten(1))
        x = self.fc2(x)
        x = self.fc3(x)
        return x

def fit(epoch, model, data_loader, criterion, optimizer, phase='valid', print_loss=True):
    if phase == 'train':
        model.train()
    if phase == 'valid':
        model.eval()
    
    running_loss = 0.0
    for batch_idx, (data, target) in enumerate(data_loader):
        data, target = data, target
        
        if phase == 'train':
            optimizer.zero_grad()
        output = model(data)
        loss = criterion(output.permute(1,0), target.permute(1,0))
        running_loss += loss.item()
        
        if phase == 'train':
            loss.backward()
            optimizer.step()
        
    loss = running_loss / len(data_loader.dataset)
    
    if print_loss:
        print (f'epoch:{epoch}, {phase}loss is {format(loss,'.10f')}')
    return loss