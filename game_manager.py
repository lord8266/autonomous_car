#pylint: disable=no-member
import carla 
import pygame
import enum
import numpy as np
import drawing_library
import Simulator
class GameManager:

    def __init__(self,simulator,resolution=(640,480)):
        self.initialize_pygame(resolution)
        self.simulator = simulator
        self.new_frame = False
        self.new_frame2 =False
        self.surface = None
        self.surface2 =None
        self.prev = pygame.time.get_ticks()
        self.draw_periodic = False
        self.color_density = Density(simulator)
    def initialize_pygame(self,resolution):
        pygame.init()
        self.display = pygame.display.set_mode(resolution,pygame.HWSURFACE | pygame.DOUBLEBUF)
    
    def render(self):
        if self.new_frame:
            self.display.blit(self.surface, (0, 0))
            self.new_frame =False 
        if self.new_frame2:
            self.display.blit(self.surface2, (0, 0))
            self.new_frame2 =False 
        pygame.display.flip()
    
    def update(self):
        self.keys = pygame.key.get_pressed()
        self.handle_events()
        curr = pygame.time.get_ticks()
        if (curr-self.prev)>1300:
            self.draw_green_line()
            self.prev = curr
    
    def draw_green_line(self):
        if self.draw_periodic:
            drawing_library.draw_arrows(self.simulator.world.debug,[i.location for i in self.simulator.navigation_system.local_route],color=carla.Color(0,255,0),life_time=0.5)

    def handle_events(self):
        for event in pygame.event.get():

            if event.type==pygame.QUIT:
                self.simulator.running =False

            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_o:
                    self.simulator.switch_input()

                if event.key==pygame.K_p:
                    self.draw_periodic = not self.draw_periodic
                    print("curr_pos is %d"%(self.simulator.navigation_system.curr_pos))
                
                if event.key==pygame.K_c:
                    self.simulator.camera_switch()

                if event.key==pygame.K_a:
                    
                    f= open('density.txt','a')
                    density = len(self.array[self.array==[0, 0, 142 ]])//3
                    f.write(str(density)+"\n")
                    f.close()

                if event.key ==pygame.K_q:
                    self.simulator.reward_system.status = Simulator.Status.COMPLETED
                
                if event.key==pygame.K_l:
                    self.simulator.lane_ai.request_new_lane(prefer_left=True)

                if event.key==pygame.K_r:
                   self.simulator.lane_ai.request_new_lane(prefer_left=False)
                   
            
    def print_waypoint(self,waypoint):
        print("transform :",waypoint.transform)
        print("lane width :",waypoint.lane_width)
        print("roadid :",waypoint.road_id)
        print("section id :",waypoint.section_id)
        print("lane id :",waypoint.lane_id)
        print("lane change :",waypoint.lane_change) 
        print("lane type :",waypoint.lane_type) 
        print("right mark :",waypoint.right_lane_marking) 
        print("left mark :",waypoint.left_lane_marking)

    def camera_callback(self,image):
        image.convert(carla.ColorConverter.Raw)
        array = np.frombuffer(image.raw_data, dtype=np.dtype("uint8"))
        array = np.reshape(array, (image.height, image.width, 4))
        array = array[:, :, :3]
        array = array[:, :, ::-1]
        self.surface = pygame.surfarray.make_surface(array.swapaxes(0, 1))
        self.new_frame =True
    
    def semantic_callback(self,image):
        image.convert(carla.ColorConverter.CityScapesPalette)
        array = np.frombuffer(image.raw_data, dtype=np.dtype("uint8"))
        array = np.reshape(array, (image.height, image.width, 4))
        array = array[:, :, :3]
        array = array[:, :, ::-1]
        self.array = array.reshape(-1,3)
        self.surface2 = pygame.surfarray.make_surface(array.swapaxes(0, 1))
        self.new_frame2 =True
        self.color_density.add_density(self.array)
        # print(self.color_density.get_offset())
        # print(self.color_density.buffer)

    def get_density(self):
        density_road = sum(np.all(self.array==[128,64,128],axis=1)) +sum(np.all(self.array==[157, 234, 50],axis=1))
        density_car = sum(np.all(self.array==[0,0,142],axis=1))
        print(f'Road: {density_road}, Car:{density_car}')


class Density:

    def __init__(self,simulator):
        self.simulator = simulator
        self.buffer = []
        self.curr_len = 0
        self.max_len =10

    def add_density(self,array):
        density = self.make_density(array)
        if len(self.buffer)>(self.max_len-1):
            self.buffer = self.buffer[1:]
        self.buffer.append(density)

    def make_density(self,array):
        density_road = sum(np.all(array==[128,64,128],axis=1)) +sum(np.all(array==[157, 234, 50],axis=1))
        density_car = sum(np.all(array==[0,0,142],axis=1))
        return density_road,density_car
    
    def get_offset(self):
        print(len(self.buffer))
        if len(self.buffer)==self.max_len:
            return (self.buffer[59][0]-self.buffer[0][0]),(self.buffer[59][1]-self.buffer[0][1])
        else:
            return 0,0

