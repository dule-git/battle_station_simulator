from enemies.Vehicle import Vehicle
from enemies.Boat import Boat
from enemies.Soldier import Soldier
from enemies.Helicopter import Helicopter
from system.System import System
from system.weapons.MachineGun import MachineGun
from system.weapons.PaintballGun import PaintballGun
from system.weapons.Weapon import Weapon
from SystemAnalyzer import SystemAnalyzer
from constants import *

import mpl_toolkits.mplot3d.axes3d as p3
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib import animation
from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt
import simplekml
from shapely.geometry import Point, LineString, Polygon
from geopy import distance
import numpy as np
import keyboard
import math
import os

kml_file = 'files/import/Canadian Mountains.kml'
# kml_file = 'files/import/Botswana Desert.kml'
# kml_file = 'files/import/Bora Bora Islands.kml'
# kml_file = 'files/import/Siberian Sea.kml'
# kml_file = 'files/import/Libian Desert.kml'
TIME_STEP = 1 # in seconds
lines = []

def update_animation_3d(num_of_frame, system, enemies, lines, system_analyzer, ax_3d):
    time = TIME_STEP * num_of_frame

    if (system.is_currently_shooting and time > system.time_at_end_of_shooting):
        time = system.time_at_end_of_shooting

    if (not system.done_shooting):

        for enemy, line in zip(enemies, lines):
            trajectory = enemy.get_trajectory_of_time(time)
            line.set_data([trajectory[X], trajectory[Y]])
            line.set_3d_properties(trajectory[Z])

            ax_3d.add_collection(enemy.get_cuboid(time))

            if (enemy == system.target):
                target_line = line

        system.update()
        # system.plot_eo_line_of_sight(lines[-2])
        if (keyboard.is_pressed('enter')):
            # clear the eo vision line
            lines[-1].set_data(np.array([[],[]]))
            lines[-1].set_3d_properties(np.array([]))
            lines[-1].set_linestyle('solid')
            lines[-1].set_color('black')

            system.shoot_target(time)
        elif (system.is_currently_shooting):
            system.plot_shooting_line(time, lines[-1])
        else:
            system.plot_weapon_trajectory(lines[-1])

        system_analyzer.add_snapshot()

        print_information(system, enemies)

def update_animation_2d(num_of_frame, system, ax_2d):
    ax_2d.set_xlim(system.get_fov_h_limit())
    ax_2d.set_ylim(system.get_fov_v_limit())
    ax_2d.add_patch(system.get_target_rectangle())
    bounding_box = system.recognize_target()
    ax_2d.plot(bounding_box[X], bounding_box[Y], color='green')

def main():
    enemies = []
    # enemies.append(Vehicle(kml_file, trajectory_id=1))
    # enemies.append(Boat(kml_file, trajectory_id=1))
    # enemies.append(Soldier(kml_file, trajectory_id=1))
    # enemies.append(Soldier(kml_file, trajectory_id=2))
    # enemies.append(Helicopter(kml_file, trajectory_id=1, on_height=300))
    enemies.append(Helicopter(kml_file, trajectory_id=2, on_height=0))

    weapon = MachineGun()
    # weapon = PaintballGun()
    system = System(enemies[0], weapon)
    system_analyzer = SystemAnalyzer(system)

    # simulation animation
    fig_3d, ax_3d, num_of_frames = init_animation_3d(enemies)
    ani_3d = animation.FuncAnimation(fig_3d, update_animation_3d, frames=num_of_frames, fargs=(system, enemies, lines, system_analyzer, ax_3d), interval=INTERVAL, blit=False, repeat=False)

    # zoom animation
    fig_2d, ax_2d = init_animation_2d()
    ani_2d = animation.FuncAnimation(fig_2d, update_animation_2d, frames=num_of_frames, fargs=(system, ax_2d), interval=INTERVAL, blit=False, repeat=False)

    plt.show()

    system_analyzer.show_analysis(TIME_STEP)

    export_animation_to_kml(system, enemies)
    system_analyzer.export_to_excel(kml_file, TIME_STEP, 'files/export/excel/')

def export_animation_to_kml(system, enemies):
    os.system('cls')
    print('Exporting animation to kml...')
     
    kml_file_animation = kml_file.replace('files/import/', '')
    kml_file_animation = kml_file_animation.replace('.kml', '')
    kml_file_animation = kml_file_animation + ' Animation.kml'

    kml = simplekml.Kml()

    SYSTEM_LAT, SYSTEM_LON, SYSTEM_ALT = read_system_location(kml_file)
    time = 0
    enemy_tol = 0.1
    enemy_step = 0.000001
    enemy_boundry = 0.001
    weapon_tol = 0.01
    weapon_step = 0.0000001
    weapon_boundry = 0.0001

    SYSTEM_LOCATION = kml.newpoint(name='SYSTEM_LOCATION')
    SYSTEM_LOCATION.coords = [(SYSTEM_LON, SYSTEM_LAT, SYSTEM_ALT)]

    tour = kml.newgxtour(name='Play me!')
    playlist = tour.newgxplaylist()

    if (system.done_shooting):
        weapon_delayed_start = ((INTERVAL / 1000) / TIME_STEP) * system.time_at_start_of_shooting
        weapon_duration = Weapon.TIME_STEP_WEAPON * ((INTERVAL / 1000) / TIME_STEP)
        WEAPON_SPPED_UP = 8
        for i in range(1, len(system.weapon.x_arr), WEAPON_SPPED_UP):
            weapon_animated_update = playlist.newgxanimatedupdate(gxduration=WEAPON_SPPED_UP * weapon_duration, gxdelayedstart=weapon_delayed_start + i * weapon_duration)
            weapon_animated_update.update.change = '<Placemark targetId="Weapon_' + str(i) + '"><visibility>1</visibility></Placemark>'
            wait = playlist.newgxwait(gxduration=WEAPON_SPPED_UP * weapon_duration)
        
    for i in range(1, len(system.target.animation_x_coords)):
        enemy_animated_update = playlist.newgxanimatedupdate(gxduration=INTERVAL/1000)
        update = ''
        for enemy in enemies:
            update += '<Placemark targetId="' + enemy.name + '_' + str(i) + '"><visibility>1</visibility></Placemark>'
        enemy_animated_update.update.change = update
        wait = playlist.newgxwait(gxduration=INTERVAL / 1000)

    for enemy in enemies:
        lon_0 = enemy.start_lon
        lat_0 = enemy.start_lat
        alt_0 = enemy.start_alt
        for i in range(1, len(enemy.animation_x_coords) - 1):
            # start coords
            x_0, y_0, z_0 = enemy.animation_x_coords[i], enemy.animation_y_coords[i], enemy.animation_z_coords[i]
            # destination coords
            x_1, y_1, z_1 = enemy.animation_x_coords[i + 1], enemy.animation_y_coords[i + 1], enemy.animation_z_coords[i + 1]
            
            dx = x_1 - x_0
            lon_step = enemy_step
            lon_boundry = enemy_boundry
            if (dx < 0):
                lon_boundry = -enemy_boundry
                lon_step = -enemy_step
                dx = -dx

            for lon_1 in np.arange(lon_0, lon_0 + lon_boundry, lon_step):
                dist_x = distance.distance((lat_0, lon_0), (lat_0, lon_1)).m
                if (-enemy_tol <= dist_x - dx <= enemy_tol):
                    break

            dy = y_1 - y_0
            lat_step = enemy_step
            lat_boundry = enemy_boundry
            if (dy < 0):
                lat_boundry = -enemy_boundry
                lat_step = -enemy_step
                dy = -dy
            
            for lat_1 in np.arange(lat_0, lat_0 + lat_boundry, lat_step):
                dist_y = distance.distance((lat_0, lon_1), (lat_1, lon_1)).m
                if (-enemy_tol <= dist_y - dy <= enemy_tol):
                    break

            alt_1 = SYSTEM_ALT + z_1

            line_string = kml.newlinestring(name=enemy.name + '_' + str(i))
            line_string.placemark._id = line_string.name
            line_string.coords = [(lon_0, lat_0, alt_0), (lon_1, lat_1, alt_1)]
            line_string.visibility = 0
            line_string.style.linestyle.width = 5
            line_string.style.linestyle.color = simplekml.Color.yellow

            lon_0, lat_0, alt_0 = lon_1, lat_1, alt_1

    if (system.done_shooting):
        lon_0 = SYSTEM_LON
        lat_0 = SYSTEM_LAT
        alt_0 = SYSTEM_ALT
        for i in np.arange(1, len(system.weapon.x_arr) - WEAPON_SPPED_UP - 1, WEAPON_SPPED_UP):
            i = int(i)
            x_0, y_0, z_0 = system.weapon.x_arr[i], system.weapon.y_arr[i], system.weapon.z_arr[i]
            x_1, y_1, z_1 = system.weapon.x_arr[i + WEAPON_SPPED_UP], system.weapon.y_arr[i + WEAPON_SPPED_UP], system.weapon.z_arr[i + WEAPON_SPPED_UP]

            dx = x_1 - x_0
            lon_step = weapon_step
            lon_boundry = weapon_boundry
            if (dx < 0):
                lon_boundry = -weapon_boundry
                lon_step = -weapon_step
                dx = -dx

            for lon_1 in np.arange(lon_0, lon_0 + lon_boundry, lon_step):
                dist_x = distance.distance((lat_0, lon_0), (lat_0, lon_1)).m
                if (-weapon_tol <= dist_x - dx <= weapon_tol):
                    break

            dy = y_1 - y_0    
            lat_step = weapon_step
            lat_boundry = weapon_boundry
            if (dy < 0):
                lat_boundry = -weapon_boundry
                lat_step = -weapon_step
                dy = -dy
            
            for lat_1 in np.arange(lat_0, lat_0 + lat_boundry, lat_step):
                dist_y = distance.distance((lat_0, lon_1), (lat_1, lon_1)).m
                if (-weapon_tol <= dist_y - dy <= weapon_tol):
                    break

            alt_1 = SYSTEM_ALT + z_1
            print(i)
            
            line_string = kml.newlinestring(name='Weapon_' + str(i))
            line_string.placemark._id = line_string.name
            line_string.altitudemode = simplekml.AltitudeMode.absolute
            line_string.coords = [(lon_0, lat_0, alt_0), (lon_1, lat_1, alt_1)]
            line_string.visibility = 0
            line_string.style.linestyle.width = 5
            line_string.style.linestyle.color = simplekml.Color.black

            lon_0, lat_0, alt_0 = lon_1, lat_1, alt_1
            
    with open('files/export/kml/'+kml_file_animation, 'w+') as output_file:
        output_file.write(kml.kml())

    print('Animation exported as: ' + kml_file_animation)       


def init_animation_2d():
    fig_2d = plt.figure()
    ax_2d = fig_2d.add_subplot(xlim=[-10, 10], ylim=[-10, 10])
    return fig_2d, ax_2d

def init_animation_3d(enemies):
    fig = plt.figure()
    ax = p3.Axes3D(fig)

    # create a line for each enemy
    for index in range(len(enemies)):
        lobj = ax.plot([], [], lw=2)[0]
        lobj.set_data([], [])
        lines.append(lobj)

    # for eo_line_of_sight
    lobj = ax.plot([], [], ':')[0]
    lobj.set_data([], [])
    lines.append(lobj)

    # for weapon trajectory
    lobj = ax.plot([], [], ':')[0]
    lobj.set_data([], [])
    lines.append(lobj)
    
    # determine the scale of the animation
    x_max, y_max, z_max = -1, -1, -1
    x_min, y_min, z_min = 999999,999999,999999
    max_num_of_frames = -1
    for e in enemies:
        if (x_max < np.amax(e.x_coords)):
            x_max = np.amax(e.x_coords)
        if (y_max < np.amax(e.y_coords)):
            y_max = np.amax(e.y_coords)
        if (z_max < np.amax(e.z_coords)):
            z_max = np.amax(e.z_coords)

        if (x_min > np.amin(e.x_coords)):
            x_min = np.amin(e.x_coords)
        if (y_min > np.amin(e.y_coords)):
            y_min = np.amin(e.y_coords)
        if (z_min > np.amin(e.z_coords)):
            z_min = np.amin(e.z_coords)

        time = e.get_total_time_of_trajectory()
        num_of_frames = int(time / TIME_STEP)
        if (num_of_frames > max_num_of_frames):
            max_num_of_frames = num_of_frames + 1

    minimum = np.amin([x_min, y_min, z_min])
    maximum = np.amax([x_max, y_max, z_max])

    # if system location(with coordinates 0,0) is out of the picture
    if x_min > 0:
        x_min = 0
    if x_max < 0:
        x_max = 0
    if y_min > 0:
        y_min = 0
    if y_max < 0:
        y_max = 0

    ax.set_xlim3d([x_min, x_max])
    ax.set_xlabel('X')

    ax.set_ylim3d([y_min, y_max])
    ax.set_ylabel('Y')

    ax.set_zlim3d([z_min, z_max + 200])
    ax.set_zlabel('Z')

    # ax.set_xlim3d([minimum, maximum])
    # ax.set_xlabel('X')

    # ax.set_ylim3d([minimum, maximum])
    # ax.set_ylabel('Y')

    # ax.set_zlim3d([minimum, maximum])
    # ax.set_zlabel('Z')

    return fig, ax, max_num_of_frames

def show_all_trajectories_3d(enemies):
    ax = plt.axes(projection='3d')

    for e in enemies:
        x_coords, y_coords = e.get_coords()
        z_coords = np.zeros(len(x_coords))
        ax.plot3D(x_coords, y_coords, z_coords, label=e.name)

    plt.legend(loc='upper right')
    plt.show()

def show_all_trajectories_2d(enemies):
    for e in enemies:
        x_coords, y_coords = e.get_coords()
        plt.plot(x_coords, y_coords, label=e.name)

    plt.legend(loc='upper right')
    plt.show()

def print_information(system, enemies):
    os.system('cls')
    print('========= SYSTEM =========')
    print('Distance: {:.2f} m'.format(system.distance))
    print('Elevation: {:.2f}\u00b0'.format(math.degrees(system.elevation)))
    print('Azimuth: {:.2f}\u00b0'.format(math.degrees(system.azimuth)))
    print('========= ENEMIES ========')
    for enemy in enemies:
        print(enemy.name + ' velocity: ' + '{:.2f} m/s'.format(enemy.curr_velocity))

if __name__ == '__main__':
    main()
