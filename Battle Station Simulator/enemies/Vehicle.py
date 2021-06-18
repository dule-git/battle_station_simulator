from enemies.VariableVelocityEnemy import VariableVelocityEnemy
import numpy as np
import math

class Vehicle(VariableVelocityEnemy):

    name = 'Vehicle'
    length = 5 
    width = 2 
    height = 1.5 

    def __init__(self, kml_file, trajectory_id):
        self.name += str(trajectory_id)
        super().__init__(kml_file)

    def velocity_of_angle(self, angle):
        return angle * 10
