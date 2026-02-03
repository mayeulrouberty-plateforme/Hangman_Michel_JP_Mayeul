# Index des Concepts - ActInSpace 2025

> **Projet** : Cartographie cosmologique assistée par IA
> **Hackathon** : ActInSpace (24h)
> **Équipe** : Dev + Data Science
> **Cible** : Chercheurs / Agences spatiales

---

## Vue d'ensemble

| Concept | Description | Priorité | Faisabilité 24h |
|---------|-------------|----------|-----------------|
| [**A - Cross-Match Agent**](./CONCEPT_A_CrossMatch_Agent.md) | Agent conversationnel multi-catalogues | Haute | Oui |
| [**B - Anomaly Hunter**](./CONCEPT_B_Anomaly_Hunter.md) | Détection d'anomalies inter-catalogues | Moyenne | Partielle |
| [**C - Structure Predictor**](./CONCEPT_C_Structure_Predictor.md) | Prédiction structures cosmologiques | Basse | Non |

---

## Recommandation actuelle

### Pour le hackathon (24h)

**Option recommandée** : Concept A avec éléments du Concept B

> **"Cosmic Query Agent"** : Un agent qui interroge plusieurs catalogues, détecte les incohérences entre eux, et les signale comme potentiels candidats scientifiques.

Cette approche combine :
- Faisabilité du Concept A
- Innovation du Concept B (détection d'incohérences)
- Valeur scientifique réelle

### Roadmap long terme

```
24h Hackathon          6 mois              1-2 ans
     │                   │                    │
     ▼                   ▼                    ▼
┌─────────┐       ┌─────────────┐      ┌─────────────┐
│Concept A│  ───► │ A + B       │ ───► │ A + B + C   │
│  MVP    │       │ intégrés    │      │ complet     │
└─────────┘       └─────────────┘      └─────────────┘
```

---

## État de l'art - Résumé

### Ce qui existe
- AstroAgent (Harvard) - littérature + 1 catalogue
- StarWhisper - automatisation télescopes
- NASA Science Discovery Engine - classification contenu

### Notre différenciation
- **Multi-catalogues** en une requête
- **Détection d'incohérences** comme feature
- **Langage naturel** pour requêtes complexes

---

## Prochaines décisions à prendre

- [ ] **Choix final du concept** pour le hackathon
- [ ] **Stack technique** : LLM à utiliser (API vs local)
- [ ] **Scope MVP** : combien de catalogues minimum
- [ ] **Format livrable** : démo live, vidéo, rapport ?

---

## Structure du dossier

```
docs/
└── concepts/
    ├── INDEX.md                                        (ce fichier)
    ├── CONCEPT_A_CrossMatch_Agent.md                   (vue d'ensemble)
    ├── CONCEPT_A_Technical_Deep_Dive.md                (architecture + code)
    ├── CONCEPT_A_Cost_Estimation.md                    (coûts déploiement)
    ├── CONCEPT_A_Differentiator_Inconsistency_Detection.md  (angle unique)
    ├── CONCEPT_B_Anomaly_Hunter.md
    └── CONCEPT_C_Structure_Predictor.md
```

---

## Journal des décisions

| Date | Décision | Justification |
|------|----------|---------------|
| 2025-01-26 | Création documentation | Structurer le brainstorming |
| 2025-01-26 | Focus sur Concept A | Meilleure faisabilité 24h |
| 2025-01-26 | Angle différenciant validé | Détection incohérences n'existe pas publiquement |
| 2025-01-26 | Estimation coûts complétée | Demo < $1, Production ~$850/mois |
| 2025-01-26 | **MVP développé** | Prototype fonctionnel dans `src/` |

---

## Contacts & Ressources

- **ActInSpace** : [actinspace.org](https://actinspace.org/)
- **ESA Open Data** : [cosmos.esa.int](https://www.cosmos.esa.int/)
- **NASA Open Data** : [data.nasa.gov](https://data.nasa.gov/)
