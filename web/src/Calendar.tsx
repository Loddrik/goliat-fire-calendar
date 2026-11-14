import { MONTHS_SEASON, seasonLabel, type MonthRow } from "./types";
import { dict, type Lang } from "./i18n";

// Rampa secuencial apta para daltónicos (viridis, 6 pasos)
const RAMP = ["#fde725", "#7ad151", "#22a884", "#2a788e", "#414487", "#440154"];

export function color(v: number, max: number) {
  if (v <= 0) return "#f1f1f1";
  const t = Math.min(1, Math.sqrt(v / Math.max(1, max)));
  return RAMP[Math.min(RAMP.length - 1, Math.floor(t * RAMP.length))];
}

export function Calendar({ series, lang }: { series: MonthRow[]; lang: Lang }) {
  const t = dict[lang];
  const seasons = Array.from(new Set(series.map((r) => r.season))).sort((a, b) => b - a);
  const max = Math.max(1, ...series.filter((r) => r.value != null).map((r) => r.value as number));
  const byKey = new Map(series.map((r) => [`${r.season}-${r.m}`, r]));
  return (
    <div className="calendar">
      <table aria-label={t.calendar}>
        <thead>
          <tr>
            <th scope="col">{lang === "es" ? "Temporada" : "Season"}</th>
            {MONTHS_SEASON.map((m) => (
              <th key={m} scope="col">{t.months[m - 1]}</th>
            ))}
            <th scope="col">Σ</th>
          </tr>
        </thead>
        <tbody>
          {seasons.map((s) => {
            const rows = MONTHS_SEASON.map((m) => byKey.get(`${s}-${m}`));
            const total = rows.reduce((a, r) => a + (r?.value ?? 0), 0);
            const anyEnabled = rows.some((r) => r && r.state !== "not_enabled");
            return (
              <tr key={s}>
                <th scope="row">{seasonLabel(s)}</th>
                {rows.map((r, i) => {
                  if (!r) return <td key={i} className="cell future" aria-label="—"></td>;
                  const cls = `cell ${r.state}${r.provisional ? " provisional" : ""}${r.partial ? " partial" : ""}`;
                  const label = r.state === "not_enabled" ? t.notEnabled : `${r.value}${r.state === "estimated" ? ` ± ${r.band}` : ""}`;
                  const light = r.value != null && r.value > 0 && Math.sqrt(r.value / max) > 0.45;
                  return (
                    <td key={i} className={cls} style={{ background: r.state === "not_enabled" ? undefined : color(r.value ?? 0, max), color: light ? "#fff" : "#222" }}
                        title={`${t.monthsLong[r.m - 1]} ${r.y}: ${label}${r.provisional ? " · NRT" : ""}${r.partial ? (lang === "es" ? " · mes incompleto" : " · partial month") : ""}`}>
                      {r.state === "not_enabled" ? "∅" : r.partial ? `${r.value}…` : r.value}
                    </td>
                  );
                })}
                <td className="cell total">{anyEnabled ? Math.round(total) : "∅"}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
      <div className="legend" aria-label="Leyenda">
        <span><i className="sw observed" /> {t.observed}</span>
        <span><i className="sw estimated" /> {t.estimated}</span>
        <span><i className="sw not_enabled">∅</i> {t.notEnabled}</span>
        <span><i className="sw provisional" /> {t.provisional}</span>
        <span className="ramp">0 {RAMP.map((c) => <i key={c} style={{ background: c }} />)} {max}</span>
      </div>
    </div>
  );
}
