import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { readVerifiedDocument } from '../web/src/observed-data.mjs';
const base = new URL('../observed/dist/', import.meta.url);
const sha = bytes => createHash('sha256').update(bytes).digest('hex');
const index = JSON.parse(readFileSync(new URL('data/publication/index.json', base)));

test('all 54 commune documents verify and preserve distinct platforms and units', async () => {
  assert.equal(index.communes.length, 54);
  assert.deepEqual(index.verified, { months_verified: 29322, csv_verified: 162, detections_verified: 119232 });
  for (const entry of index.communes) {
    const bytes = readFileSync(new URL(entry.url.replace('/observed/', ''), base));
    const doc = await readVerifiedDocument(new Response(bytes), entry.sha256);
    assert.equal(doc.commune.cut, entry.cut);
    assert.equal(doc.unit, 'cell_days_per_platform');
    assert.equal(doc.harmonization, 'none');
    assert.deepEqual(doc.sources.map(s => s.id), ['aqua-history', 'snpp-history', 'noaa20-history']);
    for (const source of doc.sources) {
      assert.equal(source.series[0].month, source.start);
      assert.equal(source.series.at(-1).month, '2025-12');
      assert.equal(new Set(source.series.map(r => r.month)).size, source.series.length);
      const csv = readFileSync(new URL(source.csv.url.replace('/observed/', ''), base));
      assert.equal(sha(csv), source.csv.sha256);
      assert.equal(source.series.reduce((n, r) => n + (r.detections ?? 0), 0), source.csv.rows);
      for (const row of source.series) assert.equal(row.observation_coverage, 'unknown');
    }
  }
});

test('reader blocks corrupt data, incompatible units, and HTTP failures', async () => {
  const bytes = readFileSync(new URL('data/publication/08107.json', base));
  await assert.rejects(readVerifiedDocument(new Response(bytes), '0'.repeat(64)), /SHA-256/);
  const doc = JSON.parse(bytes); doc.unit = 'celldays_viirs_scale';
  const wrong = JSON.stringify(doc);
  await assert.rejects(readVerifiedDocument(new Response(wrong), sha(wrong)), /contract/);
  await assert.rejects(readVerifiedDocument(new Response('unavailable', { status: 503 }), sha(bytes)), /503/);
});

test('published harmonization retains observed January–June 2013 in every commune', () => {
  const harmonized = JSON.parse(readFileSync(new URL('../web/public/data/index.json', import.meta.url)));
  for (const entry of harmonized.comunas) {
    const doc = JSON.parse(readFileSync(new URL(`../web/public/data/comunas/${entry.cut}.json`, import.meta.url)));
    const months = doc.series.filter(r => r.y === 2013 && r.m <= 6);
    assert.equal(months.length, 6);
    for (const row of months) { assert.equal(row.state, 'observed'); assert.equal(row.sat, 'SNPP'); }
  }
});
