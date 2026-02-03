"""
Anomaly Detection Module
Detects inconsistencies between astronomical catalogs
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Any
from dataclasses import dataclass
from enum import Enum
import config


class AnomalyType(Enum):
    PHOTOMETRIC = "photometric"
    ASTROMETRIC = "astrometric"
    COLOR = "color"
    MISSING = "missing"


@dataclass
class Anomaly:
    """Represents a detected anomaly."""
    source_id: int
    anomaly_type: AnomalyType
    severity: str  # 'low', 'medium', 'high'
    sigma: float
    description: str
    details: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            'source_id': self.source_id,
            'type': self.anomaly_type.value,
            'severity': self.severity,
            'sigma': round(self.sigma, 2),
            'description': self.description,
            **self.details
        }


def safe_source_id(row) -> int:
    """Safely extract source_id from a row, handling NaN values."""
    sid = row.get('source_id') if hasattr(row, 'get') else row['source_id']
    if pd.isna(sid):
        return 0
    return int(sid)


def compute_anomaly_score(anomalies: List[Anomaly]) -> float:
    """
    Compute composite anomaly score (0-100).
    Higher = more interesting.
    """
    if not anomalies:
        return 0.0

    weights = {
        AnomalyType.PHOTOMETRIC: 30,
        AnomalyType.ASTROMETRIC: 25,
        AnomalyType.COLOR: 20,
        AnomalyType.MISSING: 25
    }

    score = 0.0
    for anomaly in anomalies:
        base = weights.get(anomaly.anomaly_type, 10)
        sigma_factor = min(anomaly.sigma / 3, 3)  # cap at 3x
        score += base * sigma_factor

    return min(score, 100)


def get_severity(sigma: float) -> str:
    """Determine severity based on sigma."""
    if sigma >= 5:
        return 'high'
    elif sigma >= 3:
        return 'medium'
    return 'low'


def detect_photometric_anomalies_gaia_sdss(df: pd.DataFrame, sigma_threshold: float = None) -> List[Anomaly]:
    """
    Detect photometric inconsistencies between Gaia G and SDSS g.

    Uses approximate transformation: G ≈ g - 0.13*(g-r) - 0.03
    (simplified, actual transformation is more complex)
    """
    threshold = sigma_threshold if sigma_threshold is not None else config.PHOTOMETRIC_SIGMA_THRESHOLD
    anomalies = []

    # Check if we have both Gaia and SDSS data
    if 'phot_g_mean_mag' not in df.columns or 'sdss_g' not in df.columns:
        return anomalies

    for idx, row in df.iterrows():
        gaia_g = row.get('phot_g_mean_mag')
        sdss_g = row.get('sdss_g')
        sdss_r = row.get('sdss_r')

        # Skip if missing data
        if pd.isna(gaia_g) or pd.isna(sdss_g) or pd.isna(sdss_r):
            continue

        # Approximate Gaia G from SDSS (simplified transformation)
        sdss_color = sdss_g - sdss_r
        expected_gaia_g = sdss_g - 0.13 * sdss_color - 0.03

        # Calculate difference
        delta_mag = abs(gaia_g - expected_gaia_g)

        # Assume typical combined error ~0.05 mag for bright sources
        combined_error = 0.05
        sigma = delta_mag / combined_error

        if sigma > threshold:
            anomalies.append(Anomaly(
                source_id=safe_source_id(row),
                anomaly_type=AnomalyType.PHOTOMETRIC,
                severity=get_severity(sigma),
                sigma=sigma,
                description=f"Gaia G={gaia_g:.2f} vs expected {expected_gaia_g:.2f} from SDSS (Δ={delta_mag:.2f} mag)",
                details={
                    'gaia_g': round(gaia_g, 3),
                    'sdss_g': round(sdss_g, 3),
                    'sdss_r': round(sdss_r, 3),
                    'expected_gaia_g': round(expected_gaia_g, 3),
                    'delta_mag': round(delta_mag, 3)
                }
            ))

    return anomalies


def detect_photometric_anomalies_gaia_2mass(df: pd.DataFrame, sigma_threshold: float = None) -> List[Anomaly]:
    """
    Detect photometric inconsistencies between Gaia and 2MASS.

    Uses G-K color to check consistency.
    """
    threshold = sigma_threshold if sigma_threshold is not None else config.PHOTOMETRIC_SIGMA_THRESHOLD
    anomalies = []

    if 'phot_g_mean_mag' not in df.columns or 'k_mag' not in df.columns:
        return anomalies

    for idx, row in df.iterrows():
        gaia_g = row.get('phot_g_mean_mag')
        k_mag = row.get('k_mag')
        bp_rp = row.get('bp_rp')

        if pd.isna(gaia_g) or pd.isna(k_mag) or pd.isna(bp_rp):
            continue

        # G-K color
        g_k = gaia_g - k_mag

        # Expected G-K based on BP-RP (rough relation for main sequence)
        # This is a simplified model
        expected_g_k = 0.5 + 1.2 * bp_rp

        delta = abs(g_k - expected_g_k)
        sigma = delta / 0.3  # typical scatter ~0.3 mag

        if sigma > threshold:
            anomalies.append(Anomaly(
                source_id=safe_source_id(row),
                anomaly_type=AnomalyType.PHOTOMETRIC,
                severity=get_severity(sigma),
                sigma=sigma,
                description=f"G-K={g_k:.2f} unusual for BP-RP={bp_rp:.2f} (expected ~{expected_g_k:.2f})",
                details={
                    'gaia_g': round(gaia_g, 3),
                    'k_mag': round(k_mag, 3),
                    'g_k_color': round(g_k, 3),
                    'bp_rp': round(bp_rp, 3),
                    'expected_g_k': round(expected_g_k, 3)
                }
            ))

    return anomalies


def detect_astrometric_anomalies(df: pd.DataFrame, sigma_threshold: float = None) -> List[Anomaly]:
    """
    Detect astrometric inconsistencies (position/proper motion).
    """
    threshold = sigma_threshold if sigma_threshold is not None else config.ASTROMETRIC_SIGMA_THRESHOLD
    anomalies = []

    # Check cross-match distance
    dist_col = None
    if 'xmatch_dist_arcsec' in df.columns:
        dist_col = 'xmatch_dist_arcsec'
    elif 'dist_2mass' in df.columns:
        dist_col = 'dist_2mass'
    elif 'dist_sdss' in df.columns:
        dist_col = 'dist_sdss'

    if dist_col is None:
        return anomalies

    for idx, row in df.iterrows():
        dist = row.get(dist_col)

        if pd.isna(dist):
            continue

        # Convert to arcsec if needed (Gaia stores in arcsec)
        dist_arcsec = dist

        # Typical good match < 0.5 arcsec
        # Flag if > 1 arcsec
        if dist_arcsec > 1.0:
            sigma = dist_arcsec / 0.3  # typical error ~0.3 arcsec

            # Check if high proper motion could explain it
            pmra = row.get('pmra', 0) or 0
            pmdec = row.get('pmdec', 0) or 0
            total_pm = np.sqrt(pmra**2 + pmdec**2)

            possible_cause = "high_proper_motion" if total_pm > 50 else "unknown"

            anomalies.append(Anomaly(
                source_id=safe_source_id(row),
                anomaly_type=AnomalyType.ASTROMETRIC,
                severity=get_severity(sigma),
                sigma=sigma,
                description=f"Large cross-match distance: {dist_arcsec:.2f} arcsec",
                details={
                    'xmatch_dist_arcsec': round(dist_arcsec, 3),
                    'pmra': round(pmra, 2) if pmra else None,
                    'pmdec': round(pmdec, 2) if pmdec else None,
                    'total_pm': round(total_pm, 2),
                    'possible_cause': possible_cause
                }
            ))

    return anomalies


def detect_color_anomalies(df: pd.DataFrame, color_threshold: float = None) -> List[Anomaly]:
    """
    Detect unusual colors that don't fit standard stellar locus.
    """
    # color_threshold affects the range considered extreme
    threshold = color_threshold if color_threshold is not None else config.COLOR_DELTA_THRESHOLD
    anomalies = []

    if 'bp_rp' not in df.columns:
        return anomalies

    # Define extreme color boundaries based on threshold
    blue_limit = -0.5 - threshold
    red_limit = 5.0 + threshold

    for idx, row in df.iterrows():
        bp_rp = row.get('bp_rp')
        gaia_g = row.get('phot_g_mean_mag')
        parallax = row.get('parallax')

        if pd.isna(bp_rp) or pd.isna(gaia_g):
            continue

        # Check for extremely blue or red colors
        if bp_rp < -0.5 or bp_rp > 5.0:
            sigma = abs(bp_rp - 1.5) / 1.0  # typical range ~0-3
            anomalies.append(Anomaly(
                source_id=safe_source_id(row),
                anomaly_type=AnomalyType.COLOR,
                severity=get_severity(sigma),
                sigma=sigma,
                description=f"Extreme BP-RP color: {bp_rp:.2f}",
                details={
                    'bp_rp': round(bp_rp, 3),
                    'gaia_g': round(gaia_g, 3),
                    'parallax': round(parallax, 3) if not pd.isna(parallax) else None
                }
            ))

    return anomalies


def detect_missing_crossmatch(df: pd.DataFrame) -> List[Anomaly]:
    """
    Detect sources present in Gaia but missing expected cross-matches.
    """
    anomalies = []

    for idx, row in df.iterrows():
        gaia_g = row.get('phot_g_mean_mag')

        if pd.isna(gaia_g):
            continue

        # Bright sources (G < 16) should generally have 2MASS matches
        has_2mass = not pd.isna(row.get('j_mag')) if 'j_mag' in df.columns else True
        has_sdss = not pd.isna(row.get('sdss_g')) if 'sdss_g' in df.columns else True

        if gaia_g < 16 and not has_2mass and 'j_mag' in df.columns:
            anomalies.append(Anomaly(
                source_id=safe_source_id(row),
                anomaly_type=AnomalyType.MISSING,
                severity='medium',
                sigma=3.0,
                description=f"Bright source (G={gaia_g:.1f}) missing 2MASS match",
                details={
                    'gaia_g': round(gaia_g, 3),
                    'missing_catalog': '2MASS'
                }
            ))

        if gaia_g < 18 and not has_sdss and 'sdss_g' in df.columns:
            anomalies.append(Anomaly(
                source_id=safe_source_id(row),
                anomaly_type=AnomalyType.MISSING,
                severity='low',
                sigma=2.0,
                description=f"Source (G={gaia_g:.1f}) missing SDSS match",
                details={
                    'gaia_g': round(gaia_g, 3),
                    'missing_catalog': 'SDSS'
                }
            ))

    return anomalies


def analyze_crossmatch_data(
    df: pd.DataFrame,
    photometric_sigma: float = None,
    astrometric_sigma: float = None,
    color_delta: float = None
) -> Dict[str, Any]:
    """
    Run all anomaly detection on cross-matched data.

    Args:
        df: Cross-matched DataFrame
        photometric_sigma: Override threshold (default: from config)
        astrometric_sigma: Override threshold (default: from config)
        color_delta: Override threshold (default: from config)

    Returns summary with all anomalies and statistics.
    """
    # Use provided thresholds or fall back to config defaults
    photo_thresh = photometric_sigma if photometric_sigma is not None else config.PHOTOMETRIC_SIGMA_THRESHOLD
    astro_thresh = astrometric_sigma if astrometric_sigma is not None else config.ASTROMETRIC_SIGMA_THRESHOLD
    color_thresh = color_delta if color_delta is not None else config.COLOR_DELTA_THRESHOLD

    all_anomalies = []

    # Run all detectors with thresholds
    all_anomalies.extend(detect_photometric_anomalies_gaia_sdss(df, sigma_threshold=photo_thresh))
    all_anomalies.extend(detect_photometric_anomalies_gaia_2mass(df, sigma_threshold=photo_thresh))
    all_anomalies.extend(detect_astrometric_anomalies(df, sigma_threshold=astro_thresh))
    all_anomalies.extend(detect_color_anomalies(df, color_threshold=color_thresh))
    all_anomalies.extend(detect_missing_crossmatch(df))

    # Group by source
    anomalies_by_source = {}
    for anomaly in all_anomalies:
        sid = anomaly.source_id
        if sid not in anomalies_by_source:
            anomalies_by_source[sid] = []
        anomalies_by_source[sid].append(anomaly)

    # Compute scores
    source_scores = {
        sid: compute_anomaly_score(anoms)
        for sid, anoms in anomalies_by_source.items()
    }

    # Sort by score
    sorted_sources = sorted(
        source_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )

    # Count by type
    type_counts = {}
    for anomaly in all_anomalies:
        t = anomaly.anomaly_type.value
        type_counts[t] = type_counts.get(t, 0) + 1

    # Count by severity
    severity_counts = {'high': 0, 'medium': 0, 'low': 0}
    for anomaly in all_anomalies:
        severity_counts[anomaly.severity] += 1

    return {
        'total_sources': len(df),
        'sources_with_anomalies': len(anomalies_by_source),
        'total_anomalies': len(all_anomalies),
        'anomaly_rate': len(anomalies_by_source) / len(df) * 100 if len(df) > 0 else 0,
        'by_type': type_counts,
        'by_severity': severity_counts,
        'top_anomalies': [
            {
                'source_id': sid,
                'score': score,
                'anomalies': [a.to_dict() for a in anomalies_by_source[sid]]
            }
            for sid, score in sorted_sources[:20]  # Top 20
        ],
        'all_anomalies': [a.to_dict() for a in all_anomalies]
    }
