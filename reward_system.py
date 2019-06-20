import carla
import navigation_system
import Simulator
class RewardSystem:

    def __init__(self,simulator):

        self.simulator = simulator
        self.curr_reward = 0
        self.max_rot_offset = 90 
        self.done = False
        self.prev_pos = self.simulator.navigation_system.curr_pos
        self.discrete_rewards = 0
        self.count = 0
        self.status = Simulator.Status.RUNNING

    def direction_penalty(self):
        offset = self.simulator.observation[1]
        self.curr_reward-= abs(offset)*20
        # need to add max offset
    
    def proximity_penalty(self):
        l1 = self.simulator.vehicle_variables.vehicle_location
        l2 =self.simulator.navigation_system.local_route[1].location
        self.curr_reward -=navigation_system.NavigationSystem.get_distance(l1,l2,res=1)*30

        #need to add max distance

    def checkpoint_reward(self):
        pos = self.simulator.navigation_system.curr_pos

        if pos==self.simulator.navigation_system.destination_index:
            self.status = Simulator.Status.COMPLETED
            self.curr_reward+=75
        elif pos>self.prev_pos:
            self.curr_reward+=20
        elif pos<self.prev_pos:
            self.curr_reward -=-50
        else:
            self.curr_reward -= 5
            
        self.prev_pos = pos
            
    def update_rewards(self):
        self.curr_reward =0
        self.checkpoint_reward()
        self.direction_penalty()
        self.proximity_penalty()
        self.get_discrete_rewards()
        return self.curr_reward,self.status

    def reset(self):
        self.curr_reward = 0
        self.prev_pos = 0
        self.status = Simulator.Status.RUNNING
        self.d =0

    
    def lane_invasion_penalty(self,event):
        lane_types = set( str(x.type) for x in event.crossed_lane_markings)
        if  "Solid" in lane_types or "SolidSolid" in lane_types or "BrokenSolid" in lane_types:
            print("wrong lane")
            self.discrete_rewards -= 50
            # self.status = Simulator.Status.FAILED

    def get_discrete_rewards(self):
        if self.discrete_rewards!=0:
            self.curr_reward += self.discrete_rewards
            self.discrete_rewards = 0
        
    def collision_penalty(self,event):
        # self.discrete_rewards -= 75
        self.status = Simulator.Status.FAILED
        print("collision")
    
    def traffic_rules(self):
        curr_control = self.simulator.vehicle_controller.control
        if (self.simulator.traffic_light_state==0 and curr_control.reverse==False):
            if curr_control.throttle == 0:
                self.discrete_rewards += 10
            else:
                self.discrete_rewards -= curr_control.throttle * 50

    # def offroad(self):
    #     print("offroad")    

    

