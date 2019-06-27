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
class Type(Enum):
    Automatic =1
    Manual =2

class Status(Enum):
    COMPLETED=1,
    FAILED=2,
    RUNNING=3,
    RESTART=4,

class CameraType(Enum):
    RGB=1,
    Semantic=2, # start_point, end_point = np.random.randint(0,len(self.navigation_system.spawn_points),size=2) #temporary
        # self.navigation_system.make_ideal_route(start_point,end_point)
class VehicleVariables:

    def __init__(self,simulator):
        self.simulator = simulator
        self.wait_for_lag = False
        self.future_transform = None
        self.update()

    def update(self):
        self.vehicle_transform = self.simulator.vehicle_controller.vehicle.get_transform()
        if self.wait_for_lag==True:
            f = self.cmp_transform(self.vehicle_transform.location,self.future_transform.location)
            if f:
                self.wait_for_lag= False
            else:
                self.vehicle_transform = self.future_transform

        self.vehicle_location = self.vehicle_transform.location
        self.vehicle_yaw = self.vehicle_transform.rotation.yaw%360

    def update_npc(self):
        pass
    def add_npc(self,actor_list):
        self.actor_list = self.simulator.world.get_actors(actor_list)
    
    def cmp_transform(self,p1,p2):
        print(p1,p2)
        if abs(p1.x-p2.x)<4:
            if abs(p1.y-p2.y)<4:
                return True
        return False
    
        # self.prev =curr
    def start_wait(self,transform):
        self.wait_for_lag =True
        self.future_transform = transform


def transform_observation(obs):
    obs_ =obs[1:3]
    obs_[0] = obs_[0]/10
    obs_[1] = obs_[1]/180 +0.5
    return obs_


class Simulator:

    def __init__(self,carla_server='127.0.0.1',port=2000):
        pygame.init()
        self.intitalize_carla(carla_server,port)
        self.initialize_navigation()
        self.initialize_vehicle()
        self.initialize_game_manager()
        self.initialize_sensor_manager()
        self.initialize_control_manager()
        self.initialize_reward_system()
        self.initialize_variables()
        self.type = Type.Automatic
        self.running = True
        self.rendering =True
        self.respawn_pos_times = 0
        self.key_control = False
        #need to change from here
        self.navigation_system.make_local_route()
        # drawing_library.draw_arrows(self.world.debug,[i.location for i in self.navigation_system.ideal_route])
        # drawing_library.print_locations(self.world.debug,[i.location for i in self.navigation_system.ideal_route])
        # self.add_npc()
        self.world.tick()
        self.world.wait_for_tick()
        
    
    def temp(self):
        self.vehicle_controller.vehicle.set_transform(self.navigation_system.start)

    def intitalize_carla(self,carla_server,port):
        self.client = carla.Client(carla_server,port)
        self.client.set_timeout(2.0)
        # self.world = self.client.get_world()
        self.world = self.client.load_world('Town03')
        settings = self.world.get_settings()
        settings.synchronous_mode = False
        # settings.no_rendering_mode = True
        self.world.apply_settings(settings)
        self.map = self.world.get_map()
        self.blueprint_library = self.world.get_blueprint_library()

    def add_npc(self):
        blueprints = self.world.get_blueprint_library().filter('vehicle.*')
        blueprints = [x for x in blueprints if int(x.get_attribute('number_of_wheels')) == 4]
        spawn_points = self.navigation_system.spawn_points

        SpawnActor = carla.command.SpawnActor
        SetAutopilot = carla.command.SetAutopilot
        FutureActor = carla.command.FutureActor
        batch = []
        actor_list =[]
        for n, transform in enumerate(spawn_points):
            if n >= 5:
                break
            blueprint = random.choice(blueprints)
            if blueprint.has_attribute('color'):
                color = random.choice(blueprint.get_attribute('color').recommended_values)
                blueprint.set_attribute('color', color)
            blueprint.set_attribute('role_name', 'autopilot')
            batch.append(SpawnActor(blueprint, transform).then(SetAutopilot(FutureActor, True)))

        for response in self.client.apply_batch_sync(batch):
            print(response)
            actor_list.append(response)

        self.vehicle_variables.add_npc(actor_list)
        
    def initialize_navigation(self):
        self.navigation_system = navigation_system.NavigationSystem(self)
        self.navigation_system.make_map_data(res=4)
        self.start_point, self.end_point = np.random.randint(0,len(self.navigation_system.spawn_points),size=2)
        self.navigation_system.make_ideal_route(self.start_point,self.end_point)
        self.base_start =self.navigation_system.ideal_route[0]
        self.base_end = self.navigation_system.ideal_route[-1]
         # temporary
    
    def new_path(self):
        self.navigation_system.make_map_data(res=4)
        self.start_point = self.end_point
        while(True):
            self.end_point = np.random.randint(0,len(self.navigation_system.spawn_points))
            if self.end_point!=self.start_point:
                if abs(self.start_point-self.end_point)>5:
                    break
            
        self.navigation_system.make_ideal_route(self.start_point,self.end_point)
        self.base_start =self.navigation_system.ideal_route[0]
        self.base_end = self.navigation_system.ideal_route[-1]
        self.navigation_system.make_local_route()

    def initialize_vehicle(self):
        self.vehicle_controller = vehicle_controller.VehicleController(self,AI=True)

    def initialize_sensor_manager(self):
       self.sensor_manager = sensor_manager.SensorManager(self)
       self.sensor_manager.initialize_rgb_camera()
       self.camera_type = CameraType.RGB
       self.sensor_manager.camera.listen(lambda image: self.game_manager.camera_callback(image))
    #    self.sensor_manager.initialize_semantic_camera()
    #    self.sensor_manager.initialize_collision_sensor()
    #    self.sensor_manager.initialize_lane_invasion_sensor()
       
       
    def initialize_game_manager(self):
        self.game_manager = game_manager.GameManager(self)
        self.game_manager.update()

    def initialize_control_manager(self):
        self.control_manager = control_manager.ControlManager(self)
    
    def initialize_reward_system(self):
        self.reward_system = reward_system.RewardSystem(self)

    def initialize_variables(self):
        self.vehicle_variables = VehicleVariables(self)
        self.vehicle_variables.start_wait(self.navigation_system.start)
    
    def step(self,action):
        self.world.tick()
        ts = self.world.wait_for_tick()
        self.vehicle_variables.update()
        self.game_manager.update()
        while False:# self.traffic_light_state == 0: #or 
            self.game_manager.update()
            self.vehicle_controller.stop()
            self.observation =self.get_observation()
            self.render()
        if self.type==Type.Automatic:
            self.vehicle_controller.control_by_AI(self.control_manager.get_control(action))
        else:
            self.vehicle_controller.control_by_input()
    
        self.navigation_system.make_local_route()
        self.observation =self.get_observation()
        reward,status = self.reward_system.update_rewards()
        self.render()
        # print(self.observation)
        # print(status)
        return self.observation,reward,status!=Status.RUNNING,{}

    def car_ahead(self):
        pass
    def switch_render(self):
        if self.rendering==True:
            self.sensor_manager.camera.stop()
            self.sensor_manager.semantic_camera.stop()
            self.rendering =False
        else:
            self.sensor_manager.camera.listen(lambda image: self.game_manager.camera_callback(image))
            self.sensor_manager.semantic_camera.listen(lambda image: self.game_manager.semantic_callback(image))
            self.rendering =True

    def get_observation(self):
        rot_offsets = self.navigation_system.get_rot_offset() # temporary
        vehicle_loc =self.vehicle_variables.vehicle_location
        closest_waypoint = self.navigation_system.local_route[1].location
        distance_to_destination_sin, distance_to_destination_cos= self.navigation_system.get_offset_distance()
        self.traffic_light_state = self.sensor_manager.traffic_light_sensor()
        half_obs = [distance_to_destination_sin,distance_to_destination_cos] + rot_offsets[:2]
        observations = half_obs #+ [cos, sin]
        # observations[3] = observations[3]/36
        # observations[4] = observations[4]/36
        # observations[5] = observations[5]/36
        return observations

    def reset(self):
        status =self.reward_system.status
        if status==Status.COMPLETED:
           return self.on_completion()
        if status==Status.RESTART:
            return self.on_failure()
        else:
            return self.on_failure()
    
    def on_completion(self):
        # start_point, end_point =  8,10# np.random.randint(0,len(self.navigation_system.spawn_points),size=2) #temporary
        # self.navigation_system.reset()
        # self.vehicle_variables.start_wait(self.navigation_system.start)
        self.reward_system.reset(t=0)
        # self.vehicle_controller.reset()
        # self.navigation_system.curr_pos =0
        return self.get_observation()
    
    def on_failure(self):
        fail_point =self.navigation_system.curr_pos
        self.navigation_system.reset()
        if self.respawn_pos_times<3:
            self.navigation_system.curr_pos =fail_point
            self.respawn_pos_times +=1
        else:
            self.respawn_pos_times =0
            fail_point = 0
        self.vehicle_variables.start_wait(self.navigation_system.ideal_route[fail_point])
        self.reward_system.reset(t=1)
        self.vehicle_controller.reset(self.navigation_system.ideal_route[fail_point])
        
        # print("Car rest at pos",self.navigation_system.start,self.navigation_system.curr_pos)
        return self.get_observation()

    def on_restart(self):
        self.respawn_pos_times =0
        self.navigation_system.reset()

        self.vehicle_variables.start_wait(self.navigation_system.ideal_route[0])
        self.reward_system.reset(t=1)
        self.vehicle_controller.reset(self.navigation_system.ideal_route[0])
        
        # print("Car rest at pos",self.navigation_system.start,self.navigation_system.curr_pos)
        return self.get_observation()

    def render(self):
        self.game_manager.render()
    
    def stop(self):
        self.vehicle_controller.vehicle.destroy()
        self.sensor_manager.stop_camera()
        settings = self.world.get_settings()
        settings.synchronous_mode = False
        self.world.apply_settings(settings)
    
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
       
