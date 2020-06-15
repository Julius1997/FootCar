import pygame


class Joueur:

    TAILLE = [60, 40]

    def __init__(self, Num, Nom, NomImage):
        # attributs généraux
        self.numero = Num
        self.nom = Nom
        self.nomImage = NomImage
        # attributs dynamiques
        self.pos = [0, 0]  # position du centre du joueur en coordonnées x,y
        self.ori = 0
        self.image0 = pygame.Surface(self.TAILLE)
        self.image = self.image0
        self.rect = self.image0.get_rect()
        self.rect[0], self.rect[1] = self.pos[0], self.pos[1]
        # score
        self.score = 0

    def update_infos(self, Nom, NomImage):
        self.nom = Nom
        self.nomImage = NomImage

    def load_image(self):
        self.image0 = pygame.image.load(self.nomImage).convert()
        self.image0.set_colorkey((0, 0, 0))  # pour n'afficher que l'image quelle que soit l'orientation du joueur
        self.image0 = pygame.transform.rotate(self.image0, -90)
        self.image = self.image0

    def update_dyn(self, npos, nori):
        self.pos = npos
        self.ori = nori
        self.image = pygame.transform.rotate(self.image0, self.ori)
        self.rect = self.image.get_rect()
        self.rect[0], self.rect[1] = self.pos[0], self.pos[1]

    def get_cmds(self):
        keys = pygame.key.get_pressed()
        return [keys[pygame.K_UP], keys[pygame.K_DOWN], keys[pygame.K_LEFT], keys[pygame.K_RIGHT], keys[pygame.K_d]]


class Ballon:

    TAILLE = [20, 20]

    def __init__(self):
        self.pos = [0, 0]
        self.surf = pygame.Surface(self.TAILLE)
        self.surf.fill((200, 200, 200))
        self.rect = self.surf.get_rect()
        self.rect[0], self.rect[1] = self.pos[0], self.pos[1]

    def update_dyn(self, npos):
        self.pos = npos
        self.rect[0], self.rect[1] = self.pos[0], self.pos[1]


class Obstacle:

    def __init__(self, position, taille):
        self.surf = pygame.Surface(taille)
        self.surf.fill((0, 0, 0))
        self.pos = position
        self.rect = self.surf.get_rect()
        self.rect[0], self.rect[1] = self.pos[0], self.pos[1]


class Cage:

    def __init__(self, position, taille):
        self.surf = pygame.Surface(taille)
        self.surf.fill((100, 200, 100))
        self.pos = position
        self.rect = self.surf.get_rect()
        self.rect[0], self.rect[1] = self.pos[0], self.pos[1]


class BonusVit:

    TAILLE = [30, 30]
    surf_act = pygame.Surface(TAILLE)
    surf_act.fill((200, 0, 0))
    surf_desact = pygame.Surface(TAILLE)
    surf_desact.fill((100, 0, 0))

    def __init__(self, position):
        self.surf = self.surf_desact
        self.pos = position
        self.rect = self.surf.get_rect()
        self.rect[0], self.rect[1] = self.pos[0], self.pos[1]
        self.actif = False

    def activation(self):
        self.actif = True
        self.surf = self.surf_act

    def desactivation(self):
        self.actif = False
        self.surf = self.surf_desact


class Equipe:

    def __init__(self, numequipe, numjoueurs):
        self.Num = numequipe
        self.NumJoueurs = numjoueurs
        self.score = 0


class Partie:

    def __init__(self, parametres):

        self.params = parametres
        [NBR_JOUREURS, PROLO, TEMPS] = self.params

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
            self.equipe = [Equipe(1, [self.joueurs[0].numero]), Equipe(2, [self.joueurs[1].numero])]
        else:  # NBR_JOUEURS == 4
            self.equipe = [Equipe(1, [self.joueurs[0].numero, self.joueurs[1].numero]),
                           Equipe(2, [self.joueurs[2].numero, self.joueurs[3].numero])]

        self.ballon = Ballon()

        self.Temps = TEMPS

    # mise à jour des différents objets de la partie
    def update(self, dataserveur):

        # ballon
        self.ballon.update_dyn(dataserveur[0][0])

        # joueurs
        for k in range(self.params[0]):
            self.joueurs[k].update_dyn(dataserveur[k + 1][0], dataserveur[k + 1][1])

        # bonus de vitesse
        for k in range(len(self.Bonus_vitesse)):
            if dataserveur[-1][0][k] != self.Bonus_vitesse[k].actif:
                if self.Bonus_vitesse[k].actif:
                    self.Bonus_vitesse[k].desactivation()
                else:
                    self.Bonus_vitesse[k].activation()

        # temps
        self.Temps = dataserveur[-1][1]


def gen_obstacles(tecran):

    epai = 15  # epaisseur des obstacles

    # on ne les voit pas, ils servent juste a faire rebondir le joueur s'il tire sur le ballon trop proche du bord
    obstacles = [
        Obstacle([-epai, -epai], [tecran[0] + 2 * epai, epai]),
        Obstacle([-epai, -epai], [epai, tecran[1] + 2 * epai]),
        Obstacle([-epai, tecran[1]], [tecran[0] + 2 * epai, epai]),
        Obstacle([tecran[0], -epai], [epai, tecran[1] + 2 * epai])]
    return obstacles


def gen_but(tecran, LargBut, ProfBut):

    # cages
    cages = [
        Cage([tecran[0] - ProfBut, (tecran[1] - LargBut) // 2], [ProfBut, LargBut]),
        Cage([0, (tecran[1] - LargBut) // 2], [ProfBut, LargBut])]

    # poteaux
    TaillePoteaux = 15
    ObstCages = [
        Obstacle([0, (tecran[1] - LargBut) // 2 - TaillePoteaux], [ProfBut, TaillePoteaux]),
        Obstacle([0, (tecran[1] + LargBut) // 2], [ProfBut, TaillePoteaux]),

        Obstacle([tecran[0] - ProfBut, (tecran[1] - LargBut) // 2 - TaillePoteaux], [ProfBut, TaillePoteaux]),
        Obstacle([tecran[0] - ProfBut, (tecran[1] + LargBut) // 2], [ProfBut, TaillePoteaux])]

    return cages, ObstCages


def gen_bonus_vitesse(tecran):

    taille_bonus = 30
    bonus = [BonusVit([tecran[0] // 10 - taille_bonus // 2, tecran[1] // 8 - taille_bonus // 2]),
             BonusVit([9 * tecran[0] // 10 - taille_bonus // 2, tecran[1] // 8 - taille_bonus // 2]),
             BonusVit([tecran[0] // 10 - taille_bonus // 2, 7 * tecran[1] // 8 - taille_bonus // 2]),
             BonusVit([9 * tecran[0] // 10 - taille_bonus // 2, 7 * tecran[1] // 8 - taille_bonus // 2])]
    return bonus
