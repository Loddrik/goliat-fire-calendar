// Textos y reglas de presentación de la vista "mapa primero". Ningún número se calcula aquí:
// solo se eligen, ordenan y formatean valores publicados en /data (publish.py y publish_web.py).
import type { Lang } from "./i18n";
import type { MonthClimatology } from "./types";
import { seasonLabel } from "./types";
const prevSeasons = (n: number) => `2012-13 a ${seasonLabel(2011 + n)}`;
const prevSeasonsEn = (n: number) => `2012-13 to ${seasonLabel(2011 + n)}`;

// Sin WebGL el mapa no se muestra; la ficha, la tabla y las descargas siguen.
export const MAP_UNAVAILABLE = {
  es: "El mapa no se puede mostrar en este navegador (le falta aceleración gráfica). La ficha de la comuna, la tabla y las descargas funcionan igual.",
  en: "The map cannot be shown in this browser (graphics acceleration is missing). The commune card, table and downloads still work.",
};

// Una sola rampa en toda la página (brief §11): 5 azules, tramos fijos iguales en las 54 comunas.
export const BLUES = ["#C6DBEF", "#9ECAE1", "#6BAED6", "#3182BD", "#08519C"];
// Calendario: celdas-día por mes.
export const MONTH_BREAKS = [1, 6, 21, 51, 101]; // 1–5 · 6–20 · 21–50 · 51–100 · más de 100
export const MONTH_LABELS = ["1–5", "6–20", "21–50", "51–100"];
// Mapa: temporadas con detección (Todas) o días con detección en una temporada.
export const MAP_BREAKS = [1, 2, 3, 5, 8]; // 1 · 2 · 3–4 · 5–7 · 8 o más
export const MAP_LABELS = ["1", "2", "3–4", "5–7"];

export function tramo(v: number, breaks: number[]): number {
  let i = -1;
  for (let k = 0; k < breaks.length; k++) if (v >= breaks[k]) i = k;
  return i; // -1 = cero
}

const MONTHS = {
  es: ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"],
  en: ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
};
export const monthName = (m: number, lang: Lang) => MONTHS[lang][m - 1];
export const monthShort = (m: number, lang: Lang) => MONTHS[lang][m - 1].slice(0, 3);

/** "2026-11-13" → "13-11-2026" */
export const dmy = (iso: string) => iso.split("-").reverse().join("-");
/** "2026-11-13" → "13 de noviembre de 2026" / "13 November 2026" */
export function longDate(iso: string, lang: Lang) {
  const [y, m, d] = iso.split("-").map(Number);
  return lang === "es" ? `${d} de ${monthName(m, lang)} de ${y}` : `${d} ${monthName(m, lang)} ${y}`;
}
export const num = (v: number | null | undefined, lang: Lang) =>
  v == null ? "—" : v.toLocaleString(lang === "es" ? "es-CL" : "en-US", { maximumFractionDigits: 1 });
export const join = (xs: string[], lang: Lang) =>
  xs.length <= 1 ? xs.join("") : `${xs.slice(0, -1).join(", ")} ${lang === "es" ? "y" : "and"} ${xs[xs.length - 1]}`;

/** Qué meses nombrar. Si hay un mes típico con actividad (mediana ≥ 5), los dos de mayor mediana.
 *  Si no (comunas con pocas temporadas grandes, como Hualqui), los dos de mayor máximo y el que más temporadas tuvo. */
export type ActivityMonths = { mode: "typical"; months: number[]; peak: number | null } | { mode: "rare"; big: number[]; frequent: number } | { mode: "none" };
const seasonOrder = (m: number) => (m + 5) % 12; // jul=0 … jun=11
export function activityMonths(clim: MonthClimatology[]): ActivityMonths {
  const byMedian = [...clim].sort((a, b) => (b.median ?? 0) - (a.median ?? 0));
  const byMax = [...clim].sort((a, b) => (b.max ?? 0) - (a.max ?? 0));
  if ((byMedian[0]?.median ?? 0) >= 5) {
    const months = byMedian.slice(0, 2).map((c) => c.m).sort((a, b) => seasonOrder(a) - seasonOrder(b));
    // Si la temporada más grande cayó en otro mes (p. ej. el febrero de 2023 en Santa Juana), se nombra también.
    const peak = byMax[0] && !months.includes(byMax[0].m) ? byMax[0].m : null;
    return { mode: "typical", months, peak };
  }
  if ((byMax[0]?.max ?? 0) === 0) return { mode: "none" };
  const big = byMax.slice(0, 2).filter((c) => (c.max ?? 0) > 0).map((c) => c.m).sort((a, b) => seasonOrder(a) - seasonOrder(b));
  const frequent = [...clim].sort((a, b) => b.seasons_with - a.seasons_with)[0].m;
  return { mode: "rare", big, frequent };
}

/** Categoría de la temporada en curso. Apagada hasta que el issue #4 (estabilidad de categorías, ciencia) la apruebe:
 *  el manifiesto exige ≥ 80 % de réplicas estables antes de mostrar una etiqueta. Con p75 < 10 nunca hay categoría. */
export const SHOW_CATEGORY = false;
export type Category = "below" | "similar" | "above" | "too_few";
export function category(current: number, p25: number | null, p75: number | null): Category {
  if (p25 == null || p75 == null || p75 < 10) return "too_few";
  return current < p25 ? "below" : current > p75 ? "above" : "similar";
}

export const UI = {
  es: {
    headline: "Actividad de fuego detectada por satélite",
    line: "Lo que los satélites de la NASA han visto desde 2012 en Biobío y Ñuble, mes a mes y sector por sector.",
    alert: "No es una alerta. Si ves fuego, llama al 130 (CONAF) o al 132 (Bomberos). Sigue los avisos de SENAPRED.",
    mapNotice: "Cada cuadro es un sector de ~1 km con calor detectado. No es un predio, una empresa ni un incendio, ni dice quién lo provocó.",
    search: "Buscar tu comuna…",
    searchHint: "Toca una comuna en el mapa o búscala por su nombre.",
    all: "Todas",
    labelAll: (n: number, cutoff: string) => `Temporadas con detección por sector, 2012-13 a 2026-27 (hasta el ${cutoff}). De ${n} temporadas. Antes de 2012 solo está en la serie.`,
    labelSeason: (s: string, y: number) => `Días con detección por sector, temporada ${s} (julio ${y} a junio ${y + 1}).`,
    labelCurrent: (s: string, cutoff: string) => `Días con detección por sector, temporada ${s}, hasta el ${cutoff} · cifra preliminar.`,
    legendAll: (n: number) => `temporadas con detección (de ${n}, la última en curso)`,
    legendSeason: (s: string) => `días con detección en ${s}`,
    none: "sin detecciones",
    more: "o más",
    popupAll: (n: number, total: number, d: number) => `Con detección en ${n} de ${total} temporadas · ${d} días en total`,
    popupSeason: (s: string, d: number, n: number, total: number) => [`${s}: ${d} ${d === 1 ? "día" : "días"} con detección`, `con detección en ${n} de ${total} temporadas`],
    sector: "Sector de ~1 km",
    seasonGroup: "Por temporada",
    monthGroup: "Por mes, sumando los años",
    // Prueba de usuario #47: años de calendario en vez de «temporadas completas», y que es pasado, no lo que viene.
    labelMonth: (m: string, n: number, from: number, to: number) => `Sectores con detección en ${m}, de ${from} a ${to} (${n} años). Es lo que se vio antes, no lo que va a pasar. No incluye la temporada en curso.`,
    legendMonth: (m: string, n: number) => `en cuántos de los ${n} años hubo detección en ${m}`,
    popupMonth: (m: string, n: number, total: number, d: number) => `${m[0].toUpperCase()}${m.slice(1)}: con detección en ${n} de ${total} temporadas · ${d} ${d === 1 ? "día" : "días en total"}`,
    // Revisión científica #47: el color es recurrencia entre años, no magnitud, y «5 de 14» describe el pasado, no una probabilidad.
    monthNote: "Cuenta en cuántos años hubo detección en este mes, no cuánto: un mes extremo de un solo año, como febrero de 2023, se ve claro. Muestra lo detectado en años pasados; no indica dónde habrá fuego. Lo que se repite cada año puede ser una quema agrícola o forestal autorizada.",
    monthLoading: "Cargando los meses…",
    basemap: "Mapa base: OpenFreeMap (OpenStreetMap)",
    serieOn: "Serie 2002–2026: observada desde 2012, aproximada antes",
    serieOff: "Serie observada 2012–2026; antes de 2012 sin estimación",
    unit: "Una celda-día = un cuadrado de ~1 km donde el satélite vio calor un día.",
    upTo: "Datos hasta el",
    phrase: (comuna: string, date: string, cur: number) => `Hasta el ${date}, ${comuna} lleva ${cur} ${cur === 1 ? "celda-día" : "celdas-día"} con detección esta temporada.`,
    range: (p25: string, p75: string, n: number) => `A esta misma fecha, en las ${n} temporadas anteriores (${prevSeasons(n)}), el rango habitual fue de ${p25} a ${p75}.`,
    cat: { below: "Es menos que lo habitual para esta fecha", similar: "Es parecido a lo habitual para esta fecha", above: "Es más que lo habitual para esta fecha" },
    catRange: (p25: string, p75: string, n: number) => `(rango habitual de ${p25} a ${p75} en las ${n} temporadas anteriores, ${prevSeasons(n)}).`,
    tooFew: (p25: string, p75: string) => `A esta fecha suele haber muy pocas detecciones aquí (rango habitual de ${p25} a ${p75}), así que todavía no se puede comparar.`,
    typical: (ms: string) => `No anticipa cómo seguirá: aquí la mayor actividad suele llegar en ${ms}.`,
    typicalPeak: (ms: string, peak: string) => `No anticipa cómo seguirá: aquí la mayor actividad suele llegar en ${ms}, pero el mes con más detecciones desde 2012 fue un ${peak}.`,
    rare: (big: string, freq: string) => `No anticipa cómo seguirá: los registros mensuales más altos desde 2012 se dieron en ${big}; en ${freq} es cuando más seguido aparece.`,
    noneMonths: "No anticipa cómo seguirá.",
    source: "Fuente: NASA FIRMS. Cifra preliminar: puede cambiar en los próximos meses.",
    seasonTotal: (s: string, y: number, v: string, comuna: string) => `Temporada ${s} (julio ${y} a junio ${y + 1}): ${v} celdas-día con detección en ${comuna}.`,
    totalsTitle: "Total por temporada",
    totalsCurrent: (cutoff: string) => `hasta el ${cutoff} · preliminar`,
    profileTitle: "¿En qué meses suele haber actividad?",
    howToRead: "¿Cómo se lee?",
    profileLegend: (n: number) => `Barra: lo habitual (mediana de ${n} temporadas completas, ${prevSeasons(n)}) · raya: el máximo de ese mes en cualquier temporada · abajo: en cuántas de las ${n} temporadas hubo detección ese mes`,
    profileNote: "El satélite ve calor: puede ser un incendio, una quema agrícola o una fuente falsa. No los distingue.",
    of: (n: number) => `de ${n}`,
    table: "Ver la serie 2002–2026 (tabla)",
    hideTable: "Ocultar la serie",
    tabSummary: "Resumen",
    tabSeries: "Serie 2002–2026",
    close: "Cerrar la comuna y volver a toda la región",
    closeShort: "Cerrar",
    printShort: "Imprimir",
    legendMore: "Qué significa cada celda",
    print: "Imprimir / guardar PDF",
    share: "Compartir",
    shareTitle: "Para compartir con tu junta o tu equipo, esto es lo que se enviará:",
    shareWhatsapp: "Compartir por WhatsApp",
    copy: "Copiar texto",
    copied: "Copiado. Pégalo en WhatsApp o en un correo.",
    csv: "CSV de la serie",
    csvDet: "CSV de detecciones",
    shareMsg: (comuna: string, months: string, big: string | null, cutoff: string, url: string) => `${comuna}: según los satélites de la NASA, lo habitual es que aparezca actividad de fuego en ${months}${big ? `; los registros mensuales más altos desde 2012 se dieron en ${big}` : ""}. Datos hasta el ${cutoff}. No es una alerta: si ves fuego, llama al 130 o al 132. ${url}`,
    shareMsgNone: (comuna: string, cutoff: string, url: string) => `${comuna}: actividad de fuego detectada por los satélites de la NASA, datos hasta el ${cutoff}. No es una alerta: si ves fuego, llama al 130 o al 132. ${url}`,
    planTitle: "Para el plan comunal",
    plan: (comuna: string, cutoff: string) => [
      "Copia el total de la temporada que necesitas y los meses donde se concentra la actividad.",
      `Cita así: GOLIAT, NASA FIRMS (MODIS/VIIRS), comuna de ${comuna}, datos hasta el ${cutoff}.`,
      "La serie completa 2002–2026, con sus estados, está en la tabla y en el CSV.",
    ],
    loading: "Cargando…",
    loadError: "No se pudieron cargar los datos de esta comuna. Elige otra comuna o recarga la página.",
    pickFirst: "Elige una comuna para ver su historial por plataforma.",
  },
  en: {
    headline: "Satellite-detected fire activity",
    line: "What NASA satellites have seen since 2012 in Biobío and Ñuble, Chile, month by month and sector by sector.",
    alert: "Not an alert. If you see fire in Chile, call 130 (CONAF) or 132 (Firefighters). Follow SENAPRED notices.",
    mapNotice: "Each square is a ~1 km sector with detected heat. It is not a property, a company or a fire, and it does not say who caused it.",
    search: "Search your commune…",
    searchHint: "Tap a commune on the map or search it by name.",
    all: "All",
    labelAll: (n: number, cutoff: string) => `Seasons with detection per sector, 2012-13 to 2026-27 (through ${cutoff}). Out of ${n} seasons. Before 2012, only in the series.`,
    labelSeason: (s: string, y: number) => `Days with detection per sector, season ${s} (July ${y} to June ${y + 1}).`,
    labelCurrent: (s: string, cutoff: string) => `Days with detection per sector, season ${s}, through ${cutoff} · preliminary.`,
    legendAll: (n: number) => `seasons with detection (of ${n}, the last one ongoing)`,
    legendSeason: (s: string) => `days with detection in ${s}`,
    none: "no detections",
    more: "or more",
    popupAll: (n: number, total: number, d: number) => `Detections in ${n} of ${total} seasons · ${d} days in total`,
    popupSeason: (s: string, d: number, n: number, total: number) => [`${s}: ${d} ${d === 1 ? "day" : "days"} with detection`, `detections in ${n} of ${total} seasons`],
    sector: "~1 km sector",
    seasonGroup: "By season",
    monthGroup: "By month, adding up the years",
    labelMonth: (m: string, n: number, from: number, to: number) => `Sectors with detection in ${m}, ${from} to ${to} (${n} years). It is what was seen before, not what will happen. The ongoing season is not included.`,
    legendMonth: (m: string, n: number) => `in how many of the ${n} years there was a detection in ${m}`,
    popupMonth: (m: string, n: number, total: number, d: number) => `${m}: detections in ${n} of ${total} seasons · ${d} ${d === 1 ? "day" : "days in total"}`,
    monthNote: "Counts in how many years there was a detection in this month, not how much: an extreme month in a single year, like February 2023, shows light. It shows past detections; it does not indicate where fire will occur. What repeats every year may be an authorized agricultural or forestry burn.",
    monthLoading: "Loading months…",
    basemap: "Basemap: OpenFreeMap (OpenStreetMap)",
    serieOn: "Series 2002–2026: observed since 2012, approximate before",
    serieOff: "Observed series 2012–2026; no estimate before 2012",
    unit: "One cell-day = a ~1 km square where the satellite saw heat on one day.",
    upTo: "Data through",
    phrase: (comuna: string, date: string, cur: number) => `As of ${date}, ${comuna} has ${cur} ${cur === 1 ? "cell-day" : "cell-days"} with detection this season.`,
    range: (p25: string, p75: string, n: number) => `By this same date, over the previous ${n} seasons (${prevSeasonsEn(n)}), the usual range was ${p25} to ${p75}.`,
    cat: { below: "That is less than usual for this date", similar: "That is about usual for this date", above: "That is more than usual for this date" },
    catRange: (p25: string, p75: string, n: number) => `(usual range ${p25} to ${p75} over the previous ${n} seasons, ${prevSeasonsEn(n)}).`,
    tooFew: (p25: string, p75: string) => `By this date there are usually very few detections here (usual range ${p25} to ${p75}), so it is too early to compare.`,
    typical: (ms: string) => `It does not anticipate what comes next: here most activity usually arrives in ${ms}.`,
    typicalPeak: (ms: string, peak: string) => `It does not anticipate what comes next: here most activity usually arrives in ${ms}, but the month with the most detections since 2012 was a ${peak}.`,
    rare: (big: string, freq: string) => `It does not anticipate what comes next: the highest monthly records since 2012 were in ${big}; ${freq} is when it shows up most often.`,
    noneMonths: "It does not anticipate what comes next.",
    source: "Source: NASA FIRMS. Preliminary figure: it may change in the coming months.",
    seasonTotal: (s: string, y: number, v: string, comuna: string) => `Season ${s} (July ${y} to June ${y + 1}): ${v} cell-days with detection in ${comuna}.`,
    totalsTitle: "Total per season",
    totalsCurrent: (cutoff: string) => `through ${cutoff} · preliminary`,
    profileTitle: "In which months is there usually activity?",
    howToRead: "How to read it",
    profileLegend: (n: number) => `Bar: the usual (median of ${n} complete seasons, ${prevSeasonsEn(n)}) · tick: the maximum for that month in any season · below: in how many of the ${n} seasons there was a detection that month`,
    profileNote: "The satellite sees heat: it may be a fire, an agricultural burn or a false source. It cannot tell them apart.",
    of: (n: number) => `of ${n}`,
    table: "See the 2002–2026 series (table)",
    hideTable: "Hide the series",
    tabSummary: "Summary",
    tabSeries: "2002–2026 series",
    close: "Close the commune and go back to the whole region",
    closeShort: "Close",
    printShort: "Print",
    legendMore: "What each cell means",
    print: "Print / save PDF",
    share: "Share",
    shareTitle: "To share with your neighbours or team, this is what will be sent:",
    shareWhatsapp: "Share on WhatsApp",
    copy: "Copy text",
    copied: "Copied. Paste it in WhatsApp or an email.",
    csv: "Series CSV",
    csvDet: "Detections CSV",
    shareMsg: (comuna: string, months: string, big: string | null, cutoff: string, url: string) => `${comuna}: according to NASA satellites, fire activity usually shows up in ${months}${big ? `; the highest monthly records since 2012 were in ${big}` : ""}. Data through ${cutoff}. Not an alert: if you see fire, call 130 or 132. ${url}`,
    shareMsgNone: (comuna: string, cutoff: string, url: string) => `${comuna}: fire activity detected by NASA satellites, data through ${cutoff}. Not an alert: if you see fire, call 130 or 132. ${url}`,
    planTitle: "For the communal plan",
    plan: (comuna: string, cutoff: string) => [
      "Copy the total of the season you need and the months where activity concentrates.",
      `Cite as: GOLIAT, NASA FIRMS (MODIS/VIIRS), commune of ${comuna}, data through ${cutoff}.`,
      "The full 2002–2026 series, with its states, is in the table and the CSV.",
    ],
    loading: "Loading…",
    loadError: "Could not load this commune. Pick another commune or reload the page.",
    pickFirst: "Pick a commune to see its platform history.",
  },
};
export type UIText = typeof UI.es;
