import carla 
import numpy as np
import route
import pygame
import game_loop
import VehicleController
import RewardSystem
from enum import Enum
class Type(Enum):
    Automatic =1
    Manual =2

class Simulator:

    def __init__(self):
        pygame.init()
        self.intitalize_carla()
        self.type = Type.Automatic

    def intitalize_carla(self):
        client = carla.Client('127.0.0.1',2000)
        client.set_timeout(2.0)
        # client.load_world('Town03')

        world = client.get_world()
        
        settings = world.get_settings() # no render
        # settings.no_rendering_mode = True
        # settings.synchronous_mode = True
        world.apply_settings(settings)

        world_map = world.get_map()
        
        all_points = world_map.get_spawn_points()
        start_point = np.random.randint(0,len(all_points))
        end_point = np.random.randint(0,len(all_points))
        start,end = all_points[start_point],all_points[end_point]

        vehicle,cam =  VehicleController.init_vehicle(world,start) # need to refactor
        controller = VehicleController.VehicleController(vehicle,AI=True)
        route_ = route.Route(world,vehicle)
        route_.make_route(start,end,4)
       
        g = game_loop.GameLoop(self,cam,controller,route_)

        self.client = client
        self.world = world
        self.world_map =world_map
        self.start =start
        self.end =end
        self.route = route_
        self.game_loop = g
        self.reward_system = RewardSystem.RewardSystem(end,self)
        self.controller = controller
        print("setting listener")
        lib = world.get_blueprint_library()
        blueprint = lib.find('sensor.other.collision')
        collision_sensor  = world.spawn_actor(blueprint,carla.Transform(),attach_to=vehicle)
    
        collision_sensor.listen(lambda event: collision_with(event)) # listen callback to sensor
        route_.draw_path()

    def step(self,action): # action is a steer angle from -0.5 to 0.5 (steer)
        if self.type==Type.Automatic:
            self.controller.control_by_AI(action)
        else:
            self.controller.control_by_input()
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
    
    def switch_input(self):
        
        if self.type==Type.Manual:
            self.type = Type.Automatic
        else:
            self.type = Type.Manual


def collision_with(event):
    # RewardSystem.ref.done = True
    print("collision")