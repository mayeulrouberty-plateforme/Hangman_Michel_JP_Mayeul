# Concept C : Structure Predictor

> **Statut** : En exploration
> **Dernière mise à jour** : 2025-01-26
> **Priorité** : Basse (trop ambitieux pour 24h)

---

## Résumé

Un modèle prédictif qui estime la distribution de matière (visible et noire) dans les zones non encore cartographiées de l'univers, en extrapolant à partir des patterns observés dans les superstructures cosmologiques connues.

---

## Problème adressé

- **Cartographie incomplète** : seule une fraction du ciel est observée en détail
- **Planification d'observations** : où pointer les télescopes en priorité ?
- **Modèles de matière noire** : besoin de prédictions testables
- **Compréhension des superstructures** : filaments, vides, murs cosmiques

---

## Solution proposée

### Fonctionnalités visées

1. **Apprentissage des patterns** :
   - Entraînement sur les structures connues (filaments, amas, vides)
   - Corrélation position-densité-environnement

2. **Prédiction spatiale** :
   - Estimation de densité de matière pour régions non observées
   - Carte de probabilité de présence de structures

3. **Validation croisée** :
   - Comparaison prédictions vs observations réelles
   - Métriques de confiance

---

## Architecture technique (ébauche)

```
┌─────────────────────────────────────┐
│     Données d'entraînement          │
│  (Catalogues + Simulations N-body)  │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│        Feature Engineering          │
│  - Densité locale                   │
│  - Distance aux structures connues  │
│  - Redshift                         │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│         Modèle prédictif            │
│  (Graph Neural Network / CNN 3D)    │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│      Carte de prédiction 3D         │
│   + Incertitudes / Intervalles      │
└─────────────────────────────────────┘
```

---

## Approches ML possibles

| Méthode | Avantage | Inconvénient |
|---------|----------|--------------|
| Graph Neural Networks | Capture topologie des structures | Complexe à implémenter |
| CNN 3D | Bon pour patterns spatiaux | Nécessite voxelisation |
| Gaussian Process | Incertitudes natives | Ne scale pas |
| Neural Density Estimation | Flexible | Besoin de beaucoup de données |

---

## Données nécessaires

### Observations réelles
- Catalogues de redshift (SDSS, 2dFGRS, 6dFGS)
- Catalogues d'amas de galaxies
- Cartes de lentilles gravitationnelles (weak lensing)

### Simulations
- Illustris-TNG
- EAGLE
- Millennium Simulation

---

## Faisabilité 24h

| Aspect | Évaluation |
|--------|------------|
| Complexité technique | **Très haute** |
| Données disponibles | Partiellement |
| Prototype réalisable | **Non réaliste** |
| Démo convaincante | Difficile |

### Pourquoi c'est trop ambitieux

1. **Entraînement lourd** : GNN/CNN 3D nécessitent GPU et temps
2. **Préparation données** : alignement observations/simulations complexe
3. **Validation** : comment prouver que les prédictions sont bonnes ?
4. **Expertise requise** : cosmologie computationnelle

---

## Variante simplifiée possible

### "Structure Density Estimator" (MVP)

Au lieu de prédire les zones inconnues, **visualiser** les structures connues de façon innovante :

- Interpolation simple entre points connus
- Carte de densité 2D/3D interactive
- Overlay matière visible vs matière noire (si données disponibles)

**Faisabilité** : Moyenne (plus réaliste mais moins innovant)

---

## Concurrence / État de l'art

| Projet existant | Description |
|-----------------|-------------|
| BORG (Bayesian Origin Reconstruction) | Reconstruction champ de densité |
| CosmicFlows | Cartographie mouvements galaxies |
| Simulations Illustris | Prédictions basées simulations |

Ces projets sont le fruit de **décennies de recherche** avec des équipes dédiées.

---

## Valeur scientifique potentielle

- **Planification missions** : prioriser zones à observer
- **Tests cosmologiques** : confronter prédictions aux observations
- **Matière noire** : contraindre sa distribution à grande échelle

---

## Questions ouvertes

- [ ] Peut-on simplifier suffisamment pour 24h ?
- [ ] Existe-t-il des modèles pré-entraînés utilisables ?
- [ ] Comment présenter des résultats partiels de façon convaincante ?

---

## Recommandation

> **Ce concept est trop ambitieux pour un hackathon de 24h.**
>
> Recommandation : le garder comme "vision long terme" et partir sur Concept A ou B pour le hackathon, avec possibilité d'évoquer cette direction dans la roadmap.

---

## Prochaines étapes (si poursuivi)

1. [ ] Explorer les datasets Illustris-TNG disponibles
2. [ ] Chercher des modèles pré-entraînés en cosmologie
3. [ ] Définir une version ultra-simplifiée démontrable

---

## Ressources

- [Illustris-TNG Data Access](https://www.tng-project.org/data/)
- [BORG Algorithm](https://arxiv.org/abs/1305.4642)
- [CosmicFlows Project](https://www.ip2i.in2p3.fr/projet/cosmicflows/)
- [Graph Neural Networks for Cosmology](https://arxiv.org/abs/2012.00900)
