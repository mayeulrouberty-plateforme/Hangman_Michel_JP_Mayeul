from config import init_pygame, charger_fonts, charger_images_pendu, charger_background, init_musique
from game_logic import PartiePendu
from screens import menu_principal


def main():
    fenetre, clock = init_pygame()
    fonts = charger_fonts()
    images_pendu = charger_images_pendu()
    bg = charger_background()
    init_musique()

    menu_principal(fenetre, clock, bg, fonts, images_pendu, PartiePendu)


if __name__ == "__main__":
    main()
