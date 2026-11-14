export function parseCSV(text) {
  const input = String(text).replace(/^\uFEFF/, "");
  const rows = [];
  let row = [], field = "", quoted = false, afterQuote = false;
  for (let i = 0; i < input.length; i++) {
    const c = input[i];
    if (quoted) {
      if (c === '"' && input[i + 1] === '"') { field += '"'; i++; }
      else if (c === '"') { quoted = false; afterQuote = true; }
      else field += c;
    } else if (afterQuote) {
      if (c === ",") { row.push(field); field = ""; afterQuote = false; }
      else if (c === "\n" || c === "\r") {
        row.push(field); rows.push(row); row = []; field = ""; afterQuote = false;
        if (c === "\r" && input[i + 1] === "\n") i++;
      } else if (c !== " " && c !== "\t") throw new Error("CSV inválido después de una comilla de cierre.");
    } else if (c === '"') {
      if (field.length) throw new Error("Comilla inesperada dentro de un campo.");
      quoted = true;
    } else if (c === ",") { row.push(field); field = ""; }
    else if (c === "\n" || c === "\r") {
      row.push(field);
      if (row.some(value => value.trim() !== "")) rows.push(row);
      row = []; field = "";
      if (c === "\r" && input[i + 1] === "\n") i++;
    } else field += c;
  }
  if (quoted) throw new Error("CSV con comillas sin cerrar.");
  if (field.length || row.length || afterQuote) { row.push(field); if (row.some(value => value.trim() !== "")) rows.push(row); }
  if (!rows.length) throw new Error("El archivo está vacío.");
  const headers = rows.shift().map(value => value.trim().toLowerCase());
  if (new Set(headers).size !== headers.length || headers.some(value => !value)) throw new Error("Encabezados vacíos o duplicados.");
  for (const name of ["latitude", "longitude", "acq_date"]) {
    if (!headers.includes(name)) throw new Error("Falta la columna FIRMS obligatoria: " + name);
  }
  const data = rows.map((values, index) => {
    if (values.length !== headers.length) throw new Error("La fila " + (index + 2) + " tiene " + values.length + " columnas; se esperaban " + headers.length + ".");
    return Object.fromEntries(headers.map((header, i) => [header, values[i].trim()]));
  });
  return { headers, rows: data };
}

export function validDate(value) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(value || "")) return false;
  const parsed = new Date(value + "T00:00:00Z");
  return Number.isFinite(parsed.getTime()) && parsed.toISOString().slice(0, 10) === value;
}
export function validTime(value) {
  if (value === undefined || value === "") return true;
  if (!/^\d{1,4}$/.test(String(value))) return false;
  const time = String(value).padStart(4, "0");
  return Number(time.slice(0, 2)) < 24 && Number(time.slice(2)) < 60;
}
export function instrumentOf(row) {
  const instrument = String(row.instrument || "").trim().toUpperCase();
  if (instrument === "MODIS" || instrument === "VIIRS") return instrument;
  if ("bright_ti4" in row) return "VIIRS";
  if ("bright_t31" in row || "brightness" in row) return "MODIS";
  return "DESCONOCIDO";
}
export function normalizeRows(rows) {
  const valid = [], rejected = [], seen = new Set();
  let duplicates = 0;
  for (const [i, row] of rows.entries()) {
    const latitude = String(row.latitude ?? "").trim() === "" ? NaN : Number(row.latitude);
    const longitude = String(row.longitude ?? "").trim() === "" ? NaN : Number(row.longitude);
    if (!Number.isFinite(latitude) || !Number.isFinite(longitude) || latitude < -90 || latitude > 90 || longitude < -180 || longitude > 180 || !validDate(row.acq_date) || !validTime(row.acq_time)) {
      rejected.push({ line: i + 2, reason: "Coordenada, fecha o hora inválida" });
      continue;
    }
    const key = [latitude, longitude, row.acq_date, String(row.acq_time || "").padStart(4, "0"), row.satellite || "", instrumentOf(row)].join("|");
    const duplicate = seen.has(key);
    if (duplicate) duplicates++;
    seen.add(key);
    valid.push({ ...row, latitude, longitude, _instrument: instrumentOf(row), _duplicate: duplicate });
  }
  return { valid, rejected, duplicates };
}
export function selectRows(rows, { dayOnly = true, bbox = null, minMODIS = 30 } = {}) {
  let excludedNightOrUnknown = 0, excludedConfidence = 0, excludedBbox = 0;
  const selected = rows.filter(row => {
    if (dayOnly && String(row.daynight || "").toUpperCase() !== "D") { excludedNightOrUnknown++; return false; }
    if (row._instrument === "MODIS") {
      const confidence = String(row.confidence ?? "").trim();
      if (!confidence || !Number.isFinite(Number(confidence)) || Number(confidence) < minMODIS || Number(confidence) > 100) { excludedConfidence++; return false; }
    } else if (row._instrument === "VIIRS") {
      const confidence = String(row.confidence ?? "").trim().toLowerCase();
      if (!["n", "h", "nominal", "high"].includes(confidence)) { excludedConfidence++; return false; }
    } else { excludedConfidence++; return false; }
    if (bbox && !(row.longitude >= bbox.west && row.longitude <= bbox.east && row.latitude >= bbox.south && row.latitude <= bbox.north)) { excludedBbox++; return false; }
    return true;
  });
  return { selected, excludedNightOrUnknown, excludedConfidence, excludedBbox };
}
export function summarize(rows) {
  const dates = rows.map(row => row.acq_date).sort();
  const perPlatform = new Map();
  const cell = value => Math.floor(Math.round((value + 180) * 1e9) / 1e7);
  for (const row of rows) {
    const platform = row.satellite || "sin_plataforma";
    const key = row._instrument + "|" + platform + "|" + row.acq_date.slice(0, 7);
    if (!perPlatform.has(key)) perPlatform.set(key, { instrument: row._instrument, platform, month: row.acq_date.slice(0, 7), detections: 0, cells: new Set() });
    const group = perPlatform.get(key);
    group.detections++;
    const cellKey = row.acq_date + "|" + Math.floor(Math.round((row.latitude + 90) * 1e9) / 1e7) + "|" + cell(row.longitude);
    group.cells.add(cellKey);
  }
  return { count: rows.length, dateMin: dates[0] || null, dateMax: dates.at(-1) || null,
    monthly: Array.from(perPlatform.values()).map(group => ({ instrument: group.instrument, platform: group.platform, month: group.month, detections: group.detections, cellDays: group.cells.size })).sort((a, b) => a.month.localeCompare(b.month) || a.platform.localeCompare(b.platform)) };
}

export function observedMonths(monthly, { start, end, availableYears, instrument, platform }) {
  if (!/^\d{4}-(0[1-9]|1[0-2])$/.test(start || "") || !/^\d{4}-(0[1-9]|1[0-2])$/.test(end || "") || start > end) {
    throw new Error("Rango mensual inválido.");
  }
  const counts = new Map();
  for (const row of monthly) {
    if (counts.has(row.month)) throw new Error("Más de una plataforma en una serie comunal de referencia.");
    counts.set(row.month, row);
  }
  const years = new Set(availableYears);
  const rows = [];
  let [year, month] = start.split("-").map(Number);
  const [lastYear, lastMonth] = end.split("-").map(Number);
  if ((lastYear - year) * 12 + lastMonth - month > 1200) throw new Error("Rango de más de cien años no soportado.");
  while (year < lastYear || (year === lastYear && month <= lastMonth)) {
    const label = String(year).padStart(4, "0") + "-" + String(month).padStart(2, "0");
    const present = years.has(year);
    const value = counts.get(label);
    rows.push({ month: label, instrument, platform,
      detections: present ? value?.detections || 0 : null,
      cellDays: present ? value?.cellDays || 0 : null,
      status: present ? (value ? "observed-detections" : "no-detections-coverage-unknown") : "missing-file",
      observationCoverage: "unknown" });
    month++;
    if (month > 12) { year++; month = 1; }
  }
  return rows;
}
export function csvText(rows, headers) {
  const escape = value => '"' + String(value ?? "").replaceAll('"', '""') + '"';
  return headers.map(escape).join(",") + "\r\n" + rows.map(row => headers.map(header => escape(row[header])).join(",")).join("\r\n") + (rows.length ? "\r\n" : "");
}
