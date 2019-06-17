import carla
import route
class RewardSystem:

    def __init__(self,end_transform,simulator):
        RewardSystem.ref  = self
        self.actor_transform = None
        self.waypoint_transform = None
        self.curr_reward = 0
        self.max_rot_offset = 40 / 180
        self.done = False
        self.end_transform = end_transform
        self.route = simulator.route
        self.prev_pos = self.route.curr_pos
        self.simulator = simulator
        RewardSystem.ref =self
    def update_data(self,actor_transform,waypoint_transform):
        self.actor_transform = actor_transform
        self.waypoint_transform = waypoint_transform
    
    def set_rotation_reward(self):

        offset = (self.actor_transform.rotation.yaw - self.waypoint_transform.rotation.yaw) 
        
        offset%=360
       
        offset = route.Route.scale_angle(offset)
        
        if abs(offset)>self.max_rot_offset:
            print(f'done as offset is {offset}')
            self.done =True
        else:
            self.curr_reward += -offset*7 # temporary
        
    def set_distance_reward(self):
        
        d = route.Route.get_distance(self.waypoint_transform.location,self.actor_transform.location,res=1)
        # p1 = self.simulator.route.dynamic_path[0].location
        # p2 = self.simulator.route.dynamic_path[1].location
        # ac = self.actor_transform.location
        # a = (p2.y-p1.y)/(p2.x-p1.x)
        # b=-1
        # c = p1.y+a*p1.x
        # d = abs(a*ac.x + b*ac.y + c)/(a**2+1)**0.5
        # print(d)
        # self.d = d
        if d>=1.5:
            # self.done = True
            print(f'done as distance is {d}')
        else:
            self.curr_reward += -d*30 # temporary

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
        self.set_distance_reward()
        self.set_rotation_reward()
        self.checkpoint_reward()
        # print("update reward by %d"%(self.curr_reward))
        return self.done,self.curr_reward

    def reset(self):
        self.curr_reward = 0
        self.done =False
        self.d =0

    @staticmethod
    def lane_invade():
        print("lane invasion")
        

