import socket
import pickle
import pygame
from random import randint
import time

import Partie_client


class message:

    def __init__(self, pos, texte, taille=36):
        font = pygame.font.Font(None, taille)
        self.image = font.render(texte, 1, (10, 10, 10))
        self.rect = self.image.get_rect()
        self.position = pos
        self.rect = self.rect.move(self.position)

    def update_texte(self, newtexte, taille=36):
        font = pygame.font.Font(None, taille)
        self.image = font.render(newtexte, 1, (10, 10, 10))
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(self.position)

    def update_pos(self, newpos):
        self.rect = self.rect.move([int(newpos[0] - self.position[0]), int(newpos[1] - self.position[1])])
        self.position = newpos


def loadsound(soundname):
    sound = pygame.mixer.Sound(soundname)
    return sound


# genere le fond du terrain
def gen_background(TailleEcran):
    bg = pygame.Surface(TailleEcran)
    bg.convert()

    # premier exemple de background avec des bandes de deux verts et une ligne blanche centrale
    # bandes de verts
    bg.fill((0, 100, 0))
    nbr_bandes = 9
    second_vert = pygame.Surface([TailleEcran[0] // nbr_bandes, TailleEcran[1]])
    second_vert.convert()
    second_vert.fill((0, 120, 0))
    for k in range(nbr_bandes):
        if k % 2 == 0:
            bg.blit(second_vert, [k * TailleEcran[0] // nbr_bandes, 0])

    # ligne blanche
    largeur_ligne = 6
    ligne = pygame.Surface([largeur_ligne, TailleEcran[1]])
    ligne.convert()
    ligne.fill((255, 255, 255))
    bg.blit(ligne, [(TailleEcran[0] - largeur_ligne) // 2, 0])

    return bg


# redessine les differents objets a l'ecran
def dessine(win, joueurs, ball, bonus_vit, messages):

    for j in joueurs:
        win.blit(j.image, j.rect)
    win.blit(ball.surf, ball.rect)
    for bonus in bonus_vit:
        win.blit(bonus.surf, bonus.rect)
    for msg in messages:
        win.blit(msg.image, msg.rect)


# efface les differents objets a l'ecran
def efface(win, background, joueurs, ball, bonus_vit, messages):

    for j in joueurs:
        win.blit(background, j.rect, j.rect)
    win.blit(background, ball.rect, ball.rect)
    for bonus in bonus_vit:
        win.blit(background, bonus.rect, bonus.rect)
    for msg in messages:
        win.blit(background, msg.rect, msg.rect)


def but(SonBut, SonButcontre, win, TailleEcran, background, butfavorable):

    if not butfavorable:
        SonButcontre.play()
    SonBut.play()
    pygame.time.delay(200)

    # golgolgolgolgol
    for k in range(13):
        message_but = message([randint(0, TailleEcran[0] - 90), randint(0, TailleEcran[1] - 75)],
                              "GOL", randint(45, 150))
        win.blit(message_but.image, message_but.rect)
        pygame.display.update()

        pygame.time.delay(150)

        win.blit(background, message_but.rect, message_but.rect)

    pygame.time.delay(1000)

    # gooooooooooooool
    for k in range(30):
        message_but = message([TailleEcran[0] // 2 - 60 - 11 * k, TailleEcran[1] // 2 - 5], "GO" + "O" * k + "L!", 45)
        win.blit(message_but.image, message_but.rect)
        pygame.display.update()

        pygame.time.delay(120)

        win.blit(background, message_but.rect, message_but.rect)

    pygame.time.delay(1000)


def client(ipserver, port, nom, nomim):

    pygame.init()
    TailleEcran = [1250, 650]
    win = pygame.display.set_mode(TailleEcran)
    pygame.display.set_caption("FootCar")

    background = gen_background(TailleEcran)

    # message connection au serveur
    win.blit(background, (0, 0))
    msgattser = message([TailleEcran[0] // 2 - 100, TailleEcran[1] // 2 - 5], "Connection au serveur...")
    win.blit(msgattser.image, msgattser.rect)
    pygame.display.update()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    SERVER = ipserver
    PORT = port

    # on tente de se connecter au serveur
    connected = False
    while not connected:
        try:
            s.connect((SERVER, PORT))
            print('bien connecté au serveur')
            connected = True
        except socket.error as e:
            print(f"Impossible de se connecter à l'ip {SERVER} sur le port {PORT}")
            time.sleep(5)

    # message attente de joueur
    win.blit(background, msgattser.rect, msgattser.rect)
    msgattj = message([TailleEcran[0] // 2 - 150, TailleEcran[1] // 2 - 5], "En attente des autres joueurs...")
    win.blit(msgattj.image, msgattj.rect)
    pygame.display.update()

    #print("envoie au serveur le nom et le nom de l'image")
    s.send(pickle.dumps([nom, nomim]))

    [datapartie, idclient] = pickle.loads(s.recv(4096))
    #print('data de la partie recus, travail en cours...')

    # message preparation de la partie
    win.blit(background, msgattser.rect, msgattser.rect)
    msgprep = message([TailleEcran[0] // 2 - 150, TailleEcran[1] // 2 - 5], "Préparation de la partie...")
    win.blit(msgprep.image, msgprep.rect)
    pygame.display.update()

    # chargement des sons
    SonBut = loadsound('medias/Gol.wav')
    SonButcontre = loadsound('medias/le-non-de-paul-le-guen-barca-psg.wav')

    # creation de l'objet partie
    game_client = Partie_client.Partie(datapartie[-1])

    #print('partie créée')

    # complete l'objet avec les datas du serveur
    game_client.ballon.update_dyn(datapartie[0][0])
    for k in range(game_client.params[0]):  # a automatiser
        dataj = datapartie[k+1]
        game_client.joueurs[k].update_infos(dataj[1], dataj[2])
        game_client.joueurs[k].load_image()
        game_client.joueurs[k].update_dyn(dataj[3], dataj[4])

    # envoie au serveur que le client est prêt
    s.send(pickle.dumps('ready'))

    # création des messages
    messages = [message([TailleEcran[0] // 2 - 25, 10], str(game_client.Temps)),
                message([TailleEcran[0] // 2 - 55, 10], str(game_client.equipe[0].score)),
                message([TailleEcran[0] // 2 + 43, 10], str(game_client.equipe[1].score))]
    for j in game_client.joueurs:
        messages.append(message([j.rect[0], j.rect[1] - 18], j.nom, 18))

    # on dessine les obstacles et les cages sur le background
    for cage in game_client.Cages:
        background.blit(cage.surf, cage.rect)
    for obst in game_client.Obstacles:
        background.blit(obst.surf, obst.rect)
    win.blit(background, [0, 0])
    pygame.display.update()

    # on prépare le background pour le compte à rebour des engagements
    bg_engage = background.copy()
    for j in game_client.joueurs:
        bg_engage.blit(j.image, j.rect)
    bg_engage.blit(game_client.ballon.surf, game_client.ballon.rect)
    for mes in messages[3:]:
        bg_engage.blit(mes.image, mes.rect)

    print("Coucou c'est Lambertos, je te souhaite une bonne partie bro!")

    # la partie commence
    gameison = True
    engage = True
    prolongations = False
    while gameison:

        # on efface les objets
        efface(win, background, game_client.joueurs, game_client.ballon, game_client.Bonus_vitesse, messages)

        # s'il y a engagement, cinématique associée
        if engage:

            win.blit(bg_engage, [0, 0])
            for mes in messages[:3]:
                win.blit(mes.image, mes.rect)

            # affichage du compte a rebour
            decompte = 3
            while decompte > 0:
                msg_decompte = message([TailleEcran[0] // 2 - 5, TailleEcran[1] // 2 - 5], str(decompte))
                win.blit(msg_decompte.image, msg_decompte.rect)
                pygame.display.update()
                pygame.time.delay(500)
                win.blit(bg_engage, msg_decompte.rect, msg_decompte.rect)
                pygame.display.update()
                pygame.time.delay(500)
                decompte -= 1

            win.blit(background, [0, 0])
            engage = False

        # on recupere les commandes de l'utilisateur pour les envoyer au serveur

        # Pour quitter. ATTENTION important de garder pygame.event.get() pour récup aussi les commandes
        for event in pygame.event.get():
            if event == pygame.QUIT:
                gameison = False

        cmds_client = game_client.joueurs[idclient].get_cmds()
        # print('envoie au serveur:' + str(cmds_client))
        s.send(pickle.dumps(cmds_client))
        # print(f"nbr de bytes du message: {len(pickle.dumps(cmds_client))}")

        # on attend de recevoir les données du serveur
        try:
            dataserveur = pickle.loads(s.recv(256))

            if dataserveur:

                # print(f"[Message du serveur] {dataserveur}")

                # si le serveur annonce GameOver
                if dataserveur[0] == 'GameOver':
                    # on se prépare à sortir de la boucle
                    gameison = False

                    # si on était en prolongations, il y a eu but
                    if prolongations:
                        prolongations = False

                        # on regarde si le but est favorable ou défavorable
                        butfavorable = False
                        for k in range(2):
                            if game_client.equipe[k].score != dataserveur[1][k]:
                                for numj in game_client.equipe[k].NumJoueurs:
                                    if idclient == numj:
                                        butfavorable = True

                        # on joue la cinématique
                        but(SonBut, SonButcontre, win, TailleEcran, background, butfavorable)

                        # on actualise le score de chaque équipe
                        game_client.equipe[0].score, game_client.equipe[1].score = dataserveur[1][0], dataserveur[1][1]

                    # creation des messages de fin
                    msg_fin = [
                        message([TailleEcran[0] // 2 - 80, TailleEcran[1] // 2 - 20], "Partie terminee"),
                        message([TailleEcran[0] // 2 - 80, TailleEcran[1] // 2 + 20],
                                "Score final: " + str(game_client.equipe[0].score) +
                                " - " + str(game_client.equipe[1].score))
                              ]
                    if game_client.equipe[0].score != game_client.equipe[1].score:
                        if game_client.equipe[0].score > game_client.equipe[1].score:
                            numequipe = str(game_client.equipe[0].Num)
                        else:  # game_client.equipe[0].score < game_client.equipe[1].score:
                            numequipe = str(game_client.equipe[1].Num)
                        msg_fin.append(message([TailleEcran[0] // 2 - 80, TailleEcran[1] // 2 + 40],
                                               "Victoire pour l'équipe " + numequipe + "!"))
                    else:
                        msg_fin.append(message([TailleEcran[0] // 2 - 80, TailleEcran[1] // 2 + 40], "Match nul..."))

                    # affichage des messages
                    for msg in msg_fin:
                        win.blit(msg.image, msg.rect)
                    pygame.display.update()

                # si le serveur annonce but
                elif dataserveur[0] == 'But':

                    # on regarde si le but est favorable ou défavorable
                    butfavorable = False
                    for k in range(2):
                        if game_client.equipe[k].score != dataserveur[1][k]:
                            for numj in game_client.equipe[k].NumJoueurs:
                                if idclient == numj:
                                    butfavorable = True

                    # on joue la cinématique
                    but(SonBut, SonButcontre, win, TailleEcran, background, butfavorable)

                    # on actualise le score de chaque équipe
                    game_client.equipe[0].score, game_client.equipe[1].score = dataserveur[1][0], dataserveur[1][1]
                    messages[1].update_texte(str(dataserveur[1][0]))
                    messages[2].update_texte(str(dataserveur[1][1]))

                    # on annonce engagement
                    engage = True

                # si le serveur annonce prolongations
                elif dataserveur[0] == 'Prolongations':

                    # affiche un message pour annoncer prolongations
                    message_prolo = message([TailleEcran[0] // 2 - 80, TailleEcran[1] // 2 - 5], "Prolongations!")
                    win.blit(message_prolo.image, message_prolo.rect)
                    pygame.display.update()

                    pygame.time.delay(500)

                    win.blit(background, message_prolo.rect, message_prolo.rect)

                    engage = True
                    prolongations = True

                # si la partie est en cours
                else:
                    # on actualise les paramètres des objets, on génère les messages et on dessine à l'écran
                    game_client.update(dataserveur)

                    msgtemps = str(game_client.Temps // 60) + ':' +\
                               str((game_client.Temps % 60) // 10) + str((game_client.Temps % 60) % 10)
                    messages[0].update_texte(msgtemps)
                    messages[1].update_texte(str(game_client.equipe[0].score))
                    messages[2].update_texte(str(game_client.equipe[1].score))

                    for j in game_client.joueurs:
                        messages[3 + j.numero].update_pos([j.rect[0], j.rect[1] - 18])

                    dessine(win, game_client.joueurs, game_client.ballon, game_client.Bonus_vitesse, messages)
                    pygame.display.update()

            else:
                print('anomalie communication serveur')

        except socket.error as e:
            print('impossible de recevoir')
            print(e)

    pygame.time.delay(1000)
    pygame.quit()

    return game_client.equipe[0].score, game_client.equipe[1].score,\
           game_client.joueurs[0].nomImage, game_client.joueurs[1].nomImage,\
           game_client.joueurs[0].nom, game_client.joueurs[1].nom


"""
ipserver = "192.168.1.100"
port = 5555
nom = 'jules'
nomim = 'jules.png'

client(ipserver, port, nom, nomim)
"""
