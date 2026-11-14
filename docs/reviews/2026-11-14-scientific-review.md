# Scientific review #1 — 2026-11-14 ~16:00 (automated, read-only reviewer agent)

**Verdict:** method PASSES WITH OBSERVATIONS; the first list of enabled communes and the CUT keys DID NOT PASS. Nothing was published before the fixes below.

| # | Finding | Severity | What we changed |
|---|---|---|---|
| 1 | 15 Ñuble CUT codes shifted (source: npm table). Polygons matched names, keys did not. | blocking for any join | Replaced with official DPA codes; pipeline re-run from `comunas.py`. |
| 2 | `experiment.py` dropped Jul–Dec 2012 despite a comment saying otherwise. | numbers change | Line removed. r: 2.337 → 2.353. |
| 3 | Per-commune enablement used the final test block; communes with ~0 Aqua (Hualpén 0, Talcahuano 2…) were "enabled"; no check against raw Aqua (raw beat corrected in 23/54 communes). | gates invalid | Gates now LOSO-only: Aqua ≥ 50 cell-days, beats climatology ≥ 6/8, beats raw Aqua ≥ 6/8. Enabled: 36 → **14**. |
| 4 | "± MAE" is not a confidence band (coverage ~50 % of active months in reviewer's replication). | wording | Renamed "typical error"; coverage computed and published (70 % / 88 % at ±2·MAE after fixes); never called confidence. |
| 5 | Nevados de Chillán leak: ~74 cell-days in 8 cells within 4 km after the mask. | mask | Two rings around every volcanic (B) cell, no day threshold. Mask: 167 → 223 cells. |
| 6 | Rule-A cells outside Talcahuano are town centres with Terra-only detections (urban morning false alarms), not industry. | wording | Stated in method and mask docstring. |
| 7 | Recurrence counted S-NPP ∪ NOAA-20 → ~50 % inflation from 2018. | numbers change | One platform per season, same rule as the series. |
| 8 | Season comparison compared a partial November with full Novembers. | numbers change | Every season truncated to the same day of the same month as the cut-off. |
| 9 | M2 used the mean; median is the proper control for MAE and is stronger. | control | M2 = median. M1 still wins. |
| 10 | NOAA-20 bridge range is 0.93–1.06 (not 0.94–1.06); July ratio 1.20 on tiny counts. | wording | Stated. |
| 11 | Document Terra exclusion, UTC day handling, night/SAA, filter sensitivity, r by season, p90 weakness. | documentation | Added to `method.md`. |

Not addressed (declared): candidate B (affine) not run; no per-commune method selection (would likely rescue the 12 communes that beat climatology but not raw Aqua); no CONAF cross-check yet; `type = 2` jump in 2018 (likely MODIS collection version change) not verified.
