import math
import pygame
import time
#import matplotlib.pyplot as plt

from Utiles import normal_angle, calc_mvt, somme_vect


def collide_orient_rect(orient_rect1, orient_rect2):
    """
    Determine si deux rectangles orientés sont en collision et stocke les couples [droite, droite2] qui se touchent.
    Renvoie juste True si un des rectangles est dans l'autre mais qu'aucun des bords ne se touche

    :param orient_rect1: liste contenant rect, orientation (en degrés), longueur et largeur (en pixels) du rectangle 1
    :param orient_rect2: idem pour le rectangle 2
    :return: la liste contenant les couples [droite, droite2] en collision, ou True si un des rect est dans l'autre
    """

    def determ_sommets(rect, ori, long, larg):
        """
        détermine les points aux sommets du rectangle orienté
        :param rect:
        :param ori:
        :param long:
        :param larg:
        :return:
        """

        HG, HD = [rect[0], rect[1]], [rect[0] + rect[2], rect[1]]
        BG, BD = [rect[0], rect[1] + rect[3]], [rect[0] + rect[2], rect[1] + rect[3]]

        sinangle = math.sin((ori % 90) * math.pi / 180)
        if 0 <= (ori % 180) < 90:
            HG[1] += long * sinangle
            BD[1] -= long * sinangle
            HD[0] -= larg * sinangle
            BG[0] += larg * sinangle
        elif 90 <= (ori % 180) < 180:
            HG[1] += larg * sinangle
            BD[1] -= larg * sinangle
            HD[0] -= long * sinangle
            BG[0] += long * sinangle

        return [HG, HD, BD, BG]

    def determ_coefs_droite(sommets):
        """
        détermine les coefficients des équations des 4 droites composant un rectangle en fonrnissant les coordonnées
        de ses sommets (les sommets doivent être donnés dans un ordre de sommets adjascents)

        :param sommets: liste de coordonnées des 4 sommets du rectangle dont on cherche les coefs des droites des côtés
        :return: liste de 4 éléments, chacun est une liste comprenant les coefs A et B de l'équation de droite d'un des
        côtés du rectangle, ainsi que les deux points délimitant ce côté
        """

        # HG, HD, BD, BG = sommets
        coefs_droites = []
        for k in range(4):
            if k == 3:
                if sommets[0][0] != sommets[k][0]:
                    A = (sommets[0][1] - sommets[k][1]) / (sommets[0][0] - sommets[k][0])
                    B = sommets[0][1] - A * sommets[0][0]
                else:
                    A = ''
                    B = sommets[k][0]
                coefs_droites.append([A, B, sommets[k], sommets[0]])
            else:
                if sommets[k+1][0] != sommets[k][0]:
                    A = (sommets[k+1][1] - sommets[k][1]) / (sommets[k+1][0] - sommets[k][0])
                    B = sommets[k+1][1] - A*sommets[k+1][0]
                else:
                    A = ''
                    B = sommets[k][0]
                coefs_droites.append([A, B, sommets[k], sommets[k+1]])
        return coefs_droites

    [rect1, ori1, long1, larg1] = orient_rect1
    [rect2, ori2, long2, larg2] = orient_rect2

    collision = []

    # on commence par vérifier si les rect sont en collision, puis si oui, on examine les rect orientés
    if rect1.colliderect(rect2):

        # genere une liste avec les coordonnees des sommets de chaque rectangles orientes, en convention[x, y]
        sommets1 = determ_sommets(rect1, ori1, long1, larg1)
        sommets2 = determ_sommets(rect2, ori2, long2, larg2)

        # genere une liste avec les coefs a et b des equations de droites (y=ax+b) des cotes de chaque rectangle
        coefs_droites1 = determ_coefs_droite(sommets1)
        coefs_droites2 = determ_coefs_droite(sommets2)

        # Pour chaque paires (droite du rect1, droite du rect2), on determine leur point d'intersection et on regarde
        # s'il fait partie des deux segments representants les cotes d'equations respectives la paire de droites.
        # De plus, si tous le points d'intersections appartiennent a un rectangle mais aucun a l'autre,
        # alors les bords des rectangles ne se touchent pas, et un des rectangles est dans l'autre

        compt1in2, compt2in1 = 0, 0  # pour determiner si 1 est dans 2 ou inversement
        for droite in coefs_droites1:
            for droite2 in coefs_droites2:
                # si aucune des deux droites n'est d'equation x=b
                if droite[0] != '' and droite2[0] != '':
                    # si les deux droites ont un coef directeur different
                    if droite[0] != droite2[0]:
                        # determination des coordonnees du point d'intersection des deux droites
                        X = (droite2[1] - droite[1]) / (droite[0] - droite2[0])
                        Y = droite[0]*X + droite[1]
                        pt_intersec = [X, Y]
                        compt_coll = 0
                        # si le pt d'intersection est dans le segment 1
                        if min(droite[2][0], droite[3][0]) <= pt_intersec[0] <= max(droite[2][0], droite[3][0]):
                            if min(droite[2][1], droite[3][1]) <= pt_intersec[1] <= max(droite[2][1], droite[3][1]):
                                compt2in1 += 1
                                compt_coll += 1
                        # si le pt d'intersection est dans le segment 2
                        if min(droite2[2][0], droite2[3][0]) <= pt_intersec[0] <= max(droite2[2][0], droite2[3][0]):
                            if min(droite2[2][1], droite2[3][1]) <= pt_intersec[1] <= max(droite2[2][1], droite2[3][1]):
                                compt1in2 += 1
                                compt_coll += 1
                        # si ce point fait parti du segment 1 et aussi du 2, alors il y a collision
                        if compt_coll == 2:
                            collision.append([droite, droite2])
                    # si elles ont le meme coef directeur
                    else:
                        # si elles ont egalement le meme second membre
                        if droite2[1] == droite[1]:
                            # si un des deux points extremes du segment 2 est dans le segment 1, alors il y a collision
                            if min(droite[2][0], droite[3][0]) <= droite2[2][0] <= max(droite[2][0], droite[3][0]):
                                collision.append([droite, droite2])
                                compt2in1 += 1
                            elif min(droite[2][0], droite[3][0]) <= droite2[3][0] <= max(droite[2][0], droite[3][0]):
                                collision.append([droite, droite2])
                                compt2in1 += 1
                            # si un des deux points extremes du segment 1 est dans le segment 2, alors il y a collision
                            if min(droite2[2][0], droite2[3][0]) <= droite[2][0] <= max(droite2[2][0], droite2[3][0]):
                                collision.append([droite, droite2])
                                compt1in2 += 1
                            elif min(droite2[2][0], droite2[3][0]) <= droite[3][0] <= max(droite2[2][0], droite2[3][0]):
                                collision.append([droite, droite2])
                                compt1in2 += 1
                # si les deux droites sont d'équation x=b
                elif droite[0] == '' and droite2[0] == '':
                    # si c'est le même b
                    if droite[1] == droite2[1]:
                        # si un des deux points extremes du segment 2 est dans le segment 1, alors il y a collision
                        if min(droite[2][0], droite[3][0]) <= droite2[2][0] <= max(droite[2][0], droite[3][0]):
                            collision.append([droite, droite2])
                            compt2in1 += 1
                        elif min(droite[2][0], droite[3][0]) <= droite2[3][0] <= max(droite[2][0], droite[3][0]):
                            collision.append([droite, droite2])
                            compt2in1 += 1
                        # si un des deux points extremes du segment 1 est dans le segment 2, alors il y a collision
                        if min(droite2[2][0], droite2[3][0]) <= droite[2][0] <= max(droite2[2][0], droite2[3][0]):
                            collision.append([droite, droite2])
                            compt1in2 += 1
                        elif min(droite2[2][0], droite2[3][0]) <= droite[3][0] <= max(droite2[2][0], droite2[3][0]):
                            collision.append([droite, droite2])
                            compt1in2 += 1
                # si seulement la premiere droite est d'equation x=b
                elif droite[0] == '':
                    X = droite[1]
                    Y = droite2[0]*X + droite2[1]
                    pt_intersec = [X, Y]
                    compt_coll = 0
                    # si le pt d'intersection est dans le segment 1
                    if min(droite[2][0], droite[3][0]) <= pt_intersec[0] <= max(droite[2][0], droite[3][0]):
                        if min(droite[2][1], droite[3][1]) <= pt_intersec[1] <= max(droite[2][1], droite[3][1]):
                            compt2in1 += 1
                            compt_coll += 1
                    # si le pt d'intersection est dans le segment 2
                    if min(droite2[2][0], droite2[3][0]) <= pt_intersec[0] <= max(droite2[2][0], droite2[3][0]):
                        if min(droite2[2][1], droite2[3][1]) <= pt_intersec[1] <= max(droite2[2][1], droite2[3][1]):
                            compt1in2 += 1
                            compt_coll += 1
                    # si ce point fait parti du segment 1 et aussi du 2, alors il y a collision
                    if compt_coll == 2:
                        collision.append([droite, droite2])
                # si seulement la seconde droite est d'equation x=b
                elif droite2[0] == '':
                    X = droite2[1]
                    Y = droite[0]*X + droite[1]
                    pt_intersec = [X, Y]
                    compt_coll = 0
                    # si le pt d'intersection est dans le segment 1
                    if min(droite[2][0], droite[3][0]) <= pt_intersec[0] <= max(droite[2][0], droite[3][0]):
                        if min(droite[2][1], droite[3][1]) <= pt_intersec[1] <= max(droite[2][1], droite[3][1]):
                            compt2in1 += 1
                            compt_coll += 1
                    # si le pt d'intersection est dans le segment 2
                    if min(droite2[2][0], droite2[3][0]) <= pt_intersec[0] <= max(droite2[2][0], droite2[3][0]):
                        if min(droite2[2][1], droite2[3][1]) <= pt_intersec[1] <= max(droite2[2][1], droite2[3][1]):
                            compt1in2 += 1
                            compt_coll += 1
                    # si ce point fait parti du segment 1 et aussi du 2, alors il y a collision
                    if compt_coll == 2:
                        collision.append([droite, droite2])

        # si un des rectangles est dans l'autre
        if compt2in1 == 16 or compt1in2 == 16 or ((ori1 - ori2) % 90 == 0 and (compt2in1 == 8 or compt1in2 == 8)):
            collision = True

    return collision


def collide_checker(to_update_j, to_update_b, obstacles):
    """
    Check les etats des objets et retourne une liste contenant les paires d'objets en collision

    a faire: automatiser l'information des dimensions des rect/rect orientés

    :param to_update_j:
    :param to_update_b:
    :param obstacles:
    :param tecran:
    :return:
    """
    obj_coll = []

    for k in range(len(to_update_j)):
        tuj = to_update_j[k]

        segmts_contact = collide_orient_rect([tuj[2], tuj[1][1], 60, 40], [to_update_b[2], 0, 20, 20])
        if segmts_contact:
            obj_coll.append(['JB', k, 0, segmts_contact])

        for i in range(len(to_update_j)):
            tuj2 = to_update_j[i]
            if k != i:
                segmts_contact = collide_orient_rect([tuj[2], tuj[1][1], 60, 40], [tuj2[2], tuj2[1][1], 60, 40])
                if segmts_contact:
                    obj_coll.append(['JJ', k, i, segmts_contact])

        for n in range(len(obstacles)):
            obst = obstacles[n]
            segmts_contact = collide_orient_rect([tuj[2], tuj[1][1], 60, 40], [obst.rect, 0, obst.rect[2], obst.rect[3]])
            if segmts_contact:
                obj_coll.append(['JO', k, n, segmts_contact])

    for n in range(len(obstacles)):
        obst = obstacles[n]
        segmts_contact = collide_orient_rect([obst.rect, 0, obst.rect[2], obst.rect[3]], [to_update_b[2], 0, 20, 20])
        if segmts_contact:
            obj_coll.append(['OB', n, 0, segmts_contact])

    return obj_coll

"""
def repos_collided_obj(obstacle, objet):
    # annule le mvt de l'objet (ainsi que son mvt de rotation) de sorte à ne plus être en collision avec l'obstacle
    # si la collision persiste, on ajoute autant le fois le mvt de l'obstacle que nécessaire pour l'empêcher

    [pos, vit, rect, mvts, long, larg] = objet
    if not isinstance(mvts[0], (float, int)):  # si c'est un joueur, il a un mvt et un mvt d'angle, sinon juste un mvt
        mvt, mvt_a = mvts[0], mvts[1]
    else:
        mvt, mvt_a = mvts, 0

    [posobst, vitobst, rectobst, mvtsobst, longobst, largobst] = obstacle
    if not isinstance(mvtsobst[0], (float, int)):  # si c'est un joueur, il a un mvt et un mvt d'angle, sinon juste mvt
        mvtobst = mvtsobst[0]
    else:
        mvtobst = mvtsobst

    # on annule le mvt de l'objet
    newmvt = [0, 0]
    newpos = [pos[0] - mvt[0], pos[1] - mvt[1]]
    newvit = [vit[0], vit[1] - mvt_a]
    if mvt_a != 0:
        newsurf = pygame.Surface([60, 40])
        newsurf = pygame.transform.rotate(newsurf, newvit[1])
        newrect = newsurf.get_rect(center=rect.center)
    else:
        newrect = rect
    newrect[0], newrect[1] = int(newpos[0]), int(newpos[1])

    # s'il y a toujours collision, on effectue en plus le mvt de l'obstacle, qui vient nécessairement vers l'objet
    k = 0
    while collide_orient_rect([newrect, newvit[1], long, larg], [rectobst, vitobst[1], longobst, largobst]):
        k += 1
        newmvt = [(mvtobst[0] - mvt[0]) * k, (mvtobst[1] - mvt[1]) * k]
        newpos = [newpos[0] + newmvt[0], newpos[1] + newmvt[1]]
        newrect[0], newrect[1] = int(newpos[0]), int(newpos[1])

    newobjet = [newpos, newvit, newrect, newmvt]
    return newobjet
"""


def check_collided_obj(obj, joueurs, obstacles):
    """
    check pour un objet, s'il est en contact avec d'autres objets vus comme des obstacles (obstacle ou joueur)
    :param obj: ballon ou joueur représenté par [rect, ori, long, larg] directement applicable à collide_orient_rect
    :param joueurs: vus comme des obstacles potentiels (représenté par son to_update)
    :param obstacles: vus comme des obstacles potentiels (représenté par sa forme objet)
    :return: liste dont les éléments sont composés d'une lettre indiquant si joueur ou obstacle, et le numéro corresp
    """
    collision = []

    # on vérifie si un des joueurs (qui n'est pas l'objet) est en contact avec l'objet
    for k in range(len(joueurs)):
        if joueurs[k] != obj and collide_orient_rect([joueurs[k][2], joueurs[k][1][1], 60, 40], obj):
            collision.append(['J', k])
    # on vérifie si un des obstacles est en contact avec l'objet
    for k in range(len(obstacles)):
        ob = obstacles[k]
        if collide_orient_rect([ob.rect, 0, ob.rect[2], ob.rect[3]], obj):
            collision.append(['O', k])

    return collision


def mvtback(tu):
    # fait revenir le to_update dans sa position précédante
    return [tu[3][0], tu[3][1], tu[3][2], tu[3]]


def calc_vit_reflexion(vit, ori_ref):
    # calcul du vecteur vitesse réflexion

    #print(f'ori_ref:\n {ori_ref}')
    #time.sleep(2)

    cosvit = math.cos((vit[1] - ori_ref) * math.pi / 180)
    sinvit = math.sin((vit[1] - ori_ref) * math.pi / 180)
    vitcompl_ref = vit[0] * (cosvit + 1j * sinvit)  # attention les y vers le bas?
    #print(f'cosvit, sinvit:\n {(round(cosvit, 2), round(sinvit, 2))}')
    #print(f'vit compl dans la nouvelle ref:\n {round(vitcompl_ref.real, 2) + 1j * round(vitcompl_ref.imag, 2)}')
    #time.sleep(2)

    nvitcompl_ref = abs(vitcompl_ref.real) + 1j * vitcompl_ref.imag
    #print(f'newvit compl dans la nouvelle ref:\n {round(nvitcompl_ref.real, 2) + 1j * round(nvitcompl_ref.imag, 2)}')
    #time.sleep(2)

    nvitcompl = nvitcompl_ref.real * math.cos(ori_ref * math.pi / 180) -\
                nvitcompl_ref.imag * math.sin(ori_ref * math.pi / 180) +\
                1j * (nvitcompl_ref.imag * math.cos(ori_ref * math.pi / 180) +
                      nvitcompl_ref.real * math.sin(ori_ref * math.pi / 180))
    #print(f'newvit compl:\n {round(nvitcompl.real, 2) + 1j * round(nvitcompl.imag, 2)}')
    #time.sleep(2)

    if nvitcompl.real != 0:
        newori = math.atan(nvitcompl.imag / nvitcompl.real) * 180 / math.pi
        if nvitcompl.real < 0:
            newori += 180
        newori = normal_angle(newori)
    elif nvitcompl.imag > 0:
        newori = 90
    elif nvitcompl.imag < 0:
        newori = -90
    else:  # newv = 0, 0
        newori = 0

    newori = round(newori, 0)
    #print(f'newori:\n {newori}')
    #time.sleep(2)

    return [vit[0], newori]


def calc_ori_ref(rect, segment):

    # attention: y est vers le bas

    # segment = [a, b, pt1, pt2]
    milieu_seg = [(segment[3][0] + segment[2][0]) / 2, (segment[3][1] + segment[2][1]) / 2]
    centre_rect = rect.center
    #print(f'milieu segment: {milieu_seg}\ncentre rect: {centre_rect}')

    if centre_rect[0] != milieu_seg[0]:
        ori_ref = math.atan(-1 * (milieu_seg[1] - centre_rect[1]) / (milieu_seg[0] - centre_rect[0])) * 180 / math.pi
        if milieu_seg[0] - centre_rect[0] < 0:
            ori_ref -= 180
        ori_ref = normal_angle(ori_ref)
    else:
        if milieu_seg[1] - centre_rect[1] > 0:
            ori_ref = -90
        else:  # milieu_seg[1] - centre_rect[1] < 0:
            ori_ref = 90

    return ori_ref


def calc_mvts(to_update_j_apri, to_update_b_apri, obstacles, drifts):
    """
    vérifie et modifie si besoin les nouveaux jeux de paramètres des joueurs et du ballon

    :param to_update_j_apri: liste des nouveaux jeux de paramètres [pos, vit, rect, tujinit] pour chaque joueur
    :param to_update_b_apri: liste du nouveau jeu de paramètres [pos, vit, rect, tubinit] pour le ballon
    :param obstacles: liste contenant les obstacles de la partie
    :param drifts: liste indiquant, pour chaque joueur, s'il drift
    :return: listes des nouveaux paramètres pour chaque joueur et le ballon, à appliquer aux méthodes update_dyn
    """
    #print('nouvelle boucle')

    # tant que des objets sont en collision
    collisions = collide_checker(to_update_j_apri, to_update_b_apri, obstacles)
    while collisions:

        #for colli in collisions:
        #    print(colli[:3])

        for colli in collisions:

            # nouvelle methode plus simple: tous les objets en collision sont replacés où ils étaient juste avant
            # et on change leur vitesse selon le choc

            if colli[0] == 'JB':

                tuj = to_update_j_apri[colli[1]]
                tub = to_update_b_apri
                #print(f'tuj: {tuj}\ntub: {tub}')

                # on replace les rect où ils étaient à l'instant d'avant, normalement il ne se touchent donc pas
                newtub = mvtback(tub)
                newtuj = mvtback(tuj)

                # on verifie qu'il n'y avait pas d'autre collision avec le ballon
                autre_coll = False
                # on check d'abord toutes les collisions du même instant
                for autre_colli in collisions:
                    if autre_colli != colli:

                        # si un autre joueur tape le ballon
                        if autre_colli[0] == 'JB':
                            autre_coll = True

                            # on replace également ce joueur
                            tuj_autre = to_update_j_apri[autre_colli[1]]
                            newtuj_autre = mvtback(tuj_autre)
                            # on inverse sa vitesse
                            newvitj_autre = [-newtuj_autre[1][0], newtuj_autre[1][1]]
                            newtuj_autre[1] = newvitj_autre
                            # on change le tuj correspondant dans la liste des tuj
                            to_update_j_apri[autre_colli[1]] = newtuj_autre
                            # on enleve la collision de la liste car on vient de la traiter
                            collisions.remove(autre_colli)

                        # si le ballon tape un obstacle
                        elif autre_colli[0] == 'OB':
                            autre_coll = True

                            # on enleve la collision de la liste car on vient de la traiter
                            collisions.remove(autre_colli)

                # s'il n'y a pas d'autres collisions au meme instant, on déroule en vérifiant à la fin si le nouveau tub
                # ne va pas entrer en collision avec autre chose à l'instant suivant, si oui on considere autre_coll

                # on détermine alors la nouvelle vitesse du ballon:

                # s'il n'y a pas eu d'autre collision avec le ballon
                if not autre_coll:

                    listevectplot = [newtub[1]]  # pour contenir les vecteurs à plotter pour faire des tests

                    # détermine le vecteur reflecteur du joueur
                    ori_ref = calc_ori_ref(tuj[2], colli[3][0][0])
                    coll_plusieurs_cotes = False
                    limites_ori = []
                    if len(colli[3]) > 1:  # si pluseuirs côtés du joueur sont en contact avec le ballon
                        #print('plusieurs cotés du joueur touchés')
                        coll_plusieurs_cotes = True
                        limites_ori = [round(normal_angle(ori_ref), 2)]
                        vect_ref = [1, ori_ref]
                        for k in range(1, len(colli[3])):
                            ori_ref = calc_ori_ref(tuj[2], colli[3][k][0])
                            limites_ori.append(round(normal_angle(ori_ref), 2))
                            vect_ref = somme_vect(vect_ref, [1, ori_ref])
                        ori_ref = vect_ref[1]
                    #print(f'ori_ref du joueur: {ori_ref}')
                    listevectplot.append([10, ori_ref])

                    # déduit la vitesse de réflexion du ballon sur le joueur
                    newvitb = calc_vit_reflexion(newtub[1], ori_ref)
                    # il faut que le ballon ne rebondisse pas vers le joueur, ce qui peut arriver s'il tape un coin
                    if coll_plusieurs_cotes:
                        # apriori il y a 2 limites_ori, avec un écart de 90°
                        limites_ori.sort()
                        if limites_ori[-1] > 270 and limites_ori[0] < 90:
                            limites_ori[0] += 360
                            limites_ori.sort()
                        #print(f'newvitb[1] calculée: {newvitb[1]}')
                        #print(f'encadrement de la vitesse de réflexion du ballon entre:\n{limites_ori}')
                        if not limites_ori[0] <= newvitb[1] <= limites_ori[1]:
                            if newvitb[1] > limites_ori[0]:
                                newvitb[1] = limites_ori[0]
                            else:
                                newvitb[1] = limites_ori[1]
                    #print(f'vitesse ballon reflechie:\n{newvitb}')
                    listevectplot.append(newvitb)

                    # détermine et applique la composante de vitesse associée au shoot
                    cos_vitj_ref = math.cos(normal_angle(newtuj[1][1] - ori_ref) * math.pi / 180)
                    if newtuj[1][0] < 0:
                        cos_vitj_ref *= -1
                    #print(f'cos (vref, vitj):\n{round(cos_vitj_ref, 2)}')
                    if cos_vitj_ref > 0:
                        if newtuj[1][0] > 0:
                            vitshoot = [2 * newtuj[1][0] * cos_vitj_ref, newtuj[1][1]]
                        else:
                            vitshoot = [2 * -newtuj[1][0] * cos_vitj_ref, normal_angle(newtuj[1][1] - 180)]
                    elif cos_vitj_ref == 0:
                        if newtuj[1][0] > 0:
                            vitshoot = [0.5 * newtuj[1][0], newtuj[1][1]]
                        else:
                            vitshoot = [0.5 * -newtuj[1][0], normal_angle(newtuj[1][1] - 180)]
                    else:
                        vitshoot = [0, 0]
                    newvitb = somme_vect(newvitb, vitshoot)
                    #print(f'vitesse ballon shooté: {newvitb}')
                    listevectplot.append(vitshoot)
                    listevectplot.append(newvitb)

                    # on vérifie qu'on ne dépasse pas la limite de vitesse
                    if newvitb[0] > 12:
                        newvitb[0] = 12

                    newvitb = [round(newvitb[0], 2), round(newvitb[1], 0)]
                    #print(f'vitesse finale ballon:\n{newvitb}')

                    # plot pour tests
                    """
                    col = ['b', 'r', 'y', 'm', 'g']
                    leg = ['vitb', 'réflecteur', 'vitb réfléchie', 'vitshoot', 'newvitb']
                    fig, ax = plt.subplots()
                    ax.axis([-15, 15, -15, 15])
                    for k in range(len(listevectplot)):
                        vect = listevectplot[k]
                        if k != 3:
                            ax.arrow(0, 0, vect[0] * math.cos(vect[1] * math.pi / 180),
                                     vect[0] * math.sin(vect[1] * math.pi / 180),
                                     color=col[k], head_width=0.5, label=leg[k])
                            ax.plot([0, vect[0] * math.cos(vect[1] * math.pi / 180)],
                                    [0, vect[0] * math.sin(vect[1] * math.pi / 180)],
                                    color=col[k], label=leg[k])
                            ax.legend(loc='upper center', shadow=True)
                        else:
                            vitbref = listevectplot[2]
                            x0 = vitbref[0] * math.cos(vitbref[1] * math.pi / 180)
                            y0 = vitbref[0] * math.sin(vitbref[1] * math.pi / 180)
                            ax.arrow(x0, y0,
                                     vect[0] * math.cos(vect[1] * math.pi / 180),
                                     vect[0] * math.sin(vect[1] * math.pi / 180),
                                     color=col[k], head_width=0.5, label=leg[k])
                            ax.plot([x0, x0 + vect[0] * math.cos(vect[1] * math.pi / 180)],
                                    [y0, y0 + vect[0] * math.sin(vect[1] * math.pi / 180)],
                                    color=col[k], label=leg[k])
                            ax.legend(loc='upper center', shadow=True)
                    plt.show()
                    """
                    # on check aussi l'instant suivant au cas ou le ballon tape alternativement le tireur et autre chose

                    # détermine le rect du ballon à l'instant suivant, selon la vitesse qu'on vient de calculer
                    nextmvtb = calc_mvt(newvitb)
                    nextposb = [round(newtub[0][0] + nextmvtb[0], 2), round(newtub[0][1] + nextmvtb[1], 2)]
                    nextrectb = newtub[2].copy()
                    nextrectb[0], nextrectb[1] = nextposb[0], nextposb[1]
                    # on check s'il sera en collision avec un objet
                    if check_collided_obj([nextrectb, 0, 20, 20], to_update_j_apri, obstacles):
                        autre_coll = True

                # s'il y a eu d'autres collision avec le ballon
                if autre_coll:
                    #print('plusieurs collisions avec le ballon')
                    # a ameliorer
                    # le ballon est immobilisé
                    newvitb = [0, 0]
                    # on inverse la vitesse du tireur
                    newvitj = [-newtuj[1][0], newtuj[1][1]]
                    newtuj[1] = newvitj

                    # test: on donne au ballon la moitié de la nouvelle vitesse du joueur, puis verif
                    if newvitj[0] < 0:
                        newvitb = [round(-newvitj[0] / 2, 2), normal_angle(newvitj[1] + 180)]
                    else:
                        newvitb = [round(newvitj[0] / 2, 2), newvitj[1]]
                    # détermine le rect du ballon à l'instant suivant, selon la vitesse qu'on vient de calculer
                    nextmvtb = calc_mvt(newvitb)
                    nextposb = [round(newtub[0][0] + nextmvtb[0], 2), round(newtub[0][1] + nextmvtb[1], 2)]
                    nextrectb = newtub[2].copy()
                    nextrectb[0], nextrectb[1] = nextposb[0], nextposb[1]
                    # pareil avec le tireur
                    nextmvtj = calc_mvt(newvitj)
                    nextposj = [round(newtuj[0][0] + nextmvtj[0], 2), round(newtuj[0][1] + nextmvtj[1], 2)]
                    nextrectj = newtuj[2].copy()
                    nextrectj[0], nextrectj[1] = nextposj[0], nextposj[1]
                    next_tuJ_apri = to_update_j_apri
                    next_tuJ_apri[colli[1]][2] = nextrectj
                    # on check si le ballon sera en collision avec un objet
                    if check_collided_obj([nextrectb, 0, 20, 20], next_tuJ_apri, obstacles):
                        newtub = mvtback(newtub)
                        newvitb = [0, 0]

                newtub[1] = newvitb

                to_update_j_apri[colli[1]] = newtuj
                to_update_b_apri = newtub

            elif colli[0] == 'OB':

                obst = obstacles[colli[1]]
                tub = to_update_b_apri
                #print(f'tub: {tub}\nrectobst: {obst.rect}')

                # on replace le ballon ou il était
                newtub = mvtback(tub)

                # détermine le vecteur reflecteur de l'obstacle
                ori_ref = calc_ori_ref(obst.rect, colli[3][0][0])
                coll_plusieurs_cotes = False
                limites_ori = []
                if len(colli[3]) > 1:  # si plusieurs côtés de l'obstacle sont en contact avec le ballon
                    coll_plusieurs_cotes = True
                    limites_ori = [round(normal_angle(ori_ref), 2)]
                    vect_ref = [1, ori_ref]
                    for k in range(1, len(colli[3])):
                        ori_ref = calc_ori_ref(obst.rect, colli[3][k][0])
                        limites_ori.append(round(normal_angle(ori_ref), 2))
                        vect_ref = somme_vect(vect_ref, [1, ori_ref])
                    ori_ref = vect_ref[1]
                #print(f'ori_ref obst: {ori_ref}')

                # déduit la vitesse de réflexion du ballon sur l'obstacle
                newvitb = calc_vit_reflexion(newtub[1], ori_ref)
                # il faut que le ballon ne rebondisse pas vers l'obstacle, ce qui peut arriver s'il tape un coin
                if coll_plusieurs_cotes and limites_ori[0] != limites_ori[1]:
                    # apriori il y a 2 limites_ori, avec un écart de 90°, et l'obstacle est fixe (4 ori possibles)
                    limites_ori.sort()
                    if limites_ori[-1] == 270 and limites_ori[0] == 0:
                        limites_ori[0] = 360
                        limites_ori.sort()
                    #print(f'newvitb[1] calculée: {newvitb[1]}')
                    #print(f'encadrement de la vitesse de réflexion du ballon entre:\n{limites_ori}')
                    if not limites_ori[0] <= newvitb[1] <= limites_ori[1]:
                        if newvitb[1] > limites_ori[0]:
                            newvitb[1] = limites_ori[0]
                        else:
                            newvitb[1] = limites_ori[1]
                #print(f'newvitb: {newvitb}')

                newtub[1] = newvitb

                to_update_b_apri = newtub

            elif colli[0] == 'JJ':

                tuj = to_update_j_apri[colli[1]]
                tuj2 = to_update_j_apri[colli[2]]
                #print(f'tuj: {tuj}\ntuj2: {tuj2}')

                # on replace les joueurs où ils étaient
                newtuj = mvtback(tuj)
                newtuj2 = mvtback(tuj2)

                # inverse la vitesse de chaque joueur
                newtuj[1][0] *= -1
                newtuj2[1][0] *= -1

                to_update_j_apri[colli[1]] = newtuj
                to_update_j_apri[colli[2]] = newtuj2

                # on supprime de la liste la collision indiquant le même chose vu par l'autre joueur
                for co in collisions:
                    if co[0] == 'JJ' and co[1] == colli[2] and co[2] == colli[1]:
                        collisions.remove(co)

            else:  # colli[0] == 'JO'

                tuj = to_update_j_apri[colli[1]]
                obst = obstacles[colli[2]]
                #print(f'tuj: {tuj}\nrectobst: {obst.rect}')

                # on replace le joueur où il était
                newtuj = mvtback(tuj)

                # inverse la vitesse du joueur
                newtuj[1][0] *= -1

                to_update_j_apri[colli[1]] = newtuj

        # on check tant que les replacements effectués entrainent d'autres chocs
        collisions = collide_checker(to_update_j_apri, to_update_b_apri, obstacles)

    # ne garde que [pos, vit] des to_update
    to_update_j = []
    for tuj in to_update_j_apri:
        to_update_j.append(tuj[:2])

    to_update_b = to_update_b_apri[:2]

    return to_update_j, to_update_b
