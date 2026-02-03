# Roadmap - Monitoring des Débris Orbitaux

## Objectif

Ajouter un onglet **"Space Traffic"** à l'application Cosmic Query Agent pour le suivi en temps réel des satellites et débris spatiaux, avec détection de conjonctions et aide à la décision.

---

## Phase 1 - MVP Satellites (Priorité Critique)

### 1.1 Infrastructure de base

| Module | Fichier | Fonctionnalités |
|--------|---------|-----------------|
| Requêtes TLE | `modules/satellites/satellite_queries.py` | Téléchargement TLE (Space-Track, CelesTrak), propagation SGP4 |
| Classification | `modules/satellites/debris_classifier.py` | Classification LEO/MEO/GEO, type d'objet (actif/débris/rocket body) |
| Visualisation | `modules/visualization/cesium_viewer.py` | Globe 3D CesiumJS, trajectoires orbitales |

**Dépendances Python à ajouter :**
```txt
skyfield>=1.46
sgp4>=2.23
spacetrack>=1.2.0
satellite-tle>=0.15.1
```

**Livrables :**
- [ ] Connexion API Space-Track (compte gratuit requis)
- [ ] Affichage de 10 000+ objets sur globe 3D
- [ ] Filtres par type (satellite actif, débris, étage de fusée)
- [ ] Recherche par NORAD ID ou nom

### 1.2 Détection de conjonctions

| Module | Fichier | Fonctionnalités |
|--------|---------|-----------------|
| Analyseur | `modules/satellites/conjunction_analyzer.py` | Détection TCA (Time of Closest Approach), distance minimale |

**Livrables :**
- [ ] Scan automatique des approches < 10 km
- [ ] Liste triée par criticité (distance, temps restant)
- [ ] Visualisation 3D de la trajectoire de conjonction

---

## Phase 2 - Intelligence (Priorité Haute)

### 2.1 Système d'alertes

| Module | Fichier | Fonctionnalités |
|--------|---------|-----------------|
| Alertes UI | `modules/ui/alerts.py` | Dashboard alertes, niveaux critique/warning/info |
| Webhooks | `modules/api/webhooks.py` | Intégration Slack, Teams, PagerDuty |

**Livrables :**
- [ ] Dashboard temps réel avec compteurs
- [ ] Historique des alertes avec timeline
- [ ] Notifications push configurables

### 2.2 Calcul de probabilité de collision (Pc)

| Algorithme | Description | Référence |
|------------|-------------|-----------|
| COLA | Collision Avoidance standard ESA | [ESA SDC5](https://conference.sdo.esoc.esa.int/proceedings/sdc5/paper/68) |
| Covariance | Ellipsoïde d'incertitude 3D | [ACC 2002](http://congres.cran.univ-lorraine.fr/2002/ACC%202002/pdffiles/papers/298.pdf) |

**Livrables :**
- [ ] Métrique Pc (Probability of Collision) par conjonction
- [ ] Visualisation de l'ellipsoïde d'incertitude dans Cesium
- [ ] Seuils configurables (10⁻⁴ = warning, 10⁻³ = critique)

### 2.3 Générateur de manœuvres d'évitement

| Module | Fichier | Fonctionnalités |
|--------|---------|-----------------|
| Planificateur | `modules/satellites/maneuver_planner.py` | Delta-V minimal, fenêtres optimales |

**Dépendances :**
```txt
poliastro>=0.17  # Mécanique orbitale avancée
```

**Livrables :**
- [ ] Calcul automatique du delta-V minimal
- [ ] Suggestions de fenêtres de manœuvre (économie carburant)
- [ ] Export CCSDS pour upload satellite

### 2.4 Base de données historique

| Module | Fichier | Fonctionnalités |
|--------|---------|-----------------|
| DB Manager | `modules/database/db_manager.py` | SQLite/PostgreSQL, historique conjonctions |
| Modèles | `modules/database/models.py` | SQLAlchemy ORM |

**Dépendances :**
```txt
sqlalchemy>=2.0.0
alembic>=1.13.0
```

**Livrables :**
- [ ] Stockage de toutes les conjonctions détectées
- [ ] Analyse statistique (fréquence, zones à risque)
- [ ] Export CSV/JSON pour analyse externe

---

## Phase 3 - Fonctionnalités Pro (Priorité Moyenne)

### 3.1 Prédiction de rentrée atmosphérique

| Module | Fichier | Fonctionnalités |
|--------|---------|-----------------|
| Prédicteur | `modules/satellites/reentry_predictor.py` | Propagation long-terme, zone d'impact |

**Livrables :**
- [ ] Fenêtre de rentrée (date ± incertitude)
- [ ] Cartographie zone d'impact potentielle
- [ ] Alertes pour objets massifs (> 500 kg)

### 3.2 Module compliance réglementaire

**Standards à vérifier :**
- FCC : désorbitation < 25 ans
- IADC : mitigation guidelines
- ISO 24113 : space debris mitigation

**Livrables :**
- [ ] Checklist automatique pré-lancement
- [ ] Rapport de conformité PDF
- [ ] Calcul durée de vie résiduelle

### 3.3 Agent LLM orbital

| Module | Fichier | Fonctionnalités |
|--------|---------|-----------------|
| Assistant | `modules/ai/orbital_assistant.py` | Interprétation alertes, recommandations |

**Livrables :**
- [ ] Interprétation en langage naturel des alertes
- [ ] Recommandations contextuelles ("Manœuvre conseillée dans 6h")
- [ ] Chatbot expert orbital mechanics

### 3.4 Détection d'anomalies orbitales

Extension de `anomaly_detector.py` existant :

**Livrables :**
- [ ] Détection manœuvres non planifiées
- [ ] Identification débris de fragmentations récentes
- [ ] Score de fiabilité par satellite

---

## Phase 4 - Polish UX (Priorité Basse)

### 4.1 Mode "Mission Control"

- [ ] Dashboard temps réel style NASA
- [ ] Multi-vues : 3D + timeline + alertes + tableaux
- [ ] Thème sombre salles de contrôle
- [ ] Sons d'alerte configurables

### 4.2 Visualisation temporelle

- [ ] Timeline interactive (Gantt)
- [ ] Slider temporel dans Cesium
- [ ] Mode playback (rejouer conjonction passée)
- [ ] Comparaison avant/après manœuvre

### 4.3 Export rapports professionnels

**Dépendances :**
```txt
fpdf2>=2.7.7
jinja2>=3.1.3
```

**Livrables :**
- [ ] Génération PDF avec graphiques
- [ ] Templates personnalisables (agences, opérateurs)
- [ ] Intégration LaTeX pour équations

### 4.4 API REST

| Module | Fichier | Fonctionnalités |
|--------|---------|-----------------|
| API | `modules/api/rest_api.py` | Endpoints RESTful |
| Auth | `modules/api/auth.py` | JWT, rate limiting |

**Dépendances :**
```txt
fastapi>=0.109.0
uvicorn>=0.27.0
pyjwt>=2.8.0
```

---

## Structure de fichiers cible

```
src/
├── app.py                          # + Onglet "Space Traffic"
├── config.py                       # + Config satellites
│
├── modules/
│   ├── satellites/
│   │   ├── satellite_queries.py    # TLE, SGP4
│   │   ├── conjunction_analyzer.py # Pc, TCA
│   │   ├── maneuver_planner.py     # Delta-V
│   │   ├── debris_classifier.py    # LEO/MEO/GEO
│   │   └── reentry_predictor.py    # Rentrée atmo
│   │
│   ├── visualization/
│   │   └── cesium_viewer.py        # Globe 3D
│   │
│   ├── ai/
│   │   └── orbital_assistant.py    # LLM orbital
│   │
│   ├── database/
│   │   ├── db_manager.py
│   │   └── models.py
│   │
│   └── ui/
│       └── alerts.py
│
└── data/
    ├── tle_cache/                  # Cache TLE local
    └── conjunctions.db             # Historique
```

---

## Critères de succès

| Métrique | Objectif |
|----------|----------|
| Précision détection | 100% conjonctions < 1 km, < 5% faux positifs |
| Temps réel | Mise à jour positions toutes les 5 min |
| Scalabilité | 10 000+ objets sans ralentissement |
| Compliance | Rapports conformes CCSDS |
| Autonomie | Alertes critiques 24/7 sans intervention |

---

## Ressources externes

- **Space-Track.org** : API officielle USSPACECOM (compte gratuit)
- **CelesTrak** : TLE publics, données supplémentaires
- **ESA DISCOS** : Base de données objets spatiaux européenne
- **LeoLabs** : Données radar (commercial, si budget)

---

## Estimation temporelle

| Phase | Durée |
|-------|-------|
| Phase 1 - MVP | 2-3 semaines |
| Phase 2 - Intelligence | 3-4 semaines |
| Phase 3 - Pro | 4-6 semaines |
| Phase 4 - Polish | 2-3 semaines |

**Total : 11-16 semaines** pour une plateforme complète de Space Traffic Management.
