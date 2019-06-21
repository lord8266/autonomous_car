
import carla
import math
class Util(object):

    @staticmethod
    def blits(destination_surface, source_surfaces, rect=None, blend_mode=0):
        for surface in source_surfaces:
            destination_surface.blit(surface[0], surface[1], rect, blend_mode)

    @staticmethod
    def length(v):
        return math.sqrt(v.x**2 + v.y**2 + v.z**2)

    @staticmethod
    def get_bounding_box(actor):
        bb = actor.trigger_volume.extent
        corners = [carla.Location(x=-bb.x, y=-bb.y),
                   carla.Location(x=bb.x, y=-bb.y),
                   carla.Location(x=bb.x, y=bb.y),
                   carla.Location(x=-bb.x, y=bb.y),
                   carla.Location(x=-bb.x, y=-bb.y)]
        corners = [x + actor.trigger_volume.location for x in corners]
        t = actor.get_transform()
        t.transform(corners)
        return corners
    
class SensorManager():

    def __init__(self,simulator):
        self.simulator =simulator
        self.traffic_lights = simulator.world.get_actors().filter('traffic.traffic_light')
        
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
        self.collision_sensor.listen(lambda event: self.simulator.reward_system.collision_penalty(event))
    
    def initialize_lane_invasion_sensor(self):
        lane_invasion_sensor_blueprint = self.simulator.blueprint_library.find('sensor.other.lane_invasion')
        self.lane_invasion_sensor = self.simulator.world.spawn_actor(lane_invasion_sensor_blueprint,carla.Transform(),attach_to=self.simulator.vehicle_controller.vehicle)
        self.lane_invasion_sensor.listen(lambda event: self.simulator.reward_system.lane_invasion_penalty(event))

    def stop_camera(self):
        self.camera.stop()

    def traffic_light_sensor(self):
        vehicle =self.simulator.vehicle_controller.vehicle

        

        for traffic_light in self.traffic_lights:
            trigger = traffic_light.trigger_volume
            traffic_light.get_transform().transform(trigger.location)

            # Calculate box intersection (rough approximation).
            distance_to_car = trigger.location.distance(vehicle.get_location())
            s = Util.length(trigger.extent) +Util.length(vehicle.bounding_box.extent)
            if distance_to_car <= s:
                sta = str(traffic_light.get_state())
                # print("found a traffic light with state %s\n"%(str(sta)) )
                if sta == "Red":
                    return 0
                return 1

        return 1
