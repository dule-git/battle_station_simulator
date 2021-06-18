from constants import *

from fastkml import kml
from geopy import distance
import numpy as np
import math
from abc import ABC, abstractmethod
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib.pyplot as plt

class Enemy:
    
    color = 'red'

    def __init__(self, kml_file, on_height=0):
        
        # coordinates the animation reads
        self.animation_x_coords = np.array([])
        self.animation_y_coords = np.array([])
        self.animation_z_coords = np.array([])

        # x, y, z coordinate for each ployline dot
        self.x_coords = np.array([])
        self.y_coords = np.array([])
        self.z_coords = np.array([])

        # difference in x,y,z axis between consecutive polyline dots
        self.dx = np.array([])
        self.dy = np.array([])
        self.dz = np.array([])

        # travelled distances for each section between polyline dots
        self.travelled_distance = np.array([])
        # travelled distances for each section between polyline dots but if look from a 2d plane above (x,y plane)
        self.travelled_distance_xy = np.array([])

        # plus on the z-axis, helicopter is on a certain height from the ground
        self.on_height = on_height

        self.curr_section = 0
        self.end_of_trajectory = False
        
        self.cuboid = None

        self.read_trajectory(kml_file, self.name)
        self.calculate_trajectory_parameters()

    # Reads basic information about the trajectory
    # --> x, y, z coordinates of the polyline dots
    # --> travelled distances for each section between pointes
    def read_trajectory(self, kml_file, type_of_enemy):

        # read my polyline from kml_file        
        placemark = self.get_my_placemark(kml_file, type_of_enemy)
        SYSTEM_LAT, SYSTEM_LON, SYSTEM_ALT = read_system_location(kml_file)

        # adding on_height to an existing height for targets in air
        lat_lon_alt_coordinates = np.zeros((len(placemark.geometry.coords), 3))
        for i, coord in enumerate(placemark.geometry.coords):
            lat_lon_alt_coordinates[i][LAT] = coord[LAT]
            lat_lon_alt_coordinates[i][LON] = coord[LON]
            lat_lon_alt_coordinates[i][ALT] = coord[ALT] + self.on_height

        # read staring lat, lon, alt for later exporting animation to kml
        self.start_lat = lat_lon_alt_coordinates[0][LAT]
        self.start_lon = lat_lon_alt_coordinates[0][LON]
        self.start_alt = lat_lon_alt_coordinates[0][ALT]

        # read starting coordinates
        prev_coord = lat_lon_alt_coordinates[0]
        dx = distance.distance((prev_coord[LAT], prev_coord[LON]), (prev_coord[LAT], SYSTEM_LON)).m
        dy = distance.distance((prev_coord[LAT], prev_coord[LON]), (SYSTEM_LAT, prev_coord[LON])).m
        dz = prev_coord[ALT] - SYSTEM_ALT

        if (prev_coord[LON] < SYSTEM_LON):
            dx = -dx
        
        if (prev_coord[LAT] < SYSTEM_LAT):
            dy = -dy

        x_placemark = dx
        y_placemark = dy
        z_placemark = dz

        self.x_coords = np.append(self.x_coords, x_placemark)
        self.y_coords = np.append(self.y_coords, y_placemark)
        self.z_coords = np.append(self.z_coords, z_placemark)

        self.curr_x = x_placemark
        self.curr_y = y_placemark
        self.curr_z = z_placemark

        for coord in lat_lon_alt_coordinates[1:]:
            # calculate axis distances between two consecutive polyline points
            dx = distance.distance((prev_coord[LAT], prev_coord[LON]), (prev_coord[LAT], coord[LON])).m
            dy = distance.distance((prev_coord[LAT], prev_coord[LON]), (coord[LAT], prev_coord[LON])).m
            dz = coord[ALT] - prev_coord[ALT]

            if (coord[LON] < prev_coord[LON]):
                dx = -dx
            x_placemark += dx
            
            if (coord[LAT] < prev_coord[LAT]):
                dy = -dy
            y_placemark += dy

            z_placemark = coord[ALT] - SYSTEM_ALT

            self.x_coords = np.append(self.x_coords, x_placemark)
            self.y_coords = np.append(self.y_coords, y_placemark)
            self.z_coords = np.append(self.z_coords, z_placemark)

            self.dx = np.append(self.dx, dx)
            self.dy = np.append(self.dy, dy)
            self.dz = np.append(self.dz, dz)
            
            travelled_distance_xy = math.sqrt(math.pow(dx, 2) + math.pow(dy, 2))
            self.travelled_distance_xy = np.append(self.travelled_distance_xy, travelled_distance_xy)
            travelled_distance_3d = math.sqrt(math.pow(travelled_distance_xy, 2) + math.pow(dz, 2))
            self.travelled_distance = np.append(self.travelled_distance, travelled_distance_3d)
            prev_coord = np.copy(coord)

    def get_trajectory_of_time(self, time):

        # find the trajectory section I am currently at
        self.end_of_trajectory = True
        for i, t in enumerate(self.time):
            if (time - t < 0):
                self.end_of_trajectory = False
                self.curr_section = i
                self.curr_time = time
                break
            else:
                time -= t

        if not self.end_of_trajectory:
            distance_travelled_till_time = self.velocity[i] * time + (self.acceleration[i] * math.pow(time, 2)) / 2
            distance_left_to_travel = self.travelled_distance[i] - distance_travelled_till_time
            
            self.curr_x = self.x_coords[i + 1] - self.dx[i] * (distance_left_to_travel / self.travelled_distance[i])
            self.curr_y = self.y_coords[i + 1] - self.dy[i] * (distance_left_to_travel / self.travelled_distance[i])
            self.curr_z = self.z_coords[i + 1] - self.dz[i] * (distance_left_to_travel / self.travelled_distance[i])

            self.animation_x_coords = np.append(
                self.animation_x_coords, self.curr_x)
            self.animation_y_coords = np.append(
                self.animation_y_coords, self.curr_y)
            self.animation_z_coords = np.append(
                self.animation_z_coords, self.curr_z)

            # parameters used for printing and system analysis
            self.curr_velocity = self.velocity[i] + self.acceleration[i] * time
            elevation_angle = math.atan(self.dz[i] / self.travelled_distance_xy[i])
            self.curr_velocity_xy = self.curr_velocity * abs(math.cos(elevation_angle))
            self.curr_velocity_z = self.curr_velocity * abs(math.sin(elevation_angle))
        else:
            self.curr_x = 0
            self.curr_y = 0
            self.curr_z = 0
            self.curr_velocity = 0
            self.curr_velocity_xy = 0
            self.curr_velocity_z = 0

            self.animation_x_coords = np.append(
                self.animation_x_coords, self.curr_x)
            self.animation_y_coords = np.append(
                self.animation_y_coords, self.curr_y)
            self.animation_z_coords = np.append(
                self.animation_z_coords, self.curr_z)

        return [self.animation_x_coords, self.animation_y_coords, self.animation_z_coords]

    # used to predict the coordinates at the given time
    # simular to get_trajectory_of_time but doesn't change the object data
    # and returns only one pair of coordinates
    def predict_xyz_of_time(self, time):
        # find the trajectory section I am currently at
        end_of_trajectory = True
        for i, t in enumerate(self.time):
            if (time - t < 0):
                end_of_trajectory = False
                break
            else:
                time -= t

        if not end_of_trajectory:
            distance_travelled_till_time = self.velocity[i] * time + (self.acceleration[i] * math.pow(time, 2)) / 2
            distance_left_to_travel = self.travelled_distance[i] - distance_travelled_till_time
            
            predicted_x = self.x_coords[i + 1] - self.dx[i] * (distance_left_to_travel / self.travelled_distance[i])
            predicted_y = self.y_coords[i + 1] - self.dy[i] * (distance_left_to_travel / self.travelled_distance[i])
            predicted_z = self.z_coords[i + 1] - self.dz[i] * (distance_left_to_travel / self.travelled_distance[i])

            return (predicted_x, predicted_y, predicted_z)
        else:
            return (self.curr_x, self.curr_y, self.curr_z)

    # returns the cuboid that represents the enemy on the map
    def get_cuboid(self, time):
        x, y, z = self.predict_xyz_of_time(time)

        points = np.zeros((8, 3))

        for i, t in enumerate(self.time):
            if (time - t < 0):
                self.curr_section = i
                self.curr_time = time
                break
            else:
                time -= t

        x1, y1, x2, y2 = self.x_coords[i], self.y_coords[i], self.x_coords[i + 1], self.y_coords[i + 1]
        k = (y2 - y1) / (x2 - x1)
        alpha = math.atan(k)
        dx_help_point = math.cos(alpha) * (self.length / 2)
        dy_help_point = math.sin(alpha) * (self.length / 2)
        dx = math.sin(alpha) * (self.width / 2)
        dy = math.cos(alpha) * (self.width / 2)
        if (k < 0):
            help_point_1 = (x - dx_help_point, y + dy_help_point)
            help_point_2 = (x + dx_help_point, y - dy_help_point)
            # top plane
            points[0] = np.array([help_point_1[X] - dx, help_point_1[Y] - dy, z + self.height])
            points[1] = np.array([help_point_1[X] + dx, help_point_1[Y] + dy, z + self.height])
            points[2] = np.array([help_point_2[X] + dx, help_point_2[Y] + dy, z + self.height])
            points[3] = np.array([help_point_2[X] - dx, help_point_2[Y] - dy, z + self.height])
            # bottom plane
            points[4] = np.array([help_point_1[X] - dx, help_point_1[Y] - dy, z])
            points[5] = np.array([help_point_1[X] + dx, help_point_1[Y] + dy, z])
            points[6] = np.array([help_point_2[X] + dx, help_point_2[Y] + dy, z])
            points[7] = np.array([help_point_2[X] - dx, help_point_2[Y] - dy, z])

        else:
            help_point_1 = (x - dx_help_point, y - dy_help_point)
            help_point_2 = (x + dx_help_point, y + dy_help_point)
            # top plane
            points[0] = np.array([help_point_1[X] + dx, help_point_1[Y] - dy, z + self.height])
            points[1] = np.array([help_point_1[X] - dx, help_point_1[Y] + dy, z + self.height])
            points[2] = np.array([help_point_2[X] - dx, help_point_2[Y] + dy, z + self.height])
            points[3] = np.array([help_point_2[X] + dx, help_point_2[Y] - dy, z + self.height])
            # bottom plane
            points[4] = np.array([help_point_1[X] + dx, help_point_1[Y] - dy, z])
            points[5] = np.array([help_point_1[X] - dx, help_point_1[Y] + dy, z])
            points[6] = np.array([help_point_2[X] - dx, help_point_2[Y] + dy, z])
            points[7] = np.array([help_point_2[X] + dx, help_point_2[Y] - dy, z])
        
        top_plane = [points[0], points[1], points[2], points[3]]
        bottom_plane = [points[4], points[5], points[6], points[7]]
        right_plane = [points[0], points[3], points[7], points[4]]
        left_plane = [points[1], points[2], points[6], points[5]]
        front_plane = [points[0], points[1], points[5], points[4]]
        back_plane = [points[2], points[3], points[7], points[6]]
        cuboid = np.array([top_plane, bottom_plane, right_plane, left_plane, front_plane, back_plane])

        # remove from plot
        if (self.cuboid != None):
            self.cuboid.remove()

        self.cuboid = Poly3DCollection(cuboid, facecolors=np.repeat(Enemy.color, 6), edgecolor='k')
        return self.cuboid
        
    @abstractmethod
    def calculate_trajectory_parameters(self):
        pass

    @abstractmethod
    def velocity_of_angle(self, angle):
        pass

    def get_total_time_of_trajectory(self):
        return np.sum(self.time)
    
    def get_my_placemark(self, kml_file, type_of_enemy):
        with open(kml_file, 'rt', encoding="utf-8") as file:
            doc = file.read()
        k = kml.KML()
        k.from_string(doc.encode('utf-8'))
        
        root = list(k.features())
        placemarks = list(root[0].features())

        placemark = None
        for p in placemarks:
            if p.name == type_of_enemy:
                placemark = p
                break
        
        return placemark

    def get_coords(self):
        return self.x_coords, self.y_coords, self.z_coords

    


