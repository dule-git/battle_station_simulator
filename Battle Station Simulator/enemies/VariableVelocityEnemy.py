from enemies.Enemy import Enemy

import numpy as np
import math

class VariableVelocityEnemy(Enemy):

    def __init__(self, kml_file):
        super().__init__(kml_file)

    # calculating trajectory parameters like:
    # --> angle of each turn
    # --> maximum velocity for each turn based on its angle#
    # --> acceleration and time for that section of the trajectory
    def calculate_trajectory_parameters(self):
        self.velocity = np.array([0])
        self.acceleration = np.array([])
        self.time = np.array([])
        for i in range(1, len(self.x_coords) - 1):
            
            v = self.get_velocity_for_turn(i)

            self.velocity = np.append(self.velocity, v)
            self.acceleration = np.append(
                self.acceleration,
                (math.pow(self.velocity[-1], 2) - math.pow(self.velocity[-2], 2)) / (2 * self.travelled_distance[i - 1]))
            self.time = np.append(
                self.time,
                (self.velocity[-1] - self.velocity[-2]) / self.acceleration[-1])
        
        self.velocity[-1] = 0
        self.acceleration[-1] = (math.pow(self.velocity[-1], 2) - math.pow(self.velocity[-2], 2)) / (2 * self.travelled_distance[i - 1])
        self.time[-1] = (self.velocity[-1] - self.velocity[-2]) / self.acceleration[-1]
    
    def get_velocity_for_turn(self, i):
        x1, y1, x2, y2 = 0, 0, 0, 0
        x0, y0 = self.x_coords[i], self.y_coords[i]
        if (self.x_coords[i - 1] <= self.x_coords[i + 1]):
            x1 = self.x_coords[i - 1] - x0
            y1 = self.y_coords[i - 1] - y0
            x2 = self.x_coords[i + 1] - x0
            y2 = self.y_coords[i + 1] - y0
        else:
            x1 = self.x_coords[i + 1] - x0
            y1 = self.y_coords[i + 1] - y0
            x2 = self.x_coords[i - 1] - x0
            y2 = self.y_coords[i - 1] - y0
        x0 = 0
        y0 = 0

        k1 = (y1 - y0) / (x1 - x0)
        k2 = (y2 - y0) / (x2 - x0)

        theta = math.atan(abs((k2 - k1) / (1 + k2 * k1)))
        v = -1

        while (v == -1):
            if (x1 <= 0 and y1 >= 0 and x2 <= 0 and y2 >= 0):
                v = self.velocity_of_angle(theta)
            elif (x1 <= 0 and y1 >= 0 and x2 >= 0 and y2 >= 0):
                if (k1 * k2 <= -1):
                    v = self.velocity_of_angle(theta)
                else:
                    v = self.velocity_of_angle(math.pi - theta)
            elif (x1 <= 0 and y1 >= 0 and x2 >= 0 and y2 <= 0):
                v = self.velocity_of_angle(math.pi - theta)
            elif (x1 <= 0 and y1 >= 0 and x2 <= 0 and y2 <= 0):
                if (k1 * k2 <= -1):
                    v = self.velocity_of_angle(math.pi - theta)
                else:
                    v = self.velocity_of_angle(theta)
            elif (x1 >= 0 and y1 >= 0 and x2 >= 0 and y2 >= 0):
                v = self.velocity_of_angle(theta)
            elif (x1 >= 0 and y1 >= 0 and x2 >= 0 and y2 <= 0):
                if (k1 * k2 <= -1):
                    v = self.velocity_of_angle(math.pi - theta)
                else:
                    v = self.velocity_of_angle(theta)
            elif (x1 <= 0 and y1 <= 0 and x2 >= 0 and y2 >= 0):
                v = self.velocity_of_angle(math.pi - theta)
            elif (x1 >= 0 and y1 <= 0 and x2 >= 0 and y2 <= 0):
                v = self.velocity_of_angle(theta)
            elif (x1 <= 0 and y1 <= 0 and x2 >= 0 and y2 <= 0):
                if (k1 * k2 <= -1):
                    v = self.velocity_of_angle(theta)
                else:
                    v = self.velocity_of_angle(math.pi - theta)
            elif (x1 <= 0 and y1 <= 0 and x2 <= 0 and y2 <= 0):
                v = self.velocity_of_angle(theta)
            else:
                x1, x2 = x2, x1
                y1, y2 = y2, y1
        
        return v
