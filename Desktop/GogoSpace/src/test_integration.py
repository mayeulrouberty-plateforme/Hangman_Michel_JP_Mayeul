#!/usr/bin/env python3
"""
Integration Tests - Cosmic Query Agent + STM
Run: python test_integration.py
"""
import sys
import traceback

def test_imports():
    """Test all module imports."""
    print("=" * 50)
    print("TEST 1: Imports")
    print("=" * 50)

    modules = [
        ('config', 'Configuration'),
        ('astro_queries', 'Astronomical Queries'),
        ('anomaly_detector', 'Anomaly Detection'),
        ('llm_agent', 'LLM Agent'),
        ('stm_data', 'STM Data (TLE)'),
        ('stm_propagator', 'STM Propagator'),
        ('spacetrack_client', 'Space-Track Client'),
        ('cesium_viewer', 'Cesium 3D Viewer'),
    ]

    results = []
    for module_name, desc in modules:
        try:
            __import__(module_name)
            print(f"  [OK] {desc} ({module_name})")
            results.append(True)
        except ImportError as e:
            print(f"  [FAIL] {desc} ({module_name}): {e}")
            results.append(False)

    return all(results)


def test_config():
    """Test configuration loading."""
    print("\n" + "=" * 50)
    print("TEST 2: Configuration")
    print("=" * 50)

    import config

    checks = [
        ('CELESTRAK_BASE_URL', hasattr(config, 'CELESTRAK_BASE_URL')),
        ('TLE_CATEGORIES', hasattr(config, 'TLE_CATEGORIES')),
        ('DEFAULT_PROPAGATION_HOURS', hasattr(config, 'DEFAULT_PROPAGATION_HOURS')),
        ('PHOTOMETRIC_SIGMA_THRESHOLD', hasattr(config, 'PHOTOMETRIC_SIGMA_THRESHOLD')),
    ]

    for name, exists in checks:
        status = "[OK]" if exists else "[FAIL]"
        print(f"  {status} {name}")

    return all(exists for _, exists in checks)


def test_stm_data():
    """Test STM data module."""
    print("\n" + "=" * 50)
    print("TEST 3: STM Data (Celestrak TLE)")
    print("=" * 50)

    import stm_data

    # Test categories
    categories = stm_data.get_tle_categories()
    print(f"  [OK] {len(categories)} TLE categories available")

    # Test TLE fetch (stations - small dataset)
    print("  [..] Fetching TLE from Celestrak (stations)...")
    try:
        satellites = stm_data.fetch_tle_celestrak('stations', limit=5)
        if satellites:
            print(f"  [OK] Fetched {len(satellites)} satellites")
            for sat in satellites[:3]:
                print(f"       - {sat.name} (NORAD: {sat.norad_id})")
            return True
        else:
            print("  [FAIL] No satellites returned")
            return False
    except Exception as e:
        print(f"  [FAIL] Fetch error: {e}")
        return False


def test_stm_propagator():
    """Test STM propagator module."""
    print("\n" + "=" * 50)
    print("TEST 4: STM Propagator (Skyfield/SGP4)")
    print("=" * 50)

    import stm_data
    import stm_propagator

    # Get ISS TLE
    print("  [..] Fetching ISS TLE...")
    iss = stm_data.fetch_iss()

    if not iss:
        print("  [FAIL] Could not fetch ISS TLE")
        return False

    print(f"  [OK] ISS: {iss.name}")

    # Test current position
    print("  [..] Calculating current position...")
    try:
        pos = stm_propagator.get_current_position(iss.tle_line1, iss.tle_line2, iss.name)
        print(f"  [OK] ISS Position:")
        print(f"       Lat: {pos['lat']:.2f} deg")
        print(f"       Lon: {pos['lon']:.2f} deg")
        print(f"       Alt: {pos['alt_km']:.0f} km")
        print(f"       Speed: {pos['velocity_km_s']:.2f} km/s")
    except Exception as e:
        print(f"  [FAIL] Position error: {e}")
        return False

    # Test orbit info
    print("  [..] Extracting orbital parameters...")
    try:
        orbit = stm_propagator.get_orbit_info(iss.tle_line1, iss.tle_line2)
        print(f"  [OK] Orbit Info:")
        print(f"       Type: {orbit.get('orbit_type', 'N/A')}")
        print(f"       Period: {orbit.get('period_minutes', 0):.1f} min")
        print(f"       Inclination: {orbit.get('inclination_deg', 0):.1f} deg")
    except Exception as e:
        print(f"  [FAIL] Orbit info error: {e}")
        return False

    # Test propagation (short)
    print("  [..] Propagating orbit (1 hour)...")
    try:
        df = stm_propagator.propagate_orbit(
            iss.tle_line1, iss.tle_line2, iss.name,
            hours_ahead=1, step_minutes=10
        )
        print(f"  [OK] Propagation: {len(df)} points calculated")
    except Exception as e:
        print(f"  [FAIL] Propagation error: {e}")
        traceback.print_exc()
        return False

    return True


def test_cosmic_queries():
    """Test astronomical queries (requires network)."""
    print("\n" + "=" * 50)
    print("TEST 5: Cosmic Queries (VizieR/SIMBAD)")
    print("=" * 50)

    import astro_queries

    # Test SIMBAD resolution
    print("  [..] Resolving M42 via SIMBAD...")
    try:
        coords = astro_queries.resolve_object_name('M42')
        if coords:
            print(f"  [OK] M42: RA={coords['ra']:.4f}, Dec={coords['dec']:.4f}")
        else:
            print("  [FAIL] Could not resolve M42")
            return False
    except Exception as e:
        print(f"  [FAIL] SIMBAD error: {e}")
        return False

    # Test Gaia query (small region)
    print("  [..] Querying Gaia DR3 (small region)...")
    try:
        df = astro_queries.query_gaia_region(
            coords['ra'], coords['dec'],
            radius_deg=0.01,  # Very small for quick test
            limit=10
        )
        print(f"  [OK] Gaia: {len(df)} sources found")
    except Exception as e:
        print(f"  [FAIL] Gaia query error: {e}")
        return False

    return True


def test_spacetrack_client():
    """Test Space-Track client module."""
    print("\n" + "=" * 50)
    print("TEST 6: Space-Track Client")
    print("=" * 50)

    import spacetrack_client

    # Test client creation
    client = spacetrack_client.get_client()
    print(f"  [OK] Client created")

    # Test credentials check
    is_configured = spacetrack_client.is_spacetrack_available()
    if is_configured:
        print(f"  [OK] Space-Track credentials configured")
    else:
        print(f"  [INFO] Space-Track not configured (optional)")
        print(f"       Set SPACETRACK_USER and SPACETRACK_PASSWORD in .env")

    # Test categories
    categories = spacetrack_client.get_spacetrack_categories()
    print(f"  [OK] {len(categories)} object types available")

    return True  # Not a failure if credentials not set


def test_cesium_viewer():
    """Test Cesium viewer module."""
    print("\n" + "=" * 50)
    print("TEST 7: Cesium 3D Viewer")
    print("=" * 50)

    import cesium_viewer

    # Test HTML generation
    test_satellites = [
        {
            'name': 'TEST-SAT-1',
            'norad_id': 12345,
            'object_type': 'PAYLOAD',
            'country': 'US',
            'lat': 45.0,
            'lon': -75.0,
            'alt_km': 400
        },
        {
            'name': 'DEBRIS-FRAG',
            'norad_id': 99999,
            'object_type': 'DEBRIS',
            'country': '',
            'lat': -30.0,
            'lon': 120.0,
            'alt_km': 800
        }
    ]

    print("  [..] Generating Cesium HTML...")
    try:
        import json
        satellites_json = json.dumps(test_satellites)
        html = cesium_viewer.generate_cesium_html(
            satellites_json=satellites_json,
            height=600,
            show_labels=True,
            show_orbits=False
        )

        if '<div id="cesiumContainer">' in html:
            print(f"  [OK] Cesium HTML generated ({len(html)} chars)")
        else:
            print(f"  [FAIL] HTML missing cesiumContainer")
            return False

        # Check for key elements
        checks = [
            ('Cesium.js script', 'cesium.com/downloads/cesiumjs'),
            ('Viewer initialization', 'new Cesium.Viewer'),
            ('Color mapping', 'getColorByType'),
            ('Legend', 'legend-item'),
        ]

        for name, pattern in checks:
            if pattern in html:
                print(f"  [OK] {name} present")
            else:
                print(f"  [WARN] {name} missing")

        return True

    except Exception as e:
        print(f"  [FAIL] HTML generation error: {e}")
        traceback.print_exc()
        return False


def test_anomaly_detector():
    """Test anomaly detection."""
    print("\n" + "=" * 50)
    print("TEST 8: Anomaly Detection")
    print("=" * 50)

    import anomaly_detector
    import pandas as pd

    # Create mock data
    mock_data = pd.DataFrame({
        'source_id': [1, 2, 3],
        'ra': [83.82, 83.83, 83.84],
        'dec': [-5.39, -5.40, -5.41],
        'phot_g_mean_mag': [10.0, 12.0, 15.0],
        'bp_rp': [1.5, 2.0, 6.0],  # 6.0 is extreme - should trigger anomaly
        'parallax': [2.5, 1.0, 0.5],
        'k_mag': [8.0, 10.0, 13.0],
    })

    print("  [..] Running anomaly detection on mock data...")
    try:
        results = anomaly_detector.analyze_crossmatch_data(mock_data)
        print(f"  [OK] Analysis complete:")
        print(f"       Total sources: {results['total_sources']}")
        print(f"       With anomalies: {results['sources_with_anomalies']}")
        print(f"       Anomaly rate: {results['anomaly_rate']:.1f}%")
        print(f"       By type: {results['by_type']}")
        return True
    except Exception as e:
        print(f"  [FAIL] Anomaly detection error: {e}")
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "#" * 60)
    print("#  COSMIC QUERY AGENT - INTEGRATION TESTS")
    print("#" * 60)

    tests = [
        ("Imports", test_imports),
        ("Configuration", test_config),
        ("STM Data", test_stm_data),
        ("STM Propagator", test_stm_propagator),
        ("Cosmic Queries", test_cosmic_queries),
        ("Space-Track Client", test_spacetrack_client),
        ("Cesium 3D Viewer", test_cesium_viewer),
        ("Anomaly Detection", test_anomaly_detector),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n  [ERROR] Test {name} crashed: {e}")
            traceback.print_exc()
            results.append((name, False))

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, result in results:
        status = "PASS" if result else "FAIL"
        emoji = "[OK]" if result else "[XX]"
        print(f"  {emoji} {name}: {status}")

    print(f"\nResult: {passed}/{total} tests passed")

    if passed == total:
        print("\n*** ALL TESTS PASSED ***")
        return 0
    else:
        print("\n*** SOME TESTS FAILED ***")
        return 1


if __name__ == "__main__":
    sys.exit(main())
