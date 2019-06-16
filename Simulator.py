import carla 
import numpy as np
import route
import pygame
import game_loop
import VehicleController
import RewardSystem

class Simulator:

    def __init__(self):
        self.intitalize_carla()

    def intitalize_carla(self):
        client = carla.Client('127.0.0.1',2000)
        client.set_timeout(2.0)
        world = client.get_world()

        settings = world.get_settings() # no render
        settings.no_rendering_mode = False
        world.apply_settings(settings)

        world_map = world.get_map()
        all_points = world_map.get_spawn_points()
        start,end = all_points[0],all_points[1]

        vehicle,cam =  VehicleController.init_vehicle(world,start)
        controller = VehicleController.VehicleController(vehicle)
        route = route.Route(world,vehicle)
        route.make_route(start,end,6)
        route.draw_path()
        g = game_loop.GameLoop(cam,controller,route)

        self.client = client
        self.world = world
        self.world_map =world_map
        self.start =start
        self.end =end
        self.route = route
        self.game_loop = g
        