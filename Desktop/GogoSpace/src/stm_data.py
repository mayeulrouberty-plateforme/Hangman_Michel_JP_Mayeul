"""
Space Traffic Management - Data Module
Fetches TLE data from Celestrak (no API key required)
"""
import requests
import pandas as pd
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import config


@dataclass
class Satellite:
    """Represents a satellite with TLE data."""
    name: str
    norad_id: int
    intl_designator: str
    tle_line1: str
    tle_line2: str
    epoch: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'norad_id': self.norad_id,
            'intl_designator': self.intl_designator,
            'tle_line1': self.tle_line1,
            'tle_line2': self.tle_line2,
            'epoch': self.epoch.isoformat() if self.epoch else None
        }


def fetch_tle_celestrak(category: str = 'stations', limit: int = 100) -> List[Satellite]:
    """
    Fetch TLE data from Celestrak.

    Args:
        category: TLE category (stations, active, starlink, etc.)
        limit: Maximum number of satellites to return

    Returns:
        List of Satellite objects
    """
    # Map category to Celestrak GROUP parameter
    category_map = {
        'stations': 'stations',
        'active': 'active',
        'starlink': 'starlink',
        'oneweb': 'oneweb',
        'visual': 'visual',
        'weather': 'weather',
        'noaa': 'noaa',
        'gps-ops': 'gps-ops',
        'galileo': 'galileo',
        'debris': 'cosmos-2251-debris'  # Example debris
    }

    group = category_map.get(category, category)

    # Celestrak GP API (TLE format)
    url = f"{config.CELESTRAK_BASE_URL}?GROUP={group}&FORMAT=tle"

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        satellites = parse_tle_text(response.text)
        return satellites[:limit]

    except requests.RequestException as e:
        print(f"Celestrak error: {e}")
        return []


def parse_tle_text(tle_text: str) -> List[Satellite]:
    """
    Parse TLE text format into Satellite objects.

    TLE format:
    Line 0: Satellite name
    Line 1: TLE line 1 (starts with 1)
    Line 2: TLE line 2 (starts with 2)
    """
    satellites = []
    lines = [l.strip() for l in tle_text.strip().split('\n') if l.strip()]

    i = 0
    while i < len(lines) - 2:
        name_line = lines[i]
        line1 = lines[i + 1]
        line2 = lines[i + 2]

        # Validate TLE format
        if not line1.startswith('1 ') or not line2.startswith('2 '):
            i += 1
            continue

        try:
            # Extract NORAD ID from line 1 (columns 3-7)
            norad_id = int(line1[2:7].strip())

            # Extract international designator from line 1 (columns 10-17)
            intl_designator = line1[9:17].strip()

            # Extract epoch from line 1 (columns 19-32)
            epoch_str = line1[18:32].strip()
            epoch = parse_tle_epoch(epoch_str)

            satellites.append(Satellite(
                name=name_line.strip(),
                norad_id=norad_id,
                intl_designator=intl_designator,
                tle_line1=line1,
                tle_line2=line2,
                epoch=epoch
            ))

        except (ValueError, IndexError) as e:
            print(f"TLE parse error: {e}")

        i += 3

    return satellites


def parse_tle_epoch(epoch_str: str) -> Optional[datetime]:
    """
    Parse TLE epoch format (YYDDD.DDDDDDDD).
    YY = year (00-56 = 2000-2056, 57-99 = 1957-1999)
    DDD.DDDDDDDD = day of year with fractional part
    """
    try:
        year_2digit = int(epoch_str[:2])
        day_of_year = float(epoch_str[2:])

        # Y2K handling
        if year_2digit < 57:
            year = 2000 + year_2digit
        else:
            year = 1900 + year_2digit

        # Convert day of year to datetime
        base = datetime(year, 1, 1)
        from datetime import timedelta
        return base + timedelta(days=day_of_year - 1)

    except (ValueError, IndexError):
        return None


def satellites_to_dataframe(satellites: List[Satellite]) -> pd.DataFrame:
    """Convert list of Satellites to DataFrame."""
    if not satellites:
        return pd.DataFrame()

    return pd.DataFrame([s.to_dict() for s in satellites])


def get_tle_categories() -> Dict[str, str]:
    """Get available TLE categories with descriptions."""
    return config.TLE_CATEGORIES


def get_satellite_by_norad(norad_id: int, satellites: List[Satellite]) -> Optional[Satellite]:
    """Find satellite by NORAD ID in a list."""
    for sat in satellites:
        if sat.norad_id == norad_id:
            return sat
    return None


def fetch_iss() -> Optional[Satellite]:
    """Convenience function to fetch ISS TLE."""
    satellites = fetch_tle_celestrak('stations', limit=10)
    for sat in satellites:
        if 'ISS' in sat.name.upper() or sat.norad_id == 25544:
            return sat
    return satellites[0] if satellites else None
