# Method — how GOLIAT harmonizes MODIS and VIIRS hotspots

*Frozen on 2026-11-14 (hackathon day 1). Everything below is reproducible from `pipeline/` in this order: `download_firms.py` → `inventory.py` → `comunas.py` → `build_detections.py` → `build_monthly.py` → `build_mask.py` → `experiment.py` → `publish.py`.*

## 1. The question

MODIS (Terra/Aqua, 1 km, since 2000) and VIIRS (S-NPP, NOAA-20, NOAA-21, 375 m, since 2012) both detect active fires, but VIIRS sees roughly twice as many "events" at our counting unit. Stacking the two records produces a false jump in 2012. The question is not "can we put them in one table" but **"can a MODIS-only month be expressed in VIIRS units with an error we can measure, commune by commune?"**

## 2. Data contract (frozen before any fitting)

| Item | Decision |
|---|---|
| Inputs | NASA FIRMS archive CSVs by country (MODIS, VIIRS S-NPP, through 2025) + FIRMS area API (MODIS SP/NRT, VIIRS S-NPP/NOAA-20/NOAA-21 SP/NRT) for 2018→ NOAA platforms and for 2026. Full inventory with SHA-256 in `data/processed/inventory.csv`. |
| Territory | 54 communes of Biobío (08) and Ñuble (16). Polygons: geoBoundaries CHL ADM3 (gbOpen, 2020, derived from BCN). CUT codes from `chilean-territorial-divisions`. |
| Unit | **Cell-day**: a 0.01° (~1 km) cell with ≥ 1 daytime detection on a given day. Grid origin at 0°, cell = floor(coord / 0.01). Each cell belongs to exactly one commune (its centroid's commune). |
| Filters | `daynight = 'D'`; MODIS `confidence ≥ 30`; VIIRS `confidence ≠ 'l'`. These are processing choices, not an equivalence between the two confidence scales. |
| Source priority | Archive SP > API SP > NRT; duplicates removed on (platform, lat, lon, date, time). Months touched by NRT are flagged *provisional*. |
| Season | July–June, named by the starting year (2022 = Jul 2022–Jun 2023). |
| Static-source mask | Built on detections before 2020-07-01 (training period only). A cell is masked if (A) ≥ 30 detection days over ≥ 8 seasons, or (B) ≥ 10 days and ≥ 50 % of typed detections `type = 1` (volcano), or (C) ≥ 15 days and ≥ 60 % typed `type = 2`; plus the 8 neighbours of any A/B cell with ≥ 100 days. 167 cells. Applied identically to SP and NRT. Effect 2013–2019: removes 9.0 % of Aqua cell-days, 1.9 % of S-NPP, 43.7 % of Terra (urban/industrial morning pass); Talcahuano loses 94 % (refinery). |
| Platforms | Reference: **VIIRS S-NPP daytime**. Terra, night-time passes and NOAA-21 are outside the published series. |

## 3. Experiment

**Partitions.** Training + internal selection: seasons 2012–2019 (8). Final test: 2020–2021 (seen once). 2022 onward: Aqua's orbit drifts; used only as diagnostic. Months 2020-08 and 2020-09 are excluded from both sensors (Aqua outage 16 Aug – 2 Sep 2020).

**Target.** Monthly S-NPP cell-days per commune. **Predictor.** Monthly Aqua cell-days per commune.

| Role | Method | Question it answers |
|---|---|---|
| Diagnostic | M0: raw Aqua | How wrong is "just stack them"? |
| Minimal reference | M1: one regional constant factor r = ΣVIIRS/ΣAqua over training | Is a single scale enough? |
| Temporal control | M2: VIIRS monthly climatology per commune (mean over training seasons, **no Aqua**) | Does MODIS add anything beyond "the usual month"? |
| Candidate A | Factor per month-group (Sep…May single, Jun–Aug pooled) with regional shrinkage: r_c,g = (V_c,g + κ·r_R,g) / (A_c,g + κ); κ ∈ {0, 10, 30, 50, 100, 300, ∞} chosen by leave-one-season-out | Does seasonal calibration beat the constant? |
| Candidate B | Regularized affine regression | **Not evaluated** (time). Declared. |

**Results (leave-one-season-out on training, mean absolute error summed over 54 communes × 8 seasons):**

| M0 | M1 | M2 | A(κ=100, best) |
|---|---|---|---|
| 1 126.8 | **913.5** | 1 633.3 | 914.7 |

**Final test 2020–2021, regional monthly MAE:** M0 133 · **M1 44.1** · M2 86.1 · A 45.4.

**Reading.** The seasonal factor ties with the constant one (0.1 % difference); the extra parameters buy nothing at commune scale. MODIS does carry temporal information: both calibrated methods halve the error of the VIIRS climatology. We therefore publish the **simplest method, M1: r = 2.337**.

**Disclosure.** The decision to publish M1 instead of A was taken *after* the final test block had been looked at with A. The final-test numbers for M1 are therefore not a strictly independent evaluation; the choice rests on the training-only LOSO comparison, where the tie was already visible.

## 4. Publication gates (project rules, not NASA standards)

| Gate | Rule | Result |
|---|---|---|
| Temporal contribution | M1 beats M2 (climatology) on commune MAE | checked per commune |
| Stability | M1 beats M2 in ≥ 6 of the 8 LOSO seasons | checked per commune |
| **Enabled** | both | **36 of 54 communes** get a 2002–2012 estimate; the other 18 show "not enabled" and only observed VIIRS from July 2012 |
| Uncertainty | band = ± the commune's mean absolute error of M1 in LOSO | shown on every estimated cell |
| Recent platform | NOAA-20 vs S-NPP bridge, seasons 2018–2024: annual ratio 0.94–1.06, monthly MAPE 12–29 % | pass; factor 1.0 declared |
| Categories | anomaly categories (low/normal/high) would need an 80 %-stability test we did not run | **no categories shown**; values and percentiles only |
| Territory | cell → single commune; regional totals are sums of communes | pass |
| Integrity | screen, print view and CSV read the same JSON | by construction |

Not enabled: Lota, Santa Juana, Lebu, Contulmo, Los Álamos, Los Ángeles, Cabrero, Nacimiento, Negrete, Santa Bárbara, Chillán, Bulnes, Pinto, Yungay, Ninhue, Treguaco, Ránquil, San Fabián. Two patterns: communes where Aqua saw very little in 2012–2019 (Lota 12 cell-days, Lebu 36, Negrete 43), and communes where the climatology is already as good as the calibrated MODIS (Los Ángeles, Chillán, Bulnes, Pinto: MAE within 5 %). Santa Juana fails only the stability rule (5 of 8 seasons).

## 5. The published series

- **Observed:** S-NPP for seasons 2012–2017, NOAA-20 for 2018 onward (so the current season stays on one platform; S-NPP ended 2026-11-02).
- **Estimated:** Aqua × 2.337 for July 2002 – June 2012, only in enabled communes, with the ± band.
- **Season comparison:** current season's cumulative cell-days through the cut-off month, against the same months of every observed season since 2012 (median, p25, p75, p90). Same territory, same months, observed data only.
- **Recurrence map:** per commune, each cell's number of seasons with ≥ 1 daytime VIIRS detection since 2012 (after the mask). Observed only; no harmonization involved.

## 6. Limits we state in the app

- A detection is not a fire and a cell-day is not a hectare (FIRMS FAQ).
- We do not measure observation opportunity: a month with zero detections may be cloudy, not fire-free.
- 2002–2012 is extrapolation: performance in the overlap does not prove small historical fires are recovered. Before 2002-07 (Terra only) nothing is shown.
- NRT months are provisional; FIRMS replaces NRT with standard processing after ~5 months.
- Agricultural burns and wildfires are both "fire activity"; we do not separate them.
- No alerts, no forecasts. For emergencies: CONAF and SENAPRED.

## 7. Reviews

An automated, read-only scientific review (checklist C1–C20 of the preparation repo) was run on 2026-11-14 over this pipeline; its findings and what we changed are in `docs/reviews/`.
