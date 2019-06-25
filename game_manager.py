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
        self.surface = None
        self.prev = pygame.time.get_ticks()
        self.draw_periodic = False

    def initialize_pygame(self,resolution):
        pygame.init()
        self.display = pygame.display.set_mode(resolution,pygame.HWSURFACE | pygame.DOUBLEBUF)
    
    def render(self):
        if self.new_frame:
            self.display.blit(self.surface, (0, 0))
            self.new_frame =False 
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

                if event.key==pygame.K_r:
                    self.simulator.switch_render()

                if event.key ==pygame.K_q:
                    self.simulator.reward_system.status = Simulator.Status.COMPLETED
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
        self.surface = pygame.surfarray.make_surface(array.swapaxes(0, 1))
        self.new_frame =True
        



