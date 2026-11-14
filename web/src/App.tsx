import { useEffect, useMemo, useState } from "react";
import type { ComunaDoc, DerivedDoc, IndexDoc, RegionDoc } from "./types";
import { dict, type Lang } from "./i18n";
import { Calendar } from "./Calendar";
import { ExploreMap, MAP_UNAVAILABLE } from "./ExploreMap";
import { MapBoundary } from "./MapBoundary";
import { CommunePanel } from "./CommunePanel";
import { ObservedHistory } from "./ObservedHistory";
import { GoliatLogo } from "./brand/GoliatLogo";
import { UI } from "./ui";
import "./App.css";

const params = () => new URLSearchParams(location.search);
const validCut = (c: string | null) => (c && /^\d{5}$/.test(c) ? c : null);

function getJson<T>(url: string, signal: AbortSignal): Promise<T> {
  return fetch(url, { signal, cache: "no-cache" }).then((r) => { if (!r.ok) throw new Error(url); return r.json(); });
}

export default function App() {
  const [lang, setLang] = useState<Lang>(() => {
    const fromUrl = params().get("lang");
    if (fromUrl === "es" || fromUrl === "en") return fromUrl;
    return navigator.language.startsWith("es") ? "es" : "en";
  });
  const [index, setIndex] = useState<IndexDoc | null>(null);
  const [region, setRegion] = useState<RegionDoc | null>(null);
  const [cut, setCut] = useState<string | null>(() => validCut(params().get("cut")));
  const [doc, setDoc] = useState<ComunaDoc | null>(null);
  const [derived, setDerived] = useState<DerivedDoc | null>(null);
  const [season, setSeason] = useState<number | null>(() => { const s = Number(params().get("t")); return s >= 2012 ? s : null; });
  const [q, setQ] = useState("");
  const [searching, setSearching] = useState(false);
  const [tableOpen, setTableOpen] = useState(() => params().get("vista") === "tabla");
  const [view, setView] = useState(() => (params().get("view") === "observed" ? "observed" : "reconstruction"));
  const [error, setError] = useState(false);
  const t = dict[lang];
  const T = UI[lang];

  useEffect(() => {
    const c = new AbortController();
    getJson<IndexDoc>("/data/index.json", c.signal).then(setIndex).catch(() => { if (!c.signal.aborted) setError(true); });
    getJson<RegionDoc>("/data/derived/region.json", c.signal).then(setRegion).catch(() => { /* sin mapa: la ficha sigue funcionando */ });
    return () => c.abort();
  }, []);
  useEffect(() => {
    const c = new AbortController();
    setDoc(null); setDerived(null); setError(false);
    if (!cut) return;
    getJson<ComunaDoc>(`/data/comunas/${cut}.json`, c.signal)
      .then((r) => { if (r.cut !== cut) throw new Error("commune"); setDoc(r); })
      .catch(() => { if (!c.signal.aborted) setError(true); });
    getJson<DerivedDoc>(`/data/derived/${cut}.json`, c.signal).then((r) => { if (r.cut === cut) setDerived(r); }).catch(() => { /* la ficha muestra lo que hay */ });
    return () => c.abort();
  }, [cut]);
  // La URL es el estado que se comparte: comuna, temporada del mapa, vista de tabla, idioma y vista FireChronos.
  useEffect(() => {
    const u = new URL(location.href);
    const set = (k: string, v: string | null) => (v ? u.searchParams.set(k, v) : u.searchParams.delete(k));
    set("cut", cut); set("t", season ? String(season) : null); set("vista", tableOpen ? "tabla" : null);
    set("view", view === "observed" ? "observed" : null); set("lang", lang);
    history.replaceState(null, "", u);
  }, [cut, season, tableOpen, view, lang]);
  useEffect(() => {
    document.documentElement.lang = lang;
    const name = doc && doc.cut === cut ? `${doc.comuna} · ` : "";
    document.title = `${name}GOLIAT · ${T.headline}`;
  }, [lang, doc, cut, T.headline]);

  const current = doc?.cut === cut ? doc : null;
  const enabledCount = index ? index.comunas.filter((c) => c.enabled).length : "…";

  const matches = useMemo(() => {
    // Sin tildes ni mayúsculas: "chillan" encuentra Chillán; también por CUT.
    const fold = (s: string) => s.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
    const n = fold(q.trim());
    if (!n) return [];
    return (index?.comunas ?? []).filter((c) => fold(c.comuna).includes(n) || c.cut.startsWith(n)).slice(0, 8);
  }, [index, q]);
  const pick = (c: string) => { setCut(c); setQ(""); setSearching(false); };

  const search = (
    <div className="search-box no-print">
      <input type="search" placeholder={T.search} value={q} aria-label={T.search}
        onChange={(e) => { setQ(e.target.value); setSearching(true); }} onFocus={() => setSearching(true)}
        onKeyDown={(e) => { if (e.key === "Enter" && matches[0]) pick(matches[0].cut); if (e.key === "Escape") setSearching(false); }} />
      {searching && matches.length > 0 && (
        <ul role="listbox" aria-label={t.pick}>
          {matches.map((c) => (
            <li key={c.cut}><button role="option" aria-selected={c.cut === cut} onClick={() => pick(c.cut)}>
              <span>{c.comuna}</span><small>{c.region} · {c.enabled ? "2002→" : "2012→"}</small>
            </button></li>
          ))}
        </ul>
      )}
    </div>
  );

  const method = current && (
    <div className="method">
      <ul className="gates">
        <li>{lang === "es" ? "Validación cruzada 2012–2019, error absoluto medio mensual" : "Cross-validation 2012–2019, monthly mean absolute error"}: Aqua {lang === "es" ? "crudo" : "raw"} <b>{current.gates.loso_mae_raw}</b> · Aqua × {current.r_const} <b>{current.gates.loso_mae_const}</b> · {lang === "es" ? "climatología" : "climatology"} <b>{current.gates.loso_mae_clim}</b></li>
        <li>{lang === "es" ? "Gana a la climatología en" : "Beats climatology in"} <b>{current.gates.wins_vs_clim}/{current.gates.of}</b> {t.seasons} {current.gates.gate_vs_clim ? "✓" : "✗"} · {lang === "es" ? "gana a Aqua crudo en" : "beats raw Aqua in"} <b>{current.gates.wins_vs_raw}/{current.gates.of}</b> {current.gates.gate_vs_raw ? "✓" : "✗"} · Aqua 2012–2019: <b>{current.gates.aqua_train}</b> (≥ {current.gates.min_aqua} {current.gates.gate_aqua ? "✓" : "✗"}) · S-NPP: {current.gates.snpp_train}</li>
        {current.reconstruction_enabled && <li>{lang === "es" ? "Error típico del estimado" : "Typical error of estimates"}: ± {current.gates.band_mae} ({lang === "es" ? "cubre" : "covers"} {Math.round(current.gates.band_coverage_1 * 100)} % {lang === "es" ? "de los meses activos" : "of active months"}; {Math.round(current.gates.band_coverage_2 * 100)} % {lang === "es" ? "con" : "at"} ±2)</li>}
      </ul>
      {t.methodBody.map((p, i) => <p key={i}>{p}</p>)}
    </div>
  );

  return (
    <div className="app">
      <header>
        <div className="brand">
          <a href={`/?lang=${lang}`} className="logo" aria-label="GOLIAT"><GoliatLogo variant="horizontal" height={30} lang={lang} /></a>
          <div>
            <h1>{T.headline}</h1>
            <p className="sub">{T.line(enabledCount)}</p>
          </div>
        </div>
        <div className="tools no-print">
          <button onClick={() => setLang(lang === "es" ? "en" : "es")} aria-label="Language">{lang === "es" ? "EN" : "ES"}</button>
        </div>
      </header>
      <p className="alert-strip" role="note">{T.alert}</p>
      <nav className="view-switch no-print" aria-label={lang === "es" ? "Vistas de datos" : "Data views"}>
        <button aria-pressed={view === "reconstruction"} onClick={() => setView("reconstruction")}>{lang === "es" ? "Mapa y calendario armonizado · GOLIAT" : "Map and harmonized calendar · GOLIAT"}</button>
        <button aria-pressed={view === "observed"} onClick={() => setView("observed")}>{lang === "es" ? "Historial por plataforma · FireChronos" : "Platform history · FireChronos"}</button>
      </nav>

      {view === "observed" ? (
        <main className="observed-main">
          {search}
          {cut ? <ObservedHistory cut={cut} lang={lang} /> : <p className="muted">{T.pickFirst}</p>}
        </main>
      ) : (
        <>
          <div className="explore">
            <div className="explore-map no-print">
              <MapBoundary fallback={<p className="map-unavailable" role="status">{MAP_UNAVAILABLE[lang]}</p>}>
                <ExploreMap region={region} selected={cut} onPick={pick} season={season} setSeason={setSeason} lang={lang} />
              </MapBoundary>
            </div>
            <aside className="panel">
              {search}
              {!cut ? <p className="muted hint">{T.searchHint}</p>
                : error ? <p role="alert">{T.loadError}</p>
                : current ? <CommunePanel doc={current} derived={derived} season={season} lang={lang} tableOpen={tableOpen} toggleTable={() => setTableOpen(!tableOpen)} method={method} />
                : <p className="muted">{T.loading}</p>}
            </aside>
          </div>

          {current && (
            <section className={`card serie${tableOpen ? "" : " print-only"}`} id="serie">
              <h2>{t.calendar} · {current.comuna} · 2002–2026</h2>
              <p className="help">{t.calendarHelp}</p>
              <Calendar series={current.series} totals={derived?.season_totals ?? []} lang={lang} />
            </section>
          )}
          {current && <section className="card print-only">{method}</section>}
        </>
      )}

      <footer>
        <p className="disclaimer">{t.disclaimer}</p>
        <p className="sources">{view === "reconstruction" ? t.sources : (lang === "es" ? "Historia por plataforma: NASA FIRMS · DPA 2023, SUBDERE / IDE Chile · Sin armonización ni máscara persistente adicional." : "Platform history: NASA FIRMS · DPA 2023, SUBDERE / IDE Chile · No harmonization or additional persistence mask.")}</p>
        <p className="sources">We acknowledge the use of data and/or imagery from NASA's Fire Information for Resource Management System (FIRMS) (https://earthdata.nasa.gov/firms), part of NASA's Earth Science Data and Information System (ESDIS).</p>
      </footer>
    </div>
  );
}
