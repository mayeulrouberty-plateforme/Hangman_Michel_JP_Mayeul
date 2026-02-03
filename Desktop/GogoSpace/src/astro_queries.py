"""
Astronomical Query Module
Queries via VizieR (CDS Strasbourg) - independent from ESA Gaia TAP
"""
from astroquery.vizier import Vizier
from astroquery.simbad import Simbad
from astropy.coordinates import SkyCoord, match_coordinates_sky
import astropy.units as u
import pandas as pd
import numpy as np
from typing import Optional, Dict, List
import config


# VizieR catalog IDs
CATALOGS = {
    'gaia': 'I/355/gaiadr3',      # Gaia DR3
    '2mass': 'II/246/out',         # 2MASS Point Source Catalog
    'sdss': 'V/154/sdss16',        # SDSS DR16
}


def query_gaia_region(
    ra: float,
    dec: float,
    radius_deg: float = config.DEFAULT_SEARCH_RADIUS_DEG,
    limit: int = config.DEFAULT_ROW_LIMIT
) -> pd.DataFrame:
    """
    Query Gaia DR3 via VizieR.
    """
    coord = SkyCoord(ra=ra, dec=dec, unit=(u.deg, u.deg), frame='icrs')

    v = Vizier(
        columns=['Source', 'RA_ICRS', 'DE_ICRS', 'Plx', 'e_Plx',
                 'pmRA', 'pmDE', 'Gmag', 'BPmag', 'RPmag', 'BP-RP',
                 'RV', 'Teff', 'logg'],
        row_limit=limit
    )

    result = v.query_region(coord, radius=radius_deg*u.deg, catalog=CATALOGS['gaia'])

    if not result:
        return pd.DataFrame()

    df = result[0].to_pandas()

    # Rename columns for consistency
    df = df.rename(columns={
        'Source': 'source_id',
        'RA_ICRS': 'ra',
        'DE_ICRS': 'dec',
        'Plx': 'parallax',
        'e_Plx': 'parallax_error',
        'pmRA': 'pmra',
        'pmDE': 'pmdec',
        'Gmag': 'phot_g_mean_mag',
        'BPmag': 'phot_bp_mean_mag',
        'RPmag': 'phot_rp_mean_mag',
        'BP-RP': 'bp_rp',
        'RV': 'radial_velocity',
        'Teff': 'teff_gspphot',
        'logg': 'logg_gspphot'
    })

    return df


def query_2mass_region(
    ra: float,
    dec: float,
    radius_deg: float = config.DEFAULT_SEARCH_RADIUS_DEG,
    limit: int = config.DEFAULT_ROW_LIMIT
) -> pd.DataFrame:
    """
    Query 2MASS via VizieR.
    """
    coord = SkyCoord(ra=ra, dec=dec, unit=(u.deg, u.deg), frame='icrs')

    v = Vizier(
        columns=['RAJ2000', 'DEJ2000', 'Jmag', 'e_Jmag', 'Hmag', 'e_Hmag', 'Kmag', 'e_Kmag', '2MASS'],
        row_limit=limit
    )

    result = v.query_region(coord, radius=radius_deg*u.deg, catalog=CATALOGS['2mass'])

    if not result:
        return pd.DataFrame()

    df = result[0].to_pandas()

    df = df.rename(columns={
        'RAJ2000': 'ra',
        'DEJ2000': 'dec',
        'Jmag': 'j_mag',
        'e_Jmag': 'j_mag_err',
        'Hmag': 'h_mag',
        'e_Hmag': 'h_mag_err',
        'Kmag': 'k_mag',
        'e_Kmag': 'k_mag_err',
        '2MASS': 'tmass_id'
    })

    return df


def query_sdss_region(
    ra: float,
    dec: float,
    radius_deg: float = config.DEFAULT_SEARCH_RADIUS_DEG,
    limit: int = config.DEFAULT_ROW_LIMIT
) -> pd.DataFrame:
    """
    Query SDSS via VizieR.
    """
    coord = SkyCoord(ra=ra, dec=dec, unit=(u.deg, u.deg), frame='icrs')

    v = Vizier(
        columns=['RA_ICRS', 'DE_ICRS', 'umag', 'gmag', 'rmag', 'imag', 'zmag',
                 'e_umag', 'e_gmag', 'e_rmag', 'e_imag', 'e_zmag', 'objID'],
        row_limit=limit
    )

    result = v.query_region(coord, radius=radius_deg*u.deg, catalog=CATALOGS['sdss'])

    if not result:
        return pd.DataFrame()

    df = result[0].to_pandas()

    df = df.rename(columns={
        'RA_ICRS': 'ra',
        'DE_ICRS': 'dec',
        'umag': 'sdss_u',
        'gmag': 'sdss_g',
        'rmag': 'sdss_r',
        'imag': 'sdss_i',
        'zmag': 'sdss_z',
        'e_umag': 'sdss_u_err',
        'e_gmag': 'sdss_g_err',
        'e_rmag': 'sdss_r_err',
        'e_imag': 'sdss_i_err',
        'e_zmag': 'sdss_z_err',
        'objID': 'sdss_id'
    })

    return df


def crossmatch_catalogs(
    df1: pd.DataFrame,
    df2: pd.DataFrame,
    max_sep_arcsec: float = 2.0,
    ra1: str = 'ra',
    dec1: str = 'dec',
    ra2: str = 'ra',
    dec2: str = 'dec',
    suffix: str = '_2'
) -> pd.DataFrame:
    """
    Cross-match two catalogs by position.

    Args:
        df1: Primary catalog (all rows kept)
        df2: Secondary catalog (matched to df1)
        max_sep_arcsec: Maximum separation for a valid match
        ra1, dec1: Column names for coords in df1
        ra2, dec2: Column names for coords in df2
        suffix: Suffix for df2 columns in output

    Returns:
        df1 with matched df2 columns added (NaN if no match)
    """
    if df1.empty or df2.empty:
        return df1

    # Filter out rows with NaN coordinates
    valid1 = df1[df1[ra1].notna() & df1[dec1].notna()].copy()
    valid2 = df2[df2[ra2].notna() & df2[dec2].notna()].copy()

    if valid1.empty or valid2.empty:
        return df1

    # Create SkyCoord objects
    coords1 = SkyCoord(ra=valid1[ra1].values*u.deg, dec=valid1[dec1].values*u.deg)
    coords2 = SkyCoord(ra=valid2[ra2].values*u.deg, dec=valid2[dec2].values*u.deg)

    # Find nearest match for each source in valid1
    idx, sep, _ = match_coordinates_sky(coords1, coords2)

    # Create result dataframe from valid sources
    result = valid1.copy()

    # Add match info
    result['xmatch_idx'] = idx
    result['xmatch_dist_arcsec'] = sep.arcsec

    # Add valid2 columns for valid matches
    valid_match = sep.arcsec < max_sep_arcsec

    for col in valid2.columns:
        if col in [ra2, dec2]:
            new_col = col + suffix
        else:
            new_col = col

        # Get matched values
        matched_vals = valid2.iloc[idx[valid_match]][col].values

        # Initialize column with appropriate dtype
        if valid2[col].dtype == 'object' or (len(matched_vals) > 0 and hasattr(matched_vals, 'dtype') and matched_vals.dtype == 'object'):
            result[new_col] = None
        else:
            result[new_col] = np.nan

        result.loc[valid_match, new_col] = matched_vals

    # Mark invalid matches
    result.loc[~valid_match, 'xmatch_dist_arcsec'] = np.nan

    # Drop helper column
    result = result.drop(columns=['xmatch_idx'])

    return result


def query_gaia_crossmatch_2mass(
    ra: float,
    dec: float,
    radius_deg: float = config.DEFAULT_SEARCH_RADIUS_DEG,
    limit: int = config.DEFAULT_ROW_LIMIT
) -> pd.DataFrame:
    """
    Query Gaia and 2MASS, return cross-matched catalog.
    """
    # Query both catalogs
    gaia = query_gaia_region(ra, dec, radius_deg, limit)
    tmass = query_2mass_region(ra, dec, radius_deg, limit * 2)  # Get more to ensure matches

    if gaia.empty:
        return gaia

    if tmass.empty:
        return gaia

    # Cross-match
    result = crossmatch_catalogs(gaia, tmass, max_sep_arcsec=2.0)

    return result


def query_gaia_crossmatch_sdss(
    ra: float,
    dec: float,
    radius_deg: float = config.DEFAULT_SEARCH_RADIUS_DEG,
    limit: int = config.DEFAULT_ROW_LIMIT
) -> pd.DataFrame:
    """
    Query Gaia and SDSS, return cross-matched catalog.
    """
    gaia = query_gaia_region(ra, dec, radius_deg, limit)
    sdss = query_sdss_region(ra, dec, radius_deg, limit * 2)

    if gaia.empty:
        return gaia

    if sdss.empty:
        return gaia

    result = crossmatch_catalogs(gaia, sdss, max_sep_arcsec=2.0)

    return result


def query_gaia_full_crossmatch(
    ra: float,
    dec: float,
    radius_deg: float = config.DEFAULT_SEARCH_RADIUS_DEG,
    limit: int = config.DEFAULT_ROW_LIMIT
) -> pd.DataFrame:
    """
    Query Gaia with both 2MASS and SDSS cross-matches.
    """
    # Get Gaia
    gaia = query_gaia_region(ra, dec, radius_deg, limit)

    if gaia.empty:
        return gaia

    # Get 2MASS and cross-match
    tmass = query_2mass_region(ra, dec, radius_deg, limit * 2)
    if not tmass.empty:
        gaia = crossmatch_catalogs(gaia, tmass, max_sep_arcsec=2.0)
        # Rename xmatch column for 2MASS
        if 'xmatch_dist_arcsec' in gaia.columns:
            gaia = gaia.rename(columns={'xmatch_dist_arcsec': 'dist_2mass'})

    # Get SDSS and cross-match
    sdss = query_sdss_region(ra, dec, radius_deg, limit * 2)
    if not sdss.empty:
        # Avoid column conflicts
        sdss_cols_to_use = [c for c in sdss.columns if c not in ['ra', 'dec']]
        sdss_subset = sdss[['ra', 'dec'] + sdss_cols_to_use]
        gaia = crossmatch_catalogs(gaia, sdss_subset, max_sep_arcsec=2.0)
        if 'xmatch_dist_arcsec' in gaia.columns:
            gaia = gaia.rename(columns={'xmatch_dist_arcsec': 'dist_sdss'})

    return gaia


def resolve_object_name(name: str) -> Optional[Dict[str, float]]:
    """
    Resolve an object name to coordinates using SIMBAD.
    """
    try:
        result = Simbad.query_object(name)
        if result is not None and len(result) > 0:
            # SIMBAD now returns 'ra' and 'dec' in degrees (lowercase)
            ra_val = result['ra'][0]
            dec_val = result['dec'][0]
            return {
                'ra': float(ra_val),
                'dec': float(dec_val),
                'name': name
            }
    except Exception as e:
        print(f"SIMBAD error: {e}")
    return None


def execute_custom_adql(query: str) -> pd.DataFrame:
    """
    Execute custom ADQL - not supported with VizieR.
    Returns empty DataFrame with message.
    """
    return pd.DataFrame({'message': ['ADQL not supported with VizieR backend']})


def get_source_by_id(source_id: int) -> Optional[pd.DataFrame]:
    """
    Get Gaia source by ID - requires Gaia TAP, not available via VizieR.
    """
    return None
