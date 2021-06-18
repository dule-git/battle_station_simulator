from constants import *

from scipy.optimize import fsolve
import numpy as np
import math

class Weapon:

    TIME_STEP_WEAPON = 0.001

    def __init__(self):
        self.system = None
        self.theta = None
        self.k = 0.5 * self.BALLISTIC_COEFF * ro * self.AREA * (1 / self.MASS) * self.V_0
        self.x_arr = np.array([])
        self.y_arr = np.array([])
        self.z_arr = np.array([])
    
    def update(self):
        self.calculate_theta()
        self.calculate_trajectory()

    # can accept x,y,z coordinates of the enemy
    # if kwargs are not passed, calculate the theta for the following target
    def calculate_theta(self, **kwargs):
        HEIGHT_STEP = 0.1
        THETA_STEP = 0.0001
        TOLERANCE = 0.1
        G_OVER_K_SQUARED = g / math.pow(self.k, 2)

        if (len(kwargs) == 0):
            distance = self.system.distance
            elevation = self.system.elevation
        else:
            x_pos, y_pos, z_pos = kwargs['x'], kwargs['y'], kwargs['z']
            distance = math.sqrt(x_pos ** 2 + y_pos ** 2 + z_pos ** 2)
            elevation = math.asin(z_pos / distance)

        target = self.system.target
        xy_pos = distance * math.cos(elevation)
        z_pos = distance * math.sin(elevation)

        coordinates = np.zeros((int(target.height / HEIGHT_STEP), 2))
        for i, z in enumerate(np.arange(z_pos + target.height, z_pos, -HEIGHT_STEP)):
            if (i < len(coordinates)):
                coordinates[i] = np.array([xy_pos, z])
        
        for coordinate in coordinates:
            xy_temp = coordinate[0]
            z_temp = coordinate[1]
            xy_times_k = xy_temp * self.k

            self.theta = fsolve(self.solve_theta, 0, args=(xy_temp, z_temp, xy_times_k, G_OVER_K_SQUARED))[0]
            break
            i = 5

            # if (z_temp > 0):
            #     thetas = np.arange(math.pi / 2, 0, -THETA_STEP)
            # else:
            #     thetas = np.arange(0, -math.pi / 2, -THETA_STEP)

            # for theta in thetas:
            #     cos_theta = math.cos(theta)
            #     tan_theta = math.tan(theta)
            #     ln = math.log(abs(1 - xy_times_k / (self.V_0 * cos_theta)))
                
            #     if -TOLERANCE <= (z_temp - xy_temp * tan_theta - G_OVER_K_SQUARED * (ln + xy_times_k / (self.V_0 * cos_theta))) <= TOLERANCE:
            #         self.theta = theta
            #         return
        
        # self.theta = None

    # function that fsolve tries to find the root for
    # the root will be the elevation angle of shooting => theta
    def solve_theta(self, theta, *args):
        xy = args[0]
        z = args[1]
        xy_times_k = args[2]
        G_OVER_K_SQUARED = args[3]

        cos_theta = math.cos(theta)
        tan_theta = math.tan(theta)

        ln = math.log(abs(1 - xy_times_k / (self.V_0 * cos_theta)))
        
        return z - xy * tan_theta - G_OVER_K_SQUARED * (ln + xy_times_k / (self.V_0 * cos_theta))

    def x_of(self, t, theta, azimuth):
        xy = (self.V_0/self.k)*(1 - math.exp(-self.k*t))*math.cos(theta)
        return math.cos(azimuth) * xy

    def y_of(self, t, theta, azimuth):
        xy = (self.V_0/self.k)*(1 - math.exp(-self.k*t))*math.cos(theta)
        return math.sin(azimuth) * xy

    def z_of(self, t, theta, azimuth):
        return (self.V_0 / self.k) * (1 - math.exp(-self.k * t)) * math.sin(theta) + (g / math.pow(self.k, 2)) * (1 - self.k * t - math.exp(-self.k * t))
        
    def calculate_trajectory(self, **kwargs):
        if (len(kwargs) == 0):
            x_target = self.system.target.curr_x
            y_target = self.system.target.curr_y
            z_target = self.system.target.curr_z
            azimuth = self.system.azimuth
            theta = self.theta
        else:
            x_target = kwargs['x']
            y_target = kwargs['y']
            z_target = kwargs['z']
            azimuth = kwargs['azimuth']
            theta = kwargs['theta']

        if (self.theta != None):
            tol = 0.5
            self.x_arr = np.array([0])
            self.y_arr = np.array([0])
            self.z_arr = np.array([0])
            t = 0
            connect = True
            while not ((-tol <= abs(self.x_arr[-1] - x_target) <= tol) and
                      (-tol <= abs(self.y_arr[-1] - y_target) <= tol) and
                      (-tol <= abs(self.z_arr[-1] - z_target - self.system.target.height) <= tol)):                
                self.x_arr = np.append(self.x_arr, self.x_of(t, theta, azimuth))
                self.y_arr = np.append(self.y_arr, self.y_of(t, theta, azimuth))
                self.z_arr = np.append(self.z_arr, self.z_of(t, theta, azimuth))
                t += Weapon.TIME_STEP_WEAPON

                if (t > 5):
                    connect = False
                    break
            
            if (connect):
                self.x_arr = np.append(self.x_arr, x_target)
                self.y_arr = np.append(self.y_arr, y_target)
                self.z_arr = np.append(self.z_arr, z_target)
            self.time_to_reach_target = t
        else:
            self.x_arr = np.array([])
            self.y_arr = np.array([])
            self.z_arr = np.array([])
    







    
    
    