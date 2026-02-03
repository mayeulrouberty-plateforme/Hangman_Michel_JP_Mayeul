# Calcul de Fenêtres de Lancement Sécurisées

## Objectif

Identifier les créneaux horaires où un lancement de satellite peut traverser les couches orbitales avec un risque minimal de collision avec les débris catalogués.

---

## Le problème à résoudre

Une fusée traverse **toutes les altitudes** de 0 à l'orbite cible (~400-800 km) en **8-12 minutes**. Pendant cette phase, elle est vulnérable aux collisions avec les ~25 000 objets catalogués.

---

## Contraintes d'une fenêtre de lancement

### 1. Contraintes orbitales (physique)

| Contrainte | Explication |
|------------|-------------|
| **Inclinaison** | Déterminée par la latitude du site de lancement |
| **RAAN** | Dépend de l'heure de lancement (rotation terrestre) |
| **Plan orbital cible** | Rendez-vous avec ISS, constellation, etc. |

**Formule de base :**
```
Inclinaison minimale = latitude du site de lancement

Ex: Kourou (5.2°N) → inclinaison min = 5.2°
    Baïkonour (45.6°N) → inclinaison min = 45.6°
```

### 2. Contraintes de sécurité (débris)

La trajectoire de montée doit éviter les "tubes de collision" autour de chaque objet catalogué.

```
Zone d'exclusion autour d'un débris :

    Cylindre de rayon R = vitesse_relative × temps_incertitude + marge_sécurité

    Typiquement : R ≈ 50-200 km (selon précision TLE)
```

---

## Méthode de calcul

### Étape 1 : Définir la trajectoire nominale

```
Entrées :
- Site de lancement (lat, lon)
- Orbite cible (altitude, inclinaison)
- Azimut de lancement

Sortie :
- Trajectoire r⃗(t) de T+0 à T+insertion (8-12 min)
- Positions successives tous les 10 secondes
```

### Étape 2 : Propager tous les objets catalogués

Pour chaque objet dans le catalogue TLE :

```python
for t in [T_lancement, T_lancement + 15 min]:
    position_debris[i] = propagate_sgp4(tle[i], t)
```

### Étape 3 : Calculer les distances minimales

```python
def check_launch_window(t_launch, trajectory, catalog):
    for t_flight in range(0, 900, 10):  # 0 à 15 min, pas de 10s
        pos_rocket = trajectory(t_flight)

        for debris in catalog:
            pos_debris = propagate(debris, t_launch + t_flight)
            distance = norm(pos_rocket - pos_debris)

            if distance < SEUIL_DANGER:  # ex: 50 km
                return False, debris, t_flight

    return True, None, None
```

### Étape 4 : Scanner les fenêtres possibles

```python
def find_safe_windows(date, duration_hours=24, step_minutes=1):
    safe_windows = []

    for t in range(0, duration_hours * 60, step_minutes):
        t_launch = date + timedelta(minutes=t)
        is_safe, _, _ = check_launch_window(t_launch, trajectory, catalog)

        if is_safe:
            safe_windows.append(t_launch)

    # Fusionner les fenêtres consécutives
    return merge_consecutive_windows(safe_windows)
```

---

## Visualisation du résultat

```
Fenêtres de lancement pour le 15/02/2026 (Kourou → LEO 550km)

00:00 ████████░░░░████░░░░░░██████████░░░░████████ 24:00
      |-- sûr --|     |--- sûr ---|    |-- sûr --|

Légende :
█ = Fenêtre sûre (aucun objet < 50 km de la trajectoire)
░ = Fenêtre à risque (approche détectée)

Détail des blocages :
- 02:15-02:45 : COSMOS 2251 DEB (NORAD 34567) à 23 km
- 06:30-08:00 : Constellation Starlink (multiples passages)
- 15:20-15:35 : ISS à 45 km
```

---

## Complexité et faisabilité

### Avec données TLE publiques

| Aspect | Faisabilité | Précision |
|--------|-------------|-----------|
| Identification des fenêtres | Possible | ±10-30 min |
| Évitement objets majeurs | Fiable | Marge 50+ km |
| Évitement petits débris | Limité | Non catalogués invisibles |
| Fenêtres opérationnelles | Insuffisant | Requiert données précises |

### Limitations honnêtes

1. **Débris non catalogués** : ~1 million d'objets > 1 cm ne sont pas trackés
2. **Précision TLE** : Erreur de position = ±1-10 km
3. **Trajectoire réelle** : Varie selon conditions météo, performance moteur
4. **Temps réel** : Les opérateurs reçoivent des updates jusqu'à T-30 min

---

## Comparaison avec les opérateurs réels

| Acteur | Méthode |
|--------|---------|
| **SpaceX** | COLA automatisé avec données 18th SDS |
| **ESA/Arianespace** | Coordination avec CNES CAESAR |
| **NASA** | Conjunction Assessment via JSC |

Ils utilisent :
- Données haute précision (SP ephemeris, pas TLE)
- Mises à jour en temps réel (T-24h, T-6h, T-30min)
- Marges de sécurité réduites (5-10 km) grâce à la précision

---

## Proposition pour le prototype

### Fonctionnalité réaliste à implémenter

```
ENTRÉES UTILISATEUR :
- Site de lancement (dropdown : Kourou, Cap Canaveral, Baïkonour...)
- Orbite cible (altitude, inclinaison)
- Période d'analyse (ex: 7 jours)

SORTIES :
- Timeline visuelle des fenêtres "vertes" vs "rouges"
- Liste des objets bloquants avec heure de passage
- Score de confiance (basé sur âge des TLE)

AVERTISSEMENT AFFICHÉ :
"Analyse indicative basée sur TLE publics.
Ne constitue pas une validation opérationnelle.
Consulter l'autorité de lancement pour validation finale."
```

---

## Formules clés

### Distance minimale trajectoire-objet

```
d_min = min over t of ||r_rocket(t) - r_debris(t)||

Avec marge temporelle :
d_safe = d_min - (σ_rocket + σ_debris) × 3  # Règle 3-sigma
```

### Durée de fenêtre sûre

```
Si aucun objet ne passe à moins de 50 km pendant 15 min :
→ Fenêtre de lancement = [T - 5 min, T + 5 min]

Marge réduite car trajectoire fixe, pas de manœuvre possible après T+0.
```

---

## Modélisation de la trajectoire de montée

### Profil simplifié (gravity turn)

```
Phase 1 : Montée verticale (0-10 km)
  - Accélération constante ~3g
  - Durée : ~30 secondes

Phase 2 : Gravity turn (10-100 km)
  - Inclinaison progressive vers l'horizontale
  - Durée : ~2 minutes

Phase 3 : Insertion orbitale (100-200 km)
  - Accélération horizontale
  - Circularisation
  - Durée : ~5-8 minutes
```

### Équations paramétriques

```
Altitude h(t) :
  h(t) = h_0 + v_0*t + 0.5*a*t² - corrections_gravité

Position angulaire θ(t) :
  θ(t) = θ_0 + ω_terre*t + Δθ_propulsion

Coordonnées ECI :
  x(t) = (R_terre + h(t)) * cos(θ(t)) * cos(φ(t))
  y(t) = (R_terre + h(t)) * sin(θ(t)) * cos(φ(t))
  z(t) = (R_terre + h(t)) * sin(φ(t))
```

---

## Algorithme d'optimisation

### Objectif

Trouver la fenêtre de lancement qui maximise la distance minimale aux débris.

```python
def optimize_launch_window(date_range, trajectory, catalog):
    best_window = None
    best_min_distance = 0

    for t_launch in date_range:
        min_distance = float('inf')

        for t_flight in flight_timeline:
            for debris in catalog:
                d = distance(trajectory(t_flight), debris.position(t_launch + t_flight))
                min_distance = min(min_distance, d)

        if min_distance > best_min_distance:
            best_min_distance = min_distance
            best_window = t_launch

    return best_window, best_min_distance
```

### Optimisation par gradient

Pour réduire le temps de calcul (25 000 objets × 1440 minutes × 90 points de trajectoire) :

1. **Pré-filtrage par altitude** : Éliminer les objets hors de la plage 0-800 km
2. **Indexation spatiale** : Octree ou grille 3D pour recherche rapide
3. **Parallélisation** : Calcul multi-thread par fenêtre temporelle
4. **Cache TLE** : Éviter de re-propager les mêmes objets

---

## Intégration dans l'application

### Nouvel onglet : "Launch Window Planner"

```
┌─────────────────────────────────────────────────────────┐
│  🚀 Launch Window Planner                               │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Site de lancement : [Kourou (CSG)        ▼]           │
│  Orbite cible      : [550] km  Inclinaison: [51.6]°    │
│  Période d'analyse : [2026-02-15] à [2026-02-22]       │
│                                                         │
│  [🔍 Analyser les fenêtres]                            │
│                                                         │
├─────────────────────────────────────────────────────────┤
│  Résultats : 47 fenêtres sûres identifiées              │
│                                                         │
│  15/02 ██░░██████░░░░████░░██████████░░████             │
│  16/02 ░░████████░░██████░░░░░░████████░░██             │
│  ...                                                    │
│                                                         │
│  ⚠️ Analyse indicative - Validation opérationnelle     │
│     requise avant lancement réel.                       │
└─────────────────────────────────────────────────────────┘
```

---

## Références

- Vallado, D. "Fundamentals of Astrodynamics and Applications"
- NASA Launch Services Program - Range Safety Requirements
- CNES - "Conjunction Assessment for Launch Operations"
- FAA - Commercial Space Launch Requirements (14 CFR Part 450)
