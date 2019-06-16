# pylint: disable=no-member
# pylint: disable=import-error
# pylint: disable=no-name-in-module
import carla
from carla import DebugHelper
import pygame
pygame.init()
client = carla.Client('127.0.0.1',2000)
client.set_timeout(2.0)

world = client.get_world()
lib = world.get_blueprint_library()

vehicle = lib.filter('vehicle.bmw.*')[0]

town =world.get_map()

curr= town.get_waypoint(carla.Location())

# point = town.get_spawn_points()[0]
# actor = world.spawn_actor(vehicle,point)
all =[]
cnt =0
while curr!=None and curr not in all:
    curr = curr.next(10.0)
    for i,w_point in enumerate(curr):
        world.debug.draw_string(w_point.transform.location, f'{i} {cnt}', draw_shadow=False,
                                            color=carla.Color(r=255, g=0, b=0), life_time=120.0,
                                            persistent_lines=True)
    print([i.road_id for i in curr])
    curr = curr[0]
    cnt+=1
    
    pygame.time.wait(1764)