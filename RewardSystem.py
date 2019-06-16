import carla
import route
class RewardSystem:

    def __init__(self,end_transform):
        RewardSystem.ref  = self
        self.actor_transform = None
        self.waypoint_transform = None
        self.curr_reward = 0
        self.max_rot_offset = 50/360
        self.done = False
        self.end_transform = end_transform

    def update_data(self,actor_transform,waypoint_transform):
        self.actor_transform = actor_transform
        self.waypoint_transform = waypoint_transform
    
    def set_rotation_reward(self):

        offset = abs(self.actor_transform.rotation.yaw - self.waypoint_transform.rotation.yaw)
        if offset>self.max_rot_offset:
            self.done =True
        else:
            self.curr_reward += -offset/3 # temporary
        
    def set_distance_reward(self):

        d = route.Route.get_distance(self.waypoint_transform.location,self.actor_transform.location,res=0)

        if d>=2.7:
            self.done = True
        else:
            self.curr_reward += -d*10 # temporary
    
    def update_rewards(self):
        self.curr_reward =0
        self.set_distance_reward()
        self.set_rotation_reward()
        return self.done,self.curr_reward

    def reset(self):
        self.curr_reward = 0
        self.done =False

        
