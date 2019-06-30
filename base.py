


import Simulator
import pygame
import numpy as np
from sklearn.preprocessing import StandardScaler
import ai_model
# import gym

# from keras.models import Sequential
# from keras.layers import Dense, Activation, Flatten
# from keras.optimizers import Adam
from keras.optimizers import sgd
# from rl.agents.dqn import DQNAgent
# from rl.policy import EpsGreedyQPolicy
# from rl.memory import SequentialMemory






# model = Sequential()
# model.add(Flatten(input_shape=(1,5)))
# model.add(Dense(18))
# model.add(Activation('relu'))
# model.add(Dense(12))
# model.add(Activation('relu'))
# model.add(Dense(10))
# model.add(Activation('linear'))
# 127.0.0.1
# 127.0.0.1
# 127.0.0.1ow_length=1)
# dqn = DQNAgent(model=model, nb_actions=10, memory=memory, nb_steps_warmup=10,
# target_model_update=1e-2, policy=policy)
# dqn.compile(Adam(lr=1e-3), metrics=['mae'])

# dqn.fit(simulator, nb_steps=5000, visualize=False, verbose=2)

def get_action():
    max_ = len(simulator.control_manager.controls)
    return np.random.randint(0,max_)

simulator = Simulator.Simulator()

# running = simulator.running
# observation = simulator.get_observation()
# prev = pygame.time.get_ticks()
# curr_reward =0 
# clock = pygame.time.Clock()


# while running:
#     action = get_action()

    
#     curr = pygame.time.get_ticks()
#     observation,reward,done,_ = simulator.step(action)
#     curr_reward+=reward
#     if (curr-prev)>1000/200:
#         # print("Reward: ",simulator.reward_system.curr_reward)
#         # print(observation, end='\n\n')
#         # print(simulator.vehicle_controller.control)
#         # print(simulator.vehicle_variables.vehicle_location,simulator.navigation_system.start.location)
#         prev =curr
#     # print(1000/(curr-prev))
#     # prev = curr
#     if done:
#         simulator.reset()
#         continue

#     # simulator.render()
#     running = simulator.running

model = ai_model.Model(simulator,4,len(simulator.control_manager.controls))
model.train_model()

simulator.stop()
pygame.quit()



