import math as m
import numpy as np
import matplotlib.pyplot as plt

PAINTBALL_VELOCITY_SLOW = 91
PAINTBALL_VELOCITY_FAST = 204
PAINTBALL_BALLISTIC_COEFF = 0.47
PAINTBALL_AREA = 0.00016
PAINTBALL_MASS = 0.0039

BULLET_VELOCITY = 920
BULLET_BALLISTIC_COEFF = 0.235
BULLET_AREA = 0.00016
BULLET_MASS = 0.05

ro = 1.2
g = 9.81

v0 = 0
k = 0

def x_air(t, theta):
    return (v0/k)*(1 - m.exp(-k*t))*m.cos(theta)

def y_air(t, theta):
    return (v0/k)*(1 - m.exp(-k*t))*m.sin(theta) + (g/m.pow(k, 2))*(1 - k*t - m.exp(-k*t))

def x(t, theta):
    return v0*m.cos(theta)*t

def y(t, theta):
    return v0*m.sin(theta)*t - 0.5*g*m.pow(t,2)

def init(projectile_type):
    global v0
    global k
    if (projectile_type == 'bullet'):
        v0 = BULLET_VELOCITY
        k = 0.5 * BULLET_BALLISTIC_COEFF * ro * BULLET_AREA * (1/BULLET_MASS) * BULLET_VELOCITY
    elif (projectile_type == 'paintball_fast'):
        v0 = PAINTBALL_VELOCITY_FAST
        k = 0.5 * PAINTBALL_BALLISTIC_COEFF * ro * PAINTBALL_AREA * (1/PAINTBALL_MASS) * PAINTBALL_VELOCITY_FAST
    else:
        v0 = PAINTBALL_VELOCITY_SLOW
        k = 0.5 * PAINTBALL_BALLISTIC_COEFF * ro * PAINTBALL_AREA * (1/PAINTBALL_MASS) * PAINTBALL_VELOCITY_SLOW

init('paintball_fast')
max_range = -1
max_theta = -1
max_x = []
max_y = []

for theta in np.arange(0, 1.57, 0.01):
    x_air_arr = np.array([])
    y_air_arr = np.array([])
    x_arr = np.array([])
    y_arr = np.array([])

    x_air_arr = np.append(x_air_arr, x_air(0, theta))
    y_air_arr = np.append(y_air_arr, y_air(0, theta))
    x_arr = np.append(x_arr, x(0, theta))
    y_arr = np.append(y_arr, y(0, theta))

    for t in np.arange(0.1, 100, 0.1):

        if (y_air_arr[-1] >= 0):
            x_air_arr = np.append(x_air_arr, x_air(t, theta))
            y_air_arr = np.append(y_air_arr, y_air(t, theta))

        if (y_arr[-1] >= 0):
            x_arr = np.append(x_arr, x(t, theta))
            y_arr = np.append(y_arr, y(t, theta))

    if (x_air_arr[-1] > max_range):
        max_theta = theta
        max_range = x_air_arr[-1]
        max_x_air = np.copy(x_air_arr)
        max_y_air = np.copy(y_air_arr)
        max_x = np.copy(x_arr)
        max_y = np.copy(y_arr)

plt.plot(max_x_air, max_y_air, label='With drag force')
plt.plot(max_x, max_y, label='Without drag force')
plt.xlabel('x')
plt.ylabel('y')
plt.legend(loc="upper right")
plt.grid()
plt.axis('equal')
plt.title('Paintball, angle ' + '{:.2f}'.format(m.degrees(max_theta)) + ', max range: ' + '{:.2f}'.format(max_x_air[-1]))
plt.show()

    
