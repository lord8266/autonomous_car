

import carla 
import numpy as np
import route
import pygame
import game_loop
import VehicleController
import Simulator
# client = carla.Client('127.0.0.1',2000)
# client.set_timeout(2.0)
# world = client.get_world()

# settings = world.get_settings() # no render
# settings.no_rendering_mode = False
# world.apply_settings(settings)

# world_map = world.get_map()
# all_points = world_map.get_spawn_points()
# start,end = all_points[0],all_points[1]

# vehicle,cam =  VehicleController.init_vehicle(world,start)
# controller = VehicleController.VehicleController(vehicle)
# route = route.Route(world,vehicle)
# route.make_route(start,end,6)
# route.draw_path()
# g = game_loop.GameLoop(cam,controller,route)

simulator = Simulator.Simulator()
simulator.init_system()
# g.run()

running = simulator.game_loop.running
prev_state = None
prev = pygame.time.get_ticks()
curr_reward =0 
clock = pygame.time.Clock()
while running:
    clock.tick_busy_loop(60)

    
    state,reward,done = simulator.step(0)
    prev_state = state
    curr_reward+=reward
    curr = pygame.time.get_ticks()

    if done:
        simulator.reset()
        print(curr_reward)
        curr_reward = 0
    simulator.render()
    running = simulator.game_loop.running

simulator.stop()
pygame.quit()



