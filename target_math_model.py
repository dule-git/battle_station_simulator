from fastkml import kml
import math as m
import numpy as np
import matplotlib.pyplot as plt
from geopy import distance

LAT = 1
LON = 0
R = 6371000

start_lat = -(22 + 33 / 60 + 40 / 3600)
start_lon = 17 + 8 / 60 + 7 / 3600

with open('Vlatacom.kml', 'rt', encoding="utf-8") as file:
    doc = file.read()

k = kml.KML()
k.from_string(doc)

root = list(k.features())
placemarks = list(root[0].features())

ax = plt.axes(projection ='3d')

for placemark in placemarks:
    x_placemark, y_placemark = 0, 0
    x_path = np.array([x_placemark])
    y_path = np.array([y_placemark])

    prev_coord = [start_lon, start_lat]
    for coord in placemark.geometry.coords[1:]:
        dx = distance.distance((prev_coord[LAT], prev_coord[LON]), (prev_coord[LAT], coord[LON])).m
        dy = distance.distance((prev_coord[LAT], prev_coord[LON]), (coord[LAT], prev_coord[LON])).m

        if (coord[LON] > prev_coord[LON]):
            x_placemark += dx
        else:
            x_placemark -= dx
        
        if (coord[LAT] > prev_coord[LAT]):
            y_placemark += dy
        else:
            y_placemark -= dy

        x_path = np.append(x_path, x_placemark)
        y_path = np.append(y_path, y_placemark)

        prev_coord = np.copy(coord)

    z_path = np.zeros(len(x_path))
    ax.plot3D(x_path, y_path, z_path, label=placemark.name)



plt.legend(loc='upper right')
plt.show()