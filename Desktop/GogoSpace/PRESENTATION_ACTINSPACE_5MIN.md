# Presentation ActInSpace 2025 - Cosmic Query Agent

> **Duree** : 5 minutes (4 min presentation + 1 min Q&A)
> **Equipe** : 4 presentateurs
> **Format** : Pitch rapide + Demo eclair

---

## Repartition des Roles

| Presentateur | Role | Slides | Duree |
|--------------|------|--------|-------|
| **P1** | Probleme + Solution | 1-2 | 1 min |
| **P2** | Technique | 3 | 45 sec |
| **P3** | Demo Live | 4 | 1 min 15 |
| **P4** | Business + Closing | 5-6 | 1 min |

---

## SLIDE 1 : Accroche + Probleme (P1)

### Visuel
```
┌─────────────────────────────────────────────────────────────┐
│              🚀 COSMIC QUERY AGENT                          │
│     Intelligence Spatiale pour Operations de Lancement      │
│                                                             │
│  ────────────────────────────────────────────────────────   │
│                                                             │
│  LE PROBLEME                                                │
│                                                             │
│  🔴 50,000 objets en orbite (debris + satellites)           │
│  🔴 Donnees fragmentees (Space-Track, Gaia, Celestrak)      │
│  🔴 Aucun outil unifie pour evaluer les risques             │
│                                                             │
│  💰 1 report de lancement = 500k - 2M EUR                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Script P1 (30 sec)
> "Bonjour, equipe [NOM], projet Cosmic Query Agent.
>
> Vous etes operateur de lancement. Dans 3 heures, decollage. Mais parmi les 50 000 objets en orbite, combien menacent votre trajectoire ?
>
> Aujourd'hui, impossible de le savoir rapidement. Les donnees sont fragmentees entre Space-Track, Celestrak, les catalogues ESA.
>
> Resultat : des reports de lancement qui coutent jusqu'a 2 millions d'euros."

---

## SLIDE 2 : Notre Solution (P1)

### Visuel
```
┌─────────────────────────────────────────────────────────────┐
│  COSMIC QUERY AGENT - 3 MODULES                             │
│  ──────────────────────────────                             │
│                                                             │
│  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐     │
│  │ COSMIC        │ │ LAUNCH RISK   │ │ GLOBE 3D      │     │
│  │ QUERIES       │ │ ASSESSMENT    │ │               │     │
│  │               │ │               │ │               │     │
│  │ Cross-match   │ │ Score 0-100   │ │ 50,000 objets │     │
│  │ 3 catalogues  │ │ Proba succes  │ │ temps reel    │     │
│  │ Detection IA  │ │ Fenetres opt. │ │               │     │
│  └───────────────┘ └───────────────┘ └───────────────┘     │
│                                                             │
│  ✅ 30 secondes pour un score de risque complet             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Script P1 (30 sec)
> "Notre solution unifie tout en une plateforme.
>
> Module 1 : on croise automatiquement Gaia, 2MASS et SDSS pour detecter les anomalies astronomiques.
>
> Module 2 : un score de risque de 0 a 100, une probabilite de succes, des fenetres de lancement optimales.
>
> Module 3 : un globe 3D avec les 50 000 objets en temps reel.
>
> Le tout en 30 secondes. [P2] pour la technique."

---

## SLIDE 3 : Comment ca marche (P2)

### Visuel
```
┌─────────────────────────────────────────────────────────────┐
│  ARCHITECTURE + ALGORITHME                                  │
│  ─────────────────────────                                  │
│                                                             │
│  DONNEES                      SCORE DE RISQUE (0-100)       │
│  ───────                      ───────────────────────       │
│  Gaia DR3 (1.8B sources)      = Densite debris    (25 pts)  │
│  2MASS, SDSS                  + Proba collision   (30 pts)  │
│  Space-Track (50k objets)     + Nb conjonctions   (20 pts)  │
│  Celestrak TLE                + Congestion orbite (15 pts)  │
│                               + Facteur temporel  (10 pts)  │
│  DETECTION ANOMALIES                                        │
│  ───────────────────          Succes = (100-Score) x 0.98   │
│  4 types: photometrique,                                    │
│  astrometrique, couleur,      🟢 <20  🟡 20-40  🔴 >40      │
│  cross-match manquant                                       │
│                                                             │
│  Stack: Python, Streamlit, Cesium, LLM                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Script P2 (45 sec)
> "Techniquement, on aggrege les meilleures sources : Gaia de l'ESA, Space-Track pour les debris, Celestrak pour les TLE.
>
> Notre algorithme calcule un score composite. 5 facteurs : densite de debris, probabilite de collision basee sur la distance 3D, nombre de conjonctions, congestion orbitale, et facteur temporel.
>
> Pour les anomalies astronomiques, on detecte 4 types : photometrique, astrometrique, couleur extreme, et cross-match manquant. Tout est interprete par un LLM.
>
> Stack 100% Python, open source. [P3], demo."

---

## SLIDE 4 : Demo Live (P3)

### Visuel
```
┌─────────────────────────────────────────────────────────────┐
│  DEMO LIVE                                                  │
│  ─────────                                                  │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                                                     │   │
│  │     [APPLICATION EN DIRECT]                         │   │
│  │                                                     │   │
│  │     1. Recherche M42 → Detection anomalies          │   │
│  │     2. Evaluation risque Kourou → LEO 400km         │   │
│  │     3. Globe 3D satellites/debris                   │   │
│  │                                                     │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  🌐 http://127.0.0.1:8502                                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Script P3 - DEMO LIVE (1 min 15)

**Partie 1 - Cosmic Queries (25 sec)**
> "Demo live. Je cherche M42, nebuleuse d'Orion.
>
> [CLIC] En 5 secondes, 200 sources croisees entre Gaia, 2MASS, SDSS.
>
> Onglet Anomalies : 70% ont une anomalie. Je clique sur une source rouge, le popup affiche les details. Notre LLM interprete."

**Partie 2 - Launch Risk (25 sec)**
> "Module risque. Site : Kourou. Orbite : LEO 400km.
>
> [CLIC] Score : 23/100, vert. Probabilite succes : 95%. 3 conjonctions detectees. Fenetre optimale dans 4 heures.
>
> Rapport exportable en un clic."

**Partie 3 - Globe (25 sec)**
> "Le globe 3D. 50 000 objets. Vert = satellites, rouge = debris.
>
> [ZOOM] Je zoome sur Kourou, je vois exactement ce qui orbite au-dessus.
>
> Tout est mis a jour toutes les heures. [P4] pour le business."

---

## SLIDE 5 : Marche et Business Model (P4)

### Visuel
```
┌─────────────────────────────────────────────────────────────┐
│  MARCHE ET MODELE                                           │
│  ────────────────                                           │
│                                                             │
│  SEGMENTS               PRICING                             │
│  ────────               ───────                             │
│  👨‍🔬 Chercheurs          FREE      0 EUR     Volume         │
│  🏛️ Agences (ESA/CNES)  PRO       49 EUR/mois              │
│  🚀 Operateurs          ENTERPRISE 5-50k/mois  Revenue     │
│     (Ariane, SpaceX)                                        │
│                                                             │
│  PROJECTIONS                                                │
│  ───────────                                                │
│  Y1: 72k EUR  │  Y3: 1.2M EUR  │  Y5: 3M EUR               │
│                                                             │
│  AVANTAGE COMPETITIF                                        │
│  ───────────────────                                        │
│  Seul outil = Astronomie + Risk + Globe unifie              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Script P4 (30 sec)
> "Trois segments. Chercheurs en freemium pour le volume. Agences ESA, CNES pour la credibilite. Operateurs comme ArianeGroup ou SpaceX pour le revenu : 5 a 50k par mois.
>
> Projections : 72 000 euros annee 1, 1.2 million annee 3, 3 millions annee 5.
>
> Notre avantage : on est les seuls a unifier astronomie, evaluation de risque et visualisation 3D."

---

## SLIDE 6 : Closing (P4)

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
│  ON CHERCHE                                                 │
│  ──────────                                                 │
│  ✓ Mentoring mecanique orbitale                             │
│  ✓ Beta-testeurs agences/operateurs                         │
│  ✓ Seed 150k EUR                                            │
│                                                             │
│  ═══════════════════════════════════════════════════════    │
│                                                             │
│  MERCI !   Questions ?                                      │
│                                                             │
│  [QR CODE]  cosmicquery.space                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Script P4 (30 sec)
> "On cherche du mentoring en mecanique orbitale, des beta-testeurs dans les agences ou chez les operateurs, et un seed de 150 000 euros.
>
> Scannez le QR code pour tester la demo.
>
> Merci ! On repond a vos questions."

---

## Timing Resume

| Slide | Presentateur | Contenu | Duree | Cumul |
|-------|--------------|---------|-------|-------|
| 1 | P1 | Probleme | 0:30 | 0:30 |
| 2 | P1 | Solution | 0:30 | 1:00 |
| 3 | P2 | Technique | 0:45 | 1:45 |
| 4 | P3 | Demo | 1:15 | 3:00 |
| 5 | P4 | Business | 0:30 | 3:30 |
| 6 | P4 | Closing | 0:30 | 4:00 |
| - | Tous | **Q&A** | 1:00 | **5:00** |

---

## Checklist Avant Presentation

### Technique
- [ ] App lancee et testee (http://127.0.0.1:8502)
- [ ] M42 pre-charge en cache
- [ ] LLM connecte (Tailscale 100.113.253.81:1234)
- [ ] Space-Track synchronise (< 1h)
- [ ] Backup video 1 min (si probleme reseau)

### Presentateurs
- [ ] Ordre de passage clair
- [ ] Transitions pratiquees ("Je passe a P2...")
- [ ] Chronometre visible

### Materiel
- [ ] QR code imprime ou affiche
- [ ] Clicker/telecommande
- [ ] Micro teste

---

## Questions Anticipees (1 min Q&A)

| Question Probable | Reponse (15 sec max) |
|-------------------|----------------------|
| "Difference avec LeoLabs ?" | "Eux font du tracking. Nous, de l'intelligence : anomalies + risque + interpretation IA." |
| "Fiabilite des donnees ?" | "Space-Track = source officielle US. Gaia = gold standard ESA." |
| "Pourquoi un LLM ?" | "Pour interpreter, pas calculer. Le scoring est 100% deterministe." |
| "Concurrence agences ?" | "Complementaire. Elles fournissent les donnees, on fournit l'intelligence." |
| "Et la securite ?" | "Deployable on-premise pour clients sensibles." |

---

## Script Complet Condense (pour memorisation)

### P1 (1 min)
> "Bonjour, equipe [NOM], Cosmic Query Agent. Vous etes operateur, decollage dans 3h, 50 000 objets en orbite. Lequel menace votre trajectoire ? Aujourd'hui, impossible a savoir vite. Donnees fragmentees. Reports a 2 millions d'euros.
>
> Notre solution : 3 modules. Cross-match astronomique avec detection IA. Score de risque 0-100 avec probabilite de succes. Globe 3D temps reel. 30 secondes pour tout savoir. [P2]."

### P2 (45 sec)
> "On aggrege Gaia, Space-Track, Celestrak. Score = 5 facteurs : debris, collision, conjonctions, congestion, temporel. Detection de 4 types d'anomalies. LLM pour interpreter. Stack Python, open source. [P3] demo."

### P3 (1 min 15)
> "M42. [CLIC] 200 sources, 5 secondes. Anomalies : 70%. Popup, interpretation LLM.
> Risque : Kourou, LEO. [CLIC] Score 23, succes 95%, 3 conjonctions, fenetre +4h. Export.
> Globe : 50 000 objets, vert satellites, rouge debris. [ZOOM] Kourou. Mise a jour horaire. [P4]."

### P4 (1 min)
> "Chercheurs free, agences pro, operateurs enterprise 5-50k/mois. 72k Y1, 1.2M Y3, 3M Y5. Seul outil unifie astronomie + risque + 3D.
>
> On cherche : mentoring orbital, beta-testeurs, seed 150k. QR code pour la demo. Merci, questions ?"

---

*Presentation 5 minutes - ActInSpace 2025*
