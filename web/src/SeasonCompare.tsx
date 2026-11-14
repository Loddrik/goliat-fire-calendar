import { seasonLabel, type SeasonCompare as SC } from "./types";
import { dict, type Lang } from "./i18n";

export function SeasonCompare({ sc, lang }: { sc: SC; lang: Lang }) {
  const t = dict[lang];
  const n = sc.n;
  const last = sc.months[sc.months.length - 1];
  const range = `${sc.cutoff_day} ${lang === "es" ? "de" : ""} ${t.monthsLong[last - 1]}`.replace(/\s+/g, " ");
  const max = Math.max(1, sc.current, ...Object.values(sc.observed_seasons));
  const bars = Object.entries(sc.observed_seasons).map(([s, v]) => ({ s: Number(s), v }));
  const verdict = sc.median == null ? "" : sc.current > (sc.p90 ?? Infinity) ? (lang === "es" ? "sobre el percentil 90" : "above the 90th percentile")
    : sc.current > (sc.p75 ?? Infinity) ? (lang === "es" ? "sobre el percentil 75" : "above the 75th percentile")
    : sc.current >= (sc.median ?? 0) ? (lang === "es" ? "en torno a la mediana" : "around the median") : (lang === "es" ? "bajo la mediana" : "below the median");
  return (
    <section className="card season">
      <h2>{t.season} {seasonLabel(sc.season)}</h2>
      <p className="help">{t.seasonHelp(range, n)}</p>
      <div className="kpis">
        <div className="kpi big"><span>{t.current}</span><strong>{sc.current}</strong><em>{verdict}</em></div>
        <div className="kpi"><span>{t.median}</span><strong>{sc.median ?? "—"}</strong></div>
        <div className="kpi"><span>{t.p75}</span><strong>{sc.p75 ?? "—"}</strong></div>
        <div className="kpi"><span>{t.p90}</span><strong>{sc.p90 ?? "—"}</strong></div>
      </div>
      <div className="bars" role="img" aria-label={`${t.current}: ${sc.current}; ${t.median}: ${sc.median}`}>
        {bars.map((b) => (
          <div key={b.s} className="bar" title={`${seasonLabel(b.s)}: ${b.v}`}>
            <div className="fill" style={{ height: `${(100 * b.v) / max}%` }} />
            <label>{String(b.s).slice(2)}</label>
          </div>
        ))}
        <div className="bar current" title={`${seasonLabel(sc.season)}: ${sc.current}`}>
          <div className="fill" style={{ height: `${(100 * sc.current) / max}%` }} />
          <label>{String(sc.season).slice(2)}</label>
        </div>
      </div>
    </section>
  );
}
