# CLAUDE.md - Cosmic Query Agent & Launch Risk Assessment

## Project Overview

**Cosmic Query Agent** - Two integrated modules for space operations:

1. **Cosmic Queries**: AI-powered multi-catalog astronomical query tool with anomaly detection
2. **Launch Risk Assessment**: Collision risk evaluation and success probability for satellite launches

- **Context**: ActInSpace Hackathon 2025
- **Status**: MVP Functional (2026-01-31)
- **Target users**:
  - Researchers, space agencies (ESA, CNES)
  - Launch operators (ArianeGroup, SpaceX, RocketLab, Rocket Factory Augsburg)
- **Key innovations**:
  - Automatic detection of cross-catalog inconsistencies
  - Launch risk scoring with collision probability analysis

## Quick Start

```bash
cd src
.\venv\Scripts\python.exe -m streamlit run app.py --server.headless true
# Opens at http://127.0.0.1:8502
```

## Architecture

```
src/
├── app.py              # Streamlit UI (main entry)
├── config.py           # Configuration (LLM, thresholds, STM)
├── astro_queries.py    # VizieR queries (Gaia, 2MASS, SDSS)
├── anomaly_detector.py # Cross-catalog anomaly detection
├── llm_agent.py        # LLM integration (local/OpenAI)
├── stm_data.py         # TLE data fetching (Celestrak)
├── stm_propagator.py   # Orbit propagation (SGP4/Skyfield)
├── spacetrack_client.py # Space-Track.org API (debris data + caching)
├── cesium_viewer.py    # CesiumJS 3D globe visualization
├── launch_risk.py      # Launch risk assessment algorithm
├── data/               # Cache directory
│   └── spacetrack_cache.json  # Cached space objects
├── .env                # Local config
└── requirements.txt

docs/
├── PROJECT_STATUS.md   # Full status, roadmap, bugs fixed
└── concepts/           # Original concept documentation
```

## Key Technical Decisions

1. **VizieR over Gaia TAP** - ESA Gaia TAP had JOIN errors (500), VizieR (CDS Strasbourg) is stable
2. **Manual cross-match** - Using astropy `match_coordinates_sky` (max 2 arcsec separation)
3. **Session state persistence** - Results in `st.session_state` to survive Streamlit reruns
4. **Thinking model support** - Extract content after `</think>` tag for GLM-4.7, DeepSeek-R1

## LLM Configuration

Local LLM via LM Studio (recommended for RTX 5090 32GB):
```env
USE_LOCAL_LLM=true
LOCAL_LLM_URL=http://127.0.0.1:1234/v1
LOCAL_LLM_MODEL=zai-org/glm-4.7-flash
```

Best models: GLM-4.7-Flash (17.5GB Q4), DeepSeek-R1-Distill-Qwen-32B (18GB Q4)

## Data Sources

All via VizieR (CDS Strasbourg):
- **Gaia DR3**: I/355/gaiadr3 - positions, magnitudes, parallax
- **2MASS**: II/246/out - J, H, K infrared photometry
- **SDSS DR16**: V/154/sdss16 - u, g, r, i, z optical photometry

## Anomaly Detection

Types detected:
- **Photometric**: G magnitude vs expected from 2MASS/SDSS
- **Astrometric**: Position mismatch between catalogs
- **Color**: Extreme BP-RP values
- **Missing**: Expected cross-match not found

Configurable thresholds (default 3 sigma).

## Testing

```python
import astro_queries, anomaly_detector

coords = astro_queries.resolve_object_name('M42')
df = astro_queries.query_gaia_crossmatch_2mass(coords['ra'], coords['dec'], 0.1, 200)
anomalies = anomaly_detector.analyze_crossmatch_data(df)
# Typical: 200 sources, ~70% with anomalies
```

## Launch Risk Assessment

Module d'evaluation des risques pour les operateurs de lancement:

**Fonctionnalites:**
- Score de risque global (0-100)
- Probabilite de succes du lancement
- Detection des evenements de conjonction
- Recommandations de fenetres de lancement optimales
- Rapport detaille exportable en Markdown

**Sites de lancement supportes:**
- Kourou (CSG), Cape Canaveral, Vandenberg, Baikonur
- Jiuquan, Tanegashima, Sriharikota, Plesetsk
- Mahia Peninsula, Starbase Boca Chica

**Orbites cibles:**
- LEO (400km, 550km Starlink)
- SSO (600km)
- MEO (20000km)
- GTO, GEO

**Algorithme de risque:**
```python
import launch_risk

assessment = launch_risk.assess_launch_risk(
    launch_site="Kourou (CSG)",
    target_orbit="LEO (400km)",
    launch_datetime=datetime.now(),
    space_objects=catalog
)
print(f"Risk: {assessment.overall_risk_score}/100")
print(f"Success: {assessment.success_probability}%")
```

## Globe 3D (CesiumJS)

Visualisation 3D temps reel des satellites et debris:

**Sources de donnees:**
- **Celestrak**: Satellites actifs (gratuit, sans compte)
- **Space-Track.org**: Debris + tous objets (compte gratuit requis)

**Configuration Space-Track:**
1. Creer compte: https://www.space-track.org/auth/createAccount
2. Ajouter dans `.env`:
```env
SPACETRACK_USER=votre-email
SPACETRACK_PASSWORD=votre-mot-de-passe
```

**Fonctionnalites:**
- Globe interactif avec zoom/rotation
- Code couleur: Vert=satellites, Rouge=debris, Orange=corps fusees
- Clic sur objet pour details
- Export CSV des positions

## Known Issues (Fixed 2026-01-26)

- SIMBAD columns now lowercase ('ra'/'dec')
- LLM response.content can be None - added checks
- NaN in source_id/coordinates - added safe handling
- Streamlit session state - results persist across button clicks

## Reprendre le Projet

1. **Lancer LM Studio** sur port 1234, charger GLM-4.7-Flash
2. **Lancer l'app:**
   ```bash
   cd "M:\Projet ActInSpace\src"
   .\venv\Scripts\python.exe -m streamlit run app.py --server.headless true
   ```
3. **Tester:** http://127.0.0.1:8502 → M42 → Rechercher → Anomalies → Interpreter

**Prochaines etapes prioritaires:**
1. Ameliorer l'affichage des interpretations LLM
2. Ajouter filtres avances (magnitude, parallaxe)
3. Export PDF des analyses
4. Tests unitaires

Voir `docs/PROJECT_STATUS.md` pour roadmap complete.

## See Also

- `docs/PROJECT_STATUS.md` - Detailed status, roadmap, all bugs fixed
- `docs/concepts/INDEX.md` - Original concept exploration
