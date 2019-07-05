
import drawing_library
import carla
import navigation_system
import math
import numpy as np
from agents.tools import misc
import pygame
import lane_ai
from enum import Enum
from collections import deque
from keras import Sequential
from keras.layers import Dense
from keras.optimizers import sgd,Adam
import os
import random
import reward_system
HIDDEN1_UNITS = 50
HIDDEN2_UNITS = 40

class ControlState(Enum):
    AI=1,
    MANUAL=2

class CollisionControl:

    def __init__(self,lane_ai):
        self.lane_ai = lane_ai
        self.lane_changer = lane_ai.lane_changer
        self.simulator = lane_ai.simulator
        self.state = ControlState.MANUAL
        self.environment = SpeedControlEnvironment(self)
        self.halt_time = pygame.time.get_ticks()

    def update(self):
        self.closest_obstacles = self.lane_ai.lane_closest
        self.apply_condtions()
    
    def apply_condtions(self):
        
        if self.lane_changer.state==lane_ai.State.LANE_CHANGE:
            self.disable_AI()
            self.lane_changing_halt()
            self.lane_changer.update_waypoint()

        elif self.lane_changer.state==lane_ai.State.RUNNING:
            if self.state==ControlState.AI:
                self.modify_by_AI()
            self.same_lane_halt()
            self.check_new_lane()

           
    
    def lane_changing_halt(self):
        target_lane_id = self.lane_changer.target_lane_id

        if target_lane_id in self.closest_obstacles:
            closest_obstacle = self.closest_obstacles[target_lane_id]
            if closest_obstacle.distance<7.5 and closest_obstacle.delta_d<0.005:
                self.halt()
            else:
                self.halt_time = pygame.time.get_ticks()
        self.same_lane_halt(distance=4)

    def same_lane_halt(self,distance=7.5):
        vehicle_lane_id = self.simulator.vehicle_variables.vehicle_waypoint.lane_id

        if vehicle_lane_id in self.closest_obstacles:
            closest_obstacle = self.closest_obstacles[vehicle_lane_id]
            if closest_obstacle.distance<distance and closest_obstacle.delta_d<0.005:
                self.halt()
            else:
                self.halt_time = pygame.time.get_ticks()
    
    def halt(self):
        curr =pygame.time.get_ticks()
        if (curr-self.halt_time)>300000:
            self.simulator.re_level()
            self.halt_time = curr
        else:
            self.disable_AI(failed=2)
            vel = self.simulator.vehicle_variables.vehicle_velocity_magnitude
            if vel>0.05:
                self.simulator.vehicle_controller.destroy_movement()
            control = self.simulator.vehicle_controller.control
            control.throttle = 0
            control.brake = 0.95
    
    def check_new_lane(self):
        vehicle_lane_id = self.simulator.vehicle_variables.vehicle_waypoint.lane_id

        if vehicle_lane_id in self.closest_obstacles:
            closest_obstacle = self.closest_obstacles[vehicle_lane_id]

            if 7.5<closest_obstacle.distance<30 and closest_obstacle.delta_d<0.005 :
                change_lane = self.lane_changer.check_new_lane(min_angle=150)
                if not change_lane:
                    self.enable_AI(closest_obstacle)

    
    def enable_AI(self,closest_obstacle):
        if self.state!=ControlState.AI:
            self.state = ControlState.AI
            self.environment.start(closest_obstacle)
            closest_obstacle.ai_follower = self
            print("Enabled AI")
    
    def disable_AI(self,failed=0):
        if self.state==ControlState.AI:
            self.state = ControlState.MANUAL
            self.environment.stop(failed)
            print("Disabled AI")

    def modify_by_AI(self):
        obstacle = self.environment.obstacle
        if obstacle.road_id!=self.environment.current_road:
            self.disable_AI()
        self.environment.ai.run_epoch()


class SpeedControlEnvironment:

    def __init__(self,collision_control):
        self.collision_control = collision_control
        # pass distance and delta_d
        # reward negative distance
        self.actions = [30,20,-20,-40,-60,-120,-140]
        self.ai = SpeedControlAI(self,state_size=2,action_size=7)

    def start(self,obstacle):
        self.obstacle = obstacle
        self.current_road = obstacle.road_id
        self.control = self.collision_control.simulator.vehicle_controller.control
        self.ai.reset()

    def stop(self,failed=0):
        
        self.ai.run_epoch(True,failed)
          

    def get_observation(self):
      
        return [self.obstacle.distance,self.obstacle.delta_d]
    
    def modify_control(self,action):

      
        mod = self.actions[action]
        if mod<-100:
            mod = abs(mod+100)/100
            self.control.brake = mod
        elif mod <0:
            mod = abs(mod)/100
            self.control.throttle*=mod
        else:
            mod+=100
            mod = mod/100
            self.control.throttle*=mod
        
        vel = self.collision_control.simulator.vehicle_variables.vehicle_velocity_magnitude
        extra =0
        obs = self.get_observation()

        if 8<self.obstacle.distance<10:
            return [self.get_observation(),obs[1]*30-obs[0]]
        else:
            return [self.get_observation(),-obs[0]]


class SpeedControlAI:

    def __init__(self,environment,state_size=3,action_size=6,save_file='save/model'):

        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=32*30)
        self.gamma = 0.95    # discount rate
        self.learning_rate=0.002
        self.running = True
        self.epsilon = 0.05  # exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.model = self.build_model()
        self.reward_tracker = reward_system.RewardTracker(self,2,70000,prefix='traffic_system')
        self.start =0
        self.load()
        self.save_file = save_file
        self.environment = environment
        self.prev_state = None
        self.batch_size =32
        self.step =0
        
    def build_model(self):

        model = Sequential()
        model.add(Dense(HIDDEN1_UNITS, input_dim=self.state_size, activation='tanh'))
        model.add(Dense(HIDDEN2_UNITS, input_dim=self.state_size, activation='tanh'))
        model.add(Dense(self.action_size, activation='softmax'))
        model.compile(loss = 'mse',optimizer = Adam(lr = self.learning_rate))
        print("built")
        return model


    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state):
        print(state)
        act_values = self.model.predict(state)
        return np.argmax(act_values[0])  # returns index value of o/p action

    def predict(self,state):
        state = np.reshape(state, [1, self.state_size])
        act_values = self.model.predict(state)
        return np.argmax(act_values[0])
        
    def replay(self, batch_size):

        minibatch = random.sample(self.memory, batch_size)
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                target = (reward + self.gamma *
                          np.amax(self.model.predict(next_state)[0]))
            target_f = self.model.predict(state)
            target_f[0][action] = target
            self.model.fit(state, target_f, epochs=1, verbose=0)
        # if self.epsilon > self.epsilon_min:
        #     self.epsilon *= self.epsilon_decay


    def load(self):
        self.episode =0
        last_model,episode,epsilon =self.reward_tracker.get_previous()
        if last_model:
            self.model.load_weights(os.path.join('traffic_system', 'save','models',last_model))
            print("Loaded",last_model)
            self.epsilon = epsilon
            self.episode = episode
            print(self.episode)
            print("Last completed episode : ",self.start)


    def reset(self):
        self.step = 0
        self.total_rewards = 0
        self.prev_state =np.reshape(self.environment.get_observation(),[1,self.state_size]) 

    def run_epoch(self,done=False,failed=0):
        batch_size = self.batch_size
        prev_state = self.prev_state
        action = self.act(prev_state)
        state,reward = self.environment.modify_control(action)

        if failed==0:
            print("Ending Normal")
        elif failed==2:
            reward -=abs(self.total_rewards)
            print("Halt end")
        else:
            print("Something wrong")
        state = np.reshape(state, [1, self.state_size])
        self.remember(prev_state, action, reward, state, done)

        if len(self.memory) > batch_size:
            self.replay(batch_size)

        self.prev_state = state
        self.total_rewards+=reward
        if not self.step%20:
            print(f"Step:{self.step}, Rewards: {self.total_rewards}")
        if done:
            self.reward_tracker.end_episode(self.total_rewards/(self.step+1))
            print(f"Complete Episode {self.episode}, Total Rewards: {self.total_rewards/(self.step+1)}")
            self.episode+=1
        self.step+=1

        return action

    # def train_model(self):

    #     done = False
    #     batch_size = 32
    #     EPISODES = 70000
    #     prev_rewards =0
    #     for e in range(self.start,EPISODES):
    #         state = self.simulator.reset() #change to initial state
    #         state = np.reshape(state, [1, self.state_size])
    #         self.total_rewards = 0
            
    #         for time in range(100):
    #             if not time%50:
    #                 pass
    #                 print(f"Step {time}, Rewards: {self.total_rewards}")
    #             # env.render()
    #             action = self.act(state) # self.act(state)
    #             # next_state, reward, done, _ = env.step(action)
    #             next_state,reward,done,_ = self.simulator.step(action) #check
    #             self.total_rewards += reward

    #             # reward = reward if not done else -10 #check
    #             next_state = np.reshape(next_state, [1, self.state_size])
    #             self.remember(state, action, reward, next_state, done)
    #             state = next_state
    #             if done:
    #                 break
    #             if len(self.memory) > batch_size:
    #                 self.replay(batch_size)
    #             if self.simulator.running==False:
    #                 self.running =False
    #                 break
                
    #         self.reward_tracker.end_episode(self.total_rewards)
    #         print(f"Complete Episode {e} , Epsilon: {self.epsilon}, Total Rewards: {self.total_rewards},Position: {self.simulator.navigation_system.curr_pos} / {len(self.simulator.navigation_system.ideal_route)} ")
            
    #         if self.running==False:
    #             break
    #         if e%30==0:
    #             if self.epsilon > self.epsilon_min:
    #                 self.epsilon *= self.epsilon_decay
    #         prev_rewards =self.total_rewards
    
        

