import carla 
import numpy as np
import navigation_system
import pygame
import game_manager
import vehicle_controller
import control_manager
import sensor_manager
import reward_system
import drawing_library
import math
from enum import Enum
import weakref
import  random
import lane_ai

class TrafficController:

    def __init__(self,simulator,vehicle_count):

        self.simulator = simulator
        self.prev = pygame.time.get_ticks()
        self.batch_running =False
        self.count = 0
        self.max =vehicle_count
    def add_vehicles(self):
        blueprints = self.simulator.world.get_blueprint_library().filter('vehicle.*')
        blueprints = [x for x in blueprints if int(x.get_attribute('number_of_wheels')) == 4]
        spawn_points = self.simulator.navigation_system.spawn_points

        SpawnActor = carla.command.SpawnActor
        SetAutopilot = carla.command.SetAutopilot
        FutureActor = carla.command.FutureActor
        batch = []
        actor_list =[]
        for n, transform in enumerate(spawn_points):
            if n >= 50:
                break
            blueprint = random.choice(blueprints)
            if blueprint.has_attribute('color'):
                color = random.choice(blueprint.get_attribute('color').recommended_values)
                blueprint.set_attribute('color', color)
            blueprint.set_attribute('role_name', 'autopilot')
            batch.append(SpawnActor(blueprint, transform).then(SetAutopilot(FutureActor, True)))

        for response in self.simulator.client.apply_batch_sync(batch):
            # print(response)
            actor_list.append(response.actor_id)
        self.get_actors(actor_list)

    def get_actors(self,actor_list):
        vehicles = self.simulator.world.get_actors(actor_list) 
        self.vehicles = vehicles
    
    def update_distances(self):

        
        p1 = self.simulator.vehicle_variables.vehicle_location
        for v in self.vehicles:
            p2 = v.get_location()
            d = navigation_system.NavigationSystem.get_distance(p1,p2,res=1)
            # print(v,self.vehicles[v])
            if d<35:
                self.simulator.lane_ai.add_obstacle(v)
            
        
    
    def update(self):

        curr =pygame.time.get_ticks()

        if (curr-self.prev)>500:
            self.batch_running =True
            self.update_distances()
            self.prev = curr
