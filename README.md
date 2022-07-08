I have built a program that simulated a battle station which consists of a pan-tilt platform, weapon unit and an electro-optical surveillance unit. 
The simulation is showing various types of enemies that are moving in 3D space towards an allied battle station. 
The movement of enemies is predefined. User creates trajectories of enemy movement in "Google Maps" and then exports the data into a .kml file which is then parsed and plotted by the program. 
Allied battle station is located at a predefined fixed position and it tracks the given enemy. 
This is shown by plotting the trajectory of a projectile using kinematic formulas. 
The projectile can also be fired. The "fire" action algorithm calculates the intersection of a projectile and enemy movement trajectory, the time it takes the projectile to reach that point of intersection, and then plots the projectile trajectory as the enemy moves, the result is a hit enemy. 
Whole simulation, along with the "fire" mechanism  can be exported into a .kml file and then be played in a software that supports that format, like "Google Earth". 
