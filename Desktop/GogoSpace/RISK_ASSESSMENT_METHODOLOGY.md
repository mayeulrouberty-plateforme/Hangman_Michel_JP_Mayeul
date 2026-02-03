# Méthodologie d'Évaluation des Risques de Lancement

> Documentation technique du module `launch_risk.py`
> Cosmic Query Agent - ActInSpace 2025

---

## Vue d'Ensemble

Le système d'évaluation des risques analyse la probabilité de succès d'un lancement spatial en prenant en compte la densité de débris, les risques de collision et les événements de conjonction dans l'orbite cible.

---

## Architecture du Score de Risque (0-100)

Le score global est la **somme de 5 facteurs de risque** :

```
Score Total = Densité Débris + Collision + Conjonctions + Congestion + Temporel
              (0-25 pts)       (0-30 pts)  (0-20 pts)     (0-15 pts)   (0-10 pts)
```

### Interprétation du Score

| Score | Niveau | Indicateur | Action Recommandée |
|-------|--------|------------|-------------------|
| 0-20 | Low | 🟢 | Procéder avec protocoles standards |
| 20-40 | Moderate | 🟡 | Surveillance accrue recommandée |
| 40-60 | Elevated | 🟠 | Optimisation fenêtre de lancement |
| 60-100 | High | 🔴 | Report recommandé pour analyse détaillée |

---

## 1. Densité de Débris (0-25 points)

### Formule

```python
# Volume de la coquille orbitale (km³)
R_interne = 6371 + altitude_min  # Rayon terrestre + altitude min
R_externe = 6371 + altitude_max  # Rayon terrestre + altitude max

Volume = (4/3) × π × (R_externe³ - R_interne³)

# Densité par 1000 km³
Densité = (Nombre_objets_dans_bande / Volume) × 1000

# Score de risque (plafonné à 25)
debris_risk = min(Densité × 1000, 25)
```

### Seuils de Densité

| Densité (obj/1000 km³) | Niveau de Risque |
|------------------------|------------------|
| < 0.001 | Low |
| 0.001 - 0.01 | Moderate |
| 0.01 - 0.1 | Elevated |
| > 0.1 | High |

### Catégorisation des Objets

- **DEBRIS** : Fragments de collision, débris opérationnels
- **ROCKET BODY** : Étages de fusées abandonnés
- **PAYLOAD** : Satellites (actifs ou inactifs)

---

## 2. Probabilité de Collision (0-30 points)

### Calcul de Distance 3D

```python
# Conversion coordonnées géographiques vers distance (km)
lat_diff = |trajectoire_lat - objet_lat| × 111
lon_diff = |trajectoire_lon - objet_lon| × 111 × cos(trajectoire_lat)
alt_diff = |trajectoire_alt - objet_alt|

# Distance euclidienne 3D
distance = √(lat_diff² + lon_diff² + alt_diff²)
```

> **Note** : 111 km ≈ 1 degré de latitude à la surface terrestre

### Calcul de Probabilité

```python
# Pour chaque approche < seuil (20 km par défaut)
# Somme pondérée inverse de la distance
risk_sum = Σ (1 / (distance_km + 0.1))

# Probabilité de collision (%)
probability = min(risk_sum × 0.1, 99.9)

# Score de risque (plafonné à 30)
collision_risk = min(probability × 0.3, 30)
```

### Logique

Plus un objet est proche de la trajectoire, plus sa contribution au risque est élevée (relation inverse). Le terme `+0.1` évite la division par zéro.

---

## 3. Événements de Conjonction (0-20 points)

### Formule

```python
# Nombre d'objets passant à moins du seuil de la trajectoire
conjunction_risk = min(nombre_approches_proches × 2, 20)
```

### Classification des Approches

| Distance (km) | Niveau | Description |
|---------------|--------|-------------|
| < 1 | **Critical** | Risque de collision imminent |
| 1 - 5 | **High** | Manœuvre d'évitement potentielle |
| 5 - 20 | **Moderate** | Surveillance requise |

### Données Retournées

Pour chaque conjonction détectée :
- Nom de l'objet
- Type (DEBRIS, PAYLOAD, ROCKET BODY)
- NORAD ID
- Distance minimale (km)
- Altitudes respectives
- Niveau de risque

---

## 4. Congestion Orbitale (0-15 points)

### Formule

```python
# Basé sur le nombre total d'objets dans la bande d'altitude cible
congestion_risk = min(total_objects / 100, 15)
```

### Interprétation

| Objets dans la bande | Score |
|---------------------|-------|
| 0-100 | 0-1 |
| 100-500 | 1-5 |
| 500-1000 | 5-10 |
| >1500 | 15 (max) |

---

## 5. Facteur Temporel (0-10 points)

### Formule

```python
heure = heure_lancement (0-23)

if 6 ≤ heure ≤ 18:  # Journée
    time_risk = 5
else:               # Nuit
    time_risk = 2
```

### Justification

- Activité opérationnelle accrue en journée
- Plus de manœuvres de satellites
- Communications plus fréquentes

---

## Probabilité de Succès

### Formule

```python
# Probabilité de base (inverse du risque)
base_success = 100 - overall_risk_score

# Facteur de fiabilité historique des lanceurs
# Les lanceurs modernes ont ~95-98% de fiabilité
success_probability = max(min(base_success × 0.98, 99.5), 50)
```

### Contraintes

- **Maximum** : 99.5% (aucun lancement n'est garanti)
- **Minimum** : 50% (même en conditions difficiles)

---

## Génération de Trajectoire

### Modèle Simplifié de Phase Ascensionnelle

```python
# Paramètres
t = 0 à 1 (progression normalisée)
durée_totale ≈ 600 secondes (10 minutes)

# Profil d'altitude (exponentiel)
altitude(t) = altitude_cible × (1 - e^(-3t))

# Distance au sol (downrange)
downrange(t) = t × 500 km

# Profil de vitesse
velocity(t) = 7.8 × t km/s
```

### Calcul de l'Azimut de Lancement

```python
# Inclinaison orbitale cible
inc = inclinaison_orbite

# Latitude du site de lancement
lat = latitude_site

if inc > |lat|:
    azimut = 90 - arcsin(cos(inc) / cos(lat))
else:
    azimut = 90  # Lancement vers l'est
```

---

## Paramètres d'Entrée

| Paramètre | Source | Utilisation |
|-----------|--------|-------------|
| **Position objets (lat, lon, alt)** | Space-Track.org / Celestrak | Calcul distances |
| **Type objet** | Métadonnées TLE | Classification DEBRIS/PAYLOAD/ROCKET |
| **Altitude cible (min, max)** | Orbite sélectionnée | Filtrage bande de densité |
| **Inclinaison orbitale** | Orbite sélectionnée | Calcul azimut |
| **Site de lancement (lat, lon)** | Base de données interne | Point de départ trajectoire |
| **Date/heure de lancement** | Input utilisateur | Facteur temporel |

---

## Sites de Lancement Supportés

| Site | Latitude | Longitude | Pays |
|------|----------|-----------|------|
| Kourou (CSG) | 5.236° | -52.775° | Guyane Française |
| Cape Canaveral | 28.396° | -80.605° | USA |
| Vandenberg | 34.632° | -120.611° | USA |
| Baikonur | 45.965° | 63.305° | Kazakhstan |
| Jiuquan | 40.958° | 100.291° | Chine |
| Tanegashima | 30.400° | 130.969° | Japon |
| Sriharikota | 13.720° | 80.230° | Inde |
| Plesetsk | 62.925° | 40.577° | Russie |
| Mahia Peninsula | -39.262° | 177.864° | Nouvelle-Zélande |
| Starbase Boca Chica | 25.997° | -97.157° | USA |

---

## Orbites Cibles Supportées

| Orbite | Alt. Min (km) | Alt. Max (km) | Inclinaison Typique |
|--------|---------------|---------------|---------------------|
| LEO (400km) | 350 | 450 | 51.6° |
| LEO (550km - Starlink) | 500 | 600 | 53.0° |
| SSO (600km) | 550 | 650 | 97.8° |
| MEO (20000km) | 19,000 | 21,000 | 55.0° |
| GTO | 200 | 35,786 | 6.0° |
| GEO | 35,700 | 35,900 | 0.0° |

---

## Fenêtres de Lancement Optimales

Le système génère 6 fenêtres sur 24h avec variation de risque :

```python
for i in range(6):
    window_time = base_time + (i × 4 heures)

    # Variation sinusoïdale du risque
    window_risk = overall_risk × (0.85 + 0.3 × |sin(i)|)

    recommendation = "optimal" if window_risk < overall_risk else "acceptable"
```

---

## Limitations du Modèle

1. **Trajectoire simplifiée** : Modèle exponentiel, pas de simulation physique complète
2. **Positions statiques** : Ne propage pas les orbites des objets en temps réel
3. **Distance euclidienne** : Approximation, pas de calcul de TCA (Time of Closest Approach)
4. **Pas de covariance** : N'utilise pas les matrices de covariance des TLE
5. **Facteur temporel basique** : Ne prend pas en compte les cycles d'activité solaire

---

## Améliorations Futures

- [ ] Intégration SGP4 pour propagation orbitale en temps réel
- [ ] Matrices de covariance pour probabilité de collision précise
- [ ] Données météo spatiales (activité solaire, flux)
- [ ] Historique des manœuvres d'évitement
- [ ] Machine learning sur données historiques de conjonction

---

## Références

- **Space-Track.org** : Source primaire des TLE et catalogues
- **Celestrak** : Données TLE publiques
- **ESA Space Debris Office** : Méthodologies de référence
- **NASA Conjunction Assessment** : Standards de l'industrie

---

*Documentation générée le 2026-01-31*
*Module : `src/launch_risk.py`*
