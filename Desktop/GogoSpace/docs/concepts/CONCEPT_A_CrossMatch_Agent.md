# Concept A : Cross-Match Agent

> **Statut** : En exploration
> **Dernière mise à jour** : 2025-01-26
> **Priorité** : Haute (recommandé pour 24h)

---

## Résumé

Un agent IA conversationnel qui agrège automatiquement les données de multiples catalogues astronomiques pour une région ou un objet donné, et génère un rapport unifié.

---

## Problème adressé

Les chercheurs en astrophysique font face à :
- **Fragmentation des données** : dizaines de catalogues (Gaia, SDSS, 2MASS, WISE, DES, etc.)
- **Formats hétérogènes** : systèmes de coordonnées variés, unités différentes
- **Cross-match manuel** : processus fastidieux et source d'erreurs
- **Temps perdu** : heures passées à consolider des données avant l'analyse

---

## Solution proposée

### Fonctionnalités principales

1. **Interface conversationnelle** : requêtes en langage naturel
   - "Que sait-on de la région autour de RA=180, Dec=+45 dans un rayon de 1 degré ?"
   - "Donne-moi toutes les infos sur l'étoile HD 12345"

2. **Agrégation multi-sources** : interrogation simultanée de :
   - Gaia DR3
   - SDSS DR17
   - 2MASS
   - WISE
   - VizieR (méta-catalogue)

3. **Cross-match automatique** : alignement des sources entre catalogues

4. **Rapport synthétique** : génération d'un document unifié avec :
   - Tableau consolidé des propriétés
   - Visualisations (diagramme HR, carte du ciel)
   - Références croisées

---

## Architecture technique (ébauche)

```
┌─────────────────┐
│  Interface NL   │  (Streamlit / Gradio)
└────────┬────────┘
         │
┌────────▼────────┐
│   Agent LLM     │  (GPT-4 / Claude / Local)
│  + Tool Calls   │
└────────┬────────┘
         │
┌────────▼────────┐
│  Orchestrateur  │
│   de requêtes   │
└────────┬────────┘
         │
    ┌────┴────┬─────────┬─────────┐
    ▼         ▼         ▼         ▼
┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐
│ Gaia  │ │ SDSS  │ │ 2MASS │ │ VizieR│
│  API  │ │  API  │ │  API  │ │  API  │
└───────┘ └───────┘ └───────┘ └───────┘
```

---

## Technologies envisagées

| Composant | Options |
|-----------|---------|
| LLM | OpenAI GPT-4, Claude API, Mistral, LLaMA local |
| Framework agent | LangChain, CrewAI, AutoGen |
| APIs astronomiques | astroquery (Python), TAP services |
| Interface | Streamlit, Gradio |
| Base de données | PostgreSQL + pgvector (cache) |

---

## Faisabilité 24h

| Aspect | Évaluation |
|--------|------------|
| Complexité technique | Moyenne |
| Données disponibles | Oui (APIs publiques) |
| Prototype réalisable | Oui |
| Démo convaincante | Oui |

### MVP réaliste pour le hackathon
- [ ] 2-3 catalogues intégrés (Gaia + SDSS minimum)
- [ ] Interface conversationnelle basique
- [ ] Cross-match sur coordonnées
- [ ] Export rapport simple

---

## Concurrence / État de l'art

| Projet existant | Différence avec notre concept |
|-----------------|------------------------------|
| AstroAgent (Harvard) | Focus littérature, 1 seul catalogue (SIMBAD) |
| StarWhisper | Orienté automatisation télescope |
| Gaia Sky Assistant | Documentation uniquement |

**Notre différenciation** : Multi-catalogues + synthèse intelligente + langage naturel

---

## Questions ouvertes

- [ ] Quelle granularité de cross-match ? (position seule vs propriétés)
- [ ] Comment gérer les ambiguïtés (plusieurs matches possibles) ?
- [ ] Faut-il un cache local pour les performances ?
- [ ] Quel format de sortie privilégier ? (PDF, JSON, interactif)

---

## Prochaines étapes

1. [ ] Valider l'accès aux APIs (Gaia TAP, SDSS CasJobs)
2. [ ] Prototyper une requête simple avec astroquery
3. [ ] Tester l'intégration LLM → génération ADQL
4. [ ] Définir le format du rapport de sortie

---

## Ressources

- [astroquery documentation](https://astroquery.readthedocs.io/)
- [Gaia TAP service](https://gea.esac.esa.int/archive/)
- [SDSS SkyServer](https://skyserver.sdss.org/)
- [VizieR TAP](https://vizier.cds.unistra.fr/viz-bin/VizieR)
