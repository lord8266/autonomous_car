import numpy as np
from collections import deque
from keras import Sequential
from keras.layers import Dense
from keras.optimizers import sgd,Adam
import os
import random
import reward_system
HIDDEN1_UNITS = 50
HIDDEN2_UNITS = 40

class Model:

    def __init__(self,simulator,state_size=3,action_size=6,save_file='save/model'):

        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=32*30)
        self.gamma = 0.95    # discount rate
        self.learning_rate=0.002
        self.running = True
        self.epsilon = 0.05  # exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.simulator =simulator
        self.model = self.build_model()
        self.reward_tracker = reward_system.RewardTracker(self,200,70000)
        self.start =0
        self.load()
        self.save_file = save_file
        self.simulator.ai_model = self
        

    def build_model(self):

        model = Sequential()
        model.add(Dense(HIDDEN1_UNITS, input_dim=self.state_size, activation='tanh'))
        model.add(Dense(HIDDEN2_UNITS, input_dim=self.state_size, activation='tanh'))
        model.add(Dense(self.action_size, activation='softmax'))
        model.compile(loss = 'mse',optimizer = Adam(lr = self.learning_rate))
        # self.load('./save/Carla-dqn.h5')
        print("built")
        return model


    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state):
        # if random.random() <= self.epsilon:  #discuss
        #     return random.randrange(self.action_size) 
        # act_values = self.model.predict(state)
        # return np.argmax(act_values[0])  # returns index value of o/p action
        key_state,action = self.simulator.vehicle_controller.check_key_state()
        self.simulator.key_control =key_state
        if key_state:
            # print("Imitate Activated")
            return action
        act_values = self.model.predict(state)
        return np.argmax(act_values[0])  # returns index value of o/p action

    def predict(self,state):
        state = np.reshape(state, [1, self.state_size])
        act_values = self.model.predict(state)
        return np.argmax(act_values[0])
        
    def replay(self, batch_size):

        minibatch = random.sample(self.memory, batch_size)
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                target = (reward + self.gamma *
                          np.amax(self.model.predict(next_state)[0]))
            target_f = self.model.predict(state)
            target_f[0][action] = target
            self.model.fit(state, target_f, epochs=1, verbose=0)
        # if self.epsilon > self.epsilon_min:
        #     self.epsilon *= self.epsilon_decay


    def load(self):
        last_model,episode,epsilon =self.reward_tracker.get_previous()
        if last_model:
            self.model.load_weights(os.path.join('save','models',last_model))
            print("Loaded",last_model)
            self.epsilon = epsilon
            self.start = episode
            print("Last completed episode : ",self.start)

    def save(self, name):
        self.model.save_weights(os.path.join('save','models',name))


    def train_model(self):

        done = False
        batch_size = 32
        EPISODES = 70000
        prev_rewards =0
        for e in range(self.start,EPISODES):
            state = self.simulator.reset() #change to initial state
            state = np.reshape(state, [1, self.state_size])
            self.total_rewards = 0
            
            for time in range(100):
                if not time%50:
                    print(f"Step {time}, Rewards: {self.total_rewards}")
                # env.render()
                action = self.act(state) # self.act(state)
                # next_state, reward, done, _ = env.step(action)
                next_state,reward,done,_ = self.simulator.step(action) #check
                self.total_rewards += reward

                # reward = reward if not done else -10 #check
                next_state = np.reshape(next_state, [1, self.state_size])
                # self.remember(state, action, reward, next_state, done)
                state = next_state
                if done:
                    break
                # if len(self.memory) > batch_size:
                #     self.replay(batch_size)
                if self.simulator.running==False:
                    self.running =False
                    break
                
            self.reward_tracker.end_episode(self.total_rewards)
            print(f"Complete Episode {e} , Epsilon: {self.epsilon}, Total Rewards: {self.total_rewards},Position: {self.simulator.navigation_system.curr_pos} / {len(self.simulator.navigation_system.ideal_route)} ")
            
            if self.running==False:
                break
            if e%30==0:
                if self.epsilon > self.epsilon_min:
                    self.epsilon *= self.epsilon_decay
            prev_rewards =self.total_rewards
    
