import drawing_library
import carla
class LaneAI:
    def __init__(self,simulator):
            self.count = 1
            self.simulator =simulator

    def get_obstacle_status(self,event):
        print(event.distance, self.count)
        self.count += 1
        self.request_new_lane()

    def request_new_lane(self):
        vehicle =self.simulator.vehicle_variables.vehicle_location
        waypoint = self.simulator.map.get_waypoint(vehicle)
        next_waypoint =None
        print(waypoint.lane_change)
        if str(waypoint.lane_change)=='Left':
            next_waypoint = waypoint.get_left_lane()
            print("Change Left")
            self.simulator.navigation_system.make_parallel(next_waypoint,0)

        elif str(waypoint.lane_change)=='Right' or str(waypoint.lane_change)=='Both':
            next_waypoint = waypoint.get_right_lane()
            print("Change Right")
            self.simulator.navigation_system.make_parallel(next_waypoint,1)# 1-right ,0-left
        else:
            print("Not Possible")

        # if next_waypoint:
        #     debug = self.simulator.world.debug
        #     # drawing_library.draw_lines(self.simulator.world.debug,[i.transform.location for i in [waypoint,next_waypoint] ],color=carla.Color(255,0,0) )
        #     debug.draw_line(waypoint.transform.location,next_waypoint.transform.location,life_time=3,color=carla.Color(255,0,0))
        #     self.simulator.navigation_system.make_parallel(next_waypoint)

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