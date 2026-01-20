import pygame
import random
import os

# ---------- CONSTANTES ----------
LARGEUR, HAUTEUR = 800, 600
BLANC = (255, 255, 255)
NOIR = (0, 0, 0)
BLEU = (50, 50, 200)
ROUGE = (200, 50, 50)

MOTS_FILE = "mots.txt"
SCORES_FILE = "scores.txt"

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
for i in range(1, 8):
    chemin = os.path.join("images", f"pendu{i}.png")
    img = pygame.image.load(chemin).convert_alpha()
    images_pendu.append(img)

# ---------- THEME WESTERN ----------
bg_western = pygame.image.load(os.path.join("images", "western_bg.png")).convert()
bg_western = pygame.transform.scale(bg_western, (LARGEUR, HAUTEUR))


# ---------- FONCTIONS UTILITAIRES FICHIERS ----------
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


def sauver_score(nom, score):
    nom = nom.strip()
    if not nom:
        nom = "ANONYME"
    with open(SCORES_FILE, "a", encoding="utf-8") as f:
        f.write(f"{nom};{score}\n")


def charger_scores():
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


# ---------- ECRANS ----------
def ecran_scores():
    en_cours = True
    while en_cours:
        fenetre.blit(bg_western, (0, 0))
        dessiner_texte(fenetre, "Tableau des scores", FONT_GRANDE, NOIR, (LARGEUR // 2, 60))

        scores = charger_scores()

        y = 130
        for i, (nom, sc) in enumerate(scores[:10], start=1):
            texte = f"{i}. {nom} - {sc}"
            dessiner_texte(fenetre, texte, FONT_PETITE, NOIR, (LARGEUR // 2, y))
            y += 35

        dessiner_texte(
            fenetre,
            "Appuie sur ESC ou clique pour revenir au menu",
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


# ---------- LOGIQUE DU JEU ----------
def jouer_une_partie():
    vies_max = choisir_difficulte()
    mot_secret = mot_aleatoire()
    lettres_trouvees = set()
    lettres_ratees = set()

    termine = False
    gagne = False

    while not termine:
        clock.tick(60)
        fenetre.blit(bg_western, (0, 0))

        # Calcul des erreurs et choix de l'image du pendu
        erreurs = len(lettres_ratees)
        index_img = min(erreurs, len(images_pendu) - 1)
        img = images_pendu[index_img]

        # Positionner le pendu centré en bas de l'écran
        pendu_rect = img.get_rect()
        pendu_rect.midbottom = (LARGEUR // 2, HAUTEUR - 40)  # 40 px au-dessus du bas
        fenetre.blit(img, pendu_rect)

        # Mot affiché au-dessus, centré
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
            f"Vies restantes : {vies_max - erreurs}",
            FONT_PETITE,
            NOIR,
            (LARGEUR // 2, 190),
        )

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.KEYDOWN:
                if event.unicode.isalpha():
                    lettre = event.unicode.upper()
                    if lettre in mot_secret:
                        if lettre not in lettres_trouvees:
                            lettres_trouvees.add(lettre)
                    else:
                        if lettre not in lettres_ratees:
                            lettres_ratees.add(lettre)

        if all(l in lettres_trouvees for l in mot_secret):
            gagne = True
            termine = True
        elif len(lettres_ratees) >= vies_max:
            gagne = False
            termine = True

        pygame.display.flip()

    erreurs = len(lettres_ratees)
    vies_restantes = max(0, vies_max - erreurs)
    base = 50 if vies_max == 7 else 100 if vies_max == 6 else 150
    score = base + vies_restantes * 10

    ecran_fin(mot_secret, gagne, score)


def ecran_fin(mot_secret, gagne, score):
    nom = ""
    en_cours = True
    while en_cours:
        fenetre.blit(bg_western, (0, 0))
        if gagne:
            dessiner_texte(
                fenetre,
                "Bravo, tu as gagné !",
                FONT_GRANDE,
                BLEU,
                (LARGEUR // 2, 100),
            )
        else:
            dessiner_texte(
                fenetre,
                "Dommage, tu as perdu !",
                FONT_GRANDE,
                ROUGE,
                (LARGEUR // 2, 100),
            )

        dessiner_texte(
            fenetre,
            f"Le mot était : {mot_secret}",
            FONT_MOYENNE,
            NOIR,
            (LARGEUR // 2, 180),
        )
        dessiner_texte(
            fenetre,
            f"Score : {score}",
            FONT_MOYENNE,
            NOIR,
            (LARGEUR // 2, 230),
        )

        dessiner_texte(
            fenetre,
            "Entre ton nom puis Entrée :",
            FONT_PETITE,
            NOIR,
            (LARGEUR // 2, 300),
        )
        dessiner_texte(
            fenetre,
            nom + "|",
            FONT_MOYENNE,
            BLEU,
            (LARGEUR // 2, 350),
        )

        dessiner_texte(
            fenetre,
            "ESC = ignorer, tu reviendras au menu",
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
                elif event.key == pygame.K_RETURN:
                    sauver_score(nom, score)
                    en_cours = False
                elif event.key == pygame.K_BACKSPACE:
                    nom = nom[:-1]
                else:
                    if len(event.unicode) == 1 and (event.unicode.isalnum() or event.unicode == " "):
                        if len(nom) < 15:
                            nom += event.unicode.upper()

        pygame.display.flip()
        clock.tick(60)


# ---------- MENU PRINCIPAL ----------
def menu_principal():
    en_cours = True

    while en_cours:
        clock.tick(60)

        # Fond western
        fenetre.blit(bg_western, (0, 0))

        # Titre style western
        dessiner_texte(
            fenetre,
            "Le Meilleur Pendu",
            FONT_GRANDE,
            (80, 40, 0),
            (LARGEUR // 2, 80),
        )

        # Boutons
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
