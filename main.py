import pygame
import random
import os
import time


# ---------- CONSTANTES ----------
LARGEUR, HAUTEUR = 800, 600
BLANC = (255, 255, 255)
NOIR = (0, 0, 0)
BLEU = (50, 50, 200)
ROUGE = (200, 50, 50)

MOTS_FILE = "mots.txt"
SCORES_FILE = "scores.txt"    # scores uniquement dans scores.txt


# ---------- INITIALISATION ----------
pygame.init()
pygame.mixer.init()

pygame.display.set_caption("Le meilleur pendu")
fenetre = pygame.display.set_mode((LARGEUR, HAUTEUR))
clock = pygame.time.Clock()

# Musique de fond
if os.path.exists("audio.mp3"):
    try:
        pygame.mixer.music.load("audio.mp3")
        pygame.mixer.music.set_volume(0.6)
        pygame.mixer.music.play(-1)
    except pygame.error:
        print("Impossible de lire audio.mp3")

# Fonts
FONT_GRANDE = pygame.font.SysFont("comicsans", 60)
FONT_MOYENNE = pygame.font.SysFont("comicsans", 40)
FONT_PETITE = pygame.font.SysFont("comicsans", 30)


# ---------- CHARGEMENT IMAGES PENDU ----------
images_pendu = []
# ATTENTION : ici on charge pendu1.png à pendu7.png (index 0->pendu1, 6->pendu7)
for i in range(1, 8):
    chemin = os.path.join("images", f"pendu{i}.png")
    img = pygame.image.load(chemin).convert_alpha()
    images_pendu.append(img)


# ---------- THEME WESTERN ----------
bg_western = pygame.image.load(os.path.join("images", "western_bg.png")).convert()
bg_western = pygame.transform.scale(bg_western, (LARGEUR, HAUTEUR))


# ---------- FONCTIONS FICHIERS (mots + scores texte) ----------
def charger_mots():
    mots = []
    if not os.path.exists(MOTS_FILE):
        return ["PENDU"]
    with open(MOTS_FILE, "r", encoding="utf-8") as f:
        for ligne in f:
            mot = ligne.strip().upper()
            if mot:
                mots.append(mot)
    if not mots:
        mots = ["PENDU"]
    return mots


def ajouter_mot(mot):
    mot = mot.strip().upper()
    if not mot:
        return
    with open(MOTS_FILE, "a", encoding="utf-8") as f:
        f.write(mot + "\n")


def mot_aleatoire():
    mots = charger_mots()
    return random.choice(mots)


def sauver_score_texte(nom, score):
    nom = nom.strip()
    if not nom:
        nom = "ANONYME"
    with open(SCORES_FILE, "a", encoding="utf-8") as f:
        f.write(f"{nom};{score}\n")


def charger_scores_texte():
    scores = []
    if not os.path.exists(SCORES_FILE):
        return scores
    with open(SCORES_FILE, "r", encoding="utf-8") as f:
        for ligne in f:
            ligne = ligne.strip()
            if ";" in ligne:
                nom, sc = ligne.split(";", 1)
                try:
                    scores.append((nom, int(sc)))
                except ValueError:
                    pass
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores


def top3_scores():
    scores = charger_scores_texte()
    return scores[:3]


# ---------- DESSIN / AFFICHAGE TEXTE ----------
def dessiner_texte(surface, texte, font, couleur, centre):
    rend = font.render(texte, True, couleur)
    rect = rend.get_rect(center=centre)
    surface.blit(rend, rect)


def dessiner_bouton(surface, texte, rect, couleur_fond, couleur_texte):
    pygame.draw.rect(surface, couleur_fond, rect, border_radius=10)
    pygame.draw.rect(surface, NOIR, rect, 2, border_radius=10)
    dessiner_texte(surface, texte, FONT_MOYENNE, couleur_texte, rect.center)


def construire_affichage_mot(mot_secret, lettres_trouvees):
    affichage = ""
    for lettre in mot_secret:
        if lettre in lettres_trouvees:
            affichage += lettre + " "
        else:
            affichage += "_ "
    return affichage.strip()


# ---------- ECRAN SCORES (texte complet) ----------
def ecran_scores():
    en_cours = True
    while en_cours:
        fenetre.blit(bg_western, (0, 0))
        dessiner_texte(fenetre, "Tableau des scores", FONT_GRANDE, NOIR, (LARGEUR // 2, 60))

        scores = charger_scores_texte()

        y = 130
        for i, (nom, sc) in enumerate(scores[:10], start=1):
            texte = f"{i}. {nom} - {sc}"
            dessiner_texte(fenetre, texte, FONT_PETITE, NOIR, (LARGEUR // 2, y))
            y += 35

        dessiner_texte(
            fenetre,
            "ESC ou clic = retour",
            FONT_PETITE,
            ROUGE,
            (LARGEUR // 2, HAUTEUR - 50),
        )

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                en_cours = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                en_cours = False

        pygame.display.flip()
        clock.tick(60)


def saisir_texte(invite):
    texte = ""
    en_cours = True
    while en_cours:
        fenetre.blit(bg_western, (0, 0))
        dessiner_texte(fenetre, invite, FONT_MOYENNE, NOIR, (LARGEUR // 2, 150))
        dessiner_texte(fenetre, texte + "|", FONT_MOYENNE, BLEU, (LARGEUR // 2, 250))
        dessiner_texte(
            fenetre,
            "Entrée = valider, ESC = annuler",
            FONT_PETITE,
            ROUGE,
            (LARGEUR // 2, 350),
        )

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return ""
                elif event.key == pygame.K_RETURN:
                    en_cours = False
                elif event.key == pygame.K_BACKSPACE:
                    texte = texte[:-1]
                else:
                    if len(event.unicode) == 1 and (event.unicode.isalpha() or event.unicode == " "):
                        texte += event.unicode.upper()

        pygame.display.flip()
        clock.tick(60)
    return texte.strip()


def ecran_ajout_mot():
    mot = saisir_texte("Tape un mot à ajouter :")
    if mot:
        ajouter_mot(mot)


def choisir_difficulte():
    en_cours = True
    vies = 7
    while en_cours:
        fenetre.blit(bg_western, (0, 0))
        dessiner_texte(fenetre, "Choisis la difficulté", FONT_GRANDE, NOIR, (LARGEUR // 2, 120))

        rect_facile = pygame.Rect(LARGEUR // 2 - 250, 220, 160, 60)
        rect_normal = pygame.Rect(LARGEUR // 2 - 80, 220, 160, 60)
        rect_difficile = pygame.Rect(LARGEUR // 2 + 90, 220, 160, 60)

        dessiner_bouton(fenetre, "Facile", rect_facile, (150, 255, 150), NOIR)
        dessiner_bouton(fenetre, "Normal", rect_normal, (255, 255, 150), NOIR)
        dessiner_bouton(fenetre, "Difficile", rect_difficile, (255, 150, 150), NOIR)

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if rect_facile.collidepoint(x, y):
                    vies = 7
                    en_cours = False
                elif rect_normal.collidepoint(x, y):
                    vies = 6
                    en_cours = False
                elif rect_difficile.collidepoint(x, y):
                    vies = 5
                    en_cours = False
    return vies


# ---------- LOGIQUE DU JEU AVEC SCORE + CHRONO + MULTIPLES MOTS ----------
def jouer_une_partie():
    vies_max = choisir_difficulte()
    vies_restantes = vies_max

    score_total = 0
    temps_restant = 60.0
    temps_derniere_mise_a_jour = time.time()

    mot_secret = mot_aleatoire()
    lettres_trouvees = set()
    lettres_ratees = set()

    en_jeu = True

    while en_jeu:
        dt = time.time() - temps_derniere_mise_a_jour
        temps_derniere_mise_a_jour = time.time()
        temps_restant -= dt
        if temps_restant <= 0:
            temps_restant = 0
            en_jeu = False  # fin : plus de temps

        clock.tick(60)
        fenetre.blit(bg_western, (0, 0))

        erreurs = len(lettres_ratees)

        # ----- MAPPING IMAGES SELON DIFFICULTE -----
        # images_pendu[0] = pendu1.png ... images_pendu[6] = pendu7.png
        if vies_max == 7:  # Facile : progression linéaire 1 -> 7
            # erreurs: 0 1 2 3 4 5 6 7 (on borne après)
            index_img = min(erreurs, 6)
        elif vies_max == 6:  # Normal : on « compresse » au milieu
            # erreurs: 0 1 2 3 4 5 6
            # index:   0 1 2 4 5 6 6  (saute pendu4 un peu plus tard)
            mapping = [0, 1, 2, 4, 5, 6, 6]
            index_img = mapping[min(erreurs, len(mapping) - 1)]
        else:  # Difficile (vies_max == 5)
            # erreurs: 0 1 2 3 4 5
            # index:   0 1 3 4 5 6  (on saute quelques étapes entre 3 et 7)
            mapping = [0, 1, 3, 4, 5, 6]
            index_img = mapping[min(erreurs, len(mapping) - 1)]

        img = images_pendu[index_img]

        pendu_rect = img.get_rect()
        pendu_rect.midbottom = (LARGEUR // 2, HAUTEUR - 40)
        fenetre.blit(img, pendu_rect)

        affichage_mot = construire_affichage_mot(mot_secret, lettres_trouvees)
        dessiner_texte(fenetre, affichage_mot, FONT_GRANDE, NOIR, (LARGEUR // 2, 80))

        dessiner_texte(
            fenetre,
            f"Lettres ratées : {' '.join(sorted(lettres_ratees))}",
            FONT_PETITE,
            ROUGE,
            (LARGEUR // 2, 150),
        )
        dessiner_texte(
            fenetre,
            f"Vies restantes : {vies_restantes}",
            FONT_PETITE,
            NOIR,
            (LARGEUR // 2, 190),
        )

        minutes = int(temps_restant) // 60
        secondes = int(temps_restant) % 60
        couleur_temps = (0, 200, 0) if temps_restant > 20 else (255, 165, 0) if temps_restant > 10 else (200, 0, 0)
        dessiner_texte(
            fenetre,
            f"Temps : {minutes:02d}:{secondes:02d}",
            FONT_PETITE,
            couleur_temps,
            (LARGEUR // 2, 230),
        )
        dessiner_texte(
            fenetre,
            f"Score : {score_total} pts",
            FONT_PETITE,
            BLEU,
            (LARGEUR // 2, 270),
        )

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.KEYDOWN and temps_restant > 0 and vies_restantes > 0:
                if event.unicode.isalpha():
                    lettre = event.unicode.upper()
                    if lettre in mot_secret:
                        if lettre not in lettres_trouvees:
                            lettres_trouvees.add(lettre)
                            nb = mot_secret.count(lettre)
                            score_total += nb
                    else:
                        if lettre not in lettres_ratees:
                            lettres_ratees.add(lettre)
                            vies_restantes -= 1  # perd une vie
                            if vies_restantes <= 0:
                                vies_restantes = 0
                                en_jeu = False  # fin : plus de vies

        # Mot terminé ?
        if all(l in lettres_trouvees for l in mot_secret) and temps_restant > 0 and vies_restantes > 0:
            score_total += 10      # bonus mot trouvé
            temps_restant += 10    # bonus temps

            # Nouveau mot : on reset les états pour le mot
            mot_secret = mot_aleatoire()
            lettres_trouvees.clear()
            lettres_ratees.clear()
            vies_restantes = vies_max  # réinitialise les vies à chaque nouveau mot

        pygame.display.flip()

    # Partie terminée : temps mort ou plus de vie
    score_final = score_total

    ecran_fin(mot_secret, score_final)


def ecran_fin(mot_secret, score_final):
    nom = ""
    en_cours = True
    pseudo_valide = False

    while en_cours:
        fenetre.blit(bg_western, (0, 0))

        dessiner_texte(
            fenetre,
            "Fin de la partie",
            FONT_GRANDE,
            ROUGE,
            (LARGEUR // 2, 80),
        )

        dessiner_texte(
            fenetre,
            f"Le mot était : {mot_secret}",
            FONT_MOYENNE,
            NOIR,
            (LARGEUR // 2, 150),
        )

        dessiner_texte(
            fenetre,
            f"Score : {score_final} pts",
            FONT_MOYENNE,
            NOIR,
            (LARGEUR // 2, 200),
        )

        if not pseudo_valide:
            dessiner_texte(
                fenetre,
                "Entre ton pseudo (3 lettres) puis Entrée :",
                FONT_PETITE,
                NOIR,
                (LARGEUR // 2, 260),
            )
            dessiner_texte(
                fenetre,
                nom + "|",
                FONT_MOYENNE,
                BLEU,
                (LARGEUR // 2, 310),
            )
        else:
            dessiner_texte(
                fenetre,
                "Top 3 scores :",
                FONT_PETITE,
                BLEU,
                (LARGEUR // 2, 260),
            )
            scores = top3_scores()
            y = 300
            for i, (pseudo, sc) in enumerate(scores, 1):
                texte = f"{i}. {pseudo} - {sc} pts"
                dessiner_texte(fenetre, texte, FONT_PETITE, NOIR, (LARGEUR // 2, y))
                y += 30

        dessiner_texte(
            fenetre,
            "ESC = retour au menu",
            FONT_PETITE,
            ROUGE,
            (LARGEUR // 2, 420),
        )

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    en_cours = False
                elif not pseudo_valide:
                    if event.key == pygame.K_RETURN:
                        pseudo = nom[:3].upper() if nom else "AAA"
                        pseudo_valide = True
                        sauver_score_texte(pseudo, score_final)
                    elif event.key == pygame.K_BACKSPACE:
                        nom = nom[:-1]
                    else:
                        if len(event.unicode) == 1 and event.unicode.isalpha():
                            if len(nom) < 3:
                                nom += event.unicode.upper()

        pygame.display.flip()
        clock.tick(60)


# ---------- MENU PRINCIPAL ----------
def menu_principal():
    en_cours = True

    while en_cours:
        clock.tick(60)
        fenetre.blit(bg_western, (0, 0))

        dessiner_texte(
            fenetre,
            "Le Meilleur Pendu",
            FONT_GRANDE,
            (80, 40, 0),
            (LARGEUR // 2, 80),
        )

        rect_jouer = pygame.Rect(LARGEUR // 2 - 150, 180, 300, 60)
        rect_ajout = pygame.Rect(LARGEUR // 2 - 150, 260, 300, 60)
        rect_scores = pygame.Rect(LARGEUR // 2 - 150, 340, 300, 60)
        rect_quitter = pygame.Rect(LARGEUR // 2 - 150, 420, 300, 60)

        couleur_bois = (153, 102, 51)
        couleur_rouge_sombre = (140, 30, 30)

        dessiner_bouton(fenetre, "Jouer", rect_jouer, couleur_bois, BLANC)
        dessiner_bouton(fenetre, "Ajouter un mot", rect_ajout, couleur_bois, BLANC)
        dessiner_bouton(fenetre, "Scores", rect_scores, couleur_bois, BLANC)
        dessiner_bouton(fenetre, "Quitter", rect_quitter, couleur_rouge_sombre, BLANC)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                en_cours = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if rect_jouer.collidepoint(x, y):
                    jouer_une_partie()
                elif rect_ajout.collidepoint(x, y):
                    ecran_ajout_mot()
                elif rect_scores.collidepoint(x, y):
                    ecran_scores()
                elif rect_quitter.collidepoint(x, y):
                    en_cours = False

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    menu_principal()
