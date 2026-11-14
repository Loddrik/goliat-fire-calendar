import { parseCSV, normalizeRows, selectRows, summarize, csvText, observedMonths } from "./core.mjs";
const $ = id => document.getElementById(id);
const bbox = { west: -73.9, south: -38.9, east: -71.0, north: -35.8 };
const state = { sources: [], history: null, current: null, selected: [], normalized: null, headers: [], monthly: [], query: null, busy: 0 };
const number = value => Number(value).toLocaleString("es-CL");
const hash = async buffer => Array.from(new Uint8Array(await crypto.subtle.digest("SHA-256", buffer))).map(value => value.toString(16).padStart(2, "0")).join("");
function element(tag, text, className) {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  if (className) node.className = className;
  return node;
}
function message(text, error = false) {
  $("message").textContent = text;
  $("message").classList.toggle("error", error);
}
function download(name, content, type) {
  const url = URL.createObjectURL(new Blob([content], { type }));
  const link = document.createElement("a");
  link.href = url; link.download = name; link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
function resetView(text, error = false) {
  state.selected = []; state.monthly = []; state.query = null;
  $("count").textContent = "—"; $("date-min").textContent = "—"; $("date-max").textContent = "—";
  ["export-csv", "export-monthly", "export-manifest"].forEach(id => { $(id).disabled = true; });
  $("file-summary").hidden = true; $("calendar-wrap").hidden = true;
  $("monthly-note").textContent = "";
  for (const [target, span] of [["monthly-body", 5], ["records-body", 6]]) {
    const cell = element("td", "Sin datos cargados.", "empty"); cell.colSpan = span;
    const row = document.createElement("tr"); row.append(cell); $(target).replaceChildren(row);
  }
  message(text, error);
}
function clearResults(text, error = false) {
  state.current = null; state.normalized = null;
  resetView(text, error);
}
function rowOf(values) {
  const row = document.createElement("tr");
  values.forEach(value => row.append(element("td", String(value ?? "—"))));
  return row;
}
function renderCalendar(monthly) {
  const byMonth = new Map(monthly.map(row => [row.month, row]));
  const seasons = [...new Set(monthly.map(row => {
    const [year, month] = row.month.split("-").map(Number);
    return month >= 7 ? year : year - 1;
  }))].sort((a, b) => a - b);
  const maximum = Math.max(1, ...monthly.map(row => row.cellDays || 0));
  const fragment = document.createDocumentFragment();
  for (const season of seasons) {
    const tr = document.createElement("tr");
    const heading = element("th", season + "–" + String(season + 1).slice(-2));
    heading.scope = "row"; tr.append(heading);
    for (const month of [7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6]) {
      const year = month >= 7 ? season : season + 1;
      const key = year + "-" + String(month).padStart(2, "0");
      const value = byMonth.get(key);
      const available = value && value.cellDays !== null;
      const cell = element("td", available ? number(value.cellDays) : "—");
      const label = available ? key + ": " + value.cellDays + " celdas-día; cobertura desconocida"
        : key + ": " + (value?.status === "missing-file" ? "archivo anual no disponible" : "fuera del período solicitado");
      cell.title = label; cell.setAttribute("aria-label", label);
      cell.className = available ? "heat-" + (value.cellDays ? Math.max(1, Math.ceil(Math.log1p(value.cellDays) / Math.log1p(maximum) * 4)) : 0) : "heat-missing";
      tr.append(cell);
    }
    fragment.append(tr);
  }
  $("calendar-body").replaceChildren(fragment);
  $("calendar-caption").textContent = state.current.commune.name + " · CUT " + state.current.commune.cut + " · " + state.current.platform + " · observaciones diurnas, Type=0 · escala de color propia de esta consulta, no comparable entre sensores";
  $("calendar-wrap").hidden = false;
}
function renderQuery() {
  if (!state.current || !state.normalized) return;
  const historical = state.current.kind === "historical-observed";
  const start = $("start-month").value, end = $("end-month").value;
  if ((start && end && start > end) || (historical && (start < state.current.start || end > state.current.end || !start || !end))) {
    resetView(historical ? "Elige un período dentro de " + state.current.start + " y " + state.current.end + ", con inicio anterior al fin." : "La fecha inicial debe ser anterior a la final.", true);
    return;
  }
  const filters = { dayOnly: historical || $("day-only").checked, bbox: !historical && $("scope-select").value === "pilot" ? bbox : null, minMODIS: 30 };
  const selection = selectRows(state.normalized.valid, filters);
  const selected = selection.selected.filter(row => (!start || row.acq_date.slice(0, 7) >= start) && (!end || row.acq_date.slice(0, 7) <= end));
  const excludedPeriod = selection.selected.length - selected.length;
  state.selected = selected;
  const summary = summarize(selected);
  state.monthly = historical ? observedMonths(summary.monthly, { start, end, availableYears: state.current.available_years, instrument: state.current.instrument, platform: state.current.platform }) : summary.monthly;
  $("count").textContent = number(summary.count);
  $("date-min").textContent = summary.dateMin || "—";
  $("date-max").textContent = summary.dateMax || "—";
  const visibleMonthly = state.monthly.slice(-24);
  $("monthly-body").replaceChildren(...visibleMonthly.map(group => rowOf([group.month, group.instrument, group.platform, group.detections === null ? "—" : number(group.detections), group.cellDays === null ? "—" : number(group.cellDays)])));
  $("monthly-note").textContent = state.monthly.length > 24 ? "Vista de los últimos 24 de " + state.monthly.length + " meses. La descarga incluye la serie completa." : "";
  if (!state.monthly.length) {
    const cell = element("td", "Ninguna fila supera los filtros de esta consulta. No implica ausencia de actividad.", "empty"); cell.colSpan = 5;
    const row = document.createElement("tr"); row.append(cell); $("monthly-body").append(row);
  }
  $("records-body").replaceChildren(...selected.slice(0, 100).map(row => rowOf([row.acq_date, String(row.acq_time || "").padStart(4, "0"), row.latitude, row.longitude, row.satellite || "sin dato", row.confidence || "sin dato"])));
  if (!selected.length) {
    const cell = element("td", "Sin detecciones seleccionadas.", "empty"); cell.colSpan = 6;
    const row = document.createElement("tr"); row.append(cell); $("records-body").append(row);
  }
  const rawCount = state.normalized.valid.length + state.normalized.rejected.length;
  $("file-summary").textContent = "Entrada cargada: " + number(rawCount) + " filas · Formato inválido: " + number(state.normalized.rejected.length) + " · Duplicadas detectadas: " + number(state.normalized.duplicates) + " (las detecciones las conservan; las celdas-día no repiten ocupaciones) · Excluidas por franja: " + number(selection.excludedNightOrUnknown) + " · Confianza/instrumento: " + number(selection.excludedConfidence) + " · Área: " + number(selection.excludedBbox) + " · Período: " + number(excludedPeriod) + (state.current.sample_scope === "pilot_bbox" ? " · SHA-256 del CSV original de la fuente: " : " · SHA-256 del archivo cargado: ") + (state.current.sha256 || "no disponible");
  $("file-summary").hidden = false;
  if (historical) {
    renderCalendar(state.monthly);
    message("CUT " + state.current.commune.cut + " · " + state.current.commune.name + " · Geografía fija DPA 2023, por centro de celda. Datos diurnos filtrados por confianza y Type=0; sin máscara adicional ni armonización. El registro " + state.current.platform + " se mantiene separado." + (state.current.versions.length > 1 ? " El archivo contiene distintas versiones de procesamiento (" + state.current.versions.join(", ") + "); sus cambios aún no se han evaluado." : ""));
  } else {
    $("calendar-wrap").hidden = true;
    const scope = state.current.sample_scope === "pilot_bbox" ? "Muestra ya recortada al rectángulo piloto. " : "";
    message(scope + (summary.count ? "Consulta de observaciones lista; sin asignación comunal ni armonización." : "Sin detecciones seleccionadas; no demuestra ausencia de actividad.") + (state.current.truncated ? " Archivo publicado truncado." : ""));
  }
  state.query = {
    schema_version: 2, created_at: new Date().toISOString(), source: {
      name: state.current.name, url: state.current.url || null, sha256: state.current.sha256 || null,
      hash_scope: historical ? "derived-communal-csv" : state.current.sample_scope === "pilot_bbox" ? "full-original-provider-csv" : "uploaded-file",
      retrieved_at: state.current.retrieved_at || null, processing_status: state.current.processing_status || "unverified",
      product: state.current.product || "unverified", sample_scope: state.current.sample_scope || "uploaded-file",
      truncated: Boolean(state.current.truncated), source_rows: state.current.source_rows ?? rawCount,
      published_rows: state.current.published_rows ?? rawCount,
      ...(historical ? { source_files: state.current.files, available_years: state.current.available_years, missing_years: state.current.missing_years, versions: state.current.versions } : {})
    },
    scope: historical ? { kind: "commune-fixed-DPA-2023", cut: state.current.commune.cut, name: state.current.commune.name, region_cut: state.current.commune.region_cut, assignment: "0.01-degree-cell-centre" } : filters.bbox ? { kind: "preliminary-bbox-not-commune", bounds: filters.bbox } : { kind: "loaded-file-only" },
    filters: { daynight: filters.dayOnly ? "D" : "all", modis_min_confidence: 30, viirs_confidence: ["n", "h", "nominal", "high"], requested_months: { start: start || null, end: end || null }, type: historical ? ["0"] : "not-filtered", additional_static_mask: "not-applied" },
    grid: { degrees: 0.01, longitude_origin: -180, latitude_origin: -90, time_basis: "UTC", counting: "per-platform-cell-day" },
    counts: { input: rawCount, invalid: state.normalized.rejected.length, duplicates: state.normalized.duplicates, selected: summary.count, excluded_daynight: selection.excludedNightOrUnknown, excluded_confidence: selection.excludedConfidence, excluded_bbox: selection.excludedBbox, excluded_period: excludedPeriod },
    selected_period: { start: summary.dateMin, end: summary.dateMax }, monthly: state.monthly,
    administrative_assignment: historical ? { ...state.history.geography, rule: "cell-centre", historical_boundaries: false } : "not-performed",
    harmonization: "not-started", observation_coverage: "unknown",
    acknowledgement: "NASA FIRMS: https://firms.modaps.eosdis.nasa.gov/; DPA: SUBDERE / IDE Chile"
  };
  ["export-csv", "export-monthly", "export-manifest"].forEach(id => { $(id).disabled = false; });
}
function configureMode(historical) {
  $("commune-controls").hidden = !historical;
  $("scope-controls").hidden = historical;
  $("day-only").disabled = historical;
  if (historical) $("day-only").checked = true;
  $("filter-description").textContent = historical ? "Archivo preparado: Aqua o plataforma VIIRS seleccionada; solo día, confianza MODIS ≥ 30 / VIIRS nominal-alta, Type=0 (vegetación presumida). No hay máscara adicional." : "Confianza: MODIS ≥ 30; VIIRS nominal/alta. Sin filtro Type ni asignación comunal para archivos locales o muestras NRT.";
}
function loadRows(rows, headers, metadata, resetDates = true) {
  state.headers = headers;
  state.normalized = normalizeRows(rows);
  state.current = metadata;
  if (resetDates) {
    const dates = state.normalized.valid.map(row => row.acq_date).sort();
    $("start-month").value = metadata.start || dates[0]?.slice(0, 7) || "";
    $("end-month").value = metadata.end || dates.at(-1)?.slice(0, 7) || "";
  }
  $("start-month").min = metadata.start || ""; $("end-month").min = metadata.start || "";
  $("start-month").max = metadata.end || ""; $("end-month").max = metadata.end || "";
  renderQuery();
}
async function loadSource(resetDates = true) {
  const token = ++state.busy;
  $("file-input").value = "";
  const source = state.sources.find(item => item.id === $("source-select").value);
  if (!source) { configureMode(false); return clearResults("Selecciona una fuente o carga un CSV FIRMS."); }
  const historical = source.kind === "historical-observed";
  configureMode(historical);
  if (!historical) return loadRows(source.rows || [], source.columns || [], { ...source, name: source.id + ".csv" });
  if (resetDates) { $("start-month").value = source.start; $("end-month").value = source.end; }
  const commune = state.history.communes.find(item => item.cut === $("commune-select").value);
  const segment = source.communes.find(item => item.cut === commune?.cut);
  if (!commune || !segment) return clearResults("La comuna no tiene un archivo preparado para esa fuente.", true);
  clearResults("Comprobando el archivo comunal y su hash…");
  try {
    const response = await fetch("./" + segment.url);
    if (!response.ok) throw new Error("No se pudo leer el archivo comunal.");
    const buffer = await response.arrayBuffer();
    if (buffer.byteLength > 15 * 1024 * 1024) throw new Error("Archivo comunal excede el límite de esta versión.");
    const actualHash = await hash(buffer);
    if (actualHash !== segment.sha256) throw new Error("El hash del archivo comunal no coincide con su inventario.");
    const parsed = parseCSV(new TextDecoder("utf-8", { fatal: true }).decode(buffer));
    if (parsed.rows.length !== segment.rows || parsed.rows.some(row => row.cut_com !== commune.cut || row.type !== "0" || row.daynight !== "D")) throw new Error("El contenido no coincide con la comuna o los filtros del inventario.");
    if (token !== state.busy) return;
    loadRows(parsed.rows, parsed.headers, { ...source, name: source.id + "-" + commune.cut + ".csv", commune,
      sha256: actualHash, url: segment.url, processing_status: "annual-country-archive-see-versions",
      product: source.title, sample_scope: "complete-prepared-commune-for-source",
      retrieved_at: state.history.created_at, source_rows: segment.rows, published_rows: segment.rows }, resetDates);
  } catch (error) {
    if (token === state.busy) clearResults(error.message, true);
  }
}
function renderSources(snapshot) {
  const historical = state.history?.sources || [];
  state.sources = [...historical, ...(snapshot.sources || [])];
  $("source-list").replaceChildren();
  $("source-select").replaceChildren(element("option", "Selecciona una fuente disponible"));
  $("source-select").firstChild.value = "";
  if (!state.sources.length) {
    const card = element("article", undefined, "source-card");
    card.append(element("h3", "Todavía no hay datos"), element("p", "Carga un CSV FIRMS o ejecuta las descargas reproducibles."));
    $("source-list").append(card);
  }
  for (const source of state.sources) {
    const historic = source.kind === "historical-observed";
    const available = historic ? source.status === "prepared" : source.status === "downloaded";
    const card = element("article", undefined, "source-card");
    card.append(element("div", available ? (historic ? "ARCHIVO ANUAL · GEOGRAFÍA DPA 2023" : "MUESTRA RECIENTE · NRT") : "NO DISPONIBLE", "status" + (available ? "" : " unavailable")));
    card.append(element("h3", source.title || source.product || source.id));
    if (available) {
      if (historic) {
        card.append(element("p", source.start + " → " + source.end + " · " + source.available_years.length + " archivos anuales."));
        card.append(element("p", number(source.rows) + " detecciones seleccionadas en 54 comunas · Type=0, día y confianza."));
        card.append(element("p", source.missing_years.length ? "Años ausentes: " + source.missing_years.join(", ") : "Todos los archivos anuales previstos están descargados; cobertura observacional desconocida."));
        card.append(element("p", "Versiones del campo FIRMS: " + source.versions.join(", ") + (source.versions.length > 1 ? ". Cambios pendientes de evaluar." : ".")));
      } else {
        card.append(element("p", number(source.source_rows) + " filas originales · " + number(source.pilot_rows) + " en el rectángulo preliminar."));
        card.append(element("p", "Adquisición: " + (source.acquisition_min || "sin dato") + " → " + (source.acquisition_max || "sin dato") + ". Separada de los históricos."));
      }
      const option = element("option", historic ? source.title : source.product + " · muestra NRT");
      option.value = source.id; $("source-select").append(option);
    } else card.append(element("p", source.error || "No se pudo obtener un archivo válido."));
    const link = element("a", historic ? "Catálogo original ↗" : "Fuente original ↗");
    link.href = historic ? "https://firms.modaps.eosdis.nasa.gov/data/country/yearly_summary_files.txt" : source.url;
    link.target = "_blank"; link.rel = "noopener noreferrer"; card.append(link);
    $("source-list").append(card);
  }
  $("snapshot-date").textContent = state.history ? "Históricos preparados: " + new Date(state.history.created_at).toLocaleString("es-CL", { timeZone: "America/Santiago" }) + " · Chile" : snapshot.created_at ? "Muestra: " + new Date(snapshot.created_at).toLocaleString("es-CL", { timeZone: "America/Santiago" }) : "Sin archivos descargados";
  if (state.history) {
    const regions = [...new Set(state.history.communes.map(item => item.region_cut))].sort();
    $("commune-select").replaceChildren();
    for (const region of regions) {
      const group = document.createElement("optgroup");
      group.label = region === "08" ? "Biobío" : "Ñuble";
      for (const commune of state.history.communes.filter(item => item.region_cut === region).sort((a, b) => a.name.localeCompare(b.name, "es"))) {
        const option = element("option", commune.name + " · " + commune.cut);
        option.value = commune.cut; group.append(option);
      }
      $("commune-select").append(group);
    }
    $("commune-select").value = state.history.communes.some(item => item.cut === "08109") ? "08109" : state.history.communes[0].cut;
    $("geography-summary").textContent = "54 comunas: 33 de Biobío y 21 de Ñuble. Geografía fija DPA 2023 aplicada a todos los años; asignación única por centro de celda de 0,01°. Las muestras NRT rectangulares siguen separadas. No se publican aún series armonizadas.";
  }
}
$("source-select").addEventListener("change", () => { void loadSource(true); });
$("commune-select").addEventListener("change", () => { void loadSource(false); });
$("file-input").addEventListener("change", async event => {
  const file = event.target.files[0];
  if (!file) return;
  const request = ++state.busy;
  configureMode(false); clearResults("Validando el archivo local…");
  try {
    if (file.size > 15 * 1024 * 1024) throw new Error("El archivo supera 15 MB. Prepara un recorte para esta versión.");
    const buffer = await file.arrayBuffer();
    const parsed = parseCSV(new TextDecoder("utf-8", { fatal: true }).decode(buffer));
    const sha256 = await hash(buffer);
    if (request !== state.busy) return;
    $("source-select").value = "";
    loadRows(parsed.rows, parsed.headers, { name: file.name, sha256, processing_status: "unverified", sample_scope: "uploaded-file" });
  } catch (error) {
    if (request === state.busy) clearResults(error.message, true);
  }
});
$("day-only").addEventListener("change", renderQuery);
$("start-month").addEventListener("change", renderQuery);
$("end-month").addEventListener("change", renderQuery);
$("scope-select").addEventListener("change", () => {
  $("scope-description").textContent = $("scope-select").value === "pilot" ? "−73,9 a −71,0° lon · −38,9 a −35,8° lat. No es un límite administrativo." : "Solo las filas presentes en el archivo cargado; una muestra recortada sigue siendo un recorte.";
  renderQuery();
});
$("export-csv").addEventListener("click", () => {
  if (state.query) download("firechronos-observado-" + (state.current.commune?.cut || "consulta") + ".csv", csvText(state.selected, state.headers), "text/csv;charset=utf-8");
});
$("export-monthly").addEventListener("click", () => {
  if (!state.query) return;
  const rows = state.monthly.map(row => ({ month: row.month, instrument: row.instrument, platform: row.platform, cut_com: state.current.commune?.cut || "", detections: row.detections, cell_days: row.cellDays, status: row.status || "observed-detections", observation_coverage: "unknown" }));
  download("firechronos-mensual-" + (state.current.commune?.cut || "consulta") + ".csv", csvText(rows, ["month", "instrument", "platform", "cut_com", "detections", "cell_days", "status", "observation_coverage"]), "text/csv;charset=utf-8");
});
$("export-manifest").addEventListener("click", () => {
  if (state.query) download("firechronos-consulta.json", JSON.stringify(state.query, null, 2) + "\n", "application/json");
});
async function readJSON(url) {
  const response = await fetch(url, { cache: "no-store" });
  if (!response.ok) throw new Error("No se pudo leer " + url);
  return response.json();
}
const results = await Promise.allSettled([readJSON("./data/snapshot.json"), readJSON("./data/history-manifest.json")]);
const snapshot = results[0].status === "fulfilled" ? results[0].value : { sources: [] };
state.history = results[1].status === "fulfilled" ? results[1].value : null;
renderSources(snapshot);
if (state.history?.sources.length) {
  $("source-select").value = state.history.sources[0].id;
  await loadSource(true);
} else {
  configureMode(false);
  clearResults("Selecciona una muestra o carga un CSV FIRMS. Los históricos comunales no están disponibles en esta versión.");
}
