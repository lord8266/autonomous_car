


import Simulator
import pygame
import numpy as np
from sklearn.preprocessing import StandardScaler

simulator = Simulator.Simulator()


running = simulator.running
observation = simulator.get_observation()
prev = pygame.time.get_ticks()
curr_reward =0 
clock = pygame.time.Clock()



def get_action():
    max_ = len(simulator.control_manager.controls)
    return np.random.randint(0,max_)


while running:
    clock.tick_busy_loop(60)
    
    action = get_action()

    
    curr = pygame.time.get_ticks()

    if (curr-prev)>60:
        observation,reward,status = simulator.step(action)
        curr_reward+=reward
        # print(observation)
        prev = curr
        if status==Simulator.Status.FAILED:
            simulator.reset()
        if status==Simulator.Status.COMPLETED:
            simulator.on_completion()
    
    simulator.render()
    running = simulator.running

simulator.stop()
pygame.quit()



