

import carla 
import numpy as np
import route
import pygame
import game_loop
import VehicleController
import Simulator
import gen



simulator = Simulator.Simulator()
simulator.init_system()
states = gen.generator()

running = simulator.game_loop.running
state = simulator.get_state()
prev = pygame.time.get_ticks()
curr_reward =0 
clock = pygame.time.Clock()



def get_action():
    # t1 = simulator.route.actor_transform.rotation.yaw
    # t2 = simulator.route.wapoint_transform.rotation.yaw
    # if (t1-t2)>0.1:
    #     return -0.1
    # elif (t1-t2)<0.1:
    #     return 0.1 
    # else:
    #     return 0
    return states[np.random.randint(0,len(states))]


while running:
    clock.tick_busy_loop(60)
    
    action = get_action()

    state,reward,done = simulator.step(action)
    prev_state = state
    curr_reward+=reward
    curr = pygame.time.get_ticks()

    if (curr-prev)>310:
        print(state)
        prev = curr
    if done:
        simulator.reset()
        # print(curr_reward)
    simulator.render()
    running = simulator.game_loop.running

simulator.stop()
pygame.quit()



