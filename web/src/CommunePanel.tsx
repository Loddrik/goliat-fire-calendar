import { useState, type ReactNode } from "react";
import type { Lang } from "./i18n";
import type { ComunaDoc, DerivedDoc } from "./types";
import { seasonLabel } from "./types";
import { SHOW_CATEGORY, UI, activityMonths, category, dmy, join, longDate, monthName, monthShort, num } from "./ui";
import { download, seriesCsv } from "./csv";

const MONTHS_SEASON = [7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6];

export function CommunePanel({ doc, derived, season, lang, tableOpen, toggleTable, method }: {
  doc: ComunaDoc; derived: DerivedDoc | null; season: number | null; lang: Lang;
  tableOpen: boolean; toggleTable: () => void; method: ReactNode;
}) {
  const T = UI[lang];
  const [copied, setCopied] = useState(false);
  const sc = doc.season_compare;
  const cutoff = dmy(doc.cutoff);
  const act = derived ? activityMonths(derived.month_climatology) : null;
  const names = (ms: number[]) => join(ms.map((m) => monthName(m, lang)), lang);

  // Frase de temporada: los números de season_compare, tal cual. La categoría queda apagada hasta el issue #4.
  const cat = category(sc.current, sc.p25, sc.p75);
  const p25 = num(sc.p25, lang), p75 = num(sc.p75, lang);
  const compare = cat === "too_few" ? T.tooFew(p25, p75)
    : SHOW_CATEGORY ? `${T.cat[cat]} ${T.catRange(p25, p75, sc.n)}` : T.range(p25, p75, sc.n);
  const months = !act ? "" : act.mode === "typical" ? (act.peak ? T.typicalPeak(names(act.months), monthName(act.peak, lang)) : T.typical(names(act.months)))
    : act.mode === "rare" ? T.rare(names(act.big), monthName(act.frequent, lang)) : T.noneMonths;

  const url = `${location.origin}/explorar?cut=${doc.cut}`;
  const shareText = !act || act.mode === "none" ? T.shareMsgNone(doc.comuna, cutoff, url)
    : act.mode === "typical" ? T.shareMsg(doc.comuna, names(act.months), act.peak ? monthName(act.peak, lang) : null, cutoff, url)
    : T.shareMsg(doc.comuna, monthName(act.frequent, lang), names(act.big), cutoff, url);
  async function copy() {
    try { await navigator.clipboard.writeText(shareText); setCopied(true); } catch { /* sin portapapeles: el texto queda a la vista para copiarlo a mano */ }
  }
  const whatsapp = `https://wa.me/?text=${encodeURIComponent(shareText)}`;

  const totals = (derived?.season_totals ?? []).filter((t) => t.season >= 2012);
  const tMax = Math.max(1, ...totals.map((t) => t.value ?? 0));
  const sel = season != null ? totals.find((t) => t.season === season) : null;
  const clim = derived ? MONTHS_SEASON.map((m) => derived.month_climatology.find((c) => c.m === m)!) : [];
  const cMax = Math.max(1, ...clim.map((c) => c.max ?? 0));
  const nSeasons = clim[0]?.n ?? 14;

  return (
    <div className="ficha">
      <div className="ficha-head">
        <h2>{doc.comuna} <small>· {doc.region} · CUT {doc.cut}</small></h2>
        <p className="muted">{T.upTo} {cutoff}</p>
        <span className={`chip ${doc.reconstruction_enabled ? "on" : ""}`}>{doc.reconstruction_enabled ? T.serieOn : T.serieOff}</span>
      </div>

      <div className="phrase">
        <p>{T.phrase(doc.comuna, longDate(doc.cutoff, lang), sc.current)} {compare} {months}</p>
        <p className="muted small">{T.source}</p>
        <p className="muted small">{T.unit}</p>
      </div>

      {derived && (
        <section className="block">
          <h3>{T.totalsTitle}</h3>
          {sel && <p className="sel-total">{T.seasonTotal(seasonLabel(sel.season), sel.season, num(sel.value, lang), doc.comuna)}{!sel.complete && ` (${T.totalsCurrent(cutoff)})`}</p>}
          <div className="totals" role="img" aria-label={totals.map((t) => `${seasonLabel(t.season)}: ${num(t.value, lang)}`).join("; ")}>
            {totals.map((t) => (
              <div key={t.season} className={`tbar${season === t.season ? " sel" : ""}${!t.complete ? " partial" : ""}`} title={`${seasonLabel(t.season)}: ${num(t.value, lang)}${!t.complete ? ` · ${T.totalsCurrent(cutoff)}` : ""}`}>
                <span className="v">{num(t.value, lang)}</span>
                <div className="f" style={{ height: `${(100 * (t.value ?? 0)) / tMax}%` }} />
                <span className="y">{String(t.season).slice(2)}-{String(t.season + 1).slice(2)}</span>
              </div>
            ))}
          </div>
          <p className="muted small">{lang === "es" ? "Celdas-día por temporada (julio a junio). La última va " : "Cell-days per season (July to June). The last one is "}{T.totalsCurrent(cutoff)}.</p>
        </section>
      )}

      {derived && (
        <section className="block">
          <h3>{T.profileTitle}</h3>
          <div className="profile" role="img" aria-label={clim.map((c) => `${monthName(c.m, lang)}: ${num(c.median, lang)}`).join("; ")}>
            {clim.map((c) => (
              <div key={c.m} className="pcol" title={`${monthName(c.m, lang)} · ${lang === "es" ? "típico" : "typical"} ${num(c.median, lang)} · ${lang === "es" ? "máximo" : "max"} ${num(c.max, lang)} · ${c.seasons_with} ${T.of(c.n)}`}>
                <span className="v">{num(c.median, lang)}</span>
                <div className="track">
                  <div className="max" style={{ bottom: `${(100 * (c.max ?? 0)) / cMax}%` }} />
                  <div className="f" style={{ height: `${(100 * (c.median ?? 0)) / cMax}%` }} />
                </div>
                <span className="m">{monthShort(c.m, lang)}</span>
                <span className="w">{c.seasons_with}<br />{T.of(c.n)}</span>
              </div>
            ))}
          </div>
          <p className="muted small">{T.profileLegend(nSeasons)}</p>
          <p className="note small">{T.profileNote}</p>
        </section>
      )}

      <div className="actions no-print">
        <button className="primary" onClick={toggleTable} aria-expanded={tableOpen}>{tableOpen ? T.hideTable : T.table}</button>
        <div className="share-preview">
          <b>{T.shareTitle}</b>
          <p>{shareText}</p>
          <div className="row">
            <a className="btn whatsapp" href={whatsapp} target="_blank" rel="noopener noreferrer">{T.shareWhatsapp}</a>
            <button onClick={copy}>{T.copy}</button>
          </div>
          {copied && <small>{T.copied}</small>}
        </div>
        <button onClick={() => window.print()}>{T.print}</button>
        <p className="links">
          <button className="link" onClick={() => download(`goliat_${doc.cut}_${doc.comuna}.csv`, seriesCsv(doc))}>{T.csv}</button>
          {" · "}
          <a href={`/data/detections/${doc.cut}.csv`} download>{T.csvDet}</a>
        </p>
      </div>

      <details className="fold">
        <summary>{T.planTitle}</summary>
        <ul>{T.plan(doc.comuna, cutoff).map((x) => <li key={x}>{x}</li>)}</ul>
      </details>
      <details className="fold method-fold">
        <summary>{lang === "es" ? "Cómo se hizo y qué no muestra" : "How it was made and what it does not show"}</summary>
        {method}
      </details>
    </div>
  );
}
