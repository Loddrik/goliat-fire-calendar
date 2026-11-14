import { useEffect, useMemo, useState } from "react";
import type { ComunaDoc, IndexDoc } from "./types";
import { dict, type Lang } from "./i18n";
import { Calendar } from "./Calendar";
import { SeasonCompare } from "./SeasonCompare";
import { RecurrenceMap, MAP_UNAVAILABLE } from "./RecurrenceMap";
import { MapBoundary } from "./MapBoundary";
import { download, seriesCsv } from "./csv";
import { ObservedHistory } from "./ObservedHistory";
import "./App.css";

export default function App() {
  const [lang, setLang] = useState<Lang>(() => {
    const fromUrl = new URLSearchParams(location.search).get("lang");
    if (fromUrl === "es" || fromUrl === "en") return fromUrl;
    return navigator.language.startsWith("es") ? "es" : "en";
  });
  const [index, setIndex] = useState<IndexDoc | null>(null);
  const [cut, setCut] = useState<string>(() => new URLSearchParams(location.search).get("cut") ?? "08107");
  const [doc, setDoc] = useState<ComunaDoc | null>(null);
  const [q, setQ] = useState("");
  const [showMethod, setShowMethod] = useState(false);
  const [view, setView] = useState(() => new URLSearchParams(location.search).get("view") === "observed" ? "observed" : "reconstruction");
  const [error, setError] = useState(false);
  const t = dict[lang];

  useEffect(() => {
    const controller = new AbortController();
    fetch("/data/index.json", { signal: controller.signal, cache: "no-cache" })
      .then(r => { if (!r.ok) throw new Error("index"); return r.json(); })
      .then(setIndex).catch(() => { if (!controller.signal.aborted) setError(true); });
    return () => controller.abort();
  }, []);
  useEffect(() => {
    const controller = new AbortController();
    setDoc(null); setError(false);
    if (!/^\d{5}$/.test(cut)) { setError(true); return; }
    fetch(`/data/comunas/${cut}.json`, { signal: controller.signal, cache: "no-cache" })
      .then(r => { if (!r.ok) throw new Error("commune"); return r.json(); })
      .then(result => { if (result.cut !== cut) throw new Error("commune"); if (!controller.signal.aborted) setDoc(result); })
      .catch(() => { if (!controller.signal.aborted) setError(true); });
    return () => controller.abort();
  }, [cut]);
  useEffect(() => {
    const u = new URL(location.href); u.searchParams.set("cut", cut); u.searchParams.set("view", view); history.replaceState(null, "", u);
  }, [cut, view]);
  useEffect(() => { document.documentElement.lang = lang; document.title = lang === "es" ? "GOLIAT · Actividad de fuego detectada" : "GOLIAT · Detected fire activity"; }, [lang]);
  const currentDoc = doc?.cut === cut ? doc : null;

  const list = useMemo(() => {
    // Sin tildes ni mayúsculas: "chillan" encuentra Chillán; también se puede buscar por CUT.
    const fold = (s: string) => s.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
    const n = fold(q.trim());
    return (index?.comunas ?? []).filter((c) => !n || fold(c.comuna).includes(n) || c.cut.startsWith(n)).sort((a, b) => a.region.localeCompare(b.region) || a.comuna.localeCompare(b.comuna));
  }, [index, q]);

  return (
    <div className="app">
      <header>
        <div>
          <h1>{t.title}</h1>
          <p className="sub">{t.subtitle}</p>
          <p className="sub audience">{lang === "es"
            ? `Cuándo y dónde los satélites de la NASA han detectado fuego en tu comuna: desde 2012, y desde 2002 en ${index ? index.comunas.filter((c) => c.enabled).length : "…"} comunas.`
            : `When and where NASA satellites have detected fire in your commune: since 2012, and since 2002 in ${index ? index.comunas.filter((c) => c.enabled).length : "…"} communes.`}</p>
          <p className="sub alert-note">{lang === "es"
            ? "No es una alerta. Si ves fuego, llama al 130 (CONAF) o al 132 (Bomberos). Sigue los avisos de SENAPRED."
            : "Not an alert. If you see fire in Chile, call 130 (CONAF) or 132 (Firefighters). Follow SENAPRED notices."}</p>
        </div>
        <div className="tools no-print">
          <button onClick={() => setLang(lang === "es" ? "en" : "es")} aria-label="Language">{lang === "es" ? "EN" : "ES"}</button>
          {currentDoc && view === "reconstruction" && <button onClick={() => download(`goliat_${currentDoc.cut}_${currentDoc.comuna}.csv`, seriesCsv(currentDoc))}>{t.csv}</button>}
          {currentDoc && view === "reconstruction" && <a className="btn" href={`/data/detections/${currentDoc.cut}.csv`} download>{t.csvDet}</a>}
          <button onClick={() => window.print()}>{t.print}</button>
        </div>
      </header>
      <nav className="view-switch no-print" aria-label={lang === "es" ? "Vistas de datos" : "Data views"}>
        <button aria-pressed={view === "reconstruction"} onClick={() => setView("reconstruction")}>{lang === "es" ? "Calendario armonizado · GOLIAT" : "Harmonized calendar · GOLIAT"}</button>
        <button aria-pressed={view === "observed"} onClick={() => setView("observed")}>{lang === "es" ? "Historial por plataforma · FireChronos" : "Platform history · FireChronos"}</button>
      </nav>

      <div className="layout">
        <aside className="no-print">
          <label className="search"><span className="sr">{t.pick}</span>
            <input placeholder={t.search} value={q} onChange={(e) => setQ(e.target.value)} />
          </label>
          <ul className="comunas" role="listbox" aria-label={t.pick}>
            {list.map((c) => (
              <li key={c.cut}>
                <button role="option" aria-selected={c.cut === cut} className={c.cut === cut ? "sel" : ""} onClick={() => setCut(c.cut)}>
                  <span>{c.comuna}</span><small>{c.region}{view === "reconstruction" ? (c.enabled ? " · 2002→" : " · 2012→") : ""}</small>
                </button>
              </li>
            ))}
          </ul>
        </aside>

        <main>
          {view === "observed" ? <ObservedHistory cut={cut} lang={lang} /> : error ? <p role="alert">{lang === "es" ? "No se pudieron cargar los datos de esta comuna. Selecciona otra comuna o recarga la página." : "Could not load this commune. Select another commune or reload the page."}</p> : doc?.cut === cut ? (
            <>
              <div className="titlebar">
                <h2>{doc.comuna} <small>{doc.region} · CUT {doc.cut}</small></h2>
                <div className={`badge ${doc.reconstruction_enabled ? "ok" : "no"}`} title={doc.reconstruction_enabled ? "" : t.reconNotWhy}>
                  {doc.reconstruction_enabled ? t.reconEnabled : t.reconNot}
                </div>
                <span className="cutoff">{t.cutoff} {doc.cutoff}</span>
              </div>
              {!doc.reconstruction_enabled && <p className="why">{t.reconNotWhy}</p>}

              <section className="card">
                <h2>{t.calendar}</h2>
                <p className="help">{t.calendarHelp}</p>
                <Calendar series={doc.series} lang={lang} />
              </section>

              <SeasonCompare sc={doc.season_compare} lang={lang} />

              <section className="card">
                <h2>{t.recurrence}</h2>
                <p className="help">{t.recurrenceHelp}</p>
                <MapBoundary fallback={<p className="map-unavailable" role="status">{MAP_UNAVAILABLE[lang]}</p>}><RecurrenceMap doc={doc} onPick={setCut} lang={lang} /></MapBoundary>
              </section>

              <section className="card method">
                <h2><button className="link" onClick={() => setShowMethod(!showMethod)} aria-expanded={showMethod}>{showMethod ? "▾" : "▸"} {t.method}</button></h2>
                <div className={showMethod ? "" : "print-only"}>
                  <ul className="gates">
                    <li>{lang === "es" ? "Validación cruzada 2012–2019, error absoluto medio mensual" : "Cross-validation 2012–2019, monthly mean absolute error"}: Aqua {lang === "es" ? "crudo" : "raw"} <b>{doc.gates.loso_mae_raw}</b> · Aqua × {doc.r_const} <b>{doc.gates.loso_mae_const}</b> · {lang === "es" ? "climatología" : "climatology"} <b>{doc.gates.loso_mae_clim}</b></li>
                    <li>{lang === "es" ? "Gana a la climatología en" : "Beats climatology in"} <b>{doc.gates.wins_vs_clim}/{doc.gates.of}</b> {t.seasons} {doc.gates.gate_vs_clim ? "✓" : "✗"} · {lang === "es" ? "gana a Aqua crudo en" : "beats raw Aqua in"} <b>{doc.gates.wins_vs_raw}/{doc.gates.of}</b> {doc.gates.gate_vs_raw ? "✓" : "✗"} · Aqua 2012–2019: <b>{doc.gates.aqua_train}</b> (≥ {doc.gates.min_aqua} {doc.gates.gate_aqua ? "✓" : "✗"}) · S-NPP: {doc.gates.snpp_train}</li>
                    {doc.reconstruction_enabled && <li>{lang === "es" ? "Error típico del estimado" : "Typical error of estimates"}: ± {doc.gates.band_mae} ({lang === "es" ? "cubre" : "covers"} {Math.round(doc.gates.band_coverage_1 * 100)} % {lang === "es" ? "de los meses activos" : "of active months"}; {Math.round(doc.gates.band_coverage_2 * 100)} % {lang === "es" ? "con" : "at"} ±2)</li>}
                  </ul>
                  {t.methodBody.map((p, i) => <p key={i}>{p}</p>)}
                </div>
              </section>
            </>
          ) : <p>…</p>}
          <footer>
            <p className="disclaimer">{t.disclaimer}</p>
            <p className="sources">{view === "reconstruction" ? t.sources : (lang === "es" ? "Historia por plataforma: NASA FIRMS · DPA 2023, SUBDERE / IDE Chile · Sin armonización ni máscara persistente adicional." : "Platform history: NASA FIRMS · DPA 2023, SUBDERE / IDE Chile · No harmonization or additional persistence mask.")}</p>
          </footer>
        </main>
      </div>
    </div>
  );
}
