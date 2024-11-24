import torch
from torch import nn
import json
import time
import sys
import os

sys.path.append("/model")
from dataset import train_loader,test_loader
from Model import Model,Configs

num_epochs = int(os.environ.get('EPOCHES','50'))
param_path = os.environ.get('RESULT_PATH','/model/results/result.pt')
config_file = os.environ.get('MODEL_CONFIG','/model/model.json')
kst_offset = 9 * 3600

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

start=time.time() + kst_offset
print(f'Start At {time.strftime("%m-%d %H:%M:%S",time.localtime(start))}')
for epoch in range(num_epochs):
    model.train()
    train_loss = 0.0
    for input_tensor, target_tensor in train_loader:
        input_tensor = input_tensor.to(device)
        target_tensor = target_tensor.to(device)
        outputs = model(input_tensor)
        loss = criterion(outputs, target_tensor)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        train_loss += loss.item()
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
    spend = time.time() - start + kst_offset
    time_per_epoch = spend / (epoch + 1)
    next_epoch_end_time = start + (epoch + 2) * time_per_epoch
    all_epoch_end_time = start + num_epochs * time_per_epoch
    print(f'Epoch [{epoch+1}/{num_epochs}] '
            f'Loss (Train|Test): {avg_train_loss:.4f} | {avg_test_loss:.4f}, '
            f'Next: {time.strftime("%H:%M",time.localtime(next_epoch_end_time))}, '
            f'End: {time.strftime("%H:%M",time.localtime(all_epoch_end_time))} '
            f'Spend: {((spend)/60):.2f}M')
    torch.save(model.state_dict(),param_path)
end=time.time() + kst_offset
print(f'End At {time.strftime("%m-%d %H:%M:%S",time.localtime(end))}, Mean per epoch {((end-start)/60/num_epochs):.2f}')