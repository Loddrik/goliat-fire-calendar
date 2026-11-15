import { useEffect, useState } from "react";
import type { Text, Lang } from "./text";
import { dateLong, seasonLabel } from "./text";

// Las dos preguntas por comuna, con números leídos tal cual de web/public/data/ (regla 6):
// perfil de 12 meses desde derived/<cut>.json y comparación de temporada desde comunas/<cut>.json.
// Se monta con key={cut}, así cada comuna parte con estado limpio.

type Clim = { m: number; n: number; median: number; p25: number; p75: number; max: number; seasons_with: number };
type Derived = { cut: string; month_climatology: Clim[] };
type Compare = { season: number; current: number; observed_seasons: Record<string, number>; median: number | null; n: number };
type Commune = { cut: string; comuna: string; cutoff: string; season_compare: Compare };

const ORDER = [7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6];
// Decimales con coma en español (la mediana de 14 temporadas puede terminar en ,5).
const num = (v: number | null, lang: Lang) => (v == null ? null : v.toLocaleString(lang === "es" ? "es-CL" : "en-US", { maximumFractionDigits: 1 }));

export function CommuneSample({ cut, t, lang }: { cut: string; t: Text; lang: Lang }) {
  const [derived, setDerived] = useState<Derived | null>(null);
  const [doc, setDoc] = useState<Commune | null>(null);
  const [error, setError] = useState(false);

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
  const top = Math.max(1, ...clim.map(c => c.max)) * 1.2;
  const n = clim[0]?.n ?? 0;
  const sc = doc.season_compare;
  const years = Object.keys(sc.observed_seasons).map(Number);
  const a = seasonLabel(Math.min(...years)), b = seasonLabel(Math.max(...years));
  if (n !== sc.n) console.warn(`GOLIAT: n distinto entre derived (${n}) y season_compare (${sc.n}) en ${cut}`);

  return (
    <div className="lp-sample">
      <article className="lp-q">
        <h3>{t.q1}</h3>
        <div className="lp-profile" role="list">
          {clim.map((c, i) => (
            <div className="lp-col" role="listitem" key={c.m}>
              <span className="lp-sr">{t.ofSeasonsAria(t.monthsShort[i], num(c.median, lang)!, num(c.max, lang)!, c.seasons_with, c.n)}</span>
              <span className="lp-val" aria-hidden="true">{num(c.median, lang)}</span>
              <div className="lp-track" aria-hidden="true">
                <div className="lp-bar" style={{ height: `${(c.median / top) * 100}%` }} />
                <div className="lp-max" style={{ bottom: `${(c.max / top) * 100}%` }} />
                <span className="lp-maxv" style={{ bottom: `calc(${(c.max / top) * 100}% + 3px)` }}>{num(c.max, lang)}</span>
              </div>
              <span className="lp-mon" aria-hidden="true">{t.monthsShort[i]}</span>
              <span className="lp-k" aria-hidden="true">{c.seasons_with}<span className="lp-k-of">{t.ofWord} {c.n}</span></span>
            </div>
          ))}
        </div>
        <p className="lp-note">{t.q1short(n)}</p>
        <details className="lp-more">
          <summary>{t.howToRead}</summary>
          <p className="lp-note">{t.q1note(n, a, b)}</p>
        </details>
      </article>
      <article className="lp-q">
        <h3>{t.q2}</h3>
        <p className="lp-fact">{t.q2sentence(doc.comuna, seasonLabel(sc.season), dateLong(doc.cutoff, lang), num(sc.current, lang)!, sc.n, a, b, num(sc.median, lang))}</p>
        <p className="lp-note">{t.q2note(sc.n)}</p>
        <a className="lp-btn lp-btn-primary" href={`/explorar?cut=${cut}&lang=${lang}`}>{t.open(doc.comuna)} <span aria-hidden="true">→</span></a>
      </article>
    </div>
  );
}
