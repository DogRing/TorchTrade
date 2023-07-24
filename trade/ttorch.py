import torch
import torch.nn as nn

class SCI_Block(nn.Module):
    def __init__(self, features, hidden, dropout=0.5):
        super(SCI_Block,self).__init__()
        self.dropout = dropout
        self.pad = nn.ReplicationPad1d((1,0))
        self.phi = nn.Sequential(
            nn.ReplicationPad1d((5,1)),
            nn.Conv1d(features, hidden, kernel_size=4,dilation=1, stride=1),
            nn.LeakyReLU(negative_slope=0.01, inplace=True),
            nn.Dropout(self.dropout),
            nn.Conv1d(hidden, features, kernel_size=4),
            nn.Tanh()
        )
        self.psi = nn.Sequential(
            nn.ReplicationPad1d((5,1)),
            nn.Conv1d(features, hidden, kernel_size=5,dilation=1, stride=1),
            nn.LeakyReLU(negative_slope=0.01, inplace=True),
            nn.Dropout(self.dropout),
            nn.Conv1d(hidden, features, kernel_size=3),
            nn.Tanh()
        )
        self.U   = nn.Sequential(
            nn.ReplicationPad1d((5,1)),
            nn.Conv1d(features, hidden, kernel_size=5,dilation=1, stride=1),
            nn.LeakyReLU(negative_slope=0.01, inplace=True),
            nn.Dropout(self.dropout),
            nn.Conv1d(hidden, features, kernel_size=3),
            nn.Tanh()
        )
        self.P   = nn.Sequential(
            nn.ReplicationPad1d((5,1)),
            nn.Conv1d(features, hidden, kernel_size=5,dilation=1, stride=1),
            nn.LeakyReLU(negative_slope=0.01, inplace=True),
            nn.Dropout(self.dropout),
            nn.Conv1d(hidden, features, kernel_size=3),
            nn.Tanh()
        )
    
    def forward(self, F):
        if F.size()[2] %2 == 1:
            F = self.pad(F)
        Fe = F[:, :,  ::2]
        Fo = F[:, :, 1::2]
        d = Fo.mul(torch.exp(self.phi(Fe)))
        c = Fe.mul(torch.exp(self.psi(Fo)))
        
        Fe = c + self.U(d)
        Fo = d - self.P(c)
        
        return Fo, Fe
    

class SCINet(nn.Module):
    def __init__(self, L, features, hidden):
        super(SCINet, self).__init__()
        self.num_layer = 2**L-1
        self.L = L
        self.layers = nn.ModuleList(
            [SCI_Block(features, hidden) for i in range(self.num_layer)])
        
    def forward(self, x):
        results = [x]
        for i in range(self.num_layer):
            seq = results.pop(0)
            Fo, Fe = self.layers[i](seq)
            results.append(Fo)
            results.append(Fe)
        
        interval = 2**(self.L-1)
        while True:
            res = []
            for i in range(interval):
                res.append(torch.cat((results[i], results[i+interval]),2))
            
            results = res
            if interval == 1:
                break
            else:
                interval = interval//2
        x = x + results[0]
        return x
    
class SCINet_stack(nn.Module):
    def __init__(self, stacks, layers, features, hidden=16):
        super(SCINet_stack, self).__init__()
        self.layers = nn.ModuleList(
            [SCINet(layers,features,hidden) for i in range(stacks)])
        self.fc1 = nn.Linear(64,16)
        self.fc2 = nn.Linear(16*features,64)
        self.fc3 = nn.Linear(64,16)
        self.fc4 = nn.Linear(16,1)
    
    def forward(self, x):
        for i in self.layers:
            x = i(x)
        x = self.fc1(x)
        x = self.fc2(x.flatten(1))
        x = self.fc3(x)
        x = self.fc4(x)
        return x

device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
model = SCINet_stack(2,6,14, hidden=16).to(device)
path = "./SCINp.pt"
model.load_state_dict(torch.load(path))
model.to(device)
model.eval()

def pred_per(x_data):
    x = torch.FloatTensor(x_data).to(device)
    x[-4:] -= x[-4:].min(1,keepdim=True)[0]
    x[-4:] /= x[-4:].max(1,keepdim=True)[0]
    x = torch.nan_to_num(x)
    x = torch.reshape(x,(1,14,64))
    return model(x)[0][0].item()