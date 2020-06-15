import socket
import pickle
import threading
import time

import Partie


def serveur(NBRJOUEURS, PROLONGATION, TEMPS):

    global ETATS, etat, infosenv, ready, cmdrecv, commandesjoueurs, msg_actu_jeu, msg_actu_jeu_send
    ETATS = ['Demarrage serveur', 'Connexions joueurs', 'Partie créée', 'Partie en cours', 'Partie terminée']
    etat = 0
    infosenv = [False]*NBRJOUEURS
    ready = [False]*NBRJOUEURS
    cmdrecv = [False]*NBRJOUEURS
    commandesjoueurs = [[False, False, False, False, False]]*NBRJOUEURS
    msg_actu_jeu = []
    msg_actu_jeu_send = [False]*NBRJOUEURS

    PartieCreee = threading.Event()
    PartiePrete = threading.Event()
    DemarragePartie = threading.Event()

    CommandesRecues = threading.Event()
    msg_actu_jeu_pret = threading.Event()
    msg_actu_jeu_allsend = threading.Event()

    SERVER = ""
    PORT = 5555

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        s.bind((SERVER, PORT))
    except socket.error as e:
        str(e)

    # on attend des connections (arg = combien de connections sont acceptees)
    s.listen(NBRJOUEURS)
    etat += 1
    print("Serveur en attente de connexions...")

    global nbrjoueurs_co
    nbrjoueurs_co = 0

    # thread assurant la communication avec le client qui lui est associé
    def interac_client(conn, id_client):

        # envoie de message
        def send_info(msg):
            conn.sendall(pickle.dumps(msg))

        # reception de message
        def recv_info(taille_msg):
            try:
                data = pickle.loads(conn.recv(taille_msg))

                # si on ne recoit rien
                if not data:
                    print(f"Joueur{id_client} déconnecté")
                    return None

                # si on recoit bien une info
                else:
                    # print(f"[Message du client {id_client}] {data}")
                    return data

            except socket.error as err:
                print('impossible de recevoir data')
                print(err)

            except EOFError as EOFerr:
                print('Reception data vide')
                print(EOFerr)

        global game

        # on commence par attendre la creation de la partie
        PartieCreee.wait()

        # des qu'on recoit les infos du joueur du client, on les donne à la partie
        [nomj, nomimj] = recv_info(2048)
        print(f"reception de : {nomj, nomimj}")
        game.joueurs[id_client].update_infos(nomj, nomimj)

        global infosenv
        infosenv[id_client] = True
        # on attend que ts les clients aient envoyé leurs infos et si on est le dernier, on dit aux autres que c'est ok
        if infosenv == [True]*NBRJOUEURS:
            print('tous les joueurs ont donné leurs infos')
            # for j in game.joueurs:
            #     print(f"test: noms du joueur numero {j.numero}: {j.nom}")
            PartiePrete.set()
        else:
            PartiePrete.wait()

        # on envoie les infos de la partie (de quoi afficher le ballon et les joueurs)
        print(f'envoie de la partie au client{id_client}...')
        infos_prepartie = [[game.ballon.pos]]
        for j in game.joueurs:
            infos_prepartie.append([j.numero, j.nom, j.nomImage, j.pos, j.vit[1]])
        infos_prepartie.append(game.params)
        send_info([infos_prepartie, id_client])
        print(f'partie envoyée au client{id_client}')

        # on attend que le client renvoie ready
        global ready, etat, ETATS
        retourclient = recv_info(256)
        while retourclient != 'ready':
            retourclient = recv_info(256)
        ready[id_client] = True
        # on attend que tous les clients aient renvoyé ready, et si on est le dernier, on dit aux autres que c'est ok
        if ready == [True] * NBRJOUEURS:
            etat += 1
            DemarragePartie.set()
        else:
            DemarragePartie.wait()

        # la partie commence!
        while ETATS[etat] == 'Partie en cours':

            global cmdrecv, commandesjoueurs
            # print(f"commandes du client {id_client} en attente")
            retourclient = recv_info(32)
            while len(retourclient) != 5:  # a verifier
                retourclient = recv_info(32)
            # print(f"Commandes client {id_client}: {retourclient}")
            commandesjoueurs[id_client] = retourclient
            cmdrecv[id_client] = True
            # on attend que tous les clients aient renvoyé leurs commandes
            # si on est le dernier, on set l'event pour prévenir chaque thread que c'est bon, et on clear immédiatement
            if cmdrecv == [True] * NBRJOUEURS:
                CommandesRecues.set()
                CommandesRecues.clear()
                cmdrecv = [False] * NBRJOUEURS
            else:
                CommandesRecues.wait()

            # on attend que le jeu fasse ses calculs, puis on envoie la réponse du jeu
            msg_actu_jeu_pret.wait()
            global msg_actu_jeu, msg_actu_jeu_send
            # print(f"Envoie au client {id_client}: {msg_actu_jeu}")
            send_info(msg_actu_jeu)

            # si ts les threads ont envoyé la réponse à leur client, on clear msg_actu_jeu_pretet on prévient les autres
            # threads avec msg_actu_jeu_allsend
            msg_actu_jeu_send[id_client] = True
            if msg_actu_jeu_send == [True]*NBRJOUEURS:
                msg_actu_jeu_pret.clear()
                msg_actu_jeu_send = [False]*NBRJOUEURS
                msg_actu_jeu_allsend.set()
            else:
                msg_actu_jeu_allsend.wait()

        # fin du thread
        print(str(conn) + "déconnecté")
        global nbrjoueurs_co
        nbrjoueurs_co -= 1
        conn.close()

    # tant qu'on n'a pas NBRJOUEURS joueurs, on cherche a en accepter
    threadsclients = []
    while ETATS[etat] == 'Connexions joueurs':
        conn, addr = s.accept()
        print("Connecté à :", addr)
        threadsclients.append(threading.Thread(target=interac_client, args=(conn, nbrjoueurs_co)))
        threadsclients[-1].start()
        nbrjoueurs_co += 1
        if nbrjoueurs_co == NBRJOUEURS:
            etat += 1

    # on a le bon nombre de clients connectés, on crée alors une partie et on envoie à chaque client
    # les infos initiales de la partie, et on attend que chacun réponde qu'il est prêt pour démarrer
    print('Création de la partie...')
    global game
    game = Partie.Partie([NBRJOUEURS, PROLONGATION, TEMPS])
    #print('Partie créée, communication avec les clients avant lancement de la partie...')
    PartieCreee.set()

    # on attend que la communication avec les clients se termine
    DemarragePartie.wait()

    print('que la partie commence!')

    while ETATS[etat] == 'Partie en cours':

        # chaque thread va recevoir les commandes du joueur qu'il supervise
        CommandesRecues.wait()

        # print('commandes recues: ' + str(commandesjoueurs))

        msg_actu_jeu = game.resoudre(commandesjoueurs)

        # print('message généré pour chaque joueur: ' + str(msg_actu_jeu))
        # print(f"nbr de bytes du message: {len(pickle.dumps(msg_actu_jeu))}")
        msg_actu_jeu_pret.set()

        msg_actu_jeu_allsend.wait()

        if msg_actu_jeu[0] == 'GameOver':
            etat += 1
            time.sleep(10)

    # fin de la partie
    print('Fermeture du serveur')
    s.close()


"""
NBRJOUEURS = 2  # 2 ou 4
PROLONGATION = False
TEMPS = 60

serveur(NBRJOUEURS, PROLONGATION, TEMPS)
"""
