import pygame
import math
import time

from Utiles import normal_angle, calc_mvt, somme_vect
from Calc_mvts import calc_mvts, collide_orient_rect


class Joueur:

    TAILLE = [60, 40]
    LIMVIT_NORM, LIMVIT_UP = 5, 8
    LIMVITARR_NORM, LIMVITARR_UP = 4, 6
    COEF_FROTT = 0.95

    def __init__(self, Num, Nom, NomImage):
        # attributs généraux
        self.numero = Num
        self.nom = Nom
        self.nomImage = NomImage
        # attributs dynamiques
        self.pos = [0, 0]  # position du centre du joueur en coordonnées x,y
        self.vit = [0, 0]  # norme et angle
        self.acc = 0
        self.sensroues = 0  # 1 si les roues font aller vers la gauche, -1 vers la droite, 0 tout droit
        self.oridrift = -1  # prend la place de vit[1] dans le calcul du mvt si le joueur drift, sinon vaut -1
        self.surf0 = pygame.Surface(self.TAILLE)
        self.surf = self.surf0
        self.rect = self.surf.get_rect()
        self.rect[0], self.rect[1] = self.pos[0], self.pos[1]
        # attributs concernant la vitesse max
        self.compteur_fin_bonus_vit = 0
        self.limite_vit = self.LIMVIT_NORM
        self.limite_vitarr = self.LIMVITARR_NORM
        # score
        self.score = 0

    def update_infos(self, Nom, NomImage):
        self.nom = Nom
        self.nomImage = NomImage

    def update_dyn(self, to_update):

        [npos, nvit] = to_update

        self.pos = npos
        self.vit = nvit

        self.surf = pygame.transform.rotate(self.surf0, self.vit[1])
        self.rect = self.surf.get_rect()  # center=self.rect.center)
        self.rect[0], self.rect[1] = int(self.pos[0]), int(self.pos[1])

    # fonctions de gestion pour les bonus de vitesse
    def bonus_vit(self):
        self.limite_vit = self.LIMVIT_UP
        self.limite_vitarr = self.LIMVITARR_UP
        self.compteur_fin_bonus_vit = 400

    def fin_bonus_vit(self):
        if self.limite_vit == self.LIMVIT_UP:
            self.compteur_fin_bonus_vit -= 1
            if self.compteur_fin_bonus_vit == 0:
                self.limite_vit = self.LIMVIT_NORM
                self.limite_vitarr = self.LIMVITARR_NORM


class Ballon:

    TAILLE = [20, 20]
    LIMVIT = 12
    COEF_FROTT = 0.995

    def __init__(self):
        self.pos = [0, 0]
        self.vit = [0, 0]
        self.surf = pygame.Surface(self.TAILLE)
        self.rect = self.surf.get_rect()
        self.rect[0], self.rect[1] = self.pos[0], self.pos[1]

    def update_dyn(self, to_update):

        [npos, nvit] = to_update

        self.pos = npos
        self.vit = nvit
        self.rect[0], self.rect[1] = self.pos[0], self.pos[1]


class Obstacle:

    def __init__(self, position, taille):
        self.surf = pygame.Surface(taille)
        self.pos = position
        self.rect = self.surf.get_rect()
        self.rect[0], self.rect[1] = self.pos[0], self.pos[1]


class Cage:

    def __init__(self, position, taille):
        self.surf = pygame.Surface(taille)
        self.pos = position
        self.rect = self.surf.get_rect()
        self.rect[0], self.rect[1] = self.pos[0], self.pos[1]


class BonusVit:

    TAILLE = [30, 30]

    def __init__(self, position):
        self.surf = pygame.Surface(self.TAILLE)
        self.pos = position
        self.rect = self.surf.get_rect()
        self.rect[0], self.rect[1] = self.pos[0], self.pos[1]
        self.actif = False
        self.compteur_reactivation = 0

    def activation(self):
        self.actif = True

    def desactivation(self):
        self.actif = False
        self.compteur_reactivation = 1000

    def compt_reacti(self):
        if not self.actif:
            self.compteur_reactivation -= 1
            if self.compteur_reactivation == 0:
                self.activation()


class Equipe:

    def __init__(self, numequipe, numjoueurs):
        self.Num = numequipe
        self.NumJoueurs = numjoueurs
        self.score = 0


class Partie:

    def __init__(self, parametres):

        self.params = parametres
        [NBR_JOUREURS, PROLO, TEMPS] = self.params

        self.prolongations = False
        self.gameover = False

        self.clock = pygame.time.Clock()

        self.TailleEcran = [1250, 650]

        self.Obstacles = gen_obstacles(self.TailleEcran)

        ProfondeurBut, LargueurBut = 50, 100
        self.Cages, obstcages = gen_but(self.TailleEcran, LargueurBut, ProfondeurBut)
        self.Obstacles += obstcages

        self.Bonus_vitesse = gen_bonus_vitesse(self.TailleEcran)

        self.joueurs = []
        for k in range(NBR_JOUREURS):
            self.joueurs.append(Joueur(k, '', ''))

        if NBR_JOUREURS == 2:
            self.equipe = [Equipe(1, [self.joueurs[0]]), Equipe(2, [self.joueurs[1]])]
        else:  # NBR_JOUEURS == 4
            self.equipe = [Equipe(1, [self.joueurs[0], self.joueurs[1]]), Equipe(2, [self.joueurs[2], self.joueurs[3]])]

        self.ballon = Ballon()

        self.engagement()  # erreur si pas 2 ou 4 joueurs

        self.FPS = 60
        self.Temps = TEMPS * self.FPS

    # utilise les commandes des joueurs pour faire avancer le jeu et générer un message pour les clients
    def resoudre(self, commandesjoueurs):

        # on avance le temps
        # s'il reste du temps:
        # on récupère les commandes des joueurs
        # on calcule a priori la liste de variables to_update du ballon et de chaque joueur
        # on passe ces to_update dans la fonction calc_mvts qui résout les chocs
        # on recupere les to_update a posteriori (aucun choc) pour modifier les objets correspondant
        # on active les boost, on check s'il y a un but et on applique les conséquences
        # enfin, on envoie à chaque client les pos et ori des objets afin qu'il les affiche, ou une notification
        # pour signaler un but, la fin du match ou des prolongations

        notification = None

        # on avance le temps
        self.clock.tick(self.FPS)
        if self.Temps != 0 and not self.prolongations:
            self.Temps -= 1
        elif self.prolongations:
            self.Temps += 1
        else:
            if self.params[1] and self.equipe[0].score == self.equipe[1].score:
                self.prolongations = True
                notification = "Prolongations"
                self.engagement()
            else:
                self.gameover = True
                notification = "GameOver"

        # création de la liste indiquant, pour chaque joueur, s'il drift (l'élément k passe à True si le joueur k drift)
        drifts = [False] * self.params[0]

        # récupération des commandes des joueurs
        for k in range(self.params[0]):
            if commandesjoueurs[k][0]:
                self.joueurs[k].acc = 1
            if commandesjoueurs[k][1]:
                self.joueurs[k].acc = -1
            if not (commandesjoueurs[k][0] or commandesjoueurs[k][1]) or\
                    (commandesjoueurs[k][0] and commandesjoueurs[k][1]):
                self.joueurs[k].acc = 0
            if commandesjoueurs[k][2]:
                self.joueurs[k].sensroues = 1
            if commandesjoueurs[k][3]:
                self.joueurs[k].sensroues = -1
            if not (commandesjoueurs[k][2] or commandesjoueurs[k][3]) or\
                    (commandesjoueurs[k][2] and commandesjoueurs[k][3]):
                self.joueurs[k].sensroues = 0
            if commandesjoueurs[k][4]:
                if self.joueurs[k].oridrift == -1:
                    self.joueurs[k].oridrift = self.joueurs[k].vit[1]
                drifts[k] = True
            else:
                self.joueurs[k].oridrift = -1

        # calcul des to_update pour les joueurs
        to_update_j_apri = []
        for j in self.joueurs:

            # nouveau vecteur vitesse
            mod_newvit = j.COEF_FROTT * j.vit[0] + j.acc
            if abs(mod_newvit) > 1:
                mvt_a = j.sensroues * math.sqrt(abs(mod_newvit)) * mod_newvit / abs(mod_newvit)
                mvt_a = int(mvt_a)
                a_newvit = j.vit[1] + mvt_a
            else:
                mvt_a = 0
                a_newvit = j.vit[1]
            newvit = [mod_newvit, normal_angle(a_newvit)]
            if newvit[0] >= j.limite_vit:
                newvit[0] = j.limite_vit
            if newvit[0] <= -j.limite_vitarr:
                newvit[0] = -j.limite_vitarr
            # transforme une faible vitesse en immobilisation + réduction de la quantité d'infomations via la précision
            if abs(newvit[0]) < 1:
                newvit[0] **= 2
            newvit = [round(newvit[0], 2), round(newvit[1], 0)]

            # mouvement (selon si drift ou non)
            if j.oridrift == -1:
                mvt = calc_mvt(newvit)
            else:
                newvit[0] *= 0.8
                vitdrift = somme_vect([newvit[0] / 40, newvit[1]], [39 * newvit[0] / 40, j.oridrift])
                if newvit[0] < 0:
                    vitdrift[1] = normal_angle(vitdrift[1] + 180)
                    j.oridrift = vitdrift[1]
                    mvt = calc_mvt([-vitdrift[0], vitdrift[1]])
                else:
                    j.oridrift = vitdrift[1]
                    mvt = calc_mvt(vitdrift)

            # nouvelle position
            newpos = [j.pos[0] + mvt[0], j.pos[1] + mvt[1]]

            # réduction de la précision afin de réduire le volume d'infos à transmettre (reste précis tout de même)
            #newvit = [round(newvit[0], 2), round(newvit[1], 0)]
            newpos = [round(newpos[0], 2), round(newpos[1], 2)]

            # nouvelle surf et rect
            newsurf = pygame.transform.rotate(j.surf0, newvit[1])
            newrect = newsurf.get_rect(center=j.rect.center)
            newrect[0], newrect[1] = int(newpos[0]), int(newpos[1])

            # to_update_j_apri.append([newpos, newvit, newrect, [mvt, mvt_a]])
            to_update_j_apri.append([newpos, newvit, newrect, [j.pos, j.vit, j.rect.copy()]])

        # calcul du to_update du ballon
        # vitesse ballon
        newvit = [self.ballon.COEF_FROTT * self.ballon.vit[0], self.ballon.vit[1]]
        # transforme une faible vitesse en immobilisation + réduction de la quantité d'infomations via la précision
        if abs(newvit[0]) < 1:
            newvit[0] **= 2
        newvit = [round(newvit[0], 2), round(newvit[1], 0)]

        # position ballon
        mvt = calc_mvt(newvit)
        newpos = [self.ballon.pos[0] + mvt[0], self.ballon.pos[1] + mvt[1]]
        #réduction de la qté d'infos via la précision
        newpos = [round(newpos[0], 2), round(newpos[1], 2)]

        #rect ballon
        newrect = self.ballon.rect.copy()
        newrect[0], newrect[1] = int(newpos[0]), int(newpos[1])

        # réduction de la précision afin de réduire le volume d'infos à transmettre (reste précis tout de même)
        #newvit = [round(newvit[0], 2), round(newvit[1], 0)]
        #newpos = [round(newpos[0], 2), round(newpos[1], 2)]

        # to_update_b_apri = [newpos, newvit, newrect, mvt]
        to_update_b_apri = [newpos, newvit, newrect, [self.ballon.pos, self.ballon.vit, self.ballon.rect]]

        # application de calc_mvts
        to_update_j, to_update_b = calc_mvts(to_update_j_apri, to_update_b_apri, self.Obstacles, drifts)

        # update des objets
        for k in range(len(self.joueurs)):
            self.joueurs[k].update_dyn(to_update_j[k])
        self.ballon.update_dyn(to_update_b)

        # récupération éventuelle des bonus de vitesse
        self.gestion_bonus_vitesse()

        # but éventuel
        if self.check_goal():
            if not self.prolongations:
                notification = "But"
                self.engagement()
            else:
                notification = "GameOver"
                self.prolongations = False
                self.gameover = True

        # création du message pour les clients
        if notification is None:
            msgclient = [[self.ballon.pos]]
            for j in self.joueurs:
                msgclient.append([j.pos, j.vit[1]])
            bonusactifs = []
            for b in self.Bonus_vitesse:
                bonusactifs.append(b.actif)
            msgclient.append([bonusactifs, self.Temps // self.FPS])
        else:
            msgclient = [notification]
            if notification == "GameOver":
                msgclient.append([self.equipe[0].score, self.equipe[1].score])
            elif notification == "But":
                msgclient.append([self.equipe[0].score, self.equipe[1].score])
            elif notification == "Prolongations":
                pass

        return msgclient

    # replace et initialise les bonus de vitesse, les joueurs et le ballon pour un nouvel engagement
    def engagement(self):

        tecran = self.TailleEcran

        for bonus in self.Bonus_vitesse:
            bonus.activation()

        for j in self.joueurs:
            # on s'assure qu'il n'a plus de bonus
            j.compteur_fin_bonus_vit = 1
            j.fin_bonus_vit()
            # s'il y a 2 joueurs
            if self.params[0] == 2:
                if j.numero == 0:
                    j.update_dyn([[tecran[0] // 4 - j.rect[2] // 2, tecran[1] // 2 - j.rect[3] // 2], [0, 0]])
                elif j.numero == 1:
                    j.update_dyn([[(3 * tecran[0]) // 4 - j.rect[2] // 2, tecran[1] // 2 - j.rect[3] // 2], [0, 180]])
            # s'il y a 4 joueurs
            elif self.params[0] == 4:
                if j.numero == 0:
                    j.update_dyn([[tecran[0] // 4 - j.rect[2] // 2, tecran[1] // 4 - j.rect[3] // 2], [0, 0]])
                elif j.numero == 1:
                    j.update_dyn([[(tecran[0]) // 4 - j.rect[2] // 2, 3 * tecran[1] // 4 - j.rect[3] // 2], [0, 0]])
                elif j.numero == 2:
                    j.update_dyn([[(3 * tecran[0]) // 4 - j.rect[2] // 2, tecran[1] // 4 - j.rect[3] // 2], [0, 180]])
                elif j.numero == 3:
                    j.update_dyn(
                        [[(3 * tecran[0]) // 4 - j.rect[2] // 2, 3 * tecran[1] // 4 - j.rect[3] // 2], [0, 180]])

        self.ballon.update_dyn([[(tecran[0] - self.ballon.rect[2]) // 2, (tecran[1] - self.ballon.rect[3]) // 2], [0, 0]])

    def gestion_bonus_vitesse(self):
        # gestion de la récupération des bonus de vitesse, ses effets et la réactivation des bonus inactifs

        # pour chaque bonus de vitesse, on verifie si un joueur le recupere
        # et s'il est inactif, on fait avancer sa fonction de reactivation
        for bonus in self.Bonus_vitesse:
            if bonus.actif:
                for j in self.joueurs:
                    if collide_orient_rect([j.rect, j.vit[1], 60, 40], [bonus.rect, 0, bonus.rect[2], bonus.rect[3]]):
                        j.bonus_vit()
                        bonus.desactivation()
            bonus.compt_reacti()

        # si des joueurs sont sous l'effet d'un bonus de vitesse, leur compteur de fin de bonus s'incremente
        for j in self.joueurs:
            j.fin_bonus_vit()

    def check_goal(self):

        goal = False
        for k in range(2):
            if self.Cages[k].rect.contains(self.ballon.rect):
                self.equipe[k].score += 1
                goal = True

        return goal


def gen_obstacles(TailleEcran):

    epai = 15  # epaisseur des obstacles

    # on ne les voit pas, ils servent juste a faire rebondir le joueur s'il tire sur le ballon trop proche du bord
    obstacles = [
        Obstacle([-epai, -epai], [TailleEcran[0] + 2 * epai, epai]),
        Obstacle([-epai, -epai], [epai, TailleEcran[1] + 2 * epai]),
        Obstacle([-epai, TailleEcran[1]], [TailleEcran[0] + 2 * epai, epai]),
        Obstacle([TailleEcran[0], -epai], [epai, TailleEcran[1] + 2 * epai])
    ]

    return obstacles


def gen_but(TailleEcran, LargBut, ProfBut):

    # cages
    cages = [
        Cage([TailleEcran[0] - ProfBut, (TailleEcran[1] - LargBut) // 2], [ProfBut, LargBut]),
        Cage([0, (TailleEcran[1] - LargBut) // 2], [ProfBut, LargBut])
    ]

    # poteaux
    TaillePoteaux = 15
    ObstCages = [
        Obstacle([0, (TailleEcran[1] - LargBut) // 2 - TaillePoteaux], [ProfBut, TaillePoteaux]),
        Obstacle([0, (TailleEcran[1] + LargBut) // 2], [ProfBut, TaillePoteaux]),

        Obstacle([TailleEcran[0] - ProfBut, (TailleEcran[1] - LargBut) // 2 - TaillePoteaux], [ProfBut, TaillePoteaux]),
        Obstacle([TailleEcran[0] - ProfBut, (TailleEcran[1] + LargBut) // 2], [ProfBut, TaillePoteaux])
    ]

    return cages, ObstCages


def gen_bonus_vitesse(TailleEcran):

    taille_bonus = 30
    bonus = [BonusVit([TailleEcran[0] // 10 - taille_bonus // 2, TailleEcran[1] // 8 - taille_bonus // 2]),
             BonusVit([9 * TailleEcran[0] // 10 - taille_bonus // 2, TailleEcran[1] // 8 - taille_bonus // 2]),
             BonusVit([TailleEcran[0] // 10 - taille_bonus // 2, 7 * TailleEcran[1] // 8 - taille_bonus // 2]),
             BonusVit([9 * TailleEcran[0] // 10 - taille_bonus // 2, 7 * TailleEcran[1] // 8 - taille_bonus // 2])]

    return bonus
