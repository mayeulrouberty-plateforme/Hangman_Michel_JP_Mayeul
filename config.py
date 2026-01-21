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
BASE_DIR = os.path.dirname(__file__)
MOTS_FILE = os.path.join(BASE_DIR, "mots.txt")
SCORES_FILE = os.path.join(BASE_DIR, "scores.txt")
IMAGES_DIR = os.path.join(BASE_DIR, "images")
AUDIO_FILE = os.path.join(BASE_DIR, "audio.mp3")


def init_pygame():
    pygame.init()
    pygame.mixer.init()
    fenetre = pygame.display.set_mode((LARGEUR, HAUTEUR))
    pygame.display.set_caption("Le Pendu")
    clock = pygame.time.Clock()
    return fenetre, clock


def charger_fonts():
    font_grande = pygame.font.SysFont("comicsans", 60)
    font_moyenne = pygame.font.SysFont("comicsans", 40)
    font_petite = pygame.font.SysFont("comicsans", 30)
    return font_grande, font_moyenne, font_petite


def charger_images_pendu():
    images = []
    for i in range(1, 8):
        chemin = os.path.join(IMAGES_DIR, f"pendu{i}.png")
        img = pygame.image.load(chemin).convert_alpha()
        images.append(img)
    return images


def charger_background():
    bg = pygame.image.load(os.path.join(IMAGES_DIR, "western_bg.png")).convert()
    bg = pygame.transform.scale(bg, (LARGEUR, HAUTEUR))
    return bg


def init_musique():
    if os.path.exists(AUDIO_FILE):
        try:
            pygame.mixer.music.load(AUDIO_FILE)
            pygame.mixer.music.set_volume(0.6)
            pygame.mixer.music.play(-1)
        except pygame.error:
            print("Impossible de lire la musique.")
