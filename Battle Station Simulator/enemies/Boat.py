from enemies.VariableVelocityEnemy import VariableVelocityEnemy
import numpy as np

class Boat(VariableVelocityEnemy):

    name = 'Boat'
    length = 10
    width = 3
    height = 3

    def __init__(self, kml_file, trajectory_id):
        self.name += str(trajectory_id)
        super().__init__(kml_file)

    def velocity_of_angle(self, angle):
        return angle * 5

    




    

    