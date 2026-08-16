"""
taghazout_surf — a tiny Python client for the free Taghazout surf forecast feed.

The feed is public, keyless and covers 20 named breaks on the Taghazout–Agadir
coast in Morocco: https://taghazout.io/weather-data/_feed.php?loc=anchor-point

Usage:
    from taghazout_surf import get_spot, list_spots, SPOTS

    now = get_spot("anchor-point")
    print(now["spot"]["name"], now["swell_m"], "m @", now["period_s"], "s")
    print("surf potential:", now["surf_potential_percent"], "%")

CLI:
    python taghazout_surf.py anchor-point

Data: weather by Open-Meteo.com (CC BY 4.0); wave model NOAA WaveWatch III via
PacIOOS. Tide height is modelled sea level relative to the low point of the
forecast window — not a harbour-gauge reading. Use local judgement before you
paddle out.

MIT licensed.
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.parse
import urllib.request

__version__ = "1.0.0"

FEED_URL = "https://taghazout.io/weather-data/_feed.php"

#: The 20 breaks the feed covers, as spot_key -> human name.
SPOTS = {
    "taghazout": "Taghazout Bay",
    "anchor-point": "Anchor Point",
    "hash-point": "Hash Point",
    "panorama": "Panorama Point",
    "la-source": "La Source",
    "mysteries": "Mysteries",
    "killer-point": "Killer Point",
    "banana-point": "Banana Point",
    "devils-rock": "Devil's Rock",
    "cro-cro": "Cro-Cro",
    "km11": "KM11",
    "km12": "KM12",
    "boilers": "Boilers",
    "dracula": "Dracula's",
    "tamri": "Tamri",
    "anza": "Anza",
    "tamraght": "Tamraght",
    "agadir": "Agadir Beach",
    "imsouane": "Imsouane Bay",
    "imsouane-cathedral": "Imsouane Cathedral",
}


class TaghazoutFeedError(RuntimeError):
    """Raised when the feed cannot be read or returns ok=false."""


def list_spots() -> dict[str, str]:
    """Return the supported spot keys mapped to their display names."""
    return dict(SPOTS)


def get_spot(spot: str = "taghazout", timeout: int = 15) -> dict:
    """Fetch the current compact forecast summary for one break.

    Args:
        spot: a key from SPOTS, e.g. "anchor-point".
        timeout: seconds to wait for the response.

    Returns:
        The decoded feed payload (see README for the field list).

    Raises:
        TaghazoutFeedError: on network failure, bad JSON, or ok=false.
    """
    if spot not in SPOTS:
        raise TaghazoutFeedError(
            f"unknown spot {spot!r} — try one of: {', '.join(sorted(SPOTS))}"
        )

    url = f"{FEED_URL}?loc={urllib.parse.quote(spot)}"
    request = urllib.request.Request(
        url, headers={"User-Agent": f"taghazout-surf-python/{__version__}"}
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError) as exc:
        raise TaghazoutFeedError(f"could not reach the feed: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise TaghazoutFeedError(f"feed returned invalid JSON: {exc}") from exc

    if not payload.get("ok"):
        raise TaghazoutFeedError(f"feed reported a problem for {spot!r}")
    return payload


def summarise(payload: dict) -> str:
    """One human-readable line from a feed payload."""
    name = payload.get("spot", {}).get("name", "unknown spot")
    return (
        f"{name}: {payload.get('swell_m', '?')}m @ {payload.get('period_s', '?')}s, "
        f"wind {payload.get('wind_kmh', '?')} km/h, "
        f"water {payload.get('water_temp_c', '?')}°C, "
        f"potential {payload.get('surf_potential_percent', '?')}%"
    )


def _main(argv: list[str]) -> int:
    spot = argv[1] if len(argv) > 1 else "taghazout"
    if spot in ("-h", "--help"):
        print(__doc__)
        return 0
    if spot in ("-l", "--list"):
        for key, name in SPOTS.items():
            print(f"{key:<22} {name}")
        return 0
    try:
        print(summarise(get_spot(spot)))
    except TaghazoutFeedError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv))
