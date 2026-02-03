# Presentation ActInSpace 2025 - Cosmic Query Agent

> **Duree totale** : 10 minutes (ajustable)
> **Equipe** : 4 presentateurs
> **Format** : Pitch + Demo

---

## Repartition des Roles

| Presentateur | Role | Slides | Duree |
|--------------|------|--------|-------|
| **P1** | CEO / Vision | 1-3 | 2 min |
| **P2** | CTO / Technique | 4-7 | 3 min |
| **P3** | Product / Demo | 8-10 | 3 min |
| **P4** | Business / Closing | 11-13 | 2 min |

---

## SLIDE 1 : Titre (P1)

### Visuel
```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│              🚀 COSMIC QUERY AGENT                          │
│                                                             │
│     Intelligence Spatiale pour Operations de Lancement      │
│                                                             │
│              ─────────────────────────────                  │
│                   ActInSpace 2025                           │
│                                                             │
│     [Logo ESA]  [Logo CNES]  [Logo ActInSpace]              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Script P1 (30 sec)
> "Bonjour, nous sommes l'equipe [NOM] et nous vous presentons Cosmic Query Agent.
>
> Imaginez : vous etes operateur de lancement. Dans 3 heures, votre fusee doit decoller. Mais parmi les 50 000 objets en orbite, combien menacent votre trajectoire ? Quelle est votre probabilite de succes ?
>
> Aujourd'hui, repondre a ces questions prend des heures. Avec Cosmic Query Agent, ca prend 30 secondes."

---

## SLIDE 2 : Le Probleme (P1)

### Visuel
```
┌─────────────────────────────────────────────────────────────┐
│  LE PROBLEME                                                │
│  ───────────                                                │
│                                                             │
│  🔴 50,000+ objets en orbite (satellites, debris)           │
│                                                             │
│  🔴 Donnees fragmentees entre multiples sources             │
│     - Space-Track (USA)                                     │
│     - Celestrak                                             │
│     - Catalogues astronomiques (Gaia, 2MASS, SDSS)          │
│                                                             │
│  🔴 Pas d'outil unifie pour :                               │
│     - Evaluer les risques de collision                      │
│     - Detecter les anomalies cross-catalogues               │
│     - Optimiser les fenetres de lancement                   │
│                                                             │
│  💰 Cout d'un report de lancement : 500k - 2M EUR           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Script P1 (45 sec)
> "Le probleme est triple.
>
> Premierement, il y a plus de 50 000 objets traces en orbite terrestre. Satellites actifs, debris, etages de fusees abandonnes.
>
> Deuxiemement, les donnees sont fragmentees. Space-Track aux USA, Celestrak, les catalogues astronomiques europeens comme Gaia de l'ESA. Personne n'a une vue unifiee.
>
> Troisiemement, les operateurs de lancement n'ont pas d'outil simple pour evaluer leur risque de collision en temps reel.
>
> Resultat ? Des reports de lancement qui coutent entre 500 000 et 2 millions d'euros. Par lancement."

---

## SLIDE 3 : Notre Solution (P1)

### Visuel
```
┌─────────────────────────────────────────────────────────────┐
│  COSMIC QUERY AGENT                                         │
│  ──────────────────                                         │
│                                                             │
│  ┌─────────────────┐    ┌─────────────────┐                 │
│  │   MODULE 1      │    │   MODULE 2      │                 │
│  │   COSMIC        │    │   LAUNCH RISK   │                 │
│  │   QUERIES       │    │   ASSESSMENT    │                 │
│  │                 │    │                 │                 │
│  │ • Cross-match   │    │ • Score 0-100   │                 │
│  │   3 catalogues  │    │ • Probabilite   │                 │
│  │ • Detection     │    │   de succes     │                 │
│  │   anomalies IA  │    │ • Fenetres      │                 │
│  │ • Visualisation │    │   optimales     │                 │
│  └─────────────────┘    └─────────────────┘                 │
│                    ↓                                        │
│           ┌─────────────────┐                               │
│           │  GLOBE 3D       │                               │
│           │  Temps Reel     │                               │
│           └─────────────────┘                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Script P1 (45 sec)
> "Notre solution : Cosmic Query Agent. Une plateforme qui unifie tout.
>
> Module 1 : Cosmic Queries. On interroge simultanement Gaia, 2MASS et SDSS. On detecte automatiquement les anomalies entre catalogues grace a l'intelligence artificielle.
>
> Module 2 : Launch Risk Assessment. Un score de risque de 0 a 100, une probabilite de succes, et des fenetres de lancement optimales. En 30 secondes.
>
> Le tout visualise sur un globe 3D temps reel avec tous les satellites et debris.
>
> Je laisse la parole a [P2] pour la partie technique."

---

## SLIDE 4 : Architecture Technique (P2)

### Visuel
```
┌─────────────────────────────────────────────────────────────┐
│  ARCHITECTURE                                               │
│  ────────────                                               │
│                                                             │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐                │
│  │  Gaia    │   │  2MASS   │   │  SDSS    │                │
│  │  DR3     │   │          │   │  DR16    │                │
│  │ 1.8B src │   │ 470M src │   │  1B src  │                │
│  └────┬─────┘   └────┬─────┘   └────┬─────┘                │
│       └──────────────┼──────────────┘                       │
│                      ↓                                      │
│            ┌─────────────────┐                              │
│            │   VizieR API    │                              │
│            │  (CDS Strasbourg)│                              │
│            └────────┬────────┘                              │
│                     ↓                                       │
│  ┌─────────────────────────────────────────┐               │
│  │         COSMIC QUERY AGENT              │               │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐   │               │
│  │  │Cross-   │ │Anomaly  │ │ LLM     │   │               │
│  │  │Match    │ │Detector │ │ Agent   │   │               │
│  │  └─────────┘ └─────────┘ └─────────┘   │               │
│  └─────────────────────────────────────────┘               │
│                     ↓                                       │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐                │
│  │Space-    │   │Celestrak │   │ Cesium   │                │
│  │Track.org │   │  TLE     │   │ 3D Globe │                │
│  └──────────┘   └──────────┘   └──────────┘                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Script P2 (45 sec)
> "Cote technique, notre architecture s'appuie sur les meilleures sources de donnees.
>
> En haut, les catalogues astronomiques : Gaia de l'ESA avec 1.8 milliards de sources, 2MASS, SDSS. On y accede via VizieR, l'API du CDS de Strasbourg.
>
> Au centre, notre moteur. Trois composants cles : le cross-matcher qui correle les catalogues, le detecteur d'anomalies base sur des seuils statistiques sigma, et un agent LLM pour interpreter les resultats.
>
> En bas, les donnees orbitales : Space-Track point org pour le catalogue complet incluant les debris, Celestrak pour les TLE, et Cesium pour la visualisation 3D."

---

## SLIDE 5 : Detection d'Anomalies (P2)

### Visuel
```
┌─────────────────────────────────────────────────────────────┐
│  DETECTION D'ANOMALIES - 4 TYPES                            │
│  ───────────────────────────────                            │
│                                                             │
│  🔴 PHOTOMETRIQUE                                           │
│     Magnitude Gaia G ≠ attendue depuis 2MASS/SDSS           │
│     Formule: |G_obs - G_expected| / σ > 3                   │
│                                                             │
│  🟣 ASTROMETRIQUE                                           │
│     Position cross-match > 1 arcsec                         │
│     Possible: mouvement propre eleve                        │
│                                                             │
│  🟠 COULEUR                                                 │
│     BP-RP extreme (< -0.5 ou > 5.0)                         │
│     Etoiles inhabituelles, quasars, artefacts               │
│                                                             │
│  🔵 CROSS-MATCH MANQUANT                                    │
│     Source brillante (G < 16) sans correspondance 2MASS     │
│     Potentiel: transitoire, erreur catalogue                │
│                                                             │
│  ═══════════════════════════════════════════════════════    │
│  Score composite 0-100 base sur sigma et type               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Script P2 (45 sec)
> "Notre detecteur identifie 4 types d'anomalies.
>
> Photometrique : quand la magnitude Gaia ne correspond pas a ce qu'on attend des donnees infrarouges 2MASS ou optiques SDSS.
>
> Astrometrique : quand les positions entre catalogues divergent de plus d'une seconde d'arc.
>
> Couleur : les objets avec des couleurs BP-RP extremes, potentiellement des quasars ou des artefacts.
>
> Et les cross-matchs manquants : une source brillante dans Gaia sans correspondance attendue ailleurs.
>
> Chaque anomalie recoit un score base sur son ecart statistique en sigma. Plus c'est eleve, plus c'est interessant scientifiquement."

---

## SLIDE 6 : Evaluation des Risques de Lancement (P2)

### Visuel
```
┌─────────────────────────────────────────────────────────────┐
│  FORMULE DU SCORE DE RISQUE                                 │
│  ──────────────────────────                                 │
│                                                             │
│  Score Total (0-100) =                                      │
│                                                             │
│    Densite Debris     (0-25 pts)                            │
│    ████████████░░░░░░░░░░░░░░░░░░                           │
│    Volume coquille orbitale + comptage                      │
│                                                             │
│  + Probabilite Collision (0-30 pts)                         │
│    ████████████████░░░░░░░░░░░░░░                           │
│    Distance 3D trajectoire ↔ objets                         │
│                                                             │
│  + Conjonctions       (0-20 pts)                            │
│    ████████████░░░░░░░░░░░░░░░░░░                           │
│    Nombre d'approches < 20 km                               │
│                                                             │
│  + Congestion         (0-15 pts)                            │
│    ██████░░░░░░░░░░░░░░░░░░░░░░░░                           │
│    Objets totaux dans bande                                 │
│                                                             │
│  + Facteur Temporel   (0-10 pts)                            │
│    ████░░░░░░░░░░░░░░░░░░░░░░░░░░                           │
│    Jour vs Nuit                                             │
│                                                             │
│  ═══════════════════════════════════════════════════════    │
│  Probabilite Succes = (100 - Score) × 0.98                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Script P2 (45 sec)
> "Pour l'evaluation des risques, on calcule un score composite de 0 a 100.
>
> 5 facteurs. La densite de debris dans l'orbite cible : on calcule le volume de la coquille orbitale et on compte les objets.
>
> La probabilite de collision : distance 3D entre chaque point de la trajectoire et les objets traces.
>
> Le nombre de conjonctions : combien d'objets passent a moins de 20 kilometres.
>
> La congestion generale de l'orbite. Et un facteur temporel jour/nuit.
>
> La probabilite de succes est l'inverse du risque, ponderee par la fiabilite historique des lanceurs, environ 98%.
>
> Je passe la main a [P3] pour la demonstration."

---

## SLIDE 7 : Stack Technique (P2)

### Visuel
```
┌─────────────────────────────────────────────────────────────┐
│  TECHNOLOGIES                                               │
│  ────────────                                               │
│                                                             │
│  FRONTEND           BACKEND            DATA                 │
│  ─────────          ───────            ────                 │
│  Streamlit          Python 3.11        Pandas               │
│  Plotly             Astropy            NumPy                │
│  Aladin Lite v3     Astroquery         SGP4/Skyfield        │
│  CesiumJS           OpenAI API                              │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  100% Open Source (sauf LLM API)                    │   │
│  │  Deployable on-premise ou cloud                     │   │
│  │  API REST disponible                                │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  PERFORMANCE                                                │
│  ───────────                                                │
│  • Query cross-match : < 5 secondes                         │
│  • Risk assessment : < 30 secondes                          │
│  • Globe 3D : 10,000+ objets temps reel                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Script P2 (30 sec)
> "Cote stack : Streamlit pour le frontend, Python et Astropy pour le backend, Cesium pour le globe 3D.
>
> L'ensemble est open source, deployable on-premise pour les clients sensibles comme la defense, ou en cloud.
>
> Performances : un cross-match en moins de 5 secondes, une evaluation de risque en moins de 30 secondes, et un globe 3D capable d'afficher 10 000 objets en temps reel."

---

## SLIDE 8 : Demo - Cosmic Queries (P3)

### Visuel
```
┌─────────────────────────────────────────────────────────────┐
│  DEMO LIVE : COSMIC QUERIES                                 │
│  ──────────────────────────                                 │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                                                     │   │
│  │     [SCREENSHOT / VIDEO DE L'APPLICATION]           │   │
│  │                                                     │   │
│  │     1. Recherche "M42" (Nebuleuse d'Orion)          │   │
│  │     2. Cross-match Gaia + 2MASS + SDSS              │   │
│  │     3. Detection anomalies automatique              │   │
│  │     4. Visualisation Aladin Lite                    │   │
│  │     5. Interpretation LLM                           │   │
│  │                                                     │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  💡 En LIVE sur http://127.0.0.1:8502                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Script P3 - DEMO LIVE (1 min 30)
> "Passons a la demonstration. J'ouvre l'application.
>
> [OUVRIR L'APP]
>
> Je tape M42, la celebre nebuleuse d'Orion. Je lance la recherche.
>
> [CLIQUER RECHERCHER]
>
> En moins de 5 secondes, on a recupere les donnees de Gaia, 2MASS et SDSS. 200 sources croisees.
>
> [MONTRER L'ONGLET RESULTATS]
>
> Ici, l'onglet Anomalies. Notre algorithme a detecte 70% de sources avec au moins une anomalie. Rouge pour photometrique, violet pour astrometrique.
>
> [MONTRER LA CARTE ALADIN]
>
> Sur la carte Aladin, je peux cliquer sur n'importe quelle source. Un popup apparait avec tous les details : magnitude, couleur, et la liste des anomalies detectees.
>
> [CLIQUER SUR UNE SOURCE]
>
> Et si je veux comprendre, je clique sur Interpreter. Notre LLM analyse l'anomalie et propose des hypotheses scientifiques.
>
> [MONTRER INTERPRETATION LLM]"

---

## SLIDE 9 : Demo - Launch Risk (P3)

### Visuel
```
┌─────────────────────────────────────────────────────────────┐
│  DEMO LIVE : LAUNCH RISK ASSESSMENT                         │
│  ──────────────────────────────────                         │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                                                     │   │
│  │     [SCREENSHOT / VIDEO DU MODULE RISK]             │   │
│  │                                                     │   │
│  │     Site: Kourou (CSG)                              │   │
│  │     Orbite: LEO 400km                               │   │
│  │     Date: [AUJOURD'HUI]                             │   │
│  │                                                     │   │
│  │     → Score de Risque: 23/100 🟢                    │   │
│  │     → Probabilite Succes: 95.4%                     │   │
│  │     → Conjonctions: 3                               │   │
│  │     → Fenetre Optimale: +4h                         │   │
│  │                                                     │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Script P3 - DEMO LIVE (1 min)
> "Maintenant le module d'evaluation des risques. Je passe en mode Space Traffic Management.
>
> [CHANGER DE MODE]
>
> Je selectionne le site de lancement : Kourou, en Guyane francaise. L'orbite cible : LEO 400 kilometres, comme la Station Spatiale.
>
> [SELECTIONNER]
>
> Je clique sur Evaluer le Risque.
>
> [CLIQUER]
>
> En 30 secondes, on a le resultat. Score de risque : 23 sur 100, indicateur vert. Probabilite de succes : 95.4%.
>
> 3 conjonctions detectees, c'est-a-dire 3 objets qui passeront a moins de 20 kilometres de notre trajectoire.
>
> Et le systeme recommande une fenetre optimale 4 heures plus tard pour reduire encore le risque.
>
> [MONTRER LE RAPPORT]
>
> Je peux exporter ce rapport en Markdown pour l'envoyer aux autorites."

---

## SLIDE 10 : Demo - Globe 3D (P3)

### Visuel
```
┌─────────────────────────────────────────────────────────────┐
│  DEMO LIVE : GLOBE 3D TEMPS REEL                            │
│  ───────────────────────────────                            │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                                                     │   │
│  │     [SCREENSHOT CESIUM GLOBE]                       │   │
│  │                                                     │   │
│  │     🟢 Satellites actifs (vert)                     │   │
│  │     🔴 Debris (rouge)                               │   │
│  │     🟠 Corps de fusees (orange)                     │   │
│  │                                                     │   │
│  │     Zoom sur zone de lancement                      │   │
│  │     Rotation interactive                            │   │
│  │     Clic = details objet                            │   │
│  │                                                     │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  📊 Source: Space-Track.org (50,000+ objets)                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Script P3 (30 sec)
> "Enfin, le globe 3D.
>
> [MONTRER LE GLOBE]
>
> Chaque point represente un objet en orbite. Vert pour les satellites actifs, rouge pour les debris, orange pour les corps de fusees abandonnes.
>
> Je peux zoomer sur Kourou, voir exactement ce qui orbite au-dessus de notre site de lancement.
>
> [ZOOMER]
>
> Cliquer sur un objet donne son nom, son numero NORAD, son altitude.
>
> 50 000 objets, mis a jour toutes les heures depuis Space-Track.
>
> Je laisse [P4] conclure sur le business model."

---

## SLIDE 11 : Marche et Clients (P4)

### Visuel
```
┌─────────────────────────────────────────────────────────────┐
│  MARCHE CIBLE                                               │
│  ────────────                                               │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  TAM: 500M EUR     │  SAM: 50M EUR   │  SOM: 5M EUR │   │
│  │  Space Data        │  Launch Ops     │  Y3 Target   │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  SEGMENTS CLIENTS                                           │
│  ────────────────                                           │
│                                                             │
│  👨‍🔬 CHERCHEURS          🏛️ AGENCES          🚀 OPERATEURS   │
│     50,000+ astronomes     ESA, CNES            ArianeGroup   │
│     Universites            NASA, JAXA           SpaceX        │
│     Observatoires          ISRO, ASI            RocketLab     │
│                                                             │
│     Volume client          Reference            Revenue       │
│     Free/49 EUR/mois       50-500k EUR/an       100k-1M EUR/an│
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Script P4 (45 sec)
> "Le marche des donnees spatiales, c'est 500 millions d'euros. Notre segment adressable, les operations de lancement, represente 50 millions. Notre objectif a 3 ans : 5 millions.
>
> Trois segments de clients.
>
> Les chercheurs : 50 000 astronomes dans le monde. Ils generent du volume et de la visibilite. Modele freemium.
>
> Les agences spatiales : ESA, CNES, NASA. Elles apportent la credibilite et des contrats institutionnels de 50 a 500 000 euros par an.
>
> Les operateurs de lancement : ArianeGroup, SpaceX, RocketLab. C'est la ou est le revenu. 100 000 a 1 million par an. Parce qu'un report de lancement coute bien plus cher."

---

## SLIDE 12 : Business Model (P4)

### Visuel
```
┌─────────────────────────────────────────────────────────────┐
│  MODELE ECONOMIQUE                                          │
│  ─────────────────                                          │
│                                                             │
│  ┌──────────────┬──────────────┬──────────────┐            │
│  │    FREE      │     PRO      │  ENTERPRISE  │            │
│  ├──────────────┼──────────────┼──────────────┤            │
│  │  0 EUR       │  49 EUR/mois │  Sur devis   │            │
│  │              │              │  5-50k/mois  │            │
│  ├──────────────┼──────────────┼──────────────┤            │
│  │  100 req/mois│  5000 req    │  Illimite    │            │
│  │  Demo Risk   │  10 assess.  │  Full access │            │
│  │  Community   │  Email       │  24/7 + SLA  │            │
│  └──────────────┴──────────────┴──────────────┘            │
│                                                             │
│  PROJECTIONS                                                │
│  ───────────                                                │
│                                                             │
│  Annee 1: 72k EUR ARR   (500 free, 20 pro, 1 enterprise)   │
│  Annee 3: 1.2M EUR ARR  (5000 free, 300 pro, 15 enterprise)│
│  Annee 5: 3M EUR ARR    (10000 free, 500 pro, 30 enterprise)│
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Script P4 (45 sec)
> "Notre modele est un SaaS freemium en 3 tiers.
>
> Free pour les chercheurs individuels : 100 requetes par mois, demonstration du module risque. Ca cree l'adoption.
>
> Pro a 49 euros par mois pour les equipes de recherche : 5000 requetes, 10 evaluations de risque, support email.
>
> Enterprise sur devis, de 5000 a 50 000 euros par mois : acces illimite, support 24/7, SLA 99.9%, option on-premise.
>
> Nos projections : 72 000 euros de revenus recurrents la premiere annee. 1.2 million a 3 ans. 3 millions a 5 ans avec 30 clients enterprise."

---

## SLIDE 13 : Call to Action (P4)

### Visuel
```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│              🚀 COSMIC QUERY AGENT                          │
│                                                             │
│     "Lancez en confiance. Decouvrez l'invisible."           │
│                                                             │
│  ═══════════════════════════════════════════════════════    │
│                                                             │
│  CE QU'ON CHERCHE                                           │
│  ────────────────                                           │
│                                                             │
│  ✓ Mentoring technique (mecanique orbitale)                 │
│  ✓ Acces beta-testeurs agences/operateurs                   │
│  ✓ Financement seed (150k EUR)                              │
│                                                             │
│  ═══════════════════════════════════════════════════════    │
│                                                             │
│  PROCHAINES ETAPES                                          │
│  ─────────────────                                          │
│                                                             │
│  Q2 2025: Beta publique                                     │
│  Q3 2025: Premier client enterprise                         │
│  Q4 2025: Integration Gaia DR4                              │
│                                                             │
│  ═══════════════════════════════════════════════════════    │
│                                                             │
│  MERCI !                                                    │
│                                                             │
│  Contact: [EMAIL]                                           │
│  Demo: cosmicquery.space                                    │
│                                                             │
│  [QR CODE vers la demo]                                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Script P4 (30 sec)
> "Pour conclure, ce qu'on cherche aujourd'hui.
>
> Du mentoring technique, particulierement en mecanique orbitale pour affiner nos modeles.
>
> L'acces a des beta-testeurs dans les agences ou chez les operateurs.
>
> Et un financement seed de 150 000 euros pour passer de MVP a produit commercial.
>
> Prochaines etapes : beta publique au Q2, premier client enterprise au Q3.
>
> Merci pour votre attention. On est disponibles pour vos questions, et vous pouvez scanner le QR code pour tester la demo en direct.
>
> [TOUS] Merci !"

---

## Annexe : Timing Detaille

| Slide | Presentateur | Duree | Cumul |
|-------|--------------|-------|-------|
| 1. Titre | P1 | 0:30 | 0:30 |
| 2. Probleme | P1 | 0:45 | 1:15 |
| 3. Solution | P1 | 0:45 | 2:00 |
| 4. Architecture | P2 | 0:45 | 2:45 |
| 5. Anomalies | P2 | 0:45 | 3:30 |
| 6. Risk Score | P2 | 0:45 | 4:15 |
| 7. Stack | P2 | 0:30 | 4:45 |
| 8. Demo Cosmic | P3 | 1:30 | 6:15 |
| 9. Demo Risk | P3 | 1:00 | 7:15 |
| 10. Demo Globe | P3 | 0:30 | 7:45 |
| 11. Marche | P4 | 0:45 | 8:30 |
| 12. Business | P4 | 0:45 | 9:15 |
| 13. Closing | P4 | 0:30 | 9:45 |
| **TOTAL** | | | **~10 min** |

---

## Annexe : Conseils de Presentation

### Avant la presentation

- [ ] Tester l'application sur le reseau du lieu
- [ ] Preparer un backup video de la demo
- [ ] Verifier la connexion LLM (Tailscale si distant)
- [ ] Charger les donnees en cache (M42, Space-Track)

### Pendant la presentation

- **P1** : Poser le probleme avec impact emotionnel (cout des reports)
- **P2** : Rester technique mais accessible, utiliser les visuels
- **P3** : Demo fluide, preparer les clics a l'avance
- **P4** : Finir sur l'ambition et le call-to-action clair

### Questions anticipees

| Question | Reponse courte |
|----------|----------------|
| "C'est quoi la difference avec LeoLabs ?" | "Eux font du tracking. Nous, on fait de l'intelligence : anomalies + risque + astronomie." |
| "Les donnees sont fiables ?" | "Space-Track est la source officielle US. Gaia est le gold standard ESA." |
| "Pourquoi un LLM ?" | "Pour interpreter, pas pour calculer. Le scoring est deterministe." |
| "Comment vous monetisez le free ?" | "Conversion vers Pro/Enterprise + notoriete academique." |
| "Quid de la competition avec les agences ?" | "On est complementaire. Elles fournissent les donnees, on fournit l'intelligence." |

---

## Annexe : Assets a Preparer

### Visuels PowerPoint

1. Logo Cosmic Query Agent (PNG transparent)
2. Screenshots application (haute resolution)
3. Diagramme architecture (editable)
4. Icones segments clients
5. QR code vers demo

### Demo

1. Application pre-chargee avec M42
2. Cache Space-Track recent (< 1h)
3. LLM connecte et teste
4. Backup video MP4 de 2 min

### Documents a distribuer

1. One-pager PDF
2. Business Model Canvas resume
3. Carte de visite avec QR code

---

*Document de presentation - ActInSpace 2025*
*Version 1.0 - Janvier 2026*
