import numpy as np
from collections import deque
from keras import Sequential
from keras.layers import Dense
from keras.optimizers import sgd
import random
HIDDEN1_UNITS = 18
HIDDEN2_UNITS = 15

class Model:

    def __init__(self,simulator,state_size=5,action_size=10):

        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=2000)
        self.gamma = 0.95    # discount rate
        self.learning_rate=0.001
        self.running = True
        self.epsilon = 0.7  # exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.simulator =simulator
        self.model = self.build_model()

    def build_model(self):

        model = Sequential()
        model.add(Dense(HIDDEN1_UNITS, input_dim=self.state_size, activation='tanh'))
        model.add(Dense(HIDDEN2_UNITS, activation='tanh'))
        model.add(Dense(self.action_size, activation='softmax'))
        model.compile(loss = 'mse',optimizer = sgd(lr = self.learning_rate))
        self.load('./save/Carla-dqn.h5')
        return model


    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state):
        if random.random() <= self.epsilon:  #discuss
            return random.randrange(self.action_size) 
        act_values = self.model.predict(state)
        return np.argmax(act_values[0])  # returns index value of o/p action

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


    def load(self, name):
        self.model.load_weights(name)

    def save(self, name):
        self.model.save_weights(name)


    def train_model(self):

        done = False
        batch_size = 32
        EPISODES = 1000
        for e in range(EPISODES):
            state = self.simulator.on_completion() #change to initial state
            state = np.reshape(state, [1, self.state_size])
            total_rewards = 0
            for time in range(750):
                if not time%75:
                    print(f"Step {time}, Rewards: {total_rewards}")
                # env.render()
                action = self.act(state) # self.act(state)
                # next_state, reward, done, _ = env.step(action)
                next_state,reward,done,_ = self.simulator.step(action) #check
                total_rewards += reward
                # reward = reward if not done else -10 #check
                next_state = np.reshape(next_state, [1, self.state_size])
                self.remember(state, action, reward, next_state, done)
                state = next_state
                if done:
                    print("episode: {}/{}, score: {}, e: {:.2}"
                        .format(e, EPISODES, time, self.epsilon))
                    break
                if len(self.memory) > batch_size:
                    self.replay(batch_size)
                if self.simulator.running==False:
                    self.running =False
                    break
            print(f"Complete Episode {e} , Epsilon: {self.epsilon}, Total Rewards: {total_rewards}")
            if self.running==False:
                break
            if self.epsilon > self.epsilon_min:
                self.epsilon *= self.epsilon_decay  
            if e % 10 == 0:
                print("saving")
                self.save('./save/Carla-dqn.h5')