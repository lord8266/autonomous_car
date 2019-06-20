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
from enum import Enum
import weakref
class Type(Enum):
    Automatic =1
    Manual =2

class Status(Enum):
    COMPLETED=1,
    FAILED=2,
    RUNNING=3

class CameraType(Enum):
    RGB=1,
    Semantic=2, # start_point, end_point = np.random.randint(0,len(self.navigation_system.spawn_points),size=2) #temporary
        # self.navigation_system.make_ideal_route(start_point,end_point)
class VehicleVariables:

    def __init__(self,simulator):
        self.simulator = simulator
        self.prev = pygame.time.get_ticks()-100
        self.update()

    def update(self):
        # curr =pygame.time.get_ticks()
        self.vehicle_transform = self.simulator.vehicle_controller.vehicle.get_transform()
        self.vehicle_location = self.vehicle_transform.location
        self.vehicle_yaw = self.vehicle_transform.rotation.yaw%360

        self.closest_waypoint = self.simulator.map.get_waypoint(self.vehicle_location)
        self.closest_waypoint_transform= self.closest_waypoint.transform
        self.closest_waypoint_location = self.closest_waypoint_transform.location
        self.closest_waypoint_yaw = self.closest_waypoint_transform.rotation.yaw%360
        # self.prev =curr
    
    def get_distance(self):
        return navigation_system.NavigationSystem.get_distance(self.closest_waypoint_location,self.vehicle_location,res=1)

    

class Simulator:

    def __init__(self):
        pygame.init()
        self.intitalize_carla()
        self.initialize_navigation()
        self.initialize_vehicle()
        self.initialize_game_manager()
        self.initialize_sensor_manager()
        self.initialize_control_manager()
        self.initialize_variables()
        self.initialize_reward_system()
        self.type = Type.Automatic
        self.running = True
        #need to change from here
        self.navigation_system.make_local_route()
        drawing_library.draw_arrows(self.world.debug,[i.location for i in self.navigation_system.ideal_route])
        drawing_library.print_locations(self.world.debug,[i.location for i in self.navigation_system.ideal_route])
        
    def intitalize_carla(self):
        self.client = carla.Client('127.0.0.1',2000)
        self.client.set_timeout(2.0)
        self.world = self.client.get_world()
        self.map = self.world.get_map()
        self.blueprint_library = self.world.get_blueprint_library()


        # self.collision_sensor = CollisionSensor(vehicle)       
        # # self.lane_invasion_sensor = LaneInvasionSensor(vehicle)
        
    def initialize_navigation(self):
        self.navigation_system = navigation_system.NavigationSystem(self)
        self.navigation_system.make_map_data(res=4)
        start_point, end_point = np.random.randint(0,len(self.navigation_system.spawn_points),size=2)
        self.navigation_system.make_ideal_route(8,10)
         # temporary
    


    def initialize_vehicle(self):
        self.vehicle_controller = vehicle_controller.VehicleController(self,AI=True)

    def initialize_sensor_manager(self):
       self.sensor_manager = sensor_manager.SensorManager(self)
       self.sensor_manager.initialize_rgb_camera()
       self.sensor_manager.initialize_semantic_camera()
       self.sensor_manager.initialize_collision_sensor()
       self.sensor_manager.initialize_lane_invasion_sensor()
       self.camera_type = CameraType.RGB
       self.sensor_manager.camera.listen(lambda image: self.game_manager.camera_callback(image))
       
    def initialize_game_manager(self):
        self.game_manager = game_manager.GameManager(self)

    def initialize_control_manager(self):
        self.control_manager = control_manager.ControlManager(self)
    
    def initialize_reward_system(self):
        self.reward_system = reward_system.RewardSystem(self)

    def initialize_variables(self):
        self.vehicle_variables = VehicleVariables(self)
    
    def step(self,action):
        self.vehicle_variables.update()
        
        self.game_manager.update()
        if self.type==Type.Automatic:
            self.vehicle_controller.control_by_AI(self.control_manager.get_control(action))
        else:
            self.vehicle_controller.control_by_input()

        self.navigation_system.make_local_route()
        self.observation =self.get_observation()
        reward,status = self.reward_system.update_rewards()
        return self.observation,reward,status

    def get_observation(self):
        rot_offsets = self.navigation_system.get_rot_offset() # temporary
        vehicle_loc =self.vehicle_variables.vehicle_location
        closest_waypoint = self.navigation_system.local_route[1].location
        distance_to_closest_waypoint = navigation_system.NavigationSystem.get_distance(vehicle_loc,closest_waypoint,res=1)
        self.traffic_light_state = self.sensor_manager.traffic_light_sensor()
        return [self.traffic_light_state,distance_to_closest_waypoint] + rot_offsets

    def reset(self):
        self.navigation_system.reset()
        # start_point, end_point = np.random.randint(0,len(self.navigation_system.spawn_points),size=2) #temporary
        # self.navigation_system.make_ideal_route(start_point,end_point)
        self.reward_system.reset()
        self.vehicle_controller.reset()
    
    def on_completion(self):
        start_point, end_point = 8,10 #np.random.randint(0,len(self.navigation_system.spawn_points),size=2) #temporary
        self.navigation_system.make_ideal_route(start_point,end_point)
        self.reward_system.reset()
        self.vehicle_controller.reset()
       
    def init_system(self):
        self.reset()
      
    
    def render(self):
        self.game_manager.render()
    
    def stop(self):
        self.vehicle_controller.vehicle.destroy()
        self.sensor_manager.stop_camera()
    
    def switch_input(self):
        
        if self.type==Type.Manual:
            self.type = Type.Automatic
        else:
            self.type = Type.Manual

    def camera_switch(self): #temporary
        if (self.camera_type==CameraType.RGB):
            self.camera_type = CameraType.Semantic
            self.sensor_manager.semantic_camera.listen(lambda image: self.game_manager.semantic_callback(image))
            self.sensor_manager.camera.stop()

        else:
            self.sensor_manager.camera.listen(lambda image: self.game_manager.camera_callback(image))
            self.sensor_manager.semantic_camera.stop()
            self.camera_type = CameraType.RGB

def collision_with(event):
    
    print("collision")



# class CollisionSensor():
#     def __init__(self, parent_actor):
#         self.sensor = None
#         self._parent = parent_actor
#         world = self._parent.get_world()
#         bp = world.get_blueprint_library().find('sensor.other.collision')
#         self.sensor = world.spawn_actor(bp, carla.Transform(), attach_to=self._parent)
#        .
#         weak_self = weakref.ref(self)
#         self.sensor.listen(lambda event: CollisionSensor._on_collision(weak_self, event))

    

#     @staticmethod
#     def _on_collision(weak_self, event):
#         print("collision")
#         RewardSystem.RewardSystem.collision_with()
   



# class LaneInvasionSensor(object):
#     def __init__(self, parent_actor):
#         self.sensor = None
#         self._parent = parent_actor
#         world = self._parent.get_world()
#         bp = world.get_blueprint_library().find('sensor.other.lane_invasion')
#         self.sensor = world.spawn_actor(bp, carla.Transform(), attach_to=self._parent)
#         weak_self = weakref.ref(self)
#         self.sensor.listen(lambda event: LaneInvasionSensor._on_invasion(weak_self, event))

#     @staticmethod
#     def _on_invasion(weak_self, event):
#         print("lane invation")
#         RewardSystem.RewardSystem.lane_invade()
       
