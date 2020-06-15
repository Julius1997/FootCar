import math


def normal_angle(angle):
    # normalise une valeur d'angle en degres entre 0 et 360
    while angle >= 360:
        angle -= 360
    while angle < 0:
        angle += 360
    return angle


def calc_mvt(vit):
    # calcul un mouvement en (x,y) a partir d'un vecteur (norme,angle)
    mvt = [vit[0] * math.cos(vit[1] * math.pi / 180), -vit[0] * math.sin(vit[1] * math.pi / 180)]
    return mvt


def somme_vect(vect1, vect2):
    # effectue la somme vectorielle de 2 vecteurs
    if vect1[0] != 0 and vect2[0] != 0:
        arg1 = vect1[1]*math.pi/180
        arg2 = vect2[1]*math.pi/180
        mod1 = vect1[0]
        mod2 = vect2[0]
        res = mod1*math.cos(arg1) + 1j*mod1*math.sin(arg1) + mod2*math.cos(arg2) + 1j*mod2*math.sin(arg2)
        if res.real != 0:
            param_atan = res.imag / res.real
            angle = math.atan(param_atan) * 180 / math.pi
        else:
            if res.imag > 0:
                angle = 90
            else:
                angle = 270
        if res.real < 0:
            angle = normal_angle(angle + 180)
        module = abs(res)
    elif vect1[0] != 0:
        angle = vect1[1]
        module = vect1[0]
    elif vect2[0] != 0:
        angle = vect2[1]
        module = vect2[0]
    else:
        module = 0
        angle = 0
    return [module, angle]
