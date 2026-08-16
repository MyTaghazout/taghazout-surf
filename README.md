# taghazout-surf

A tiny, zero-dependency client for the **free Taghazout surf forecast feed** — 20 named
breaks on the Taghazout–Agadir coast in Morocco, no API key, no signup.

Python and JavaScript, MIT licensed. The feed is public and served from
[taghazout.io](https://taghazout.io), a free forecast and trip planner for the coast.

```bash
# Python (stdlib only)
python taghazout_surf.py anchor-point
# → Anchor Point: 0.66m @ 8.4s, wind 11.2 km/h, water 21.6°C, potential 82%

# Node 18+
node taghazout-surf.js imsouane
# → Imsouane Bay: 1.14m @ 8.4s, wind 21.3 km/h, water 21.1°C, potential 94%
```

## The endpoint

```
GET https://taghazout.io/weather-data/_feed.php?loc=<spot_key>
```

No key, no auth, JSON. Please cache for a few minutes rather than polling in a loop —
the underlying models only update every few hours anyway.

📖 **Full API reference:** [taghazout.gitbook.io/taghazout-docs](https://taghazout.gitbook.io/taghazout-docs/introduction)
· 📊 **Spot registry as a dataset:** [Hugging Face](https://huggingface.co/datasets/MyTaghazout/taghazout-surf-spots)

### Example

```bash
curl "https://taghazout.io/weather-data/_feed.php?loc=anchor-point"
```

```json
{
  "ok": true,
  "feed_type": "compact_surf_forecast_summary",
  "spot": { "key": "anchor-point", "name": "Anchor Point", "area": "North Taghazout" },
  "updated_at": "2026-08-16T16:00",
  "swell_m": 0.66,
  "period_s": 8.4,
  "swell_direction_deg": 319,
  "sea_state_m": 1.2,
  "wind_kmh": 11.2,
  "gust_kmh": 24.1,
  "water_temp_c": 21.6,
  "air_temp_c": 23.7,
  "surf_potential_percent": 82,
  "tide": { "label": "Rising tide", "trend": "rising", "height_m": 2.53 },
  "beginner_verdict": "...",
  "advanced_verdict": "..."
}
```

### Fields

| Field | Meaning |
|---|---|
| `swell_m` / `period_s` / `swell_direction_deg` | Decomposed swell components |
| `sea_state_m` | Total sea state (swell + wind wave), not the same as `swell_m` |
| `wind_wave_ratio` | How much of the sea state is local wind chop (higher = messier) |
| `wind_kmh` / `gust_kmh` | Wind at the break |
| `water_temp_c` / `air_temp_c` | Temperatures (3/2 wetsuit most of the year here) |
| `surf_potential_percent` | 0–100 score for the current window |
| `best_window` | The hours that earned the score today |
| `beginner_verdict` / `advanced_verdict` | Plain-language read for each level |
| `tide` | Modelled sea level — see the caveat below |
| `uv_index_max`, `moon`, `air_quality`, `sunrise`, `sunset` | Day context |

## Supported spots

`taghazout` · `anchor-point` · `hash-point` · `panorama` · `la-source` · `mysteries` ·
`killer-point` · `banana-point` · `devils-rock` · `cro-cro` · `km11` · `km12` ·
`boilers` · `dracula` · `tamri` · `anza` · `tamraght` · `agadir` · `imsouane` ·
`imsouane-cathedral`

Full registry with forecast pages: [`taghazout-surf-spots.csv`](./taghazout-surf-spots.csv)

## Honest caveats

- **Tide height is modelled sea level**, relative to the low point of the forecast
  window — it is *not* a harbour-gauge or chart-datum measurement.
- These are **models, not observations**. The site shows a confidence flag when
  Open-Meteo and NOAA WaveWatch III disagree; this compact feed gives you the blended
  read. Use local judgement before you paddle out.

## Data attribution

Weather data by [Open-Meteo.com](https://open-meteo.com/) (CC BY 4.0) ·
wave model **NOAA WaveWatch III** via [PacIOOS](https://www.pacioos.hawaii.edu/).
If you redistribute data from this feed, carry that attribution with it.

## Why this exists

I live on this coast and built [taghazout.io](https://taghazout.io) because there was no
straight answer to "is tomorrow worth it?" for these specific breaks. The feed is the
same data the site's own [forecast pages](https://taghazout.io/weather/) run on — opened
up so anyone can build with it.

MIT © taghazout.io
