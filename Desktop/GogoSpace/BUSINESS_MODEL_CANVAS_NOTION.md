# Business Model Canvas - Cosmic Query Agent

> **ActInSpace Hackathon 2025**
> Outil d'analyse astronomique multi-catalogues avec evaluation des risques de lancement satellite

---

## Vue d'Ensemble

**COSMIC QUERY AGENT** - Space Intelligence Platform for Launch Operations

| Module 1: Cosmic Queries | Module 2: Launch Risk Assessment |
| ------------------------ | -------------------------------- |
| Cross-catalog analysis | Collision probability |
| Anomaly detection AI | Success prediction |
| Multi-source correlation | Optimal launch windows |

---

## 1. Key Partners (Partenaires Cles)

### Agences Spatiales

| Partenaire | Role | Valeur Apportee |
| ---------- | ---- | --------------- |
| **ESA** | Fournisseur de donnees Gaia | Catalogue DR3, 1.8 milliards de sources |
| **CNES** | Partenaire institutionnel | Expertise mission, reseau spatial francais |
| **NASA** | Donnees complementaires | Catalogues SDSS, donnees orbitales |
| **NOAA/18 SDS** | Surveillance spatiale | Donnees conjonction officielles |

### Fournisseurs de Donnees

| Partenaire | Type de Donnees | Acces |
| ---------- | --------------- | ----- |
| **Space-Track.org** | TLE, debris, catalogue complet | API gratuite (compte requis) |
| **Celestrak** | TLE satellites actifs | API publique |
| **CDS Strasbourg** | VizieR (Gaia, 2MASS, SDSS) | API ouverte |
| **SIMBAD** | Identification objets | API ouverte |

### Operateurs de Lancement (Clients Strategiques)

| Operateur | Interet | Potentiel |
| --------- | ------- | --------- |
| **ArianeGroup** | Optimisation Ariane 6/Vega-C | Partenaire premium |
| **SpaceX** | Volume de lancements eleve | Licence enterprise |
| **RocketLab** | Lancements frequents LEO | SaaS subscription |
| **Rocket Factory Augsburg** | Nouveau entrant europeen | Early adopter |

### Partenaires Technologiques

- **LM Studio / OpenAI** : Infrastructure LLM pour interpretation
- **Cesium** : Visualisation 3D globe
- **Streamlit** : Framework UI rapid prototyping

---

## 2. Key Activities (Activites Principales)

### Cycle de Developpement

1. **Ingestion Donnees** : VizieR, Space-Track, Celestrak
2. **Cross-matching** : Correlation multi-catalogues
3. **Detection Anomalies** : Algorithmes statistiques (sigma)
4. **Evaluation Risques** : Modele de collision probabiliste
5. **Interpretation IA** : LLM pour analyse contextuelle
6. **Visualisation** : Aladin Lite, Cesium 3D

### Activites par Module

**Module Cosmic Queries :**
- Maintenance des connecteurs API (VizieR, SIMBAD)
- Amelioration algorithmes de detection d'anomalies
- Entrainement/fine-tuning prompts LLM
- Mise a jour des transformations photometriques

**Module Launch Risk :**
- Mise a jour quotidienne du catalogue spatial
- Calibration des modeles de risque
- Validation avec donnees historiques de conjonction
- Generation de rapports automatises

### Operations

| Activite | Frequence | Criticite |
| -------- | --------- | --------- |
| Sync Space-Track | Toutes les heures | Haute |
| Sync Celestrak | Toutes les 6h | Moyenne |
| Backup donnees | Quotidien | Haute |
| Monitoring API | Temps reel | Critique |

---

## 3. Key Resources (Ressources Cles)

### Donnees

| Source | Volume | Mise a Jour | Cout |
| ------ | ------ | ----------- | ---- |
| Gaia DR3 | 1.8B sources | Statique (DR4 en 2026) | Gratuit |
| 2MASS | 470M sources | Statique | Gratuit |
| SDSS DR16 | 1B+ sources | Annuel | Gratuit |
| Space-Track | 50,000+ objets | Temps reel | Gratuit |
| Celestrak | 10,000+ TLE | Quotidien | Gratuit |

### Stack Technique

| Couche | Technologies |
| ------ | ------------ |
| Frontend | Streamlit (Python) |
| Backend | Python 3.11+ |
| LLM | LM Studio local / OpenAI API |
| Propagation | SGP4 / Skyfield |
| Viz 2D | Aladin Lite v3, Plotly |
| Viz 3D | CesiumJS |
| Data | Pandas, Astropy, Astroquery |

> 100% Open Source (sauf LLM API) - Deployable on-premise ou cloud - API REST disponible

### Performance

- Query cross-match : < 5 secondes
- Risk assessment : < 30 secondes
- Globe 3D : 10,000+ objets temps reel

### Expertise Humaine

| Competence | Niveau Requis | Application |
| ---------- | ------------- | ----------- |
| Astrophysique | Expert | Interpretation anomalies |
| Mecanique orbitale | Intermediaire | Propagation, risques |
| Data Science | Expert | Algorithmes detection |
| DevOps | Intermediaire | Deploiement, scaling |

### Propriete Intellectuelle

- Algorithmes de scoring de risque proprietaires
- Modeles de correlation cross-catalogue
- Prompts LLM optimises pour astronomie
- UX/UI specialisee operations spatiales

---

## 4. Value Propositions (Propositions de Valeur)

### Pour les Chercheurs / Astronomes

**"Detectez les anomalies que les autres manquent"**

- Cross-matching automatique 3 catalogues
- Detection anomalies photometriques/astrometriques
- Interpretation IA des resultats
- Export compatible VO (Virtual Observatory)
- Gain de temps : heures → minutes

**Benefices quantifies :**
- Reduction 90% du temps de cross-matching manuel
- Detection de 15-20% d'anomalies supplementaires
- Interpretation contextuelle instantanee

### Pour les Agences Spatiales (ESA, CNES, NASA)

**"Intelligence spatiale unifiee"**

- Vue consolidee debris + satellites
- Evaluation risques standardisee
- Rapports automatises pour missions
- Integration donnees multi-sources
- Conformite Space Sustainability

### Pour les Operateurs de Lancement

**"Lancez en confiance, optimisez vos fenetres"**

- Score de risque 0-100 instantane
- Probabilite de succes calculee
- Fenetres de lancement optimales
- Alertes conjonction en temps reel
- Rapports exportables pour autorites

**ROI pour operateurs :**
- Reduction des reports de lancement
- Optimisation assurance (primes basees sur risque)
- Conformite reglementaire simplifiee

### Matrice de Valeur par Segment

| Proposition | Chercheurs | Agences | Operateurs |
| ----------- | ---------- | ------- | ---------- |
| Cross-matching AI | ★★★ | ★★ | ★ |
| Detection anomalies | ★★★ | ★★ | ★ |
| Evaluation risques | ★ | ★★★ | ★★★ |
| Visualisation 3D | ★★ | ★★★ | ★★★ |
| Rapports automatises | ★★ | ★★★ | ★★★ |
| API Integration | ★ | ★★ | ★★★ |

---

## 5. Customer Relationships (Relations Client)

### Modeles de Relation par Segment

| Segment | Type de Relation | Canaux | Support |
| ------- | ---------------- | ------ | ------- |
| Chercheurs | Self-service | Web app, docs | Community forum |
| Universites | Self-service + onboarding | Web app, API | Email, workshops |
| Agences | Dedicated support | API, custom deploy | Account manager |
| Operateurs | Strategic partnership | API, on-premise | 24/7 hotline |

### Parcours Client (Funnel)

1. **DECOUVERTE** : Demo en ligne, hackathon, publications
2. **ESSAI** : Free tier (100 requetes/mois)
3. **ADOPTION** : Subscription Pro
4. **EXPANSION** : API integration, volumes
5. **ADVOCACY** : Co-publication, temoignages

### Engagement et Retention

**Chercheurs :**
- Newsletter mensuelle (nouvelles anomalies detectees)
- Webinaires techniques trimestriels
- Co-publications scientifiques

**Operateurs :**
- Revue trimestrielle de performance
- Alertes proactives (nouveaux debris)
- Roadmap produit co-construite

---

## 6. Channels (Canaux de Distribution)

### Canaux Directs

| Canal | Cible | Conversion |
| ----- | ----- | ---------- |
| **Web App SaaS** | Tous segments | Self-signup |
| **API REST** | Developpeurs, integration | Documentation |
| **On-Premise** | Agences, defense | Vente directe |

### Canaux Indirects

| Canal | Partenaire | Modele |
| ----- | ---------- | ------ |
| Marketplaces cloud | AWS, Azure, GCP | Revenue share |
| Integrations | Satellite tool vendors | API licensing |
| Revendeurs | Consultants aerospace | Commission |

### Strategie Go-to-Market

- **Phase 1 (0-6 mois)** : Hackathon + Beta chercheurs
- **Phase 2 (6-12 mois)** : SaaS public + premiers operateurs
- **Phase 3 (12-24 mois)** : API enterprise + contrats agences
- **Phase 4 (24+ mois)** : Marketplace + ecosysteme partenaires

### Presence Digitale

- **Site web** : cosmicquery.space (a creer)
- **Documentation** : docs.cosmicquery.space
- **API Portal** : api.cosmicquery.space
- **GitHub** : Open-source core algorithms
- **LinkedIn** : Thought leadership aerospace

---

## 7. Customer Segments (Segments de Clientele)

### Segmentation Primaire

| Segment | Exemples | Strategie |
| ------- | -------- | --------- |
| **Chercheurs** (Volume) | Astronomes, Universites, Observatoires, PhD students | Freemium |
| **Agences** (Prestige) | ESA, CNES, NASA, JAXA, ISRO, ASI | Contrats institutionnels |
| **Operateurs** (Revenue) | ArianeGroup, SpaceX, RocketLab, Rocket Factory Augsburg, Relativity Space, Firefly Aerospace | Enterprise licensing |

### Profil : Chercheurs / Astronomes

| Attribut | Detail |
| -------- | ------ |
| Taille marche | 50,000+ astronomes mondiaux |
| Budget | Limite (grants) |
| Decision | Individuelle |
| Besoin principal | Decouverte, publication |
| Pain point | Temps de cross-matching |
| Willingness to pay | 0-50 EUR/mois |

### Profil : Agences Spatiales

| Attribut | Detail |
| -------- | ------ |
| Taille marche | ~70 agences nationales |
| Budget | Eleve (institutionnel) |
| Decision | Procurement long |
| Besoin principal | Surveillance, missions |
| Pain point | Integration donnees |
| Willingness to pay | 50k-500k EUR/an |

### Profil : Operateurs de Lancement

| Attribut | Detail |
| -------- | ------ |
| Taille marche | ~50 operateurs actifs |
| Budget | Commercial |
| Decision | ROI-driven |
| Besoin principal | Risk mitigation |
| Pain point | Retards/reports |
| Willingness to pay | 100k-1M EUR/an |

### Priorisation (Matrice Attractivite)

| Segment | Accessibilite | Rentabilite | Priorite |
| ------- | ------------- | ----------- | -------- |
| Chercheurs | Haute | Basse | P2 (volume) |
| Agences | Moyenne | Haute | P2 (reference) |
| Operateurs | Moyenne | Tres haute | **P1 (revenue)** |

---

## 8. Cost Structure (Structure de Couts)

### Couts Fixes Mensuels

| Poste | Cout Mensuel | Cout Annuel | Notes |
| ----- | ------------ | ----------- | ----- |
| Hebergement cloud | 500 EUR | 6,000 EUR | Scalable |
| Domaines/SSL | 10 EUR | 120 EUR | - |
| LLM API (OpenAI) | 200 EUR | 2,400 EUR | Si non-local |
| Outils dev | 100 EUR | 1,200 EUR | GitHub, monitoring |
| **Total Fixe** | **810 EUR** | **9,720 EUR** | - |

### Couts Variables

| Poste | Cout Unitaire | Volume Estime | Cout Mensuel |
| ----- | ------------- | ------------- | ------------ |
| API calls VizieR | Gratuit | Illimite | 0 EUR |
| API Space-Track | Gratuit | Illimite | 0 EUR |
| Compute (queries) | 0.01 EUR/req | 10,000 req | 100 EUR |
| Stockage data | 0.02 EUR/GB | 100 GB | 2 EUR |
| **Total Variable** | - | - | **~102 EUR** |

### Couts de Developpement (Phase Initiale)

| Poste | Effort | Cout Estime |
| ----- | ------ | ----------- |
| MVP (Hackathon) | 48h | 0 EUR (hackathon) |
| V1.0 Production | 3 mois | 15,000 EUR |
| V2.0 Enterprise | 6 mois | 50,000 EUR |
| Maintenance annuelle | Continu | 20,000 EUR/an |

### Repartition des Couts (% du CA cible)

| Poste | Pourcentage |
| ----- | ----------- |
| Infrastructure cloud | 20% |
| Developpement/maintenance | 40% |
| Commercial/Marketing | 20% |
| Support client | 10% |
| Admin/Legal | 10% |

---

## 9. Revenue Streams (Sources de Revenus)

### Modele de Pricing

**Tier 1 : FREE** (Chercheurs individuels)
- Cosmic Queries : 100/mois
- Anomaly detection : Basic
- Launch Risk : Demo only
- Support : Community
- **Prix : 0 EUR**

**Tier 2 : PRO** (Equipes recherche)
- Cosmic Queries : 5,000/mois
- Anomaly detection : Full
- Launch Risk : 10 assessments/mois
- Support : Email
- API Access : Read-only
- **Prix : 49 EUR/mois**

**Tier 3 : ENTERPRISE** (Operateurs)
- Cosmic Queries : Illimite
- Anomaly detection : Full + custom
- Launch Risk : Illimite
- Support : 24/7 dedicated
- API Access : Full + webhooks
- On-premise option : Disponible
- SLA : 99.9% uptime
- **Prix : Sur devis (5k-50k EUR/mois)**

### Projections de Revenus

| Annee | Free Users | Pro | Enterprise | ARR |
| ----- | ---------- | --- | ---------- | --- |
| Y1 | 500 | 20 | 1 | 72k EUR |
| Y2 | 2,000 | 100 | 5 | 360k EUR |
| Y3 | 5,000 | 300 | 15 | 1.2M EUR |
| Y5 | 10,000 | 500 | 30 | 3M EUR |

### Sources de Revenus Additionnelles

| Source | Modele | Potentiel |
| ------ | ------ | --------- |
| Consulting | Jour/homme (1,500 EUR) | 50k EUR/an |
| Formation | Sessions (5k EUR) | 30k EUR/an |
| Data licensing | Per-dataset | 20k EUR/an |
| White-label | License annuelle | 100k EUR/an |
| Grants recherche | H2020, ESA BIC | 200k EUR (one-time) |

### Metriques Cles

| KPI | Cible Y1 | Cible Y3 |
| --- | -------- | -------- |
| MRR | 6k EUR | 100k EUR |
| Churn rate | < 5% | < 3% |
| CAC | 500 EUR | 1,000 EUR |
| LTV | 2,000 EUR | 10,000 EUR |
| LTV:CAC | 4:1 | 10:1 |

---

## Resume Executif

### Probleme

- Cross-matching manuel chronophage
- Risques lancement non quantifies
- Donnees fragmentees entre sources

### Solution

- AI-powered analysis
- Scoring automatise
- Fenetres optimales
- Vue unifiee

### Marche

- **TAM** : 500M EUR (space data)
- **SAM** : 50M EUR (launch ops)
- **SOM** : 5M EUR (Y3)

### Avantage Competitif

- Seul outil cross-catalog + risk
- LLM interpretation
- Interface unifiee

### Modele Economique

- SaaS freemium
- Enterprise licensing
- Consulting

### Traction

- Hackathon ActInSpace 2025
- MVP fonctionnel
- 3 modules integres

---

## Annexes

### A. Competitive Landscape

| Concurrent | Forces | Faiblesses | Positionnement |
| ---------- | ------ | ---------- | -------------- |
| AGI (ESA) | Officiel, complet | Lourd, pas temps reel | Institutionnel |
| LeoLabs | Tracking temps reel | Pas d'astronomie | Tracking only |
| ExoAnalytic | Imagerie optique | Cher, US-only | Defense |
| Slingshot | SSA moderne | Pas de cross-catalog | Operators |
| **Cosmic Query** | **Unifie, AI, accessible** | **Nouveau** | **All-in-one** |

### B. Roadmap Produit

| Trimestre | Milestone |
| --------- | --------- |
| Q1 2025 | MVP Hackathon |
| Q2 2025 | Beta publique |
| Q3 2025 | V1.0 + API |
| Q4 2025 | Premier client enterprise |
| Q2 2026 | Integration Gaia DR4 |
| Q4 2026 | Certification ESA |

### C. Equipe Requise (Cible)

| Role | FTE | Priorite |
| ---- | --- | -------- |
| CTO / Lead Dev | 1 | P1 |
| Data Scientist | 1 | P1 |
| DevOps | 0.5 | P2 |
| Sales Enterprise | 1 | P2 |
| Customer Success | 0.5 | P3 |

---

*Document genere pour ActInSpace 2025*
*Version 1.0 - Janvier 2026*
