import { MONTHS_SEASON, seasonLabel, type MonthRow, type SeasonTotal } from "./types";
import { dict, type Lang } from "./i18n";
import { BLUES, MONTH_BREAKS, MONTH_LABELS, num, tramo } from "./ui";

// Tramos fijos iguales en las 54 comunas (brief §11): 0 · 1–5 · 6–20 · 21–50 · 51–100 · más de 100 celdas-día.
export function color(v: number) {
  const i = tramo(v, MONTH_BREAKS);
  return i < 0 ? "#ffffff" : BLUES[i];
}

export function Calendar({ series, totals, bandMae, lang }: { series: MonthRow[]; totals: SeasonTotal[]; bandMae?: number; lang: Lang }) {
  const t = dict[lang];
  const seasons = Array.from(new Set(series.map((r) => r.season))).sort((a, b) => b - a);
  const totalBy = new Map(totals.map((x) => [x.season, x]));
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
            <th scope="col">{lang === "es" ? "Total" : "Total"}</th>
          </tr>
        </thead>
        <tbody>
          {seasons.map((s) => {
            const rows = MONTHS_SEASON.map((m) => byKey.get(`${s}-${m}`));
            const tot = totalBy.get(s);
            return (
              <tr key={s}>
                <th scope="row">{seasonLabel(s)}</th>
                {rows.map((r, i) => {
                  if (!r) return <td key={i} className="cell future" aria-label="—"></td>;
                  const cls = `cell ${r.state}${r.provisional ? " provisional" : ""}${r.partial ? " partial" : ""}`;
                  const label = r.state === "not_enabled" ? t.notEnabled : `${num(r.value, lang)}${r.state === "estimated" ? ` ± ${num(r.band ?? null, lang)}` : ""}`;
                  const light = r.value != null && tramo(r.value, MONTH_BREAKS) >= 3;
                  return (
                    <td key={i} className={cls} style={{ background: r.state === "not_enabled" ? undefined : color(r.value ?? 0), color: light ? "#fff" : "#1A1A1A" }}
                        title={`${t.monthsLong[r.m - 1]} ${r.y}: ${label}${r.provisional ? " · NRT" : ""}${r.partial ? (lang === "es" ? " · mes incompleto" : " · partial month") : ""}`}>
                      {r.state === "not_enabled" ? "∅" : r.partial ? `${num(r.value, lang)}…` : num(r.value, lang)}
                    </td>
                  );
                })}
                <td className="cell total" title={tot && !tot.complete ? (lang === "es" ? "temporada incompleta" : "incomplete season") : undefined}>
                  {!tot || tot.value == null ? "∅" : `${num(tot.value, lang)}${tot.state === "estimated" ? "±" : ""}${tot.complete ? "" : "…"}`}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
      <div className="legend" aria-label="Leyenda">
        <span><i className="sw observed" /> {t.observed}</span>
        {series.some((r) => r.state === "estimated") && <span><i className="sw estimated" /> {t.estimated}{bandMae != null && series.some((r) => r.state === "estimated") ? (lang === "es" ? `: ± ${num(bandMae, lang)} celdas-día por mes en esta comuna. Un total con ± incluye meses aproximados; su error puede ser mayor que el ± de un mes.` : `: ± ${num(bandMae, lang)} cell-days per month in this commune. A total with ± includes approximate months; its error can exceed the monthly ±.`) : ""}</span>}
        {series.some((r) => r.state === "not_enabled") && <span><i className="sw not_enabled">∅</i> {t.notEnabled}</span>}
        <span><i className="sw provisional" /> {t.provisional}</span>
        <span className="ramp"><i className="zero" />0</span>
        {BLUES.map((c, i) => <span key={c} className="ramp"><i style={{ background: c }} />{i < MONTH_LABELS.length ? MONTH_LABELS[i] : (lang === "es" ? "más de 100" : "over 100")}</span>)}
        <span>{lang === "es" ? "celdas-día por mes · mismos tramos en las 54 comunas" : "cell-days per month · same bands in all 54 communes"}</span>
      </div>
    </div>
  );
}
