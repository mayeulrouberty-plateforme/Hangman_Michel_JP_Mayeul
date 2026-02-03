"""
Cosmic Query Agent - Main Streamlit Application
ActInSpace Hackathon 2025
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional, Dict, Any
import numpy as np
import json
from datetime import datetime, timezone

import config
import astro_queries
import anomaly_detector
import llm_agent
import stm_data
import stm_propagator
import spacetrack_client
import cesium_viewer
import launch_risk


# Page config
st.set_page_config(
    page_title="Cosmic Query Agent",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)


def init_session_state():
    """Initialize session state variables."""
    defaults = {
        'query_results': None,
        'anomaly_results': None,
        'last_query': None,
        'query_history': [],
        'selected_sources': [],
        'interpretations': {},
        'detection_params': {
            'photometric_sigma': 3.0,
            'astrometric_sigma': 3.0,
            'color_delta': 0.3,
            'xmatch_max_dist': 2.0
        },
        # STM State
        'stm_satellites': None,
        'stm_selected_sat': None,
        'stm_trajectory': None,
        'app_mode': 'cosmic',  # 'cosmic' or 'stm'
        # 3D Globe State
        'globe_satellites': None,
        'globe_debris': None,
        'globe_data_source': 'celestrak',  # 'celestrak', 'spacetrack', 'both'
        # Launch Risk Assessment State
        'risk_assessment': None,
        'risk_report': None,
        'space_catalog': None,  # Cached space objects for risk analysis
        # Query coordinates for visualization
        'query_ra': None,
        'query_dec': None
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_sidebar():
    """Render sidebar with configuration options."""
    with st.sidebar:
        st.title("Cosmic Query Agent")
        st.caption("ActInSpace 2025")

        st.divider()

        # Application mode selection
        app_mode = st.radio(
            "Module",
            ["Cosmic Queries", "Launch Risk Assessment"],
            help="Basculer entre les modules"
        )
        st.session_state.app_mode = 'stm' if 'Launch' in app_mode else 'cosmic'

        st.divider()

        # Mode-specific sidebar content
        if st.session_state.app_mode == 'stm':
            return render_stm_sidebar()

        # Cosmic Queries mode selection
        mode = st.radio(
            "Mode de recherche",
            ["Coordonnees", "Nom d'objet", "Langage naturel"],
            help="Choisissez comment specifier votre cible"
        )

        st.divider()

        # Search parameters
        st.subheader("Parametres de recherche")

        radius = st.slider(
            "Rayon de recherche (degres)",
            min_value=0.01,
            max_value=1.0,
            value=0.1,
            step=0.01
        )

        limit = st.selectbox(
            "Nombre max de sources",
            [100, 500, 1000, 5000],
            index=1
        )

        st.divider()

        # Catalogs
        st.subheader("Catalogues")
        use_gaia = st.checkbox("Gaia DR3", value=True, disabled=True)
        use_2mass = st.checkbox("2MASS (infrarouge)", value=True)
        use_sdss = st.checkbox("SDSS DR16 (optique)", value=False)

        st.divider()

        # Anomaly detection toggle
        st.subheader("Detection d'anomalies")
        detect_anomalies = st.checkbox("Activer la detection", value=True)

        st.divider()

        # LLM status
        st.subheader("Statut LLM")
        if config.USE_LOCAL_LLM:
            st.success(f"LLM Local actif")
            st.caption(config.LOCAL_LLM_URL)
        elif config.OPENAI_API_KEY:
            st.success("OpenAI API")
        else:
            st.warning("LLM non configure")

        return {
            'mode': mode,
            'radius': radius,
            'limit': limit,
            'use_2mass': use_2mass,
            'use_sdss': use_sdss,
            'detect_anomalies': detect_anomalies
        }


def render_detection_settings():
    """Render advanced detection settings panel."""
    st.subheader("Reglages de detection")
    st.caption("Ajustez les seuils selon vos besoins de recherche")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Seuils de detection (en sigma)**")

        photo_sigma = st.slider(
            "Anomalies photometriques",
            min_value=1.0,
            max_value=10.0,
            value=st.session_state.detection_params['photometric_sigma'],
            step=0.5,
            help="Ecart en magnitude entre catalogues pour signaler une anomalie"
        )

        astro_sigma = st.slider(
            "Anomalies astrometriques",
            min_value=1.0,
            max_value=10.0,
            value=st.session_state.detection_params['astrometric_sigma'],
            step=0.5,
            help="Ecart de position entre catalogues"
        )

    with col2:
        st.markdown("**Parametres de cross-match**")

        color_delta = st.slider(
            "Seuil couleur anormale (mag)",
            min_value=0.1,
            max_value=1.0,
            value=st.session_state.detection_params['color_delta'],
            step=0.05,
            help="Ecart de couleur BP-RP pour signaler une anomalie"
        )

        xmatch_dist = st.slider(
            "Distance max cross-match (arcsec)",
            min_value=0.5,
            max_value=5.0,
            value=st.session_state.detection_params['xmatch_max_dist'],
            step=0.5,
            help="Distance maximale pour associer deux sources"
        )

    # Update session state
    st.session_state.detection_params = {
        'photometric_sigma': photo_sigma,
        'astrometric_sigma': astro_sigma,
        'color_delta': color_delta,
        'xmatch_max_dist': xmatch_dist
    }

    # Preset buttons
    st.markdown("**Presets**")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Conservateur", help="Moins de faux positifs"):
            st.session_state.detection_params = {
                'photometric_sigma': 5.0,
                'astrometric_sigma': 5.0,
                'color_delta': 0.5,
                'xmatch_max_dist': 1.5
            }
            st.rerun()

    with col2:
        if st.button("Standard", help="Parametres par defaut"):
            st.session_state.detection_params = {
                'photometric_sigma': 3.0,
                'astrometric_sigma': 3.0,
                'color_delta': 0.3,
                'xmatch_max_dist': 2.0
            }
            st.rerun()

    with col3:
        if st.button("Sensible", help="Detecte plus d'anomalies"):
            st.session_state.detection_params = {
                'photometric_sigma': 2.0,
                'astrometric_sigma': 2.0,
                'color_delta': 0.2,
                'xmatch_max_dist': 3.0
            }
            st.rerun()

    return st.session_state.detection_params


def render_coordinate_input():
    """Render coordinate input form."""
    st.subheader("Entrez les coordonnees")
    st.caption("Coordonnees equatoriales J2000 (ICRS)")
    col1, col2 = st.columns(2)
    with col1:
        ra = st.number_input("RA - Right Ascension (degres)", 0.0, 360.0, 180.0, 0.1)
    with col2:
        dec = st.number_input("Dec - Declinaison (degres)", -90.0, 90.0, 45.0, 0.1)
    return ra, dec


def render_object_input():
    """Render object name input."""
    st.subheader("Recherche par nom d'objet")
    st.caption("Entrez un nom d'objet astronomique (resolution via SIMBAD)")
    name = st.text_input(
        "Nom de l'objet",
        placeholder="Ex: M31, M42, NGC 1234, Vega, Betelgeuse...",
        help="Catalogues supportes: Messier (M), NGC, IC, HD, HIP, noms propres"
    )
    return name


def render_natural_language_input():
    """Render natural language query input."""
    st.subheader("Recherche en langage naturel")
    st.caption("Decrivez votre recherche, le LLM generera la requete")
    query = st.text_area(
        "Votre requete",
        placeholder="Ex: Quelles etoiles brillantes autour de M31 ont des donnees infrarouges ?",
        height=100
    )
    return query


def compute_data_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """Compute summary statistics for the data."""
    summary = {
        'total_sources': len(df)
    }

    if 'phot_g_mean_mag' in df.columns:
        g_mag = df['phot_g_mean_mag'].dropna()
        if len(g_mag) > 0:
            summary['magnitude_range'] = f"{g_mag.min():.1f} - {g_mag.max():.1f}"
            summary['median_magnitude'] = g_mag.median()

    if 'parallax' in df.columns:
        plx = df['parallax'].dropna()
        if len(plx) > 0:
            summary['parallax_range'] = f"{plx.min():.2f} - {plx.max():.2f} mas"

    if 'bp_rp' in df.columns:
        color = df['bp_rp'].dropna()
        if len(color) > 0:
            summary['color_range'] = f"{color.min():.2f} - {color.max():.2f}"

    return summary


def render_results_table(df: pd.DataFrame):
    """Render results as interactive table."""
    st.subheader(f"Resultats ({len(df)} sources)")

    # Column selection
    all_cols = df.columns.tolist()
    default_cols = ['source_id', 'ra', 'dec', 'phot_g_mean_mag', 'bp_rp', 'parallax']
    default_cols = [c for c in default_cols if c in all_cols]

    selected_cols = st.multiselect(
        "Colonnes a afficher",
        all_cols,
        default=default_cols[:6]
    )

    if selected_cols:
        st.dataframe(
            df[selected_cols],
            use_container_width=True,
            height=400
        )


def render_aladin_viewer(ra: float, dec: float, fov: float = 0.5, sources: list = None):
    """
    Render Aladin Lite sky viewer with sources overlay.

    Args:
        ra: Right Ascension in degrees
        dec: Declination in degrees
        fov: Field of view in degrees
        sources: List of dicts with 'ra', 'dec', 'name' keys
    """
    import streamlit.components.v1 as components

    # Prepare sources JavaScript array
    sources_js = "[]"
    if sources:
        source_items = []
        for s in sources[:500]:  # Limit for performance
            name = str(s.get('name', s.get('source_id', 'Source'))).replace("'", "\\'")
            source_items.append(f"{{ra: {s['ra']}, dec: {s['dec']}, name: '{name}'}}")
        sources_js = f"[{','.join(source_items)}]"

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <link rel="stylesheet" href="https://aladin.cds.unistra.fr/AladinLite/api/v3/latest/aladin.min.css" />
        <script type="text/javascript" src="https://aladin.cds.unistra.fr/AladinLite/api/v3/latest/aladin.js" charset="utf-8"></script>
        <style>
            #aladin-lite-div {{
                width: 100%;
                height: 500px;
            }}
            body {{
                margin: 0;
                padding: 0;
            }}
        </style>
    </head>
    <body>
        <div id="aladin-lite-div"></div>
        <script type="text/javascript">
            let aladin;
            A.init.then(() => {{
                aladin = A.aladin('#aladin-lite-div', {{
                    target: '{ra} {dec}',
                    fov: {fov},
                    survey: 'P/DSS2/color',
                    showReticle: true,
                    showZoomControl: true,
                    showFullscreenControl: true,
                    showLayersControl: true,
                    showGotoControl: true,
                    showFrame: true,
                    fullScreen: false
                }});

                // Add sources as catalog
                const sources = {sources_js};
                if (sources.length > 0) {{
                    let cat = A.catalog({{
                        name: 'Query Results',
                        sourceSize: 12,
                        color: '#ff6600',
                        onClick: 'showPopup'
                    }});

                    sources.forEach(s => {{
                        cat.addSources([A.source(s.ra, s.dec, {{name: s.name}})]);
                    }});

                    aladin.addCatalog(cat);
                }}

                // Add Gaia DR3 catalog overlay
                aladin.addCatalog(A.catalogFromVizieR('I/355/gaiadr3', '{ra} {dec}', {fov}, {{
                    onClick: 'showTable',
                    name: 'Gaia DR3',
                    color: '#00aaff',
                    sourceSize: 8
                }}));
            }});
        </script>
    </body>
    </html>
    """

    components.html(html, height=520, scrolling=False)


def render_aladin_anomalies(
    ra: float,
    dec: float,
    fov: float,
    df: pd.DataFrame,
    anomaly_results: Dict[str, Any]
):
    """
    Render Aladin Lite v3 with interactive anomaly visualization.

    Features:
    - Color-coded markers by anomaly type and severity
    - Clickable popups with anomaly details
    - Pulsing overlays for high-priority sources
    - Legend and filter controls

    Args:
        ra: Center Right Ascension in degrees
        dec: Center Declination in degrees
        fov: Field of view in degrees
        df: DataFrame with source data (must have 'ra', 'dec', 'source_id')
        anomaly_results: Results from anomaly_detector.analyze_crossmatch_data()
    """
    import streamlit.components.v1 as components
    import json

    # Build anomaly lookup by source_id
    anomaly_lookup = {}
    for item in anomaly_results.get('top_anomalies', []):
        sid = item['source_id']
        anomaly_lookup[sid] = {
            'score': item['score'],
            'anomalies': item['anomalies']
        }

    # Prepare sources with anomaly data
    sources_data = []
    for _, row in df.iterrows():
        if pd.isna(row.get('ra')) or pd.isna(row.get('dec')):
            continue

        sid = row.get('source_id', 0)
        if pd.isna(sid):
            sid = 0
        else:
            sid = int(sid)

        source = {
            'ra': float(row['ra']),
            'dec': float(row['dec']),
            'source_id': sid,
            'g_mag': round(float(row.get('phot_g_mean_mag', 0)), 2) if pd.notna(row.get('phot_g_mean_mag')) else None,
            'bp_rp': round(float(row.get('bp_rp', 0)), 2) if pd.notna(row.get('bp_rp')) else None,
            'parallax': round(float(row.get('parallax', 0)), 3) if pd.notna(row.get('parallax')) else None
        }

        # Add anomaly info if exists
        if sid in anomaly_lookup:
            source['has_anomaly'] = True
            source['score'] = anomaly_lookup[sid]['score']
            source['anomalies'] = anomaly_lookup[sid]['anomalies']
        else:
            source['has_anomaly'] = False
            source['score'] = 0
            source['anomalies'] = []

        sources_data.append(source)

    # Limit for performance
    sources_data = sources_data[:500]
    sources_json = json.dumps(sources_data, ensure_ascii=False)

    # Statistics for the legend
    stats = {
        'total': len(sources_data),
        'with_anomalies': sum(1 for s in sources_data if s['has_anomaly']),
        'high_priority': sum(1 for s in sources_data if s['score'] >= 50)
    }
    stats_json = json.dumps(stats)

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <link rel="stylesheet" href="https://aladin.cds.unistra.fr/AladinLite/api/v3/latest/aladin.min.css" />
        <script src="https://aladin.cds.unistra.fr/AladinLite/api/v3/latest/aladin.js" charset="utf-8"></script>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }}

            #container {{
                position: relative;
                width: 100%;
                height: 580px;
            }}

            #aladin-lite-div {{
                width: 100%;
                height: 500px;
                border-radius: 8px;
                overflow: hidden;
            }}

            /* Legend Panel */
            #legend {{
                position: absolute;
                top: 10px;
                left: 10px;
                background: rgba(0, 0, 0, 0.85);
                color: white;
                padding: 12px;
                border-radius: 8px;
                font-size: 11px;
                z-index: 100;
                max-width: 180px;
                backdrop-filter: blur(10px);
            }}

            #legend h4 {{
                margin-bottom: 8px;
                font-size: 12px;
                border-bottom: 1px solid rgba(255,255,255,0.3);
                padding-bottom: 4px;
            }}

            .legend-item {{
                display: flex;
                align-items: center;
                margin: 4px 0;
                cursor: pointer;
                padding: 2px 4px;
                border-radius: 4px;
                transition: background 0.2s;
            }}

            .legend-item:hover {{
                background: rgba(255,255,255,0.1);
            }}

            .legend-marker {{
                width: 12px;
                height: 12px;
                border-radius: 50%;
                margin-right: 8px;
                border: 2px solid rgba(255,255,255,0.5);
            }}

            .legend-item.disabled {{
                opacity: 0.4;
            }}

            /* Severity section */
            .severity-section {{
                margin-top: 10px;
                padding-top: 8px;
                border-top: 1px solid rgba(255,255,255,0.2);
            }}

            /* Stats bar */
            #stats-bar {{
                display: flex;
                justify-content: space-around;
                padding: 8px;
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                border-radius: 0 0 8px 8px;
                color: white;
                font-size: 11px;
            }}

            .stat-item {{
                text-align: center;
            }}

            .stat-value {{
                font-size: 16px;
                font-weight: bold;
                color: #00d4ff;
            }}

            /* Custom popup styles */
            .aladin-popup {{
                max-width: 320px !important;
            }}

            .anomaly-popup {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                font-size: 12px;
            }}

            .anomaly-popup h3 {{
                margin: 0 0 8px 0;
                padding-bottom: 6px;
                border-bottom: 2px solid;
                font-size: 14px;
            }}

            .anomaly-popup .score-badge {{
                display: inline-block;
                padding: 2px 8px;
                border-radius: 12px;
                font-weight: bold;
                font-size: 11px;
                margin-left: 8px;
            }}

            .anomaly-popup .props {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 4px;
                margin: 8px 0;
                padding: 8px;
                background: rgba(0,0,0,0.05);
                border-radius: 4px;
            }}

            .anomaly-popup .prop {{
                font-size: 11px;
            }}

            .anomaly-popup .prop-label {{
                color: #666;
            }}

            .anomaly-popup .anomaly-list {{
                margin-top: 10px;
            }}

            .anomaly-popup .anomaly-item {{
                padding: 6px 8px;
                margin: 4px 0;
                border-radius: 4px;
                border-left: 3px solid;
            }}

            .anomaly-popup .anomaly-item.high {{
                background: rgba(220, 53, 69, 0.1);
                border-color: #dc3545;
            }}

            .anomaly-popup .anomaly-item.medium {{
                background: rgba(255, 193, 7, 0.1);
                border-color: #ffc107;
            }}

            .anomaly-popup .anomaly-item.low {{
                background: rgba(40, 167, 69, 0.1);
                border-color: #28a745;
            }}

            .anomaly-popup .anomaly-type {{
                font-weight: bold;
                text-transform: uppercase;
                font-size: 10px;
            }}

            .anomaly-popup .anomaly-desc {{
                font-size: 11px;
                color: #333;
                margin-top: 2px;
            }}

            .anomaly-popup .sigma {{
                font-size: 10px;
                color: #666;
                float: right;
            }}

            /* Pulsing animation for high priority */
            @keyframes pulse {{
                0% {{ opacity: 1; transform: scale(1); }}
                50% {{ opacity: 0.6; transform: scale(1.3); }}
                100% {{ opacity: 1; transform: scale(1); }}
            }}

            .high-priority-ring {{
                animation: pulse 2s ease-in-out infinite;
            }}
        </style>
    </head>
    <body>
        <div id="container">
            <div id="aladin-lite-div"></div>

            <!-- Legend Panel -->
            <div id="legend">
                <h4>Types d'anomalies</h4>
                <div class="legend-item" data-type="photometric" onclick="toggleType('photometric')">
                    <div class="legend-marker" style="background: #e74c3c;"></div>
                    <span>Photometrique</span>
                </div>
                <div class="legend-item" data-type="astrometric" onclick="toggleType('astrometric')">
                    <div class="legend-marker" style="background: #9b59b6;"></div>
                    <span>Astrometrique</span>
                </div>
                <div class="legend-item" data-type="color" onclick="toggleType('color')">
                    <div class="legend-marker" style="background: #f39c12;"></div>
                    <span>Couleur</span>
                </div>
                <div class="legend-item" data-type="missing" onclick="toggleType('missing')">
                    <div class="legend-marker" style="background: #3498db;"></div>
                    <span>Cross-match manquant</span>
                </div>

                <div class="severity-section">
                    <h4>Severite</h4>
                    <div class="legend-item" data-severity="high" onclick="toggleSeverity('high')">
                        <div class="legend-marker" style="background: #dc3545; box-shadow: 0 0 8px #dc3545;"></div>
                        <span>Haute (≥5σ)</span>
                    </div>
                    <div class="legend-item" data-severity="medium" onclick="toggleSeverity('medium')">
                        <div class="legend-marker" style="background: #ffc107;"></div>
                        <span>Moyenne (3-5σ)</span>
                    </div>
                    <div class="legend-item" data-severity="low" onclick="toggleSeverity('low')">
                        <div class="legend-marker" style="background: #28a745;"></div>
                        <span>Basse (&lt;3σ)</span>
                    </div>
                </div>

                <div class="legend-item" style="margin-top: 10px; border-top: 1px solid rgba(255,255,255,0.2); padding-top: 8px;">
                    <div class="legend-marker" style="background: #6c757d;"></div>
                    <span>Normal (sans anomalie)</span>
                </div>
            </div>

            <!-- Stats Bar -->
            <div id="stats-bar">
                <div class="stat-item">
                    <div class="stat-value" id="stat-total">-</div>
                    <div>Sources</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value" id="stat-anomalies" style="color: #ffc107;">-</div>
                    <div>Avec anomalies</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value" id="stat-high" style="color: #dc3545;">-</div>
                    <div>Haute priorite</div>
                </div>
            </div>
        </div>

        <script>
            // Data from Python
            const sourcesData = {sources_json};
            const stats = {stats_json};

            // Color schemes
            const COLORS = {{
                types: {{
                    photometric: '#e74c3c',
                    astrometric: '#9b59b6',
                    color: '#f39c12',
                    missing: '#3498db'
                }},
                severity: {{
                    high: '#dc3545',
                    medium: '#ffc107',
                    low: '#28a745'
                }},
                normal: '#6c757d'
            }};

            // Filter state
            let activeFilters = {{
                types: new Set(['photometric', 'astrometric', 'color', 'missing']),
                severities: new Set(['high', 'medium', 'low'])
            }};

            // Catalogs reference
            let catalogs = {{}};
            let aladin;

            // Initialize Aladin
            A.init.then(() => {{
                aladin = A.aladin('#aladin-lite-div', {{
                    target: '{ra} {dec}',
                    fov: {fov},
                    survey: 'P/DSS2/color',
                    showReticle: true,
                    showZoomControl: true,
                    showFullscreenControl: true,
                    showLayersControl: true,
                    showGotoControl: true,
                    showFrame: true
                }});

                // Update stats
                document.getElementById('stat-total').textContent = stats.total;
                document.getElementById('stat-anomalies').textContent = stats.with_anomalies;
                document.getElementById('stat-high').textContent = stats.high_priority;

                // Create catalogs for each category
                createCatalogs();

                // Add sources to catalogs
                addSourcesToMap();
            }});

            function createCatalogs() {{
                // Normal sources catalog
                catalogs.normal = A.catalog({{
                    name: 'Sources normales',
                    sourceSize: 10,
                    color: COLORS.normal,
                    onClick: 'showPopup'
                }});
                aladin.addCatalog(catalogs.normal);

                // Anomaly catalogs by type
                for (const [type, color] of Object.entries(COLORS.types)) {{
                    catalogs[type] = A.catalog({{
                        name: `Anomalies ${{type}}`,
                        sourceSize: 14,
                        color: color,
                        onClick: 'showPopup'
                    }});
                    aladin.addCatalog(catalogs[type]);
                }}

                // High priority overlay (circles)
                catalogs.highPriority = A.catalog({{
                    name: 'Haute priorite',
                    sourceSize: 24,
                    color: '#dc3545',
                    shape: 'circle',
                    onClick: 'showPopup'
                }});
                aladin.addCatalog(catalogs.highPriority);
            }}

            function getSourceColor(source) {{
                if (!source.has_anomaly) return COLORS.normal;

                // Get primary anomaly type
                if (source.anomalies && source.anomalies.length > 0) {{
                    const primaryType = source.anomalies[0].type;
                    return COLORS.types[primaryType] || COLORS.normal;
                }}
                return COLORS.normal;
            }}

            function getPrimarySeverity(source) {{
                if (!source.anomalies || source.anomalies.length === 0) return null;

                // Return highest severity
                const severityOrder = ['high', 'medium', 'low'];
                for (const sev of severityOrder) {{
                    if (source.anomalies.some(a => a.severity === sev)) return sev;
                }}
                return 'low';
            }}

            function buildPopupContent(source) {{
                const hasAnomaly = source.has_anomaly;
                const primaryType = source.anomalies?.[0]?.type || 'normal';
                const borderColor = hasAnomaly ? COLORS.types[primaryType] : COLORS.normal;

                let html = `<div class="anomaly-popup">`;

                // Header
                html += `<h3 style="border-color: ${{borderColor}}">
                    Source ${{source.source_id}}
                    ${{hasAnomaly ? `<span class="score-badge" style="background: ${{borderColor}}; color: white;">Score: ${{source.score.toFixed(0)}}/100</span>` : ''}}
                </h3>`;

                // Properties
                html += `<div class="props">`;
                if (source.g_mag !== null) html += `<div class="prop"><span class="prop-label">G mag:</span> ${{source.g_mag}}</div>`;
                if (source.bp_rp !== null) html += `<div class="prop"><span class="prop-label">BP-RP:</span> ${{source.bp_rp}}</div>`;
                if (source.parallax !== null) html += `<div class="prop"><span class="prop-label">Parallaxe:</span> ${{source.parallax}} mas</div>`;
                html += `<div class="prop"><span class="prop-label">RA:</span> ${{source.ra.toFixed(5)}}°</div>`;
                html += `<div class="prop"><span class="prop-label">Dec:</span> ${{source.dec.toFixed(5)}}°</div>`;
                html += `</div>`;

                // Anomalies list
                if (hasAnomaly && source.anomalies.length > 0) {{
                    html += `<div class="anomaly-list">`;
                    html += `<strong>Anomalies detectees (${{source.anomalies.length}}):</strong>`;

                    for (const anom of source.anomalies) {{
                        html += `<div class="anomaly-item ${{anom.severity}}">
                            <span class="anomaly-type" style="color: ${{COLORS.types[anom.type]}}">${{anom.type}}</span>
                            <span class="sigma">${{anom.sigma.toFixed(1)}}σ</span>
                            <div class="anomaly-desc">${{anom.description}}</div>
                        </div>`;
                    }}
                    html += `</div>`;
                }} else {{
                    html += `<p style="color: #28a745; margin-top: 10px;">✓ Aucune anomalie detectee</p>`;
                }}

                // Actions
                html += `<div style="margin-top: 12px; padding-top: 8px; border-top: 1px solid #ddd; font-size: 10px; color: #666;">
                    <a href="https://simbad.u-strasbg.fr/simbad/sim-coo?Coord=${{source.ra}}+${{source.dec}}&Radius=2&Radius.unit=arcsec"
                       target="_blank" style="color: #3498db;">Voir dans SIMBAD ↗</a>
                </div>`;

                html += `</div>`;
                return html;
            }}

            function addSourcesToMap() {{
                // Clear existing
                for (const cat of Object.values(catalogs)) {{
                    cat.removeAll?.();
                }}

                for (const source of sourcesData) {{
                    // Check filters
                    if (source.has_anomaly) {{
                        const primaryType = source.anomalies?.[0]?.type;
                        const primarySeverity = getPrimarySeverity(source);

                        if (!activeFilters.types.has(primaryType)) continue;
                        if (!activeFilters.severities.has(primarySeverity)) continue;

                        // Add to type-specific catalog
                        if (catalogs[primaryType]) {{
                            const popup = buildPopupContent(source);
                            catalogs[primaryType].addSources([
                                A.source(source.ra, source.dec, {{
                                    name: `Source ${{source.source_id}}`,
                                    popupTitle: `Source ${{source.source_id}}`,
                                    popupDesc: popup
                                }})
                            ]);
                        }}

                        // Add high priority ring overlay
                        if (source.score >= 50) {{
                            catalogs.highPriority.addSources([
                                A.source(source.ra, source.dec, {{
                                    name: `HP-${{source.source_id}}`
                                }})
                            ]);
                        }}
                    }} else {{
                        // Normal source
                        const popup = buildPopupContent(source);
                        catalogs.normal.addSources([
                            A.source(source.ra, source.dec, {{
                                name: `Source ${{source.source_id}}`,
                                popupTitle: `Source ${{source.source_id}}`,
                                popupDesc: popup
                            }})
                        ]);
                    }}
                }}
            }}

            function toggleType(type) {{
                const item = document.querySelector(`.legend-item[data-type="${{type}}"]`);

                if (activeFilters.types.has(type)) {{
                    activeFilters.types.delete(type);
                    item.classList.add('disabled');
                }} else {{
                    activeFilters.types.add(type);
                    item.classList.remove('disabled');
                }}

                addSourcesToMap();
            }}

            function toggleSeverity(severity) {{
                const item = document.querySelector(`.legend-item[data-severity="${{severity}}"]`);

                if (activeFilters.severities.has(severity)) {{
                    activeFilters.severities.delete(severity);
                    item.classList.add('disabled');
                }} else {{
                    activeFilters.severities.add(severity);
                    item.classList.remove('disabled');
                }}

                addSourcesToMap();
            }}
        </script>
    </body>
    </html>
    """

    components.html(html, height=600, scrolling=False)


def render_sky_map(df: pd.DataFrame, center_ra: float = None, center_dec: float = None):
    """Render interactive sky map with Aladin Lite and Plotly."""
    if 'ra' not in df.columns or 'dec' not in df.columns:
        return

    st.subheader("Visualisation du Ciel")

    # Calculate center if not provided
    if center_ra is None:
        center_ra = df['ra'].mean()
    if center_dec is None:
        center_dec = df['dec'].mean()

    # Calculate FOV based on data spread
    ra_spread = df['ra'].max() - df['ra'].min()
    dec_spread = df['dec'].max() - df['dec'].min()
    fov = max(ra_spread, dec_spread) * 1.2
    fov = max(0.1, min(fov, 10))  # Clamp between 0.1 and 10 degrees

    # Visualization mode selection
    viz_mode = st.radio(
        "Mode de visualisation",
        ["Aladin Lite (imagerie)", "Graphique Plotly"],
        horizontal=True
    )

    if viz_mode == "Aladin Lite (imagerie)":
        # Prepare sources for Aladin
        sources = []
        for _, row in df.iterrows():
            if pd.notna(row['ra']) and pd.notna(row['dec']):
                sources.append({
                    'ra': row['ra'],
                    'dec': row['dec'],
                    'name': str(row.get('source_id', 'Source'))
                })

        st.caption(f"Centre: RA={center_ra:.4f}°, Dec={center_dec:.4f}° | FOV={fov:.2f}°")
        render_aladin_viewer(center_ra, center_dec, fov, sources)
        st.caption("🔶 Orange: Resultats de requete | 🔵 Bleu: Gaia DR3 (overlay)")

    else:
        # Plotly scatter plot
        color_col = None
        if 'phot_g_mean_mag' in df.columns:
            color_col = 'phot_g_mean_mag'

        fig = px.scatter(
            df,
            x='ra',
            y='dec',
            color=color_col,
            color_continuous_scale='Viridis_r' if color_col else None,
            hover_data=['source_id'] if 'source_id' in df.columns else None,
            labels={'ra': 'RA (deg)', 'dec': 'Dec (deg)', 'phot_g_mean_mag': 'G mag'},
            title="Distribution spatiale"
        )

        fig.update_layout(
            xaxis_title="Right Ascension (deg)",
            yaxis_title="Declinaison (deg)",
            height=500
        )

        st.plotly_chart(fig, use_container_width=True)


def render_hr_diagram(df: pd.DataFrame):
    """Render HR diagram if data available."""
    if 'bp_rp' not in df.columns or 'phot_g_mean_mag' not in df.columns:
        return

    if 'parallax' not in df.columns:
        return

    st.subheader("Diagramme HR")

    # Filter valid data
    valid = df[
        (df['parallax'] > 0) &
        (df['parallax'].notna()) &
        (df['bp_rp'].notna()) &
        (df['phot_g_mean_mag'].notna())
    ].copy()

    if len(valid) < 10:
        st.info("Pas assez de donnees avec parallaxe valide pour le diagramme HR.")
        return

    # Calculate absolute magnitude
    valid['abs_g'] = valid['phot_g_mean_mag'] + 5 * np.log10(valid['parallax'] / 100)

    fig = px.scatter(
        valid,
        x='bp_rp',
        y='abs_g',
        color='parallax',
        color_continuous_scale='Plasma',
        hover_data=['source_id'],
        labels={
            'bp_rp': 'BP - RP (mag)',
            'abs_g': 'M_G (mag abs)',
            'parallax': 'Parallaxe (mas)'
        }
    )

    fig.update_layout(
        yaxis_autorange='reversed',
        height=500,
        title="Diagramme Hertzsprung-Russell"
    )

    st.plotly_chart(fig, use_container_width=True)


def render_anomaly_dashboard(anomaly_results: Dict[str, Any], df: pd.DataFrame):
    """Render anomaly detection dashboard."""
    st.subheader("Anomalies detectees")

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Sources analysees", anomaly_results['total_sources'])
    with col2:
        st.metric("Avec anomalies", anomaly_results['sources_with_anomalies'])
    with col3:
        st.metric("Taux", f"{anomaly_results['anomaly_rate']:.1f}%")
    with col4:
        st.metric("Total anomalies", anomaly_results['total_anomalies'])

    # Sky visualization with anomalies
    st.subheader("Carte du ciel - Anomalies")

    show_sky_viz = st.checkbox(
        "Afficher la visualisation Aladin Lite",
        value=True,
        help="Carte interactive avec code couleur par type d'anomalie"
    )

    if show_sky_viz and 'ra' in df.columns and 'dec' in df.columns:
        # Calculate center and FOV
        center_ra = df['ra'].mean()
        center_dec = df['dec'].mean()
        ra_spread = df['ra'].max() - df['ra'].min()
        dec_spread = df['dec'].max() - df['dec'].min()
        fov = max(ra_spread, dec_spread) * 1.2
        fov = max(0.1, min(fov, 10))

        st.caption(
            f"Centre: RA={center_ra:.4f}°, Dec={center_dec:.4f}° | "
            f"FOV={fov:.2f}° | Cliquez sur une source pour voir les details"
        )

        render_aladin_anomalies(center_ra, center_dec, fov, df, anomaly_results)

        st.caption(
            "🔴 Photometrique | 🟣 Astrometrique | 🟠 Couleur | "
            "🔵 Cross-match manquant | ⚫ Normal"
        )

    # Distribution by type
    if anomaly_results['by_type']:
        col1, col2 = st.columns(2)

        with col1:
            type_df = pd.DataFrame([
                {'Type': k, 'Count': v}
                for k, v in anomaly_results['by_type'].items()
            ])
            fig = px.bar(type_df, x='Type', y='Count', title="Par type")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            sev_df = pd.DataFrame([
                {'Severite': k, 'Count': v}
                for k, v in anomaly_results['by_severity'].items()
            ])
            colors = {'high': '#d62728', 'medium': '#ff7f0e', 'low': '#bcbd22'}
            fig = px.bar(
                sev_df,
                x='Severite',
                y='Count',
                title="Par severite",
                color='Severite',
                color_discrete_map=colors
            )
            st.plotly_chart(fig, use_container_width=True)

    # Top anomalies
    if anomaly_results['top_anomalies']:
        st.subheader("Top anomalies")

        # Filter controls
        col1, col2 = st.columns(2)
        with col1:
            filter_type = st.selectbox(
                "Filtrer par type",
                ["Tous"] + list(anomaly_results['by_type'].keys())
            )
        with col2:
            filter_severity = st.selectbox(
                "Filtrer par severite",
                ["Tous", "high", "medium", "low"]
            )

        severity_markers = {'high': '[!!!]', 'medium': '[!!]', 'low': '[!]'}

        for i, item in enumerate(anomaly_results['top_anomalies'][:20], 1):
            # Apply filters
            if filter_type != "Tous":
                if not any(a['type'] == filter_type for a in item['anomalies']):
                    continue
            if filter_severity != "Tous":
                if not any(a['severity'] == filter_severity for a in item['anomalies']):
                    continue

            with st.expander(
                f"#{i} Source {item['source_id']} (Score: {item['score']:.0f}/100)",
                expanded=(i <= 3)
            ):
                for anom in item['anomalies']:
                    marker = severity_markers.get(anom['severity'], '[?]')
                    st.write(
                        f"{marker} **{anom['type'].upper()}** ({anom['sigma']:.1f} sigma): {anom['description']}"
                    )

                # Action buttons
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("Ajouter a la selection", key=f"select_{item['source_id']}"):
                        if item['source_id'] not in st.session_state.selected_sources:
                            st.session_state.selected_sources.append(item['source_id'])
                            st.success(f"Source {item['source_id']} ajoutee")

                with col2:
                    # Link to external resources
                    simbad_url = f"https://simbad.u-strasbg.fr/simbad/sim-coo?Coord={df.loc[df['source_id']==item['source_id'], 'ra'].values[0]}+{df.loc[df['source_id']==item['source_id'], 'dec'].values[0]}&Radius=2&Radius.unit=arcsec"
                    st.link_button("Voir dans SIMBAD", simbad_url)

                with col3:
                    if llm_agent.is_llm_available() and len(item['anomalies']) > 0:
                        if st.button("Interpreter", key=f"interpret_{item['source_id']}"):
                            with st.spinner("Analyse LLM en cours..."):
                                interpretation = llm_agent.interpret_anomaly(item['anomalies'][0])
                                st.session_state.interpretations[item['source_id']] = interpretation

                # Show stored interpretation if exists
                if item['source_id'] in st.session_state.interpretations:
                    st.markdown("---")
                    st.markdown("**Interpretation LLM :**")
                    st.markdown(st.session_state.interpretations[item['source_id']])


def render_workflow_tools(df: pd.DataFrame, anomaly_results: Optional[Dict] = None):
    """Render workflow improvement tools."""
    st.subheader("Outils de workflow")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Export des donnees**")

        # Export formats
        export_format = st.selectbox(
            "Format d'export",
            ["CSV", "JSON", "VOTable (IVOA)"]
        )

        export_anomalies_only = st.checkbox("Exporter uniquement les anomalies", value=False)

        if export_anomalies_only and anomaly_results:
            anomaly_ids = [a['source_id'] for a in anomaly_results['top_anomalies']]
            export_df = df[df['source_id'].isin(anomaly_ids)]
        else:
            export_df = df

        if export_format == "CSV":
            csv = export_df.to_csv(index=False)
            st.download_button(
                "Telecharger CSV",
                csv,
                f"cosmic_query_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "text/csv"
            )
        elif export_format == "JSON":
            json_data = export_df.to_json(orient='records', indent=2)
            st.download_button(
                "Telecharger JSON",
                json_data,
                f"cosmic_query_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                "application/json"
            )
        elif export_format == "VOTable (IVOA)":
            st.info("Export VOTable: utilisez TOPCAT pour conversion avancee")
            csv = export_df.to_csv(index=False)
            st.download_button(
                "Telecharger CSV (compatible TOPCAT)",
                csv,
                f"cosmic_query_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "text/csv"
            )

    with col2:
        st.markdown("**Selection de sources**")

        if st.session_state.selected_sources:
            st.write(f"{len(st.session_state.selected_sources)} source(s) selectionnee(s)")

            # Show selected
            for sid in st.session_state.selected_sources[:10]:
                st.code(str(sid))

            if len(st.session_state.selected_sources) > 10:
                st.caption(f"... et {len(st.session_state.selected_sources) - 10} autres")

            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("Exporter selection"):
                    selected_df = df[df['source_id'].isin(st.session_state.selected_sources)]
                    csv = selected_df.to_csv(index=False)
                    st.download_button(
                        "Telecharger",
                        csv,
                        "selection.csv",
                        "text/csv"
                    )
            with col_b:
                if st.button("Vider selection"):
                    st.session_state.selected_sources = []
                    st.rerun()
        else:
            st.info("Aucune source selectionnee. Utilisez l'onglet Anomalies pour ajouter des sources.")

    # Query history
    st.markdown("**Historique des requetes**")
    if st.session_state.query_history:
        for i, query in enumerate(st.session_state.query_history[-5:][::-1], 1):
            st.text(f"{i}. {query['timestamp']} - {query['description']}")
    else:
        st.info("Aucune requete dans l'historique")


def render_synthesis(query: str, data_summary: Dict, anomalies: Optional[Dict] = None):
    """Render LLM synthesis."""
    if not llm_agent.is_llm_available():
        st.info("Configurez un LLM (local ou OpenAI) pour activer la synthese automatique")
        return

    st.subheader("Synthese")

    if st.button("Generer la synthese"):
        with st.spinner("Analyse en cours..."):
            synthesis = llm_agent.synthesize_results(query, data_summary, anomalies)
            st.markdown(synthesis)


# ============================================
# STM (Space Traffic Management) Functions
# ============================================

def render_stm_sidebar():
    """Render STM sidebar configuration."""
    with st.sidebar:
        st.subheader("Launch Risk Assessment")
        st.caption("Outil pour operateurs de lancement")

        st.divider()

        # Data sources status
        st.markdown("**Sources de donnees**")

        # Space-Track
        if spacetrack_client.is_spacetrack_available():
            cache_info = spacetrack_client.get_cache_info()
            if cache_info.get('exists'):
                st.success(f"Space-Track: {cache_info.get('object_count', 0)} obj")
                st.caption(f"Cache: {cache_info.get('age_hours', 0):.1f}h")
            else:
                st.info("Space-Track: OK (cache vide)")
        else:
            st.warning("Space-Track: non configure")

        # Celestrak (always available)
        st.success("Celestrak: disponible")

        st.divider()

        # Category selection for catalog tab
        categories = stm_data.get_tle_categories()
        category = st.selectbox(
            "Categorie (Catalogue)",
            list(categories.keys()),
            format_func=lambda x: f"{x} - {categories[x]}"
        )

        limit = st.slider("Objets max (Globe)", 50, 500, 200)

        st.divider()

        # Quick stats if catalog loaded
        if st.session_state.get('space_catalog'):
            catalog = st.session_state.space_catalog
            st.markdown("**Catalogue charge**")

            debris = sum(1 for o in catalog if o.get('object_type') == 'DEBRIS')
            sats = sum(1 for o in catalog if o.get('object_type') == 'PAYLOAD')
            rockets = sum(1 for o in catalog if o.get('object_type') == 'ROCKET BODY')
            from_spacetrack = sum(1 for o in catalog if o.get('source') == 'Space-Track')
            from_celestrak = sum(1 for o in catalog if o.get('source') == 'Celestrak')

            st.metric("Total", len(catalog))
            col1, col2 = st.columns(2)
            col1.metric("Debris", debris)
            col2.metric("Satellites", sats)

            st.caption(f"Sources: Space-Track ({from_spacetrack}) + Celestrak ({from_celestrak})")

        return {
            'category': category,
            'limit': limit,
            'prop_hours': 6  # Keep for compatibility
        }


def render_stm_data_tab(stm_params: Dict):
    """Render STM data collection tab."""
    st.subheader("Donnees Satellites (TLE)")

    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("Telecharger TLE", type="primary"):
            with st.spinner(f"Telechargement {stm_params['category']}..."):
                satellites = stm_data.fetch_tle_celestrak(
                    stm_params['category'],
                    stm_params['limit']
                )
                if satellites:
                    st.session_state.stm_satellites = satellites
                    st.success(f"{len(satellites)} satellites charges!")
                else:
                    st.error("Erreur de telechargement")

    with col2:
        if st.session_state.stm_satellites:
            st.info(f"{len(st.session_state.stm_satellites)} satellites en memoire")

    # Display satellites
    if st.session_state.stm_satellites:
        df = stm_data.satellites_to_dataframe(st.session_state.stm_satellites)

        st.divider()

        # Add orbit info
        orbit_info = []
        for sat in st.session_state.stm_satellites:
            info = stm_propagator.get_orbit_info(sat.tle_line1, sat.tle_line2)
            orbit_info.append({
                'norad_id': sat.norad_id,
                'orbit_type': info.get('orbit_type', 'N/A'),
                'altitude_km': info.get('altitude_km_approx', 0),
                'period_min': info.get('period_minutes', 0),
                'inclination': info.get('inclination_deg', 0)
            })

        orbit_df = pd.DataFrame(orbit_info)
        display_df = df[['name', 'norad_id']].merge(orbit_df, on='norad_id')

        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total", len(display_df))
        col2.metric("LEO", len(display_df[display_df['orbit_type'] == 'LEO']))
        col3.metric("MEO", len(display_df[display_df['orbit_type'] == 'MEO']))
        col4.metric("GEO", len(display_df[display_df['orbit_type'] == 'GEO']))

        st.dataframe(
            display_df,
            use_container_width=True,
            height=400
        )


def render_stm_tracking_tab(stm_params: Dict):
    """Render satellite tracking tab."""
    st.subheader("Suivi en Temps Reel")

    if not st.session_state.stm_satellites:
        st.warning("Chargez d'abord des satellites (onglet Donnees)")
        return

    # Satellite selection
    sat_options = {s.norad_id: s.name for s in st.session_state.stm_satellites}
    selected_id = st.selectbox(
        "Satellite",
        list(sat_options.keys()),
        format_func=lambda x: f"{sat_options[x]} (NORAD: {x})"
    )

    if selected_id:
        sat = stm_data.get_satellite_by_norad(selected_id, st.session_state.stm_satellites)
        st.session_state.stm_selected_sat = sat

        if sat:
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Position Actuelle**")
                if st.button("Rafraichir Position"):
                    pass  # Will refresh below

                pos = stm_propagator.get_current_position(
                    sat.tle_line1, sat.tle_line2, sat.name
                )

                st.metric("Latitude", f"{pos['lat']:.2f} deg")
                st.metric("Longitude", f"{pos['lon']:.2f} deg")
                st.metric("Altitude", f"{pos['alt_km']:.0f} km")
                st.metric("Vitesse", f"{pos['velocity_km_s']:.2f} km/s")

            with col2:
                st.markdown("**Parametres Orbitaux**")
                orbit = stm_propagator.get_orbit_info(sat.tle_line1, sat.tle_line2)

                st.metric("Type d'orbite", orbit.get('orbit_type', 'N/A'))
                st.metric("Periode", f"{orbit.get('period_minutes', 0):.1f} min")
                st.metric("Inclinaison", f"{orbit.get('inclination_deg', 0):.1f} deg")
                st.metric("Excentricite", f"{orbit.get('eccentricity', 0):.4f}")


def render_stm_propagation_tab(stm_params: Dict):
    """Render orbit propagation tab."""
    st.subheader("Propagation d'Orbite")

    if not st.session_state.stm_selected_sat:
        st.warning("Selectionnez un satellite (onglet Suivi)")
        return

    sat = st.session_state.stm_selected_sat

    st.info(f"Satellite: **{sat.name}** (NORAD: {sat.norad_id})")

    if st.button("Calculer Trajectoire", type="primary"):
        with st.spinner(f"Propagation sur {stm_params['prop_hours']}h..."):
            df = stm_propagator.propagate_orbit(
                sat.tle_line1,
                sat.tle_line2,
                sat.name,
                hours_ahead=stm_params['prop_hours'],
                step_minutes=5
            )
            st.session_state.stm_trajectory = df
            st.success(f"{len(df)} points calcules!")

    if st.session_state.stm_trajectory is not None:
        df = st.session_state.stm_trajectory

        st.divider()

        # Ground track map
        st.markdown("### Trace au Sol")
        import plotly.express as px

        fig = px.scatter_geo(
            df,
            lat='lat',
            lon='lon',
            color='alt_km',
            hover_data=['time', 'velocity_km_s'],
            title=f"Trajectoire - {sat.name}",
            color_continuous_scale='Viridis'
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

        # Altitude profile
        col1, col2 = st.columns(2)

        with col1:
            fig = px.line(df, x='time', y='alt_km', title="Altitude vs Temps")
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = px.line(df, x='time', y='velocity_km_s', title="Vitesse vs Temps")
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)

        # Data table
        with st.expander("Donnees brutes"):
            st.dataframe(df, use_container_width=True)


def render_stm_globe_tab(stm_params: Dict):
    """Render 3D Globe visualization with CesiumJS."""
    st.subheader("Globe 3D - Visualisation Temps Reel")

    # Data source selection
    col1, col2, col3 = st.columns(3)

    with col1:
        data_source = st.radio(
            "Source de donnees",
            ["Celestrak", "Space-Track.org", "Les deux"],
            help="Celestrak: satellites actifs. Space-Track: + debris (compte requis)"
        )

    with col2:
        if data_source in ["Space-Track.org", "Les deux"]:
            object_type = st.selectbox(
                "Type d'objets (Space-Track)",
                ["DEBRIS", "ROCKET BODY", "PAYLOAD", "ALL"],
                help="DEBRIS: debris spatiaux, ROCKET BODY: corps de fusees"
            )
        else:
            object_type = None

    with col3:
        max_objects = st.slider("Nombre max d'objets", 50, 1000, 200)

    st.divider()

    # Check Space-Track availability
    spacetrack_available = spacetrack_client.is_spacetrack_available()

    if data_source in ["Space-Track.org", "Les deux"] and not spacetrack_available:
        st.warning(
            "Space-Track.org necessite un compte gratuit. "
            "Ajoutez SPACETRACK_USER et SPACETRACK_PASSWORD dans .env\n\n"
            "Inscription: https://www.space-track.org/auth/createAccount"
        )

    # Load data button
    col1, col2 = st.columns([1, 3])

    with col1:
        load_clicked = st.button("Charger les donnees", type="primary")

    if load_clicked:
        all_objects = []

        # Fetch from Celestrak
        if data_source in ["Celestrak", "Les deux"]:
            with st.spinner("Chargement Celestrak..."):
                celestrak_sats = stm_data.fetch_tle_celestrak(
                    stm_params.get('category', 'active'),
                    min(max_objects, 500)
                )
                if celestrak_sats:
                    st.success(f"Celestrak: {len(celestrak_sats)} satellites")

                    # Compute positions
                    for sat in celestrak_sats:
                        try:
                            pos = stm_propagator.get_current_position(
                                sat.tle_line1, sat.tle_line2, sat.name
                            )
                            all_objects.append({
                                'name': sat.name,
                                'norad_id': sat.norad_id,
                                'object_type': 'PAYLOAD',
                                'country': '',
                                'lat': pos['lat'],
                                'lon': pos['lon'],
                                'alt_km': pos['alt_km']
                            })
                        except Exception:
                            continue

        # Fetch from Space-Track
        if data_source in ["Space-Track.org", "Les deux"] and spacetrack_available:
            with st.spinner("Chargement Space-Track (debris)..."):
                client = spacetrack_client.get_client()

                if object_type == "ALL":
                    spacetrack_objects = client.fetch_all_objects(max_objects // 3)
                else:
                    spacetrack_objects = client.fetch_tle_by_type(
                        object_type, max_objects
                    )

                if spacetrack_objects:
                    st.success(f"Space-Track: {len(spacetrack_objects)} objets")

                    # Compute positions
                    for obj in spacetrack_objects:
                        try:
                            pos = stm_propagator.get_current_position(
                                obj.tle_line1, obj.tle_line2, obj.name
                            )
                            all_objects.append({
                                'name': obj.name,
                                'norad_id': obj.norad_id,
                                'object_type': obj.object_type,
                                'country': obj.country,
                                'lat': pos['lat'],
                                'lon': pos['lon'],
                                'alt_km': pos['alt_km']
                            })
                        except Exception:
                            continue

        if all_objects:
            st.session_state.globe_satellites = all_objects
            st.success(f"Total: {len(all_objects)} objets prets pour visualisation")
        else:
            st.error("Aucune donnee chargee")

    st.divider()

    # Get objects (may be None or empty)
    objects = st.session_state.globe_satellites or []

    # Statistics
    col1, col2, col3, col4 = st.columns(4)

    payload_count = sum(1 for o in objects if o.get('object_type') == 'PAYLOAD')
    debris_count = sum(1 for o in objects if o.get('object_type') == 'DEBRIS')
    rocket_count = sum(1 for o in objects if o.get('object_type') == 'ROCKET BODY')

    col1.metric("Total Objets", len(objects))
    col2.metric("Satellites", payload_count)
    col3.metric("Debris", debris_count)
    col4.metric("Corps Fusees", rocket_count)

    st.divider()

    # Visualization options
    col1, col2 = st.columns(2)
    with col1:
        show_labels = st.checkbox("Afficher les noms", value=False)
    with col2:
        show_orbits = st.checkbox("Afficher les orbites", value=True)

    # Render CesiumJS globe (always show, even without data)
    st.markdown("### Globe 3D Interactif")
    if not objects:
        st.info("Cliquez sur 'Charger les donnees' pour afficher les satellites et debris.")
    else:
        st.caption("Utilisez la souris pour naviguer. Cliquez sur un objet pour plus d'infos.")

    cesium_viewer.render_cesium_globe(
        satellites=objects,
        height=config.CESIUM_DEFAULT_HEIGHT,
        show_labels=show_labels,
        show_orbits=show_orbits
    )

    # Data export (only if we have data)
    if objects:
        with st.expander("Donnees brutes"):
            df = pd.DataFrame(objects)
            st.dataframe(df, use_container_width=True)

            csv = df.to_csv(index=False)
            st.download_button(
                "Telecharger CSV",
                csv,
                f"space_objects_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "text/csv"
            )


def render_risk_assessment_tab(stm_params: Dict):
    """Render launch risk assessment tab."""
    st.subheader("Evaluation des Risques de Lancement")
    st.markdown(
        "Analysez les risques de collision et evaluez la probabilite de succes "
        "pour votre lancement de satellite."
    )

    st.divider()

    # Launch parameters input
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Parametres de lancement")

        # Launch site selection
        sites = launch_risk.get_launch_sites()
        site_names = list(sites.keys())
        selected_site = st.selectbox(
            "Site de lancement",
            site_names,
            index=0,
            help="Selectionnez le site de lancement"
        )

        # Show site info
        site_info = sites[selected_site]
        st.caption(f"📍 {site_info['country']} | Lat: {site_info['lat']:.2f}° | Lon: {site_info['lon']:.2f}°")

        # Target orbit selection
        orbits = launch_risk.get_target_orbits()
        orbit_names = list(orbits.keys())
        selected_orbit = st.selectbox(
            "Orbite cible",
            orbit_names,
            index=0,
            help="Selectionnez l'orbite de destination"
        )

        # Show orbit info
        orbit_info = orbits[selected_orbit]
        st.caption(f"🛰️ Altitude: {orbit_info['alt_min']}-{orbit_info['alt_max']} km | Inclinaison: {orbit_info['typical_inc']}°")

    with col2:
        st.markdown("### Date et heure")

        # Launch date
        launch_date = st.date_input(
            "Date de lancement",
            value=datetime.now().date(),
            min_value=datetime.now().date()
        )

        # Launch time
        launch_time = st.time_input(
            "Heure de lancement (UTC)",
            value=datetime.now().time()
        )

        # Combine date and time
        launch_datetime = datetime.combine(launch_date, launch_time)
        launch_datetime = launch_datetime.replace(tzinfo=timezone.utc)

        st.markdown("### Options")

        # Data source for risk calculation
        use_cache = st.checkbox(
            "Utiliser le cache Space-Track",
            value=True,
            help="Utilise les donnees en cache si disponibles (recommande)"
        )

    st.divider()

    # Analysis buttons
    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        analyze_clicked = st.button(
            "🚀 Analyser les Risques",
            type="primary",
            use_container_width=True
        )

    with col2:
        refresh_data = st.button(
            "🔄 Actualiser le Catalogue Spatial",
            use_container_width=True,
            help="Telecharge Space-Track (debris) + Celestrak (satellites actifs)"
        )

    def load_combined_catalog(force_refresh: bool = False, max_objects: int = 500) -> list:
        """Load space catalog from both Space-Track and Celestrak."""
        all_positioned = []
        seen_norad_ids = set()

        # 1. Space-Track (debris + all objects)
        st.write("📡 Chargement Space-Track (debris, corps fusees)...")
        spacetrack_objects = spacetrack_client.get_space_objects(force_refresh=force_refresh)

        if spacetrack_objects:
            progress = st.progress(0, text="Space-Track...")
            limit = min(len(spacetrack_objects), max_objects // 2)
            for i, obj in enumerate(spacetrack_objects[:limit]):
                try:
                    pos = stm_propagator.get_current_position(
                        obj.tle_line1, obj.tle_line2, obj.name
                    )
                    all_positioned.append({
                        'name': obj.name,
                        'norad_id': obj.norad_id,
                        'object_type': obj.object_type,
                        'country': obj.country,
                        'lat': pos['lat'],
                        'lon': pos['lon'],
                        'alt_km': pos['alt_km'],
                        'source': 'Space-Track'
                    })
                    seen_norad_ids.add(obj.norad_id)
                except (ValueError, RuntimeError, KeyError):
                    continue
                progress.progress((i + 1) / limit)
            st.write(f"  ✓ {len(all_positioned)} objets Space-Track")

        # 2. Celestrak (active satellites)
        st.write("🛰️ Chargement Celestrak (satellites actifs)...")
        celestrak_sats = stm_data.fetch_tle_celestrak('active', max_objects // 2)

        if celestrak_sats:
            progress = st.progress(0, text="Celestrak...")
            added = 0
            for i, sat in enumerate(celestrak_sats):
                # Skip if already from Space-Track
                if sat.norad_id in seen_norad_ids:
                    continue
                try:
                    pos = stm_propagator.get_current_position(
                        sat.tle_line1, sat.tle_line2, sat.name
                    )
                    all_positioned.append({
                        'name': sat.name,
                        'norad_id': sat.norad_id,
                        'object_type': 'PAYLOAD',
                        'country': '',
                        'lat': pos['lat'],
                        'lon': pos['lon'],
                        'alt_km': pos['alt_km'],
                        'source': 'Celestrak'
                    })
                    added += 1
                except (ValueError, RuntimeError, KeyError):
                    continue
                progress.progress((i + 1) / len(celestrak_sats))
            st.write(f"  ✓ {added} satellites Celestrak ajoutes")

        return all_positioned

    # Load/refresh space catalog
    if refresh_data:
        with st.spinner("Telechargement du catalogue spatial complet..."):
            positioned_objects = load_combined_catalog(force_refresh=True, max_objects=600)

            if positioned_objects:
                st.session_state.space_catalog = positioned_objects
                st.session_state.globe_satellites = positioned_objects

                # Count by source
                spacetrack_count = sum(1 for o in positioned_objects if o.get('source') == 'Space-Track')
                celestrak_count = sum(1 for o in positioned_objects if o.get('source') == 'Celestrak')
                debris_count = sum(1 for o in positioned_objects if o.get('object_type') == 'DEBRIS')

                st.success(
                    f"Catalogue actualise: {len(positioned_objects)} objets\n"
                    f"- Space-Track: {spacetrack_count} (dont {debris_count} debris)\n"
                    f"- Celestrak: {celestrak_count} satellites"
                )
            else:
                st.error("Erreur lors du telechargement")

    # Perform risk analysis
    if analyze_clicked:
        # Load catalog if not already loaded
        if not st.session_state.space_catalog:
            with st.spinner("Chargement du catalogue spatial (Space-Track + Celestrak)..."):
                positioned_objects = load_combined_catalog(force_refresh=not use_cache, max_objects=600)

                if positioned_objects:
                    st.session_state.space_catalog = positioned_objects
                    st.session_state.globe_satellites = positioned_objects

        if st.session_state.space_catalog:
            with st.spinner("Analyse des risques en cours..."):
                assessment = launch_risk.assess_launch_risk(
                    launch_site=selected_site,
                    target_orbit=selected_orbit,
                    launch_datetime=launch_datetime,
                    space_objects=st.session_state.space_catalog
                )

                launch_params = {
                    'site': selected_site,
                    'orbit': selected_orbit,
                    'datetime': launch_datetime.isoformat()
                }

                report = launch_risk.generate_risk_report_markdown(assessment, launch_params)

                st.session_state.risk_assessment = assessment
                st.session_state.risk_report = report

            st.success("Analyse terminee!")
        else:
            st.error("Impossible de charger le catalogue spatial. Verifiez les credentials Space-Track.")

    # Display results if available
    if st.session_state.risk_assessment:
        assessment = st.session_state.risk_assessment

        st.divider()

        # Risk score cards
        st.markdown("### Resultats de l'Analyse")

        col1, col2, col3, col4 = st.columns(4)

        # Risk score with color
        risk_score = assessment.overall_risk_score
        if risk_score < 20:
            risk_color = "green"
            risk_label = "FAIBLE"
        elif risk_score < 40:
            risk_color = "orange"
            risk_label = "MODERE"
        elif risk_score < 60:
            risk_color = "orange"
            risk_label = "ELEVE"
        else:
            risk_color = "red"
            risk_label = "CRITIQUE"

        col1.metric(
            "Score de Risque",
            f"{risk_score}/100",
            risk_label,
            delta_color="inverse"
        )

        col2.metric(
            "Probabilite de Succes",
            f"{assessment.success_probability}%"
        )

        col3.metric(
            "Risque de Collision",
            f"{assessment.collision_risk:.3f}%"
        )

        col4.metric(
            "Evenements de Conjonction",
            assessment.conjunction_events
        )

        st.divider()

        # Detailed analysis in tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Facteurs de Risque",
            "⚠️ Objets a Risque",
            "🕐 Fenetres Optimales",
            "📄 Rapport Complet"
        ])

        with tab1:
            st.markdown("#### Decomposition des Facteurs de Risque")

            for factor, value in assessment.risk_factors.items():
                factor_name = factor.replace('_', ' ').title()
                st.progress(value / 30, text=f"{factor_name}: {value:.1f}/30")

            st.markdown("#### Recommandations")
            for i, rec in enumerate(assessment.recommendations, 1):
                st.info(f"{i}. {rec}")

        with tab2:
            if assessment.high_risk_objects:
                st.markdown("#### Objets Presentant un Risque de Collision")

                risk_df = pd.DataFrame(assessment.high_risk_objects)
                st.dataframe(
                    risk_df[['object_name', 'object_type', 'distance_km', 'risk_level']],
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.success("Aucun objet a risque detecte dans la trajectoire de lancement.")

        with tab3:
            st.markdown("#### Fenetres de Lancement Recommandees")

            for i, window in enumerate(assessment.optimal_windows, 1):
                window_time = window['window_start'][:16].replace('T', ' ')
                risk = window['risk_score']
                status = "✅ Optimal" if window['recommendation'] == 'optimal' else "☑️ Acceptable"

                col1, col2, col3 = st.columns([3, 1, 1])
                col1.write(f"**Fenetre {i}:** {window_time} UTC")
                col2.write(f"Risque: {risk}/100")
                col3.write(status)

        with tab4:
            if st.session_state.risk_report:
                st.markdown(st.session_state.risk_report)

                # Download button for report
                st.download_button(
                    "📥 Telecharger le Rapport",
                    st.session_state.risk_report,
                    f"launch_risk_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                    "text/markdown"
                )


def render_stm_section(stm_params: Dict):
    """Render full STM section."""
    st.title("Launch Risk Assessment")
    st.markdown(
        "**Plateforme d'evaluation des risques pour les lancements spatiaux** | "
        "Analyse de collision, densite de debris, et recommandations de fenetres de lancement."
    )

    st.divider()

    tab1, tab2, tab3 = st.tabs([
        "🚀 Evaluation des Risques",
        "🌍 Globe 3D",
        "📡 Catalogue Spatial"
    ])

    with tab1:
        render_risk_assessment_tab(stm_params)

    with tab2:
        render_stm_globe_tab(stm_params)

    with tab3:
        render_stm_data_tab(stm_params)


# ============================================
# Cosmic Queries Functions (existing)
# ============================================

def execute_query(params: Dict, query_type: str, **kwargs) -> Optional[pd.DataFrame]:
    """Execute astronomical query based on parameters."""
    try:
        ra = kwargs.get('ra')
        dec = kwargs.get('dec')
        radius = params['radius']
        limit = params['limit']

        with st.spinner("Interrogation des catalogues..."):
            if params['use_2mass'] and params['use_sdss']:
                df = astro_queries.query_gaia_full_crossmatch(ra, dec, radius, limit)
            elif params['use_2mass']:
                df = astro_queries.query_gaia_crossmatch_2mass(ra, dec, radius, limit)
            elif params['use_sdss']:
                df = astro_queries.query_gaia_crossmatch_sdss(ra, dec, radius, limit)
            else:
                df = astro_queries.query_gaia_region(ra, dec, radius, limit)

        # Add to history
        st.session_state.query_history.append({
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'description': f"RA={ra:.2f}, Dec={dec:.2f}, r={radius}",
            'ra': ra,
            'dec': dec,
            'radius': radius
        })

        return df

    except Exception as e:
        st.error(f"Erreur lors de la requete : {e}")
        return None


def main():
    """Main application."""
    init_session_state()

    # Sidebar
    params = render_sidebar()

    # Check if STM mode
    if st.session_state.app_mode == 'stm':
        render_stm_section(params)
        # Footer
        st.divider()
        st.caption(
            "Launch Risk Assessment - ActInSpace 2025 | "
            "Donnees: Space-Track.org + Celestrak | "
            "Pour operateurs de lancement (ArianeGroup, SpaceX, RocketLab...)"
        )
        return

    # Main content - Cosmic Queries
    st.title("Cosmic Query Agent")
    st.markdown(
        "Explorez l'univers en interrogeant plusieurs catalogues astronomiques "
        "et detectez automatiquement les incoherences entre les sources."
    )

    st.divider()

    # Show current mode
    st.markdown(f"**Mode actuel :** {params['mode']} *(changez dans la barre laterale)*")

    # Input based on mode
    ra, dec = None, None
    query_text = ""

    if params['mode'] == "Coordonnees":
        ra, dec = render_coordinate_input()
        query_text = f"Recherche autour de RA={ra}, Dec={dec}"

    elif params['mode'] == "Nom d'objet":
        obj_name = render_object_input()
        if obj_name:
            with st.spinner(f"Resolution de {obj_name}..."):
                coords = astro_queries.resolve_object_name(obj_name)
                if coords:
                    ra, dec = coords['ra'], coords['dec']
                    st.success(f"{obj_name} -> RA={ra:.4f} deg, Dec={dec:.4f} deg")
                    query_text = f"Recherche autour de {obj_name}"
                else:
                    st.error(f"Impossible de resoudre '{obj_name}'")

    elif params['mode'] == "Langage naturel":
        nl_query = render_natural_language_input()
        if nl_query:
            query_text = nl_query
            intent = llm_agent.parse_user_intent(nl_query)
            st.json(intent)

            if intent.get('object_name'):
                coords = astro_queries.resolve_object_name(intent['object_name'])
                if coords:
                    ra, dec = coords['ra'], coords['dec']
                    st.success(f"{intent['object_name']} -> RA={ra:.4f} deg, Dec={dec:.4f} deg")
            elif intent.get('ra') and intent.get('dec'):
                ra, dec = intent['ra'], intent['dec']

    # Execute button
    st.divider()
    st.subheader("Lancer la recherche")

    col1, col2 = st.columns([1, 4])
    with col1:
        search_clicked = st.button("Rechercher", type="primary", use_container_width=True)
    with col2:
        if ra is not None and dec is not None:
            st.info(f"Cible : RA={ra:.4f}, Dec={dec:.4f}, Rayon={params['radius']} deg")

    # Execute search if button clicked
    if search_clicked and ra is not None and dec is not None:
        df = execute_query(params, "search", ra=ra, dec=dec)

        if df is not None and len(df) > 0:
            st.session_state.query_results = df
            st.session_state.last_query = query_text
            st.session_state.query_ra = ra
            st.session_state.query_dec = dec

            if params['detect_anomalies']:
                with st.spinner("Detection des anomalies..."):
                    # Pass thresholds as parameters (thread-safe)
                    st.session_state.anomaly_results = anomaly_detector.analyze_crossmatch_data(
                        df,
                        photometric_sigma=st.session_state.detection_params['photometric_sigma'],
                        astrometric_sigma=st.session_state.detection_params['astrometric_sigma'],
                        color_delta=st.session_state.detection_params['color_delta']
                    )
        elif df is not None:
            st.warning("Aucune source trouvee dans cette region.")

    elif search_clicked:
        st.warning("Veuillez specifier des coordonnees valides.")

    # Always show results if we have data in session_state
    if st.session_state.query_results is not None and len(st.session_state.query_results) > 0:
        df = st.session_state.query_results
        anomaly_results = st.session_state.anomaly_results
        query_text = st.session_state.last_query or "Recherche"

        data_summary = compute_data_summary(df)

        st.divider()
        st.success(f"Resultats: {len(df)} sources chargees")

        # Tabs for different views
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Donnees",
            "Visualisation",
            "Anomalies",
            "Reglages",
            "Workflow"
        ])

        with tab1:
            render_results_table(df)

        with tab2:
            render_sky_map(
                df,
                center_ra=st.session_state.query_ra,
                center_dec=st.session_state.query_dec
            )
            render_hr_diagram(df)

        with tab3:
            if anomaly_results:
                render_anomaly_dashboard(anomaly_results, df)
            else:
                st.info("Detection d'anomalies desactivee")

        with tab4:
            detection_params = render_detection_settings()
            st.info("Modifiez les seuils puis relancez la recherche pour appliquer")

        with tab5:
            render_workflow_tools(df, anomaly_results)
            render_synthesis(query_text, data_summary, anomaly_results)

    # Footer
    st.divider()
    st.caption(
        "Cosmic Query Agent - ActInSpace 2025 | "
        "Donnees : Gaia DR3, 2MASS, SDSS via VizieR (CDS Strasbourg)"
    )


if __name__ == "__main__":
    main()