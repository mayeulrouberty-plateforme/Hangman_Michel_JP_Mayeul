# Cosmic Query Agent - Etat du Projet

**Date:** 2026-01-26
**Hackathon:** ActInSpace 2025
**Statut:** MVP Fonctionnel

---

## Resume du Projet

Agent intelligent pour l'exploration multi-catalogues astronomiques avec detection automatique d'anomalies cross-catalogues.

**Differenciateur unique:** Aucun outil public n'existe pour la detection automatique d'incoherences entre catalogues astronomiques.

---

## Architecture Technique

```
src/
├── app.py              # Interface Streamlit (755 lignes)
├── config.py           # Configuration centralisee
├── astro_queries.py    # Requetes VizieR (Gaia, 2MASS, SDSS)
├── anomaly_detector.py # Detection d'anomalies
├── llm_agent.py        # Integration LLM (local/OpenAI)
├── .env                # Configuration locale
└── requirements.txt    # Dependances Python
```

### Stack Technique
- **Frontend:** Streamlit
- **Backend:** Python 3.x
- **Catalogues:** VizieR (CDS Strasbourg)
  - Gaia DR3 (I/355/gaiadr3)
  - 2MASS (II/246/out)
  - SDSS DR16 (V/154/sdss16)
- **LLM:** Compatible OpenAI API (local via LM Studio ou OpenAI)
- **Visualisation:** Plotly

---

## Fonctionnalites Implementees

### Recherche
- [x] Recherche par coordonnees (RA/Dec)
- [x] Recherche par nom d'objet (SIMBAD)
- [x] Recherche en langage naturel (LLM)
- [x] Cross-match Gaia + 2MASS
- [x] Cross-match Gaia + SDSS
- [x] Cross-match complet (Gaia + 2MASS + SDSS)

### Detection d'Anomalies
- [x] Anomalies photometriques (Gaia vs 2MASS/SDSS)
- [x] Anomalies astrometriques (position)
- [x] Anomalies de couleur (BP-RP extreme)
- [x] Sources manquantes dans cross-match
- [x] Score composite 0-100
- [x] Severite (low/medium/high)
- [x] Seuils configurables via UI

### Visualisation
- [x] Tableau de donnees interactif
- [x] Carte du ciel (scatter plot RA/Dec)
- [x] Diagramme HR (couleur vs magnitude absolue)
- [x] Graphiques anomalies par type/severite

### LLM
- [x] Support LLM local (LM Studio, Ollama)
- [x] Support OpenAI API
- [x] Interpretation des anomalies
- [x] Synthese des resultats
- [x] Conversion langage naturel -> intention
- [x] Gestion modeles "thinking" (GLM-4.7, DeepSeek-R1)

### Workflow
- [x] Export CSV/JSON
- [x] Selection de sources
- [x] Historique des requetes (session)
- [x] Liens SIMBAD pour chaque source

---

## Configuration Actuelle

### .env
```
USE_LOCAL_LLM=true
LOCAL_LLM_URL=http://127.0.0.1:1234/v1
LOCAL_LLM_MODEL=zai-org/glm-4.7-flash
```

### Seuils par defaut
- Photometric sigma: 3.0
- Astrometric sigma: 3.0
- Color delta: 0.3 mag
- Cross-match distance: 2.0 arcsec

---

## Bugs Corriges (2026-01-26)

1. **SIMBAD colonnes renommees** - 'RA'/'DEC' -> 'ra'/'dec' (lowercase, degrees)
2. **Streamlit width parameter** - `use_container_width=True` (pas `width="stretch"`)
3. **LLM content None** - Verification `content is None` avant `.strip()`
4. **NaN dans source_id** - Fonction `safe_source_id()` avec check `pd.isna()`
5. **NaN dans SkyCoord** - Filtrage des coordonnees invalides avant cross-match
6. **Session state reset** - Resultats persistes independamment du bouton recherche
7. **Import re** - Deplace en tete de fichier
8. **JSON parsing** - Gestion robuste des blocs markdown et erreurs

---

## Tests Valides

```
M42 (Nebuleuse d'Orion):
- Resolution SIMBAD: RA=83.8201, Dec=-5.3876
- Sources Gaia+2MASS: 100-200 selon rayon
- Anomalies detectees: ~70% des sources
- Types: photometric (majoritaire), astrometric, color, missing
- Interpretation LLM: fonctionne (GLM-4.7-Flash)
```

---

## Ameliorations Planifiees

### Priorite 1 - UI/UX
- [ ] Affichage plus clair des interpretations LLM
- [ ] Bouton "Interpreter toutes les anomalies"
- [ ] Export des interpretations en PDF/Markdown
- [ ] Indicateur de chargement ameliore
- [ ] Theme sombre

### Priorite 2 - Fonctionnel
- [ ] Filtres avances (magnitude min/max, parallaxe, couleur)
- [ ] Catalogue WISE/ALLWISE
- [ ] Comparaison multi-regions
- [ ] Sauvegarde/restauration de session complete
- [ ] Mode batch pour grandes regions

### Priorite 3 - LLM
- [ ] Prompt ADQL optimise pour modeles thinking
- [ ] Cache Redis/SQLite des interpretations
- [ ] Resume global automatique apres recherche
- [ ] Suggestions de recherches similaires

### Priorite 4 - Technique
- [ ] Tests unitaires (pytest)
- [ ] Logging structure (module logging)
- [ ] CI/CD pipeline
- [ ] Docker containerization
- [ ] Documentation API

### Priorite 5 - Science
- [ ] Detection d'etoiles variables
- [ ] Identification de candidats exoplanetes
- [ ] Clustering d'anomalies similaires
- [ ] Integration avec Aladin Lite

---

## Commandes Utiles

### Lancer l'application
```bash
cd "M:\Projet ActInSpace\src"
.\venv\Scripts\python.exe -m streamlit run app.py --server.headless true
```

### Tester le pipeline
```python
import astro_queries, anomaly_detector, llm_agent

coords = astro_queries.resolve_object_name('M42')
df = astro_queries.query_gaia_crossmatch_2mass(coords['ra'], coords['dec'], 0.1, 200)
anomalies = anomaly_detector.analyze_crossmatch_data(df)
print(f"Sources: {len(df)}, Anomalies: {anomalies['sources_with_anomalies']}")
```

### Tester le LLM
```bash
curl http://127.0.0.1:1234/v1/models
curl -X POST http://127.0.0.1:1234/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"zai-org/glm-4.7-flash","messages":[{"role":"user","content":"Hello"}]}'
```

---

## Modeles LLM Recommandes (RTX 5090 32GB)

| Modele | VRAM Q4 | Forces |
|--------|---------|--------|
| GLM-4.7-Flash | 17.5GB | Reasoning, coding, recent (Jan 2026) |
| DeepSeek-R1-Distill-Qwen-32B | 18GB | Reasoning, ADQL |
| Qwen3-30B-A3B | 8GB | Rapide, MoE |
| MiMo-V2-Flash | ~20GB | Code, math |

---

## Ressources

- **VizieR:** https://vizier.cds.unistra.fr/
- **SIMBAD:** https://simbad.u-strasbg.fr/
- **Gaia Archive:** https://gea.esac.esa.int/archive/
- **Astroquery docs:** https://astroquery.readthedocs.io/
- **Streamlit docs:** https://docs.streamlit.io/

---

## Contact / Equipe

Projet ActInSpace Hackathon 2025
