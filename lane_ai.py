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
            self.lane_closest = {}

    def get_closest_obstacles(self):
        vehicle  = self.simulator.vehicle_controller.vehicle
        vehicle_waypoint = self.simulator.map.get_waypoint(self.simulator.vehicle_variables.vehicle_location)
        vehicle_lane_id = vehicle_waypoint.lane_id
        vehicle_road_id = vehicle_waypoint.road_id

        lane_closest = {}
        lane_sign = vehicle_lane_id>0

        if vehicle_road_id in self.obstacle_table:

            for lane in self.obstacle_table[vehicle_road_id]:
                if (lane>0)==lane_sign:
                    in_front = [ w for w in self.obstacle_table[vehicle_road_id][lane] if w.angle<120] 
                    # print(in_front)
                    if in_front:
                        closest_obstacle = min(in_front ,key=lambda f:f.distance)
                        lane_closest[lane] = closest_obstacle
                    
        
        self.lane_closest = lane_closest

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
        if len(self.add_buffer)>50:
            r = self.add_buffer[:50]
            self.add_buffer = self.add_buffer[50:]
            for o,r,l in r:
                self.add_to_set(o,r,l)
        else:
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
                
            
                
            
            return next_waypoint
        
        return None
        
        # if next_waypoint:
        #     debug = self.simulator.world.debug
        #     # drawing_library.draw_lines(self.simulator.world.debug,[i.transform.location for i in [waypoint,next_waypoint] ],color=carla.Color(255,0,0) )
        #     debug.draw_line(waypoint.transform.location,next_waypoint.transform.location,life_time=3,color=carla.Color(255,0,0))
        #     self.simulator.navigation_system.make_parallel(next_waypoint)

    def check_waypoint_angle(self,next_waypoint,vehicle_transform,turn_angle=150):
       
        vp = vehicle_transform
        p2 = next_waypoint.transform.location
        u2 =misc.vector(p2, vp.location)
        u1 = np.array(misc.vector(vp.location,self.simulator.navigation_system.ideal_route[self.simulator.navigation_system.curr_pos].location))
        angle = math.degrees(np.arccos(u1.dot(u2) ))
        cnt =0 
        # print(angle)
        while angle<turn_angle and cnt<10:
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
        vehicle_road_id = self.simulator.vehicle_variables.vehicle_waypoint.road_id
        vehicle_lane_id = self.simulator.vehicle_variables.vehicle_waypoint.lane_id

        if road_id==vehicle_road_id:
            if obstacle.id not in self.obstacles:
                self.obstacles[obstacle.id] =Obstacle(self.simulator,obstacle,road_id,lane_id)
                self.update_ = True
            else:
                self.obstacles[obstacle.id].last_updated = pygame.time.get_ticks()

    def update_set(self):
        curr_road_id =self.simulator.vehicle_variables.vehicle_waypoint.road_id
        rem_buffer = []
        curr = pygame.time.get_ticks()
        for _,o in self.obstacles.items():
            if (curr-o.last_updated)>2000 or o.road_id!=curr_road_id:
                rem_buffer.append(_)

        for r in rem_buffer:
            self.update_= True
            self.obstacles.pop(r)
             
    def update(self):

        curr =pygame.time.get_ticks()
        self.update_set()
        self.start_queue()
        self.update_table()
        if (curr-self.prev)>200:
            self.prev =curr
            for _,obstacle in self.obstacles.items():
                obstacle.update()

        if (curr-self.print_prev)>=400:
            self.print_table()
            self.print_prev = curr
        
        self.collision_control()
    
    def collision_control(self):
        vehicle_lane_id = self.simulator.vehicle_variables.vehicle_waypoint.lane_id
        
        if vehicle_lane_id in self.lane_closest:
            obstacle  = self.lane_closest[vehicle_lane_id]

            if self.lane_changer.state==State.RUNNING:
                if obstacle.distance<10 and obstacle.delta_d<0:
                    change_lane = self.lane_changer.check_new_lane(min_angle=110)
                    if not change_lane:
                        print("Stopping")
                        control = self.simulator.vehicle_controller.control
                        control.throttle = 0
                        control.brake = 0.95

                elif obstacle.distance<20 and obstacle.delta_d<0:
                    change_lane = self.lane_changer.check_new_lane(min_angle=150)
            else:
                if obstacle.distance<7 and obstacle.delta_d<0:
                    print("Other case stopping")
                    control = self.simulator.vehicle_controller.control
                    control.throttle = 0
                    control.brake = 0.95
                    

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
        self.get_closest_obstacles()

    def print_table(self):
        curr =pygame.time.get_ticks()
        road_id = self.simulator.vehicle_variables.vehicle_waypoint.road_id
        lane_id = self.simulator.vehicle_variables.vehicle_waypoint.lane_id
        # print("Current Table")
        print(f"Vehicle: LaneType: { str(self.simulator.vehicle_variables.vehicle_waypoint.lane_type)}, LaneWidth:{str(self.simulator.vehicle_variables.vehicle_waypoint.lane_width)} Road:{road_id} Lane:{lane_id}")
        # for road in self.obstacle_table:
        #     print("Road",road)
        #     for lane in self.obstacle_table[road]:
        #         print("  Lane:",lane)

        #         if road_id==road and lane_id==lane:
        #             print("   Vehicle Here")
        #         for obs in self.obstacle_table[road][lane]:
        #             print("   Name:",obs.vehicle, "Last Updated:",curr-obs.last_updated,"Angle:",obs.angle,"Distance:",obs.distance,"Delta:",obs.delta_d)

        print("Closest:")
        for i,obs in self.lane_closest.items():
            print(f'Lane:',i,)
            print("   Name:",obs.vehicle, "Last Updated:",curr-obs.last_updated,"Angle:",obs.angle,"Distance:",obs.distance,"Delta:",obs.delta_d)
        print()

class Obstacle:

    def __init__(self,simulator,vehicle,road_id,lane_id):
        self.simulator = simulator
        self.vehicle = vehicle
        self.last_updated = pygame.time.get_ticks()
        self.prev_distance = 0
        self.update()

    def update(self):
        # self.last_updated = pygame.time.get_ticks()
        waypoint = self.simulator.map.get_waypoint(self.vehicle.get_location())
        self.road_id = waypoint.road_id
        self.lane_id = waypoint.lane_id
        self.waypoint = waypoint
        self.distance = navigation_system.NavigationSystem.get_distance(waypoint.transform.location,self.simulator.vehicle_variables.vehicle_location,res=1)
        self.delta_d = self.distance-self.prev_distance
        self.prev_distance = self.distance
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
        self.current_obstacle = None
        self.stop = False
        self.prev_stop = self.stop
    
    def update(self):
        curr =pygame.time.get_ticks()

           
    
    def check_new_lane(self,min_angle):

        done =False
        if self.state==State.RUNNING:
            wp = self.lane_ai.simulator.vehicle_variables.vehicle_waypoint
            closest_data = self.lane_ai.lane_closest

            distance_to_same_lane_obstacle = closest_data[wp.lane_id].distance
            next_waypoint = self.lane_ai.request_new_lane()
            
            if next_waypoint:
                
                next_waypoint_lane_id = next_waypoint.lane_id
                if next_waypoint_lane_id in closest_data:
                    distance_other_lane_obstacle = closest_data[next_waypoint_lane_id].distance

                    if distance_to_same_lane_obstacle<distance_other_lane_obstacle:
                        print("Same",distance_to_same_lane_obstacle,", other",distance_other_lane_obstacle)
                        done  =True
                else:
                    done = True

                if done:
                    next_waypoint= self.lane_ai.check_waypoint_angle(next_waypoint,self.lane_ai.simulator.vehicle_variables.vehicle_transform,min_angle)
                    self.lane_ai.simulator.navigation_system.add_event(next_waypoint)
                    self.target_waypoint_id = next_waypoint_lane_id
                    self.state = State.LANE_CHANGE

           
        else:
            self.update_waypoint()

        return done
       

    def update_waypoint(self):
        wp_lane_id = self.lane_ai.simulator.vehicle_variables.vehicle_waypoint.lane_id
        
        if wp_lane_id==self.target_waypoint_id:
            self.state = State.RUNNING




