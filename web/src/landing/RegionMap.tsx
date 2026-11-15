import { useEffect, useMemo, useRef, useState } from "react";
import type { Text } from "./text";
import { seasonLabel, type Lang } from "./text";

// Mapa animado del hero (#40): recorre el año de julio a junio y en cada mes se encienden los sectores
// con detección en ese mes, sumando solo temporadas completas (/data/derived/region_months.json, de
// pipeline/publish_web.py). Es para mirar, no para interactuar: elegir una comuna se hace con el buscador
// o en Explorar. Botón de pausa (WCAG 2.2.2); con «reducir movimiento» queda quieto en el mes más alto.
// Canvas sin teselas. Solo dos capas fuera de pantalla (mes actual y siguiente) para no gastar memoria en
// un celular; la animación se detiene cuando el mapa no está a la vista o la pestaña está oculta.

type Cell = { x: number; y: number; ms: number[] };
type Months = { cutoff: string; seasons: number[]; cell_size_deg: number; cells: Cell[] };
type Ring = number[][];
type Feature = { geometry: { type: "Polygon" | "MultiPolygon"; coordinates: Ring[] | Ring[][] } };
type Geo = { features: Feature[] };

const ORDER = [7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6];
// Más temporadas con detección en ese mes = más claro: se «enciende» sobre el azul noche. Rampa de la app.
export const NIGHT_RAMP = ["#4F8FC0", "#9ECAE1", "#C6DBEF", "#FFFFFF"];
const col = (n: number) => NIGHT_RAMP[n >= 5 ? 3 : n >= 3 ? 2 : n === 2 ? 1 : 0];
const HOLD = 1200, FADE = 600, STEP = HOLD + FADE;

const BOUNDS = { lonMin: -73.98, lonMax: -70.97, latMin: -38.51, latMax: -35.99 };
const KX = Math.cos((37.25 * Math.PI) / 180);

function useReducedMotion() {
  const [reduced, setReduced] = useState(() => matchMedia("(prefers-reduced-motion: reduce)").matches);
  useEffect(() => {
    const mq = matchMedia("(prefers-reduced-motion: reduce)");
    const on = () => setReduced(mq.matches);
    mq.addEventListener("change", on);
    return () => mq.removeEventListener("change", on);
  }, []);
  return reduced;
}

export function RegionMap({ t, lang }: { t: Text; lang: Lang }) {
  const wrap = useRef<HTMLDivElement>(null);
  const canvas = useRef<HTMLCanvasElement>(null);
  const [data, setData] = useState<Months | null>(null);
  const [geo, setGeo] = useState<Geo | null>(null);
  const [error, setError] = useState(false);
  const [width, setWidth] = useState(0);
  const reduced = useReducedMotion();
  const [paused, setPaused] = useState(false);
  const [visible, setVisible] = useState(true);
  const [month, setMonth] = useState(9); // índice en ORDER; 9 = abril
  const still = reduced || paused || !visible;

  useEffect(() => {
    const c = new AbortController();
    Promise.all([
      fetch("/data/derived/region_months.json", { signal: c.signal }).then(r => { if (!r.ok) throw new Error("months"); return r.json(); }),
      fetch("/data/comunas.geojson", { signal: c.signal }).then(r => { if (!r.ok) throw new Error("geo"); return r.json(); }),
    ]).then(([d, g]) => { setData(d); setGeo(g); }).catch(() => { if (!c.signal.aborted) setError(true); });
    return () => c.abort();
  }, []);

  useEffect(() => {
    const el = wrap.current;
    if (!el) return;
    const ro = new ResizeObserver(([e]) => setWidth(Math.floor(e.contentRect.width)));
    ro.observe(el);
    const io = new IntersectionObserver(([e]) => setVisible(e.isIntersecting && !document.hidden));
    io.observe(el);
    const vis = () => setVisible(!document.hidden);
    document.addEventListener("visibilitychange", vis);
    return () => { ro.disconnect(); io.disconnect(); document.removeEventListener("visibilitychange", vis); };
  }, []);

  const s = width / ((BOUNDS.lonMax - BOUNDS.lonMin) * KX);
  const height = Math.round((BOUNDS.latMax - BOUNDS.latMin) * s);

  // Por mes (en el orden jul→jun): celdas ordenadas para que las más claras queden encima, y su conteo.
  const byMonth = useMemo(() => {
    if (!data) return null;
    return ORDER.map(m => data.cells.filter(c => c.ms[m - 1] > 0).map(c => ({ x: c.x, y: c.y, n: c.ms[m - 1] })).sort((a, b) => a.n - b.n));
  }, [data]);
  const counts = useMemo(() => byMonth?.map(l => l.length) ?? [], [byMonth]);
  const peak = counts.length ? counts.indexOf(Math.max(...counts)) : 9;

  // Dibujo: base (límites) + mes i + mes j con fundido. Las capas se rehacen solo al cambiar de mes.
  const layers = useRef<{ base?: HTMLCanvasElement; cache: Map<number, HTMLCanvasElement>; key: string }>({ cache: new Map(), key: "" });

  useEffect(() => {
    const cv = canvas.current;
    if (!cv || !byMonth || !geo || width < 60) return;
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    cv.width = width * dpr; cv.height = height * dpr;
    const px = (lon: number) => (lon - BOUNDS.lonMin) * KX * s;
    const py = (lat: number) => (BOUNDS.latMax - lat) * s;
    const off = () => { const c = document.createElement("canvas"); c.width = width * dpr; c.height = height * dpr; const x = c.getContext("2d")!; x.setTransform(dpr, 0, 0, dpr, 0, 0); return [c, x] as const; };
    const L = layers.current;
    const key = `${width}x${height}@${dpr}`;
    if (L.key !== key) { L.base = undefined; L.cache.clear(); L.key = key; }
    if (!L.base) {
      const [c, x] = off();
      x.fillStyle = "#0D2252"; x.strokeStyle = "rgba(169,184,206,.30)"; x.lineWidth = 0.6;
      for (const f of geo.features) {
        const polys = (f.geometry.type === "Polygon" ? [f.geometry.coordinates] : f.geometry.coordinates) as Ring[][];
        x.beginPath();
        for (const poly of polys) for (const ring of poly) { ring.forEach(([lon, lat], i) => (i ? x.lineTo(px(lon), py(lat)) : x.moveTo(px(lon), py(lat)))); x.closePath(); }
        x.fill(); x.stroke();
      }
      L.base = c;
    }
    const step = data!.cell_size_deg;
    const cw = Math.max(1.6, step * KX * s), ch = Math.max(1.6, step * s);
    const paint = (i: number) => {
      const [c, x] = off();
      for (const e of byMonth[i]) {
        const X = px(e.x * step), Y = py((e.y + 1) * step);
        // Halo suave en los sectores con detección en 3 o más temporadas (sin shadowBlur: es caro en celular).
        if (e.n >= 3) { x.fillStyle = "rgba(198,219,239,.22)"; x.fillRect(X - cw, Y - ch, cw * 3, ch * 3); }
        x.fillStyle = col(e.n); x.fillRect(X, Y, cw, ch);
      }
      return c;
    };
    // Caché de a lo más 3 meses pintados (el actual, el siguiente y el que se está yendo).
    const layer = (i: number) => {
      let c = L.cache.get(i);
      if (!c) {
        c = paint(i); L.cache.set(i, c);
        while (L.cache.size > 3) L.cache.delete(L.cache.keys().next().value!);
      }
      return c;
    };
    const ctx = cv.getContext("2d")!;
    const draw = (i: number, fade: number) => {
      const j = (i + 1) % 12;
      const li = layer(i), lj = fade > 0 ? layer(j) : null;
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.clearRect(0, 0, cv.width, cv.height);
      ctx.drawImage(L.base!, 0, 0);
      ctx.globalAlpha = 1 - fade; ctx.drawImage(li, 0, 0);
      if (lj) { ctx.globalAlpha = fade; ctx.drawImage(lj, 0, 0); }
      ctx.globalAlpha = 1;
    };
    if (still) { draw(reduced && !paused ? peak : month, 0); return; }
    let raf = 0;
    const t0 = performance.now() - month * STEP;
    const tick = (now: number) => {
      const tt = (now - t0) % (12 * STEP), i = Math.floor(tt / STEP), f = tt - i * STEP;
      const fade = f < HOLD ? 0 : (f - HOLD) / FADE;
      draw(i, fade);
      const shown = fade > 0.5 ? (i + 1) % 12 : i;
      setMonth(m => (m === shown ? m : shown));
      raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
    // El mes de partida se toma al (re)arrancar; no se reinicia en cada cambio de mes.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [byMonth, geo, width, height, still, reduced]);

  const shownMonth = reduced && !paused ? peak : month;
  const cmax = Math.max(1, ...counts);
  const seasons = data?.seasons ?? [];
  const range = seasons.length ? [seasonLabel(seasons[0]), seasonLabel(seasons[seasons.length - 1])] as const : null;
  const fmt = (n: number) => n.toLocaleString(lang === "es" ? "es-CL" : "en-US");

  return (
    <figure className="lp-map">
      <div className="lp-map-bar">
        <div aria-hidden="true">
          <div className="lp-map-month">{byMonth ? t.monthsLong[shownMonth] : " "}</div>
          <div className="lp-map-count">{byMonth && range ? t.mapCount(fmt(counts[shownMonth]), seasons.length) : " "}</div>
        </div>
        {!reduced && byMonth && (
          <button type="button" className="lp-map-pause" onClick={() => setPaused(p => !p)} aria-label={paused ? t.mapPlay : t.mapPause} aria-pressed={paused}>
            {paused
              ? <svg width="14" height="14" viewBox="0 0 14 14" aria-hidden="true"><path d="M3 1 13 7 3 13z" fill="currentColor" /></svg>
              : <svg width="14" height="14" viewBox="0 0 14 14" aria-hidden="true"><rect x="2" y="1" width="3.5" height="12" fill="currentColor" /><rect x="8.5" y="1" width="3.5" height="12" fill="currentColor" /></svg>}
          </button>
        )}
      </div>
      <div className="lp-map-canvas" ref={wrap} style={{ height: height || undefined }}>
        {error ? <p className="lp-map-msg">{t.mapError}</p> : !byMonth ? <p className="lp-map-msg">{t.mapLoading}</p> : null}
        <canvas ref={canvas} role="img" aria-label={range ? t.mapAria(range[0], range[1], t.monthsLong[peak]) : t.mapLoading}
          className={byMonth ? "on" : ""} style={{ width, height }} />
      </div>
      {byMonth && (
        <div className="lp-map-tl" aria-hidden="true">
          {counts.map((c, i) => (
            <div key={i} className={i === shownMonth ? "on" : ""}><i style={{ height: `${Math.max(3, (c / cmax) * 34)}px` }} /><span>{t.monthsShort[i]}</span></div>
          ))}
        </div>
      )}
      <figcaption className="lp-map-foot">
        <span className="lp-legend">
          <span className="lp-legend-label">{t.legend}</span>
          {NIGHT_RAMP.map((c, i) => <span key={c}><i style={{ background: c }} />{t.legendClasses[i]}</span>)}
        </span>
        <span className="lp-map-note">{range ? t.mapNote(range[0], range[1]) : " "}</span>
      </figcaption>
    </figure>
  );
}
