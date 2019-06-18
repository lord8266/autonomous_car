import carla
import route
class RewardSystem:

    def __init__(self,end_transform,simulator):
        RewardSystem.ref  = self
        self.actor_transform = None
        self.waypoint_transform = None
        self.curr_reward = 0
        self.max_rot_offset = 90 / 180
        self.done = False
        self.end_transform = end_transform
        self.route = simulator.route
        self.prev_pos = self.route.curr_pos
        self.simulator = simulator
        self.count = 0
        RewardSystem.ref =self
    def update_data(self,actor_transform,waypoint_transform):
        self.actor_transform = actor_transform
        self.waypoint_transform = waypoint_transform
    

    def checkpoint_reward(self):
        pos = self.route.curr_pos
        if pos>self.prev_pos:
            self.curr_reward+=20
            # print("reach point %d" %(pos))
        elif pos<self.prev_pos:
            self.curr_reward -=-50
        else:
            self.curr_reward -= 5.6
            
        self.prev_pos = pos
            
    def update_rewards(self):
        self.curr_reward =0
        self.checkpoint_reward()
        # self.lane_invade()
        # self.traffic_rules()
        # self.collision_with()
        # self.offroad()

        # print("update reward by %d"%(self.curr_reward))
        return self.done,self.curr_reward

    def reset(self):
        self.curr_reward = 0
        self.done =False
        self.d =0

    @staticmethod
    def lane_invade(text):
        print("lane invation - ",text)

        if text == "'Solid'" or text == "'SolidSolid'" or text == "'BrokenSolid'":
            print("wrong lane")
        # r1 = self.actor_transform.rotation.yaw%360  
        # r2 = self.waypoint_transform.rotation.yaw%360
        # offset = abs(r1-r2)
        # if offset>90:
        #     self.count+=1
        #     print("lane invaded", self.count)
        #     self.curr_reward += 20

        # self.curr_reward += -offset*7 # temporary

    @staticmethod
    def collision_with():
        RewardSystem.ref.done = True
        print("collision")
    
    def traffic_rules(self):
        print("traffic rules")
    
    def offroad(self):
        print("offroad")    

        

