"""
Space-Track.org API Client
Provides access to full catalog including debris
Requires free account at https://www.space-track.org

Features:
- Caches fetched data to JSON file (1 request/hour limit)
- Loads from cache if available and not expired
- Fetches maximum data in single request for efficiency
"""
import requests
import pandas as pd
import json
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

# Cache configuration
CACHE_DIR = Path(__file__).parent / "data"
CACHE_FILE = CACHE_DIR / "spacetrack_cache.json"
CACHE_EXPIRY_HOURS = 1  # Space-Track rate limit

# Space-Track credentials
SPACETRACK_USER = os.getenv("SPACETRACK_USER", "")
SPACETRACK_PASSWORD = os.getenv("SPACETRACK_PASSWORD", "")

BASE_URL = "https://www.space-track.org"
LOGIN_URL = f"{BASE_URL}/ajaxauth/login"


@dataclass
class SpaceObject:
    """Represents any tracked space object (satellite or debris)."""
    name: str
    norad_id: int
    intl_designator: str
    object_type: str  # PAYLOAD, ROCKET BODY, DEBRIS, UNKNOWN
    country: str
    launch_date: Optional[str]
    tle_line1: str
    tle_line2: str
    rcs_size: Optional[str]  # SMALL, MEDIUM, LARGE
    epoch: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'norad_id': self.norad_id,
            'intl_designator': self.intl_designator,
            'object_type': self.object_type,
            'country': self.country,
            'launch_date': self.launch_date,
            'tle_line1': self.tle_line1,
            'tle_line2': self.tle_line2,
            'rcs_size': self.rcs_size,
            'epoch': self.epoch.isoformat() if self.epoch else None
        }


def _ensure_cache_dir():
    """Create cache directory if it doesn't exist."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _get_cache_age_hours() -> Optional[float]:
    """Get cache file age in hours, or None if no cache."""
    if not CACHE_FILE.exists():
        return None
    mtime = datetime.fromtimestamp(CACHE_FILE.stat().st_mtime, tz=timezone.utc)
    age = datetime.now(timezone.utc) - mtime
    return age.total_seconds() / 3600


def is_cache_valid() -> bool:
    """Check if cache exists and is not expired."""
    age = _get_cache_age_hours()
    if age is None:
        return False
    return age < CACHE_EXPIRY_HOURS


def get_cache_info() -> Dict[str, Any]:
    """Get information about the cache file."""
    if not CACHE_FILE.exists():
        return {
            'exists': False,
            'path': str(CACHE_FILE),
            'message': 'No cache file found'
        }

    age_hours = _get_cache_age_hours()
    mtime = datetime.fromtimestamp(CACHE_FILE.stat().st_mtime, tz=timezone.utc)
    size_mb = CACHE_FILE.stat().st_size / (1024 * 1024)

    # Count objects in cache
    try:
        with open(CACHE_FILE, 'r') as f:
            data = json.load(f)
            object_count = len(data.get('objects', []))
    except (IOError, json.JSONDecodeError, KeyError):
        object_count = 0

    return {
        'exists': True,
        'path': str(CACHE_FILE),
        'valid': age_hours < CACHE_EXPIRY_HOURS,
        'age_hours': round(age_hours, 2),
        'last_updated': mtime.isoformat(),
        'size_mb': round(size_mb, 2),
        'object_count': object_count,
        'expires_in_hours': max(0, round(CACHE_EXPIRY_HOURS - age_hours, 2))
    }


def save_to_cache(objects: List['SpaceObject'], metadata: Dict = None) -> bool:
    """Save objects to cache file."""
    try:
        _ensure_cache_dir()

        data = {
            'fetched_at': datetime.now(timezone.utc).isoformat(),
            'object_count': len(objects),
            'metadata': metadata or {},
            'objects': [obj.to_dict() for obj in objects]
        }

        with open(CACHE_FILE, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"Saved {len(objects)} objects to cache: {CACHE_FILE}")
        return True
    except Exception as e:
        print(f"Failed to save cache: {e}")
        return False


def load_from_cache() -> List['SpaceObject']:
    """Load objects from cache file."""
    if not CACHE_FILE.exists():
        print("No cache file found")
        return []

    try:
        with open(CACHE_FILE, 'r') as f:
            data = json.load(f)

        objects = []
        for item in data.get('objects', []):
            epoch = None
            if item.get('epoch'):
                try:
                    epoch = datetime.fromisoformat(item['epoch'])
                except (ValueError, TypeError):
                    pass

            objects.append(SpaceObject(
                name=item['name'],
                norad_id=item['norad_id'],
                intl_designator=item['intl_designator'],
                object_type=item['object_type'],
                country=item['country'],
                launch_date=item['launch_date'],
                tle_line1=item['tle_line1'],
                tle_line2=item['tle_line2'],
                rcs_size=item['rcs_size'],
                epoch=epoch
            ))

        print(f"Loaded {len(objects)} objects from cache")
        return objects
    except Exception as e:
        print(f"Failed to load cache: {e}")
        return []


class SpaceTrackClient:
    """Client for Space-Track.org API."""

    def __init__(self, username: str = None, password: str = None):
        self.username = username or SPACETRACK_USER
        self.password = password or SPACETRACK_PASSWORD
        self.session = requests.Session()
        self._authenticated = False

    def is_configured(self) -> bool:
        """Check if credentials are configured."""
        return bool(self.username and self.password)

    def login(self) -> bool:
        """Authenticate with Space-Track."""
        if not self.is_configured():
            print("Space-Track credentials not configured")
            return False

        try:
            resp = self.session.post(
                LOGIN_URL,
                data={'identity': self.username, 'password': self.password}
            )
            if resp.status_code == 200 and 'Invalid' not in resp.text:
                self._authenticated = True
                return True
            else:
                print(f"Space-Track login failed: {resp.text[:100]}")
                return False
        except requests.RequestException as e:
            print(f"Space-Track connection error: {e}")
            return False

    def _ensure_auth(self) -> bool:
        """Ensure we're authenticated."""
        if not self._authenticated:
            return self.login()
        return True

    def fetch_tle_by_type(
        self,
        object_type: str = "DEBRIS",
        limit: int = 500,
        epoch_days: int = 30
    ) -> List[SpaceObject]:
        """
        Fetch TLE data by object type.

        Args:
            object_type: PAYLOAD, ROCKET BODY, DEBRIS, or UNKNOWN
            limit: Maximum number of objects
            epoch_days: Only objects with TLE updated in last N days

        Returns:
            List of SpaceObject
        """
        if not self._ensure_auth():
            return []

        epoch_date = (datetime.now(timezone.utc) - timedelta(days=epoch_days)).strftime('%Y-%m-%d')

        # Space-Track API query
        query_url = (
            f"{BASE_URL}/basicspacedata/query/class/gp/"
            f"OBJECT_TYPE/{object_type}/"
            f"EPOCH/%3E{epoch_date}/"
            f"orderby/NORAD_CAT_ID%20asc/"
            f"limit/{limit}/"
            f"format/json"
        )

        try:
            resp = self.session.get(query_url, timeout=60)
            resp.raise_for_status()
            data = resp.json()
            return self._parse_gp_response(data)
        except Exception as e:
            print(f"Space-Track query error: {e}")
            return []

    def fetch_debris(self, limit: int = 1000) -> List[SpaceObject]:
        """Fetch debris objects."""
        return self.fetch_tle_by_type("DEBRIS", limit)

    def fetch_rocket_bodies(self, limit: int = 500) -> List[SpaceObject]:
        """Fetch rocket body objects."""
        return self.fetch_tle_by_type("ROCKET BODY", limit)

    def fetch_active_payloads(self, limit: int = 500) -> List[SpaceObject]:
        """Fetch active payload satellites."""
        return self.fetch_tle_by_type("PAYLOAD", limit)

    def fetch_all_objects(self, limit_per_type: int = 300) -> List[SpaceObject]:
        """Fetch mix of all object types."""
        all_objects = []

        for obj_type in ["PAYLOAD", "ROCKET BODY", "DEBRIS"]:
            objects = self.fetch_tle_by_type(obj_type, limit_per_type)
            all_objects.extend(objects)
            print(f"Fetched {len(objects)} {obj_type}")

        return all_objects

    def fetch_comprehensive_catalog(
        self,
        use_cache: bool = True,
        force_refresh: bool = False,
        epoch_days: int = 30
    ) -> List[SpaceObject]:
        """
        Fetch comprehensive catalog data in ONE request for maximum efficiency.

        This is designed to work with Space-Track's 1 request/hour limit by:
        1. Fetching ALL object types in a single query
        2. No limit on number of objects
        3. Caching results to file for reuse

        Args:
            use_cache: If True, return cached data if valid
            force_refresh: If True, ignore cache and fetch fresh data
            epoch_days: Only objects with TLE updated in last N days

        Returns:
            List of SpaceObject (can be 30,000+ objects)
        """
        # Check cache first
        if use_cache and not force_refresh and is_cache_valid():
            cached = load_from_cache()
            if cached:
                print(f"Using cached data ({len(cached)} objects)")
                return cached

        if not self._ensure_auth():
            print("Authentication failed, trying to load from cache...")
            return load_from_cache()

        epoch_date = (datetime.now(timezone.utc) - timedelta(days=epoch_days)).strftime('%Y-%m-%d')

        # Single comprehensive query - NO limit, all object types
        # This fetches the entire active catalog in one request
        query_url = (
            f"{BASE_URL}/basicspacedata/query/class/gp/"
            f"EPOCH/%3E{epoch_date}/"
            f"orderby/NORAD_CAT_ID%20asc/"
            f"format/json"
        )

        print(f"Fetching comprehensive catalog (epoch > {epoch_date})...")
        print("This may take a minute for the full catalog...")

        try:
            resp = self.session.get(query_url, timeout=300)  # 5 min timeout for large data
            resp.raise_for_status()
            data = resp.json()

            objects = self._parse_gp_response(data)

            # Count by type
            type_counts = {}
            for obj in objects:
                t = obj.object_type
                type_counts[t] = type_counts.get(t, 0) + 1

            print(f"Fetched {len(objects)} total objects:")
            for t, c in sorted(type_counts.items()):
                print(f"  - {t}: {c}")

            # Save to cache
            metadata = {
                'epoch_days': epoch_days,
                'type_counts': type_counts
            }
            save_to_cache(objects, metadata)

            return objects

        except Exception as e:
            print(f"Space-Track comprehensive query error: {e}")
            print("Attempting to load from cache...")
            return load_from_cache()

    def fetch_by_norad_ids(self, norad_ids: List[int]) -> List[SpaceObject]:
        """Fetch specific objects by NORAD ID."""
        if not self._ensure_auth():
            return []

        ids_str = ",".join(str(i) for i in norad_ids)
        query_url = (
            f"{BASE_URL}/basicspacedata/query/class/gp/"
            f"NORAD_CAT_ID/{ids_str}/"
            f"format/json"
        )

        try:
            resp = self.session.get(query_url, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            return self._parse_gp_response(data)
        except Exception as e:
            print(f"Space-Track query error: {e}")
            return []

    def _parse_gp_response(self, data: List[Dict]) -> List[SpaceObject]:
        """Parse GP (General Perturbations) API response."""
        objects = []

        for item in data:
            try:
                # Build TLE lines from GP elements
                tle1 = item.get('TLE_LINE1', '')
                tle2 = item.get('TLE_LINE2', '')

                if not tle1 or not tle2:
                    continue

                epoch_str = item.get('EPOCH', '')
                epoch = None
                if epoch_str:
                    try:
                        epoch = datetime.fromisoformat(epoch_str.replace('Z', '+00:00'))
                    except ValueError:
                        pass

                objects.append(SpaceObject(
                    name=item.get('OBJECT_NAME', 'UNKNOWN'),
                    norad_id=int(item.get('NORAD_CAT_ID', 0)),
                    intl_designator=item.get('OBJECT_ID', ''),
                    object_type=item.get('OBJECT_TYPE', 'UNKNOWN'),
                    country=item.get('COUNTRY_CODE', ''),
                    launch_date=item.get('LAUNCH_DATE', ''),
                    tle_line1=tle1,
                    tle_line2=tle2,
                    rcs_size=item.get('RCS_SIZE', ''),
                    epoch=epoch
                ))
            except (ValueError, KeyError) as e:
                print(f"Parse error: {e}")
                continue

        return objects


def objects_to_dataframe(objects: List[SpaceObject]) -> pd.DataFrame:
    """Convert list of SpaceObjects to DataFrame."""
    if not objects:
        return pd.DataFrame()
    return pd.DataFrame([o.to_dict() for o in objects])


def get_spacetrack_categories() -> Dict[str, str]:
    """Get available Space-Track object types."""
    return {
        'PAYLOAD': 'Satellites actifs/inactifs',
        'ROCKET BODY': 'Corps de fusees',
        'DEBRIS': 'Debris spatiaux',
        'ALL': 'Tous les objets'
    }


# Singleton client instance
_client = None


def get_client() -> SpaceTrackClient:
    """Get or create Space-Track client."""
    global _client
    if _client is None:
        _client = SpaceTrackClient()
    return _client


def is_spacetrack_available() -> bool:
    """Check if Space-Track is configured and accessible."""
    client = get_client()
    return client.is_configured()


def get_space_objects(force_refresh: bool = False) -> List[SpaceObject]:
    """
    Get space objects - from cache or fresh API call.

    This is the main function for the website to use.
    It automatically handles caching and rate limits.

    Args:
        force_refresh: If True, ignore cache and fetch fresh data

    Returns:
        List of SpaceObject
    """
    client = get_client()

    if not force_refresh and is_cache_valid():
        return load_from_cache()

    if client.is_configured():
        return client.fetch_comprehensive_catalog(force_refresh=force_refresh)

    # No credentials, try cache anyway
    return load_from_cache()


def get_objects_by_type(object_type: str = None) -> List[SpaceObject]:
    """
    Get space objects filtered by type.

    Args:
        object_type: PAYLOAD, ROCKET BODY, DEBRIS, or None for all

    Returns:
        Filtered list of SpaceObject
    """
    objects = get_space_objects()

    if object_type is None:
        return objects

    return [o for o in objects if o.object_type == object_type]


def get_debris() -> List[SpaceObject]:
    """Get all debris objects."""
    return get_objects_by_type("DEBRIS")


def get_satellites() -> List[SpaceObject]:
    """Get all satellite/payload objects."""
    return get_objects_by_type("PAYLOAD")


def get_rocket_bodies() -> List[SpaceObject]:
    """Get all rocket body objects."""
    return get_objects_by_type("ROCKET BODY")
