import random
from storage import charger_mots


class PartiePendu:
    def __init__(self, vies_max, temps_initial=60.0):
        self.vies_max = vies_max
        self.vies_restantes = vies_max
        self.temps_restant = temps_initial
        self.score = 0

        self.mot_secret = self._nouveau_mot()
        self.lettres_trouvees = set()
        self.lettres_ratees = set()

        self.terminee = False
        self.perdu = False

    def _nouveau_mot(self):
        return random.choice(charger_mots())

    def appliquer_lettre(self, lettre):
        lettre = lettre.upper()
        if not lettre.isalpha() or self.terminee:
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

    def mettre_a_jour_temps(self, dt):
        if self.terminee:
            return
        self.temps_restant = max(0, self.temps_restant - dt)
        if self.temps_restant <= 0:
            self.terminee = True

    def mot_trouve(self):
        return all(l in self.lettres_trouvees for l in self.mot_secret)

    def passer_au_mot_suivant(self):
        self.score += 10
        self.temps_restant += 10
        self.mot_secret = self._nouveau_mot()
        self.lettres_trouvees.clear()
        self.lettres_ratees.clear()
        self.vies_restantes = self.vies_max
        self.terminee = False
        self.perdu = False


def construire_affichage_mot(mot_secret, lettres_trouvees):
    return " ".join([l if l in lettres_trouvees else "_" for l in mot_secret])
