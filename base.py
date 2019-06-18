


import Simulator
import pygame
import numpy as np

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

    observation,reward,done = simulator.step(action)
    curr_reward+=reward
    curr = pygame.time.get_ticks()

    if (curr-prev)>310:
        print(observation)
        prev = curr
    if done:
        simulator.reset()
    
    simulator.render()
    running = simulator.running

simulator.stop()
pygame.quit()



