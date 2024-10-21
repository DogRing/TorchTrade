import gym
import numpy as np
import pandas as pd
from gym import spaces

class TradingEnv(gym.Env):
    def __init__(self,data_df,close_df,balance,seq_len,fee=0.9975):
        super(TradingEnv,self).__init__()
        self.data_df=data_df
        self.close_df=close_df.values
        self.current_price=self.close_df[seq_len-1]
        self.seq_len=seq_len
        self.fee=fee
        self.init_balance=balance
        self.reward_range=(-np.inf,np.inf)
        self.action_space=spaces.Discrete(5)
        self.reset()

    def reset(self):
        self.current_step=0
        self.coin_held=0
        self.balance=self.init_balance
        return self._next_observation()

    def _next_observation(self):
        obs=self.data_df[:,self.current_step:self.current_step+self.seq_len]
        return obs,[self.balance / self.init_balance,self.coin_held * self.current_price /self.init_balance]
    
    def step(self,action):
        current_price=self.close_df[self.current_step+self.seq_len-1]
        if action== 0:
            self.balance+=current_price * self.coin_held * self.fee
            self.coin_held=0
        if action== 1:
            self.balance+=current_price * self.coin_held * 0.5 * self.fee
            self.coin_held=self.coin_held*0.5
        if action== 3:
            self.coin_held+=self.balance * 0.5 / current_price * self.fee
            self.balance-=self.balance*0.5
        if action== 4:
            self.coin_held=self.balance / current_price * self.fee
            self.balance=0
        self.current_step+=1
        done=self.current_step >= len(self.data_df[0])-self.seq_len-1
        obs,balance=self._next_observation()
        reward=self.balance+self.coin_held*current_price
        return obs,balance,reward,done,{}
    
    def render(self):
        print(f'Step: {self.current_step}')
        print(f'Bitcoin Held: {self.coin_held}')
        print(f'Balance: ${self.balance:.2f}')
