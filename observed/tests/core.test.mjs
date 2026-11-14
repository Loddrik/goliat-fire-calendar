import test from "node:test";
import assert from "node:assert/strict";
import { parseCSV, normalizeRows, selectRows, summarize, csvText, observedMonths } from "../dist/core.mjs";
const base = { latitude: "-36.5", longitude: "-72.5", acq_date: "2026-11-14", acq_time: "105", instrument: "MODIS", satellite: "Aqua", confidence: "80", daynight: "D" };
test("CSV quoted fields, BOM, CRLF, multiline and round trip", () => {
  const row = { ...base, note: 'contiene, coma y "comillas"\nsalto' };
  const csv = "\uFEFF" + csvText([row], Object.keys(row));
  assert.deepEqual(parseCSV(csv).rows, [row]);
});
test("rejects malformed CSV structure and duplicate headers", () => {
  assert.throws(() => parseCSV("latitude,longitude,acq_date\n-36,-72,2026-11-14,extra"));
  assert.throws(() => parseCSV("latitude,longitude,acq_date\n\"-36,-72,2026-11-14"));
  assert.throws(() => parseCSV("latitude,longitude,acq_date,latitude\n"));
});
test("does not convert empty coordinates or impossible dates into observations", () => {
  const result = normalizeRows([base, { ...base, latitude: "" }, { ...base, acq_date: "2026-02-30" }, { ...base, acq_time: "2460" }, { ...base, longitude: "NaN" }]);
  assert.equal(result.valid.length, 1);
  assert.equal(result.rejected.length, 4);
});
test("applies day, instrument confidence and bbox exclusions separately", () => {
  const rows = normalizeRows([base, { ...base, daynight: "N" }, { ...base, confidence: "29" }, { ...base, latitude: "-30" }, { ...base, instrument: "VIIRS", confidence: "l" }, { ...base, instrument: "VIIRS", confidence: "n" }]).valid;
  const result = selectRows(rows, { bbox: { west: -73.9, east: -71, south: -38.9, north: -35.8 } });
  assert.equal(result.selected.length, 2);
  assert.equal(result.excludedNightOrUnknown, 1);
  assert.equal(result.excludedConfidence, 2);
  assert.equal(result.excludedBbox, 1);
});
test("deduplicates occupied cell-days within platform without merging satellites", () => {
  const rows = normalizeRows([base, { ...base }, { ...base, acq_time: "1305" }, { ...base, acq_date: "2026-11-15" }, { ...base, satellite: "Terra" }]);
  assert.equal(rows.duplicates, 1);
  const summary = summarize(rows.valid);
  const aqua = summary.monthly.find(group => group.platform === "Aqua");
  assert.equal(aqua.detections, 4);
  assert.equal(aqua.cellDays, 2);
  assert.equal(summary.monthly.length, 2);
});
test("grid assignment is deterministic at 0.01-degree boundaries", () => {
  const summary = summarize(normalizeRows([base, { ...base, longitude: "-72.50000000000001" }, { ...base, longitude: "-72.49" }]).valid);
  assert.equal(summary.monthly[0].cellDays, 2);
});
test("empty observed selection has no fabricated dates", () => {
  assert.deepEqual(summarize([]), { count: 0, dateMin: null, dateMax: null, monthly: [] });
});
test("months distinguish no detections from a missing yearly file", () => {
  const rows = observedMonths([{ month: "2023-02", detections: 3, cellDays: 2 }], {
    start: "2023-01", end: "2024-01", availableYears: [2023], instrument: "MODIS", platform: "Aqua" });
  assert.equal(rows[0].detections, 0);
  assert.equal(rows[0].status, "no-detections-coverage-unknown");
  assert.equal(rows[1].cellDays, 2);
  assert.equal(rows[12].detections, null);
  assert.equal(rows[12].status, "missing-file");
});
test("observed monthly completion never merges platforms silently", () => {
  assert.throws(() => observedMonths([{ month: "2023-02" }, { month: "2023-02" }], {
    start: "2023-01", end: "2023-03", availableYears: [2023], instrument: "VIIRS", platform: "N" }));
});
test("invalid calendar months are rejected before completion", () => {
  for (const start of ["2023-00", "2023-13", "2023-1"]) {
    assert.throws(() => observedMonths([], { start, end: "2024-01", availableYears: [2023, 2024] }));
  }
});
