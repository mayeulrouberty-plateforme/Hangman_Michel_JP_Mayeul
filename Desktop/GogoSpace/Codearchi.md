# Cosmic Query Agent - Architecture Technique

**Version:** 2.0 (STM Integration)
**Date:** 2026-01-31
**Hackathon:** ActInSpace 2025

---

## Vue d'Ensemble

Application Streamlit unifiée combinant:
- **Cosmic Queries**: Exploration multi-catalogues astronomiques avec détection d'anomalies
- **Space Traffic Management (STM)**: Suivi de satellites et propagation d'orbites

```
┌─────────────────────────────────────────────────────────────┐
│                    COSMIC QUERY AGENT                        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐    ┌─────────────────────────────────┐ │
│  │   SIDEBAR       │    │         MAIN CONTENT            │ │
│  │                 │    │                                 │ │
│  │ [Module]        │    │  ┌─────────┐ ┌─────────────────┐│ │
│  │ ○ Cosmic Queries│    │  │ Cosmic  │ │ Space Traffic   ││ │
│  │ ○ Space Traffic │    │  │ Queries │ │ Management      ││ │
│  │                 │    │  └─────────┘ └─────────────────┘│ │
│  │ [Config...]     │    │                                 │ │
│  └─────────────────┘    └─────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## Structure des Fichiers

```
src/
├── app.py                 # Point d'entrée Streamlit (~1100 lignes)
├── config.py              # Configuration centralisée
├── requirements.txt       # Dépendances Python
├── .env                   # Variables d'environnement (local)
├── test_integration.py    # Tests d'intégration
│
├── # COSMIC QUERIES
├── astro_queries.py       # Requêtes VizieR (Gaia, 2MASS, SDSS)
├── anomaly_detector.py    # Détection d'anomalies cross-catalogue
├── llm_agent.py           # Intégration LLM (local/OpenAI)
│
├── # SPACE TRAFFIC MANAGEMENT
├── stm_data.py            # Téléchargement TLE (Celestrak)
├── stm_propagator.py      # Propagation orbite (Skyfield/SGP4)
├── spacetrack_client.py   # API Space-Track.org (débris)
└── cesium_viewer.py       # Visualisation Globe 3D (CesiumJS)
```

---

## Modules Détaillés

### 1. `app.py` - Interface Streamlit

Point d'entrée unique gérant les deux modules.

```python
# Structure principale
def main():
    init_session_state()
    params = render_sidebar()

    if st.session_state.app_mode == 'stm':
        render_stm_section(params)
    else:
        render_cosmic_section(params)
```

**Onglets Cosmic Queries:**
- Données (tableau sources)
- Visualisation (carte ciel, diagramme HR)
- Anomalies (dashboard détection)
- Réglages (seuils détection)
- Workflow (export, historique)

**Onglets STM:**
- Données TLE (téléchargement, liste satellites)
- Suivi Temps Réel (position actuelle)
- Propagation (trajectoire, trace au sol)

---

### 2. `config.py` - Configuration

```python
# LLM Configuration
USE_LOCAL_LLM = True/False
LOCAL_LLM_URL = "http://127.0.0.1:1234/v1"
LOCAL_LLM_MODEL = "zai-org/glm-4.7-flash"

# Anomaly Detection Thresholds
PHOTOMETRIC_SIGMA_THRESHOLD = 3.0
ASTROMETRIC_SIGMA_THRESHOLD = 3.0
COLOR_DELTA_THRESHOLD = 0.3

# STM Configuration
CELESTRAK_BASE_URL = "https://celestrak.org/NORAD/elements/gp.php"
DEFAULT_PROPAGATION_HOURS = 24
PROPAGATION_STEP_MINUTES = 10

# TLE Categories
TLE_CATEGORIES = {
    'stations': 'Stations spatiales (ISS, Tiangong)',
    'active': 'Satellites actifs',
    'starlink': 'Constellation Starlink',
    'oneweb': 'Constellation OneWeb',
    ...
}
```

---

### 3. `astro_queries.py` - Requêtes Astronomiques

Interroge VizieR (CDS Strasbourg) pour les catalogues.

```python
# Catalogues disponibles
CATALOGS = {
    'gaia': 'I/355/gaiadr3',      # Gaia DR3
    '2mass': 'II/246/out',         # 2MASS
    'sdss': 'V/154/sdss16',        # SDSS DR16
}

# Fonctions principales
def query_gaia_region(ra, dec, radius_deg, limit) -> DataFrame
def query_2mass_region(ra, dec, radius_deg, limit) -> DataFrame
def query_sdss_region(ra, dec, radius_deg, limit) -> DataFrame
def crossmatch_catalogs(df1, df2, max_sep_arcsec) -> DataFrame
def query_gaia_crossmatch_2mass(ra, dec, radius, limit) -> DataFrame
def query_gaia_full_crossmatch(ra, dec, radius, limit) -> DataFrame
def resolve_object_name(name) -> Dict[ra, dec]  # Via SIMBAD
```

---

### 4. `anomaly_detector.py` - Détection d'Anomalies

Détecte les incohérences entre catalogues.

```python
class AnomalyType(Enum):
    PHOTOMETRIC = "photometric"   # Magnitude incohérente
    ASTROMETRIC = "astrometric"   # Position décalée
    COLOR = "color"               # Couleur extrême
    MISSING = "missing"           # Cross-match manquant

@dataclass
class Anomaly:
    source_id: int
    anomaly_type: AnomalyType
    severity: str  # 'low', 'medium', 'high'
    sigma: float
    description: str
    details: Dict

# Détecteurs
def detect_photometric_anomalies_gaia_sdss(df) -> List[Anomaly]
def detect_photometric_anomalies_gaia_2mass(df) -> List[Anomaly]
def detect_astrometric_anomalies(df) -> List[Anomaly]
def detect_color_anomalies(df) -> List[Anomaly]
def detect_missing_crossmatch(df) -> List[Anomaly]

# Analyse complète
def analyze_crossmatch_data(df) -> Dict:
    return {
        'total_sources': int,
        'sources_with_anomalies': int,
        'anomaly_rate': float,
        'by_type': Dict,
        'by_severity': Dict,
        'top_anomalies': List[Dict]
    }
```

---

### 5. `llm_agent.py` - Intégration LLM

Support LLM local (LM Studio) et OpenAI.

```python
# Client flexible
def get_client() -> OpenAI:
    if config.USE_LOCAL_LLM:
        return OpenAI(base_url=config.LOCAL_LLM_URL, api_key="not-needed")
    return OpenAI(api_key=config.OPENAI_API_KEY)

# Fonctions
def natural_language_to_adql(query, context) -> str
def synthesize_results(query, data_summary, anomalies) -> str
def interpret_anomaly(anomaly) -> str
def parse_user_intent(query) -> Dict

# Support modèles "thinking" (GLM-4.7, DeepSeek-R1)
# Extraction automatique après </think> tag
```

---

### 6. `stm_data.py` - Données Satellites

Téléchargement TLE depuis Celestrak (gratuit, sans API key).

```python
@dataclass
class Satellite:
    name: str
    norad_id: int
    intl_designator: str
    tle_line1: str
    tle_line2: str
    epoch: datetime

# Fonctions
def fetch_tle_celestrak(category, limit) -> List[Satellite]
def parse_tle_text(tle_text) -> List[Satellite]
def satellites_to_dataframe(satellites) -> DataFrame
def get_tle_categories() -> Dict[str, str]
def fetch_iss() -> Satellite  # Convenience
```

**Catégories disponibles:**
- `stations` - ISS, Tiangong
- `starlink` - Constellation Starlink (~6000)
- `active` - Tous satellites actifs
- `visual` - Satellites visibles à l'oeil nu
- `weather` - Satellites météo
- `gps-ops` - GPS opérationnels
- `galileo` - Galileo (EU)

---

### 7. `stm_propagator.py` - Propagation Orbite

Calcul de trajectoires avec Skyfield et SGP4.

```python
# Position actuelle
def get_current_position(tle1, tle2, name) -> Dict:
    return {
        'lat': float,
        'lon': float,
        'alt_km': float,
        'velocity_km_s': float
    }

# Propagation temporelle
def propagate_orbit(tle1, tle2, name, hours_ahead, step_minutes) -> DataFrame:
    # Colonnes: time, lat, lon, alt_km, velocity_km_s

# Paramètres orbitaux
def get_orbit_info(tle1, tle2) -> Dict:
    return {
        'orbit_type': 'LEO'|'MEO'|'GEO'|'HEO',
        'period_minutes': float,
        'inclination_deg': float,
        'eccentricity': float,
        'altitude_km_approx': float
    }

# Visibilité depuis observateur
def check_visibility(tle1, tle2, obs_lat, obs_lon) -> Dict
```

---

### 8. `spacetrack_client.py` - API Space-Track.org

Accès au catalogue complet incluant débris spatiaux.

**Prérequis:** Compte gratuit sur https://www.space-track.org

```python
@dataclass
class SpaceObject:
    name: str
    norad_id: int
    object_type: str  # PAYLOAD, ROCKET BODY, DEBRIS
    country: str
    tle_line1: str
    tle_line2: str
    rcs_size: str  # SMALL, MEDIUM, LARGE

class SpaceTrackClient:
    def login() -> bool
    def fetch_debris(limit) -> List[SpaceObject]
    def fetch_rocket_bodies(limit) -> List[SpaceObject]
    def fetch_active_payloads(limit) -> List[SpaceObject]
    def fetch_all_objects(limit_per_type) -> List[SpaceObject]
    def fetch_by_norad_ids(norad_ids) -> List[SpaceObject]

# Helpers
def is_spacetrack_available() -> bool
def get_client() -> SpaceTrackClient
def get_spacetrack_categories() -> Dict[str, str]
```

**Configuration .env:**
```bash
SPACETRACK_USER=votre-email
SPACETRACK_PASSWORD=votre-mot-de-passe
```

---

### 9. `cesium_viewer.py` - Globe 3D CesiumJS

Visualisation 3D temps réel des objets spatiaux.

```python
# Génération HTML CesiumJS
def generate_cesium_html(
    satellites_json: str,
    height: int = 700,
    show_labels: bool = True,
    show_orbits: bool = True
) -> str

# Rendu dans Streamlit
def render_cesium_globe(
    satellites: List[Dict],  # name, norad_id, lat, lon, alt_km, object_type
    height: int = 700,
    show_labels: bool = False,
    show_orbits: bool = True
)

# Préparation des données
def prepare_satellites_for_cesium(
    satellites,
    propagator_func  # Pour calculer positions actuelles
) -> List[Dict]
```

**Fonctionnalités:**
- Globe terrestre interactif (zoom, rotation, tilt)
- Code couleur par type:
  - 🟢 Vert: Satellites (PAYLOAD)
  - 🟠 Orange: Corps de fusées (ROCKET BODY)
  - 🔴 Rouge: Débris (DEBRIS)
- Panneau d'information au clic
- Contrôles: labels, orbites, animation temporelle
- Export des données

**Configuration optionnelle:**
```bash
# Token Cesium Ion pour terrain haute résolution
CESIUM_ION_TOKEN=votre-token
```

---

## Dépendances

```txt
# requirements.txt

# Web Interface
streamlit>=1.31.0

# Astronomical Data
astroquery>=0.4.7
astropy>=6.0.0

# LLM Integration
openai>=1.12.0
python-dotenv>=1.0.0

# Data Processing
pandas>=2.2.0
numpy>=1.26.0

# Visualization
plotly>=5.18.0

# Utilities
requests>=2.31.0

# Space Traffic Management (STM)
skyfield>=1.46
sgp4>=2.23
```

---

## Configuration Environnement

```bash
# .env

# LLM Local (recommandé)
USE_LOCAL_LLM=true
LOCAL_LLM_URL=http://127.0.0.1:1234/v1
LOCAL_LLM_MODEL=zai-org/glm-4.7-flash

# Ou OpenAI
# OPENAI_API_KEY=sk-...
```

---

## Lancement

```bash
# Installation
cd src
pip install -r requirements.txt

# Lancement
streamlit run app.py --server.headless true

# URL: http://127.0.0.1:8501
```

---

## Flux de Données

### Cosmic Queries

```
User Input (nom/coords)
       ↓
   SIMBAD (résolution nom)
       ↓
   VizieR (Gaia DR3)
       ↓
   VizieR (2MASS/SDSS)
       ↓
   Cross-match (astropy)
       ↓
   Anomaly Detection
       ↓
   LLM Interpretation
       ↓
   Visualisation (Plotly)
```

### Space Traffic Management

```
User Selection (catégorie)
       ↓
   Celestrak (TLE download)
       ↓
   Parse TLE
       ↓
   Skyfield (propagation SGP4)
       ↓
   Position/Trajectoire
       ↓
   Visualisation (Plotly Geo)
```

---

## API Externe Utilisées

| Service | Usage | Auth |
|---------|-------|------|
| VizieR (CDS) | Catalogues Gaia, 2MASS, SDSS | Aucune |
| SIMBAD (CDS) | Résolution noms objets | Aucune |
| Celestrak | TLE satellites | Aucune |
| LM Studio | LLM local | Aucune |
| OpenAI | LLM cloud (optionnel) | API Key |

---

## Tests

```bash
# Lancer tous les tests
cd src
python3 test_integration.py
```

```python
# Test Cosmic Queries
import astro_queries, anomaly_detector

coords = astro_queries.resolve_object_name('M42')
df = astro_queries.query_gaia_crossmatch_2mass(coords['ra'], coords['dec'], 0.1, 200)
anomalies = anomaly_detector.analyze_crossmatch_data(df)
print(f"Sources: {len(df)}, Anomalies: {anomalies['sources_with_anomalies']}")

# Test STM
import stm_data, stm_propagator

satellites = stm_data.fetch_tle_celestrak('stations', 10)
iss = stm_data.fetch_iss()
pos = stm_propagator.get_current_position(iss.tle_line1, iss.tle_line2, iss.name)
print(f"ISS: {pos['lat']:.2f}, {pos['lon']:.2f}, Alt: {pos['alt_km']:.0f} km")

# Test Space-Track (si configuré)
import spacetrack_client

if spacetrack_client.is_spacetrack_available():
    client = spacetrack_client.get_client()
    debris = client.fetch_debris(100)
    print(f"Debris: {len(debris)} objets")

# Test Cesium Viewer
import cesium_viewer, json

test_data = [{'name': 'TEST', 'norad_id': 1, 'lat': 0, 'lon': 0, 'alt_km': 400, 'object_type': 'PAYLOAD'}]
html = cesium_viewer.generate_cesium_html(json.dumps(test_data), 600)
print(f"Cesium HTML: {len(html)} chars")
```

---

## Roadmap

### Phase 1 - MVP (Complet)
- [x] Cosmic Queries (Gaia, 2MASS, SDSS)
- [x] Anomaly Detection
- [x] LLM Integration
- [x] STM Basic (TLE, propagation)
- [x] Space-Track.org (débris spatiaux)
- [x] Globe 3D CesiumJS
- [x] Tests d'intégration

### Phase 2 - Améliorations
- [ ] Détection de conjonctions satellites
- [ ] Aladin Lite intégré
- [ ] Export PDF rapports
- [ ] Cache Redis/SQLite
- [ ] Alertes collision temps réel

### Phase 3 - Production
- [ ] Docker containerization
- [ ] CI/CD pipeline
- [ ] Tests unitaires complets
- [ ] Documentation API
- [ ] Monitoring / observabilité

---

## Équipe

Projet ActInSpace Hackathon 2025

---

*Document mis à jour le 2026-01-31 - Version 2.1 (Space-Track + Globe 3D)*
