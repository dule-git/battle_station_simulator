import math
import numpy as np
from matplotlib.patches import Rectangle

class EO_System:
    
    MIN_FOV_H = math.radians(1.67)
    MIN_FOV_V = math.radians(1.67)


    SCREEN_WIDTH = 640
    SCREEN_HEIGHT = 640

    MAX_DISTANCE = 20000

    def __init__(self, target):
        self.target = target
        self.fov_h = EO_System.MIN_FOV_H
        self.fov_v = EO_System.MIN_FOV_V

        x, y, z = self.target.curr_x, self.target.curr_y, self.target.curr_z
        self.distance_xy = math.sqrt(math.pow(x, 2) + math.pow(y, 2))
        self.distance = math.sqrt(math.pow(self.distance_xy, 2) + math.pow(z, 2))
        self.azimuth = math.atan2(y, x)
        self.elevation = math.asin(z / self.distance)

    def update(self):
        x = self.target.curr_x
        y = self.target.curr_y
        z = self.target.curr_z

        try:
            self.distance_xy = math.sqrt(math.pow(x, 2) + math.pow(y, 2))
            self.distance = math.sqrt(math.pow(self.distance_xy, 2) + math.pow(z, 2))
            self.azimuth = math.atan2(y, x)
            self.elevation = math.asin(z / self.distance)
        except ZeroDivisionError:
            self.azimuth = 0
            self.elevation = 0
            self.distance = 0
            self.distance_xy = 0

    def recognize_target(self):
        y = self.SCREEN_HEIGHT * (self.target.height / self.v)
        x = self.SCREEN_WIDTH * (self.target.width / self.h)

        if (y >= 32 and x >= 32):
            xs = np.array([-self.target.width / 2 - 0.2, -self.target.width / 2 - 0.2, self.target.width / 2 + 0.2, self.target.width / 2 + 0.2, -self.target.width / 2 - 0.2])
            ys = np.array([-self.target.height/2 - 0.2, self.target.height/2 + 0.2, self.target.height/2 + 0.2, -self.target.height/2 - 0.2, -self.target.height/2 - 0.2])
        else:
            xs = np.array([])    
            ys = np.array([])    
        return xs, ys

    def get_target_rectangle(self):
        return Rectangle((-self.target.width/2, -self.target.height/2), self.target.width, self.target.height, facecolor=self.target.color)

    def get_fov_h_limit(self):
        self.v = math.tan(self.fov_h) * self.distance
        return np.array([-self.v/2, self.v/2])

    def get_fov_v_limit(self):
        self.h = math.tan(self.fov_v) * self.distance
        return np.array([-self.h/2, self.h/2])

    def follow_target(self, target):
        self.target = target
