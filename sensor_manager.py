
import carla
class SensorManager():

    def __init__(self,simulator):
        self.simulator =simulator
        
    def initialize_rgb_camera(self):
        camera_blueprint  = self.simulator.blueprint_library.find('sensor.camera.rgb')
        camera_blueprint.set_attribute('image_size_x', '640')
        camera_blueprint.set_attribute('image_size_y', '480')
        spawn_transform = carla.Transform(carla.Location(x=-7.5, z=5.8),carla.Rotation(pitch=-29))
        self.camera = self.simulator.world.spawn_actor(camera_blueprint,spawn_transform,attach_to=self.simulator.vehicle_controller.vehicle)
        
    
    def initialize_semantic_camera(self):
        semantic_blueprint  = self.simulator.blueprint_library.find('sensor.camera.semantic_segmentation')
        semantic_blueprint.set_attribute('image_size_x', '640')
        semantic_blueprint.set_attribute('image_size_y', '480')
        spawn_transform = carla.Transform(carla.Location(x=-7.5, z=5.8),carla.Rotation(pitch=-29))
        self.semantic_camera = self.simulator.world.spawn_actor(semantic_blueprint,spawn_transform,attach_to=self.simulator.vehicle_controller.vehicle)
        

    def initialize_collision_sensor(self):
        collision_sensor_blueprint = self.simulator.blueprint_library.find('sensor.other.collision')
        self.collision_sensor = self.simulator.world.spawn_actor(collision_sensor_blueprint,carla.Transform(),attach_to=self.simulator.vehicle_controller.vehicle)
        self.collision_sensor.listen(lambda event: self.simulator.reward_system.collision_event(event))
    
    def initialize_lane_invasion_sensor(self):
        lane_invasion_sensor_blueprint = self.simulator.blueprint_library.find('sensor.other.lane_invasion')
        self.lane_invasion_sensor = self.simulator.world.spawn_actor(lane_invasion_sensor_blueprint,carla.Transform(),attach_to=self.simulator.vehicle_controller.vehicle)
        self.lane_invasion_sensor.listen(lambda event: self.simulator.reward_system.lane_invasion_event(event))

    def stop_camera(self):
        self.camera.stop()
