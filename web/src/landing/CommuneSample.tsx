import { useEffect, useState } from "react";
import type { Text, Lang } from "./text";
import { dateLong, seasonLabel } from "./text";

// Tu comuna en tres preguntas para cualquier persona (#40): ¿cuándo?, ¿y este año?, ¿qué año tuvo más?
// Cada una con una respuesta corta en grande y un gráfico de apoyo; lo técnico va en letra chica.
// Números leídos tal cual de web/public/data/ (regla 6): derived/<cut>.json (month_climatology,
// season_totals) y comunas/<cut>.json (season_compare, series). Solo se eligen y se cuentan valores
// publicados (el mes más alto, cuántas temporadas quedaron por encima); no se calcula ninguna cifra nueva.
// Se monta con key={cut}.

type Clim = { m: number; n: number; median: number; max: number; seasons_with: number };
type SeasonTotal = { season: number; value: number | null; state: "estimated" | "observed" | "not_enabled"; complete: boolean };
type Derived = { cut: string; current_season: number; month_climatology: Clim[]; season_totals: SeasonTotal[] };
type Compare = { season: number; current: number; observed_seasons: Record<string, number>; median: number | null; n: number };
type Point = { season: number; y: number; m: number; value: number | null; state: string; partial?: boolean };
type Commune = { cut: string; comuna: string; cutoff: string; season_compare: Compare; series: Point[] };

const ORDER = [7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6];
// Bajo este valor de mediana en el mes más alto, ningún mes se destaca (revisión científica #40).
const LOW = 3;
const num = (v: number | null, lang: Lang) => (v == null ? "—" : v.toLocaleString(lang === "es" ? "es-CL" : "en-US", { maximumFractionDigits: 1 }));

/** Meses que se destacan: mediana ≥ la mitad del mes más alto. Hasta 3 «estos meses»; más, «repartido». */
export function highlight(medians: number[]) {
  const peak = Math.max(...medians);
  if (peak < LOW) return { kind: "low" as const, months: [] as number[], peak };
  const months = medians.map((v, i) => [v, i]).filter(([v]) => v >= peak / 2).map(([, i]) => i);
  return { kind: months.length > 3 ? ("spread" as const) : ("focus" as const), months, peak };
}

export function CommuneSample({ cut, t, lang, enabled }: { cut: string; t: Text; lang: Lang; enabled: number }) {
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

  const c = doc.comuna;

  // ---- 1. ¿Cuándo? ------------------------------------------------------------------------------
  const clim = ORDER.map(m => derived.month_climatology.find(x => x.m === m)).filter((x): x is Clim => !!x);
  const med = clim.map(x => x.median ?? 0);
  const n = clim[0]?.n ?? 0;
  const h = highlight(med);
  const names = h.months.map(i => t.monthsLong[i]);
  // «todos los años» / «casi todos» sale de seasons_with (temporadas con al menos una detección ese mes).
  const minWith = h.months.length ? Math.min(...h.months.map(i => clim[i].seasons_with)) : 0;
  const often = minWith === n ? "all" : minWith >= n - 2 ? "almost" : "some";
  const whenAnswer = h.kind === "low" ? t.whenLow : h.kind === "spread" ? t.whenSpread(names) : t.whenFocus(names, often);
  // El mes extremo de un solo año: si cae fuera de los meses nombrados, se nombra con su año (de la serie publicada).
  const maxes = clim.map(x => x.max ?? 0);
  const peakMax = Math.max(...maxes), peakI = maxes.indexOf(peakMax);
  // Siempre se nombra; si cae fuera de los meses nombrados, se dice que no sigue el patrón.
  const peakOut = !h.months.includes(peakI);
  const peakTie = maxes.filter(v => v === peakMax).length > 1;
  // Un «extremo» de 2 celdas-día no dice nada: se nombra desde 2 × LOW.
  const peakPoint = peakMax >= 2 * LOW
    ? doc.series.find(p => p.m === ORDER[peakI] && p.state === "observed" && !p.partial && p.season < derived.current_season && p.value === peakMax)
    : undefined;
  const top = h.kind === "low" ? clim.reduce((b, x, i) => (x.seasons_with > clim[b].seasons_with ? i : b), 0) : med.indexOf(h.peak);
  const shown = picked ?? top;
  const barMax = Math.max(...med, 2 * LOW);

  // ---- 2. ¿Y este año? --------------------------------------------------------------------------
  const sc = doc.season_compare;
  const years = Object.keys(sc.observed_seasons).map(Number).sort((a, b) => a - b);
  const vals = years.map(y => sc.observed_seasons[String(y)]);
  // Conteo de temporadas publicadas por encima, por debajo e iguales (no es una cifra nueva).
  const above = vals.filter(v => v > sc.current).length, below = vals.filter(v => v < sc.current).length;
  const equal = vals.length - above - below, nv = vals.length;
  const nowAnswer = (sc.median ?? 0) < LOW && sc.current < LOW ? t.nowQuiet
    : above >= nv - 3 ? t.nowLess(above, nv, equal)
    : below >= nv - 3 ? t.nowMore(below, nv, equal)
    : t.nowMid(above, below, equal);
  // Mientras el corte cae entre julio y noviembre, el verano no ha empezado.
  const early = Number(doc.cutoff.slice(5, 7)) >= 7 && Number(doc.cutoff.slice(5, 7)) <= 11;
  const vmax = Math.max(4, sc.current, ...vals);
  const pos = (v: number) => `${(v / vmax) * 100}%`;
  const stack = vals.map((v, i) => vals.slice(0, i).filter(w => w === v).length);
  const lift = Math.max(0, ...stack) * 10;

  // ---- 3. ¿Qué año tuvo más? (solo temporadas completas observadas) -------------------------------
  const seasons = derived.season_totals.filter(s => s.complete && s.state === "observed");
  const sMax = Math.max(1, ...seasons.map(s => s.value ?? 0));
  const tops = seasons.filter(s => s.value === sMax);
  const topSeason = tops[0];

  return (
    <div className="lp-qs">
      <article className="lp-q">
        <p className="lp-q-ask">{t.whenAsk(c)}</p>
        <p className="lp-q-answer">{whenAnswer}</p>
        {peakPoint && <p className={`lp-q-peak${peakOut ? " out" : ""}`}>{t.whenPeak(t.monthsLong[peakI], peakPoint.y, num(peakMax, lang), peakOut, peakTie)}</p>}
        {h.kind !== "low" && <p className="lp-q-detail">{t.whenBurns}</p>}
        <div className="lp-mbars" role="group" aria-label={t.whenAsk(c)}>
          {clim.map((x, i) => (
            <button key={x.m} type="button" className={`lp-mbar${h.months.includes(i) ? " hi" : ""}${shown === i ? " on" : ""}`}
              aria-pressed={shown === i} aria-label={t.monthAria(t.monthsLong[i], num(x.median, lang), x.seasons_with, x.n)} onClick={() => setPicked(i)}>
              <span className="lp-mbar-track"><b style={{ height: `${Math.max(x.median > 0 ? 4 : 0, (x.median / barMax) * 100)}%` }} /></span>
              <span className="lp-mbar-m">{t.monthsShort[i]}</span>
            </button>
          ))}
        </div>
        <p className="lp-q-detail" aria-live="polite">{t.monthLine(t.monthsLong[shown], num(clim[shown].median, lang), clim[shown].seasons_with, clim[shown].n)}</p>
        <p className="lp-q-fine">{t.whenFine(n)}</p>
      </article>

      <article className="lp-q">
        <p className="lp-q-ask">{t.nowAsk}</p>
        <p className="lp-q-answer">{nowAnswer}</p>
        <p className="lp-q-warn">{t.nowWarn(early)}</p>
        <div className="lp-dots" aria-hidden="true" style={{ height: 70 + lift }}>
          <span className="lp-dots-cur-l" style={{ left: pos(sc.current) }}>{t.nowThis}: {num(sc.current, lang)}</span>
          <span className="lp-dots-axis" style={{ top: 34 + lift }} />
          {years.map((y, i) => <span key={y} className="lp-dot" style={{ left: pos(vals[i]), top: 28 + lift - stack[i] * 10 }} title={`${seasonLabel(y)}: ${vals[i]}`} />)}
          <span className="lp-dots-cur" style={{ left: pos(sc.current), height: 29 + lift }} />
          <span className="lp-dots-ax" style={{ left: 0, top: 52 + lift }}>{t.nowFewer}</span>
          <span className="lp-dots-ax" style={{ right: 0, top: 52 + lift }}>{t.nowMoreAx}</span>
        </div>
        <p className="lp-q-detail">{t.nowLine(dateLong(doc.cutoff, lang), num(sc.current, lang), num(sc.median, lang))}</p>
        <p className="lp-q-fine">{t.nowFine}</p>
      </article>

      <article className="lp-q">
        <p className="lp-q-ask">{t.yearsAsk}</p>
        <p className="lp-q-answer">{tops.length ? t.yearsAnswer(tops.map(s => seasonLabel(s.season)), tops.map(s => s.season + 1)) : "—"}</p>
        <div className="lp-ybars" role="list" aria-label={t.yearsAsk}>
          {seasons.map(s => (
            <div key={s.season} role="listitem" className={`lp-ybar${s.value === sMax ? " hi" : ""}`}>
              <span className="lp-sr">{seasonLabel(s.season)}: {num(s.value, lang)}</span>
              <span className="lp-ybar-track" aria-hidden="true" title={`${seasonLabel(s.season)}: ${num(s.value, lang)}`}><b style={{ height: `${Math.max(3, ((s.value ?? 0) / sMax) * 100)}%` }} /></span>
              <span className="lp-ybar-y" aria-hidden="true">{String(s.season).slice(2)}</span>
            </div>
          ))}
        </div>
        <p className="lp-q-detail">{topSeason ? t.yearsLine(seasonLabel(topSeason.season), num(topSeason.value, lang)) : ""}</p>
        <p className="lp-q-fine">{t.yearsFine(enabled)}</p>
      </article>
    </div>
  );
}
