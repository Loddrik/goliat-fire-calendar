# GOLIAT — Harmonized Fire Activity Calendar for Biobío and Ñuble

> NASA Space Apps Challenge 2026 · Concepción, Chile · Challenge: *Harmonization of MODIS and VIIRS Hot Spots*

Official statistics count where a fire started, two seasons late. Satellites show where it burned, month by month, up to last week. **GOLIAT harmonizes 24 years of MODIS and VIIRS active-fire detections (NASA FIRMS) into one fire activity calendar for every commune in Biobío and Ñuble.**

Work started on 2026-11-14 at 09:00 local time, when the hackathon opened.

## Structure

- `pipeline/` — Python + DuckDB: download, cleaning, harmonization, validation, pre-aggregation.
- `web/` — TypeScript + Vite: map, calendar, indicators, CSV export.
- `docs/` — method, decisions and sources.
- `data/raw/` — FIRMS downloads (not versioned). `data/processed/` — harmonized outputs.

## Data

- NASA FIRMS (MODIS C6.1 and VIIRS 375 m active fire products, SP and NRT). We acknowledge the use of data from NASA's Fire Information for Resource Management System (FIRMS), part of NASA's Earth Science Data and Information System (ESDIS).
- CONAF, Chile — wildfire occurrence by commune, 1985–2024.

## License

Apache 2.0. See `LICENSE`.

## Use of AI

Claude Code (Anthropic) was used to write code, research sources and run read-only reviewer agents (scientific, product and jury checklists). All numbers shown by the app are computed by the deterministic pipeline; no AI model generates figures.
