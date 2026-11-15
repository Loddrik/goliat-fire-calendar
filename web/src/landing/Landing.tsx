import { useEffect, useId, useMemo, useRef, useState, type KeyboardEvent } from "react";
import { GoliatLogo } from "../brand/GoliatLogo";
import { Icon } from "../brand/Icon";
import { RegionMap } from "./RegionMap";
import { CommuneSample } from "./CommuneSample";
import { TEXT, FIRMS_ACK, REPO, METHOD, LANCE_URL, dateShort, type Lang, type Text } from "./text";
import "./landing.css";

type Entry = { cut: string; comuna: string; region: string; enabled: boolean };
type Index = { cutoff: string; current_season: number; r_const: number; params?: { train?: number[]; min_aqua?: number; min_wins?: number; band_coverage_1mae?: number; rel_err_median_active?: number }; comunas: Entry[] };

const LANG_KEY = "goliat-lang";
const fold = (s: string) => s.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
// El idioma viaja a la app en ?lang= (la app lo puede leer; hoy decide por el navegador).
const explorer = (cut?: string) => `/explorar?${cut ? `cut=${cut}&` : ""}lang=${document.documentElement.lang === "en" ? "en" : "es"}`;
const go = (cut: string) => { location.href = explorer(cut); };

function initialLang(): Lang {
  const q = new URLSearchParams(location.search).get("lang");
  if (q === "es" || q === "en") return q;
  try { const v = localStorage.getItem(LANG_KEY); if (v === "es" || v === "en") return v; } catch { /* sin almacenamiento */ }
  return navigator.language?.toLowerCase().startsWith("es") ? "es" : "en";
}

export default function Landing() {
  const [lang, setLang] = useState<Lang>(initialLang);
  const [index, setIndex] = useState<Index | null>(null);
  const [sample, setSample] = useState("16302");
  const t = TEXT[lang];

  useEffect(() => {
    const c = new AbortController();
    fetch("/data/index.json", { signal: c.signal, cache: "no-cache" }).then(r => r.json()).then(setIndex).catch(() => {});
    return () => c.abort();
  }, []);
  useEffect(() => {
    document.documentElement.lang = lang;
    document.title = t.htmlTitle;
    try { localStorage.setItem(LANG_KEY, lang); } catch { /* sin almacenamiento */ }
  }, [lang, t.htmlTitle]);

  const comunas = useMemo(() => [...(index?.comunas ?? [])].sort((a, b) => a.comuna.localeCompare(b.comuna, "es")), [index]);
  const enabled = comunas.filter(c => c.enabled).length;
  const train = index?.params?.train ?? [];

  return (
    <div className="lp">
      <header className="lp-top">
        <div className="lp-wrap lp-top-in">
          <a href="/" className="lp-home" aria-label="GOLIAT"><GoliatLogo height={34} lang={lang} /></a>
          <nav className="lp-nav" aria-label={lang === "es" ? "Secciones" : "Sections"}>
            <a href="#como-leer" className="lp-hide-sm">{t.navHow}</a>
            <a href="#challenge" className="lp-hide-sm">{t.navChallenge}</a>
            <a href={explorer()} className="lp-btn"><span className="lp-long">{t.navExplore}</span><span className="lp-short">{t.navExploreShort}</span></a>
            <button className="lp-btn lp-lang" onClick={() => setLang(lang === "es" ? "en" : "es")} aria-label={t.langLabel}>{t.langButton}</button>
          </nav>
        </div>
      </header>

      <main>
        <section className="lp-hero">
          <div className="lp-wrap lp-hero-in">
            <div className="lp-hero-text">
              <Headline key={lang} t={t} />
              <p className="lp-sub">{t.sub}</p>
              <p className="lp-alert"><Icon name="telefono" size={20} /> <span>{t.alert}</span></p>
              <Search comunas={comunas} t={t} />
              <p className="lp-meta">
                {index ? <>{t.meta(comunas.length, dateShort(index.cutoff, lang))} · <a href={explorer()}>{t.allLink(comunas.length)}</a></> : "\u00a0"}
              </p>
            </div>
            <RegionMap t={t} lang={lang} onPick={go} />
          </div>
        </section>

        <section className="lp-section" aria-labelledby="q-title">
          <div className="lp-wrap">
            <div className="lp-head">
              <h2 id="q-title">{t.qTitle}</h2>
              <label className="lp-pick">
                <span>{t.pickLabel}</span>
                <select value={sample} onChange={e => setSample(e.target.value)} id="lp-sample">
                  {comunas.length ? comunas.map(c => <option key={c.cut} value={c.cut}>{c.comuna} · {c.region}</option>) : <option value="16302">Coihueco · Ñuble</option>}
                </select>
              </label>
            </div>
            <p className="lp-lead">{t.qIntro} {t.unit}</p>
            <CommuneSample key={sample} cut={sample} t={t} lang={lang} />
          </div>
        </section>

        <section className="lp-section lp-uses" aria-labelledby="uses-title">
          <div className="lp-wrap">
            <h2 id="uses-title">{t.usesTitle}</h2>
            <div className="lp-cards">
              {t.uses.map(u => (
                <article key={u.icon} className="lp-card">
                  <Icon name={u.icon} size={28} className="lp-card-icon" />
                  <h3>{u.t}</h3>
                  <p>{u.d}</p>
                </article>
              ))}
            </div>
          </div>
        </section>

        <section className="lp-section" id="como-leer" aria-labelledby="how-title">
          <div className="lp-wrap">
            <h2 id="how-title">{t.statesTitle}</h2>
            <p className="lp-lead">{t.statesIntro}</p>
            <ul className="lp-states">
              {t.states.map(([name, desc], i) => (
                <li key={name}>
                  <span className={`lp-cell lp-cell-${i}`} aria-hidden="true">{["12", "41 ±14", "∅", "4•"][i]}</span>
                  <span><b>{name}</b> · {desc}</span>
                </li>
              ))}
            </ul>
            <p className="lp-samples">{t.samplesNote}</p>
            <p className="lp-notis">{t.notIs}</p>
          </div>
        </section>

        <section className="lp-challenge" id="challenge" aria-labelledby="ch-title" lang="en">
          <div className="lp-wrap lp-ch-in">
            <div>
              {t.challengeLead && <p className="lp-ch-lead" lang="es">{t.challengeLead}</p>}
              <p className="lp-eyebrow">The challenge · NASA Space Apps 2026</p>
              <h2 id="ch-title">Harmonization of MODIS and VIIRS Hot Spots</h2>
            </div>
            <div className="lp-ch-body">
              <p>MODIS (1 km pixels, since 2000) and VIIRS (375 m, since 2012) see fire differently. VIIRS picks up far more small, cool hot spots{index ? <> (here about {index.r_const.toFixed(2)}× as many cell-days)</> : null}, so stitching the two records together creates a false jump in 2012. Terra and Aqua are at the end of their missions, with drifting orbits; once MODIS stops, the years before 2012 can only be compared through a bridge like this one.</p>
              {index && (
                <details className="lp-ch-more">
                <summary>{t.challengeMore}</summary>
                <p>
                  We fit one regional factor, <b>Aqua × {index.r_const.toFixed(2)}</b>, against S-NPP VIIRS on the {train[0]}–{train[train.length - 1]} seasons and test it leaving one season out at a time.
                  A commune gets a 2002–2012 estimate only if Aqua saw at least {index.params?.min_aqua ?? "—"} cell-days in {train[0]}–{train[train.length - 1]} and the corrected series beats both the VIIRS climatology and raw Aqua in at least {index.params?.min_wins ?? "—"} of {train.length} held-out seasons.
                  <b> {enabled} of {comunas.length} communes pass</b>; the rest show VIIRS observations from 2012 only, rather than an estimate that failed the test. Every estimate carries its typical error (the mean leave-one-season-out error){index.params?.band_coverage_1mae != null && index.params?.rel_err_median_active != null ? <>: in internal validation across all 54 communes, ±1 covers about {Math.round(index.params.band_coverage_1mae * 100)} % of active months and the median relative error is {Math.round(index.params.rel_err_median_active * 100)} %. It is not a confidence band nor a guarantee: coverage measured in the published communes and in later seasons was somewhat lower.</> : "."}
                </p>
                </details>
              )}
              <p>The harmonization lives in the monthly series from 2002. The regional map above is VIIRS only (2012 onward).</p>
              <p className="lp-ch-links">
                <a href={METHOD} target="_blank" rel="noreferrer">Read the method <Icon name="externo" size={16} /></a>
                <a href={REPO} target="_blank" rel="noreferrer">Source code <Icon name="codigo" size={16} /></a>
                <a href={explorer()}>Open the explorer <Icon name="flecha" size={16} /></a>
              </p>
            </div>
          </div>
        </section>
      </main>

      <footer className="lp-foot">
        <div className="lp-wrap">
          <div className="lp-foot-logos">
            <GoliatLogo height={40} lang={lang} />
            <span className="lp-foot-sep" aria-hidden="true" />
            <img src="/brand/spaceapps/space-apps-color-negro.svg" alt="NASA Space Apps Challenge" height={52} style={{ height: 52, width: "auto" }} />
          </div>
          <p className="lp-foot-team">{t.team}</p>
          <p>{t.sources}</p>
          <p lang="en">{FIRMS_ACK} <a href={LANCE_URL} target="_blank" rel="noreferrer">{t.lance} <Icon name="externo" size={14} /></a></p>
          <p><a href={REPO} target="_blank" rel="noreferrer">{t.repo} <Icon name="externo" size={14} /></a></p>
        </div>
      </footer>
    </div>
  );
}

// Título animado (#37): la pregunta, y después «Usa lo que vieron los satélites para» con la última
// parte cambiando. Todas las frases se apilan en la misma celda para que el alto no salte.
// Ciclo continuo; se pausa con el mouse encima. Con «reducir movimiento» queda la pregunta fija. El lector de pantalla lee hFull una sola vez.
const Q_MS = 3200, WORD_MS = 2400;
function Headline({ t }: { t: Text }) {
  const [step, setStep] = useState(0); // 0 = pregunta; 1..n = palabra n
  const [hover, setHover] = useState(false);
  const [reduced, setReduced] = useState(() => matchMedia("(prefers-reduced-motion: reduce)").matches);
  useEffect(() => {
    const mq = matchMedia("(prefers-reduced-motion: reduce)");
    const on = () => setReduced(mq.matches);
    mq.addEventListener("change", on);
    return () => mq.removeEventListener("change", on);
  }, []);
  const still = reduced || hover;
  useEffect(() => {
    if (still) return;
    const id = setTimeout(() => setStep(s => (s + 1) % (t.hWords.length + 1)), step === 0 ? Q_MS : WORD_MS);
    return () => clearTimeout(id);
  }, [step, still, t.hWords.length]);
  const shown = reduced ? 0 : step;
  return (
    <div className="lp-h1-wrap" onMouseEnter={() => setHover(true)} onMouseLeave={() => setHover(false)}>
      <h1 className="lp-h1">
        <span className="lp-sr">{t.hFull}</span>
        <span className="lp-h1-stack" aria-hidden="true">
          <span className={`lp-h1-frame${shown === 0 ? " on" : ""}`}>{t.hQuestion}</span>
          <span className={`lp-h1-frame${shown > 0 ? " on" : ""}`}>
            {t.hLead}{" "}
            <span className="lp-h1-words">
              {t.hWords.map((w, i) => <span key={w} className={`lp-h1-word${shown === i + 1 ? " on" : ""}`}>{w}</span>)}
            </span>
          </span>
        </span>
      </h1>
    </div>
  );
}

function Search({ comunas, t }: { comunas: Entry[]; t: Text }) {
  const [q, setQ] = useState("");
  const [open, setOpen] = useState(false);
  const [active, setActive] = useState(0);
  const id = useId();
  const input = useRef<HTMLInputElement>(null);
  const results = useMemo(() => {
    const n = fold(q.trim());
    if (!n) return [];
    return comunas.filter(c => fold(c.comuna).includes(n) || c.cut.startsWith(n)).slice(0, 8);
  }, [q, comunas]);

  function onKey(e: KeyboardEvent<HTMLInputElement>) {
    if (e.key === "ArrowDown") { e.preventDefault(); setOpen(true); setActive(a => Math.min(a + 1, results.length - 1)); }
    else if (e.key === "ArrowUp") { e.preventDefault(); setActive(a => Math.max(a - 1, 0)); }
    else if (e.key === "Enter" && results[active]) { e.preventDefault(); go(results[active].cut); }
    else if (e.key === "Escape") setOpen(false);
  }
  const show = open && q.trim().length > 0;
  return (
    <div className="lp-search">
      <label htmlFor={`${id}-in`} className="lp-search-label">{t.searchLabel}</label>
      <div className="lp-search-box">
        <Icon name="buscar" size={20} />
        <input
          ref={input}
          id={`${id}-in`}
          role="combobox"
          aria-expanded={show}
          aria-controls={`${id}-list`}
          aria-autocomplete="list"
          aria-activedescendant={show && results[active] ? `${id}-${results[active].cut}` : undefined}
          placeholder={t.searchPlaceholder}
          value={q}
          autoComplete="off"
          onChange={e => { setQ(e.target.value); setOpen(true); setActive(0); }}
          onFocus={() => setOpen(true)}
          onBlur={() => setTimeout(() => setOpen(false), 150)}
          onKeyDown={onKey}
        />
      </div>
      <span className="lp-sr" aria-live="polite">{show ? (results.length ? t.resultsCount(results.length) : t.noResults) : ""}</span>
      <ul className="lp-results" role="listbox" id={`${id}-list`} hidden={!show}>
          {results.length === 0 && <li className="lp-empty" role="presentation">{t.noResults}</li>}
          {results.map((c, i) => (
            <li key={c.cut} id={`${id}-${c.cut}`} role="option" aria-selected={i === active}
              className={i === active ? "on" : ""} onMouseDown={e => { e.preventDefault(); go(c.cut); }} onMouseEnter={() => setActive(i)}>
              <span>{c.comuna}</span><small>{c.region} · {t.dataFrom(c.enabled ? 2002 : 2012)}</small>
            </li>
          ))}
      </ul>
    </div>
  );
}
