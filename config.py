import pygame
import os

# Fenêtre
LARGEUR, HAUTEUR = 800, 600

# Couleurs
BLANC = (255, 255, 255)
NOIR = (0, 0, 0)
BLEU = (50, 50, 200)
ROUGE = (200, 50, 50)

# Fichiers / chemins
DOSSIER_BASE = os.path.dirname(__file__)
FICHIER_MOTS = os.path.join(DOSSIER_BASE, "mots.txt")
FICHIER_SCORES = os.path.join(DOSSIER_BASE, "scores.txt")
DOSSIER_IMAGES = os.path.join(DOSSIER_BASE, "images")
DOSSIER_SONS = os.path.join(DOSSIER_BASE, "sons")

FICHIER_MUSIQUE = os.path.join(DOSSIER_SONS, "audio.mp3")
FICHIER_SON_CLAVIER = os.path.join(DOSSIER_SONS, "keyboard_click.mp3")
FICHIER_SON_CORBEAU = os.path.join(DOSSIER_SONS, "corbeau.mp3")


def initialiser_pygame():
    pygame.init()
    pygame.mixer.init()
    fenetre = pygame.display.set_mode((LARGEUR, HAUTEUR))
    pygame.display.set_caption("Le Pendu")
    horloge = pygame.time.Clock()
    return fenetre, horloge


def charger_polices():
    police_grande = pygame.font.SysFont("comicsans", 60)
    police_moyenne = pygame.font.SysFont("comicsans", 40)
    police_petite = pygame.font.SysFont("comicsans", 30)
    return police_grande, police_moyenne, police_petite


def charger_images_pendu():
    images = []
    for i in range(1, 8):
        chemin = os.path.join(DOSSIER_IMAGES, f"pendu{i}.png")
        images.append(pygame.image.load(chemin).convert_alpha())
    return images


def charger_arriere_plan():
    image = pygame.image.load(os.path.join(DOSSIER_IMAGES, "western_bg.png")).convert()
    return pygame.transform.scale(image, (LARGEUR, HAUTEUR))


def initialiser_musique():
    if not os.path.exists(FICHIER_MUSIQUE):
        return
    try:
        pygame.mixer.music.load(FICHIER_MUSIQUE)
        pygame.mixer.music.set_volume(0.6)
        pygame.mixer.music.play(-1)
    except pygame.error:
        print("Impossible de lire la musique.")


def charger_sons():
    son_clavier = None
    son_corbeau = None
    try:
        if os.path.exists(FICHIER_SON_CLAVIER):
            son_clavier = pygame.mixer.Sound(FICHIER_SON_CLAVIER)
        if os.path.exists(FICHIER_SON_CORBEAU):
            son_corbeau = pygame.mixer.Sound(FICHIER_SON_CORBEAU)
    except pygame.error:
        print("Impossible de charger certains sons.")
    return son_clavier, son_corbeau
