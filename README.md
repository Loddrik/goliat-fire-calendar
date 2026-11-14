# GOLIAT — Harmonized Fire Activity Calendar for Biobío and Ñuble

> NASA Space Apps Challenge 2026 · Concepción, Chile · Challenge: *Harmonization of MODIS and VIIRS Hot Spots*
> **Live app:** https://goliat-fire-calendar-production.up.railway.app

**GOLIAT brings MODIS and VIIRS active-fire detections (NASA FIRMS) into a commune-level activity calendar for Biobío and Ñuble**, and shows plainly which months are observed, which are estimated, and where the estimate is not good enough to publish. Detections describe observed thermal activity; they do not measure burned area or count individual fires.

The integrated **FireChronos platform-history view** preserves the independently verified annual archive through 2025, official DPA 2023 boundaries, source hashes and downloadable metadata. It keeps Aqua, S-NPP and NOAA-20 separate and does not apply the harmonization factor. [Open platform history](https://goliat-fire-calendar-production.up.railway.app/?view=observed) · [Integration contract and verification](docs/integracion-firechronos.md).

Work started on 2026-11-14 at 09:00 local time, when the hackathon opened. Everything here was built in the 48-hour window.

## What it answers

1. In which months does detected fire activity usually concentrate in this commune?
2. How does the current season compare with previous ones, over the same territory and up to the same cut-off?

Plus a **recurrence map**: which ~1 km cells of the commune had detections in how many seasons since 2012 — "this already happened here".

For whom: municipal emergency / planning officers who must characterize the wildfire hazard in their communal risk-reduction plan (today copied by hand from a CONAF table two seasons old), community leaders and landowners preparing before the season, and researchers who need a reproducible commune-level series. **Not** an alert and **not** a forecast.

## How the harmonization works (short)

Unit: 0.01° cells with ≥ 1 daytime detection per day, after a fixed mask of industrial/volcanic sources. Reference: VIIRS S-NPP. MODIS Aqua months are converted with a single regional factor (r = 2.35) fitted on 2012–2019. Four methods were compared on held-out seasons (raw Aqua, constant factor, VIIRS climatology without Aqua, monthly factor with shrinkage); the constant factor tied with the monthly one and reduces the error of the climatology, so the simplest method is published. Per commune, the estimate is **enabled only where Aqua has ≥ 50 cell-days and the constant factor beats both the VIIRS climatology and raw Aqua in ≥ 6 of 8 cross-validated seasons** (14 of 54 communes; the rest show observed VIIRS from 2012 only). Full details, numbers and disclosures: [`docs/method.md`](docs/method.md).

## Repository

```
pipeline/   Python + DuckDB (uv). Run in order:
            download_firms.py → inventory.py → comunas.py → build_detections.py →
            build_monthly.py → build_mask.py → experiment.py → publish.py
web/        React + Vite + MapLibre. Reads the JSON that publish.py writes to web/public/data/.
observed/   Preserved FireChronos explorer, scripts, tests and observed archive (DPA 2023).
server.mjs  Express: serves web/dist and the per-commune detection CSVs. Deployed on Railway from main.
docs/       Method, decisions, reviews.
data/raw/   FIRMS downloads (not versioned). data/processed/ harmonization outputs.
```

Reproduce: `uv sync && uv run python pipeline/<step>.py` (needs `FIRMS_MAP_KEY` in `.env` for `download_firms.py`); `npm install && npm run build && npm start`.

## Data and sources

- **NASA FIRMS** — MODIS Collection 6.1 and VIIRS 375 m active fire products, standard (SP) and near-real-time (NRT). *We acknowledge the use of data and/or imagery from NASA's Fire Information for Resource Management System (FIRMS) (https://earthdata.nasa.gov/firms), part of NASA's Earth Science Data and Information System (ESDIS).*
- Commune boundaries: geoBoundaries CHL ADM3 (gbOpen, 2020; derived from Biblioteca del Congreso Nacional de Chile). CUT codes: `chilean-territorial-divisions` (npm).
- Basemap: OpenFreeMap (OpenStreetMap contributors).
- Platform-history view: NASA FIRMS annual country archives, daytime Type=0; official DPA 2023 (SUBDERE / IDE Chile), with source and normalized-geometry hashes. Different filters/geography from the harmonized view; the two series must not be spliced together.
- User research (what municipal officers, residents, firefighters and researchers in Biobío/Ñuble actually lack) and the design rationale live in the preparation repo and are summarized in `docs/`.

## License

Apache 2.0. See `LICENSE`.

## Verify the integrated publication

```sh
python3 pipeline/publish_observed.py
npm install
npm test
npm run build
npm start
```

Python publication regressions require DuckDB and Pandas from `pyproject.toml`: `uv run python -m unittest discover -s tests -p 'test_*.py' -v`. `publish.py` can regenerate harmonized JSON from versioned Parquet and GeoJSON without ignored raw files. Non-finite diagnostics are represented as `null` in browser JSON and listed under `unavailable_metrics`; original diagnostics remain unchanged. See [`observed/README.md`](observed/README.md) for full raw-data reproduction.

## Use of AI

OpenAI Codex was used to integrate the preserved FireChronos code and data, implement the observed-history view and publication contract, and run regression and browser checks. The integration corrects JSON serialization and the seasonal date window; it does not refit the harmonization model. Its code and review are versioned here.

Claude Code (Anthropic, Claude Opus / Fable models) was used throughout: to write the pipeline and web code, to search and summarize public sources for the user research, and to run read-only reviewer agents (scientific, product and jury checklists) against the method and the app. **All numbers shown by GOLIAT are computed by the deterministic pipeline in `pipeline/`; no AI model generates, estimates or rewrites any figure.** An external human reviewer (a friend of the author) reviewed the project manifesto on day 1; his revision shaped the gates and the scope.
