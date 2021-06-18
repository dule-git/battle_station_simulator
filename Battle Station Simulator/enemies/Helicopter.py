from enemies.ConstantVelocityEnemy import ConstantVelocityEnemy
import numpy as np

class Helicopter(ConstantVelocityEnemy):

    name = 'Helicopter'
    length = 8
    width = 3
    height = 3

    def __init__(self, kml_file, trajectory_id, on_height):
        self.name += str(trajectory_id)
        super().__init__(kml_file, on_height)

    def velocity_of_angle(self, angle):
        return 72

