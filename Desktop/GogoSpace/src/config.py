"""
Configuration for Cosmic Query Agent
"""
import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# LLM Local (LM Studio, Ollama, etc.)
# Set USE_LOCAL_LLM=true in .env to use local model
USE_LOCAL_LLM = os.getenv("USE_LOCAL_LLM", "false").lower() == "true"
LOCAL_LLM_URL = os.getenv("LOCAL_LLM_URL", "http://127.0.0.1:1234/v1")
LOCAL_LLM_MODEL = os.getenv("LOCAL_LLM_MODEL", "local-model")

# Default search parameters
DEFAULT_SEARCH_RADIUS_DEG = 0.1  # degrees
MAX_SEARCH_RADIUS_DEG = 1.0
DEFAULT_ROW_LIMIT = 1000

# Anomaly detection thresholds
PHOTOMETRIC_SIGMA_THRESHOLD = 3.0  # Flag if delta > 3 sigma
ASTROMETRIC_SIGMA_THRESHOLD = 3.0
COLOR_DELTA_THRESHOLD = 0.3  # magnitudes

# Gaia tables
GAIA_SOURCE_TABLE = "gaiadr3.gaia_source"
GAIA_2MASS_XMATCH = "gaiadr3.tmass_psc_xsc_best_neighbour"
GAIA_SDSS_XMATCH = "gaiadr3.sdssdr13_best_neighbour"
TMASS_TABLE = "gaiadr1.tmass_original_valid"
SDSS_TABLE = "external.sdssdr13_photoprimary"

# ============================================
# SPACE TRAFFIC MANAGEMENT (STM) Configuration
# ============================================

# Celestrak TLE sources (no API key required)
CELESTRAK_BASE_URL = "https://celestrak.org/NORAD/elements/gp.php"

# Available TLE categories
TLE_CATEGORIES = {
    'stations': 'Stations spatiales (ISS, Tiangong)',
    'active': 'Satellites actifs',
    'starlink': 'Constellation Starlink',
    'oneweb': 'Constellation OneWeb',
    'visual': 'Satellites visibles',
    'weather': 'Satellites météo',
    'noaa': 'Satellites NOAA',
    'gps-ops': 'GPS opérationnels',
    'galileo': 'Galileo (EU)',
    'debris': 'Débris spatiaux suivis'
}

# Propagation settings
DEFAULT_PROPAGATION_HOURS = 24
MAX_PROPAGATION_HOURS = 168  # 7 days
PROPAGATION_STEP_MINUTES = 10

# Conjunction detection
CONJUNCTION_THRESHOLD_KM = 10.0
CONJUNCTION_WARNING_KM = 50.0

# ============================================
# SPACE-TRACK.ORG Configuration
# ============================================
# Free account required: https://www.space-track.org/auth/createAccount
SPACETRACK_USER = os.getenv("SPACETRACK_USER", "")
SPACETRACK_PASSWORD = os.getenv("SPACETRACK_PASSWORD", "")
SPACETRACK_BASE_URL = "https://www.space-track.org"

# Object types available from Space-Track
SPACETRACK_OBJECT_TYPES = {
    'PAYLOAD': 'Satellites (actifs/inactifs)',
    'ROCKET BODY': 'Corps de fusees',
    'DEBRIS': 'Debris spatiaux',
    'ALL': 'Tous les objets'
}

# ============================================
# CESIUM Configuration
# ============================================
# Free token from https://cesium.com/ion/
CESIUM_ION_TOKEN = os.getenv("CESIUM_ION_TOKEN", "")
CESIUM_DEFAULT_HEIGHT = 700
