
import carla
class SensorManager():

    def __init__(self,simulator):
        self.simulator =simulator
    
    def initialize_camera(self):
        camera_blueprint  = self.simulator.blueprint_library.find('sensor.camera.rgb')
        camera_blueprint.set_attribute('image_size_x', '640')
        camera_blueprint.set_attribute('image_size_y', '480')
        spawn_transform = carla.Transform(carla.Location(x=-7.5, z=5.8),carla.Rotation(pitch=-29))
        self.camera = self.simulator.world.spawn_actor(camera_blueprint,spawn_transform,attach_to=self.simulator.vehicle_controller.vehicle)
        self.camera.listen(lambda image: self.simulator.game_manager.camera_callback(image))
    
    def initialize_collision_sensor(self):
        collision_sensor_blueprint = self.simulator.blueprint_library.find('sensor.other.collision')
        self.collision_sensor = self.simulator.world.spawn_actor(collision_sensor_blueprint,carla.Transform(),attach_to=self.simulator.vehicle_controller.vehicle)
        # self.collision_sensor.listen(lambda event: print("hi"))

    def stop_camera(self):
        self.camera.stop()
