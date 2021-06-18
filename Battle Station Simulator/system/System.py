from system.EO_System import EO_System
from system.weapons.Weapon import Weapon
from constants import *

import numpy as np
import math
import matplotlib.pyplot as plt

class System:

    WAITING_TIME = 5

    def __init__(self, target, weapon):
        self.eo_system = EO_System(target)
        self.weapon = weapon
        self.weapon.system = self
        self.is_currently_shooting = False
        self.done_shooting = False
        self.time_at_end_of_shooting = 9999

    def update(self):
        self.eo_system.update()
        self.weapon.update()

    def follow_target(self, target):
        self.eo_system.follow_target(target)

    def plot_eo_line_of_sight(self, line):
        eo_line_of_sight = np.array([np.array([0, self.target.curr_x]), np.array([0, self.target.curr_y])])
        line.set_data(eo_line_of_sight)
        line.set_3d_properties([0, self.target.curr_z])

    def plot_weapon_trajectory(self, line):
        line.set_data(np.array([self.weapon.x_arr, self.weapon.y_arr]))
        line.set_3d_properties(self.weapon.z_arr)
    
    def shoot_target(self, curr_time):

        self.is_currently_shooting = True

        # calculate the x,y,z of target in WAITING_TIME
        WAITING_TIME = self.weapon.time_to_reach_target
        predicted_coords = self.target.predict_xyz_of_time(curr_time + WAITING_TIME)
        
        x_at_hitting_time = predicted_coords[X]
        y_at_hitting_time = predicted_coords[Y]
        z_at_hitting_time = predicted_coords[Z]

        plt.plot(x_at_hitting_time, y_at_hitting_time, z_at_hitting_time, 'x', color='red', lw=10)

        # get the elevation of the weapon for those x,y,z
        self.weapon.calculate_theta(x=x_at_hitting_time, y=y_at_hitting_time, z=z_at_hitting_time)
        shooting_theta = self.weapon.theta
        
        # get the azimuth of the weapong for those x,y,z
        shooting_azimuth = math.atan2(y_at_hitting_time, x_at_hitting_time)
        # calculate the trajectory of the bullet
        self.weapon.calculate_trajectory(
            x=x_at_hitting_time,
            y=y_at_hitting_time,
            z=z_at_hitting_time,
            theta=shooting_theta,
            azimuth=shooting_azimuth
        )

        # time the bullet will fly
        self.time_at_start_of_shooting = curr_time + WAITING_TIME - self.weapon.time_to_reach_target
        self.time_at_end_of_shooting = curr_time + WAITING_TIME

        self.projectile_trajectory = (self.weapon.x_arr, self.weapon.y_arr, self.weapon.z_arr)

    def plot_shooting_line(self, curr_time, line):
        if (curr_time >= self.time_at_start_of_shooting):
            time = round(curr_time - self.time_at_start_of_shooting, 1)
            i = int(time / Weapon.TIME_STEP_WEAPON)
            line.set_data(np.array([self.projectile_trajectory[X][:i], self.projectile_trajectory[Y][:i]]))
            line.set_3d_properties(self.projectile_trajectory[Z][:i])
            if (curr_time >= self.weapon.time_to_reach_target + self.time_at_start_of_shooting):
                self.done_shooting = True


    def get_target_rectangle(self):
        return self.eo_system.get_target_rectangle()

    def get_fov_h_limit(self):
        return self.eo_system.get_fov_h_limit()

    def get_fov_v_limit(self):
        return self.eo_system.get_fov_v_limit()

    def recognize_target(self):
        return self.eo_system.recognize_target()

    @property
    def target(self):
        return self.eo_system.target

    @property
    def azimuth(self):
        return self.eo_system.azimuth

    @property
    def elevation(self):
        return self.eo_system.elevation

    @property
    def distance(self):
        return self.eo_system.distance

    @property
    def distance_xy(self):
        return self.eo_system.distance_xy