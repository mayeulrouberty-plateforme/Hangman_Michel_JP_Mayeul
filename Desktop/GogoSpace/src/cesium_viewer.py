"""
CesiumJS 3D Globe Viewer for Streamlit
Renders satellites and debris on an interactive 3D globe
"""
import streamlit.components.v1 as components
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, timezone
import json
import os

# Cesium Ion token (free tier available at https://cesium.com/ion/)
# Get your own free token at: https://cesium.com/ion/tokens
CESIUM_ION_TOKEN = os.getenv("CESIUM_ION_TOKEN", "")

# Empty token = use basic globe without Cesium Ion terrain
# To get high-res terrain, register at cesium.com/ion and add token to .env
DEFAULT_TOKEN = ""


def generate_czml_from_satellites(satellites: List[Dict], hours_ahead: int = 6) -> str:
    """
    Generate CZML document from satellite data.

    CZML is Cesium's native format for time-dynamic 3D visualization.
    """
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    end_time = now + timedelta(hours=hours_ahead)

    # CZML document header
    czml = [{
        "id": "document",
        "name": "Satellites",
        "version": "1.0",
        "clock": {
            "interval": f"{now.isoformat()}Z/{end_time.isoformat()}Z",
            "currentTime": f"{now.isoformat()}Z",
            "multiplier": 60,
            "range": "LOOP_STOP",
            "step": "SYSTEM_CLOCK_MULTIPLIER"
        }
    }]

    # Color mapping by object type
    colors = {
        'PAYLOAD': [0, 255, 100, 255],      # Green
        'ROCKET BODY': [255, 165, 0, 255],  # Orange
        'DEBRIS': [255, 50, 50, 255],       # Red
        'UNKNOWN': [128, 128, 128, 255],    # Gray
        'satellite': [0, 150, 255, 255]     # Blue (Celestrak)
    }

    for sat in satellites:
        obj_type = sat.get('object_type', 'satellite')
        color = colors.get(obj_type, colors['UNKNOWN'])

        # Point size based on type
        point_size = 8 if obj_type == 'PAYLOAD' else 5 if obj_type == 'DEBRIS' else 6

        czml.append({
            "id": f"sat_{sat['norad_id']}",
            "name": sat['name'],
            "description": f"""
                <p><b>NORAD ID:</b> {sat['norad_id']}</p>
                <p><b>Type:</b> {obj_type}</p>
                <p><b>Country:</b> {sat.get('country', 'N/A')}</p>
            """,
            "point": {
                "pixelSize": point_size,
                "color": {"rgba": color},
                "outlineColor": {"rgba": [255, 255, 255, 200]},
                "outlineWidth": 1
            },
            "position": {
                "interpolationAlgorithm": "LAGRANGE",
                "interpolationDegree": 5,
                "referenceFrame": "INERTIAL",
                "epoch": f"{now.isoformat()}Z",
                "cartographicDegrees": sat.get('trajectory', [])
            },
            "path": {
                "show": [{"boolean": True}],
                "width": 1,
                "material": {
                    "solidColor": {
                        "color": {"rgba": [color[0], color[1], color[2], 100]}
                    }
                },
                "resolution": 120,
                "leadTime": 3600,
                "trailTime": 3600
            }
        })

    return json.dumps(czml)


def generate_cesium_html(
    satellites_json: str,
    height: int = 700,
    show_labels: bool = True,
    show_orbits: bool = True,
    cesium_token: str = None
) -> str:
    """
    Generate complete HTML page with CesiumJS viewer.
    """
    token = cesium_token or CESIUM_ION_TOKEN or DEFAULT_TOKEN
    has_token = bool(token)

    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <script src="https://cesium.com/downloads/cesiumjs/releases/1.124/Build/Cesium/Cesium.js"></script>
        <link href="https://cesium.com/downloads/cesiumjs/releases/1.124/Build/Cesium/Widgets/widgets.css" rel="stylesheet">
        <style>
            * {{
                box-sizing: border-box;
            }}
            html, body {{
                width: 100%;
                height: 100%;
                margin: 0;
                padding: 0;
                overflow: hidden;
                font-family: sans-serif;
            }}
            #cesiumContainer {{
                width: 100%;
                height: {height}px;
                position: relative;
            }}
            #toolbar {{
                position: absolute;
                top: 10px;
                left: 10px;
                z-index: 1000;
                background: rgba(42, 42, 42, 0.9);
                padding: 10px;
                border-radius: 5px;
                color: white;
                font-size: 12px;
            }}
            #stats {{
                position: absolute;
                top: 10px;
                right: 10px;
                z-index: 1000;
                background: rgba(42, 42, 42, 0.9);
                padding: 10px;
                border-radius: 5px;
                color: white;
                font-size: 12px;
            }}
            .legend {{
                margin-top: 10px;
            }}
            .legend-item {{
                display: flex;
                align-items: center;
                margin: 3px 0;
            }}
            .legend-color {{
                width: 12px;
                height: 12px;
                margin-right: 8px;
                border-radius: 50%;
            }}
            button {{
                background: #3b82f6;
                color: white;
                border: none;
                padding: 5px 10px;
                margin: 2px;
                border-radius: 3px;
                cursor: pointer;
            }}
            button:hover {{
                background: #2563eb;
            }}
        </style>
    </head>
    <body>
        <div id="cesiumContainer"></div>

        <div id="toolbar">
            <div><b>Controles</b></div>
            <button onclick="window.toggleOrbits()">Orbites</button>
            <button onclick="window.toggleLabels()">Labels</button>
            <button onclick="window.resetView()">Reset Vue</button>
            <button onclick="window.toggleAnimation()">Play/Pause</button>

            <div class="legend">
                <div class="legend-item">
                    <div class="legend-color" style="background: #00ff64;"></div>
                    <span>Satellites</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #ffa500;"></div>
                    <span>Rocket Bodies</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #ff3232;"></div>
                    <span>Debris</span>
                </div>
            </div>
        </div>

        <div id="stats">
            <div><b>Statistiques</b></div>
            <div id="objectCount">Objets: 0</div>
            <div id="selectedInfo">Selection: -</div>
        </div>

        <script>
            try {{
                // Initialize Cesium
                const hasToken = {str(has_token).lower()};
                if (hasToken) {{
                    Cesium.Ion.defaultAccessToken = '{token}';
                }}

                // Create viewer with terrain if token available
                const viewerOptions = {{
                    animation: true,
                    timeline: true,
                    fullscreenButton: true,
                    vrButton: false,
                    geocoder: false,
                    homeButton: true,
                    infoBox: true,
                    selectionIndicator: true,
                    navigationHelpButton: false,
                    baseLayerPicker: true,
                    shouldAnimate: true
                }};

                const viewer = new Cesium.Viewer('cesiumContainer', viewerOptions);
                console.log('Cesium viewer initialized');

                // Add world terrain if token is set
                if (hasToken) {{
                    Cesium.createWorldTerrainAsync().then(terrain => {{
                        viewer.scene.terrainProvider = terrain;
                        console.log('Terrain loaded');
                    }}).catch(err => console.warn('Terrain not loaded:', err));
                }}

                // Dark theme for space visualization
                viewer.scene.backgroundColor = Cesium.Color.BLACK;
                viewer.scene.globe.enableLighting = true;

                // Satellite data
                const satelliteData = {satellites_json};

                let showOrbits = {str(show_orbits).lower()};
                let showLabels = {str(show_labels).lower()};
                let objectCount = 0;

                // Load satellites as entities (simpler approach for real-time)
                function loadSatellites() {{
                    if (!satelliteData || satelliteData.length === 0) {{
                        console.log('No satellite data to display');
                        return;
                    }}
                    satelliteData.forEach(sat => {{
                        if (!sat.lat || !sat.lon) return;

                        const color = getColorByType(sat.object_type);

                        viewer.entities.add({{
                            id: 'sat_' + sat.norad_id,
                            name: sat.name,
                            description: `
                                <table>
                                    <tr><td><b>NORAD ID:</b></td><td>${{sat.norad_id}}</td></tr>
                                    <tr><td><b>Type:</b></td><td>${{sat.object_type || 'Satellite'}}</td></tr>
                                    <tr><td><b>Country:</b></td><td>${{sat.country || 'N/A'}}</td></tr>
                                    <tr><td><b>Altitude:</b></td><td>${{sat.alt_km?.toFixed(0) || 'N/A'}} km</td></tr>
                                </table>
                            `,
                            position: Cesium.Cartesian3.fromDegrees(sat.lon, sat.lat, (sat.alt_km || 400) * 1000),
                            point: {{
                                pixelSize: sat.object_type === 'DEBRIS' ? 4 : 6,
                                color: color,
                                outlineColor: Cesium.Color.WHITE.withAlpha(0.5),
                                outlineWidth: 1
                            }},
                            label: showLabels ? {{
                                text: sat.name,
                                font: '10px sans-serif',
                                fillColor: Cesium.Color.WHITE,
                                outlineColor: Cesium.Color.BLACK,
                                outlineWidth: 2,
                                style: Cesium.LabelStyle.FILL_AND_OUTLINE,
                                pixelOffset: new Cesium.Cartesian2(0, -15),
                                distanceDisplayCondition: new Cesium.DistanceDisplayCondition(0, 5000000)
                            }} : undefined
                        }});
                        objectCount++;
                    }});

                    document.getElementById('objectCount').textContent = 'Objets: ' + objectCount;
                }}

                function getColorByType(type) {{
                    switch(type) {{
                        case 'PAYLOAD': return Cesium.Color.fromCssColorString('#00ff64');
                        case 'ROCKET BODY': return Cesium.Color.fromCssColorString('#ffa500');
                        case 'DEBRIS': return Cesium.Color.fromCssColorString('#ff3232');
                        default: return Cesium.Color.fromCssColorString('#0096ff');
                    }}
                }}

                // Make functions global for button onclick
                window.toggleOrbits = function() {{
                    showOrbits = !showOrbits;
                    viewer.entities.values.forEach(entity => {{
                        if (entity.path) {{
                            entity.path.show = showOrbits;
                        }}
                    }});
                }};

                window.toggleLabels = function() {{
                    showLabels = !showLabels;
                    viewer.entities.values.forEach(entity => {{
                        if (entity.label) {{
                            entity.label.show = showLabels;
                        }}
                    }});
                }};

                window.resetView = function() {{
                    viewer.camera.flyHome(1.5);
                }};

                window.toggleAnimation = function() {{
                    viewer.clock.shouldAnimate = !viewer.clock.shouldAnimate;
                }};

                // Selection handler
                viewer.selectedEntityChanged.addEventListener(function(entity) {{
                    if (entity) {{
                        document.getElementById('selectedInfo').textContent = 'Selection: ' + entity.name;
                    }} else {{
                        document.getElementById('selectedInfo').textContent = 'Selection: -';
                    }}
                }});

                // Load data
                loadSatellites();

                // Initial camera position
                viewer.camera.setView({{
                    destination: Cesium.Cartesian3.fromDegrees(0, 20, 25000000)
                }});

                console.log('Cesium globe fully initialized with ' + objectCount + ' objects');
            }} catch (error) {{
                console.error('Cesium initialization error:', error);
                document.getElementById('cesiumContainer').innerHTML =
                    '<div style="color: red; padding: 20px; font-size: 16px;">Error loading 3D Globe: ' + error.message + '</div>';
            }}
        </script>
    </body>
    </html>
    """
    return html


def render_cesium_globe(
    satellites: List[Dict] = None,
    height: int = 700,
    show_labels: bool = False,
    show_orbits: bool = True
):
    """
    Render CesiumJS globe in Streamlit.

    Args:
        satellites: List of satellite dicts with keys:
            - name, norad_id, lat, lon, alt_km, object_type, country
        height: Height of the viewer in pixels
        show_labels: Show satellite name labels
        show_orbits: Show orbit paths
    """
    satellites_json = json.dumps(satellites or [])

    html = generate_cesium_html(
        satellites_json=satellites_json,
        height=height,
        show_labels=show_labels,
        show_orbits=show_orbits
    )

    components.html(html, height=height + 50, scrolling=True)


def prepare_satellites_for_cesium(satellites, propagator_func=None) -> List[Dict]:
    """
    Prepare satellite data for Cesium visualization.

    Args:
        satellites: List of Satellite or SpaceObject instances
        propagator_func: Optional function to compute current position

    Returns:
        List of dicts ready for Cesium
    """
    cesium_data = []

    for sat in satellites:
        data = {
            'name': sat.name,
            'norad_id': sat.norad_id,
            'object_type': getattr(sat, 'object_type', 'satellite'),
            'country': getattr(sat, 'country', ''),
        }

        # Compute current position if propagator provided
        if propagator_func:
            try:
                pos = propagator_func(sat.tle_line1, sat.tle_line2, sat.name)
                data['lat'] = pos['lat']
                data['lon'] = pos['lon']
                data['alt_km'] = pos['alt_km']
            except Exception as e:
                print(f"Propagation error for {sat.name}: {e}")
                continue
        else:
            # Skip if no position data
            continue

        cesium_data.append(data)

    return cesium_data
