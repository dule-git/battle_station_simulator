from enemies.Enemy import Enemy

import numpy as np
import math

class ConstantVelocityEnemy(Enemy):

    def __init__(self, kml_file, on_height=0):
        super().__init__(kml_file, on_height)

    def calculate_trajectory_parameters(self):
        v = self.velocity_of_angle(-1)
        self.velocity = v * np.ones(len(self.x_coords))
        self.acceleration = np.zeros(len(self.x_coords))

        self.time = np.array([])
        for distance in self.travelled_distance:
            self.time = np.append(self.time, distance / v)
