#pylint: disable=no-member
import carla 
import pygame
import enum
import numpy as np
class Type(enum.Enum):
    AUTO=0
    MANUAL = 1

class GameLoop:

    def __init__(self,simulator,camera,controller,route):
        pygame.init()
        self.camera =camera
        self.new_frame = False
        self.vehicle_controller =  controller
        self.type = Type.AUTO
        GameLoop.ref = self
        self.surface = None
        self.running =True
        self.route = route
        self.display = pygame.display.set_mode(
            (640 ,480),
            pygame.HWSURFACE | pygame.DOUBLEBUF)
        camera.listen(GameLoop.frame_call_back)
        self.prev_time = pygame.time.get_ticks()
        self.curr_time = self.prev_time
        self.simulator = simulator

    @staticmethod
    def frame_call_back(image):
        image.convert(carla.ColorConverter.Raw)
        array = np.frombuffer(image.raw_data, dtype=np.dtype("uint8"))
        array = np.reshape(array, (image.height, image.width, 4))
        array = array[:, :, :3]
        array = array[:, :, ::-1]
        GameLoop.ref.surface = pygame.surfarray.make_surface(array.swapaxes(0, 1))
        GameLoop.ref.new_frame =True
    
    def render(self):
        if self.new_frame:
            self.display.blit(self.surface, (0, 0))
            self.new_frame =False # auto synchronize with server
        pygame.display.flip()
    
    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_p]:
            self.route.draw_vehicle_waypoint()
        self.vehicle_controller.control_by_input()
    
    def run(self):

        self.curr_time = pygame.time.get_ticks()
        t = self.curr_time-self.prev_time + np.finfo(float).eps
        # print(1000/(t))
        self.prev_time =self.curr_time
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running =False
            if event.type== pygame.KEYDOWN:
                if event.key==pygame.K_o:
                    self.simulator.switch_input()
                    

        # self.update()
        self.render()




