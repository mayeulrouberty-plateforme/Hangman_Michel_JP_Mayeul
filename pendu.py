import pygame
import random
import time
import json
import os

# Initialisation de pygame
pygame.init()
pygame.mixer.init()  # Pour le son de la vidéo

# Paramètres de la fenêtre
LARGEUR = 1200
HAUTEUR = 700
fenetre = pygame.display.set_mode((LARGEUR, HAUTEUR))
pygame.display.set_caption("Jeu du Pendu")

# Couleurs (RGB)
BLANC = (255, 255, 255)
NOIR = (0, 0, 0)
ROUGE = (255, 0, 0)
VERT = (0, 255, 0)
BLEU = (0, 100, 255)
GRIS = (200, 200, 200)
ORANGE = (255, 165, 0)

# Polices
police_titre = pygame.font.Font(None, 50)
police_normale = pygame.font.Font(None, 36)
police_petite = pygame.font.Font(None, 28)
police_mini = pygame.font.Font(None, 20)

# Liste de 100 mots
LISTE_MOTS = [
    "PYTHON", "ORDINATEUR", "CLAVIER", "SOURIS", "ECRAN", "INTERNET", "FICHIER", "DOSSIER",
    "PROGRAMME", "LOGICIEL", "FENETRE", "BOUTON", "MENU", "ICONE", "CURSEUR", "CARTE",
    "RESEAU", "SERVEUR", "CLIENT", "DONNEES", "MEMOIRE", "DISQUE", "PORTABLE", "TABLETTE",
    "TELEPHONE", "ANDROID", "APPLE", "WINDOWS", "LINUX", "CHROME", "FIREFOX", "SAFARI",
    "FACEBOOK", "YOUTUBE", "TWITTER", "INSTAGRAM", "SNAPCHAT", "TIKTOK", "ZOOM", "SKYPE",
    "GOOGLE", "AMAZON", "NETFLIX", "SPOTIFY", "TWITCH", "DISCORD", "REDDIT", "GITHUB",
    "MINECRAFT", "FORTNITE", "FOOTBALL", "BASKETBALL", "TENNIS", "NATATION", "CYCLISME",
    "COURSE", "ATHLETISME", "GYMNASTIQUE", "DANSE", "MUSIQUE", "GUITARE", "PIANO", "VIOLON",
    "BATTERIE", "CHANT", "PEINTURE", "DESSIN", "SCULPTURE", "THEATRE", "CINEMA", "ACTEUR",
    "REALISATEUR", "SCENARIO", "CAMERA", "FILM", "SERIE", "DOCUMENTAIRE", "ANIMATION",
    "ASTRONAUTE", "PLANETE", "ETOILE", "GALAXIE", "TELESCOPE", "FUSEE", "SATELLITE",
    "OCEAN", "MONTAGNE", "FORET", "DESERT", "VOLCAN", "RIVIERE", "CASCADE", "PLAGE",
    "ELEPHANT", "GIRAFE", "TIGRE", "LION", "ZEBRE"
]


def dessiner_pendu(erreurs):
    """Dessine le bonhomme pendu selon le nombre d'erreurs (0-7)"""
    x_base = 150
    y_base = 400
    
    # Potence
    pygame.draw.line(fenetre, NOIR, (x_base, y_base), (x_base, y_base - 250), 5)
    pygame.draw.line(fenetre, NOIR, (x_base, y_base - 250), (x_base + 100, y_base - 250), 5)
    pygame.draw.line(fenetre, NOIR, (x_base + 100, y_base - 250), (x_base + 100, y_base - 200), 5)
    
    if erreurs >= 1:  # Tête
        pygame.draw.circle(fenetre, NOIR, (x_base + 100, y_base - 170), 30, 3)
    if erreurs >= 2:  # Corps
        pygame.draw.line(fenetre, NOIR, (x_base + 100, y_base - 140), (x_base + 100, y_base - 60), 5)
    if erreurs >= 3:  # Bras gauche
        pygame.draw.line(fenetre, NOIR, (x_base + 100, y_base - 120), (x_base + 60, y_base - 100), 5)
    if erreurs >= 4:  # Bras droit
        pygame.draw.line(fenetre, NOIR, (x_base + 100, y_base - 120), (x_base + 140, y_base - 100), 5)
    if erreurs >= 5:  # Jambe gauche
        pygame.draw.line(fenetre, NOIR, (x_base + 100, y_base - 60), (x_base + 70, y_base), 5)
    if erreurs >= 6:  # Jambe droite
        pygame.draw.line(fenetre, NOIR, (x_base + 100, y_base - 60), (x_base + 130, y_base), 5)
    if erreurs >= 7:  # Visage triste
        pygame.draw.circle(fenetre, ROUGE, (x_base + 90, y_base - 175), 3)
        pygame.draw.circle(fenetre, ROUGE, (x_base + 110, y_base - 175), 3)
        pygame.draw.arc(fenetre, ROUGE, (x_base + 85, y_base - 165, 30, 20), 3.14, 0, 3)


def afficher_texte(texte, x, y, police, couleur):
    """Affiche du texte à l'écran"""
    surface_texte = police.render(texte, True, couleur)
    fenetre.blit(surface_texte, (x, y))


def dessiner_bouton(texte, x, y, largeur, hauteur, couleur, couleur_texte):
    """Dessine un bouton et retourne True si cliqué"""
    souris_x, souris_y = pygame.mouse.get_pos()
    clic = pygame.mouse.get_pressed()[0]
    
    # Vérifie si la souris est sur le bouton
    sur_bouton = x < souris_x < x + largeur and y < souris_y < y + hauteur
    
    # Éclaircit la couleur au survol
    if sur_bouton:
        couleur_bouton = tuple(min(c + 30, 255) for c in couleur)
    else:
        couleur_bouton = couleur
    
    # Dessine le bouton
    pygame.draw.rect(fenetre, couleur_bouton, (x, y, largeur, hauteur))
    pygame.draw.rect(fenetre, NOIR, (x, y, largeur, hauteur), 3)
    
    # Centre le texte
    surface_texte = police_normale.render(texte, True, couleur_texte)
    texte_rect = surface_texte.get_rect(center=(x + largeur // 2, y + hauteur // 2))
    fenetre.blit(surface_texte, texte_rect)
    
    return sur_bouton and clic


def charger_scoreboard():
    """Charge le top 5 des scores depuis un fichier JSON"""
    if os.path.exists("scoreboard.json"):
        try:
            with open("scoreboard.json", "r") as f:
                return json.load(f)
        except:
            return []
    return []


def sauvegarder_scoreboard(scores):
    """Sauvegarde le scoreboard dans un fichier JSON"""
    with open("scoreboard.json", "w") as f:
        json.dump(scores, f)


def ajouter_score(pseudo, score):
    """Ajoute un score et garde seulement le top 5"""
    scores = charger_scoreboard()
    scores.append({"pseudo": pseudo, "score": score})
    scores.sort(key=lambda x: x["score"], reverse=True)  # Trie du meilleur au pire
    scores = scores[:5]  # Garde seulement les 5 meilleurs
    sauvegarder_scoreboard(scores)
    return scores


def afficher_scoreboard(scores):
    """Affiche le top 5 des scores à droite de l'écran"""
    y_pos = 100
    afficher_texte("TOP 5 SCORES", 950, y_pos, police_titre, BLEU)
    y_pos += 60
    
    if not scores:
        afficher_texte("Aucun score", 950, y_pos, police_normale, GRIS)
    else:
        for i, entry in enumerate(scores[:5], 1):
            texte = f"{i}. {entry['pseudo']} - {entry['score']} pts"
            afficher_texte(texte, 950, y_pos, police_petite, NOIR)
            y_pos += 35


def lire_video_mp4(chemin_video):
    """
    Lit une vidéo MP4 en plein écran
    IMPORTANT: Cette fonction nécessite opencv-python
    Installez-le avec: pip install opencv-python
    """
    print(f"Tentative de lecture de la vidéo: {chemin_video}")
    print(f"Chemin absolu: {os.path.abspath(chemin_video)}")
    print(f"Fichier existe: {os.path.exists(chemin_video)}")
    
    try:
        import cv2
        print("OpenCV importé avec succès")
        
        # Ouvre la vidéo
        video = cv2.VideoCapture(chemin_video)
        
        if not video.isOpened():
            print("ERREUR: Impossible d'ouvrir la vidéo")
            print("Vérifiez que le fichier est bien 'game_over.mp4' et qu'il est dans le bon dossier")
            input("Appuyez sur Entrée pour continuer...")
            return
        
        print("Vidéo ouverte avec succès!")
        
        # Récupère les infos de la vidéo
        fps = video.get(cv2.CAP_PROP_FPS)
        nb_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        print(f"FPS: {fps}, Nombre de frames: {nb_frames}")
        
        clock = pygame.time.Clock()
        
        lecture_active = True
        frame_count = 0
        
        while lecture_active:
            # Lit une frame
            ret, frame = video.read()
            frame_count += 1
            
            if not ret:  # Fin de la vidéo
                print(f"Fin de la vidéo atteinte (frame {frame_count}/{nb_frames})")
                break
            
            # Convertit BGR (OpenCV) en RGB (Pygame)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Redimensionne pour remplir l'écran
            frame = cv2.resize(frame, (LARGEUR, HAUTEUR))
            
            # Transpose pour Pygame (largeur, hauteur) -> (hauteur, largeur)
            frame = frame.swapaxes(0, 1)
            
            # Affiche la frame
            surface_video = pygame.surfarray.make_surface(frame)
            fenetre.blit(surface_video, (0, 0))
            
            # Texte pour passer
            afficher_texte("Appuyez sur ESPACE pour passer", 350, 650, police_petite, BLANC)
            
            pygame.display.flip()
            
            # Gestion des événements
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    lecture_active = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:  # ESPACE pour passer
                        lecture_active = False
            
            # Respecte le framerate de la vidéo
            clock.tick(fps)
        
        video.release()
        print("Vidéo terminée")
        
    except ImportError:
        print("=" * 60)
        print("ERREUR: OpenCV n'est pas installé!")
        print("Installez-le avec: pip install opencv-python")
        print("=" * 60)
        input("Appuyez sur Entrée pour continuer...")
    except Exception as e:
        print("=" * 60)
        print(f"ERREUR lors de la lecture de la vidéo: {e}")
        print(f"Type d'erreur: {type(e).__name__}")
        print("=" * 60)
        input("Appuyez sur Entrée pour continuer...")


def afficher_ecran_game_over(score_final, mots_trouves_count):
    """Affiche l'écran de fin avec vidéo de défaite"""
    
    print("\n" + "=" * 60)
    print("GAME OVER - Vérification de la vidéo")
    print("=" * 60)
    
    # LECTURE DE LA VIDÉO DE DÉFAITE
    # Utilise le dossier du script Python, pas le dossier de travail
    dossier_script = os.path.dirname(os.path.abspath(__file__))
    chemin_video = os.path.join(dossier_script, "game_over.mp4")
    
    print(f"Recherche de la vidéo: {chemin_video}")
    print(f"Dossier du script: {dossier_script}")
    print(f"Dossier de travail actuel: {os.getcwd()}")
    print(f"Fichiers .mp4 dans le dossier du script:")
    try:
        for fichier in os.listdir(dossier_script):
            if fichier.endswith(".mp4"):
                print(f"  - {fichier}")
    except:
        print("  (impossible de lister les fichiers)")
    
    if os.path.exists(chemin_video):
        print(f"✓ Vidéo trouvée: {chemin_video}")
        lire_video_mp4(chemin_video)
    else:
        print(f"✗ Vidéo NON trouvée: {chemin_video}")
        print(f"Mettez le fichier 'game_over.mp4' dans: {dossier_script}")
    
    print("=" * 60 + "\n")
    
    # Écran de saisie du pseudo et affichage des scores
    affichage_fin = True
    pseudo = ""
    pseudo_valide = False
    
    while affichage_fin:
        fenetre.fill(NOIR)
        
        # Titre GAME OVER
        afficher_texte("GAME OVER!", 380, 80, police_titre, ROUGE)
        
        # Score et stats
        afficher_texte(f"Score Final: {score_final} pts", 320, 180, police_titre, BLANC)
        afficher_texte(f"Mots trouvés: {mots_trouves_count}/100", 300, 260, police_normale, BLANC)
        
        # Formulaire pseudo
        if not pseudo_valide:
            afficher_texte("Entrez votre pseudo (3 caractères):", 280, 360, police_petite, BLANC)
            
            # Cadre de saisie
            pygame.draw.rect(fenetre, BLANC, (350, 410, 200, 50))
            pygame.draw.rect(fenetre, ROUGE, (350, 410, 200, 50), 3)
            
            # Affiche le pseudo (max 3 caractères)
            pseudo_affiche = pseudo[:3]
            surface_pseudo = police_titre.render(pseudo_affiche, True, NOIR)
            rect_pseudo = surface_pseudo.get_rect(center=(450, 435))
            fenetre.blit(surface_pseudo, rect_pseudo)
            
            # Bouton Valider
            if dessiner_bouton("Valider", 570, 410, 120, 50, VERT, BLANC):
                if len(pseudo) == 3:
                    pseudo_valide = True
                    ajouter_score(pseudo, score_final)
        else:
            # Affiche le top 5
            afficher_texte("TOP 5 SCORES", 420, 360, police_normale, VERT)
            scores = charger_scoreboard()
            y_pos = 420
            
            if scores:
                for i, entry in enumerate(scores, 1):
                    texte = f"{i}. {entry['pseudo']} - {entry['score']} pts"
                    # Met en surbrillance le score du joueur
                    couleur = BLANC if entry['pseudo'] == pseudo else GRIS
                    afficher_texte(texte, 350, y_pos, police_petite, couleur)
                    y_pos += 40
        
        # Boutons Rejouer et Quitter
        if dessiner_bouton("Rejouer", 300, 620, 180, 50, VERT, BLANC):
            affichage_fin = False
            jeu_pendu()
            return
        
        if dessiner_bouton("Quitter", 720, 620, 180, 50, ROUGE, BLANC):
            affichage_fin = False
        
        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                affichage_fin = False
            
            if event.type == pygame.KEYDOWN and not pseudo_valide:
                if event.key == pygame.K_BACKSPACE:
                    pseudo = pseudo[:-1]
                elif len(pseudo) < 3:
                    lettre = event.unicode.upper()
                    if lettre.isalpha():
                        pseudo += lettre
        
        pygame.display.flip()
        pygame.time.Clock().tick(30)


def jeu_pendu():
    """Fonction principale du jeu"""
    
    # Variables du jeu
    score_total = 0
    mots_trouves = 0
    mots_non_trouves = []
    mots_trouves_list = []
    mots_utilises = []
    
    # Affichage temporaire du mot trouvé/loupé
    affichage_mot_actif = False
    affichage_mot_texte = ""
    affichage_mot_couleur = BLANC
    temps_affichage_mot = 0
    temps_affichage_max = 3.0
    
    # Chronomètre
    temps_restant = 60.0
    temps_derniere_mise_a_jour = time.time()
    
    # Premier mot
    mot_a_trouver = random.choice(LISTE_MOTS)
    mots_utilises.append(mot_a_trouver)
    
    # État du mot actuel
    lettres_trouvees = ["_"] * len(mot_a_trouver)
    lettres_proposees = []
    erreurs = 0
    max_erreurs = 7
    
    jeu_actif = True
    
    # Boucle principale
    while jeu_actif:
        # Calcul du temps
        temps_actuel = time.time()
        delta_temps = temps_actuel - temps_derniere_mise_a_jour
        temps_derniere_mise_a_jour = temps_actuel
        temps_restant -= delta_temps
        
        # Gestion de l'affichage temporaire du mot
        if affichage_mot_actif:
            temps_affichage_mot += delta_temps
            if temps_affichage_mot >= temps_affichage_max:
                affichage_mot_actif = False
                temps_affichage_mot = 0
        
        # Si le temps est écoulé
        if temps_restant <= 0:
            temps_restant = 0
            afficher_ecran_game_over(score_total, mots_trouves)
            return
        
        # Événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                jeu_actif = False
            
            # Saisie de lettre (seulement si pas d'affichage en cours)
            if event.type == pygame.KEYDOWN and not affichage_mot_actif:
                lettre = event.unicode.upper()
                
                if lettre.isalpha() and len(lettre) == 1 and lettre not in lettres_proposees:
                    lettres_proposees.append(lettre)
                    
                    # Vérifie si la lettre est dans le mot
                    if lettre in mot_a_trouver:
                        # Compte et remplace les lettres
                        nombre_lettres = 0
                        for i in range(len(mot_a_trouver)):
                            if mot_a_trouver[i] == lettre:
                                lettres_trouvees[i] = lettre
                                nombre_lettres += 1
                        
                        score_total += nombre_lettres  # +1 point par lettre
                    else:
                        erreurs += 1  # Mauvaise lettre
                    
                    # Mot trouvé ?
                    if "_" not in lettres_trouvees:
                        score_total += 10  # Bonus
                        mots_trouves += 1
                        mots_trouves_list.append(mot_a_trouver)
                        temps_restant += 30  # +30 secondes
                        
                        # Message de victoire
                        affichage_mot_actif = True
                        affichage_mot_texte = f"✓ MOT TROUVÉ: {mot_a_trouver}!"
                        affichage_mot_couleur = VERT
                        temps_affichage_mot = 0
                        
                        # Mot suivant
                        mots_disponibles = [m for m in LISTE_MOTS if m not in mots_utilises]
                        if len(mots_disponibles) == 0:
                            jeu_actif = False
                        else:
                            mot_a_trouver = random.choice(mots_disponibles)
                            mots_utilises.append(mot_a_trouver)
                            lettres_trouvees = ["_"] * len(mot_a_trouver)
                            lettres_proposees = []
                            erreurs = 0
                    
                    # Pendu complet ?
                    elif erreurs >= max_erreurs:
                        mots_non_trouves.append(mot_a_trouver)
                        
                        # Message d'échec
                        affichage_mot_actif = True
                        affichage_mot_texte = f"✗ MOT LOUPÉ: {mot_a_trouver}"
                        affichage_mot_couleur = ROUGE
                        temps_affichage_mot = 0
                        temps_restant -= 10  # -10 secondes
                        
                        # Mot suivant
                        mots_disponibles = [m for m in LISTE_MOTS if m not in mots_utilises]
                        if len(mots_disponibles) == 0:
                            jeu_actif = False
                        else:
                            mot_a_trouver = random.choice(mots_disponibles)
                            mots_utilises.append(mot_a_trouver)
                            lettres_trouvees = ["_"] * len(mot_a_trouver)
                            lettres_proposees = []
                            erreurs = 0
        
        # AFFICHAGE
        fenetre.fill(BLANC)
        
        # Pendu
        dessiner_pendu(erreurs)
        
        # Titre
        afficher_texte("JEU DU PENDU", 280, 20, police_titre, BLEU)
        
        # Chronomètre
        minutes = int(temps_restant) // 60
        secondes = int(temps_restant) % 60
        texte_temps = f"Temps: {minutes:02d}:{secondes:02d}"
        couleur_temps = VERT if temps_restant > 20 else ORANGE if temps_restant > 10 else ROUGE
        afficher_texte(texte_temps, 550, 80, police_normale, couleur_temps)
        
        # Score et stats
        afficher_texte(f"Score: {score_total} pts", 350, 80, police_normale, VERT)
        afficher_texte(f"Mots: {mots_trouves}/100", 350, 120, police_normale, BLEU)
        afficher_texte(f"Erreurs: {erreurs}/{max_erreurs}", 350, 160, police_normale, ROUGE)
        
        # Mot actuel
        mot_affiche = " ".join(lettres_trouvees)
        afficher_texte(mot_affiche, 300, 240, police_titre, NOIR)
        
        # Lettres proposées
        if lettres_proposees:
            texte_proposees = "Lettres: " + ", ".join(sorted(lettres_proposees))
            afficher_texte(texte_proposees, 250, 310, police_petite, BLEU)
        
        # Mots trouvés (gauche)
        afficher_texte("Mots trouvés:", 20, 400, police_petite, VERT)
        y_pos = 430
        for mot in mots_trouves_list[-5:]:
            afficher_texte(mot, 20, y_pos, police_mini, VERT)
            y_pos += 25
        
        # Mots loupés (droite de la zone de jeu)
        afficher_texte("Mots loupés:", 700, 400, police_petite, ROUGE)
        y_pos = 430
        for mot in mots_non_trouves[-5:]:
            afficher_texte(mot, 700, y_pos, police_mini, ROUGE)
            y_pos += 25
        
        # Scoreboard
        scores = charger_scoreboard()
        afficher_scoreboard(scores)
        
        # Instructions
        afficher_texte("Tapez une lettre pour jouer", 250, 620, police_petite, GRIS)
        afficher_texte("Mot trouvé = +10 pts + 30 sec | Lettre = +1 pt", 200, 650, police_petite, GRIS)
        
        # Overlay si mot trouvé/loupé
        if affichage_mot_actif:
            overlay = pygame.Surface((LARGEUR, HAUTEUR))
            overlay.set_alpha(150)
            overlay.fill(NOIR)
            fenetre.blit(overlay, (0, 0))
            
            surface_msg = police_titre.render(affichage_mot_texte, True, affichage_mot_couleur)
            rect_msg = surface_msg.get_rect(center=(LARGEUR // 2, HAUTEUR // 2))
            fenetre.blit(surface_msg, rect_msg)
        
        pygame.display.flip()
        pygame.time.Clock().tick(30)
    
    # Fin du jeu
    afficher_ecran_game_over(score_total, mots_trouves)


# Lancement
if __name__ == "__main__":
    jeu_pendu()
    pygame.quit()