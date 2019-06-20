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
        penalty =0
        offset = self.simulator.observation[2]
        penalty-= abs(offset)*20
        print("Direction Penalty: %d"%(penalty),end=" ")
        self.curr_reward +=penalty
        # need to add max offset
    
    def proximity_penalty(self):
        penalty =0
        l1 = self.simulator.vehicle_variables.vehicle_location
        l2 =self.simulator.navigation_system.local_route[1].location
        penalty -=navigation_system.NavigationSystem.get_distance(l1,l2,res=1)*30
        print("Proximity Penalty: %d"%(penalty),end=" ")
        self.curr_reward+=penalty
        #need to add max distance

    def checkpoint_reward(self):
        reward = 0
        pos = self.simulator.navigation_system.curr_pos

        if pos==self.simulator.navigation_system.destination_index:
            self.status = Simulator.Status.COMPLETED
            reward+=75
        elif pos>self.prev_pos:
            reward+=20
        elif pos<self.prev_pos:
            reward -=-50
        else:
            reward -= 5

        print("Checkpoint Reward: %d"%(reward),end=" " )
        self.curr_reward+=reward
        self.prev_pos = pos
            
    def update_rewards(self):
        self.curr_reward =0
        self.checkpoint_reward()
        self.direction_penalty()
        self.proximity_penalty()
        self.get_discrete_rewards()
        print()
        return self.curr_reward,self.status

    def reset(self):
        self.curr_reward = 0
        self.prev_pos = 0
        self.status = Simulator.Status.RUNNING
        self.d =0

    
    def lane_invasion_penalty(self,event):
        lane_types = set( str(x.type) for x in event.crossed_lane_markings)
        if  "Solid" in lane_types or "SolidSolid" in lane_types or "BrokenSolid" in lane_types:
            # print("wrong lane")
            self.discrete_rewards -= 50
            # self.status = Simulator.Status.FAILED

    def get_discrete_rewards(self):
        reward = 0
        if self.discrete_rewards!=0:
            reward += self.discrete_rewards
            self.curr_reward += reward
            self.discrete_rewards = 0 

        print("Discrete Reward: %d"%(reward),end=" " )
        
    def collision_penalty(self,event):
        # self.discrete_rewards -= 75
        self.status = Simulator.Status.FAILED
        # print("collision")
    
    def traffic_rules(self):
        curr_control = self.simulator.vehicle_controller.control
        if (self.simulator.traffic_light_state==0 and curr_control.reverse==False):
            if curr_control.throttle == 0:
                self.discrete_rewards += 10
            else:
                self.discrete_rewards -= curr_control.throttle * 50

    # def offroad(self):
    #     print("offroad")    

    

