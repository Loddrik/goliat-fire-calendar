import { useEffect, useState } from "react";
import type { Text, Lang } from "./text";
import { dateLong, seasonLabel } from "./text";

// Las preguntas por comuna, en simple (#40): una tira de 12 meses con una frase, la temporada en curso
// como puntos (una temporada por punto, al mismo día) y las temporadas desde 2002 con sus tres estados
// (aproximado desde MODIS Aqua, observado VIIRS, sin estimación). Números leídos tal cual de
// web/public/data/ (regla 6): derived/<cut>.json (month_climatology, season_totals) y comunas/<cut>.json
// (season_compare). El detalle (rango, error típico por mes) queda en Explorar. Se monta con key={cut}.

type Clim = { m: number; n: number; median: number; p25: number; p75: number; max: number; seasons_with: number };
type SeasonTotal = { season: number; value: number | null; state: "estimated" | "observed" | "not_enabled"; complete: boolean; provisional: boolean };
type Derived = { cut: string; month_climatology: Clim[]; season_totals: SeasonTotal[] };
type Compare = { season: number; current: number; observed_seasons: Record<string, number>; median: number | null; n: number };
type Commune = { cut: string; comuna: string; cutoff: string; r_const: number; reconstruction_enabled: boolean; season_compare: Compare };

const ORDER = [7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6];
// Bajo este valor de mediana en el mes más alto, ningún mes se destaca (revisión científica #40: con 2 la
// frase de Hualqui y Negrete salía de medianas de 1–2 celdas-día).
const LOW = 3;
const SHADES = ["var(--b1)", "var(--b2)", "var(--b3)", "var(--b4)", "var(--b5)"];
const num = (v: number | null, lang: Lang) => (v == null ? "—" : v.toLocaleString(lang === "es" ? "es-CL" : "en-US", { maximumFractionDigits: 1 }));

/** Meses que se destacan: mediana ≥ la mitad del mes más alto. Hasta 3 «más alta»; más, «parecidas». */
export function highlight(medians: number[]) {
  const peak = Math.max(...medians);
  if (peak < LOW) return { kind: "low" as const, months: [] as number[], peak };
  const months = medians.map((v, i) => [v, i]).filter(([v]) => v >= peak / 2).map(([, i]) => i);
  return { kind: months.length > 3 ? ("spread" as const) : ("focus" as const), months, peak };
}

export function CommuneSample({ cut, t, lang }: { cut: string; t: Text; lang: Lang }) {
  const [derived, setDerived] = useState<Derived | null>(null);
  const [doc, setDoc] = useState<Commune | null>(null);
  const [error, setError] = useState(false);
  const [picked, setPicked] = useState<number | null>(null);

  useEffect(() => {
    const c = new AbortController();
    Promise.all([
      fetch(`/data/derived/${cut}.json`, { signal: c.signal, cache: "no-cache" }).then(r => { if (!r.ok) throw new Error(); return r.json(); }),
      fetch(`/data/comunas/${cut}.json`, { signal: c.signal, cache: "no-cache" }).then(r => { if (!r.ok) throw new Error(); return r.json(); }),
    ]).then(([d, k]) => { if (d.cut !== cut || k.cut !== cut) throw new Error(); setDerived(d); setDoc(k); })
      .catch(() => { if (!c.signal.aborted) setError(true); });
    return () => c.abort();
  }, [cut]);

  if (error) return <p className="lp-muted">{t.mapError}</p>;
  if (!derived || !doc) return <p className="lp-muted" aria-busy="true">{t.loading}</p>;

  const clim = ORDER.map(m => derived.month_climatology.find(c => c.m === m)).filter((c): c is Clim => !!c);
  const med = clim.map(c => c.median ?? 0);
  const h = highlight(med);
  const n = clim[0]?.n ?? 0;
  const sc = doc.season_compare;
  const years = Object.keys(sc.observed_seasons).map(Number).sort((a, b) => a - b);
  const a = seasonLabel(years[0]), b = seasonLabel(years[years.length - 1]);
  if (n !== sc.n) console.warn(`GOLIAT: n distinto entre derived (${n}) y season_compare (${sc.n}) en ${cut}`);

  // Mes que se describe abajo: el que se tocó, o el de mediana más alta (sin actividad: el con detección en más temporadas).
  const top = h.kind === "low" ? clim.reduce((best, c, i) => (c.seasons_with > clim[best].seasons_with ? i : best), 0) : med.indexOf(h.peak);
  const shown = picked ?? top;
  const sel = clim[shown];
  // En comunas con poca actividad el tono no llega al más oscuro: la escala parte en 2 × LOW.
  const scale = Math.max(h.peak, 2 * LOW);
  const shade = (v: number) => (v <= 0 ? "var(--b0)" : SHADES[Math.min(4, Math.floor((v / scale) * 5 - 1e-9))]);
  const names = h.months.map(i => t.monthsLong[i]);
  // El mes extremo: si el valor más alto de un solo mes cae fuera de los meses nombrados, se dice aparte.
  const maxes = clim.map(c => c.max ?? 0);
  const peakMax = Math.max(...maxes), peakMaxI = maxes.indexOf(peakMax);
  const showPeak = peakMax > 0 && !h.months.includes(peakMaxI);

  // Puntos de la temporada: cada temporada observada al mismo día; los valores iguales se apilan.
  const vals = years.map(y => sc.observed_seasons[String(y)]);
  const vmax = Math.max(4, sc.current, ...vals);
  const pos = (v: number) => `${(v / vmax) * 100}%`;
  const stack = vals.map((v, i) => vals.slice(0, i).filter(w => w === v).length);
  const lift = Math.max(0, ...stack) * 10;

  return (
    <div className="lp-sample">
      <article className="lp-q">
        <h3>{t.q1}</h3>
        <div className="lp-strip" role="group" aria-label={t.q1}>
          {clim.map((c, i) => (
            <button key={c.m} type="button" className={`lp-mo${h.months.includes(i) ? " hi" : ""}${shown === i ? " on" : ""}`}
              aria-pressed={shown === i} aria-label={t.monthAria(t.monthsLong[i], num(c.median, lang), c.seasons_with, c.n)}
              onClick={() => setPicked(i)}>
              <b style={{ background: shade(c.median ?? 0) }} />
              <span>{t.monthsShort[i]}</span>
            </button>
          ))}
        </div>
        <p className="lp-fact">{h.kind === "low" ? t.factLow(doc.comuna, num(LOW, lang)) : h.kind === "spread" ? t.factSpread(doc.comuna, names) : t.factFocus(doc.comuna, names)}</p>
        {showPeak && <p className="lp-peak">{t.factPeak(t.monthsLong[peakMaxI], num(peakMax, lang))}</p>}
        <p className="lp-pickline" aria-live="polite">{t.monthLine(t.monthsLong[shown], num(sel.median, lang), sel.seasons_with, sel.n)}</p>
        <p className="lp-note">{t.stripNote(n, a, b)}</p>
      </article>
      <article className="lp-q">
        <h3>{t.q2}</h3>
        <div className="lp-dots" aria-hidden="true" style={{ height: 70 + lift }}>
          <span className="lp-dots-cur-l" style={{ left: pos(sc.current) }}>{seasonLabel(sc.season)}: {num(sc.current, lang)}</span>
          <span className="lp-dots-axis" style={{ top: 34 + lift }} />
          {years.map((y, i) => <span key={y} className="lp-dot" style={{ left: pos(vals[i]), top: 28 + lift - stack[i] * 10 }} title={`${seasonLabel(y)}: ${vals[i]}`} />)}
          <span className="lp-dots-cur" style={{ left: pos(sc.current), height: 29 + lift }} />
          <span className="lp-dots-ax" style={{ left: 0, top: 52 + lift }}>0</span>
          <span className="lp-dots-ax" style={{ right: 0, top: 52 + lift }}>{vmax}</span>
        </div>
        <p className="lp-dots-key"><span><span className="lp-dot-k" aria-hidden="true" />{t.dotsKey(a, b)}</span><span><span className="lp-cur-k" aria-hidden="true" />{t.dotsCur(seasonLabel(sc.season))}</span></p>
        <p className="lp-q2">{t.q2sentence(doc.comuna, seasonLabel(sc.season), dateLong(doc.cutoff, lang), num(sc.current, lang), sc.n, a, b, sc.median == null ? null : num(sc.median, lang))}</p>
        <p className="lp-note">{t.q2note(sc.n)}</p>
        <a className="lp-btn lp-btn-primary" href={`/explorar?cut=${cut}&lang=${lang}`}>{t.open(doc.comuna)} <span aria-hidden="true">→</span></a>
      </article>
      <SeasonStrip totals={derived.season_totals} comuna={doc.comuna} enabled={doc.reconstruction_enabled} r={doc.r_const} t={t} lang={lang} />
    </div>
  );
}

/** Temporadas completas desde 2002 con sus tres estados, sin cifra en las barras (el error típico es por mes). */
function SeasonStrip({ totals, comuna, enabled, r, t, lang }: { totals: SeasonTotal[]; comuna: string; enabled: boolean; r: number; t: Text; lang: Lang }) {
  const full = totals.filter(s => s.complete || s.state === "not_enabled");
  const vmax = Math.max(1, ...full.map(s => s.value ?? 0));
  const stateName = (s: SeasonTotal) => t.seasonsKey[s.state === "estimated" ? 0 : s.state === "observed" ? 1 : 2];
  const first = full[0]?.season, last = full[full.length - 1]?.season;
  return (
    <article className="lp-q lp-q-wide">
      <h3>{t.seasonsTitle}</h3>
      <div className="lp-seasons" role="list" aria-label={first != null && last != null ? t.seasonsAria(comuna, seasonLabel(first), seasonLabel(last)) : undefined}>
        {full.map(s => (
          <div key={s.season} role="listitem" className={`lp-ss lp-ss-${s.state}${s.season === 2012 ? " lp-ss-start" : ""}`}>
            <span className="lp-sr">{t.seasonAria(seasonLabel(s.season), stateName(s), s.state === "observed" ? num(s.value, lang) : null)}</span>
            <div className="lp-ss-track" aria-hidden="true" title={s.state === "observed" ? `${seasonLabel(s.season)}: ${num(s.value, lang)}` : seasonLabel(s.season)}>
              {s.state === "not_enabled" ? <i>∅</i> : <b style={{ height: `${Math.max(2, ((s.value ?? 0) / vmax) * 100)}%` }} />}
            </div>
            <span className="lp-ss-y" aria-hidden="true">{s.season % 5 === 2 ? `’${String(s.season).slice(2)}` : ""}</span>
          </div>
        ))}
      </div>
      <p className="lp-ss-key" aria-hidden="true">
        {enabled && <span><i className="lp-ss-k lp-ss-k-est" />{t.seasonsKey[0]}</span>}
        <span><i className="lp-ss-k lp-ss-k-obs" />{t.seasonsKey[1]}</span>
        {!enabled && <span><i className="lp-ss-k lp-ss-k-ne">∅</i>{t.seasonsKey[2]}</span>}
      </p>
      <p className="lp-note">{enabled ? t.seasonsNoteOn(r.toLocaleString(lang === "es" ? "es-CL" : "en-US", { maximumFractionDigits: 2 })) : t.seasonsNoteOff}</p>
    </article>
  );
}
