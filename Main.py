import random
import pygame
import sys
import os

dossier_script = os.path.dirname(__file__)
chemim_image = os.path.join(dossier_script, "westernMichel.png")

LARGEUR=800
HAUTEUR=600

NOIR=(0, 0, 0)
BLANC=(255, 255, 255)
GRIS = (200, 200, 200)
BLEU = (50, 50, 150)
ROUGE = (255, 0, 0)


def choisir_niveau(niveau):
    if niveau == "Facile":
        nom_fichier="Mots_Faciles.txt"
    elif niveau == "Difficile":
        nom_fichier="Mots_Difficiles.txt"
    else : 
        return "ERREUR_NIVEAU"
    
    try:
        # 'r' veut dire 'read' (lecture), encoding='utf-8' gère les accents
        with open(nom_fichier, 'r', encoding='utf-8') as fichier:
            # On lit toutes les lignes d'un coup
            lignes = fichier.readlines()
            
            # 3. Nettoyage : On enlève les retours à la ligne (\n) invisibles
            # On crée une nouvelle liste propre
            mots_propres = []
            for mot in lignes:
                mot_nettoye = mot.strip() # strip enlève les espaces et \n
                mots_propres.append(mot_nettoye)
            
            # 4. Le choix aléatoire
            mot_mystere = random.choice(mots_propres)
            return mot_mystere

    except FileNotFoundError:
            return "ERREUR_FICHIER_INTROUVABLE"

# print("Test niveau facile :", choisir_niveau("Facile"))
# print("Test niveau difficile :", choisir_niveau("Difficile"))

pygame.init()
ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
pygame.display.set_caption("Jeu du Pendu")

# --- 4. VARIABLES DU JEU (Initiales) ---
# On prépare le jeu avant d'entrer dans la boucle
niveau_actuel = "Facile"  # On force le niveau pour l'instant
mot_a_deviner = choisir_niveau(niveau_actuel)
police=pygame.font.Font (None, 50)
police_grande = pygame.font.Font(None, 120)
affichage_liste=["_"] * len(mot_a_deviner)
tentatives=7
jeu_termine=False
message_fin=""
temps_total_ms = 10000 
start_ticks = pygame.time.get_ticks() # On lance le chrono maintenant
score = 0
temps_restant_ms = temps_total_ms
try:
    image_fond = pygame.image.load("westernMichel.png")
    # On force l'image à faire la taille exacte de la fenêtre (800x600)
    image_fond = pygame.transform.scale(image_fond, (LARGEUR, HAUTEUR))
except FileNotFoundError:
    print("Attention : Image de fond introuvable. On restera sur du blanc.")
    image_fond = None
# Lettre choisie par l'utilisateur
lettre_tampon=""
print(f"TRICHE (pour tester) : Le mot est {mot_a_deviner}") # Pour voir si ça marche dans la console

images_pendu = [] 
# On boucle de 0 à 7 pour charger les fichiers automatiquement
for i in range(8): # range(8) va de 0 à 7
    nom_image = f"Pendu{i}.jpg" # Génère "pendu_0.png", "pendu_1.png"...
    
    try:
        # On charge l'image
        image = pygame.image.load(nom_image)
        image = pygame.transform.scale(image, (300, 300))
        # OPTIONNEL : On force la taille pour être sûr que ça rentre
        # image = pygame.transform.scale(image, (300, 300)) 
        images_pendu.append(image)
        
    except FileNotFoundError:
        print(f"ATTENTION : L'image {nom_image} est introuvable !")
        # Si on ne trouve pas l'image, on quitte pour éviter de planter plus tard
        sys.exit()

# --- 5. BOUCLE PRINCIPALE ---
running = True
while running:
    if not jeu_termine:
        # Temps écoulé depuis le début = Maintenant - Départ
        temps_ecoule = pygame.time.get_ticks() - start_ticks
        
        # Temps restant = 10s - Temps écoulé
        temps_restant_ms = temps_total_ms - temps_ecoule
        
        # Si le temps est écoulé (inférieur à 0)
        if temps_restant_ms <= 0:
            temps_restant_ms = 0 # On bloque à 0 pour pas afficher des nombres négatifs
            jeu_termine = True
            message_fin = f"TEMPS ÉCOULÉ ! Le mot était {mot_a_deviner}"
    # A. Événements
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # SI une touche de clavier est enfoncée : 
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running=False

            if not jeu_termine:
                if event.unicode.isalpha() and len(lettre_tampon)==0:
                    lettre_tampon=event.unicode.upper()
                
                elif event.key == pygame.K_BACKSPACE:
                    lettre_tampon=""

                elif event.key == pygame.K_RETURN:
                    # 1. LOGIQUE DU JEU
                    if lettre_tampon in mot_a_deviner:
                        print("Bravo ! Lettre trouvée.")
                        
                        # On dévoile les lettres
                        for i in range(len(mot_a_deviner)):
                            if mot_a_deviner[i] == lettre_tampon:
                                affichage_liste[i] = lettre_tampon
                    else:
                        print("Raté !")
                        tentatives -= 1
                        print(f"Vies restantes : {tentatives}")

                    # 2. VERIFICATION FIN DE PARTIE (APRES avoir joué)
                    # Victoire (si plus aucun "_" n'est présent)
                    if "_" not in affichage_liste:
                        jeu_termine = True
                        # LE SCORE EST EGAL AU TEMPS RESTANT (en points)
                        score = temps_restant_ms
                        message_fin = f"GAGNÉ ! Score : {score} pts"
                    
                    # Défaite (Attention au simple '=' ici, pas '==')
                    if tentatives == 0:
                        jeu_termine = True
                        message_fin = f"PERDU ! Le mot etait : {mot_a_deviner}"

                    # 3. LE PLUS IMPORTANT (POUR DEBLOQUER LE CLAVIER)
                    # On vide la mémoire pour pouvoir taper la lettre suivante
                    lettre_tampon = ""

    # B. Dessin
    if image_fond: # Si l'image existe
        ecran.blit(image_fond, (0, 0)) # On la colle en haut à gauche
    else:
        ecran.fill(BLANC) # Sinon, on garde le fond blanc classique
    
    # ... ENSUITE tout le reste de ton code (les rectangles, le texte, etc.) ...
    # pygame.Rect (x, y, largeur, hauteur)
    zone_haut = pygame.Rect(0, 0, LARGEUR, 150)
    # pygame.Rect (x, y, largeur, hauteur)
    zone_haut = pygame.Rect(0, 0, LARGEUR, 150)
    # "Dessine un rectangle" (Sur quoi, couleur, où et quelle taile de la variable zone_haut, on fait un contour et il est d'épaisseur 2)
    pygame.draw.rect(ecran, GRIS, zone_haut, 2)

    # Transforme la liste en texte
    texte_final = " ".join(affichage_liste)

    # Transforme le texte en image. Arguments : (texte, lissage_bords, couleur) :
    image_texte = police.render(texte_final, True, NOIR)

    # Place l'image au centre d'une zone déterminée, c'est du positionnement relatif.
    rect_texte = image_texte.get_rect(center=zone_haut.center)

    # Colle l'image dans la zone 
    ecran.blit(image_texte, rect_texte)


    # Rectangle lettre choisie haut gauche
    zone_gauche= pygame.Rect(0, 150, LARGEUR//2, 120)
    pygame.draw.rect(ecran, BLEU, zone_gauche, 2)

    texte_saisie = "Lettre choisie : " + lettre_tampon
    
    # 3. Rendu (Transformation en image)
    image_saisie = police.render(texte_saisie, True, NOIR)
    
    # 4. Positionnement de ce qu''on met dans cette case (Au centre de la zone bleue)
    rect_saisie = image_saisie.get_rect(center=zone_gauche.center)
    
    # 5. Collage sur l'écran
    ecran.blit(image_saisie, rect_saisie)


    # Rectangle temps haut droite
    zone_droite = pygame.Rect(400, 150, LARGEUR//2, 120)
    pygame.draw.rect(ecran, ROUGE, zone_droite, 2)

    # --- CALCUL DE L'AFFICHAGE (Secondes : Centièmes) ---
    secondes = temps_restant_ms // 1000
    centiemes = (temps_restant_ms % 1000) // 10
    
    # Le format f"{...:02}" force l'affichage sur 2 chiffres (ex: 05 au lieu de 5)
    texte_timer = f"Temps : {secondes}:{centiemes:02}" 
    
    image_timer = police.render(texte_timer, True, NOIR)
       
    # Positionnement
    rect_timer = image_timer.get_rect(center=zone_droite.center)
    ecran.blit(image_timer, rect_timer)   


    # Rectangle Pendu bas gauche
    zone_bas_gauche= pygame.Rect(0, 270, LARGEUR//2, 330)
    pygame.draw.rect(ecran, NOIR, zone_bas_gauche, 2)
    index_image=7-tentatives
    # Petite sécurité pour ne pas planter
    if index_image < 0: index_image = 0
    if index_image > 7: index_image = 7

    image_a_afficher=images_pendu[index_image]

    rect_pendu = image_a_afficher.get_rect(center=zone_bas_gauche.center)
    ecran.blit(image_a_afficher, rect_pendu)

    # (Temporaire : On met juste un texte pour dire que c'est ici)
    # texte_pendu = "Image du pendu ici"
    # image_pendu = police.render(texte_pendu, True, GRIS)
    # rect_pendu = image_pendu.get_rect(center=zone_bas_gauche.center)
    # ecran.blit(image_pendu, rect_pendu)


    # Rectangle temps bas droite
    zone_bas_droite = pygame.Rect(LARGEUR // 2, 270, LARGEUR // 2, 330)
    pygame.draw.rect(ecran, NOIR, zone_bas_droite, 2)

    # Ligne 1 : "Il vous reste" (Police normale)
    img_l1 = police.render("Il vous reste", True, NOIR)
    
    # Ligne 2 : LE CHIFFRE (Police GRANDE)
    # On change la couleur en rouge si c'est urgent (<= 2 vies)
    couleur_chiffre = NOIR
    if tentatives <= 2:
        couleur_chiffre = ROUGE
        
    img_chiffre = police_grande.render(str(tentatives), True, couleur_chiffre)
    
    # Ligne 3 : "tentatives" (Police normale)
    img_l3 = police.render("tentatives", True, NOIR)

    # --- POSITIONNEMENT (L'empilement) ---
    # On utilise le centre de la zone comme référence
    cx = zone_bas_droite.centerx
    cy = zone_bas_droite.centery

    # 1. On place le CHIFFRE pile au milieu
    rect_chiffre = img_chiffre.get_rect(center=(cx, cy))
    
    # 2. On place la ligne 1 au dessus du chiffre (top - 20 pixels)
    rect_l1 = img_l1.get_rect(midbottom=(cx, rect_chiffre.top - 10))
    
    # 3. On place la ligne 3 en dessous du chiffre (bottom + 20 pixels)
    rect_l3 = img_l3.get_rect(midtop=(cx, rect_chiffre.bottom + 10))

    # Collage des 3 morceaux
    ecran.blit(img_l1, rect_l1)
    ecran.blit(img_chiffre, rect_chiffre)
    ecran.blit(img_l3, rect_l3)

    if jeu_termine:
        # MODIFICATION ICI : On change les coordonnées
        # x=50, y=10 (Tout en haut), Largeur=700, Hauteur=130 (Pour couvrir la zone grise)
        zone_fin = pygame.Rect(50, 10, 700, 130)
        
        pygame.draw.rect(ecran, BLANC, zone_fin)
        pygame.draw.rect(ecran, NOIR, zone_fin, 3) 
        
        # On affiche le message
        image_fin = police.render(message_fin, True, ROUGE)
        rect_fin = image_fin.get_rect(center=zone_fin.center)
        ecran.blit(image_fin, rect_fin)
        
        # Petit texte pour dire comment quitter
        # On le remonte aussi pour qu'il rentre dans le cadre du haut
        image_quitter = police.render("Appuie sur ESC pour quitter", True, NOIR)
        rect_quitter = image_quitter.get_rect(midtop=(400, 100)) 
        ecran.blit(image_quitter, rect_quitter)
    
    # C. Rafraîchissement
    pygame.display.flip()


pygame.quit()
sys.exit()