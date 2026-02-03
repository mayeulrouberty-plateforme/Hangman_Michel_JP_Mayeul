# Concept B : Anomaly Hunter

> **Statut** : En exploration
> **Dernière mise à jour** : 2025-01-26
> **Priorité** : Moyenne (ambitieux pour 24h)

---

## Résumé

Un système de détection automatique d'anomalies dans les données astronomiques publiques, identifiant les objets ou régions qui dévient des modèles attendus — potentiels candidats pour de nouvelles découvertes (matière noire, objets exotiques, erreurs de catalogage).

---

## Problème adressé

- **Volume massif** : Gaia DR3 contient ~1.8 milliard d'objets
- **Anomalies noyées** : les cas intéressants sont perdus dans le bruit
- **Biais humain** : on trouve ce qu'on cherche, pas ce qu'on ne connaît pas
- **Incohérences inter-catalogues** : peuvent révéler des phénomènes physiques réels

---

## Solution proposée

### Types d'anomalies ciblées

1. **Anomalies statistiques** : objets hors distribution normale
   - Magnitudes incohérentes
   - Mouvements propres aberrants
   - Couleurs impossibles

2. **Incohérences inter-catalogues** :
   - Objet présent dans Gaia mais absent de SDSS (ou inverse)
   - Propriétés contradictoires entre sources
   - Décalages positionnels significatifs

3. **Candidats matière noire** :
   - Effets de lentille gravitationnelle sans source visible
   - Anomalies dans les courbes de rotation (données complémentaires)

---

## Architecture technique (ébauche)

```
┌─────────────────────────────────────┐
│         Pipeline de détection        │
└─────────────────┬───────────────────┘
                  │
    ┌─────────────┼─────────────┐
    ▼             ▼             ▼
┌───────┐   ┌───────────┐   ┌───────────┐
│ Stats │   │ ML-based  │   │  Cross-   │
│Outlier│   │ Anomaly   │   │  Match    │
│Detect │   │ Detection │   │ Conflicts │
└───┬───┘   └─────┬─────┘   └─────┬─────┘
    │             │               │
    └─────────────┼───────────────┘
                  ▼
         ┌───────────────┐
         │   Scoring &   │
         │   Ranking     │
         └───────┬───────┘
                 ▼
         ┌───────────────┐
         │  Interface    │
         │  exploration  │
         └───────────────┘
```

---

## Méthodes de détection envisagées

| Méthode | Application | Complexité |
|---------|-------------|------------|
| Isolation Forest | Outliers multidimensionnels | Basse |
| Autoencoders | Anomalies dans les spectres/images | Haute |
| DBSCAN | Clusters et points isolés | Moyenne |
| Z-score multi-varié | Déviations statistiques simples | Basse |
| Cross-match delta | Incohérences positionnelles | Basse |

---

## Technologies envisagées

| Composant | Options |
|-----------|---------|
| ML Framework | scikit-learn, PyTorch |
| Traitement données | pandas, Dask (si volume) |
| Visualisation | Plotly, Bokeh (interactif) |
| APIs astronomiques | astroquery |
| Interface | Streamlit |

---

## Faisabilité 24h

| Aspect | Évaluation |
|--------|------------|
| Complexité technique | Haute |
| Données disponibles | Oui |
| Prototype réalisable | Partiel |
| Démo convaincante | Possible si bien scopée |

### Risques
- Volume de données peut nécessiter prétraitement lourd
- Faux positifs nombreux sans fine-tuning
- Interprétation scientifique des résultats

### MVP réaliste pour le hackathon
- [ ] Subset de données (1 région du ciel limitée)
- [ ] 1-2 méthodes de détection (Isolation Forest + cross-match)
- [ ] Interface de visualisation des anomalies détectées
- [ ] Export liste de candidats

---

## Concurrence / État de l'art

| Projet existant | Notre différenciation |
|-----------------|----------------------|
| SNAD (anomaly detection) | Focus transients, pas multi-catalogue |
| Zooniverse | Crowdsourcing humain, pas automatique |
| ALeRCE | Alertes temps réel, pas exploration |

**Notre angle** : Détection d'incohérences ENTRE catalogues comme signal scientifique

---

## Valeur scientifique potentielle

- **Découverte** : possibilité de trouver des objets jamais catalogués correctement
- **Qualité des données** : identification d'erreurs dans les catalogues
- **Matière noire** : candidats pour études de lentilles gravitationnelles

---

## Questions ouvertes

- [ ] Quelle région du ciel pour la démo ?
- [ ] Comment valider qu'une anomalie est "intéressante" vs erreur ?
- [ ] Faut-il un astrophysicien dans la boucle pour interpréter ?
- [ ] Comment présenter les résultats de façon compréhensible ?

---

## Prochaines étapes

1. [ ] Identifier un dataset subset téléchargeable (ex: 1 tuile SDSS)
2. [ ] Tester Isolation Forest sur données Gaia
3. [ ] Implémenter cross-match Gaia vs SDSS et mesurer deltas
4. [ ] Définir un score d'anomalie composite

---

## Ressources

- [Gaia DR3 known issues](https://www.cosmos.esa.int/web/gaia/dr3-known-issues)
- [SNAD project](https://snad.space/)
- [Isolation Forest paper](https://cs.nju.edu.cn/zhouzh/zhouzh.files/publication/icdm08b.pdf)
- [astroML - Machine Learning for Astronomy](https://www.astroml.org/)
