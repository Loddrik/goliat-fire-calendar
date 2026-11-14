import { useEffect, useMemo, useRef, useState } from "react";
import type { Text } from "./text";
import { seasonLabel, dateShort, type Lang } from "./text";

// Mapa regional dibujado en canvas desde /data/derived/region.json (celdas de 0,01° con temporadas
// con detección, solo VIIRS 2012→) y /data/comunas.geojson. Sin teselas: no depende de un servidor de mapas.

type Cell = { cut: string; x: number; y: number; n: number };
type Region = { cutoff: string; seasons: number[]; cell_size_deg: number; cells: Cell[] };
type Ring = number[][];
type Feature = { properties: { cut: string; comuna: string; region: string }; geometry: { type: "Polygon" | "MultiPolygon"; coordinates: Ring[] | Ring[][] } };
type Geo = { features: Feature[] };

// Misma rampa y mismos tramos que el mapa de la app (1 · 2 · 3–4 · 5–7 · 8 o más temporadas).
const RAMP = ["#C6DBEF", "#9ECAE1", "#6BAED6", "#3182BD", "#08519C"];
const cls = (n: number) => (n >= 8 ? 4 : n >= 5 ? 3 : n >= 3 ? 2 : n === 2 ? 1 : 0);

// Comunas de referencia para ubicarse (capitales regionales y provincial); solo el nombre, sin datos.
const LANDMARKS = ["08101", "16101", "08301"];

const BOUNDS = { lonMin: -73.98, lonMax: -70.97, latMin: -38.51, latMax: -35.99 };
const KX = Math.cos((37.25 * Math.PI) / 180);

export function RegionMap({ t, lang, onPick }: { t: Text; lang: Lang; onPick: (cut: string) => void }) {
  const wrap = useRef<HTMLDivElement>(null);
  const canvas = useRef<HTMLCanvasElement>(null);
  const [region, setRegion] = useState<Region | null>(null);
  const [geo, setGeo] = useState<Geo | null>(null);
  const [error, setError] = useState(false);
  const [width, setWidth] = useState(0);
  const [hover, setHover] = useState<{ cut: string; name: string; x: number; y: number } | null>(null);
  const touch = useRef(false);

  useEffect(() => {
    const c = new AbortController();
    Promise.all([
      fetch("/data/derived/region.json", { signal: c.signal }).then(r => { if (!r.ok) throw new Error("region"); return r.json(); }),
      fetch("/data/comunas.geojson", { signal: c.signal }).then(r => { if (!r.ok) throw new Error("geo"); return r.json(); }),
    ]).then(([r, g]) => { setRegion(r); setGeo(g); }).catch(() => { if (!c.signal.aborted) setError(true); });
    return () => c.abort();
  }, []);

  useEffect(() => {
    if (!wrap.current) return;
    const ro = new ResizeObserver(([e]) => setWidth(Math.floor(e.contentRect.width)));
    ro.observe(wrap.current);
    return () => ro.disconnect();
  }, []);

  const s = width / ((BOUNDS.lonMax - BOUNDS.lonMin) * KX);
  const height = Math.round((BOUNDS.latMax - BOUNDS.latMin) * s);
  const px = (lon: number) => (lon - BOUNDS.lonMin) * KX * s;
  const py = (lat: number) => (BOUNDS.latMax - lat) * s;

  // Un Path2D por comuna, en píxeles CSS, para dibujar y para saber qué comuna está bajo el puntero.
  const paths = useMemo(() => {
    if (!geo || !width) return [];
    return geo.features.map(f => {
      const p = new Path2D();
      const polys = (f.geometry.type === "Polygon" ? [f.geometry.coordinates] : f.geometry.coordinates) as Ring[][];
      for (const poly of polys) for (const ring of poly) {
        ring.forEach(([lon, lat], i) => (i ? p.lineTo(px(lon), py(lat)) : p.moveTo(px(lon), py(lat))));
        p.closePath();
      }
      let x0 = Infinity, x1 = -Infinity, y0 = Infinity, y1 = -Infinity;
      for (const poly of polys) for (const [lon, lat] of poly[0]) { x0 = Math.min(x0, lon); x1 = Math.max(x1, lon); y0 = Math.min(y0, lat); y1 = Math.max(y1, lat); }
      return { cut: f.properties.cut, name: f.properties.comuna, path: p, cx: px((x0 + x1) / 2), cy: py((y0 + y1) / 2) };
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [geo, width]);

  const sorted = useMemo(() => (region ? [...region.cells].sort((a, b) => a.n - b.n) : []), [region]);

  useEffect(() => {
    const cv = canvas.current;
    if (!cv || !region || !paths.length) return;
    const dpr = window.devicePixelRatio || 1;
    cv.width = width * dpr; cv.height = height * dpr;
    const ctx = cv.getContext("2d")!;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, width, height);
    for (const p of paths) {
      ctx.fillStyle = p.cut === hover?.cut ? "#E4EEF3" : "#F1F0EA";
      ctx.fill(p.path);
    }
    ctx.lineWidth = 0.7; ctx.strokeStyle = "#C9C9C0";
    for (const p of paths) ctx.stroke(p.path);
    const step = region.cell_size_deg;
    const cw = Math.max(1.4, step * KX * s), ch = Math.max(1.4, step * s);
    for (const c of sorted) {
      ctx.fillStyle = RAMP[cls(c.n)];
      ctx.fillRect(px(c.x * step), py((c.y + 1) * step), cw, ch);
    }
    const h = paths.find(p => p.cut === hover?.cut);
    if (h) { ctx.lineWidth = 1.8; ctx.strokeStyle = "#1A1A1A"; ctx.stroke(h.path); }
    ctx.font = "500 12px 'IBM Plex Sans', system-ui, sans-serif";
    ctx.textAlign = "center"; ctx.textBaseline = "middle"; ctx.lineJoin = "round";
    for (const p of paths.filter(p => LANDMARKS.includes(p.cut))) {
      ctx.fillStyle = "#1A1A1A"; ctx.beginPath(); ctx.arc(p.cx, p.cy, 2.6, 0, Math.PI * 2); ctx.fill();
      ctx.lineWidth = 3.5; ctx.strokeStyle = "rgba(255,255,255,.92)"; ctx.strokeText(p.name, p.cx, p.cy - 12);
      ctx.fillText(p.name, p.cx, p.cy - 12);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [region, paths, sorted, hover?.cut, width, height]);

  function pick(e: { clientX: number; clientY: number }) {
    const cv = canvas.current;
    if (!cv || !paths.length) return null;
    const r = cv.getBoundingClientRect();
    const x = e.clientX - r.left, y = e.clientY - r.top;
    const ctx = cv.getContext("2d")!;
    const dpr = window.devicePixelRatio || 1;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    const hit = paths.find(p => ctx.isPointInPath(p.path, x, y));
    return hit ? { cut: hit.cut, name: hit.name, x, y } : null;
  }

  const seasons = region?.seasons ?? [];
  return (
    <figure className="lp-map">
      <figcaption className="lp-map-head">
        <span className="lp-map-title">{seasons.length ? t.mapTitle(seasonLabel(seasons[0]), seasonLabel(seasons[seasons.length - 1]), dateShort(region!.cutoff, lang)) : t.mapLoading}</span>
        <span className="lp-map-note">{t.mapNote}</span>
      </figcaption>
      <div className="lp-map-canvas" ref={wrap} style={{ height: height || undefined }}>
        {error ? <p className="lp-map-msg">{t.mapError}</p> : !region ? <p className="lp-map-msg">{t.mapLoading}</p> : null}
        <canvas
          ref={canvas}
          role="img"
          aria-label={t.mapAria}
          style={{ width, height, cursor: hover ? "pointer" : "default" }}
          onPointerDown={e => { touch.current = e.pointerType !== "mouse"; }}
          onPointerMove={e => { if (e.pointerType === "mouse") setHover(pick(e)); }}
          onPointerLeave={e => { if (e.pointerType === "mouse") setHover(null); }}
          onClick={e => {
            const h = pick(e);
            if (!h) { setHover(null); return; }
            // En pantallas táctiles, el primer toque muestra el nombre y el segundo abre la comuna.
            if (touch.current && hover?.cut !== h.cut) { setHover(h); return; }
            onPick(h.cut);
          }}
        />
        {hover && (
          <div className="lp-map-tip" style={{ left: Math.max(4, Math.min(hover.x + 12, width - 250)), top: Math.max(hover.y - 34, 4) }} aria-hidden="true">
            {hover.name} <span>{touch.current ? `· ${t.mapTapAgain}` : "→"}</span>
          </div>
        )}
      </div>
      <div className="lp-map-foot">
        <span className="lp-legend">
          {RAMP.map((c, i) => <span key={c}><i style={{ background: c }} />{t.legendClasses[i]}</span>)}
        </span>
        <span className="lp-legend-label">{t.legend} · {t.mapHint}</span>
      </div>
    </figure>
  );
}
