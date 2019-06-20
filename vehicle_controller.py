
import carla 
import numpy as np
import pygame

class VehicleController:

    def __init__(self,simulator,AI=False):
        self.simulator = simulator
        self.control = carla.VehicleControl()
        self.prev_control = carla.VehicleControl()
        self.max_throttle = 0.8
        self.max_steer = 0.7
        VehicleController.set_control(self.control,throttle=0.5)
        self.intialize_vehicle()

    def intialize_vehicle(self):
        vehicle_blueprint = self.simulator.blueprint_library.filter('vehicle.tesla.*')[0]
        self.vehicle = self.simulator.world.spawn_actor(vehicle_blueprint,self.simulator.navigation_system.start)

    def control_by_input(self):
        VehicleController.set_control(self.control)

        keys =self.simulator.game_manager.keys
        if keys[pygame.K_UP]:
            self.control.throttle+=self.max_throttle
        if keys[pygame.K_DOWN]:
            self.control.reverse = True
            self.control.throttle+=self.max_throttle
        if keys[pygame.K_SPACE]:
            self.control.brake = 1.0
        if keys[pygame.K_LEFT]:
            self.control.steer -= self.max_steer*0.91
        if keys[pygame.K_RIGHT]:
            self.control.steer += self.max_steer*0.91

        if self.cmp_control():
            self.vehicle.apply_control(self.control)
            self.equate_controls()

    def control_by_AI(self,control): 
        
        self.control =control # temporary
        if self.cmp_control():
                self.vehicle.apply_control(self.control)
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
        if self.control.reverse!=self.prev_control.reverse:
            return True
        return False
    
    def equate_controls(self):
        self.prev_control.throttle = self.control.throttle
        self.prev_control.gear = self.control.gear
        self.prev_control.brake = self.control.brake
        self.prev_control.steer = self.control.steer
        self.prev_control.reverse = self.control.reverse
    
    def reset(self):
        pos = self.simulator.navigation_system.start
        VehicleController.set_control(self.control)
        
        # vel = self.vehicle.get_velocity()
        # vel.x=0
        # vel.y=0
        id_ =self.vehicle.id
        # self.vehicle.set_velocity(vel)
        # self.vehicle.set_angular_velocity(carla.Vector3D())
        # self.vehicle.set_transform(pos)
        self.simulator.client.apply_batch([carla.command.ApplyVelocity(id_, carla.Vector3D()),
        carla.command.ApplyTransform(id_,pos),
        carla.command.ApplyAngularVelocity(id_, carla.Vector3D()) ])


    
    @staticmethod
    def set_control(control,throttle=0,brake=0,gear=1,steer=0,reverse=False):
        control.throttle =  throttle
        control.brake = brake
        control.gear =gear
        control.steer =steer
        control.reverse = reverse
    




# class LaneInvasionSensor():
#     def __init__(self, sensor):
     
#         self.sensor =sensor
#         # We need to pass the lambda a weak reference to self to avoid circular
#         # reference.
#         # weak_self = weakref.ref(self)
#         self.sensor.listen(lambda event: LaneInvasionSensor._on_invasion( event))

#     @staticmethod
#     def _on_invasion( event):
        
#         # lane_types = set(x.type for x in event.crossed_lane_markings)
#         # text = ['%r' % str(x).split()[-1] for x in lane_types]
#         # self.hud.notification('Crossed line %s' % ' and '.join(text))
#         RewardSystem.RewardSystem.lane_invade()