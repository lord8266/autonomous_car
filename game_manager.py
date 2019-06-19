#pylint: disable=no-member
import carla 
import pygame
import enum
import numpy as np
import drawing_library

class GameManager:

    def __init__(self,simulator,resolution=(640,480)):
        self.initialize_pygame(resolution)
        self.simulator = simulator
        self.new_frame = False
        self.surface = None

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
    
    def handle_events(self):
        for event in pygame.event.get():

            if event.type==pygame.QUIT:
                self.simulator.running =False

            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_o:
                    self.simulator.switch_input()
                if event.key==pygame.K_p:
                    self.simulator.navigation_system.make_local_route()
                    drawing_library.draw_arrows(self.simulator.world.debug,[i.location for i in self.simulator.navigation_system.local_route],color=carla.Color(0,255,0),life_time=0.7) #temporary
                    print("curr_pos is %d"%(self.simulator.navigation_system.curr_pos))
                if event.key==pygame.K_c:
                    self.simulator.camera_switch()
    
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
        



