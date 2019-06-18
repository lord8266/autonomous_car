import carla
import navigation_system
class RewardSystem:

    def __init__(self,simulator):

        self.simulator = simulator
        self.curr_reward = 0
        self.max_rot_offset = 90 
        self.done = False
        self.prev_pos = self.simulator.navigation_system.curr_pos
        self.discrete_rewards = 0
        self.count = 0

    def direction_reward(self):
        r1 = self.simulator.vehicle_variables.vehicle_yaw
        r2 = self.simulator.vehicle_variables.closest_waypoint_yaw
        self.curr_reward-= abs(r1-r2) #temporary
        # need to add max offset
    
    def proximity_reward(self):
        l1 = self.simulator.vehicle_variables.vehicle_location
        l2 =self.simulator.vehicle_variables.closest_waypoint_location
        self.curr_reward -=navigation_system.NavigationSystem.get_distance(l1,l2,res=1)

        #need to add max distance

    def checkpoint_reward(self):
        pos = self.simulator.navigation_system.curr_pos
        if pos>self.prev_pos:
            self.curr_reward+=20
            
        elif pos<self.prev_pos:
            self.curr_reward -=-50
        else:
            self.curr_reward -= 5.6
            
        self.prev_pos = pos
            
    def update_rewards(self):
        self.curr_reward =0
        self.checkpoint_reward()
        self.direction_reward()
        self.proximity_reward()
        self.get_discrete_rewards()
        return self.curr_reward,self.done

    def reset(self):
        self.curr_reward = 0
        self.done =False
        self.d =0

    
    def lane_invasion_event(self,event):
        lane_types = set( str(x.type) for x in event.crossed_lane_markings)
       
        # print(event.crossed_lane_markings)
        # print(lane_types)
        # for i in lane_types:
        #     print(i)
        # text = ['%r' % str(x).split()[-1] for x in lane_types]
        # text = text[0]
        # text = str(text)
        # print("lane invation - ",text)

        if  "Solid" in lane_types or "SolidSolid" in lane_types or "BrokenSolid" in lane_types:
            print("wrong lane")
            self.discrete_rewards -= 10


    def get_discrete_rewards(self):
        if self.discrete_rewards!=0:
            self.curr_reward += self.discrete_rewards
            self.discrete_rewards = 0
        
    def collision_event(self,event):
        self.done =True
        print("collision")
    
    def traffic_rules(self):
        print("traffic rules")
    
    def offroad(self):
        print("offroad")    

        
