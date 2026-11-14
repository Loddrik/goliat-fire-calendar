# Method — how GOLIAT harmonizes MODIS and VIIRS hotspots

*Frozen on 2026-11-14 (hackathon day 1); gates revised the same day after an independent scientific review (`docs/reviews/`). Everything below is reproducible from `pipeline/` in this order: `download_firms.py` → `inventory.py` → `comunas.py` → `build_detections.py` → `build_monthly.py` → `build_mask.py` → `experiment.py` → `publish.py`.*

## 1. The question

MODIS (Terra/Aqua, 1 km, since 2000) and VIIRS (S-NPP, NOAA-20, NOAA-21, 375 m, since 2012) both detect active fires, but VIIRS sees roughly 2.3× as many "events" at our counting unit. Stacking the two records produces a false jump in 2012. The question is not "can we put them in one table" but **"can a MODIS-only month be expressed in VIIRS units with an error we can measure, commune by commune?"**

## 2. Data contract (frozen before any fitting)

| Item | Decision |
|---|---|
| Inputs | NASA FIRMS archive CSVs by country (MODIS, VIIRS S-NPP, through 2025) + FIRMS area API (MODIS SP/NRT, VIIRS S-NPP/NOAA-20/NOAA-21 SP/NRT) for NOAA platforms and for 2026. Inventory with SHA-256 in `data/processed/inventory.csv`. Cut-off: 2026-11-13. |
| Territory | 54 communes of Biobío (08) and Ñuble (16). Polygons: geoBoundaries CHL ADM3 (gbOpen 2020, derived from BCN). CUT codes: official DPA (SUBDERE/INE). |
| Unit | **Cell-day**: a 0.01° (~1 km) cell with ≥ 1 daytime detection on a given day. Grid origin at 0°, cell = floor(coord / 0.01). Each cell belongs to exactly one commune (its centroid's commune). |
| Day | `daynight = 'D'`, date as given by FIRMS (UTC). The daytime pass over Chile is ~17–19 UTC, i.e. the same local calendar day, so no shift is applied. Night passes are excluded, which also avoids the South Atlantic Anomaly and night-time parallax issues. |
| Filters | MODIS `confidence ≥ 30`; VIIRS `confidence ≠ 'l'`. Processing choices, not an equivalence between scales. Sensitivity: r = 2.334 keeping low-confidence VIIRS vs 2.353 without — insensitive. |
| Source priority | Archive SP > API SP > NRT; duplicates removed on (platform, lat, lon, date, time). Months touched by NRT are flagged *provisional* (FIRMS replaces NRT with standard processing after ~5 months). |
| Season | July–June, named by the starting year (2022 = Jul 2022–Jun 2023). |
| Static-source mask | Built on detections before 2020-07-01 (training period only). A cell is masked if (A) ≥ 30 detection days over ≥ 8 seasons, or (B) ≥ 10 days and ≥ 50 % of typed detections `type = 1` (volcano), or (C) ≥ 15 days and ≥ 60 % typed `type = 2`; plus the 8 neighbours of any A cell with ≥ 100 days and the two rings (24 cells) around every B cell (volcanic activity migrates between neighbouring cells; a leak at Nevados de Chillán was found in review). 223 cells. Applied identically to SP and NRT. Effect 2013–2019: removes 9.1 % of Aqua cell-days, 1.9 % of S-NPP, 43.7 % of Terra; Talcahuano loses 94 % (refinery/steelworks). **Rule A outside the Talcahuano–Hualpén industrial pole catches town centres (San Carlos, Curanilahue, Cabrero, Mulchén, Quirihue) with 100–300 Terra-only days and almost no VIIRS days: these are urban false alarms of the MODIS morning pass, not industry.** |
| Platforms | Reference: **VIIRS S-NPP daytime**. Terra (morning pass, different diurnal phase), night-time passes and NOAA-21 are outside the published series. Before July 2002 (Terra only) nothing is shown. |

## 3. Experiment

**Partitions.** Training + internal selection: seasons 2012–2019 (8). Final test: 2020–2021. 2022 onward: Aqua's orbit drifts; diagnostic only. Months 2020-08 and 2020-09 excluded from both sensors (Aqua outage 16 Aug – 2 Sep 2020).

**Target.** Monthly S-NPP cell-days per commune. **Predictor.** Monthly Aqua cell-days per commune.

| Role | Method | Question it answers |
|---|---|---|
| Diagnostic | M0: raw Aqua | How wrong is "just stack them"? |
| Minimal reference | M1: one regional constant factor r = ΣVIIRS/ΣAqua over training | Is a single scale enough? |
| Temporal control | M2: VIIRS monthly climatology per commune (**median** over training seasons, **no Aqua**) | Does MODIS add anything beyond "the usual month"? |
| Candidate A | Factor per month-group (Sep…May single, Jun–Aug pooled) with regional shrinkage r_c,g = (V_c,g + κ·r_R,g)/(A_c,g + κ); κ ∈ {0, 10, 30, 50, 100, 300, ∞} by leave-one-season-out (LOSO) | Does seasonal/local calibration beat the constant? |
| Candidate B | Regularized affine regression | **Not evaluated** (time). Declared. |

**LOSO on training (MAE summed over 54 communes × 8 seasons):** M0 1 080.6 · **M1 881.2** · M2 1 335.2 · A(κ=100) 880.7.

**Reading.** A and M1 tie (0.05 %). MODIS carries temporal information: both calibrated methods beat the climatology by a third. We publish the simplest, **M1: r = 2.353**. Per-season r in training ranges 2.22–2.75 (CV 8 %); after 2020: 2.32, 2.91, 2.01, 2.25, 2.40, 2.88 (Aqua drift and megafire years — reported, not used).

**Method selection — disclosure.** Two candidates were compared by LOSO on 2012–2019 only and tied. We had pre-committed to evaluate A on the held-out 2020–2021 seasons and did so once (regional monthly MAE: M0 133, M1 44, M2 86, A 45). We then chose M1 for parsimony. Because that choice was made after seeing the held-out block, 2020–2021 figures for M1 are **descriptive, not an independent test**; all per-commune enablement decisions use LOSO only.

## 4. Publication gates (project rules, not NASA standards)

A commune's 2002–2012 estimate is **enabled** only if, in LOSO on 2012–2019:

1. Aqua recorded ≥ 50 cell-days in the commune (otherwise "winning" means predicting ~0 against an almost empty series);
2. M1 beats the VIIRS climatology (M2) in ≥ 6 of 8 held-out seasons (temporal contribution);
3. M1 beats raw Aqua (M0) in ≥ 6 of 8 held-out seasons (the correction must reduce the disagreement, otherwise it is not harmonization).

**Result: 14 of 54 communes enabled** — Tomé, Arauco, Cañete, Tirúa, Los Ángeles, Quilaco, Bulnes, El Carmen, San Ignacio, Quirihue, Coelemu, San Carlos, Coihueco, Ñiquén.

Why the other 40 are not: 14 have too little Aqua (coastal/urban communes: Penco, Coronel, Talcahuano, Hualpén, Lota, Lebu…); 14 do not beat the climatology stably (Santa Juana, Cabrero, Nacimiento, Quillón, Chillán Viejo…); 12 beat the climatology but **not raw Aqua** (Mulchén, Florida, Hualqui, Chillán, Pinto, Yungay, Alto Biobío…) — in those communes the local VIIRS/Aqua ratio is far below the regional 2.35, which is a clear sign that a single regional factor is too coarse there. A local factor with shrinkage (candidate A) is the natural next step; we did not have time to run per-commune method selection with the same gates, so we publish nothing there rather than a number we cannot defend.

| Other gate | Rule | Result |
|---|---|---|
| Uncertainty | band = ± the commune's mean absolute LOSO error of M1 in active months | shown on every estimated cell as **"typical error"**. Empirical coverage of ±1·MAE: 70 % of active months (88 % at ±2·MAE); median relative error 35 % in months with ≥ 10 cell-days. **It is not a confidence band.** |
| Recent platform | NOAA-20 vs S-NPP, seasons 2018–2025: annual ratio 0.93–1.06; monthly 0.96–1.20 (1.20 in July, where counts are tiny) | pass; factor 1.0 declared |
| Categories | anomaly labels would need an 80 %-stability test we did not run | **no categories**; values and percentiles only (p90 over 14 seasons is weak and labelled as such) |
| Territory | cell → single commune; regional totals are sums of communes | pass |
| Integrity | screen, print view and CSV read the same JSON | by construction |

## 5. The published series

- **Observed:** S-NPP for seasons 2012–2017, NOAA-20 for 2018 onward (one platform per season; S-NPP ended 2026-11-02).
- **Estimated:** Aqua × 2.353 for July 2002 – June 2012, only in the 14 enabled communes, with the typical-error band.
- **Season comparison:** the current season's cell-days from 1 July through the cut-off day (13 November 2026), against every observed season since 2012 **truncated to the same day of the same month**, same platform rule. Median, p25, p75, p90 of 14 seasons.
- **Recurrence map:** per commune, each cell's number of seasons with ≥ 1 daytime detection since 2012, with the same one-platform-per-season rule (summing S-NPP and NOAA-20 would inflate recent seasons by ~50 %). Observed only.

## 6. Limits we state in the app

- A detection is not a fire and a cell-day is not a hectare (FIRMS FAQ).
- We do not measure observation opportunity: a month with zero detections may be cloudy, not fire-free.
- 2002–2012 is extrapolation with a regional constant; typical relative error ~35 % in active months. Good performance in the overlap does not prove small historical fires are recovered.
- The mask was calibrated with data to June 2020; newer static sources (or renewed volcanic activity) may leak.
- NRT months are provisional. Agricultural burns and wildfires are both "fire activity"; we do not separate them.
- No alerts, no forecasts. For emergencies: CONAF and SENAPRED.

## 7. Reviews

An automated, read-only scientific review (checklist C1–C20 of the preparation repo) ran on 2026-11-14 at ~16:00 over the first version of this pipeline. It found wrong CUT keys for Ñuble, a bug dropping Jul–Dec 2012, gates that used the final test block and admitted communes with ~0 Aqua, a volcanic leak in the mask, inflated recurrence, and a partial-month comparison. All were fixed before anything was published; the review and the changes are in `docs/reviews/2026-11-14-scientific-review.md`.
