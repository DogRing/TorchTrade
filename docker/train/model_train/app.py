import torch
from torch import nn
from tqdm import tqdm
import json
import time
import sys
import os

sys.path.append("/model")
from dataset import train_loader,test_loader
from Model import Model,Configs

num_epochs = int(os.environ.get('EPOCHES','50'))
tqdm_refresh = int(os.environ.get('TQDM_REFRESH','1000'))
param_path = os.environ.get('RESULT_PATH','/model/results/result.pt')
config_file = os.environ.get('MODEL_CONFIG','/model/model.json')

device=torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
print(device)

with open(config_file,'r') as f:
    config = json.load(f)
configs = Configs(config)
model = Model(configs).to(device)
if os.path.exists(param_path)==True:
    model.load_state_dict(torch.load(param_path,weights_only=True))

criterion = nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

start=time.time()
print(f'Start At {time.strftime("%m-%d %H:%M:%S",time.localtime(start))}')
for epoch in range(num_epochs):
    model.train()
    train_loss = 0.0
    train_pbar = tqdm(total=len(train_loader),desc=f'Epoch{epoch+1}/{num_epochs} [Train]',mininterval=20,position=0,leave=False)
    for i, (input_tensor, target_tensor) in enumerate(train_loader):
        input_tensor = input_tensor.to(device)
        target_tensor = target_tensor.to(device)
        outputs = model(input_tensor)
        loss = criterion(outputs, target_tensor)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        train_loss += loss.item()
        if (i + 1) % tqdm_refresh == 0 or (i + 1) == len(train_loader):
            train_pbar.update(tqdm_refresh if i != len(train_loader)-1 else len(train_loader) % tqdm_refresh)
            train_pbar.set_description(f'Epoch {epoch+1}/{num_epochs} [Train] loss: {train_loss / (i + 1):.4f}')
    train_pbar.close()
    avg_train_loss = train_loss / len(train_loader)
    model.eval()
    test_loss = 0.0
    with torch.no_grad():
        for input_tensor, target_tensor in test_loader:
            input_tensor = input_tensor.to(device)
            target_tensor = target_tensor.to(device)
            outputs = model(input_tensor)
            loss = criterion(outputs, target_tensor)
            test_loss += loss.item()
    avg_test_loss = test_loss / len(test_loader)
    print(f'Epoch [{epoch+1}/{num_epochs}] {((time.time()-start)/60):.2f}M, Train Loss: {avg_train_loss:.4f}, Test Loss: {avg_test_loss:.4f}')
    torch.save(model.state_dict(),param_path)
end=time.time()
print(f'End At {time.strftime("%m-%d %H:%M:%S",time.localtime(end))}, Mean per epoch {((end-start)/60/num_epochs):.2f}')