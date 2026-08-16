/**
 * taghazout-surf — a tiny zero-dependency client for the free Taghazout surf
 * forecast feed (Node 18+ / any modern browser, uses global fetch).
 *
 * The feed is public, keyless and covers 20 named breaks on the
 * Taghazout–Agadir coast in Morocco.
 *
 *   import { getSpot, SPOTS } from './taghazout-surf.js';
 *   const now = await getSpot('anchor-point');
 *   console.log(now.spot.name, now.swell_m, 'm @', now.period_s, 's');
 *
 * CLI:  node taghazout-surf.js anchor-point
 *
 * Data: weather by Open-Meteo.com (CC BY 4.0); wave model NOAA WaveWatch III
 * via PacIOOS. Tide height is modelled sea level relative to the low point of
 * the forecast window, not a harbour-gauge reading. Use local judgement.
 *
 * MIT licensed.
 */

export const FEED_URL = 'https://taghazout.io/weather-data/_feed.php';

/** The 20 breaks the feed covers: spot key -> display name. */
export const SPOTS = {
  'taghazout': 'Taghazout Bay',
  'anchor-point': 'Anchor Point',
  'hash-point': 'Hash Point',
  'panorama': 'Panorama Point',
  'la-source': 'La Source',
  'mysteries': 'Mysteries',
  'killer-point': 'Killer Point',
  'banana-point': 'Banana Point',
  'devils-rock': "Devil's Rock",
  'cro-cro': 'Cro-Cro',
  'km11': 'KM11',
  'km12': 'KM12',
  'boilers': 'Boilers',
  'dracula': "Dracula's",
  'tamri': 'Tamri',
  'anza': 'Anza',
  'tamraght': 'Tamraght',
  'agadir': 'Agadir Beach',
  'imsouane': 'Imsouane Bay',
  'imsouane-cathedral': 'Imsouane Cathedral',
};

/** Fetch the current compact forecast summary for one break. */
export async function getSpot(spot = 'taghazout', { timeoutMs = 15000 } = {}) {
  if (!(spot in SPOTS)) {
    throw new Error(`unknown spot "${spot}" — try one of: ${Object.keys(SPOTS).sort().join(', ')}`);
  }

  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  let response;
  try {
    response = await fetch(`${FEED_URL}?loc=${encodeURIComponent(spot)}`, {
      signal: controller.signal,
      headers: { 'User-Agent': 'taghazout-surf-js/1.0.0' },
    });
  } catch (err) {
    throw new Error(`could not reach the feed: ${err.message}`);
  } finally {
    clearTimeout(timer);
  }

  if (!response.ok) throw new Error(`feed returned HTTP ${response.status}`);
  const payload = await response.json();
  if (!payload.ok) throw new Error(`feed reported a problem for "${spot}"`);
  return payload;
}

/** One human-readable line from a feed payload. */
export function summarise(payload) {
  return `${payload.spot?.name ?? 'unknown spot'}: ${payload.swell_m}m @ ${payload.period_s}s, `
       + `wind ${payload.wind_kmh} km/h, water ${payload.water_temp_c}°C, `
       + `potential ${payload.surf_potential_percent}%`;
}

// CLI entry point when run directly with Node.
if (typeof process !== 'undefined' && process.argv?.[1]?.endsWith('taghazout-surf.js')) {
  const spot = process.argv[2] ?? 'taghazout';
  if (spot === '--list' || spot === '-l') {
    for (const [key, name] of Object.entries(SPOTS)) console.log(key.padEnd(22), name);
  } else {
    getSpot(spot)
      .then((data) => console.log(summarise(data)))
      .catch((err) => { console.error(`error: ${err.message}`); process.exitCode = 1; });
  }
}
