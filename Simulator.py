import carla 
import numpy as np
import route
import pygame
import game_loop
import VehicleController
import RewardSystem

class Simulator:

    def __init__(self):
        pygame.init()
        self.intitalize_carla()

    def intitalize_carla(self):
        client = carla.Client('127.0.0.1',2000)
        client.set_timeout(2.0)
        world = client.get_world()

        settings = world.get_settings() # no render
        settings.no_rendering_mode = False
        settings.synchronous_mode = True
        world.apply_settings(settings)

        world_map = world.get_map()
        all_points = world_map.get_spawn_points()
        start,end = all_points[0],all_points[1]

        vehicle,cam =  VehicleController.init_vehicle(world,start)
        controller = VehicleController.VehicleController(vehicle,AI=True)
        route_ = route.Route(world,vehicle)
        route_.make_route(start,end,6)
        route_.draw_path()
        g = game_loop.GameLoop(cam,controller,route_)

        self.client = client
        self.world = world
        self.world_map =world_map
        self.start =start
        self.end =end
        self.route = route_
        self.game_loop = g
        self.reward_system = RewardSystem.RewardSystem(end)
        self.controller = controller

    def step(self,action): # action is a steer angle from -0.5 to 0.5 (steer)
        self.controller.control_by_AI(action)
        self.client.tick()
        data = self.route.get_dynamic_path()
        self.reward_system.update_data(data[1],data[2])
        done,reward = self.reward_system.update_rewards()
        return data[0],reward,done
    
    def reset(self):
        self.controller.reset(self.start)
        self.reward_system.reset()
    
    def init_system(self):
        self.reset()
        self.client.tick()
    
    def render(self):
        self.game_loop.run() # temporary

