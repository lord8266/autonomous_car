

import carla 
import numpy as np
import route
import pygame
import game_loop
import VehicleController

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


g.run()

cam.stop()
vehicle.destroy()
pygame.quit()



