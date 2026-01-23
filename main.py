from config import (
    initialiser_pygame,
    charger_polices,
    charger_images_pendu,
    charger_arriere_plan,
    initialiser_musique,
    charger_sons,
)
from game_logic import PartiePendu
from screens import menu_principal


def main():
    fenetre, horloge = initialiser_pygame()
    polices = charger_polices()
    images_pendu = charger_images_pendu()
    arriere_plan = charger_arriere_plan()

    initialiser_musique()
    son_clavier, son_corbeau = charger_sons()

    menu_principal(
        fenetre,
        horloge,
        arriere_plan,
        polices,
        images_pendu,
        PartiePendu,
        son_clavier,
        son_corbeau,
    )


if __name__ == "__main__":
    main()
