# Modèle Mathématique - Monitoring Débris Orbitaux

## Option A : Prototype Académique

Utilisation de TLE publics avec covariance approximée. Résultats indicatifs, non opérationnels.

---

## Vue d'ensemble du pipeline

```
TLE (Space-Track)
       ↓
   SGP4 Propagation
       ↓
   Position/Vitesse (ECI)
       ↓
   Screening grossier (distance < seuil)
       ↓
   Calcul TCA (Time of Closest Approach)
       ↓
   Covariance approximée (hypothèses fixes)
       ↓
   Pc estimé (formule de Chan ou Foster)
       ↓
   Affichage avec avertissement
```

---

## Étape 1 : Parsing TLE

### Format TLE (Two-Line Element)

```
ISS (ZARYA)
1 25544U 98067A   24025.50000000  .00016717  00000-0  10270-3 0  9025
2 25544  51.6400 208.9163 0006703  35.7821  74.4644 15.49560235425083
```

### Données extraites

| Champ | Valeur | Signification |
|-------|--------|---------------|
| Époque | 24025.5 | Jour 25.5 de 2024 |
| Inclinaison | 51.64° | Angle orbital |
| RAAN | 208.91° | Nœud ascendant |
| Excentricité | 0.0006703 | Quasi-circulaire |
| Argument périgée | 35.78° | Orientation ellipse |
| Anomalie moyenne | 74.46° | Position sur orbite |
| Mouvement moyen | 15.495 rev/jour | ~92 min par orbite |

---

## Étape 2 : Propagation SGP4

### Modèle SGP4 (Simplified General Perturbations 4)

**Prend en compte :**
- Aplatissement terrestre (J2, J3, J4)
- Traînée atmosphérique (terme B*)
- Effets lunisolaires (partiellement)

**Ne prend PAS en compte :**
- Pression de radiation solaire
- Marées terrestres
- Manœuvres

### Équations simplifiées

```
Position à t :
  a(t) = a₀ × (1 - δa × Δt)           # Demi-grand axe
  M(t) = M₀ + n × Δt + termes_J2      # Anomalie moyenne

  r⃗(t), v⃗(t) = f(a, e, i, Ω, ω, M)   # Coordonnées ECI
```

### Précision attendue

| Délai depuis époque TLE | Erreur position |
|-------------------------|-----------------|
| 0 jour | ~100 m - 1 km |
| 1 jour | ~1-3 km |
| 3 jours | ~5-10 km |
| 7 jours | ~10-30 km |

### Code Python (skyfield)

```python
from skyfield.api import load, EarthSatellite

ts = load.timescale()
satellite = EarthSatellite(line1, line2, name, ts)
t = ts.utc(2024, 1, 25, 12, 0, 0)
position = satellite.at(t)
r = position.position.km  # [x, y, z] en ECI
v = position.velocity.km_per_s
```

---

## Étape 3 : Screening grossier

### Problème combinatoire

- 25 000 objets = 312 millions de paires
- Impossible de tout calculer en temps réel

### Solution - Filtres successifs

| Filtre | Méthode | Réduction |
|--------|---------|-----------|
| 1. Altitude | \|h₁ - h₂\| < 50 km | ~90% éliminés |
| 2. MOID | Géométrie orbitale | ~95% restants éliminés |
| 3. Fenêtre temporelle | Propagation 7 jours | Paires finales |

### Calcul MOID simplifié

```
MOID ≈ |a₁(1-e₁) - a₂(1-e₂)|  si orbites quasi-circulaires
```

Si MOID > 50 km → pas de risque → ignorer la paire.

---

## Étape 4 : Calcul TCA (Time of Closest Approach)

### Méthode : Recherche itérative du minimum de distance

```
d(t) = ||r⃗₁(t) - r⃗₂(t)||

Trouver t* tel que d(t*) = min
```

### Algorithme

1. Propagation grossière (pas de 60s) sur fenêtre de 7 jours
2. Identifier les minima locaux < 50 km
3. Raffinement par dichotomie (pas de 1s puis 0.1s)
4. TCA = instant du minimum absolu

### Code conceptuel

```python
def find_tca(sat1, sat2, t_start, t_end, step=60):
    times = np.arange(t_start, t_end, step)
    distances = []
    for t in times:
        r1 = propagate(sat1, t)
        r2 = propagate(sat2, t)
        distances.append(np.linalg.norm(r1 - r2))

    # Trouver minimum et raffiner
    idx_min = np.argmin(distances)
    tca = refine_minimum(sat1, sat2, times[idx_min-1], times[idx_min+1])
    return tca, distances[idx_min]
```

---

## Étape 5 : Covariance approximée

### Problème

Pas de covariance fournie avec les TLE publics.

### Approximation standard (littérature)

| Composante | Valeur typique | Justification |
|------------|----------------|---------------|
| σ_radial | 100 - 500 m | Direction Terre-satellite |
| σ_along-track | 500 - 2000 m | Direction du mouvement (plus incertaine) |
| σ_cross-track | 100 - 500 m | Perpendiculaire au plan orbital |
| σ_velocity | 0.1 - 1 m/s | Chaque composante |

### Matrice de covariance simplifiée (diagonale)

```
C = diag(σ_r², σ_t², σ_n², σ_vr², σ_vt², σ_vn²)

Exemple conservateur :
C = diag(500², 1000², 500², 0.5², 1², 0.5²)  [m², (m/s)²]
```

### Limitation majeure

Ces valeurs sont des hypothèses génériques. La vraie covariance dépend de :
- Âge du TLE
- Qualité des observations
- Activité solaire (drag atmosphérique)
- Type d'objet (satellite actif vs débris)

---

## Étape 6 : Calcul de Pc (Probability of Collision)

### Hypothèses du modèle

1. Mouvement rectiligne au voisinage du TCA
2. Distributions gaussiennes des positions
3. Covariances indépendantes entre les deux objets

### Formule de Foster (1992) - Approche 2D

La probabilité est calculée dans le plan B (perpendiculaire à la vitesse relative) :

```
         1                    (  (x-μx)²     (y-μy)²  )
Pc = ―――――――――― ∬ exp( -½ ( ―――――― + ―――――― ) ) dx dy
     2π·σx·σy   A            (   σx²        σy²     )

Où A = disque de rayon R (rayon combiné des objets)
```

### Simplification (objets sphériques, covariance circulaire)

```
Pc ≈ (R_combined² / (2·σ²)) × exp(-d_miss² / (2·σ²))

Où :
- R_combined = R₁ + R₂ (rayons des objets, ~10m pour satellites)
- σ² = σ₁² + σ₂² (covariance combinée)
- d_miss = distance au TCA
```

### Exemple numérique

```
R_combined = 20 m (2 satellites de 10m)
σ = 1000 m (covariance combinée)
d_miss = 500 m

Pc ≈ (20² / (2×1000²)) × exp(-500² / (2×1000²))
Pc ≈ 0.0002 × 0.882
Pc ≈ 1.76 × 10⁻⁴
```

### Interprétation des seuils Pc

| Pc | Niveau | Action typique |
|----|--------|----------------|
| < 10⁻⁶ | Négligeable | Aucune |
| 10⁻⁶ - 10⁻⁵ | Faible | Surveillance |
| 10⁻⁵ - 10⁻⁴ | Modéré | Analyse approfondie |
| 10⁻⁴ - 10⁻³ | Élevé | Préparation manœuvre |
| > 10⁻³ | Critique | Manœuvre recommandée |

---

## Étape 7 : Limitations et avertissements

### Ce que le prototype peut affirmer

- "Approche détectée à ~X km le JJ/MM à HH:MM (±1h)"
- "Pc estimé : ~10⁻⁴ (ordre de grandeur indicatif)"
- "Surveillance recommandée"

### Ce que le prototype NE PEUT PAS affirmer

- "La collision est certaine/impossible"
- "La manœuvre doit être effectuée à T+6h"
- "Le risque est de exactement 1.76×10⁻⁴"

---

## Résumé des incertitudes cumulées

| Étape | Source d'erreur | Impact sur Pc |
|-------|-----------------|---------------|
| TLE | Données initiales imprécises | ×2 à ×10 |
| SGP4 | Modèle simplifié | ×1.5 à ×3 |
| Covariance | Hypothèses génériques | ×10 à ×100 |
| Formule Pc | Approximation 2D | ×1.2 à ×2 |
| **Total** | **Incertitude cumulée** | **×30 à ×600** |

---

## Conclusion

Le Pc calculé peut être faux d'un facteur 100. C'est un **ordre de grandeur indicatif**, pas une mesure précise.

Le prototype est utile pour :
- Sensibilisation au problème des débris
- Screening préliminaire
- Démonstration de concept

Le prototype n'est PAS adapté pour :
- Décisions opérationnelles de manœuvre
- Garantie de sécurité
- Usage par des opérateurs de satellites

---

## Références

- Foster, J.L. (1992). "The analytic basis for debris avoidance operations for the International Space Station"
- Chan, F.K. (2008). "Spacecraft Collision Probability"
- Alfano, S. (2005). "A numerical implementation of spherical object collision probability"
- NASA ORDEM 3.0 Documentation
- ESA Space Debris Office publications
