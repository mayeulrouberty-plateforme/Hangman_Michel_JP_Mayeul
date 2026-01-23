import random
from storage import charger_mots


class PartiePendu:
    """Gère l'état d'une partie de pendu."""

    def __init__(self, vies_max, temps_initial=60.0):
        self.vies_max = vies_max
        self.vies_restantes = vies_max
        self.temps_restant = temps_initial
        self.score = 0

        self.mot_secret = self._choisir_nouveau_mot()
        self.lettres_trouvees = set()
        self.lettres_ratees = set()

        self.terminee = False
        self.perdu = False

    # ---------- Mot ---------- #

    def _choisir_nouveau_mot(self):
        """Choisit un mot aléatoire dans la liste."""
        return random.choice(charger_mots())

    # ---------- Jeu ---------- #

    def appliquer_lettre(self, lettre):
        """Applique une lettre jouée par le joueur."""
        lettre = lettre.upper()

        if self.terminee or not lettre.isalpha():
            return

        if lettre in self.mot_secret:
            if lettre not in self.lettres_trouvees:
                self.lettres_trouvees.add(lettre)
                self.score += self.mot_secret.count(lettre)
        else:
            if lettre not in self.lettres_ratees:
                self.lettres_ratees.add(lettre)
                self.vies_restantes -= 1
                if self.vies_restantes <= 0:
                    self.vies_restantes = 0
                    self.terminee = True
                    self.perdu = True

    def mettre_a_jour_temps(self, dt_secondes):
        """Met à jour le timer, termine la partie si le temps est écoulé."""
        if self.terminee:
            return

        self.temps_restant = max(0, self.temps_restant - dt_secondes)
        if self.temps_restant <= 0:
            self.terminee = True

    def mot_trouve(self):
        """True si toutes les lettres du mot ont été trouvées."""
        return all(lettre in self.lettres_trouvees for lettre in self.mot_secret)

    def passer_au_mot_suivant(self):
        """Prépare un nouveau mot en gardant le score."""
        self.score += 10          # bonus mot trouvé
        self.temps_restant += 10  # bonus temps

        self.mot_secret = self._choisir_nouveau_mot()
        self.lettres_trouvees.clear()
        self.lettres_ratees.clear()
        self.vies_restantes = self.vies_max
        self.terminee = False
        self.perdu = False


def construire_affichage_mot(mot_secret, lettres_trouvees):
    """Construit l'affichage du mot avec '_' pour les lettres non trouvées."""
    return " ".join(
        lettre if lettre in lettres_trouvees else "_"
        for lettre in mot_secret
    )
