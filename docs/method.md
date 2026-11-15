# Method — how GOLIAT harmonizes MODIS and VIIRS hotspots

*Frozen on 2026-11-14 (hackathon day 1); gates revised the same day after an independent scientific review (`docs/reviews/`). The pipeline execution order is: `download_firms.py` → `inventory.py` → `comunas.py` → `build_detections.py` → `build_monthly.py` → `build_mask.py` → `experiment.py` → `publish.py`.* The processed-input experiments and their reproduction evidence are versioned. The 1,071 raw FIRMS CSVs listed in the inventory are absent from this checkout, so complete raw ingestion has not been reproduced here; see the [reconstruction audit](reviews/2026-11-14-baseline-reconstruction.md).

## 1. The question

MODIS (Terra/Aqua, 1 km, since 2000) and VIIRS (S-NPP, NOAA-20, NOAA-21, 375 m, since 2012) both detect active fires, but their sampling and sensitivity differ. In this pilot, the pooled training ratio of S-NPP to Aqua cell-days is about 2.35; it is not a ratio of individual fires. Stacking the records can introduce an instrumental jump in 2012. The question is not "can we put them in one table" but **"can a MODIS-only month be expressed in VIIRS units with an error we can measure, commune by commune?"**

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
| Static-source mask | Built on all available detections before 2020-07-01, including Terra before July 2002; this mask history is longer than the model-calibration pool 2012–2019. A cell is masked if (A) ≥ 30 detection days over ≥ 8 seasons, or (B) ≥ 10 days and ≥ 50 % of typed detections `type = 1` (volcano), or (C) ≥ 15 days and ≥ 60 % typed `type = 2`; plus the 8 neighbours of any A cell with ≥ 100 days and the two rings (24 cells) around every B cell (volcanic activity migrates between neighbouring cells; a leak at Nevados de Chillán was found in review). 223 cells. Applied identically to SP and NRT. Effect 2013–2019: removes 9.1 % of Aqua cell-days, 1.9 % of S-NPP, 43.7 % of Terra; Talcahuano loses 94 % (refinery/steelworks). **Rule A also catches town-centre cells (San Carlos, Curanilahue, Cabrero, Mulchén, Quirihue) with 100–300 Terra-only days and almost no VIIRS days. This pattern suggests possible morning-pass urban contamination; it does not independently confirm false alarms, industry, or the absence of genuine fire.** |
| Platforms | Reference: **VIIRS S-NPP daytime**. Terra (morning pass, different diurnal phase), night-time passes and NOAA-21 are outside the published series. Before July 2002 (Terra only) nothing is shown. |

## 3. Experiment

**Partitions.** Training + internal selection: seasons 2012–2019 (8). Original evaluation block: 2020–2021, now descriptive because it has been consulted during development. Seasons 2022 onward: diagnostic only. Aqua began free drift in January 2022, so January–June 2022 already falls inside season 2021; [iteration 11](reviews/2026-11-14-scientific-review-11.md) marks that transition explicitly. Months 2020-08 and 2020-09 are excluded from both sensors (Aqua outage 16 Aug – 2 Sep 2020).

**Target.** Monthly S-NPP cell-days per commune. **Predictor.** Monthly Aqua cell-days per commune.

| Role | Method | Question it answers |
|---|---|---|
| Diagnostic | M0: raw Aqua | How wrong is "just stack them"? |
| Minimal reference | M1: one regional constant factor r = ΣVIIRS/ΣAqua over training | Is a single scale enough? |
| Temporal control | M2: VIIRS monthly climatology per commune (**median** over training seasons, **no Aqua**) | Does MODIS add anything beyond "the usual month"? |
| Candidate A | Factor per month-group (Sep…May single, Jun–Aug pooled) with regional shrinkage r_c,g = (V_c,g + κ·r_R,g)/(A_c,g + κ); κ ∈ {0, 10, 30, 50, 100, 300, ∞} by leave-one-season-out (LOSO) | Does seasonal/local calibration beat the constant? |
| Candidate B | Regularized affine regression | **Development only:** nested evaluation in [iteration 3](reviews/2026-11-14-scientific-review-3.md); not part of the published series. |

**LOSO on training (MAE summed over 54 communes × 8 seasons):** M0 1 080.6 · **M1 881.2** · M2 1 335.2 · A(κ=100) 880.7.

**Reading.** A and M1 tie (0.05 %). MODIS carries temporal information: both calibrated methods beat the climatology by a third. We publish the simplest, **M1: r = 2.353**. Per-season r in training ranges 2.22–2.75 (CV 8 %); after 2020: 2.32, 2.91, 2.01, 2.25, 2.40, 2.88 (Aqua drift and megafire years — reported, not used).

**Method selection — disclosure.** Two candidates were compared by LOSO on 2012–2019 only and tied. We had pre-committed to evaluate A on the original 2020–2021 block, then chose M1 for parsimony after consulting that block. Those figures are **descriptive, not an independent test**; all published per-commune enablement decisions use LOSO only. The block has since been reused for scientific diagnostics. [Iteration 11](reviews/2026-11-14-scientific-review-11.md) reproduces the current frozen inputs and every commune-level control in `eval_final.csv`: regional monthly MAE is **M0 132.7, M1 45.7, M2 82.7, A(κ=100) 45.6**. These replace the previously quoted 133/44/86/45 figures, which do not all reproduce from the current data. No factor or publication gate changes.

## 4. Publication gates (project rules, not NASA standards)

A commune's 2002–2012 estimate is **enabled** only if, in LOSO on 2012–2019:

1. Aqua recorded ≥ 50 cell-days in the commune (otherwise "winning" means predicting ~0 against an almost empty series);
2. M1 beats the VIIRS climatology (M2) in ≥ 6 of 8 held-out seasons (temporal contribution);
3. M1 beats raw Aqua (M0) in ≥ 6 of 8 held-out seasons (the correction must reduce the disagreement, otherwise it is not harmonization).

**Result: 14 of 54 communes enabled** — Tomé, Arauco, Cañete, Tirúa, Los Ángeles, Quilaco, Bulnes, El Carmen, San Ignacio, Quirihue, Coelemu, San Carlos, Coihueco, Ñiquén.

Why the other 40 are not: 14 have too little Aqua (coastal/urban communes: Penco, Coronel, Talcahuano, Hualpén, Lota, Lebu…); 14 do not beat the climatology stably (Santa Juana, Cabrero, Nacimiento, Quillón, Chillán Viejo…); 12 beat the climatology but **not raw Aqua** (Mulchén, Florida, Hualqui, Chillán, Pinto, Yungay, Alto Biobío…) — in those communes the local VIIRS/Aqua ratio is far below the regional 2.35, which is a clear sign that a single regional factor is too coarse there. Subsequent nested per-commune selection was evaluated in iterations 2–15. Candidate A improves overall development MAE only 0.63 %; more flexible models have larger gains with important transport and subgroup limitations. Their diagnostic gate counts do not authorize additional published communes; the current decision is documented in the [research review](reviews/2026-11-14-research-decision.md).

| Other gate | Rule | Result |
|---|---|---|
| Uncertainty | band = ± the commune's mean absolute LOSO error of M1 in active months | shown on every estimated cell as **"typical error"**. Empirical coverage of ±1·MAE: 70 % of active months (88 % at ±2·MAE); median relative error 35 % in months with ≥ 10 cell-days. **It is not a confidence band.** |
| Recent platform | NOAA-20 vs S-NPP, complete seasons 2018–2025: annual ratio 0.935–1.063. The [iteration 7 audit](reviews/2026-11-14-scientific-review-7.md) finds pooled calendar-month ratios 0.831–1.170 (January–July); the previously quoted 0.96–1.20 range is not reproduced under this explicit window/mask. | factor 1.0 remains a declared regional approximation; local equivalence is not established (monthly commune WAPE 28.84 %) |
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
- **Seasonal reconstructed totals:** an internal audit of the existing fixed-mask LOSO predictions for the 14 enabled communes (112 commune-seasons, July–June seasons2012–2019) finds median absolute relative error20.34% and mean signed relative error−11.46%. These are apparent postselection development diagnostics: the same LOSO selected the communes. They do not independently validate2002–2011 totals, an annual error band or the cause of the2012 transition. Monthly enablement does not certify seasonal-total accuracy. See the [seasonal audit and issue48 response](reviews/2026-11-15-season-total-report.md).
- The mask was calibrated with data to June 2020; newer static sources (or renewed volcanic activity) may leak.
- NRT months are provisional. Agricultural burns and wildfires are both "fire activity"; we do not separate them.
- No alerts, no forecasts. For emergencies: CONAF and SENAPRED.

## 7. Reviews

An automated, read-only scientific review (checklist C1–C20 of the preparation repo) ran on 2026-11-14 at ~16:00 over the first version of this pipeline. It found wrong CUT keys for Ñuble, a bug dropping Jul–Dec 2012, gates that used the final test block and admitted communes with ~0 Aqua, a volcanic leak in the mask, inflated recurrence, and a partial-month comparison. That review led to the corrections documented in `docs/reviews/2026-11-14-scientific-review.md`. A remaining seasonal date-window error and invalid JSON serialization were subsequently corrected in PR #22; see `docs/integracion-firechronos.md` for that publication history.

**Development audit, iteration 2:** [`2026-11-14-scientific-review-2.md`](reviews/2026-11-14-scientific-review-2.md) reproduces these published figures and measures the effect of fitting the mask inside each validation fold. M1's summed MAE changes from 881.17 to 884.41 (+0.37 %) with the same 14 diagnostic gates. Nested per-commune M1/A selection improves the point estimate by only 0.63 %, with a season-block interval spanning zero; it does not justify replacing M1. The 70 % typical-error coverage above is an apparent internal calculation over all 54 communes, rather than an independent coverage guarantee for the published subset. The audit leaves the current production parameters and JSON unchanged and documents the evidence needed before any update.

**Development experiment, iteration 3:** [`2026-11-14-scientific-review-3.md`](reviews/2026-11-14-scientific-review-3.md) evaluates affine candidate B with training-only normalization, priors and masks inside nested season-wise validation. M1/B reduces development MAE by 7.04 % and passes 15 diagnostic commune gates, including Mulchén. Almost all net error reduction occurs where Aqua is positive; improvement on Aqua=0/VIIRS>0 is nearly offset by estimates added where both sensors record zero. This is a promising development result, not independent historical validation. Production still uses M1 and its existing gates.

**Frozen temporal diagnostic, iteration 11:** [`2026-11-14-scientific-review-11.md`](reviews/2026-11-14-scientific-review-11.md) freezes full 2012–2019 coefficients, per-commune choices and nested-OOF band radii, and restores them exactly from checked artifacts before evaluating later data. The candidates improve the aggregate 2020–2021 discrepancy descriptively, but all four candidate policies deteriorate in season 2025 (July 2025–June 2026). For the existing 14 enabled communes, the rounded published typical-error band covers 64.1 % of active S-NPP months in 2020–2021 and 69.1 % in seasons 2022–2025; it is not an 80 % or 95 % guarantee. Research q80 bands are wider and also lack guaranteed future coverage. No candidate, radius or gate is automatically published.

**Scale-aware band experiment, iteration 12:** [`2026-11-14-scientific-review-12.md`](reviews/2026-11-14-scientific-review-12.md) reproduces the existing point and interval controls in strict nested folds and compares absolute, square-root and relative radii at the same nominal q80 calibration. Square-root scaling reduces M1/B active-month interval loss by 15.00 % and improves it in all eight development seasons, while shifting coverage away from low-activity months toward high-activity months. It does not guarantee 80 % coverage, validate historical observation opportunity or replace the published MAE band. Both width and missed-observation distance are reported, with all fifteen combinations preserved.

**Calibration population × shape, iteration 13:** [`2026-11-14-scientific-review-13.md`](reviews/2026-11-14-scientific-review-13.md) compares all eight predeclared combinations for M1 and M1/B with fixed square-root scale and unchanged points. Neither empirical asymmetry nor switching to calibration on all months improves the primary all-month interval loss over the symmetric/active control. Asymmetry helps some Aqua=0/S-NPP>0 months but loses coverage in zero-detection months. These recipes remain development only; no public interval semantics change.

**Separate Terra predictor, iteration 14:** [`2026-11-14-scientific-review-14.md`](reviews/2026-11-14-scientific-review-14.md) tests Aqua+Terra as two regularized predictors, with a seasonal-Terra ablation and strict nested/blocked controls. Adding the tested C family to M1/B increases nested MAE by 1.21 % and is unfavorable in seven of eight seasons; small later-period gains do not justify replacing B or M1. Terra is never summed with Aqua as event counts. All existing publication gates and values remain unchanged.


## Ajuste de extremos por pérdida — etapa 15

[Revisión completa](reviews/2026-11-14-scientific-review-15.md): la optimización directa de intervalos raíz mejora los cuantiles asimétricos de igual cohorte en 8/8 folds, pero no domina la referencia simétrica en todos los destinos. Diez recetas conservadas, 85 tests y controles anteriores reproducidos; sin cambio de publicación ni cobertura garantizada.


## Decisión y reproducción acumulada

[Decisión científica](reviews/2026-11-14-research-decision.md): conservar M1 y las 14 compuertas; mejoras retrospectivas no equivalen a transporte ni cobertura garantizada. Dos checkouts reproducen 118 resultados de las etapas 2–15, el segundo con entorno nuevo desde uv.lock y 88 tests. [Reconstrucción adicional](reviews/2026-11-14-baseline-reconstruction.md): agregados y parámetros coinciden; el orden no determinado de recurrencia impide igualdad estricta de los 54 JSON comunales. La ingestión FIRMS cruda no se ha reproducido porque faltan sus 1.071 CSV.
