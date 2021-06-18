from system.weapons.Weapon import Weapon

class PaintballGun(Weapon):

    V_0 = 204
    BALLISTIC_COEFF = 0.47
    AREA = 0.00016
    MASS = 0.0039

    def __init__(self):
        super().__init__()
