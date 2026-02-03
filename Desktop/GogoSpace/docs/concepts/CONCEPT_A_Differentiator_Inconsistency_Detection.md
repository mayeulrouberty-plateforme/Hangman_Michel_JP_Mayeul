# Concept A : Angle Différenciant - Détection d'Incohérences

> **Parent** : [CONCEPT_A_CrossMatch_Agent.md](./CONCEPT_A_CrossMatch_Agent.md)
> **Dernière mise à jour** : 2025-01-26
> **Statut** : Validé comme différenciant (recherche effectuée)

---

## 1. Résumé

**Aucun outil public existant** ne propose la détection automatique d'incohérences entre catalogues astronomiques comme fonctionnalité utilisateur.

Les outils existants font du **cross-match** (associer les mêmes objets entre catalogues) mais ne **signalent pas** les anomalies.

---

## 2. État de l'art vérifié

### Ce qui existe

| Outil | Fonction | Détecte incohérences ? |
|-------|----------|------------------------|
| [nway](https://github.com/JohannesBuchner/nway) | Cross-match bayésien multi-catalogues | Non |
| [astromatch](https://github.com/ruizca/astromatch) | Cross-match statistique | Non |
| [Astropy coordinates](https://docs.astropy.org/en/stable/coordinates/matchsep.html) | Match par position | Non |
| [CDS XMatch](http://cdsxmatch.u-strasbg.fr/) | Service cross-match en ligne | Non |
| [AXS](https://github.com/astronomy-commons/axs) | Cross-match Spark distribué | Non |
| Gaia validation pipeline | QA interne ESA | Oui, mais **interne** |

### Ce qui n'existe pas publiquement

> Un outil qui dit : "Attention, pour cet objet, Gaia et SDSS donnent des valeurs contradictoires"

La [validation Gaia DR2](https://www.aanda.org/articles/aa/full_html/2019/01/aa34142-18/aa34142-18.html) détecte des discrepancies mais :
- Processus **interne** à l'ESA
- Résultats publiés dans des **papiers scientifiques**
- Pas d'outil accessible aux chercheurs

---

## 3. Types d'incohérences détectables

### 3.1 Incohérences photométriques

| Type | Description | Exemple |
|------|-------------|---------|
| Magnitude discordante | Δmag > erreur attendue | G_Gaia = 15.2 ± 0.01, g_SDSS = 16.1 ± 0.02 |
| Couleur impossible | Couleur hors plage physique | BP-RP vs g-r incompatibles |
| Variabilité non flaggée | Stable dans un catalogue, variable dans l'autre | |

### 3.2 Incohérences astrométriques

| Type | Description | Seuil typique |
|------|-------------|---------------|
| Position décalée | Δpos > erreur combinée | > 3σ position |
| Mouvement propre incohérent | PM Gaia vs PM catalogue ancien | |
| Parallaxe contradictoire | Distance photométrique vs parallaxe | |

### 3.3 Incohérences de présence

| Type | Description | Intérêt scientifique |
|------|-------------|---------------------|
| Présent A, absent B | Objet dans Gaia, pas dans SDSS | Objet très rouge/bleu, transitoire |
| Présent B, absent A | Objet dans SDSS, pas dans Gaia | Problème Gaia, objet étendu |
| Multiplicité | 1 source Gaia = 2 sources SDSS | Binaire résolue/non-résolue |

---

## 4. Valeur scientifique

### Pourquoi c'est utile ?

| Cas | Ce que ça révèle |
|-----|------------------|
| Magnitude discordante | Étoile variable, erreur calibration, blend |
| Position décalée | Mouvement propre élevé, binaire, erreur |
| Absent d'un catalogue | Objet transitoire, très rouge/bleu, artefact |
| Couleurs impossibles | Objet exotique, quasar, erreur cross-match |

### Exemples de découvertes potentielles

1. **Candidats variables** : magnitude différente entre époques Gaia vs SDSS
2. **Étoiles à haut mouvement propre** : position décalée au-delà de l'erreur
3. **Objets exotiques** : couleurs qui ne correspondent à aucun modèle stellaire
4. **Erreurs de catalogues** : QA pour les équipes de data

---

## 5. Implémentation technique

### 5.1 Algorithme de base

```python
def detect_inconsistencies(gaia_data, sdss_data, crossmatch):
    """
    Détecte les incohérences entre deux catalogues cross-matchés.

    Returns:
        list of dict: Anomalies détectées avec scores
    """
    anomalies = []

    for match in crossmatch:
        gaia = gaia_data[match.gaia_id]
        sdss = sdss_data[match.sdss_id]

        # 1. Incohérence photométrique
        mag_diff = abs(gaia.phot_g_mean_mag - sdss.g_mag)
        mag_error = sqrt(gaia.phot_g_mean_mag_error**2 + sdss.g_mag_err**2)

        if mag_diff > 3 * mag_error:  # > 3 sigma
            anomalies.append({
                'type': 'photometric',
                'gaia_id': match.gaia_id,
                'sdss_id': match.sdss_id,
                'delta': mag_diff,
                'sigma': mag_diff / mag_error,
                'severity': 'high' if mag_diff > 5 * mag_error else 'medium'
            })

        # 2. Incohérence positionnelle
        pos_diff = angular_separation(gaia.ra, gaia.dec, sdss.ra, sdss.dec)
        pos_error = sqrt(gaia.ra_error**2 + sdss.ra_err**2)  # simplification

        if pos_diff > 3 * pos_error:
            anomalies.append({
                'type': 'astrometric',
                'gaia_id': match.gaia_id,
                'delta_arcsec': pos_diff,
                'sigma': pos_diff / pos_error,
                'possible_cause': 'high_proper_motion' if gaia.pm > 50 else 'unknown'
            })

        # 3. Incohérence de couleur
        gaia_color = gaia.bp_rp
        sdss_color = sdss.g_mag - sdss.r_mag
        expected_sdss_color = transform_gaia_to_sdss_color(gaia_color)

        if abs(sdss_color - expected_sdss_color) > 0.3:  # mag
            anomalies.append({
                'type': 'color',
                'gaia_id': match.gaia_id,
                'gaia_bp_rp': gaia_color,
                'sdss_g_r': sdss_color,
                'expected': expected_sdss_color
            })

    return anomalies
```

### 5.2 Score d'anomalie composite

```python
def compute_anomaly_score(obj):
    """
    Calcule un score global d'anomalie (0-100).
    Plus le score est élevé, plus l'objet est intéressant.
    """
    score = 0

    # Pondérations
    weights = {
        'photometric': 30,
        'astrometric': 25,
        'color': 20,
        'missing': 25
    }

    for anomaly in obj.anomalies:
        base = weights.get(anomaly['type'], 10)
        sigma_factor = min(anomaly.get('sigma', 1) / 3, 3)  # cap at 3x
        score += base * sigma_factor

    return min(score, 100)
```

---

## 6. Interface utilisateur proposée

### 6.1 Vue "Anomaly Dashboard"

```
┌─────────────────────────────────────────────────────────────┐
│  🔍 Région analysée: RA=180°, Dec=+45°, r=0.5°             │
│  📊 Sources cross-matchées: 12,847                          │
│  ⚠️  Anomalies détectées: 127 (0.99%)                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Distribution des anomalies:                                │
│  ████████████████░░░░ Photométriques (67)                  │
│  ████████░░░░░░░░░░░░ Astrométriques (31)                  │
│  █████░░░░░░░░░░░░░░░ Couleur (19)                         │
│  ███░░░░░░░░░░░░░░░░░ Présence (10)                        │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  Top anomalies (par score):                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ #1 | Gaia 12345678 | Score: 87 | Δmag=1.2 (8.5σ)   │   │
│  │ #2 | Gaia 23456789 | Score: 72 | Missing SDSS      │   │
│  │ #3 | Gaia 34567890 | Score: 65 | Δpos=0.8" (5.2σ)  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  [Exporter CSV] [Voir sur Aladin] [Générer rapport]        │
└─────────────────────────────────────────────────────────────┘
```

### 6.2 Vue détaillée d'une anomalie

```
┌─────────────────────────────────────────────────────────────┐
│  Anomalie #1 - Score: 87/100                                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Identifiants:                                              │
│  • Gaia DR3: 1234567890123456789                           │
│  • SDSS DR17: 1237654321098765432                          │
│  • 2MASS: J12345678+4523456                                │
│                                                             │
│  Incohérence détectée: PHOTOMÉTRIQUE                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Catalogue │ Magnitude │ Erreur │                    │   │
│  │ Gaia G    │ 15.234    │ 0.002  │ ████████████████  │   │
│  │ SDSS g    │ 16.412    │ 0.015  │ ████████████████████│  │
│  │ Δ = 1.178 mag (8.5σ)           │                    │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Causes possibles (LLM):                                    │
│  • Étoile variable (probabilité: 65%)                      │
│  • Blend/contamination (probabilité: 20%)                  │
│  • Erreur de cross-match (probabilité: 10%)                │
│  • Autre (5%)                                              │
│                                                             │
│  Recommandations:                                           │
│  • Vérifier la courbe de lumière Gaia                      │
│  • Consulter les images SDSS pour contamination            │
│  • Comparer avec 2MASS/WISE pour SED complète              │
│                                                             │
│  [Voir dans SIMBAD] [Ouvrir Aladin] [Ajouter à watchlist]  │
└─────────────────────────────────────────────────────────────┘
```

---

## 7. Avantage compétitif

| Aspect | Outils existants | Notre solution |
|--------|------------------|----------------|
| Cross-match | ✅ | ✅ |
| Multi-catalogues | ✅ | ✅ |
| Langage naturel | ❌ (ou partiel) | ✅ |
| **Détection incohérences** | ❌ | ✅ |
| **Score d'anomalie** | ❌ | ✅ |
| **Suggestions LLM** | ❌ | ✅ |

---

## 8. Risques et limitations

| Risque | Mitigation |
|--------|------------|
| Faux positifs nombreux | Seuils ajustables, validation humaine |
| Interprétation difficile | LLM pour suggestions, liens vers docs |
| Transformations couleur imprécises | Utiliser transformations publiées (Gaia DR3 docs) |
| Volume de données | Limiter région, pagination |

---

## 9. Validation du concept

### Test rapide à faire

1. Prendre une région du ciel connue (ex: amas ouvert)
2. Cross-matcher Gaia + SDSS
3. Calculer Δmag pour tous les objets
4. Vérifier si les outliers sont des variables connues

Si les outliers correspondent à des objets intéressants connus → concept validé.

---

## 10. Sources

- [Gaia DR2 Cross-match validation](https://www.aanda.org/articles/aa/full_html/2019/01/aa34142-18/aa34142-18.html)
- [Gaia DR2 Photometric validation](https://www.aanda.org/articles/aa/full_html/2018/08/aa32756-18/aa32756-18.html)
- [nway - Bayesian cross-matching](https://github.com/JohannesBuchner/nway)
- [SNAD - anomaly detection in astronomy](https://snad.space/)
