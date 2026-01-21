import os
from config import MOTS_FILE, SCORES_FILE


def charger_mots():
    mots = []
    if not os.path.exists(MOTS_FILE):
        return ["PENDU"]
    with open(MOTS_FILE, "r", encoding="utf-8") as f:
        for ligne in f:
            mot = ligne.strip().upper()
            if mot:
                mots.append(mot)
    return mots or ["PENDU"]


def ajouter_mot(mot):
    mot = mot.strip().upper()
    if not mot:
        return
    with open(MOTS_FILE, "a", encoding="utf-8") as f:
        f.write(mot + "\n")


def sauver_score(nom, score):
    nom = (nom or "ANONYME").strip()
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


def top3_scores():
    return charger_scores()[:3]
