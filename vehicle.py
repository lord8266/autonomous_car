

import carla 
import numpy as np
import route
import pygame
import game_loop

class VehicleController:

    def __init__(self,actor):
        self.actor = actor
        self.control = carla.VehicleControl()
        self.prev_control = carla.VehicleControl()
        self.speed = 1
        self.throttle_speed = 0.4

    def control_by_input(self):
        keys =pygame.key.get_pressed()

        self.control.throttle =  0
        self.control.brake = 0
        self.control.gear =1
        self.control.steer =0

        if keys[pygame.K_UP]:
            self.control.throttle+=self.speed
        if keys[pygame.K_DOWN]:
            self.control.throttle+=self.speed
            self.control.gear =-1
        if keys[pygame.K_SPACE]:
            self.control.brake = 1.0
        if keys[pygame.K_LEFT]:
            self.control.steer -= self.throttle_speed
        if keys[pygame.K_RIGHT]:
            self.control.steer += self.throttle_speed

        if keys[pygame.K_w]:
            self.throttle_speed+=0.1
        if keys[pygame.K_s]:
            self.throttle_speed-=0.1
        self.throttle_speed = max(0,min(self.throttle_speed,0.65))

        if self.cmp_control():
            self.actor.apply_control(self.control)
            self.equate_controls()

    def cmp_control(self):
        if self.control.throttle!=self.prev_control.throttle:
            return True
        if self.control.gear!=self.prev_control.gear:
            return True
        if self.control.steer!=self.prev_control.steer:
            return True
        if self.control.brake!=self.prev_control.brake:
            return True
        return False
    
    def equate_controls(self):
        self.prev_control.throttle = self.control.throttle
        self.prev_control.gear = self.control.gear
        self.prev_control.brake = self.control.brake
        self.prev_control.steer = self.control.steer
    
def init_vehicle(world,point):
    lib = world.get_blueprint_library()
    blueprint = lib.filter('vehicle.bmw.*')[0]
    rot = point.rotation
    # rot.yaw+=180
    point = carla.Transform(point.location,rot)
    vehicle = world.spawn_actor(blueprint,point)

    blueprint  = lib.find('sensor.camera.rgb')
    blueprint.set_attribute('image_size_x', '640')
    blueprint.set_attribute('image_size_y', '480')
    cam = world.spawn_actor(blueprint,carla.Transform(carla.Location(x=-7.5, z=5.8),carla.Rotation(pitch=-29)),attach_to=vehicle)

    return vehicle,cam


client = carla.Client('127.0.0.1',2000)
client.set_timeout(2.0)
world = client.get_world()
world_map = world.get_map()

all_points = world_map.get_spawn_points()
start,end = all_points[0],all_points[1]

vehicle,cam =  init_vehicle(world,start)
controller = VehicleController(vehicle)
route = route.Route(world,vehicle)
route.make_route(start,end,6)
route.draw_path()
g = game_loop.GameLoop(cam,controller,route)


g.run()

cam.stop()
vehicle.destroy()
pygame.quit()



