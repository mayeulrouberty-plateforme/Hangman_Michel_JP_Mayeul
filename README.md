# Le Pendu 

Jeu du pendu en Python avec interface graphique réalisée avec Pygame.  
Le joueur doit deviner un mot avant la fin du temps et avant que le pendu ne soit entièrement affiché. Le jeu propose plusieurs niveaux de difficulté, un système de scores et la possibilité d’ajouter ses propres mots.

***

## Fonctionnalités

- Interface graphique complète avec **Pygame**  
- 3 niveaux de difficulté : **Facile**, **Normal**, **Difficile**  
- Chronomètre global avec bonus de temps à chaque mot trouvé  
- Score cumulatif avec **bonus par mot correctement deviné**  
- Gestion des scores persistants dans `scores.txt` et affichage du **Top 3 / Top 10**  
- Ajout de nouveaux mots via le menu (stockés dans `mots.txt`)  
- Thème western avec images du pendu (`images/pendu1.png` … `pendu7.png`)  
- Musique de fond optionnelle via `audio.mp3`  

***

## Installation

### Prérequis

- Python 3.8+  
- Pygame installé dans l’environnement courant :

```bash
pip install pygame
```

ou avec un environnement virtuel :

```bash
python -m venv .venv
source .venv/bin/activate    # macOS / Linux
# .venv\Scripts\activate.bat # Windows

pip install pygame
```

### Cloner le dépôt

```bash
git clone https://github.com/mayeulrouberty-plateforme/Hangman_Michel_JP_Mayeul.git
cd Hangman_Michel_JP_Mayeul
```

Structure attendue du projet :

```text
Hangman_Michel_JP_Mayeul/
  main.py
  config.py
  storage.py
  game_logic.py
  screens.py
  mots.txt
  scores.txt
  images/
    pendu1.png
    pendu2.png
    ...
    pendu7.png
    western_bg.png
  audio.mp3   (optionnel)
```

***

## Lancer le jeu

Depuis la racine du projet :

```bash
python main.py
```

Avec un environnement virtuel activé :

```bash
source .venv/bin/activate
python main.py
```

***

## Commandes & gameplay

### Menu principal

- **Jouer** : lance une nouvelle partie  
- **Ajouter un mot** : ajoute un mot dans `mots.txt`  
- **Scores** : affiche le tableau des scores  
- **Quitter** : ferme le jeu  

### Pendant la partie

- Tapez des lettres au clavier pour proposer des lettres.  
- Le pendu commence à apparaître **à partir de la première erreur**.  
- À chaque mot trouvé :
  - des points sont ajoutés au score ;
  - un bonus de temps est ajouté ;
  - un nouveau mot est lancé avec les vies réinitialisées.  
- La partie se termine si :
  - le temps tombe à **0**, ou  
  - vous n’avez plus de vies.

**Touches :**

- **A–Z** : proposer une lettre  
- **Échap (ESC)** : retour au menu principal  

### Écran de fin

- Entrez un pseudo de 3 lettres, puis validez avec **Entrée** pour enregistrer votre score.  
- Appuyez sur **ESC** pour retourner au menu principal.  

***

## Fichiers importants

- `main.py` : point d’entrée du jeu  
- `config.py` : configuration générale (fenêtre, couleurs, chemins, ressources)  
- `storage.py` : gestion des fichiers `mots.txt` et `scores.txt`  
- `game_logic.py` : logique du pendu (vies, temps, score, mots)  
- `screens.py` : affichage Pygame (menus, écran de jeu, écran de fin, etc.)  
- `mots.txt` : liste des mots possibles  
- `scores.txt` : scores sauvegardés  

***

## Idées d’améliorations

- Animations et effets sonores pour les erreurs et les mots trouvés  
- Mode multijoueur (tour par tour)  
- Menu d’options (durée, nombre de vies, thèmes graphiques)  
- Localisation du jeu en plusieurs langues (FR / EN, etc.)  

***

## Licence

Projet réalisé à des fins d’apprentissage.  
Vous êtes libre de le forker, le modifier et l’améliorer pour vos propres projets.
