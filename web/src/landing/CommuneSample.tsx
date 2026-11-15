import { useEffect, useState } from "react";
import type { Text, Lang } from "./text";
import { dateLong, seasonLabel } from "./text";

// Las dos preguntas por comuna, en simple (#40): una tira de 12 meses con una frase, y la temporada en
// curso como puntos (una temporada por punto, al mismo día). Números leídos tal cual de web/public/data/
// (regla 6): perfil desde derived/<cut>.json y comparación desde comunas/<cut>.json. El detalle (máximo,
// rango) queda en Explorar. Se monta con key={cut}, así cada comuna parte con estado limpio.

type Clim = { m: number; n: number; median: number; p25: number; p75: number; max: number; seasons_with: number };
type Derived = { cut: string; month_climatology: Clim[] };
type Compare = { season: number; current: number; observed_seasons: Record<string, number>; median: number | null; n: number };
type Commune = { cut: string; comuna: string; cutoff: string; season_compare: Compare };

const ORDER = [7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6];
// Bajo este valor de mediana en el mes más alto, ningún mes se destaca (comunas con poca actividad).
const LOW = 2;
const SHADES = ["var(--b1)", "var(--b2)", "var(--b3)", "var(--b4)", "var(--b5)"];
const num = (v: number | null, lang: Lang) => (v == null ? "—" : v.toLocaleString(lang === "es" ? "es-CL" : "en-US", { maximumFractionDigits: 1 }));

/** Meses que se destacan: mediana ≥ la mitad del mes más alto. Hasta 3 «se concentra»; más, «se reparte». */
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

  // Mes que se describe abajo: el que se tocó, o el más alto (o, sin actividad, el que tuvo detección en más temporadas).
  const top = h.kind === "low" ? clim.reduce((best, c, i) => (c.seasons_with > clim[best].seasons_with ? i : best), 0) : med.indexOf(h.peak);
  const shown = picked ?? top;
  const sel = clim[shown];
  const shade = (v: number) => (v <= 0 || h.peak <= 0 ? "var(--b0)" : SHADES[Math.min(4, Math.floor((v / h.peak) * 5 - 1e-9))]);
  const names = h.months.map(i => t.monthsLong[i]);

  // Puntos de la temporada: cada temporada observada al mismo día, y la en curso aparte.
  const vals = years.map(y => sc.observed_seasons[String(y)]);
  const vmax = Math.max(4, sc.current, ...vals);
  const pos = (v: number) => `${(v / vmax) * 100}%`;

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
        <p className="lp-pickline" aria-live="polite">{t.monthLine(t.monthsLong[shown], num(sel.median, lang), sel.seasons_with, sel.n)}</p>
        <p className="lp-note">{t.stripNote(n, a, b)}</p>
      </article>
      <article className="lp-q">
        <h3>{t.q2}</h3>
        <div className="lp-dots" aria-hidden="true">
          <span className="lp-dots-cur-l" style={{ left: pos(sc.current) }}>{seasonLabel(sc.season)}: {num(sc.current, lang)}</span>
          <span className="lp-dots-axis" />
          {years.map((y, i) => <span key={y} className="lp-dot" style={{ left: pos(vals[i]) }} title={`${seasonLabel(y)}: ${vals[i]}`} />)}
          <span className="lp-dots-cur" style={{ left: pos(sc.current) }} />
          <span className="lp-dots-ax" style={{ left: 0 }}>0</span>
          <span className="lp-dots-ax" style={{ right: 0 }}>{vmax}</span>
        </div>
        <p className="lp-dots-key"><span><span className="lp-dot-k" aria-hidden="true" />{t.dotsKey(a, b)}</span><span><span className="lp-cur-k" aria-hidden="true" />{t.dotsCur(seasonLabel(sc.season))}</span></p>
        <p className="lp-q2">{t.q2sentence(doc.comuna, seasonLabel(sc.season), dateLong(doc.cutoff, lang), num(sc.current, lang), sc.n, a, b, sc.median == null ? null : num(sc.median, lang))}</p>
        <p className="lp-note">{t.q2note(sc.n)}</p>
        <a className="lp-btn lp-btn-primary" href={`/explorar?cut=${cut}&lang=${lang}`}>{t.open(doc.comuna)} <span aria-hidden="true">→</span></a>
      </article>
    </div>
  );
}
