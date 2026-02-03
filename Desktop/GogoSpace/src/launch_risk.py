"""
Launch Risk Assessment Module
Evaluates collision risks and success probability for satellite launches.
Designed for space launch providers like ArianeGroup, SpaceX, RocketLab, etc.
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
import math

# Known launch sites with coordinates
LAUNCH_SITES = {
    "Kourou (CSG)": {"lat": 5.236, "lon": -52.775, "country": "French Guiana"},
    "Cape Canaveral": {"lat": 28.396, "lon": -80.605, "country": "USA"},
    "Vandenberg": {"lat": 34.632, "lon": -120.611, "country": "USA"},
    "Baikonur": {"lat": 45.965, "lon": 63.305, "country": "Kazakhstan"},
    "Jiuquan": {"lat": 40.958, "lon": 100.291, "country": "China"},
    "Tanegashima": {"lat": 30.400, "lon": 130.969, "country": "Japan"},
    "Sriharikota": {"lat": 13.720, "lon": 80.230, "country": "India"},
    "Plesetsk": {"lat": 62.925, "lon": 40.577, "country": "Russia"},
    "Mahia Peninsula": {"lat": -39.262, "lon": 177.864, "country": "New Zealand"},
    "Starbase Boca Chica": {"lat": 25.997, "lon": -97.157, "country": "USA"},
}

# Target orbits with typical parameters
TARGET_ORBITS = {
    "LEO (400km)": {"alt_min": 350, "alt_max": 450, "typical_inc": 51.6},
    "LEO (550km - Starlink)": {"alt_min": 500, "alt_max": 600, "typical_inc": 53.0},
    "SSO (600km)": {"alt_min": 550, "alt_max": 650, "typical_inc": 97.8},
    "MEO (20000km)": {"alt_min": 19000, "alt_max": 21000, "typical_inc": 55.0},
    "GTO": {"alt_min": 200, "alt_max": 35786, "typical_inc": 6.0},
    "GEO": {"alt_min": 35700, "alt_max": 35900, "typical_inc": 0.0},
}


@dataclass
class RiskAssessment:
    """Complete risk assessment for a launch."""
    overall_risk_score: float  # 0-100 (0 = safe, 100 = dangerous)
    success_probability: float  # 0-100%
    collision_risk: float  # 0-100
    debris_density_risk: float  # 0-100
    conjunction_events: int  # Number of close approaches predicted
    high_risk_objects: List[Dict]  # List of most dangerous objects
    risk_factors: Dict[str, float]  # Breakdown of risk factors
    recommendations: List[str]  # Safety recommendations
    optimal_windows: List[Dict]  # Suggested launch windows
    report_timestamp: str


def calculate_orbital_density(
    objects: List[Dict],
    target_alt_min: float,
    target_alt_max: float,
    inclination_range: Tuple[float, float] = None
) -> Dict[str, Any]:
    """
    Calculate debris/satellite density in target orbital regime.

    Args:
        objects: List of space objects with alt_km
        target_alt_min: Minimum altitude of target orbit (km)
        target_alt_max: Maximum altitude of target orbit (km)
        inclination_range: Optional (min, max) inclination filter

    Returns:
        Density metrics and risk assessment
    """
    if not objects:
        return {
            "total_objects": 0,
            "debris_count": 0,
            "satellite_count": 0,
            "density_per_1000km": 0,
            "risk_level": "unknown"
        }

    # Filter objects in altitude band
    in_band = []
    for obj in objects:
        alt = obj.get('alt_km', 0)
        if alt and target_alt_min <= alt <= target_alt_max:
            in_band.append(obj)

    # Count by type
    debris_count = sum(1 for o in in_band if o.get('object_type') == 'DEBRIS')
    rocket_count = sum(1 for o in in_band if o.get('object_type') == 'ROCKET BODY')
    payload_count = sum(1 for o in in_band if o.get('object_type') == 'PAYLOAD')

    # Calculate shell volume (simplified spherical shell)
    r_inner = 6371 + target_alt_min  # Earth radius + altitude
    r_outer = 6371 + target_alt_max
    volume = (4/3) * math.pi * (r_outer**3 - r_inner**3)  # km^3

    # Density per 1000 km^3
    density = (len(in_band) / volume) * 1000 if volume > 0 else 0

    # Risk level based on density
    if density < 0.001:
        risk_level = "low"
    elif density < 0.01:
        risk_level = "moderate"
    elif density < 0.1:
        risk_level = "elevated"
    else:
        risk_level = "high"

    return {
        "total_objects": len(in_band),
        "debris_count": debris_count,
        "rocket_body_count": rocket_count,
        "satellite_count": payload_count,
        "altitude_band": f"{target_alt_min}-{target_alt_max} km",
        "shell_volume_km3": volume,
        "density_per_1000km3": density,
        "risk_level": risk_level
    }


def calculate_collision_probability(
    launch_trajectory: List[Dict],
    space_objects: List[Dict],
    threshold_km: float = 10.0
) -> Tuple[float, List[Dict]]:
    """
    Calculate collision probability during launch ascent.

    Uses simplified conjunction analysis based on closest approach distances.

    Args:
        launch_trajectory: List of trajectory points with lat, lon, alt_km
        space_objects: List of space objects with current positions
        threshold_km: Distance threshold for conjunction (km)

    Returns:
        (collision_probability, list of close approach events)
    """
    close_approaches = []

    for traj_point in launch_trajectory:
        traj_lat = traj_point.get('lat', 0)
        traj_lon = traj_point.get('lon', 0)
        traj_alt = traj_point.get('alt_km', 0)

        for obj in space_objects:
            obj_lat = obj.get('lat')
            obj_lon = obj.get('lon')
            obj_alt = obj.get('alt_km')

            # Skip if any coordinate is None (0 is valid)
            if obj_lat is None or obj_lon is None or obj_alt is None:
                continue

            # Simplified 3D distance calculation
            # Convert to Cartesian for distance
            lat_diff = abs(traj_lat - obj_lat) * 111  # ~111 km per degree
            lon_diff = abs(traj_lon - obj_lon) * 111 * math.cos(math.radians(traj_lat))
            alt_diff = abs(traj_alt - obj_alt)

            distance = math.sqrt(lat_diff**2 + lon_diff**2 + alt_diff**2)

            if distance < threshold_km:
                close_approaches.append({
                    "object_name": obj.get('name', 'Unknown'),
                    "object_type": obj.get('object_type', 'Unknown'),
                    "norad_id": obj.get('norad_id', 0),
                    "distance_km": round(distance, 2),
                    "object_alt_km": obj_alt,
                    "trajectory_alt_km": traj_alt,
                    "risk_level": "critical" if distance < 1 else "high" if distance < 5 else "moderate"
                })

    # Sort by distance
    close_approaches.sort(key=lambda x: x['distance_km'])

    # Calculate probability (simplified model)
    # Based on number of close approaches and their distances
    if not close_approaches:
        probability = 0.001  # Baseline very low risk
    else:
        # Weighted sum based on distance
        risk_sum = sum(1 / (ca['distance_km'] + 0.1) for ca in close_approaches)
        probability = min(risk_sum * 0.1, 99.9)  # Cap at 99.9%

    return probability, close_approaches[:20]  # Return top 20


def generate_launch_trajectory(
    launch_site: Dict,
    target_orbit: Dict,
    launch_azimuth: float = None
) -> List[Dict]:
    """
    Generate simplified launch trajectory for risk analysis.

    Args:
        launch_site: Dict with lat, lon
        target_orbit: Dict with alt_min, alt_max, typical_inc
        launch_azimuth: Launch direction in degrees (auto-calculated if None)

    Returns:
        List of trajectory points
    """
    lat = launch_site['lat']
    lon = launch_site['lon']
    target_alt = (target_orbit['alt_min'] + target_orbit['alt_max']) / 2

    # Calculate launch azimuth if not provided
    if launch_azimuth is None:
        inc = target_orbit['typical_inc']
        # Simplified azimuth calculation
        # Guard against division by zero at poles (lat = ±90°)
        cos_lat = math.cos(math.radians(lat))
        if inc > abs(lat) and abs(cos_lat) > 0.001:
            cos_inc = math.cos(math.radians(inc))
            # Clamp to valid asin range [-1, 1]
            asin_arg = max(-1, min(1, cos_inc / cos_lat))
            launch_azimuth = 90 - math.degrees(math.asin(asin_arg))
        else:
            launch_azimuth = 90

    trajectory = []

    # Simulate ascent phase (0 to target altitude)
    # Simplified exponential altitude profile
    num_points = 50
    for i in range(num_points):
        t = i / (num_points - 1)  # 0 to 1

        # Altitude increases exponentially then levels off
        alt = target_alt * (1 - math.exp(-3 * t))

        # Downrange distance (simplified)
        downrange = t * 500  # ~500 km downrange at insertion

        # Calculate new lat/lon based on azimuth
        delta_lat = (downrange / 111) * math.cos(math.radians(launch_azimuth))
        delta_lon = (downrange / 111) * math.sin(math.radians(launch_azimuth)) / math.cos(math.radians(lat))

        trajectory.append({
            "phase": "ascent",
            "time_seconds": int(t * 600),  # ~10 min to orbit
            "lat": lat + delta_lat,
            "lon": lon + delta_lon,
            "alt_km": alt,
            "velocity_km_s": 7.8 * t  # Simplified velocity profile
        })

    return trajectory


def assess_launch_risk(
    launch_site: str,
    target_orbit: str,
    launch_datetime: datetime,
    space_objects: List[Dict],
    custom_site: Dict = None
) -> RiskAssessment:
    """
    Perform comprehensive launch risk assessment.

    Args:
        launch_site: Name of launch site or "Custom"
        target_orbit: Name of target orbit
        launch_datetime: Planned launch time
        space_objects: List of tracked space objects with positions
        custom_site: Custom site coordinates if launch_site is "Custom"

    Returns:
        Complete RiskAssessment dataclass
    """
    # Get site and orbit parameters
    site = custom_site if launch_site == "Custom" else LAUNCH_SITES.get(launch_site, LAUNCH_SITES["Kourou (CSG)"])
    orbit = TARGET_ORBITS.get(target_orbit, TARGET_ORBITS["LEO (400km)"])

    # Generate trajectory
    trajectory = generate_launch_trajectory(site, orbit)

    # Calculate orbital density in target regime
    density_analysis = calculate_orbital_density(
        space_objects,
        orbit['alt_min'],
        orbit['alt_max']
    )

    # Calculate collision probability
    collision_prob, close_approaches = calculate_collision_probability(
        trajectory,
        space_objects,
        threshold_km=20.0
    )

    # Risk factors calculation
    risk_factors = {}

    # 1. Debris density risk (0-25 points)
    density = density_analysis['density_per_1000km3']
    debris_risk = min(density * 1000, 25)
    risk_factors["debris_density"] = debris_risk

    # 2. Collision risk (0-30 points)
    collision_risk = min(collision_prob * 0.3, 30)
    risk_factors["collision_probability"] = collision_risk

    # 3. Conjunction events (0-20 points)
    conjunction_risk = min(len(close_approaches) * 2, 20)
    risk_factors["conjunction_events"] = conjunction_risk

    # 4. Orbit congestion (0-15 points)
    congestion_risk = min(density_analysis['total_objects'] / 100, 15)
    risk_factors["orbit_congestion"] = congestion_risk

    # 5. Time-of-day factor (0-10 points)
    # Higher risk during peak activity hours
    hour = launch_datetime.hour
    time_risk = 5 if 6 <= hour <= 18 else 2  # Daytime slightly higher
    risk_factors["temporal"] = time_risk

    # Calculate overall risk score
    overall_risk = sum(risk_factors.values())
    overall_risk = min(max(overall_risk, 0), 100)  # Clamp to 0-100

    # Success probability (inverse of risk, with adjustments)
    base_success = 100 - overall_risk
    # Historical success rate factor (launch vehicles are ~95-98% reliable)
    success_probability = max(min(base_success * 0.98, 99.5), 50)

    # Generate recommendations
    recommendations = []

    if debris_risk > 15:
        recommendations.append("Consider altitude adjustment to reduce debris exposure")

    if len(close_approaches) > 5:
        recommendations.append(f"Monitor {len(close_approaches)} tracked objects with close approach potential")

    if collision_prob > 0.1:
        recommendations.append("Recommend detailed conjunction assessment with 18 SDS data")

    if density_analysis['debris_count'] > 50:
        recommendations.append("High debris population in target orbit - consider collision avoidance maneuver capability")

    if overall_risk < 20:
        recommendations.append("Launch conditions nominal - proceed with standard protocols")
    elif overall_risk < 40:
        recommendations.append("Elevated awareness recommended - monitor conjunction warnings")
    elif overall_risk < 60:
        recommendations.append("Consider launch window optimization to reduce risk")
    else:
        recommendations.append("High risk conditions - recommend launch delay for detailed analysis")

    # Generate optimal windows (simplified - 6 windows over 24h)
    optimal_windows = []
    base_time = launch_datetime.replace(minute=0, second=0, microsecond=0)

    for i in range(6):
        window_time = base_time + timedelta(hours=i * 4)
        # Simulate slight risk variation
        window_risk = overall_risk * (0.85 + 0.3 * abs(math.sin(i)))
        optimal_windows.append({
            "window_start": window_time.isoformat(),
            "window_end": (window_time + timedelta(minutes=30)).isoformat(),
            "risk_score": round(window_risk, 1),
            "recommendation": "optimal" if window_risk < overall_risk else "acceptable"
        })

    # Sort windows by risk
    optimal_windows.sort(key=lambda x: x['risk_score'])

    return RiskAssessment(
        overall_risk_score=round(overall_risk, 1),
        success_probability=round(success_probability, 1),
        collision_risk=round(collision_prob, 3),
        debris_density_risk=round(debris_risk, 1),
        conjunction_events=len(close_approaches),
        high_risk_objects=close_approaches[:10],
        risk_factors=risk_factors,
        recommendations=recommendations,
        optimal_windows=optimal_windows[:4],
        report_timestamp=datetime.now(timezone.utc).isoformat()
    )


def generate_risk_report_markdown(assessment: RiskAssessment, launch_params: Dict) -> str:
    """Generate a formatted markdown report from assessment."""

    # Risk level color/emoji
    if assessment.overall_risk_score < 20:
        risk_indicator = "🟢 LOW"
    elif assessment.overall_risk_score < 40:
        risk_indicator = "🟡 MODERATE"
    elif assessment.overall_risk_score < 60:
        risk_indicator = "🟠 ELEVATED"
    else:
        risk_indicator = "🔴 HIGH"

    report = f"""
# Launch Risk Assessment Report

**Generated:** {assessment.report_timestamp}

## Mission Parameters
- **Launch Site:** {launch_params.get('site', 'N/A')}
- **Target Orbit:** {launch_params.get('orbit', 'N/A')}
- **Planned Launch:** {launch_params.get('datetime', 'N/A')}

---

## Risk Summary

| Metric | Value |
|--------|-------|
| **Overall Risk Score** | {assessment.overall_risk_score}/100 ({risk_indicator}) |
| **Success Probability** | {assessment.success_probability}% |
| **Collision Probability** | {assessment.collision_risk}% |
| **Conjunction Events** | {assessment.conjunction_events} |

---

## Risk Factor Breakdown

"""

    for factor, value in assessment.risk_factors.items():
        bar_length = int(value / 2)
        bar = "█" * bar_length + "░" * (15 - bar_length)
        report += f"- **{factor.replace('_', ' ').title()}**: {value:.1f}/30 [{bar}]\n"

    report += "\n---\n\n## Recommendations\n\n"

    for i, rec in enumerate(assessment.recommendations, 1):
        report += f"{i}. {rec}\n"

    if assessment.high_risk_objects:
        report += "\n---\n\n## High-Risk Objects\n\n"
        report += "| Object | Type | Distance (km) | Risk |\n"
        report += "|--------|------|---------------|------|\n"

        for obj in assessment.high_risk_objects[:5]:
            report += f"| {obj['object_name'][:20]} | {obj['object_type']} | {obj['distance_km']} | {obj['risk_level']} |\n"

    if assessment.optimal_windows:
        report += "\n---\n\n## Optimal Launch Windows\n\n"
        for i, window in enumerate(assessment.optimal_windows, 1):
            report += f"{i}. **{window['window_start'][:16]}** - Risk: {window['risk_score']}/100 ({window['recommendation']})\n"

    return report


def get_launch_sites() -> Dict[str, Dict]:
    """Return available launch sites."""
    return LAUNCH_SITES.copy()


def get_target_orbits() -> Dict[str, Dict]:
    """Return available target orbits."""
    return TARGET_ORBITS.copy()
