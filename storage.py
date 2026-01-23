import os
from config import FICHIER_MOTS, FICHIER_SCORES


def charger_mots():
    """Charge les mots depuis le fichier, renvoie au moins ['PENDU']."""
    if not os.path.exists(FICHIER_MOTS):
        return ["PENDU"]

    mots = []
    with open(FICHIER_MOTS, "r", encoding="utf-8") as f:
        for ligne in f:
            mot = ligne.strip().upper()
            if mot:
                mots.append(mot)

    return mots or ["PENDU"]


def ajouter_mot(mot):
    mot = mot.strip().upper()
    if not mot:
        return
    with open(FICHIER_MOTS, "a", encoding="utf-8") as f:
        f.write(mot + "\n")


def sauver_score(nom, score):
    nom = (nom or "ANONYME").strip()
    with open(FICHIER_SCORES, "a", encoding="utf-8") as f:
        f.write(f"{nom};{score}\n")


def charger_scores():
    """Renvoie la liste [(nom, score)] triée du plus grand au plus petit."""
    scores = []
    if not os.path.exists(FICHIER_SCORES):
        return scores

    with open(FICHIER_SCORES, "r", encoding="utf-8") as f:
        for ligne in f:
            ligne = ligne.strip()
            if ";" not in ligne:
                continue
            nom, sc = ligne.split(";", 1)
            try:
                scores.append((nom, int(sc)))
            except ValueError:
                continue

    scores.sort(key=lambda x: x[1], reverse=True)
    return scores


def top3_scores():
    return charger_scores()[:3]
