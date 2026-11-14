import { useEffect, useMemo, useRef, useState } from "react";
import * as maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
// MapLibre ≥ 6 carga su worker como módulo aparte; Vite no lo emite solo, así que se le pasa la URL del archivo copiado.
import maplibreWorkerUrl from "maplibre-gl/dist/maplibre-gl-worker.mjs?url";
maplibregl.setWorkerUrl(maplibreWorkerUrl);
import type { Lang } from "./i18n";
import type { RegionDoc } from "./types";
import { seasonLabel } from "./types";
import { BLUES, MAP_BREAKS, MAP_LABELS, UI, dmy } from "./ui";

const STYLE = "https://tiles.openfreemap.org/styles/positron";
const CELL = 0.01;
// Regla 4: el zoom máximo no llega a nivel de predio (a z12 una celda de ~1 km mide ~30 px).
const MAX_ZOOM = 12;

// Computadores municipales viejos o con la aceleración gráfica desactivada no tienen WebGL:
// MapLibre lanza al crear el mapa y, sin este resguardo, la app entera quedaba en blanco.
function webglAvailable(): boolean {
  try {
    const c = document.createElement("canvas");
    return !!(c.getContext("webgl2") || c.getContext("webgl"));
  } catch {
    return false;
  }
}
export const MAP_UNAVAILABLE = {
  es: "El mapa no se puede mostrar en este navegador (le falta aceleración gráfica). La ficha de la comuna, la tabla y las descargas funcionan igual.",
  en: "The map cannot be shown in this browser (graphics acceleration is missing). The commune card, table and downloads still work.",
};

type Ring = [number, number][];
type ComunaFeature = { type: "Feature"; properties: { cut: string; comuna: string; region: string };
  geometry: { type: "Polygon"; coordinates: Ring[] } | { type: "MultiPolygon"; coordinates: Ring[][] } };
type Geo = { type: "FeatureCollection"; features: ComunaFeature[] };
type Fc = { type: "FeatureCollection"; features: { type: "Feature"; properties: Record<string, number | string>; geometry: { type: "Point"; coordinates: number[] } | { type: "Polygon"; coordinates: number[][][] } }[] };

function bbox(f: ComunaFeature): [[number, number], [number, number]] {
  let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
  const polys: Ring[][] = f.geometry.type === "Polygon" ? [f.geometry.coordinates] : f.geometry.coordinates;
  for (const p of polys) for (const ring of p) for (const [x, y] of ring) { x0 = Math.min(x0, x); y0 = Math.min(y0, y); x1 = Math.max(x1, x); y1 = Math.max(y1, y); }
  return [[x0, y0], [x1, y1]];
}

// Color por tramo fijo, igual para "temporadas con detección" (Todas) y "días con detección" (una temporada).
const colorExpr = (prop: string): maplibregl.ExpressionSpecification =>
  ["step", ["get", prop], BLUES[0], MAP_BREAKS[1], BLUES[1], MAP_BREAKS[2], BLUES[2], MAP_BREAKS[3], BLUES[3], MAP_BREAKS[4], BLUES[4]];

export function ExploreMap({ region, selected, onPick, season, setSeason, lang }: {
  region: RegionDoc | null; selected: string | null; onPick: (cut: string) => void;
  season: number | null; setSeason: (s: number | null) => void; lang: Lang;
}) {
  const T = UI[lang];
  const el = useRef<HTMLDivElement>(null);
  const map = useRef<maplibregl.Map | null>(null);
  const geo = useRef<Geo | null>(null);
  const popup = useRef<maplibregl.Popup | null>(null);
  const [ready, setReady] = useState(false);
  const [failed, setFailed] = useState(() => !webglAvailable());
  const seasons = region?.seasons ?? [];
  const current = region?.current_season;
  const cutoff = region ? dmy(region.cutoff) : "";
  const prop = season == null ? "n" : `s${seasons.indexOf(season)}`;

  // Celdas publicadas como puntos (lejos) y cuadrados de 0,01° (cerca). Solo se reordenan; no se calcula nada.
  const data = useMemo(() => {
    if (!region) return null;
    const props = (c: RegionDoc["cells"][number]) => {
      const p: Record<string, number | string> = { cut: c.cut, n: c.n, d: c.d };
      c.s.forEach((v, i) => (p[`s${i}`] = v));
      return p;
    };
    const pts: Fc = { type: "FeatureCollection", features: region.cells.map((c) => ({ type: "Feature", properties: props(c), geometry: { type: "Point", coordinates: [(c.x + 0.5) * CELL, (c.y + 0.5) * CELL] } })) };
    const sq: Fc = { type: "FeatureCollection", features: region.cells.map((c) => {
      const x0 = c.x * CELL, y0 = c.y * CELL;
      return { type: "Feature", properties: props(c), geometry: { type: "Polygon", coordinates: [[[x0, y0], [x0 + CELL, y0], [x0 + CELL, y0 + CELL], [x0, y0 + CELL], [x0, y0]]] } };
    }) };
    return { pts, sq };
  }, [region]);

  useEffect(() => {
    if (failed || !el.current || map.current || !data) return;
    let m: maplibregl.Map;
    try {
      m = new maplibregl.Map({ container: el.current, style: STYLE, center: [-72.4, -37.1], zoom: 6.4, minZoom: 5.5, maxZoom: MAX_ZOOM, attributionControl: { compact: true }, canvasContextAttributes: { preserveDrawingBuffer: true } });
    } catch {
      setFailed(true);
      return;
    }
    m.addControl(new maplibregl.NavigationControl({ showCompass: false }), "top-right");
    m.on("load", async () => {
      // Sin puntos de interés del mapa base (comercios, empresas); quedan pueblos, caminos y ríos.
      for (const l of m.getStyle().layers ?? []) if (/poi/i.test(l.id)) m.setLayoutProperty(l.id, "visibility", "none");
      const firstLabel = (m.getStyle().layers ?? []).find((l) => l.type === "symbol")?.id;
      const g: Geo = await fetch("/data/comunas.geojson").then((r) => r.json());
      geo.current = g;
      m.addSource("comunas", { type: "geojson", data: g, promoteId: "cut" });
      m.addLayer({ id: "comunas-fill", type: "fill", source: "comunas", paint: { "fill-color": "#000", "fill-opacity": 0 } }, firstLabel);
      m.addSource("cells-pt", { type: "geojson", data: data.pts });
      m.addSource("cells-sq", { type: "geojson", data: data.sq });
      const op: maplibregl.ExpressionSpecification = ["case", ["boolean", ["feature-state", "dim"], false], 0.25, 0.85];
      m.addLayer({ id: "cells-dot", type: "circle", source: "cells-pt", maxzoom: 9, paint: { "circle-color": colorExpr("n"), "circle-radius": ["interpolate", ["linear"], ["zoom"], 5.5, 1.2, 9, 3], "circle-opacity": 0.85 } }, firstLabel);
      m.addLayer({ id: "cells-fill", type: "fill", source: "cells-sq", minzoom: 9, paint: { "fill-color": colorExpr("n"), "fill-opacity": op } }, firstLabel);
      m.addLayer({ id: "comunas-line", type: "line", source: "comunas", paint: {
        "line-color": ["case", ["boolean", ["feature-state", "selected"], false], "#1A1A1A", "#8F8F87"],
        "line-width": ["case", ["boolean", ["feature-state", "selected"], false], 2.5, 0.7] } }, firstLabel);
      m.on("click", (e) => {
        const cells = m.queryRenderedFeatures(e.point, { layers: ["cells-fill", "cells-dot"].filter((id) => m.getLayer(id)) });
        if (cells.length) { showPopup(m, e.lngLat, cells[0].properties as Record<string, number>); return; }
        const com = m.queryRenderedFeatures(e.point, { layers: ["comunas-fill"] });
        if (com[0]?.properties?.cut) onPickRef.current(String(com[0].properties.cut));
      });
      m.on("mousemove", (e) => {
        const hit = m.queryRenderedFeatures(e.point, { layers: ["comunas-fill"] }).length > 0;
        m.getCanvas().style.cursor = hit ? "pointer" : "";
      });
      setReady(true);
    });
    map.current = m;
    return () => { m.remove(); map.current = null; setReady(false); };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [data, failed]);

  // Referencias vivas para los manejadores registrados una sola vez.
  const onPickRef = useRef(onPick);
  const popupCtx = useRef({ season, seasons, lang });
  useEffect(() => { onPickRef.current = onPick; popupCtx.current = { season, seasons, lang }; });

  function showPopup(m: maplibregl.Map, at: maplibregl.LngLat, p: Record<string, number>) {
    const { season: s, seasons: ss, lang: lg } = popupCtx.current;
    const t = UI[lg];
    const total = ss.length;
    const lines = s == null ? [t.popupAll(p.n, total, p.d)] : t.popupSeason(seasonLabel(s), p[`s${ss.indexOf(s)}`] ?? 0, p.n, total);
    popup.current?.remove();
    const div = document.createElement("div");
    const b = document.createElement("b"); b.textContent = t.sector; div.appendChild(b);
    lines.forEach((l, i) => { const x = document.createElement("div"); x.textContent = l; if (i) x.className = "pop-sub"; div.appendChild(x); });
    popup.current = new maplibregl.Popup({ closeButton: true, maxWidth: "260px" }).setLngLat(at).setDOMContent(div).addTo(m);
  }

  // Temporada elegida: se muestran solo las celdas con detección en esa temporada, coloreadas por días.
  useEffect(() => {
    const m = map.current;
    if (!m || !ready) return;
    const filter: maplibregl.FilterSpecification = [">", ["get", prop], 0];
    for (const id of ["cells-dot", "cells-fill"]) { m.setFilter(id, filter); m.setPaintProperty(id, id === "cells-dot" ? "circle-color" : "fill-color", colorExpr(prop)); }
    popup.current?.remove();
  }, [prop, ready]);

  // Comuna elegida: borde marcado, celdas de las otras comunas atenuadas y el mapa se acerca.
  const last = useRef<string | null>(null);
  useEffect(() => {
    const m = map.current;
    if (!m || !ready || !geo.current) return;
    if (last.current) m.setFeatureState({ source: "comunas", id: last.current }, { selected: false });
    last.current = selected;
    if (!selected) return;
    m.setFeatureState({ source: "comunas", id: selected }, { selected: true });
    const f = geo.current.features.find((x: ComunaFeature) => x.properties.cut === selected);
    if (f) m.fitBounds(bbox(f), { padding: { top: 40, bottom: 120, left: window.innerWidth > 860 ? 420 : 20, right: 40 }, duration: 700, maxZoom: 11 });
  }, [selected, ready]);
  useEffect(() => {
    const m = map.current;
    if (!m || !ready || !region) return;
    // Atenuar con el filtro de opacidad por comuna (sin estado por celda): una expresión sobre "cut".
    m.setPaintProperty("cells-fill", "fill-opacity", selected ? ["case", ["==", ["get", "cut"], selected], 0.85, 0.3] : 0.85);
    m.setPaintProperty("cells-dot", "circle-opacity", selected ? ["case", ["==", ["get", "cut"], selected], 0.9, 0.3] : 0.85);
  }, [selected, ready, region]);

  const label = season == null ? T.labelAll(seasons.length, cutoff)
    : season === current ? T.labelCurrent(seasonLabel(season), cutoff) : T.labelSeason(seasonLabel(season), season);

  return (
    <div className="xmap">
      <p className="map-notice" role="note">ⓘ {T.mapNotice}</p>
      {failed ? <p className="map-unavailable" role="status">{MAP_UNAVAILABLE[lang]}</p> : <div ref={el} className="xmap-canvas" aria-label={label} />}
      <div className="season-bar">
        <div className="chips" role="group" aria-label={lang === "es" ? "Temporada" : "Season"}>
          <button className={season == null ? "on" : ""} aria-pressed={season == null} onClick={() => setSeason(null)}>{T.all} 2012→</button>
          {seasons.map((s) => (
            <button key={s} className={season === s ? "on" : ""} aria-pressed={season === s} onClick={() => setSeason(s)}>
              {seasonLabel(s).slice(2)}{s === current ? "•" : ""}
            </button>
          ))}
        </div>
        <p className="chips-label">{label}</p>
      </div>
      <div className="map-legend">
        <b>{season == null ? T.legendAll(seasons.length) : T.legendSeason(seasonLabel(season))}</b>
        <div className="sw-row">
          <span><i className="sw-none" />{T.none}</span>
          {BLUES.map((c, i) => <span key={c}><i style={{ background: c }} />{i < MAP_LABELS.length ? MAP_LABELS[i] : `8 ${T.more}`}</span>)}
        </div>
        <small>{T.basemap}</small>
      </div>
    </div>
  );
}
