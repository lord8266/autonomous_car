import carla
import navigation_system
import Simulator
import math
import numpy as np
import matplotlib.pyplot as plt
import os
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
    
    def state_change_penalty(self):
        if self.simulator.vehicle_controller.changed_state:
            # print("state changed")
            return 7
        else:
            return 0

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

    def checkpoint(self):
        reward = 0
        pos = self.simulator.navigation_system.curr_pos

        if pos==self.simulator.navigation_system.destination_index:
            self.simulator.new_path()
            self.status = Simulator.Status.RESTART
       
        if pos>self.prev_pos:
            reward = 200
            self.status = Simulator.Status.COMPLETED
        # elif pos<self.prev_pos:
        #     reward -=-500
        # else:
        #     reward -= 20
        #     if self.simulator.vehicle_controller.control.throttle==0 and self.simulator.traffic_light_state==1:
        #         reward-=500

        # print("Checkpoint Reward: %d"%(reward),end=" " )
        
        self.prev_pos = pos
        return reward
        
            
    def update_rewards(self):
        self.curr_reward =0
        self.curr_reward+= self.checkpoint()
        # direction_reward =self.direction_penalty()
        # proximity_reward = self.proximity_penalty()
        # discrete = self.get_discrete_rewards()
        # # +discrete
        self.curr_reward -= self.simulator.observation[1]*5
        self.curr_reward -= abs(self.simulator.observation[0]*3)
        self.curr_reward -= abs(self.simulator.observation[2])*2
        # self.curr_reward -= self.state_change_penalty()

        # print(f"CheckPoint Reward: {checkpoint_reward}, Direction Reward: {direction_reward}, Proximity Reward: {proximity_reward}, Forward Reward: {forward_reward}\n")
        # print(f"Forward Reward: {forward_reward}")

        # self.curr_reward = checkpoint_reward+direction_reward+proximity_reward+forward_reward



        return self.curr_reward,self.status

    def reset(self,t=0):
        if t:
            self.prev_pos =0

        self.curr_reward = 0
        self.status = Simulator.Status.RUNNING


    
    def lane_invasion_penalty(self,event):
        lane_types = set( str(x.type) for x in event.crossed_lane_markings)
        if  "Solid" in lane_types or "SolidSolid" in lane_types or "BrokenSolid" in lane_types:
            # print("wrong lane")
            self.discrete_rewards -= 50
            # self.status = Simulator.Status.FAILED

    def forward_reward(self):
        control = self.simulator.vehicle_controller.control
        # velocity = control.throttle*5
        cos = self.simulator.observation[-2]
        sin = self.simulator.observation[-1]
        velocity = control.throttle*(control.reverse==False and 1 or -1)*5
        # print(control.throttle)
        reward = velocity*(sin) 
        return reward


        

    def get_discrete_rewards(self):
        reward = 0
        if self.discrete_rewards!=0:
            reward += self.discrete_rewards
            self.curr_reward += reward
            self.discrete_rewards = 0 
        return self.discrete_rewards
        # print("Discrete Reward: %d"%(reward),end=" " )
        
    def collision_penalty(self,event):

        # r =self.simulator.ai_model.total_rewards
        # self.discrete_rewards += ( r >0 and -1 or 1 )*r*4
        # self.status = Simulator.Status.COMPLETED
        print("collision")
        # self.simulator.on_failure()

    def traffic_rules(self):
        curr_control = self.simulator.vehicle_controller.control
        if (self.simulator.traffic_light_state==0 and curr_control.reverse==False):
            if curr_control.throttle == 0:
                self.discrete_rewards += 10
            else:
                self.discrete_rewards -= curr_control.throttle * 50

    # def offroad(self):
    #     print("offroad")    

    

class RewardTracker:

    def __init__(self,ai_model,batch_size=20,size=1000):
        self.ai_model = ai_model
        self.batch_size =batch_size
        self.reward_buffer = np.zeros(batch_size)
        self.ep_rewards = {'avg':np.zeros( int(np.ceil(size/batch_size))-1 ),'min':np.zeros( int(np.ceil(size/batch_size))-1),'max':np.zeros(int(np.ceil(size/batch_size))-1) }
        self.get_prev_graph()
        self.size = size
        self.curr_episode =0 
        self.model_offset =0
        
    def end_episode(self,score):
        
        if not self.curr_episode%self.batch_size and self.curr_episode!=0:
            self.ep_rewards['avg'][self.curr_episode//self.batch_size-1] =   np.average(self.reward_buffer)
            self.ep_rewards['min'][self.curr_episode//self.batch_size-1] =   np.min(self.reward_buffer)
            self.ep_rewards['max'][self.curr_episode//self.batch_size-1] =   np.max(self.reward_buffer)
            self.reward_buffer[:] =0
            self.save_data()
        self.reward_buffer[self.curr_episode%self.batch_size] = score
        self.curr_episode+=1
    
    def save_data(self):
        print("Save data")
        data = np.array( self.ep_rewards['avg'])
        np.save('save/graphs/reward_data_avg',data)

        data = np.array( self.ep_rewards['min'])
        np.save('save/graphs/reward_data_min',data)

        data = np.array( self.ep_rewards['max'])
        np.save('save/graphs/reward_data_max',data)
        f_name = f'save/models/model{self.curr_episode}'
        self.ai_model.model.save_weights(f_name+".data")
        f = open(f_name+".conf",'w')
        f.write(f'{self.curr_episode} {self.ai_model.epsilon}')
        f.close()

    def get_previous(self):
        models = list(filter(lambda f:".data" in f,os.listdir('save/models')))
        if models:
            model_max = max(models,key=lambda f: int(f[5:f.find('.')]))
            # model_name = []
            # for i in models:
            #     tok,_ = i.split(".")
            #     val = tok[5:]
            f = open("save/models/" +model_max[:-5]+".conf")
            ep,epsilon = f.read().split()
            print(ep,epsilon)
            self.curr_episode = int(ep)
            return model_max,int(ep),float(epsilon)
        else:
            return "",0,0
    
    def get_prev_graph(self):
        path = 'save/graphs'
        files = os.listdir( path)
        if 'reward_data_max.npy' in files:
            self.ep_rewards['max'] = np.load(os.path.join(path,'reward_data_max.npy'))
        if 'reward_data_avg.npy' in files:
            self.ep_rewards['avg'] = np.load(os.path.join(path,'reward_data_avg.npy'))
        if 'reward_data_min.npy' in files:
            self.ep_rewards['min'] = np.load(os.path.join(path,'reward_data_min.npy'))
        
    def plot_data(self):
        plt.plot(np.arange(len(self.ep_rewards['avg']))*self.batch_size,self.ep_rewards['avg'],label='avg')
        plt.plot(np.arange(len(self.ep_rewards['avg']))*self.batch_size,self.ep_rewards['min'],label='min')
        plt.plot(np.arange(len(self.ep_rewards['avg']))*self.batch_size,self.ep_rewards['max'],label='max')
        plt.legend(loc='lower right')