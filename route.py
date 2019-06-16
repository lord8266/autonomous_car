# pylint: disable=no-member
# pylint: disable=import-error

import carla 
from agents.navigation import global_route_planner,global_route_planner_dao
from agents.tools import misc
import math
import pygame
import numpy as np
from sklearn.preprocessing import StandardScaler
class Route:
    def __init__(self,world,actor,res=3):
        self.world = world
        self.actor = actor
        self.map = world.get_map()
        self.drawn_point =False
        self.prev = pygame.time.get_ticks()

    def make_route(self,start,end,res):
        dao = global_route_planner_dao.GlobalRoutePlannerDAO(self.map,res)
        grp = global_route_planner.GlobalRoutePlanner(dao)
        grp.setup()
        self.route = grp.trace_route(start.location, end.location)
        self.clean_route()
        self.fill_gaps()
        self.clean_back()
        self.curr_pos = 0

    def draw_vehicle_waypoint(self):
        if self.drawn_point:
            t = pygame.time.get_ticks()
            if (t-self.prev)>=0.5:
                self.drawn_point = False
            return

        t = self.map.get_waypoint(self.actor.get_location()).transform
        r = t.rotation
        l = t.location
        l.z =2
        d =self.world.debug
        angle = math.radians(r.yaw)
        d.draw_arrow(l,l+carla.Location(x=math.cos(angle), y=math.sin(angle)),color=carla.Color(r=0,g=255,b =0),life_time=0.5,thickness = 0.04,arrow_size=0.3)

        self.drawn_point = True
        self.prev = pygame.time.get_ticks()
    
    def draw_path(self,**args):
        l = [i[0].transform.location for i in self.route ]
        # l = self.fin_route
        d = self.world.debug
        for p in range(1,len(l)):
            d.draw_line(l[p-1],l[p],life_time=3600,**args)
            d.draw_string(carla.Location(x=l[p].x,y=l[p].y,z=3),f'{p}',life_time=3600)
            d.draw_arrow(l[p-1], l[p], arrow_size=6,life_time=3600)
    
    def get_dynamic_path(self):
        i = self.curr_pos
        actor_transform = self.actor.get_transform()
        actor_loc = actor_transform.location
        point = self.map.get_waypoint(actor_loc)
        actor_loc = point.transform.location
        prev_len = None
        while i<len(self.route):
            loc = self.route[i][0].transform.location
            # loc = self.fin_route
            curr_len = Route.get_distance(loc,actor_loc)
            # print(f'len: {curr_len} pos: {i} | actor loc: {actor_loc.x}, {actor_loc.y} | waypoint_loc: {loc.x}, {loc.y}')
            if prev_len!=None and curr_len>prev_len:
                break
            prev_len = curr_len
            i+=1
        self.curr_pos = i-1
        dynamic_route = [ (point,None)]+ self.route[self.curr_pos:self.curr_pos+10]
        dynamic_route = [i[0].transform for i in dynamic_route ]
        # print('choosing %d\n'%(self.curr_pos))
        d = self.world.debug
        for p in range(1,len(dynamic_route)): # index might go out of range
            d.draw_line(dynamic_route[p-1].location,dynamic_route[p].location,life_time=1,color=carla.Color(r=0,g=255,b=0))
        if len(dynamic_route)<10:
            add = 10-len(dynamic_route)
            dynamic_route = dynamic_route + [dynamic_route[-1]]*add
        return (self.scale_dynamic_path( dynamic_route),actor_transform,point.transform)

    def scale_dynamic_path(self,dynamic_route):
        dynamic_route = [i.rotation.yaw%360 for i in dynamic_route]

        data_ini = dynamic_route[0]
        arr = [ Route.scale_angle(i-data_ini)  for i in dynamic_route ]
        print(arr,end='\n\n')
        return arr

    @staticmethod
    def scale_angle(angle):
        if (angle<=180):
            return angle/180
        else:
            return (angle-360)/180
        
    def clean_route(self):
        temp_route = []
        i = 0
        while i<(len(self.route)-1):
            t1 = self.route[i][0].transform
            t2 = self.route[i+1][0].transform
            temp_route.append(self.route[i])
            if Route.get_distance(t1.location,t2.location,res=1)<=5:
                i+=1
            i+=1
        temp_route.append(self.route[-1])
        self.route = temp_route    
        # there are holes created due to this 
        # might want to generate waypoint

    def clean_back(self):
        first = True
        back_cnt =0
        while first or back_cnt!=0:
            i=1
            temp_route = []
            back_cnt=0
            first =False
            temp_route.append(self.route[0])
            while i<(len(self.route)-1):
                t0 = self.route[i-1][0].transform
                t1 = self.route[i][0].transform
                t2 = self.route[i+1][0].transform
                
                b = Route.check_behind(t0,t1,t2)
                print(f'b: {b}')
                print(f'pos {i-1}: {t0.location} | pos {i}: {t1.location} | pos {i+1}: {t2.location}')
                print(f'pos {i+1} is  behind pos {i}',f'unit_vec: {Route.loc_str(b[1]) } r_vec: {Route.loc_str(b[2])} dot: {b[3]}\n')
                temp_route.append(self.route[i])
                if b[0]:
                    back_cnt+=1
                    i+=1
                i+=1
            temp_route.append(self.route[-1])
            self.route = temp_route    
    @staticmethod 
    def check_error(t0,t1,t2):
        b=None
        if t0!=None:
            b = Route.check_behind(t0,t1,t2)
        p1 = t1.location
        p2 = t2.location
        l = Route.get_distance(p1,p2)
        if l>=7 and (t0==None or  b[0]==False):
            return False
        else:
            return True

    @staticmethod
    def check_behind(t0,t1,t2): # check if t2 is behind t1
        # angle = math.radians(t1.rotation.yaw)
        unit_vec = Route.get_loc(misc.vector(t0.location,t1.location))
        r_vec = Route.get_loc(misc.vector(t1.location,t2.location))

        dot = r_vec.x*unit_vec.x + r_vec.y*unit_vec.y
        if dot<=0:
            return (True,unit_vec,r_vec,dot)
        else:
            return (False,unit_vec,r_vec,dot)

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
        while i<(len(self.route)-1):
            p1 = self.route[i][0].transform.location
            p2 = self.route[i+1][0].transform.location
            distance = Route.get_distance(p1,p2,res=1)
            temp_route.append(self.route[i])
            if distance>=7:
                print("here",i,cnt,len(temp_route))
                done=False
                angle = math.radians(self.route[i][0].transform.rotation.yaw )
                p_t = p1 + carla.Location(x = math.cos(angle)*distance/2,y =math.sin(angle)*distance/2,z=0)
                w = self.map.get_waypoint(p_t)
                temp_route.append( (w,self.route[i][1]))
            i+=1
        cnt+=1
        temp_route.append(self.route[-1])
        self.route = temp_route

    @staticmethod
    def get_distance(p1,p2,res=0): # if need to square root
        l =(p1.x-p2.x)**2 + (p1.y-p2.y)**2
        if res:
            return l**0.5
        else:
            return l

    