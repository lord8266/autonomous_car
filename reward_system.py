import carla
import navigation_system
import Simulator
import math
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
        
        # print("Direction Penalty: %d"%(penalty),end=" ")
    
        # if (abs(offset)>110):
        #     penalty-= abs(offset)*1.5
        #     self.status =Simulator.Status.FAILED
        if (abs(offset)<30):
            self.curr_reward +=100
        else:
            penalty-= abs(offset)*1.5
        
        return penalty
        # need to add max offset
    

    def proximity_penalty(self):
        penalty =0
        l1 = self.simulator.vehicle_variables.vehicle_location
        l2 =self.simulator.navigation_system.local_route[1].location
        distance = navigation_system.NavigationSystem.get_distance(l1,l2,res=1)

        if distance<=2.5:
            penalty+=100*self.simulator.navigation_system.curr_pos
        else:
            penalty-= distance*2
        # print("Proximity Penalty: %d"%(penalty),end=" ")
        return penalty
        #need to add max distance

    def checkpoint_reward(self):
        reward = 0
        pos = self.simulator.navigation_system.curr_pos

        if pos==self.simulator.navigation_system.destination_index:
            # self.status = Simulator.Status.COMPLETED
            reward+=5000*pos
        elif pos>self.prev_pos:
            reward+=5000*pos
        elif pos<self.prev_pos:
            reward -=-500
        else:
            reward -= 20
            if self.simulator.vehicle_controller.control.throttle==0 and self.simulator.traffic_light_state==1:
                reward-=500

        # print("Checkpoint Reward: %d"%(reward),end=" " )
        
        self.prev_pos = pos
        return reward
            
    def update_rewards(self):
        self.curr_reward =0
        # checkpoint_reward =self.checkpoint_reward()
        # direction_reward =self.direction_penalty()
        # proximity_reward = self.proximity_penalty()
        # self.get_discrete_rewards()
        forward_reward = self.forward_reward()
        self.forward_reward_ = forward_reward
        # print(f"CheckPoint Reward: {checkpoint_reward}, Direction Reward: {direction_reward}, Proximity Reward: {proximity_reward}, Forward Reward: {forward_reward}\n")
        # print(f"Forward Reward: {forward_reward}")

        # self.curr_reward = checkpoint_reward+direction_reward+proximity_reward+forward_reward
        self.curr_reward = forward_reward
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

    def forward_reward(self):
        control = self.simulator.vehicle_controller.control
        angle = abs(self.simulator.observation[2])
        # velocity = control.throttle*5
        cos = math.cos( math.radians(angle) )
        sin = math.sin( math.radians(angle))
        velocity = control.throttle*(control.reverse==False and 1 or -1)*5
        # print(control.throttle)
        reward = velocity*(cos- sin) - self.simulator.observation[1]*3  
        return reward


        

    def get_discrete_rewards(self):
        reward = 0
        if self.discrete_rewards!=0:
            reward += self.discrete_rewards
            self.curr_reward += reward
            self.discrete_rewards = 0 

        # print("Discrete Reward: %d"%(reward),end=" " )
        
    def collision_penalty(self,event):

        self.discrete_rewards -= 75000*self.simulator.navigation_system.curr_pos
        # self.status = Simulator.Status.COMPLETED
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

    

