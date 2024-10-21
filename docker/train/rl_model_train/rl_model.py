import torch
import torch.nn as nn
import torch.optim as optim
import sys

sys.path.append("/model")
from Model import Model,Configs
torch.set_num_threads(2)

device=torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

class ActorCritic(nn.Module):
    def __init__(self,config,action_dim):
        super(ActorCritic,self).__init__()
        output_dim = config.get('pred_len')
        self.model = Model(Configs(config))
        self.actor = nn.Linear(output_dim+2,action_dim)
        self.critic = nn.Linear(output_dim+2,1)

    def forward(self,x,b):
        features = self.model(x).squeeze(-1)
        c_features = torch.cat((features, b), dim=-1)
        action_probs = torch.softmax(self.actor(c_features),dim=-1)
        state_value = self.critic(c_features)
        return action_probs,state_value

class PPOAgent:
    def __init__(self,config,action_dim,lr,gamma,epsilon,K_epochs):
        self.policy = ActorCritic(config,action_dim).to(device)
        self.optimizer = optim.Adam(self.policy.parameters(),lr=lr)
        self.gamma = gamma
        self.epsilon = epsilon
        self.K_epochs = K_epochs

    def get_action(self,state,balance):
        balance = torch.FloatTensor(balance).unsqueeze(0).to(device)
        action_probs,_ = self.policy(state.to(device),balance)
        action = torch.multinomial(action_probs,1).item()
        return action

    def update(self,states,balances,actions,rewards,next_states,dones):
        states = torch.cat(states,dim=0).to(device)
        balances = torch.FloatTensor(balances).to(device)
        actions = torch.LongTensor(actions).to(device)
        rewards = torch.FloatTensor(rewards).to(device)
        next_states = torch.FloatTensor(next_states).to(device)
        dones = torch.FloatTensor(dones).to(device)

        _,values = self.policy(states,balances)
        _,next_values = self.policy(next_states,balances)
        advantages = []
        gae = 0
        for t in reversed(range(len(rewards))):
            delta = rewards[t] + self.gamma * next_values[t] * (1 - dones[t]) - values[t]
            gae = delta + self.gamma * 0.95 * (1 - dones[t]) * gae
            advantages.insert(0,gae)
        advantages = torch.tensor(advantages).float().to(device)
        
        batch_size = 128
        for _ in range(self.K_epochs):
            for i in range(0,len(states),batch_size):
                batch_states = states[i:i+batch_size]
                batch_balances = balances[i:i+batch_size]
                batch_actions = actions[i:i+batch_size]
                batch_advantages = advantages[i:i+batch_size]

                action_probs,values = self.policy(batch_states,batch_balances)
                
                old_action_probs = action_probs.gather(1,batch_actions.unsqueeze(1)).detach()
                ratio = action_probs.gather(1,batch_actions.unsqueeze(1)) / old_action_probs
                surr1 = ratio * batch_advantages
                surr2 = torch.clamp(ratio,1-self.epsilon,1+self.epsilon)*batch_advantages

                actor_loss = -torch.min(surr1,surr2).mean()
                critic_loss = nn.MSELoss()(values,rewards[i:i+batch_size] + self.gamma * next_values[i:i+batch_size] * (1-dones[i:i+batch_size]))

                loss = actor_loss + 0.5 * critic_loss

                self.optimizer.zero_grad()
                loss.backward()
                self.optimizer.step()
        # for _ in range(self.K_epochs):
        #     action_probs, values = self.policy(states,balances)
        #     _, next_values = self.policy(next_states)

        #     advantages = rewards + self.gamma * next_values *(1 - dones) - values
        #     old_action_probs = action_probs.gather(1, actions.unsqueeze(1)).detach()
        #     ratio = action_probs.gather(1, actions.unsqueeze(1)) / old_action_probs
        #     surr1 = ratio * advantages
        #     surr2 = torch.clamp(ratio, 1 - self.epsilon, 1 + self.epsilon) * advantages

        #     actor_loss = -torch.min(surr1,surr2).mean()
        #     critic_loss = nn.MSELoss()(values, rewards + self.gamma * next_values * (1-dones))

        #     loss = actor_loss + 0.5 * critic_loss

        #     self.optimizer.zero_grad()
        #     loss.backward()
        #     self.optimizer.step()
