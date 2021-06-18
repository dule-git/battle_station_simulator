import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import math
import time

PAINTBALL_VELOCITY_SLOW = 91
PAINTBALL_VELOCITY_FAST = 204
PAINTBALL_BALLISTIC_COEFF = 0.47
PAINTBALL_AREA = 0.00016
PAINTBALL_MASS = 0.0039

BULLET_VELOCITY = 920
BULLET_BALLISTIC_COEFF = 0.235
BULLET_AREA = 0.00016
BULLET_MASS = 0.05

g = 9.81
width = 1
h_step = 0.01
theta_step = 0.0001
tolerance = 0.01
h = 2
ro = 1.2

def x(t, theta):
    return (V_0/k)*(1 - math.exp(-k*t))*math.cos(theta)

def y(t, theta):
    return (V_0/k)*(1 - math.exp(-k*t))*math.sin(theta) + (g/math.pow(k, 2))*(1 - k*t - math.exp(-k*t))

def get_theta(d, alpha):
    global x_pos
    global y_pos
    x_pos = d * math.cos(alpha)
    y_pos = d * math.sin(alpha)
    
    coordinates = np.zeros((int(h / h_step), 2))
    for i, y in enumerate(np.arange(y_pos+h, y_pos, -h_step)):
        coordinates[i] = [x_pos, y]

    for coordinate in coordinates:
        y_temp = coordinate[1]
        x_temp = coordinate[0]
        x_times_k = x_temp * k
        for theta in np.arange(math.pi/2, 0, -theta_step):
            cos_theta = math.cos(theta)
            tan_theta = math.tan(theta)
            ln = math.log(abs(1 - x_times_k / (V_0 * cos_theta)))
            if -tolerance <= (y_temp - x_temp * tan_theta - g_over_k_squared * (ln + x_times_k / (V_0 * cos_theta))) <= tolerance:
                return theta

    return None

def init(projectile_type, _d, _alpha):
    global V_0
    global k
    global d
    global alpha
    alpha = _alpha
    d = _d

    if (projectile_type == 'bullet'):
        V_0 = BULLET_VELOCITY
        k = 0.5 * BULLET_BALLISTIC_COEFF * ro * BULLET_AREA * (1/BULLET_MASS) * BULLET_VELOCITY
    elif (projectile_type == 'paintball_fast'):
        V_0 = PAINTBALL_VELOCITY_FAST
        k = 0.5 * PAINTBALL_BALLISTIC_COEFF * ro * PAINTBALL_AREA * (1/PAINTBALL_MASS) * PAINTBALL_VELOCITY_FAST
    else:
        V_0 = PAINTBALL_VELOCITY_SLOW
        k = 0.5 * PAINTBALL_BALLISTIC_COEFF * ro * PAINTBALL_AREA * (1/PAINTBALL_MASS) * PAINTBALL_VELOCITY_SLOW

    global g_over_k_squared
    g_over_k_squared = g / math.pow(k, 2)

DISTANCE = 1900
Y_POS = 300
init('bullet', DISTANCE, math.asin(Y_POS/DISTANCE))

begin = time.time()
theta = get_theta(d, alpha)
end = time.time()

if (theta == None):
    print('Theta not found!')
else:
    print('Time taken by the program to execute:', end - begin)

x_arr = np.array([0])
y_arr = np.array([0])

for t in np.arange(0, 100, 0.1):
    if (y_arr[-1] < 0):
        break
    x_arr = np.append(x_arr, x(t, theta))
    y_arr = np.append(y_arr, y(t, theta))

fig, ax = plt.subplots()

ax.add_patch(Rectangle((x_pos - width/2, y_pos), width, h, facecolor='red'))
ax.add_patch(Rectangle((-width / 2, 0), width, int(h / 2), facecolor='blue'))
ax.set_aspect('equal')
plt.plot(x_arr, y_arr, label='Bullet trajectory')
plt.plot([0, x_pos], [0, y_pos + h], label='EO line of sight')
plt.xlabel('x')
plt.ylabel('y')
plt.legend(loc="upper right")
plt.grid()
plt.axis('equal')
plt.title('Math model, degrees: ' + '{:.2f}'.format(math.degrees(theta)))
plt.show()