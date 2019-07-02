import drawing_library
import carla
import navigation_system
import math
import numpy as np
from agents.tools import misc
import pygame

class LaneAI:
    def __init__(self,simulator):
            self.count = 1
            self.simulator =simulator
            self.previous_lane_id = None
            self.prev = pygame.time.get_ticks()

    def get_obstacle_status(self,event):
       

        actor = event.other_actor
        self.previous_vehicle = actor
        actor_waypoint = self.simulator.map.get_waypoint(actor.get_location())
        actor_lane_id = actor_waypoint.lane_id
        if self.previous_lane_id==None or self.previous_lane_id!=actor_lane_id:
            vehicle_lane_id = self.simulator.map.get_waypoint(self.simulator.vehicle_variables.vehicle_location).lane_id
            self.previous_lane_id = actor_lane_id 
            print("here",actor_lane_id,vehicle_lane_id)
            if actor_lane_id==vehicle_lane_id:
                self.simulator.navigation_system.new_change_event(prefer_left=True)
        



    def request_new_lane(self,prefer_left=True):
        vehicle =self.simulator.vehicle_variables.vehicle_location
        waypoint = self.simulator.map.get_waypoint(vehicle)
        next_waypoint =None
        print(waypoint.lane_change)
        if prefer_left:
            if str(waypoint.lane_change)=='Left' or str(waypoint.lane_change)=='Both':
                next_waypoint = waypoint.get_left_lane()
                print("Change Left")
            elif str(waypoint.lane_change)=='Right' :
                next_waypoint = waypoint.get_right_lane()
                print("Change Right")
            else:
                print("Not Possible")
        else:
            if str(waypoint.lane_change)=='Right' or str(waypoint.lane_change)=='Both':
                next_waypoint = waypoint.get_right_lane()
                print("Change Right")
            elif str(waypoint.lane_change)=='Left':
                next_waypoint = waypoint.get_left_lane()
                print("Change Left")
            else:
                print("Not Possible")
            
        if next_waypoint:
            next_waypoint= self.check_waypoint_angle(next_waypoint,self.simulator.vehicle_variables.vehicle_transform)
            drawing_library.draw_lines(self.simulator.world.debug,[i.transform.location for i in [waypoint,next_waypoint] ],color=carla.Color(255,0,0) )
            self.simulator.navigation_system.make_parallel(next_waypoint)# 1-right ,0-left

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
        return next_waypoint

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
    
 
    
#         distance 	float 	5 	Distance to throw the trace to
# hit_radius 	float 	0.5 	Radius of the trace
# only_dynamics 	bool 	false 	If true, the trace will only look for dynamic objects
# debug_linetrace 	bool 	false 	If true, the trace will be visible
# sensor_tick