from local_values import raw_folder
import torch
import numpy as np
import pandas as pd
from tqdm import tqdm
import pickle
import json
import time
import sys
import os

sys.path.append("/model")
from dataset import config
from Model import Model,Configs

param_path = os.environ['MODEL_PATH']
config_file = os.environ.get('MODEL_CONFIG','/model/model.json')
pred_result = os.environ.get('RESULT_PATH','')
trading_fee = float(os.environ.get('TRADING_FEE','0.99'))

csv_file = raw_folder+config.get('tickers')[0]+".csv"
df=pd.read_csv(csv_file,parse_dates=[0],index_col=[0])[config.get('seq_len'):]

device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
print(device)

print(f"read csv {csv_file}")
with open(config_file,'r') as f:
    config = json.load(f)
configs = Configs(config)
model = Model(configs).to(device)
model.load_state_dict(torch.load(param_path,map_location=device,weights_only=True))

model = model.eval()
results=[]
if not bool(pred_result) or not os.path.exists(pred_result):
    print("cal results")
    from dataset import train_loader
    for input_tensor,_ in train_loader:
        pred = model(input_tensor.to(device))
        results.append(pred.view(-1,8))
    results = torch.cat(results, dim=0).tolist()
else:
    print("load results")
    with open(pred_result,"rb") as fp:
        results = pickle.load(fp)

if bool(pred_result) and not os.path.exists(pred_result):
    print("save results")
    with open(pred_result,"wb") as fp:
        pickle.dump(results,fp)

print("simulate")
from scipy.optimize import minimize

# 거래 전략을 시뮬레이션하는 함수
def trading_strategy(params):
    bp, sp = params  # bp와 sp는 최적화 매개변수입니다.
    buy = False
    now_price = 0
    total_profit = 0
    max_p = 0

    for v, pred in tqdm(enumerate(results)):
        if pred > bp and not buy:
            buy = True
            now_price = df['open'][v]

        if buy:
            if pred > max_p:
                max_p = pred
            if pred < (max_p - sp):
                buy = False
                total_profit += (df['open'][v]*trading_fee - now_price) / now_price
                max_p = 0

    return -total_profit  # 음수 이익 최소화를 통해 이익 최대화

# bp와 sp에 대한 초기 추정값
initial_params = [0.5, 0.5]

# 제약 조건: bp와 sp는 모두 0과 1 사이여야 합니다.
bounds = [(0, 1), (0, 1)]

# 최적화 수행
result = minimize(trading_strategy, initial_params, bounds=bounds)
optimized_bp, optimized_sp = result.x
max_profit = -result.fun

print(f"buy_point: {optimized_bp}")
print(f"sell_point: {optimized_sp}")
print(f"max profit: {max_profit}")
