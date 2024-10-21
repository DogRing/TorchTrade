from local_values import raw_datas,datas
from rl_model import PPOAgent
from trade_env import TradingEnv
import torch
import pandas as pd
import json
import os

features = ["close", "EMA5", "EMA30", "EMA60", "value", "BW20", "dis20", "Mmt20", "RSI14", "MACD"]
data_df = pd.read_csv(datas[0],parse_dates=[0],index_col=[0])
data_df = data_df[features][3000000:]
data_df = torch.FloatTensor(data_df.values).unsqueeze(dim=0)
close_df = pd.read_csv(raw_datas[0],parse_dates=[0],index_col=[0])
close_df = close_df.resample(rule='min').first()
close_df = close_df.interpolate()
close_df = close_df['close'][3000000:]

param_path = os.environ.get('MODEL_PTH','/model/results/result.pt')
num_episodes = int(os.environ.get('EPISODES','3'))
config_file = os.environ.get('MODEL_CONFIG','/model/model.json')
with open(config_file,'r') as f:
    config = json.load(f)

config['d_model'] = 48
env = TradingEnv(data_df,close_df,balance=1000000,seq_len=180)
agent = PPOAgent(config,action_dim=5,lr=0.001,gamma=0.95,epsilon=0.2,K_epochs=10)

for episode in range(num_episodes):
    state, balance = env.reset()
    done = False
    total_reward = 0
    states,actions,balances,rewards,next_states,dones = [],[],[],[],[],[]
    while not done:
        action = agent.get_action(state,balance)
        next_state,balance,reward,done,_=env.step(action)
        states.append(state.unsqueeze(0))
        balances.append(balance)
        actions.append(action)
        rewards.append(reward)
        next_states.append(next_state)
        dones.append(done)
        state = next_state
        total_reward+=reward
    agent.update(states,balances,actions,rewards,next_states,dones)
    print(f"Episode {episode + 1}, Total Reward: {total_reward}")
