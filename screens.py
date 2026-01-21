import pygame
from config import (
    LARGEUR, HAUTEUR,
    BLANC, NOIR, BLEU, ROUGE,
)
from storage import ajouter_mot, charger_scores, top3_scores, sauver_score
from game_logic import construire_affichage_mot


def dessiner_texte(surface, texte, font, couleur, centre):
    rend = font.render(texte, True, couleur)
    rect = rend.get_rect(center=centre)
    surface.blit(rend, rect)


def dessiner_bouton(surface, texte, rect, couleur_fond, couleur_texte, font, bord=10):
    pygame.draw.rect(surface, couleur_fond, rect, border_radius=bord)
    pygame.draw.rect(surface, NOIR, rect, 2, border_radius=bord)
    dessiner_texte(surface, texte, font, couleur_texte, rect.center)


def saisir_texte(fenetre, clock, bg, fonts, invite):
    font_moy, font_petite = fonts[1], fonts[2]
    texte = ""
    en_cours = True
    while en_cours:
        fenetre.blit(bg, (0, 0))
        dessiner_texte(fenetre, invite, font_moy, NOIR, (LARGEUR // 2, 150))
        dessiner_texte(fenetre, texte + "|", font_moy, BLEU, (LARGEUR // 2, 250))
        dessiner_texte(
            fenetre,
            "Entrée = valider, ESC = annuler",
            font_petite,
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


def ecran_scores(fenetre, clock, bg, fonts):
    font_grande, _, font_petite = fonts
    en_cours = True
    while en_cours:
        fenetre.blit(bg, (0, 0))
        dessiner_texte(fenetre, "Tableau des scores", font_grande, NOIR, (LARGEUR // 2, 60))

        scores = charger_scores()
        y = 130
        for i, (nom, sc) in enumerate(scores[:10], start=1):
            texte = f"{i}. {nom} - {sc}"
            dessiner_texte(fenetre, texte, font_petite, NOIR, (LARGEUR // 2, y))
            y += 35

        dessiner_texte(
            fenetre,
            "ESC ou clic = retour",
            font_petite,
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


def ecran_ajout_mot(fenetre, clock, bg, fonts):
    mot = saisir_texte(fenetre, clock, bg, fonts, "Tape un mot à ajouter :")
    if mot:
        ajouter_mot(mot)


def choisir_difficulte(fenetre, clock, bg, fonts):
    font_grande, font_moyenne, font_petite = fonts
    en_cours = True
    vies = None
    while en_cours:
        fenetre.blit(bg, (0, 0))
        dessiner_texte(fenetre, "Choisis la difficulté", font_grande, NOIR, (LARGEUR // 2, 120))

        rect_facile = pygame.Rect(LARGEUR // 2 - 250, 220, 160, 60)
        rect_normal = pygame.Rect(LARGEUR // 2 - 80, 220, 160, 60)
        rect_difficile = pygame.Rect(LARGEUR // 2 + 90, 220, 160, 60)

        dessiner_bouton(fenetre, "Facile", rect_facile, (150, 255, 150), NOIR, font_moyenne)
        dessiner_bouton(fenetre, "Normal", rect_normal, (255, 255, 150), NOIR, font_moyenne)
        dessiner_bouton(fenetre, "Difficile", rect_difficile, (255, 150, 150), NOIR, font_moyenne)

        dessiner_texte(
            fenetre,
            "ESC = retour au menu",
            font_petite,
            ROUGE,
            (LARGEUR // 2, 320),
        )

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    vies = None
                    en_cours = False
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


def dessiner_jeu(fenetre, bg, fonts, images_pendu, partie):
    font_grande, _, font_petite = fonts
    fenetre.blit(bg, (0, 0))

    erreurs = len(partie.lettres_ratees)

    # --- Sélection de l'image du pendu ---
    img = None

    if erreurs > 0:
        # on décale pour que la 1ère erreur affiche pendu1 (index 0)
        e = erreurs - 1

        if partie.vies_max == 7:
            # Facile : progression linéaire 1 -> 7
            index_img = min(e, 6)
        elif partie.vies_max == 6:
            # Normal : mapping compressé
            mapping = [0, 1, 2, 4, 5, 6, 6]
            index_img = mapping[min(e, len(mapping) - 1)]
        else:
            # Difficile (5 vies)
            mapping = [0, 1, 3, 4, 5, 6]
            index_img = mapping[min(e, len(mapping) - 1)]

        img = images_pendu[index_img]

    # On ne dessine l'image que si on en a une (pas d'erreur => pas d'image)
    if img is not None:
        pendu_rect = img.get_rect()
        pendu_rect.midbottom = (LARGEUR // 2, HAUTEUR - 40)
        fenetre.blit(img, pendu_rect)

    # --- Affichage du mot, des infos, etc. ---
    affichage_mot = construire_affichage_mot(partie.mot_secret, partie.lettres_trouvees)
    dessiner_texte(fenetre, affichage_mot, font_grande, NOIR, (LARGEUR // 2, 80))

    dessiner_texte(
        fenetre,
        f"Lettres ratées : {' '.join(sorted(partie.lettres_ratees))}",
        font_petite,
        ROUGE,
        (LARGEUR // 2, 150),
    )
    dessiner_texte(
        fenetre,
        f"Vies restantes : {partie.vies_restantes}",
        font_petite,
        NOIR,
        (LARGEUR // 2, 190),
    )

    minutes = int(partie.temps_restant) // 60
    secondes = int(partie.temps_restant) % 60
    t = partie.temps_restant
    couleur_temps = (0, 200, 0) if t > 20 else (255, 165, 0) if t > 10 else (200, 0, 0)
    dessiner_texte(
        fenetre,
        f"Temps : {minutes:02d}:{secondes:02d}",
        font_petite,
        couleur_temps,
        (LARGEUR // 2, 230),
    )
    dessiner_texte(
        fenetre,
        f"Score : {partie.score} pts",
        font_petite,
        BLEU,
        (LARGEUR // 2, 270),
    )

    dessiner_texte(
        fenetre,
        f"Lettres ratées : {' '.join(sorted(partie.lettres_ratees))}",
        font_petite,
        ROUGE,
        (LARGEUR // 2, 150),
    )
    dessiner_texte(
        fenetre,
        f"Vies restantes : {partie.vies_restantes}",
        font_petite,
        NOIR,
        (LARGEUR // 2, 190),
    )

    minutes = int(partie.temps_restant) // 60
    secondes = int(partie.temps_restant) % 60
    t = partie.temps_restant
    couleur_temps = (0, 200, 0) if t > 20 else (255, 165, 0) if t > 10 else (200, 0, 0)
    dessiner_texte(
        fenetre,
        f"Temps : {minutes:02d}:{secondes:02d}",
        font_petite,
        couleur_temps,
        (LARGEUR // 2, 230),
    )
    dessiner_texte(
        fenetre,
        f"Score : {partie.score} pts",
        font_petite,
        BLEU,
        (LARGEUR // 2, 270),
    )


def ecran_fin(fenetre, clock, bg, fonts, mot_secret, score_final):
    from storage import top3_scores  # pour éviter cycle d'import en haut

    font_grande, font_moy, font_petite = fonts
    nom = ""
    en_cours = True
    pseudo_valide = False

    while en_cours:
        fenetre.blit(bg, (0, 0))

        dessiner_texte(
            fenetre,
            "Fin de la partie",
            font_grande,
            ROUGE,
            (LARGEUR // 2, 80),
        )

        dessiner_texte(
            fenetre,
            f"Le mot était : {mot_secret}",
            font_moy,
            NOIR,
            (LARGEUR // 2, 150),
        )

        dessiner_texte(
            fenetre,
            f"Score : {score_final} pts",
            font_moy,
            NOIR,
            (LARGEUR // 2, 200),
        )

        if not pseudo_valide:
            dessiner_texte(
                fenetre,
                "Entre ton pseudo (3 lettres) puis Entrée :",
                font_petite,
                NOIR,
                (LARGEUR // 2, 260),
            )
            dessiner_texte(
                fenetre,
                nom + "|",
                font_moy,
                BLEU,
                (LARGEUR // 2, 310),
            )
        else:
            dessiner_texte(
                fenetre,
                "Top 3 scores :",
                font_petite,
                BLEU,
                (LARGEUR // 2, 260),
            )
            scores = top3_scores()
            y = 300
            for i, (pseudo, sc) in enumerate(scores, 1):
                texte = f"{i}. {pseudo} - {sc} pts"
                dessiner_texte(fenetre, texte, font_petite, NOIR, (LARGEUR // 2, y))
                y += 30

        dessiner_texte(
            fenetre,
            "ESC = retour au menu",
            font_petite,
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
                        sauver_score(pseudo, score_final)
                    elif event.key == pygame.K_BACKSPACE:
                        nom = nom[:-1]
                    else:
                        if len(event.unicode) == 1 and event.unicode.isalpha():
                            if len(nom) < 3:
                                nom += event.unicode.upper()

        pygame.display.flip()
        clock.tick(60)


def jouer(fenetre, clock, bg, fonts, images_pendu, partie):
    en_cours = True
    retour_menu = False
    while en_cours and not retour_menu:
        dt = clock.tick(60) / 1000
        partie.mettre_a_jour_temps(dt)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    retour_menu = True
                elif not partie.terminee and partie.vies_restantes > 0 and partie.temps_restant > 0:
                    if event.unicode.isalpha():
                        partie.appliquer_lettre(event.unicode)

        if partie.mot_trouve() and not partie.terminee:
            partie.passer_au_mot_suivant()

        dessiner_jeu(fenetre, bg, fonts, images_pendu, partie)
        pygame.display.flip()

        if partie.terminee and not retour_menu:
            if partie.perdu:
                img_last = images_pendu[-1]
                fenetre.blit(bg, (0, 0))
                pendu_rect = img_last.get_rect()
                pendu_rect.midbottom = (LARGEUR // 2, HAUTEUR - 40)
                fenetre.blit(img_last, pendu_rect)
                pygame.display.flip()
                pygame.time.delay(1000)
            ecran_fin(fenetre, clock, bg, fonts, partie.mot_secret, partie.score)
            en_cours = False


def menu_principal(fenetre, clock, bg, fonts, images_pendu, PartiePenduClass):
    font_grande, font_moyenne, _ = fonts
    en_cours = True
    while en_cours:
        clock.tick(60)
        fenetre.blit(bg, (0, 0))

        dessiner_texte(
            fenetre,
            "Le Pendu",
            font_grande,
            (80, 40, 0),
            (LARGEUR // 2, 80),
        )

        rect_jouer = pygame.Rect(LARGEUR // 2 - 150, 180, 300, 60)
        rect_ajout = pygame.Rect(LARGEUR // 2 - 150, 260, 300, 60)
        rect_scores_rect = pygame.Rect(LARGEUR // 2 - 150, 340, 300, 60)
        rect_quitter = pygame.Rect(LARGEUR // 2 - 150, 420, 300, 60)

        couleur_bois = (153, 102, 51)
        couleur_rouge_sombre = (140, 30, 30)

        dessiner_bouton(fenetre, "Jouer", rect_jouer, couleur_bois, BLANC, font_moyenne)
        dessiner_bouton(fenetre, "Ajouter un mot", rect_ajout, couleur_bois, BLANC, font_moyenne)
        dessiner_bouton(fenetre, "Scores", rect_scores_rect, couleur_bois, BLANC, font_moyenne)
        dessiner_bouton(fenetre, "Quitter", rect_quitter, couleur_rouge_sombre, BLANC, font_moyenne)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                en_cours = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if rect_jouer.collidepoint(x, y):
                    vies = choisir_difficulte(fenetre, clock, bg, fonts)
                    if vies is not None:
                        partie = PartiePenduClass(vies)
                        jouer(fenetre, clock, bg, fonts, images_pendu, partie)
                elif rect_ajout.collidepoint(x, y):
                    ecran_ajout_mot(fenetre, clock, bg, fonts)
                elif rect_scores_rect.collidepoint(x, y):
                    ecran_scores(fenetre, clock, bg, fonts)
                elif rect_quitter.collidepoint(x, y):
                    en_cours = False

        pygame.display.flip()

    pygame.quit()
