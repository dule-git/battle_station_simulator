from system.weapons.Weapon import Weapon

class MachineGun(Weapon):

    V_0 = 920
    BALLISTIC_COEFF = 0.235
    AREA = 0.00016
    MASS = 0.05

    MAX_DISTANCE = 1700

    def __init__(self):
        super().__init__()
