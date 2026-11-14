import { useEffect, useRef, useState } from "react";
import * as maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
// MapLibre ≥ 6 carga su worker como módulo aparte; Vite no lo emite solo, así que se le pasa la URL del archivo copiado.
import maplibreWorkerUrl from "maplibre-gl/dist/maplibre-gl-worker.mjs?url";
maplibregl.setWorkerUrl(maplibreWorkerUrl);
import type { ComunaDoc } from "./types";
import type { Lang } from "./i18n";

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
  es: "El mapa no se puede mostrar en este navegador (le falta aceleración gráfica). El calendario y las descargas funcionan igual.",
  en: "The map cannot be shown in this browser (graphics acceleration is missing). The calendar and downloads still work.",
};

const STYLE = "https://tiles.openfreemap.org/styles/positron";
const REC_RAMP: [number, string][] = [[1, "#fee5d9"], [2, "#fcae91"], [3, "#fb6a4a"], [5, "#de2d26"], [8, "#a50f15"]];

export function RecurrenceMap({ doc, onPick, lang = "es" }: { doc: ComunaDoc | null; onPick: (cut: string) => void; lang?: Lang }) {
  const el = useRef<HTMLDivElement>(null);
  const map = useRef<maplibregl.Map | null>(null);
  const ready = useRef(false);
  const [failed, setFailed] = useState(() => !webglAvailable());

  useEffect(() => {
    if (failed || !el.current || map.current) return;
    let m: maplibregl.Map;
    try {
      m = new maplibregl.Map({ container: el.current, style: STYLE, center: [-72.6, -37.0], zoom: 6.3, attributionControl: { compact: true }, canvasContextAttributes: { preserveDrawingBuffer: true } });
    } catch {
      setFailed(true);
      return;
    }
    m.addControl(new maplibregl.NavigationControl({ showCompass: false }), "top-right");
    m.on("load", () => {
      m.addSource("comunas", { type: "geojson", data: "/data/comunas.geojson", promoteId: "cut" });
      m.addLayer({ id: "comunas-fill", type: "fill", source: "comunas", paint: { "fill-color": "#2a788e", "fill-opacity": ["case", ["boolean", ["feature-state", "selected"], false], 0.08, 0.02] } });
      m.addLayer({ id: "comunas-line", type: "line", source: "comunas", paint: { "line-color": ["case", ["boolean", ["feature-state", "selected"], false], "#111", "#2a788e"], "line-width": ["case", ["boolean", ["feature-state", "selected"], false], 2.5, 0.8] } });
      m.addSource("rec", { type: "geojson", data: { type: "FeatureCollection", features: [] } });
      m.addLayer({ id: "rec-fill", type: "fill", source: "rec", paint: { "fill-color": ["step", ["get", "n"], REC_RAMP[0][1], ...REC_RAMP.slice(1).flat()], "fill-opacity": 0.75 } });
      m.on("click", "comunas-fill", (e: maplibregl.MapMouseEvent & { features?: maplibregl.MapGeoJSONFeature[] }) => { const f = e.features?.[0]; if (f?.properties?.cut) onPick(String(f.properties.cut)); });
      m.on("mouseenter", "comunas-fill", () => (m.getCanvas().style.cursor = "pointer"));
      m.on("mouseleave", "comunas-fill", () => (m.getCanvas().style.cursor = ""));
      const pop = new maplibregl.Popup({ closeButton: false, closeOnClick: false });
      m.on("mousemove", "rec-fill", (e: maplibregl.MapMouseEvent & { features?: maplibregl.MapGeoJSONFeature[] }) => { const p = e.features?.[0]?.properties; if (p) pop.setLngLat(e.lngLat).setHTML(`<b>${p.n}</b> temporadas · ${p.d} días · ${p.f}–${p.l}`).addTo(m); });
      m.on("mouseleave", "rec-fill", () => pop.remove());
      ready.current = true;
      if (doc) paint(m, doc);
    });
    map.current = m;
    return () => { m.remove(); map.current = null; ready.current = false; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => { if (map.current && ready.current && doc) paint(map.current, doc); }, [doc]);

  if (failed) return <p className="map-unavailable" role="status">{MAP_UNAVAILABLE[lang]}</p>;

  return (
    <div className="map-wrap">
      <div ref={el} className="map" aria-label="Mapa de comunas y recurrencia" />
      <div className="legend small">
        {REC_RAMP.map(([n, c], i) => <span key={n}><i style={{ background: c }} /> {i === REC_RAMP.length - 1 ? `${n}+` : REC_RAMP[i + 1] ? `${n}–${REC_RAMP[i + 1][0] - 1}` : n}</span>)}
        <span>temporadas / seasons</span>
      </div>
    </div>
  );
}

let lastSelected: string | null = null;
function paint(m: maplibregl.Map, doc: ComunaDoc) {
  if (lastSelected) m.setFeatureState({ source: "comunas", id: lastSelected }, { selected: false });
  m.setFeatureState({ source: "comunas", id: doc.cut }, { selected: true });
  lastSelected = doc.cut;
  const feats = doc.recurrence.map((c) => {
    const x0 = c.x * 0.01, y0 = c.y * 0.01;
    return { type: "Feature" as const, properties: { n: c.n, d: c.d, f: c.f, l: c.l }, geometry: { type: "Polygon" as const, coordinates: [[[x0, y0], [x0 + 0.01, y0], [x0 + 0.01, y0 + 0.01], [x0, y0 + 0.01], [x0, y0]]] } };
  });
  (m.getSource("rec") as maplibregl.GeoJSONSource).setData({ type: "FeatureCollection", features: feats });
  if (feats.length) {
    const xs = doc.recurrence.map((c) => c.x), ys = doc.recurrence.map((c) => c.y);
    m.fitBounds([[Math.min(...xs) * 0.01 - 0.05, Math.min(...ys) * 0.01 - 0.05], [Math.max(...xs) * 0.01 + 0.06, Math.max(...ys) * 0.01 + 0.06]], { padding: 20, duration: 600, maxZoom: 10.5 });
  }
}
