import { useEffect, useState } from 'react';
import type { Lang } from './i18n';
import { download } from './csv';
import { readVerifiedDocument } from './observed-data.mjs';
import { MONTHS_SEASON, seasonLabel } from './types';

type Commune = { cut: string; name: string; region: string };
type ObservedMonth = { month: string; detections: number | null; cell_days: number | null; status: string; observation_coverage: string };
type ObservedSource = { id: string; title: string; platform: string; instrument: string; start: string; end: string; versions: string[];
  csv: { url: string; sha256: string; rows: number }; series: ObservedMonth[] };
export interface ObservedDoc {
  schema_version: number; product: string; unit: string; harmonization: string;
  commune: Commune; sources: ObservedSource[]; geography: unknown; grid: unknown; filters: unknown;
  limitations: string[]; source_manifest_sha256: string;
}
type ObservedIndex = { communes: (Commune & { url: string; sha256: string })[] };

const text = {
  es: {
    title: 'Historia observada por plataforma',
    intro: 'Explora el archivo anual de NASA FIRMS con límites oficiales DPA 2023. Cada plataforma conserva su propia serie; estos valores no están armonizados.',
    platform: 'Plataforma', start: 'Desde', end: 'Hasta', loading: 'Cargando y verificando el historial…',
    error: 'No se pudo verificar el historial. No se muestran resultados. Intenta recargar la página.',
    retry: 'Reintentar', monthly: 'CSV de la consulta', metadata: 'Metadatos de la consulta (JSON)', raw: 'CSV original de esta plataforma (todo el período)',
    calendar: 'Calendario observado', month: 'Mes', season: 'Temporada', detections: 'Detecciones', cells: 'Celdas-día',
    state: 'Estado', missing: 'Archivo no disponible', zero: 'Sin detecciones; cobertura desconocida', detected: 'Con detecciones; cobertura desconocida',
    invalid: 'Elige un rango mensual dentro del archivo disponible, con inicio anterior al fin.',
    limits: 'Cómo leer esta vista',
    notes: ['Una detección no equivale a un incendio. Una celda-día no equivale a una hectárea.',
      '0 indica que el archivo no contiene detecciones seleccionadas ese mes. No mide cobertura satelital ni demuestra ausencia de fuego. — indica archivo faltante o mes fuera de la consulta.',
      'Se usan detecciones diurnas, confianza MODIS ≥ 30 o VIIRS nominal/alta y Type=0 (vegetación presumida). La máscara persistente de GOLIAT no se aplica aquí.',
      'El historial anual termina en diciembre de 2025. Las muestras recientes NRT permanecen en el explorador original y no se concatenan con esta serie.',
      'Esta vista usa DPA 2023 fija, distinta de geoBoundaries/BCN de la reconstrucción. Comparar las cifras directamente requiere reconciliar límites y filtros.'],
    version: 'Versiones del producto', versionWarning: 'Aqua contiene versiones distintas. Su equivalencia todavía no ha sido evaluada.',
    full: 'Abrir el explorador original de FireChronos', source: 'Fuentes: NASA FIRMS · SUBDERE / IDE Chile, DPA 2023',
    scope: 'El calendario y el CSV de consulta usan el rango elegido. El CSV original incluye todo el período de esta plataforma y comuna.',
    verified: 'Integridad SHA-256 verificada', noData: 'No hay meses en este rango.',
  },
  en: {
    title: 'Observed history by platform',
    intro: 'Explore NASA FIRMS annual archives using official DPA 2023 boundaries. Each platform keeps its own series; these values are not harmonized.',
    platform: 'Platform', start: 'From', end: 'Through', loading: 'Loading and verifying history…',
    error: 'History could not be verified. No results are shown. Try reloading the page.',
    retry: 'Retry', monthly: 'Query CSV', metadata: 'Query metadata (JSON)', raw: 'Original platform CSV (entire period)',
    calendar: 'Observed calendar', month: 'Month', season: 'Season', detections: 'Detections', cells: 'Cell-days',
    state: 'Status', missing: 'File unavailable', zero: 'No detections; coverage unknown', detected: 'Detections present; coverage unknown',
    invalid: 'Choose a monthly range within the available archive, with the start before the end.',
    limits: 'How to read this view',
    notes: ['A detection is not a fire. A cell-day is not a hectare.',
      '0 means the file contains no selected detections for that month. It does not measure satellite coverage or establish absence of fire. — indicates a missing file or a month outside the query.',
      'Daytime only, MODIS confidence ≥ 30 or VIIRS nominal/high, Type=0 (presumed vegetation). The GOLIAT persistence mask is not applied here.',
      'The annual archive ends in December 2025. Recent NRT samples remain in the original explorer, separate from this series.',
      'This view uses fixed DPA 2023 boundaries, different from geoBoundaries/BCN used in the reconstruction. Direct numerical comparison requires reconciling boundaries and filters.'],
    version: 'Product versions', versionWarning: 'Aqua contains different versions. Their equivalence has not yet been evaluated.',
    full: 'Open the original FireChronos explorer (Spanish)', source: 'Sources: NASA FIRMS · SUBDERE / IDE Chile, DPA 2023',
    scope: 'The calendar and query CSV use your selected range. The original CSV includes the entire period for this platform and commune.',
    verified: 'SHA-256 integrity verified', noData: 'No months in this range.',
  },
};
const months = { es: ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic'],
  en: ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'] };
const csvCell = (value: unknown) => '"' + String(value ?? '').replaceAll('"', '""') + '"';

export function ObservedHistory({ cut, lang }: { cut: string; lang: Lang }) {
  const [index, setIndex] = useState<ObservedIndex | null>(null);
  const [doc, setDoc] = useState<ObservedDoc | null>(null);
  const [sourceId, setSourceId] = useState('noaa20-history');
  const [range, setRange] = useState({ start: '', end: '' });
  const [error, setError] = useState(false);
  const [attempt, setAttempt] = useState(0);
  const t = text[lang];

  useEffect(() => {
    const controller = new AbortController();
    setError(false);
    fetch('/observed/data/publication/index.json', { signal: controller.signal, cache: 'no-cache' })
      .then(r => { if (!r.ok) throw new Error('index'); return r.json(); })
      .then(setIndex).catch(() => { if (!controller.signal.aborted) setError(true); });
    return () => controller.abort();
  }, [attempt]);
  useEffect(() => {
    if (!index) return;
    const controller = new AbortController();
    setDoc(null); setError(false);
    const entry = index.communes.find(c => c.cut === cut);
    if (!entry) { setError(true); return; }
    fetch(entry.url, { signal: controller.signal, cache: 'no-cache' })
      .then(r => readVerifiedDocument(r, entry.sha256))
      .then(result => {
        if (controller.signal.aborted) return;
        if (result.commune.cut !== cut) throw new Error('commune');
        setDoc(result);
      }).catch(() => { if (!controller.signal.aborted) setError(true); });
    return () => controller.abort();
  }, [cut, index]);
  const source = doc?.commune.cut === cut ? doc.sources.find(s => s.id === sourceId) : undefined;
  useEffect(() => {
    if (source) setRange({ start: source.start, end: source.end });
  }, [source]);

  if (error) return <section className="card" role="alert"><p>{t.error}</p><button onClick={() => { setIndex(null); setDoc(null); setAttempt(a => a + 1); }}>{t.retry}</button></section>;
  if (!source || !doc) return <p role="status">{t.loading}</p>;
  const valid = range.start >= source.start && range.end <= source.end && range.start <= range.end && !!range.start && !!range.end;
  const rows = valid ? source.series.filter(r => r.month >= range.start && r.month <= range.end) : [];
  const byMonth = new Map(rows.map(r => [r.month, r]));
  const seasons = [...new Set(rows.map(r => { const [y, m] = r.month.split('-').map(Number); return m >= 7 ? y : y - 1; }))];
  const max = Math.max(1, ...rows.map(r => r.cell_days ?? 0));
  const status = (r: ObservedMonth) => r.cell_days === null ? t.missing : r.cell_days === 0 ? t.zero : t.detected;
  const prefix = `goliat_observed_${cut}_${source.id}_${range.start}_${range.end}`;
  const metadata = { schema_version: 1, product: doc.product, unit: doc.unit, harmonization: doc.harmonization,
    commune: doc.commune, source: { id: source.id, platform: source.platform, instrument: source.instrument, versions: source.versions },
    query: range, geography: doc.geography, filters: doc.filters, grid: doc.grid, limitations: doc.limitations,
    source_manifest_sha256: doc.source_manifest_sha256, raw_csv: { ...source.csv, scope: 'entire platform/commune archive, not query range' } };
  const exportCsv = () => {
    const header = ['cut','commune','source_id','platform','month','detections','cell_days','status','observation_coverage','unit','harmonization','geography'];
    const data = rows.map(r => [cut, doc.commune.name, source.id, source.platform, r.month, r.detections, r.cell_days, r.status, r.observation_coverage, doc.unit, 'none', 'DPA 2023']);
    download(prefix + '.csv', [header, ...data].map(r => r.map(csvCell).join(',')).join('\r\n') + '\r\n');
  };
  return <section className="observed-history" aria-labelledby="observed-title">
    <div className="titlebar"><h2 id="observed-title">{doc.commune.name} <small>{doc.commune.region} · CUT {cut}</small></h2><span className="badge ok">{t.verified}</span></div>
    <section className="card">
      <h2>{t.title}</h2><p>{t.intro}</p>
      <div className="observed-controls no-print">
        <label>{t.platform}<select id="observed-platform" value={sourceId} onChange={e => setSourceId(e.target.value)}>{doc.sources.map(s => <option key={s.id} value={s.id}>{s.instrument} · {s.platform}</option>)}</select></label>
        <label>{t.start}<input id="observed-start" type="month" min={source.start} max={source.end} value={range.start} onChange={e => setRange(r => ({ ...r, start: e.target.value }))} /></label>
        <label>{t.end}<input id="observed-end" type="month" min={source.start} max={source.end} value={range.end} onChange={e => setRange(r => ({ ...r, end: e.target.value }))} /></label>
      </div>
      <p className="help">{source.instrument} · {source.platform} · {range.start} → {range.end} · DPA 2023 · {t.cells} / UTC</p>
      <p className="help">{t.version}: {source.versions.join(', ')}. {source.instrument === 'MODIS' && t.versionWarning}</p>
      {!valid && <p role="alert">{t.invalid}</p>}
      <div className="tools observed-exports no-print">
        <button disabled={!valid} onClick={exportCsv}>{t.monthly}</button>
        <button disabled={!valid} onClick={() => download(prefix + '.json', JSON.stringify(metadata, null, 2), 'application/json;charset=utf-8')}>{t.metadata}</button>
        <a className="btn" href={source.csv.url} download>{t.raw}</a>
      </div><p className="help">{t.scope}</p>
    </section>
    {valid && <section className="card"><h2>{t.calendar}</h2>
      <p className="help">{t.notes[0]} {t.notes[1]}</p>
      <div className="calendar"><p className="swipe-hint no-print">{lang === 'es' ? 'Desliza la tabla hacia el lado para ver todos los meses →' : 'Swipe the table sideways to see every month →'}</p><table data-testid="observed-calendar"><caption className="sr">{doc.commune.name} · {source.platform} · {range.start} → {range.end} · {t.cells}</caption>
        <thead><tr><th>{t.season}</th>{MONTHS_SEASON.map(m => <th key={m} scope="col">{months[lang][m - 1]}</th>)}</tr></thead>
        <tbody>{seasons.map(s => <tr key={s}><th scope="row">{seasonLabel(s)}</th>{MONTHS_SEASON.map(m => {
          const month = `${m >= 7 ? s : s + 1}-${String(m).padStart(2, '0')}`;
          const r = byMonth.get(month); const v = r?.cell_days;
          const bg = v ? `rgba(42,120,142,${0.12 + 0.68 * Math.log1p(v) / Math.log1p(max)})` : undefined;
          const label = `${month} · ${source.platform} · ${v ?? '—'} ${t.cells} · ${r ? status(r) : t.missing}`;
          return <td key={m} data-month={month} className={`cell ${v == null ? 'not_enabled' : ''}`} style={{ backgroundColor: bg, color: v && bg && Math.log1p(v) / Math.log1p(max) > 0.65 ? '#fff' : undefined }} title={label} aria-label={label}>{v?.toLocaleString(lang === 'es' ? 'es-CL' : 'en-US') ?? '—'}</td>;
        })}</tr>)}</tbody>
      </table></div>{!rows.length && <p>{t.noData}</p>}
      <details className="observed-table"><summary>{t.monthly} · {rows.length} {lang === 'es' ? 'meses' : 'months'}</summary>
        <table><thead><tr>{[t.month, t.detections, t.cells, t.state].map(h => <th key={h} scope="col">{h}</th>)}</tr></thead>
          <tbody>{rows.map(r => <tr key={r.month}><th scope="row">{r.month}</th><td>{r.detections ?? '—'}</td><td>{r.cell_days ?? '—'}</td><td>{status(r)}</td></tr>)}</tbody></table>
      </details>
    </section>}
    <section className="card"><h2>{t.limits}</h2><ul>{t.notes.map(note => <li key={note}>{note}</li>)}</ul>
      <p><a href="https://firms.modaps.eosdis.nasa.gov/">NASA FIRMS</a> · <a href="https://geoportal.cl/geoportal/catalog/36391/division-politica-administrativa-2023">DPA 2023 · SUBDERE / IDE Chile</a></p>
      <a href="/observed/index.html">{t.full}</a>
    </section>
  </section>;
}
