import carla
import navigation_system
class RewardSystem:

    def __init__(self,simulator):

        self.simulator = simulator
        self.curr_reward = 0
        self.max_rot_offset = 90 
        self.done = False
        self.prev_pos = self.simulator.navigation_system.curr_pos
        
        self.count = 0

    

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
     
        return self.curr_reward,self.done

    def reset(self):
        self.curr_reward = 0
        self.done =False
        self.d =0

    @staticmethod
    def lane_invade():
        print("lane invation")

    
    def collision_event(self):
        print("collision")
    
    def traffic_rules(self):
        print("traffic rules")
    
    def offroad(self):
        print("offroad")    

        

