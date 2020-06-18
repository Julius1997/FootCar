import tkinter as tk
import Server
import Client
import glob
import subprocess
from random import randint

rep_user_host = [2, True, 120]
rep_user_join = ['', '', '']
scoreJ1, scoreJ2 = 0, 0
photoJ1, photoJ2 = '', ''
nomJ1, nomJ2 = '', ''


def main():
    def hostgame():

        for wind in windows_main:
            canvas.itemconfigure(wind, state=tk.HIDDEN)
        for wind in windows_hostgame:
            canvas.itemconfigure(wind, state=tk.NORMAL)

    def joingame():

        for wind in windows_main:
            canvas.itemconfigure(wind, state=tk.HIDDEN)
        for wind in windows_joingame:
            canvas.itemconfigure(wind, state=tk.NORMAL)

    def backtomainmenu():

        for wind in windows_hostgame:
            canvas.itemconfigure(wind, state=tk.HIDDEN)
        for wind in windows_joingame:
            canvas.itemconfigure(wind, state=tk.HIDDEN)
        for wind in windows_main:
            canvas.itemconfigure(wind, state=tk.NORMAL)

    def hostgamego():

        # on recupere l'ip de l'ordi
        arpa = str(subprocess.check_output("arp -a"))
        arpasplit = arpa.split()
        selfip = arpasplit[1]

        # on recupere les parametres saisis par l'utilisateur
        tps = int(temps.get())
        prolo = True
        if prolong.get() == 0:
            prolo = False
        if deuxjoueurs.get() == 1:
            nbrj = 2
        elif quatrejoueurs.get() == 1:
            nbrj = 4
        fenetre.destroy()

        # on sauve ces parametres pour les reproposer
        global rep_user_host
        rep_user_host = [nbrj, prolo, tps]

        Server.serveur(nbrj, prolo, tps)

    def randomchoice():

        k = randint(0, listpng.size() - 1)
        listpng.selection_set(k)
        listpng.activate(k)

    def joingamego():

        IPserveur = listip.get(tk.ACTIVE)

        if nomj.get() == '':
            nomjoueur = 'Joueur sans nom'
        else:
            nomjoueur = nomj.get()

        if listpng.get(tk.ACTIVE) == '':
            skinj = listpng.get(0)
        else:
            skinj = listpng.get(tk.ACTIVE)

        fenetre.destroy()

        global rep_user_join
        rep_user_join = [IPserveur, nomjoueur, skinj]

        global scoreJ1, scoreJ2, photoJ1, photoJ2, nomJ1, nomJ2
        pathskinj = "skins/" + skinj + ".png"
        scoreJ1, scoreJ2, photoJ1, photoJ2, nomJ1, nomJ2 = Client.client(IPserveur, 5555, nomjoueur, pathskinj)

    def quitter():
        global go
        go = False
        fenetre.quit()
        fenetre.destroy()

    global rep_user_host, rep_user_join
    global scoreJ1, scoreJ2, photoJ1, photoJ2, nomJ1, nomJ2

    # creation d'une fenetre
    fenetre = tk.Tk()

    # canvas qui contient tout
    canvas = tk.Canvas(fenetre, height=450, width=700)

    # image de fond
    filename = tk.PhotoImage(file='medias/bg_main_menu.png')
    background_label = tk.Label(fenetre, image=filename)
    canvas.create_window(0, 0, anchor='nw', window=background_label)

    # affichage des scores de la partie precedante
    if (photoJ1, photoJ2) != ('', ''):
        champ_annonce_scoresprec = tk.Label(fenetre, text="Resultat partie precedante:")
        canvas.create_window(550, 0, anchor='nw', window=champ_annonce_scoresprec)
        champ_scoresprec = tk.Label(fenetre, text=str(scoreJ1) + '   ' + str(scoreJ2))
        canvas.create_window(605, 40, anchor='nw', window=champ_scoresprec)
        champ_j1prec = tk.Label(fenetre, text=nomJ1)
        canvas.create_window(560, 85, anchor='nw', window=champ_j1prec)
        champ_j2prec = tk.Label(fenetre, text=nomJ2)
        canvas.create_window(640, 85, anchor='nw', window=champ_j2prec)
        try:
            imagej1 = tk.PhotoImage(file=photoJ1)
            photoj1 = tk.Label(fenetre, image=imagej1)
            canvas.create_window(560, 20, anchor='nw', window=photoj1)
            imagej2 = tk.PhotoImage(file=photoJ2)
            photoj2 = tk.Label(fenetre, image=imagej2)
            canvas.create_window(640, 20, anchor='nw', window=photoj2)
        except:
            pass

    # listes des fenetres de widgets
    windows_main, windows_hostgame, windows_joingame = [], [], []

    # creation des fenetres de widgets pour le menu principal

    # widget label bienvenue
    champ_bienvenue = tk.Label(fenetre, text="Bienvenue sur FootCar en Wifi!", font=(None, 18))
    windows_main.append(canvas.create_window(20, 0, anchor='nw', window=champ_bienvenue))

    # widget bouton host nouvelle partie
    bouton_hostgame = tk.Button(fenetre, text='Créer nouvelle partie', command=hostgame)
    windows_main.append(canvas.create_window(50, 45, anchor='nw', window=bouton_hostgame))

    # widget bouton rejoindre nouvelle partie
    bouton_joingame = tk.Button(fenetre, text='Rejoindre partie', command=joingame)
    windows_main.append(canvas.create_window(200, 45, anchor='nw', window=bouton_joingame))

    # widget bouton quitter
    bouton_quitter = tk.Button(fenetre, text='Quitter', command=quitter)
    windows_main.append(canvas.create_window(350, 45, anchor='nw', window=bouton_quitter))

    # creation des fenetres de widgets pour le menu hostgame

    # widget label nom menu
    champ_menu_host = tk.Label(fenetre, text="Menu créer partie", font=(None, 18))
    windows_hostgame.append(canvas.create_window(20, 0, anchor='nw', window=champ_menu_host))

    # widget bouton host nouvelle partie
    bouton_hostgame = tk.Button(fenetre, text='Créer nouvelle partie', command=hostgamego)
    windows_hostgame.append(canvas.create_window(50, 45, anchor='nw', window=bouton_hostgame))

    # widget bouton retour
    bouton_retour = tk.Button(fenetre, text='Retour menu principal', command=backtomainmenu)
    windows_hostgame.append(canvas.create_window(350, 45, anchor='nw', window=bouton_retour))

    # champ temps pour le serveur
    champ_tps = tk.Label(fenetre, text="Temps nouvelle partie (en secondes):")
    windows_hostgame.append(canvas.create_window(0, 100, anchor='nw', window=champ_tps))
    temps = tk.StringVar()
    temps.set(rep_user_host[2])
    saisie_tps = tk.Entry(fenetre, textvariable=temps, width=4)
    windows_hostgame.append(canvas.create_window(200, 100, anchor='nw', window=saisie_tps))

    # case a cocher pour activer les prolongations
    prolong = tk.IntVar()
    if rep_user_host[1]:
        prolong.set(rep_user_host[1])
    case_prolong = tk.Checkbutton(fenetre, variable=prolong, text='Prolongations si match nul')
    windows_hostgame.append(canvas.create_window(0, 123, anchor='nw', window=case_prolong))

    # cases a cocher pour determiner le nombre de joueurs
    champ_nbrjoueurs = tk.Label(fenetre, text="Nombre de joueurs:")
    windows_hostgame.append(canvas.create_window(0, 150, anchor='nw', window=champ_nbrjoueurs))

    deuxjoueurs = tk.IntVar()
    if rep_user_host[0] == 2:
        deuxjoueurs.set(1)
    quatrejoueurs = tk.IntVar()
    if rep_user_host[0] == 4:
        quatrejoueurs.set(1)

    def togglecase4joueurs():
        case_4joueurs.toggle()

    case_2joueurs = tk.Checkbutton(fenetre, variable=deuxjoueurs, text='2', command=togglecase4joueurs)
    windows_hostgame.append(canvas.create_window(120, 150, anchor='nw', window=case_2joueurs))

    case_4joueurs = tk.Checkbutton(fenetre, variable=quatrejoueurs, text='4', command=case_2joueurs.toggle)
    windows_hostgame.append(canvas.create_window(150, 150, anchor='nw', window=case_4joueurs))

    msg_info_hostplay = "Pour rejoindre la partie avec l'ordinateur qui héberge le serveur,\n" \
                        "il suffit de lancer une seconde fenetre du jeu\n" \
                        "et de rejoindre une partie sur la première adresse IP proposée"
    champ_info_hostplay = tk.Label(fenetre, text=msg_info_hostplay, font=(None, 10))
    windows_hostgame.append(canvas.create_window(0, 200, anchor='nw', window=champ_info_hostplay))
    
    # creation des fenetres de widgets pour le menu joingame

    # widget label nom menu
    champ_menu_join = tk.Label(fenetre, text="Menu rejoindre partie", font=(None, 18))
    windows_joingame.append(canvas.create_window(20, 0, anchor='nw', window=champ_menu_join))

    # widget bouton rejoindre nouvelle partie
    bouton_joingame = tk.Button(fenetre, text='Rejoindre partie', command=joingamego)
    windows_joingame.append(canvas.create_window(200, 45, anchor='nw', window=bouton_joingame))

    # widget bouton retour
    bouton_retour = tk.Button(fenetre, text='Retour menu principal', command=backtomainmenu)
    windows_joingame.append(canvas.create_window(350, 45, anchor='nw', window=bouton_retour))

    # choix IP ordi hote du serveur
    arpa = str(subprocess.check_output("arp -a"))
    arpasplit = arpa.split()
    ipdispo = [arpasplit[1]]
    for k in range(len(arpasplit)):
        if k > 2 and arpasplit[k][0] == 'd' and (arpasplit[k][1] == 'y' or arpasplit[k][1] == 'i'):  # trouver un critere robuste au changement de langue
            ipdispo.append(arpasplit[k - 2])
    champ_choixip = tk.Label(fenetre, text="Choisissez l'IP de l'ordinateur hôte de la partie:")
    windows_joingame.append(canvas.create_window(0, 100, anchor='nw', window=champ_choixip))
    scrollbarip = tk.Scrollbar(fenetre)
    windows_joingame.append(canvas.create_window(0, 120, anchor='nw', window=scrollbarip))
    listip = tk.Listbox(fenetre, yscrollcommand=scrollbarip.set, selectmode=tk.SINGLE, height=3)
    for ip in ipdispo:
        listip.insert(tk.END, ip)
    for k in range(listip.size()):
        if listip.get(k) == rep_user_join[0]:
            listip.selection_set(k)
            listip.activate(k)
    windows_joingame.append(canvas.create_window(15, 120, anchor='nw', window=listip))
    scrollbarip.config(command=listip.yview)

    # champ nom joueur
    champ_nomj = tk.Label(fenetre, text="Entrez votre nom:")
    windows_joingame.append(canvas.create_window(0, 175, anchor='nw', window=champ_nomj))
    nomj = tk.StringVar()
    nomj.set(rep_user_join[1])
    saisie_nomj = tk.Entry(fenetre, textvariable=nomj, width=16)
    windows_joingame.append(canvas.create_window(110, 175, anchor='nw', window=saisie_nomj))

    # choix skin
    champ_choixskin = tk.Label(fenetre, text="Choisissez votre skin:")
    windows_joingame.append(canvas.create_window(15, 200, anchor='nw', window=champ_choixskin))
    scrollbar = tk.Scrollbar(fenetre)
    windows_joingame.append(canvas.create_window(0, 220, anchor='nw', window=scrollbar))
    listpng = tk.Listbox(fenetre, yscrollcommand=scrollbar.set, selectmode=tk.SINGLE, height=5)
    for skin in glob.glob("skins/*.png"):
        skin = skin[6:len(skin)-4]
        listpng.insert(tk.END, skin)  # liste de tous les fichiers .png dans le dossier skins
    for k in range(listpng.size()):
        if listpng.get(k) == rep_user_join[2]:
            listpng.selection_set(k)
            listpng.activate(k)
    windows_joingame.append(canvas.create_window(15, 220, anchor='nw', window=listpng))
    scrollbar.config(command=listpng.yview)

    # bouton choix aleatoire
    bouton_random = tk.Button(fenetre, text='Choix de skin aléatoire', command=randomchoice)
    windows_joingame.append(canvas.create_window(170, 250, anchor='nw', window=bouton_random))

    # info skin
    info_newskin = tk.Label(fenetre, text="Info: pour ajouter un nouveau skin, placer une image au format .png\n" +
                                          "dans le dossier skins (avec pour dimensions: 40x60)")
    windows_joingame.append(canvas.create_window(0, 330, anchor='nw', window=info_newskin))

    # affichage des widgets du main menu, pack du canvas et mainloop de la fenetre

    for wind in windows_hostgame:
        canvas.itemconfigure(wind, state=tk.HIDDEN)
    for wind in windows_joingame:
        canvas.itemconfigure(wind, state=tk.HIDDEN)
    for wind in windows_main:
        canvas.itemconfigure(wind, state=tk.NORMAL)

    canvas.pack()
    fenetre.mainloop()


# global go
go = True
while go:
    main()
