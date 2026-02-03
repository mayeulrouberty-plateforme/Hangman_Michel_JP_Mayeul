"""
Space Traffic Management - Orbit Propagation Module
Uses Skyfield and SGP4 for satellite position calculations
"""
from skyfield.api import load, EarthSatellite, wgs84
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import pandas as pd
import config


# Load timescale (cached)
_ts = None

def get_timescale():
    """Get or create timescale object."""
    global _ts
    if _ts is None:
        _ts = load.timescale()
    return _ts


def create_satellite(name: str, tle_line1: str, tle_line2: str) -> EarthSatellite:
    """
    Create a Skyfield EarthSatellite from TLE lines.

    Args:
        name: Satellite name
        tle_line1: TLE line 1
        tle_line2: TLE line 2

    Returns:
        EarthSatellite object
    """
    ts = get_timescale()
    return EarthSatellite(tle_line1, tle_line2, name, ts)


def get_current_position(tle_line1: str, tle_line2: str, name: str = "Satellite") -> Dict[str, Any]:
    """
    Get current position of a satellite.

    Returns:
        Dict with lat, lon, alt_km, velocity_km_s
    """
    ts = get_timescale()
    satellite = create_satellite(name, tle_line1, tle_line2)

    now = ts.now()
    geocentric = satellite.at(now)

    # Get subpoint (lat, lon, elevation)
    subpoint = wgs84.subpoint(geocentric)

    # Get velocity
    velocity = geocentric.velocity.km_per_s
    speed = np.sqrt(sum(v**2 for v in velocity))

    return {
        'name': name,
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'lat': subpoint.latitude.degrees,
        'lon': subpoint.longitude.degrees,
        'alt_km': subpoint.elevation.km,
        'velocity_km_s': round(speed, 2)
    }


def propagate_orbit(
    tle_line1: str,
    tle_line2: str,
    name: str = "Satellite",
    hours_ahead: int = None,
    step_minutes: int = None
) -> pd.DataFrame:
    """
    Propagate satellite orbit forward in time.

    Args:
        tle_line1: TLE line 1
        tle_line2: TLE line 2
        name: Satellite name
        hours_ahead: Hours to propagate (default from config)
        step_minutes: Time step in minutes (default from config)

    Returns:
        DataFrame with columns: time, lat, lon, alt_km, velocity_km_s
    """
    if hours_ahead is None:
        hours_ahead = config.DEFAULT_PROPAGATION_HOURS
    if step_minutes is None:
        step_minutes = config.PROPAGATION_STEP_MINUTES

    ts = get_timescale()
    satellite = create_satellite(name, tle_line1, tle_line2)

    # Generate time array
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    times = []
    current = now
    end = now + timedelta(hours=hours_ahead)

    while current <= end:
        times.append(current)
        current += timedelta(minutes=step_minutes)

    # Propagate
    results = []
    for t in times:
        sky_time = ts.utc(t.year, t.month, t.day, t.hour, t.minute, t.second)
        geocentric = satellite.at(sky_time)
        subpoint = wgs84.subpoint(geocentric)

        velocity = geocentric.velocity.km_per_s
        speed = np.sqrt(sum(v**2 for v in velocity))

        results.append({
            'time': t.isoformat(),
            'lat': round(subpoint.latitude.degrees, 4),
            'lon': round(subpoint.longitude.degrees, 4),
            'alt_km': round(subpoint.elevation.km, 2),
            'velocity_km_s': round(speed, 2)
        })

    return pd.DataFrame(results)


def get_ground_track(
    tle_line1: str,
    tle_line2: str,
    name: str = "Satellite",
    hours: int = 2
) -> List[Tuple[float, float]]:
    """
    Get ground track coordinates for plotting.

    Returns:
        List of (lat, lon) tuples
    """
    df = propagate_orbit(tle_line1, tle_line2, name, hours_ahead=hours, step_minutes=1)
    return list(zip(df['lat'].tolist(), df['lon'].tolist()))


def get_orbit_period_minutes(tle_line2: str) -> float:
    """
    Calculate orbital period from TLE.
    Mean motion is in revolutions per day (columns 53-63 of line 2).
    """
    try:
        mean_motion = float(tle_line2[52:63].strip())
        if mean_motion > 0:
            return 1440.0 / mean_motion  # 1440 minutes per day
    except (ValueError, IndexError):
        pass
    return 0.0


def get_orbit_info(tle_line1: str, tle_line2: str) -> Dict[str, Any]:
    """
    Extract orbital parameters from TLE.
    """
    try:
        # Line 2 contains orbital elements
        inclination = float(tle_line2[8:16].strip())
        raan = float(tle_line2[17:25].strip())  # Right Ascension of Ascending Node
        eccentricity = float('0.' + tle_line2[26:33].strip())
        arg_perigee = float(tle_line2[34:42].strip())
        mean_anomaly = float(tle_line2[43:51].strip())
        mean_motion = float(tle_line2[52:63].strip())

        period = 1440.0 / mean_motion if mean_motion > 0 else 0

        # Estimate altitude (simplified)
        # a = (GM / (2*pi*n)^2)^(1/3) - Re
        # Simplified: period-based approximation
        semi_major_axis_km = ((period * 60 / (2 * np.pi))**2 * 398600.4418)**(1/3)
        altitude_km = semi_major_axis_km - 6371  # Earth radius

        # Classify orbit type
        # GEO check MUST come before MEO to avoid misclassification
        if altitude_km < 2000:
            orbit_type = "LEO"
        elif 35786 - 500 < altitude_km < 35786 + 500:
            orbit_type = "GEO"
        elif altitude_km < 35786:
            orbit_type = "MEO"
        else:
            orbit_type = "HEO"

        return {
            'inclination_deg': round(inclination, 2),
            'eccentricity': round(eccentricity, 6),
            'period_minutes': round(period, 2),
            'mean_motion_rev_day': round(mean_motion, 4),
            'altitude_km_approx': round(altitude_km, 0),
            'orbit_type': orbit_type,
            'raan_deg': round(raan, 2),
            'arg_perigee_deg': round(arg_perigee, 2)
        }

    except (ValueError, IndexError) as e:
        return {'error': str(e)}


def check_visibility(
    tle_line1: str,
    tle_line2: str,
    observer_lat: float,
    observer_lon: float,
    observer_alt_m: float = 0
) -> Dict[str, Any]:
    """
    Check if satellite is visible from observer location.

    Returns:
        Dict with altitude, azimuth, distance, is_visible
    """
    ts = get_timescale()
    satellite = EarthSatellite(tle_line1, tle_line2, "Sat", ts)

    # Observer position
    observer = wgs84.latlon(observer_lat, observer_lon, observer_alt_m)

    now = ts.now()
    difference = satellite - observer
    topocentric = difference.at(now)

    alt, az, distance = topocentric.altaz()

    return {
        'altitude_deg': round(alt.degrees, 2),
        'azimuth_deg': round(az.degrees, 2),
        'distance_km': round(distance.km, 2),
        'is_visible': alt.degrees > 0
    }
