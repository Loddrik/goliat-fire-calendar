import { useEffect, useMemo, useState } from "react";
import type { ComunaDoc, IndexDoc } from "./types";
import { dict, type Lang } from "./i18n";
import { Calendar } from "./Calendar";
import { SeasonCompare } from "./SeasonCompare";
import { RecurrenceMap } from "./RecurrenceMap";
import { download, seriesCsv } from "./csv";
import "./App.css";

export default function App() {
  const [lang, setLang] = useState<Lang>(() => (navigator.language.startsWith("es") ? "es" : "en"));
  const [index, setIndex] = useState<IndexDoc | null>(null);
  const [cut, setCut] = useState<string>(() => new URLSearchParams(location.search).get("cut") ?? "08107");
  const [doc, setDoc] = useState<ComunaDoc | null>(null);
  const [q, setQ] = useState("");
  const [showMethod, setShowMethod] = useState(false);
  const t = dict[lang];

  useEffect(() => { fetch("/data/index.json").then((r) => r.json()).then(setIndex); }, []);
  useEffect(() => {
    fetch(`/data/comunas/${cut}.json`).then((r) => r.json()).then(setDoc);
    const u = new URL(location.href); u.searchParams.set("cut", cut); history.replaceState(null, "", u);
  }, [cut]);

  const list = useMemo(() => {
    const n = q.trim().toLowerCase();
    return (index?.comunas ?? []).filter((c) => !n || c.comuna.toLowerCase().includes(n)).sort((a, b) => a.region.localeCompare(b.region) || a.comuna.localeCompare(b.comuna));
  }, [index, q]);

  return (
    <div className="app">
      <header>
        <div>
          <h1>{t.title}</h1>
          <p className="sub">{t.subtitle}</p>
        </div>
        <div className="tools no-print">
          <button onClick={() => setLang(lang === "es" ? "en" : "es")} aria-label="Language">{lang === "es" ? "EN" : "ES"}</button>
          {doc && <button onClick={() => download(`goliat_${doc.cut}_${doc.comuna}.csv`, seriesCsv(doc))}>{t.csv}</button>}
          <button onClick={() => window.print()}>{t.print}</button>
        </div>
      </header>

      <div className="layout">
        <aside className="no-print">
          <label className="search"><span className="sr">{t.pick}</span>
            <input placeholder={t.search} value={q} onChange={(e) => setQ(e.target.value)} />
          </label>
          <ul className="comunas" role="listbox" aria-label={t.pick}>
            {list.map((c) => (
              <li key={c.cut}>
                <button role="option" aria-selected={c.cut === cut} className={c.cut === cut ? "sel" : ""} onClick={() => setCut(c.cut)}>
                  <span>{c.comuna}</span><small>{c.region}{c.enabled ? "" : " · ∅"}</small>
                </button>
              </li>
            ))}
          </ul>
        </aside>

        <main>
          {doc ? (
            <>
              <div className="titlebar">
                <h2>{doc.comuna} <small>{doc.region} · CUT {doc.cut}</small></h2>
                <div className={`badge ${doc.reconstruction_enabled ? "ok" : "no"}`} title={doc.reconstruction_enabled ? "" : t.reconNotWhy}>
                  {doc.reconstruction_enabled ? t.reconEnabled : t.reconNot}
                </div>
                <span className="cutoff">{t.cutoff} {doc.cutoff}</span>
              </div>
              {!doc.reconstruction_enabled && <p className="why">{t.reconNotWhy}</p>}

              <SeasonCompare sc={doc.season_compare} lang={lang} />

              <section className="card">
                <h2>{t.calendar}</h2>
                <p className="help">{t.calendarHelp}</p>
                <Calendar series={doc.series} lang={lang} />
              </section>

              <section className="card">
                <h2>{t.recurrence}</h2>
                <p className="help">{t.recurrenceHelp}</p>
                <RecurrenceMap doc={doc} onPick={setCut} />
              </section>

              <section className="card method">
                <h2><button className="link" onClick={() => setShowMethod(!showMethod)} aria-expanded={showMethod}>{showMethod ? "▾" : "▸"} {t.method}</button></h2>
                <div className={showMethod ? "" : "print-only"}>
                  <ul className="gates">
                    <li>MAE {lang === "es" ? "factor constante" : "constant factor"}: <b>{doc.gates.mae_const}</b> · MAE {lang === "es" ? "climatología" : "climatology"}: <b>{doc.gates.mae_clim}</b> · {lang === "es" ? "gana en" : "wins in"} <b>{doc.gates.wins_vs_clim}/{doc.gates.of}</b> {t.seasons}</li>
                    <li>Aqua 2012–2019: {doc.gates.aqua_train} · S-NPP 2012–2019: {doc.gates.snpp_train} · r = {doc.r_const}</li>
                  </ul>
                  {t.methodBody.map((p, i) => <p key={i}>{p}</p>)}
                </div>
              </section>
            </>
          ) : <p>…</p>}
          <footer>
            <p className="disclaimer">{t.disclaimer}</p>
            <p className="sources">{t.sources}</p>
          </footer>
        </main>
      </div>
    </div>
  );
}
