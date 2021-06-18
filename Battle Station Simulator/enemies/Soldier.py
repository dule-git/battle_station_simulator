from enemies.ConstantVelocityEnemy import ConstantVelocityEnemy
import numpy as np

class Soldier(ConstantVelocityEnemy):

    name = 'Soldier'
    length = 0.5
    width = 0.5
    height = 2
    
    def __init__(self, kml_file, trajectory_id):
        self.name += str(trajectory_id)
        super().__init__(kml_file)

    def velocity_of_angle(self, angle):
        return 2.5
