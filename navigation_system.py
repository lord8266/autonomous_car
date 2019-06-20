# pylint: disable=no-member
# pylint: disable=import-error

import carla 
from agents.navigation import global_route_planner,global_route_planner_dao
from agents.tools import misc
import math
import pygame
import Simulator
import numpy as np
from sklearn.preprocessing import StandardScaler

class NavigationSystem:
    def __init__(self,simulator):
        self.simulator = simulator
        self.spawn_points = self.simulator.map.get_spawn_points()
        
        self.drawn_point =False
        self.prev = pygame.time.get_ticks()
        self.dynamic_path  = None
    
    def make_map_data(self,res=3):
        self.map_data = global_route_planner_dao.GlobalRoutePlannerDAO(self.simulator.map,res)
        self.route_planner = global_route_planner.GlobalRoutePlanner(self.map_data)
        self.route_planner.setup()
    
    def make_ideal_route(self,start_index,destination_index):
        self.start = self.spawn_points[start_index]
        self.destination = self.spawn_points[destination_index]
        self.ideal_route = self.route_planner.trace_route_transforms(self.start.location, self.destination.location)
        self.clean_route()
        self.fill_gaps()
        self.clean_back()
        self.curr_pos = 0
        self.destination_index = len(self.ideal_route)-1
    
    def make_local_route(self):

        i = self.curr_pos
        vehicle_location = self.simulator.vehicle_variables.vehicle_location
        vehicle_transform = self.simulator.vehicle_variables.vehicle_transform
        closest_waypoint_location = self.simulator.vehicle_variables.closest_waypoint_location
        closest_waypoint_transform = self.simulator.vehicle_variables.closest_waypoint_transform

        prev_len = None
        while i<len(self.ideal_route):
            loc = self.ideal_route[i].location
            # print(i)
            curr_len = NavigationSystem.get_distance(loc,vehicle_location)
           
            if prev_len!=None and curr_len>prev_len:
                break
            prev_len = curr_len
            i+=1
        self.curr_pos = i-1
        # i = max(1,i-1) #need to change
        if i!=len(self.ideal_route):
            behind = NavigationSystem.check_behind(vehicle_transform,self.ideal_route[i-1],self.ideal_route[i])
            if  behind:
                self.curr_pos+=1
        
        self.local_route = [vehicle_transform]+self.ideal_route[self.curr_pos:self.curr_pos+3]
        
        if len(self.local_route)<4:
            add = 4-len(self.local_route)
            self.local_route = self.local_route + [self.local_route[-1]]*add
        # print("choosing %d\n"%(self.curr_pos))
       

    def get_rot_offset(self): # needs to change
        vehicle_yaw = NavigationSystem.transform_angle(self.simulator.vehicle_variables.vehicle_yaw)
        # vehicle_yaw = np.tan( math.radians(self.simulator.vehicle_variables.vehicle_yaw))

        rot_offsets =[]
        # print(len(self.local_route))
        for i in range(len(self.local_route)-1):
            p1 = self.local_route[i].location
            p2 = self.local_route[i+1].location
            # vec1 = misc.vector(p1,p2)
            # vec2 = [math.cos(vehicle_yaw*180/np.pi),math.sin(vehicle_yaw*180/np.pi),0]
            # angle_ =  np.arccos(vec1.dot(vec2))*180/np.pi
            y_ = p2.y-p1.y + np.finfo(float).eps 
            x_ = p2.x-p1.x +np.finfo(float).eps 
            angle =  math.degrees(np.arctan2(y_,x_))
            rot_offsets.append( NavigationSystem.transform_angle(angle-vehicle_yaw) )
            # print(i,angle,vehicle_yaw)
        return rot_offsets


    
    @staticmethod
    def transform_angle(angle):
        if (angle<180):
            return angle
        else:
            return angle-360
         
        
    def clean_route(self):
        temp_route = []
        i = 0
        while i<(len(self.ideal_route)-1):
            t1 = self.ideal_route[i]
            t2 = self.ideal_route[i+1]
            temp_route.append(t1)
            if NavigationSystem.get_distance(t1.location,t2.location,res=1)<=5:
                i+=1
            i+=1
        temp_route.append(self.ideal_route[-1])
        self.ideal_route = temp_route    
       

    def clean_back(self):
        first = True
        back_cnt =0
        n_iter =0 
        while (first or back_cnt!=0) and n_iter<=5:
            i=1
            temp_route = []
            back_cnt=0
            first =False
            temp_route.append(self.ideal_route[0])
            while i<(len(self.ideal_route)-1):
                t0 = self.ideal_route[i-1]
                t1 = self.ideal_route[i]
                t2 = self.ideal_route[i+1]
                
                behind = NavigationSystem.check_behind(t0,t1,t2)
            
                temp_route.append(self.ideal_route[i])
                if behind:
                    back_cnt+=1
                    i+=1
                i+=1
            temp_route.append(self.ideal_route[-1])
            self.ideal_route = temp_route 
            n_iter+=1  

    def reset(self):
        # print("calling reset")
        self.curr_pos = 1
        # print("curent pos is %d"%(self.curr_pos))
    
    @staticmethod 
    def check_error(t0,t1,t2):
        b=None
        if t0!=None:
            b = NavigationSystem.check_behind(t0,t1,t2)
        p1 = t1.location
        p2 = t2.location
        l = NavigationSystem.get_distance(p1,p2)
        if l>=7 and (t0==None or  b[0]==False):
            return False
        else:
            return True

    @staticmethod
    def check_behind(t0,t1,t2):
       
        unit_vec = NavigationSystem.get_loc(misc.vector(t0.location,t1.location))
        r_vec = NavigationSystem.get_loc(misc.vector(t1.location,t2.location))

        dot = r_vec.x*unit_vec.x + r_vec.y*unit_vec.y
        if dot<0:
            return True# (True,unit_vec,r_vec,dot)
        else:
            return False # (False,unit_vec,r_vec,dot)

    @staticmethod
    def get_loc(p):
        return carla.Location(p[0],p[1],p[2])

    @staticmethod
    def loc_str(l,z=0):
        if z:
            return f'x: {l.x}, y: {l.y}, z:{l.z}'
        else:
            return f'x: {l.x}, y: {l.y}'
       
    def fill_gaps(self):
        temp_route = []
        
        p1,p2=None,None
        first = True
        done = True
        cnt =0
        i=0
        for j in range(2):
            i=0
            temp_route =[]
            while i<(len(self.ideal_route)-1):
                p1 = self.ideal_route[i].location
                p2 = self.ideal_route[i+1].location
                distance =NavigationSystem.get_distance(p1,p2,res=1)
                temp_route.append(self.ideal_route[i])
                if distance>=7:
                    done=False
                    # angle = math.radians(self.ideal_route[i].rotation.yaw) #need to change
                    p_t =carla.Location(x = (p1.x+p2.x)/2,y = (p1.y+p2.y)/2,z=p1.z)
                    w = self.simulator.map.get_waypoint(p_t)
                    temp_route.append(w.transform)
                i+=1
            cnt+=1
            temp_route.append(self.ideal_route[-1])
            self.ideal_route = temp_route

    @staticmethod
    def get_distance(p1,p2,res=0): 
        l =(p1.x-p2.x)**2 + (p1.y-p2.y)**2
        if res:
            return l**0.5
        else:
            return l
    

    
            