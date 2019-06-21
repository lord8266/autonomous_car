


import Simulator
import pygame
import numpy as np
from sklearn.preprocessing import StandardScaler
import ai_model
import numpy as np
# import gym

# from keras.models import Sequential
# from keras.layers import Dense, Activation, Flatten
# from keras.optimizers import Adam
from keras.optimizers import sgd
# from rl.agents.dqn import DQNAgent
# from rl.policy import EpsGreedyQPolicy
# from rl.memory import SequentialMemory




# running = simulator.running
# observation = simulator.get_observation()
# prev = pygame.time.get_ticks()
# curr_reward =0 
# clock = pygame.time.Clock()

# model = Sequential()
# model.add(Flatten(input_shape=(1,5)))
# model.add(Dense(18))
# model.add(Activation('relu'))
# model.add(Dense(12))
# model.add(Activation('relu'))
# model.add(Dense(10))
# model.add(Activation('linear'))

# policy = EpsGreedyQPolicy()
# memory = SequentialMemory(limit=50000, window_length=1)
# dqn = DQNAgent(model=model, nb_actions=10, memory=memory, nb_steps_warmup=10,
# target_model_update=1e-2, policy=policy)
# dqn.compile(Adam(lr=1e-3), metrics=['mae'])

# dqn.fit(simulator, nb_steps=5000, visualize=False, verbose=2)

# def get_action():
#     max_ = len(simulator.control_manager.controls)
#     return np.random.randint(0,max_)


# while running:
    
#     action = get_action()

    
#     curr = pygame.time.get_ticks()

#     if (curr-prev)>1000/40:
#         observation,reward,done,_ = simulator.step(action)
#         curr_reward+=reward
#         print(observation,simulator.navigation_system.curr_pos, end='\n\n')
#         prev = curr
#         if done:
#             simulator.reset()
#             continue

#     # simulator.render()
#     running = simulator.running

simulator = Simulator.Simulator('172.16.175.136')
model = ai_model.Model(simulator)
model.train_model()

simulator.stop()
pygame.quit()



