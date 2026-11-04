"""Parsing and lookup. The single entry point is `analyze(ip, user_agent)`.

It never raises: anything it can't work out comes back as None / "unknown".
"""
import ipaddress
import logging
from dataclasses import dataclass
from functools import lru_cache

from user_agents import parse as parse_ua

from core.config import get_settings

log = logging.getLogger("tracker")


@dataclass
class Analysis:
    ip_truncated: str | None
    browser_name: str | None
    browser_version: str | None
    os_name: str | None
    os_version: str | None
    device_type: str  # mobile | tablet | desktop | bot | unknown
    country: str | None
    region: str | None
    city: str | None


def truncate_ip(ip: str | None) -> str | None:
    """IPv4: zero the last two octets. IPv6: keep the first 48 bits."""
    if not ip:
        return None
    try:
        addr = ipaddress.ip_address(ip)
    except ValueError:
        return None
    prefix = 16 if addr.version == 4 else 48
    return str(ipaddress.ip_network(f"{ip}/{prefix}", strict=False).network_address)


def _is_public(ip: str | None) -> bool:
    if not ip:
        return False
    try:
        return ipaddress.ip_address(ip).is_global
    except ValueError:
        return False


@lru_cache
def _geo_reader():
    path = get_settings().geoip_db_path
    try:
        import geoip2.database

        return geoip2.database.Reader(path)
    except Exception as exc:  # file missing, corrupt, etc.
        log.warning("GeoIP database not available (%s). Locations will be empty.", exc)
        return None


def lookup_location(ip: str | None) -> tuple[str | None, str | None, str | None]:
    """Returns (country, region, city); all None when unknown."""
    if not _is_public(ip):
        return None, None, None
    reader = _geo_reader()
    if reader is None:
        return None, None, None
    try:
        r = reader.city(ip)
        region = r.subdivisions.most_specific.name if r.subdivisions else None
        return r.country.name, region, r.city.name
    except Exception:  # address not in the database, etc.
        return None, None, None


def parse_user_agent(user_agent: str | None) -> dict:
    empty = dict(browser_name=None, browser_version=None, os_name=None,
                 os_version=None, device_type="unknown")
    if not user_agent:
        return empty
    try:
        ua = parse_ua(user_agent)
        if ua.is_bot:  # check bots first: many bots also look like phones
            device = "bot"
        elif ua.is_tablet:
            device = "tablet"
        elif ua.is_mobile:
            device = "mobile"
        elif ua.is_pc:
            device = "desktop"
        else:
            device = "unknown"
        return dict(
            browser_name=ua.browser.family,
            browser_version=ua.browser.version_string.split(".")[0] or None,
            os_name=ua.os.family,
            os_version=ua.os.version_string or None,
            device_type=device,
        )
    except Exception as exc:
        log.warning("User-Agent parsing failed: %s", exc)
        return empty


def analyze(ip: str | None, user_agent: str | None) -> Analysis:
    country, region, city = lookup_location(ip)  # look up the full IP, then truncate
    return Analysis(
        ip_truncated=truncate_ip(ip),
        country=country,
        region=region,
        city=city,
        **parse_user_agent(user_agent),
    )
