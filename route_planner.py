# pylint: disable=no-member
# pylint: disable=import-error

import carla 
from agents.navigation import global_route_planner,global_route_planner_dao
from agents.tools import misc
import math

def draw_points(data,debug):
    cnt = 0
    for i in data:
        if not cnt%10:
            debug.draw_string(i.location,f'{cnt}')
        cnt+=1

def draw_route(data,debug,z=0.5):
    cnt = 0
    for i in data:
        t = i.transform
        begin = t.location + carla.Location(z=z)
        angle = math.radians(t.rotation.yaw)
        end = begin + carla.Location(x=math.cos(angle), y=math.sin(angle))
        debug.draw_arrow(begin, end, arrow_size=0.3,life_time=3600) 
    debug.draw_string(data[0].transform.location,f'Start')
    debug.draw_string(data[-1].transform.location,f'End')

client = carla.Client('127.0.0.1',2000)
client.set_timeout(2.0)

town = client.get_world()
town_map = town.get_map()

hop_resolution = 2 #meters

lib = town.get_blueprint_library()

points = town_map.get_spawn_points()
# draw_points(points,town.debug)

dao = global_route_planner_dao.GlobalRoutePlannerDAO(town_map,hop_resolution)
grp = global_route_planner.GlobalRoutePlanner(dao)
grp.setup()

route = grp.trace_route(points[0].location, points[10].location)
draw_route([i[0] for i in route],town.debug )

# route planner doesnt care about distance