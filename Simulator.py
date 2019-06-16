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
        # settings.no_rendering_mode = True
        # settings.synchronous_mode = True
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
        # self.world.tick()
        obs,a_transform,w_transform = self.route.get_dynamic_path()
        self.reward_system.update_data(a_transform,w_transform)
        done,reward = self.reward_system.update_rewards()
        return ([Simulator.get_scaled_distance(a_transform,w_transform)] + obs),reward,done

    @staticmethod
    def get_scaled_distance(t1,t2):
        p1 =t1.location
        p2 = t2.location
        return route.Route.get_distance(p1,p2,res=1)

    def reset(self):
        # print("reset")
        self.controller.reset(self.start)
        self.route.reset()
        self.reward_system.reset()
        
    def get_state(self):
        obs,a_transform,w_transform = self.route.get_dynamic_path()
        return [Simulator.get_scaled_distance(a_transform,w_transform)] + obs
    
    def init_system(self):
        self.reset()
        # self.world.tick()
    
    def render(self):
        self.game_loop.run() # temporary
    
    def stop(self):
        self.controller.actor.destroy()
        self.game_loop.camera.stop()

