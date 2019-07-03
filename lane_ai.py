import drawing_library
import carla
import navigation_system
import math
import numpy as np
from agents.tools import misc
import pygame
from enum import Enum
class LaneAI:
    def __init__(self,simulator):
            self.count = 1
            self.simulator =simulator
            self.previous_lane_id = None
            self.prev = pygame.time.get_ticks()
            self.obstacles  ={}
            self.cnt = 0
            self.print_prev = self.prev
            self.add_buffer = []
            self.obstacle_table = {}
            self.update_ = False
            self.lane_changer = LaneChanger(self)
            self.lane_prev = self.prev
    def get_obstacle_status(self,event):

        obstacle = event.other_actor

        if str(obstacle.type_id).find("vehicle")!=-1:
            # print(obstacle,self.cnt)
            self.cnt+=1
            obstacle_waypoint = self.simulator.map.get_waypoint(obstacle.get_location())
            obstacle_lane_id = obstacle_waypoint.lane_id
            obstacle_road_id = obstacle_waypoint.road_id

            vehicle  = self.simulator.vehicle_controller.vehicle
            vehicle_waypoint = self.simulator.map.get_waypoint(self.simulator.vehicle_variables.vehicle_location)
            vehicle_lane_id = vehicle_waypoint.lane_id
            vehicle_road_id = vehicle_waypoint.road_id

            # print(f"Found obstacle on lane:{obstacle_lane_id}, road: {obstacle_road_id}, vehicle on lane:{vehicle_lane_id}, road: {vehicle_road_id} ")
            # print(f"Obstacle ID:{obstacle}, Vehicle ID: {vehicle},  Distance:",event.distance)
            # print()
            self.add_buffer.append((obstacle,obstacle_road_id,obstacle_lane_id))

    def add_obstacle(self,obstacle):
            obstacle_waypoint = self.simulator.map.get_waypoint(obstacle.get_location())
            obstacle_lane_id = obstacle_waypoint.lane_id
            obstacle_road_id = obstacle_waypoint.road_id


            # print(f"Found obstacle on lane:{obstacle_lane_id}, road: {obstacle_road_id}, vehicle on lane:{vehicle_lane_id}, road: {vehicle_road_id} ")
            # print(f"Obstacle ID:{obstacle}, Vehicle ID: {vehicle},  Distance:",event.distance)
            # print()
            self.add_buffer.append((obstacle,obstacle_road_id,obstacle_lane_id))
    def start_queue(self):
          r = self.add_buffer
          self.add_buffer = []
          for o,r,l in r:
              self.add_to_set(o,r,l)



    def request_new_lane(self,prefer_left=False):
        curr =pygame.time.get_ticks()
        if (curr-self.lane_prev)>2000:
            vehicle =self.simulator.vehicle_variables.vehicle_location
            waypoint = self.simulator.map.get_waypoint(vehicle)
            next_waypoint =None
            print(waypoint.lane_change)
            self.lane_prev = curr
            if prefer_left:
                if str(waypoint.lane_change)=='Left' or str(waypoint.lane_change)=='Both':
                    next_waypoint = waypoint.get_left_lane()
                    # print("Change Left")
                elif str(waypoint.lane_change)=='Right' :
                    next_waypoint = waypoint.get_right_lane()
                    # print("Change Right")
                else:
                    pass
                    # print("Not Possible")
            else:
                if str(waypoint.lane_change)=='Right' or str(waypoint.lane_change)=='Both':
                    next_waypoint = waypoint.get_right_lane()
                    # print("Change Right")
                elif str(waypoint.lane_change)=='Left':
                    next_waypoint = waypoint.get_left_lane()
                    pass
                    # print("Change Left")
                else:
                    pass
                    # print("Not Possible")
                
            if next_waypoint:
                next_waypoint= self.check_waypoint_angle(next_waypoint,self.simulator.vehicle_variables.vehicle_transform)
                drawing_library.draw_lines(self.simulator.world.debug,[i.transform.location for i in [waypoint,next_waypoint] ],color=carla.Color(255,0,0) )
                self.simulator.navigation_system.make_parallel(next_waypoint)# 1-right ,0-left
                
            
            return next_waypoint
        
        return None
        
        # if next_waypoint:
        #     debug = self.simulator.world.debug
        #     # drawing_library.draw_lines(self.simulator.world.debug,[i.transform.location for i in [waypoint,next_waypoint] ],color=carla.Color(255,0,0) )
        #     debug.draw_line(waypoint.transform.location,next_waypoint.transform.location,life_time=3,color=carla.Color(255,0,0))
        #     self.simulator.navigation_system.make_parallel(next_waypoint)

    def check_waypoint_angle(self,next_waypoint,vehicle_transform):
       
        vp = vehicle_transform
        p2 = next_waypoint.transform.location
        u2 =misc.vector(p2, vp.location)
        u1 = np.array(misc.vector(vp.location,self.simulator.navigation_system.ideal_route[self.simulator.navigation_system.curr_pos].location))
        angle = math.degrees(np.arccos(u1.dot(u2) ))
        cnt =0 
        # print(angle)
        while angle<150 and cnt<10:
            n = next_waypoint.next(0.6)
            if n:
                next_waypoint = n[0]
            else:
                break
            
            p2 = next_waypoint.transform.location
            u2 =misc.vector(p2, vp.location)
            u1 = np.array(misc.vector(vp.location,self.simulator.navigation_system.ideal_route[self.simulator.navigation_system.curr_pos].location))
            angle = math.degrees(np.arccos(u1.dot(u2) ))
            # print(angle)
            cnt+=1
        return next_waypoint


        # cnt =0
        # while int(abs(y2-x2))==1:
        #     next_waypoint = next_waypoint.next(0.5)[0]
        #     cnt+=1
        #     vp = vehicle_transform.location
        #     p2 = next_waypoint.transform.location
        #     y2 = p2.y-vp.y + np.finfo(float).eps 
        #     x2 = p2.x-vp.x +np.finfo(float).eps 
            
        #     print(slope)


    def print_waypoint(self,waypoint):
        print("transform :",waypoint.transform)
        print("lane width :",waypoint.lane_width)
        print("roadid :",waypoint.road_id)
        print("section id :",waypoint.section_id)
        print("lane id :",waypoint.lane_id)
        print("lane change :",waypoint.lane_change) 
        print("lane type :",waypoint.lane_type) 
        print("right mark :",waypoint.right_lane_marking) 
        print("left mark :",waypoint.left_lane_marking)
    
    def add_to_set(self,obstacle,road_id,lane_id):

        if obstacle.id not in self.obstacles:
            self.obstacles[obstacle.id] =Obstacle(self.simulator,obstacle,road_id,lane_id)
            self.update_ = True
        else:
            self.obstacles[obstacle.id].last_updated = pygame.time.get_ticks()

    def update_set(self):
        rem_buffer = []
        curr = pygame.time.get_ticks()
        for _,o in self.obstacles.items():
            if (curr-o.last_updated)>2000:
                rem_buffer.append(_)

        for r in rem_buffer:
            self.update_= True
            self.obstacles.pop(r)
             
    def update(self):

        curr =pygame.time.get_ticks()
        self.update_set()
        self.start_queue()
        self.lane_changer.update()
        self.update_table()
        if (curr-self.prev)>200:
            self.prev =curr
            for _,obstacle in self.obstacles.items():
                obstacle.update()

        if (curr-self.print_prev)>=1000:
            # print("Current Table")
            # print(self.obstacles)
            # for obs,obs_vals in self.obstacles.items():
            #     print(obs,obs_vals.road_id,obs_vals.lane_id,"Last Updated: ",curr-obs_vals.last_updated)
            # self.print_table()
            # print()
            self.print_prev = curr

    def update_table(self):
        if self.update_:
            self.update_ = False
            self.obstacle_table = {}

            for obs_id,obs in self.obstacles.items():

                if obs.road_id in self.obstacle_table:
                    if obs.lane_id in self.obstacle_table[obs.road_id]:
                        self.obstacle_table[obs.road_id][obs.lane_id].add(obs)
                    else:
                        self.obstacle_table[obs.road_id][obs.lane_id] = {obs}
                else:
                    self.obstacle_table[obs.road_id] = {obs.lane_id:{obs}}
    
    def print_table(self):
        curr =pygame.time.get_ticks()
        road_id = self.simulator.vehicle_variables.vehicle_waypoint.road_id
        lane_id = self.simulator.vehicle_variables.vehicle_waypoint.lane_id

        for road in self.obstacle_table:
            print("Road",road)
            for lane in self.obstacle_table[road]:
                print("  Lane:",lane)

                if road_id==road and lane_id==lane:
                    print("   Vehicle Here")
                for obs in self.obstacle_table[road][lane]:
                    print("   Name:",obs.vehicle, "Last Updated:",curr-obs.last_updated,"Angle:",obs.angle,"Distance:",obs.distance)

    
class Obstacle:

    def __init__(self,simulator,vehicle,road_id,lane_id):
        self.simulator = simulator
        self.vehicle = vehicle
        self.last_updated = pygame.time.get_ticks()
        self.update()

    def update(self):
        # self.last_updated = pygame.time.get_ticks()
        waypoint = self.simulator.map.get_waypoint(self.vehicle.get_location())
        self.road_id = waypoint.road_id
        self.lane_id = waypoint.lane_id
        self.waypoint = waypoint
        self.distance = navigation_system.NavigationSystem.get_distance(waypoint.transform.location,self.simulator.vehicle_variables.vehicle_location,res=1)

        self.get_angle()

    def get_angle(self):
        p0  = self.simulator.vehicle_variables.vehicle_waypoint.transform.location
        p2 = self.simulator.vehicle_variables.vehicle_waypoint.next(1.0)[0].transform.location
        p1 = self.waypoint.transform.location

        u1 = misc.vector(p0,p1)
        u2  = misc.vector(p0,p2)     
        dot = np.array(u2).dot(u1)
        angle = math.degrees( math.acos(dot))
        self.angle = angle
    

class State(Enum):
    RUNNING=1,
    LANE_CHANGE=2,
    FOLLOW=3
    STOP=4,

class LaneChanger:

    def __init__(self,lane_ai):
        self.lane_ai = lane_ai
        self.prev = pygame.time.get_ticks()
        self.state = State.RUNNING
        self.brake_state = carla.VehicleControl( throttle = 0,steer = 0,brake = 0.4,reverse =False)
        self.current_obstacle = None
        self.stop = False
        self.prev_stop = self.stop
    
    def print_stop_state(self):
        
        for w in self.list_close:
            if w.lane_id==self.lane_ai.simulator.vehicle_variables.vehicle_waypoint.lane_id:
                closest = w
                break
        if self.prev_stop!=self.stop:
            print("Stop State: ",self.stop)
            self.prev_stop = self.stop
        
    def update(self):
        curr =pygame.time.get_ticks()

        if (curr-self.prev)>50:
            self.check_new_lane()
            self.prev =curr
            self.print_stop_state()
    
    def check_new_lane(self):
        wp = self.lane_ai.simulator.vehicle_variables.vehicle_waypoint
        road_id = wp.road_id
        lane_id = wp.lane_id

        table = self.lane_ai.obstacle_table
        obstacle_found = False
        stop =False
        if self.state==State.RUNNING:
            
            if road_id in table:

                if lane_id in table[road_id]:

                    for v in table[road_id][lane_id]:
                        

                        if v.distance <20:
                            next_ = self.lane_ai.request_new_lane()
                            if next_!=None:

                                self.state = State.LANE_CHANGE
                                self.prev_waypoint_id = wp.lane_id
                                self.current_obstacle = v
                                self.next_lane = next_.lane_id

                            else:
                                self.state = State.STOP
                            break
           

        elif self.state==State.LANE_CHANGE:

            if road_id in table:

                if lane_id in table[road_id]:

                    for v in table[road_id][lane_id]:
                        if v.distance<6 and v.angle<90:
                            self.state = State.STOP
            self.update_waypoint()

        elif self.state==State.STOP:
            stop =True
            if road_id in table:
                list_close = []
                for lane in table[road_id]:
                   
                    for v in table[road_id][lane]:
                        if v.distance<15 and v.angle<90:
                            list_close.append(v)
                self.list_close = list_close
                if list_close:
                    # print([w.vehicle for w in list_close])    
                    closest_obstacle = min(list_close,key=lambda f:f.distance)

                    vel = self.lane_ai.simulator.vehicle_variables.vehicle_velocity_magnitude
                    if vel<0.07 and 7<=closest_obstacle.distance<=14:
                        print("Continue")
                        stop =False
                    elif closest_obstacle.distance>8 and closest_obstacle.waypoint.lane_id==lane_id:
                        self.state = State.RUNNING
                else:
                    stop =False
                    self.state =State.RUNNING
        self.stop =stop
        self.lane_ai.simulator.collision_vehicle = stop
    # def follow(self):
    #     velocity = np.clip(  self.lane_ai.simulator.vehicle_variables.vehicle_velocity_magnitude,0,8.3)
    #     self.lane_ai.simulator.follow = False
    #     if velocity<0.4:
    #         if self.current_obstacle!=None:
    #             self.lane_ai.simulator.follow = True


    def apply_brakes(self):
        # d = self.current_obstacle.distance
        # d = np.clip(d,0,10)
        # velocity = np.clip(  self.lane_ai.simulator.vehicle_variables.vehicle_velocity_magnitude,0,8.3)

        
        # # velocity = np.clip(velocity,0,1)
        # print("velocity : ", velocity)
        # brake_state = ((10-d)*velocity)/10
        # brake_state = np.clip(brake_state,0,0.95)
        return 1 #brake_state

    def update_waypoint(self):
        wp = self.lane_ai.simulator.vehicle_variables.vehicle_waypoint.lane_id
        
        if wp!=self.prev_waypoint_id:
            self.state = State.RUNNING




