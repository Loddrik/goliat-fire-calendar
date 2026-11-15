// Textos de la landing. Los textos compartidos con la app (título, línea, aviso, estados) son los
// acordados con la sesión de rediseño el 14-11; si cambian allá, cambian acá.
// Lenguaje (CLAUDE.md regla 1): actividad de fuego detectada, detecciones, sectores, celdas-día.

import type { IconName } from "../brand/Icon";

export type Lang = "es" | "en";
type Use = { icon: IconName; t: string; d: string };

const MONTHS_ES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"];
const MONTHS_EN = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];

export function dateShort(iso: string, lang: Lang) {
  const [y, m, d] = iso.split("-");
  return lang === "es" ? `${d}-${m}-${y}` : `${MONTHS_EN[+m - 1].slice(0, 3)} ${+d}, ${y}`;
}
export function dateLong(iso: string, lang: Lang) {
  const [y, m, d] = iso.split("-").map(Number);
  return lang === "es" ? `${d} de ${MONTHS_ES[m - 1]} de ${y}` : `${MONTHS_EN[m - 1]} ${d}, ${y}`;
}
export const seasonLabel = (s: number) => `${s}-${String(s + 1).slice(2)}`;
const joinEs = (xs: string[]) => (xs.length < 2 ? xs.join("") : `${xs.slice(0, -1).join(", ")} y ${xs[xs.length - 1]}`);
const joinEn = (xs: string[]) => (xs.length < 2 ? xs.join("") : xs.length === 2 ? `${xs[0]} and ${xs[1]}` : `${xs.slice(0, -1).join(", ")} and ${xs[xs.length - 1]}`);
const cap = (s: string) => s.charAt(0).toUpperCase() + s.slice(1);

const es = {
  htmlTitle: "GOLIAT · Actividad de fuego detectada por satélite",
  navExplore: "Explorar comunas",
  navExploreShort: "Explorar",
  navHow: "Cómo leer los datos",
  navChallenge: "The challenge",
  langButton: "EN",
  langLabel: "EN · Read in English",
  // Título animado (issue #37): primero la pregunta; después la frase fija con la palabra que cambia.
  // Con «reducir movimiento» queda solo la pregunta. El lector de pantalla lee hFull una vez.
  hQuestion: "¿En qué meses se detecta fuego en tu comuna?",


  sub: (k: number, n: number) => `Detecciones de fuego de NASA FIRMS en las ${n} comunas de Biobío y Ñuble, mes a mes: VIIRS desde 2012 en todas y, en las ${k} donde la corrección pasa las pruebas, MODIS Aqua para 2002–2012, armonizados en una sola serie.`,
  eyebrow: (k: number, n: number) => `NASA FIRMS · VIIRS 2012–2026 · MODIS armonizado desde 2002 en ${k} de ${n} comunas`,
  alert: "No es una alerta. Si ves fuego, llama al 130 (CONAF) o al 132 (Bomberos) y sigue los avisos de SENAPRED.",
  searchLabel: "Busca tu comuna",
  searchPlaceholder: "Escribe el nombre de tu comuna…",
  dataFrom: (y: number) => `datos desde ${y}`,
  noResults: "No hay una comuna con ese nombre en Biobío o Ñuble.",
  meta: (n: number, cutoff: string) => `${n} comunas · datos hasta el ${cutoff}`,
  allLink: (n: number) => `Ver las ${n}`,
  // Mapa animado del hero (#40): el año de julio a junio, sumando solo temporadas completas.
  mapKicker: (a: string, b: string) => `Todas las temporadas, de ${a} a ${b}, mes a mes`,
  mapCount: (n: string, m: string, k: number) => `${n} sectores con detección en algún ${m} (${k} temporadas)`,
  mapNote: (a: string, b: string) => `Observado por VIIRS, de día (S-NPP hasta 2017-18, NOAA-20 desde 2018-19). Cada punto es un sector de ~1 km donde el satélite detectó calor ese mes en al menos una temporada completa (${a} a ${b}), sin fuentes fijas. Más sectores no es más fuego ni fuego más grande: lo que se repite cada año, como las quemas agrícolas, enciende más sectores que un evento grande y único como febrero de 2023, el mes con más celdas-día de la serie. Con nubes el satélite ve menos. No es un predio ni dice quién lo provocó.`,
  mapScope: (k: number, n: number) => `El mapa es solo VIIRS (2012→). La serie armonizada desde 2002 está en cada comuna: ${k} de ${n} pasan la prueba.`,
  mapAria: (a: string, b: string, peak: string) => `Mapa animado de Biobío y Ñuble que recorre el año de julio a junio: en cada mes se encienden los sectores donde el satélite VIIRS detectó calor ese mes, en las temporadas ${a} a ${b}. El mes con más sectores es ${peak}; febrero de 2023 es el mes con más celdas-día de la serie.`,
  mapPause: "Pausar la animación del mapa",
  mapPlay: "Reproducir la animación del mapa",
  legend: "temporadas con detección ese mes",
  legendClasses: ["1", "2", "3–4", "5 o más"],
  mapLoading: "Cargando el mapa…",
  mapError: "No se pudo cargar el mapa. Busca tu comuna arriba.",
  open: (c: string) => `Abrir ${c}`,

  qTitle: "Lo que puedes saber de tu comuna",
  qIntro: "Un ejemplo con datos reales.",
  pickLabel: "Comuna",
  unit: "Una celda-día es un cuadrado de ~1 km donde el satélite vio calor un día: no es un incendio ni una hectárea.",
  q1: "¿En qué meses se detecta?",
  monthsShort: ["Jul", "Ago", "Sep", "Oct", "Nov", "Dic", "Ene", "Feb", "Mar", "Abr", "May", "Jun"],
  monthsLong: ["julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre", "enero", "febrero", "marzo", "abril", "mayo", "junio"],
  monthAria: (m: string, med: string, k: number, n: number) => `${m}: mediana de ${med} celdas-día, detección en ${k} de ${n} temporadas`,
  factFocus: (c: string, ms: string[]) => `En ${c}, ${ms.length > 1 ? "los meses con la mediana más alta son" : "el mes con la mediana más alta es"} ${joinEs(ms)}.`,
  factSpread: (c: string, ms: string[]) => `En ${c}, varios meses tienen medianas parecidas: ${joinEs(ms)}.`,
  factLow: (c: string, low: string) => `En ${c}, en ningún mes la mediana llega a ${low} celdas-día: hay detecciones, pero no se repiten en un mes fijo.`,
  factPeak: (m: string, v: string) => `El valor más alto de un solo mes fue en ${m}: ${v} celdas-día en una temporada. Un año extremo no mueve la mediana.`,
  monthLine: (m: string, med: string, k: number, n: number) => `${cap(m)}: mediana de ${med} celdas-día; hubo detección en ${k} de ${n} temporadas.`,
  stripNote: (n: number, a: string, b: string) => `Observado (VIIRS, de día). Más oscuro, más celdas-día: mediana de las ${n} temporadas, ${a} a ${b}. El tono es relativo al mes más alto de esta comuna y no sirve para comparar comunas. Toca un mes para ver su número. Incluye quemas agrícolas: una detección no es un incendio.`,
  dotsKey: (a: string, b: string) => `una temporada (${a} a ${b}) al mismo día`,
  dotsCur: (s: string) => `${s}, en curso (provisional)`,
  q2: "¿Cómo va esta temporada?",
  q2sentence: (c: string, _s: string, cut: string, cur: string, n: number, a: string, b: string, med: string | null) =>
    `Hasta el ${cut} van ${cur} celdas-día en ${c} (provisional). A la misma fecha, en las ${n} temporadas anteriores (${a} a ${b}), la mediana fue ${med ?? "—"}.`,
  q2note: (n: number) => `Es lo que ya pasó: no anticipa cómo seguirá. Con ${n} temporadas, compara con cuidado; las cifras recientes son preliminares.`,
  loading: "Cargando…",

  seasonsTitle: "Temporada por temporada, desde 2012",
  seasonsKey: ["Aproximado: desde MODIS Aqua", "Observado: VIIRS", "Sin estimación"],
  seasonsNoteOn: "Celdas-día por temporada (julio a junio), observado por VIIRS; solo temporadas completas. En esta comuna la corrección desde MODIS pasó las pruebas: en Explorar está la serie desde 2002, mes a mes y con su error típico.",
  seasonsNoteOff: "Celdas-día por temporada (julio a junio), observado por VIIRS; solo temporadas completas. Antes de 2012 no damos cifra en esta comuna: la corrección desde MODIS no pasó las pruebas. No significa que no hubo fuego.",
  seasonsAria: (c: string, a: string, b: string) => `Celdas-día por temporada en ${c}, de ${a} a ${b}`,
  seasonAria: (s: string, state: string, v: string | null) => `${s}: ${state}${v == null ? "" : `, ${v} celdas-día`}`,
  usesTitle: "Para qué sirve",
  usesCta: "Elige tu comuna en Explorar",
  uses: [
    { icon: "municipio", t: "Tu plan comunal", d: "Elige tu comuna e imprime una hoja A4 o descarga el CSV, con fuente y fecha de corte." },
    { icon: "vecinos", t: "Preparar tu sector", d: "Mira qué meses y sectores se repiten, y llévalo a tu junta o al municipio." },
    { icon: "prensa", t: "Contrastar una cifra", d: "Compara temporadas al mismo día y descarga las detecciones." },
  ] as Use[],

  statesTitle: "Cómo leer los datos",
  statesIntro: "Cada mes dice de dónde viene su número:",
  states: [
    ["Observado", "lo vio el satélite VIIRS, desde 2012"],
    ["Aproximado", "estimado desde el satélite Aqua (2002–2012), con su error típico (±)"],
    ["Sin estimación", "antes de 2012 no damos cifra en esta comuna, porque la corrección no pasó las pruebas; no significa que no hubo fuego"],
    ["Puede cambiar", "cifra preliminar; FIRMS la corrige en ~5 meses"],
  ] as [string, string][],
  samplesNote: "Celdas de ejemplo, no son datos de una comuna.",
  resultsCount: (n: number) => `${n} comunas encontradas`,
  lance: "aviso de NASA LANCE",
  notIs: "Una detección no siempre es un incendio: puede ser un incendio forestal, una quema agrícola o un falso positivo. Una celda-día no es una hectárea. Un mes en cero puede haber estado nublado.",

  challengeLead: "Para el jurado de Space Apps, en inglés.",
  team: "Equipo GOLIAT · NASA Space Apps Challenge 2026 · Concepción, Chile",
  sources: "Datos: NASA FIRMS (MODIS y VIIRS), usados tal cual (ver el aviso de NASA LANCE) · Límites comunales: geoBoundaries/BCN · Mapa base: OpenFreeMap · Código abierto, Apache 2.0 · Uso de IA declarado en el README: ningún número lo genera una IA.",
  challengeMore: "How it is computed and tested",
  repo: "Código y método",
};

const en: typeof es = {
  htmlTitle: "GOLIAT · Satellite-detected fire activity",
  navExplore: "Explore communes",
  navExploreShort: "Explore",
  navHow: "How to read the data",
  navChallenge: "The challenge",
  langButton: "ES",
  langLabel: "ES · Leer en español",
  hQuestion: "In which months is fire detected in your commune?",


  sub: (k: number, n: number) => `NASA FIRMS fire detections for the ${n} communes of Biobío and Ñuble, Chile, month by month: VIIRS since 2012 in all of them and, in the ${k} where the correction passes the tests, MODIS Aqua for 2002–2012, harmonized into one series.`,
  eyebrow: (k: number, n: number) => `NASA FIRMS · VIIRS 2012–2026 · MODIS harmonized from 2002 in ${k} of ${n} communes`,
  alert: "Not an alert. If you see fire in Chile, call 130 (CONAF) or 132 (Firefighters) and follow SENAPRED notices.",
  searchLabel: "Find your commune",
  searchPlaceholder: "Type your commune's name…",
  dataFrom: (y: number) => `data from ${y}`,
  noResults: "No commune with that name in Biobío or Ñuble.",
  meta: (n: number, cutoff: string) => `${n} communes · data through ${cutoff}`,
  allLink: (n: number) => `See all ${n}`,
  mapKicker: (a: string, b: string) => `All seasons, ${a} to ${b}, month by month`,
  mapCount: (n: string, m: string, k: number) => `${n} sectors with a detection in at least one ${m} (${k} seasons)`,
  mapNote: (a: string, b: string) => `Observed by VIIRS, daytime (S-NPP through 2017-18, NOAA-20 from 2018-19). Each dot is a ~1 km sector where the satellite detected heat in that month in at least one full season (${a} to ${b}), excluding fixed sources. More sectors does not mean more or larger fire: what recurs every year, such as agricultural burns, lights up more sectors than a single large event such as February 2023, the month with the most cell-days in the series. Clouds limit what the satellite sees. Not a property, and it does not say who started it.`,
  mapScope: (k: number, n: number) => `This map is VIIRS only (2012→). The harmonized series from 2002 is in each commune: ${k} of ${n} pass the test.`,
  mapAria: (a: string, b: string, peak: string) => `Animated map of Biobío and Ñuble that runs through the year from July to June: each month lights up the sectors where VIIRS detected heat in that month, in the ${a} to ${b} seasons. The month with the most sectors is ${peak}; February 2023 is the month with the most cell-days in the series.`,
  mapPause: "Pause the map animation",
  mapPlay: "Play the map animation",
  legend: "seasons with a detection that month",
  legendClasses: ["1", "2", "3–4", "5 or more"],
  mapLoading: "Loading map…",
  mapError: "The map could not load. Search for your commune above.",
  open: (c: string) => `Open ${c}`,

  qTitle: "What you can learn about your commune",
  qIntro: "An example with real data.",
  pickLabel: "Commune",
  unit: "A cell-day is a ~1 km square where the satellite saw heat on one day: not a fire, not a hectare.",
  q1: "In which months is it detected?",
  monthsShort: ["Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar", "Apr", "May", "Jun"],
  monthsLong: ["July", "August", "September", "October", "November", "December", "January", "February", "March", "April", "May", "June"],
  monthAria: (m: string, med: string, k: number, n: number) => `${m}: median of ${med} cell-days, detections in ${k} of ${n} seasons`,
  factFocus: (c: string, ms: string[]) => `In ${c}, the ${ms.length > 1 ? "months with the highest median are" : "month with the highest median is"} ${joinEn(ms)}.`,
  factSpread: (c: string, ms: string[]) => `In ${c}, several months have similar medians: ${joinEn(ms)}.`,
  factLow: (c: string, low: string) => `In ${c}, no month reaches a median of ${low} cell-days: there are detections, but they do not recur in a fixed month.`,
  factPeak: (m: string, v: string) => `The highest single month was in ${m}: ${v} cell-days in one season. One extreme year does not move the median.`,
  monthLine: (m: string, med: string, k: number, n: number) => `${m}: median of ${med} cell-days; detections in ${k} of ${n} seasons.`,
  stripNote: (n: number, a: string, b: string) => `Observed (VIIRS, daytime). Darker means more cell-days: median of the ${n} seasons, ${a} to ${b}. Shading is relative to this commune's highest month; do not use it to compare communes. Tap a month to see its number. Includes agricultural burns: a detection is not a fire.`,
  dotsKey: (a: string, b: string) => `one season (${a} to ${b}) on the same day`,
  dotsCur: (s: string) => `${s}, in progress (provisional)`,
  q2: "How is this season going?",
  q2sentence: (c: string, _s: string, cut: string, cur: string, n: number, a: string, b: string, med: string | null) =>
    `Through ${cut}, ${c} has ${cur} cell-days (provisional). On the same date, across the ${n} previous seasons (${a} to ${b}), the median was ${med ?? "—"}.`,
  q2note: (n: number) => `This is what already happened: it does not anticipate what comes next. With ${n} seasons, compare with care; recent figures are preliminary.`,
  loading: "Loading…",

  seasonsTitle: "Season by season, since 2012",
  seasonsKey: ["Approximate: from MODIS Aqua", "Observed: VIIRS", "No estimate"],
  seasonsNoteOn: "Cell-days per season (July to June), observed by VIIRS; full seasons only. In this commune the correction from MODIS passed the tests: the explorer has the series from 2002, month by month with its typical error.",
  seasonsNoteOff: "Cell-days per season (July to June), observed by VIIRS; full seasons only. Before 2012 we give no figure for this commune: the correction from MODIS failed the tests. It does not mean there was no fire.",
  seasonsAria: (c: string, a: string, b: string) => `Cell-days per season in ${c}, ${a} to ${b}`,
  seasonAria: (s: string, state: string, v: string | null) => `${s}: ${state}${v == null ? "" : `, ${v} cell-days`}`,
  usesTitle: "What it is for",
  usesCta: "Pick your commune in the explorer",
  uses: [
    { icon: "municipio", t: "Your municipal plan", d: "Pick your commune, then print one A4 page or download the CSV, with source and cutoff date." },
    { icon: "vecinos", t: "Get your sector ready", d: "See which months and sectors keep coming back, and take it to your neighbours or the municipality." },
    { icon: "prensa", t: "Check a figure", d: "Compare seasons on the same day and download the detections." },
  ] as Use[],

  statesTitle: "How to read the data",
  statesIntro: "Each month says where its number comes from:",
  states: [
    ["Observed", "seen by the VIIRS satellite, since 2012"],
    ["Approximate", "estimated from the Aqua satellite (2002–2012), with its typical error (±)"],
    ["No estimate", "no figure before 2012 in this commune, because the correction failed the tests; it does not mean there was no fire"],
    ["May change", "preliminary figure; FIRMS corrects it in ~5 months"],
  ] as [string, string][],
  samplesNote: "Sample cells, not data from a commune.",
  resultsCount: (n: number) => `${n} communes found`,
  lance: "NASA LANCE disclaimer",
  notIs: "A detection is not always a fire: it can be a wildfire, an agricultural burn or a false positive. A cell-day is not a hectare. A month at zero may have been cloudy.",

  challengeLead: "",
  team: "Team GOLIAT · NASA Space Apps Challenge 2026 · Concepción, Chile",
  sources: "Data: NASA FIRMS (MODIS and VIIRS), used as is (see the NASA LANCE disclaimer below) · Commune boundaries: geoBoundaries/BCN · Explorer basemap: OpenFreeMap · Open source, Apache 2.0 · AI use declared in the README: no figure is generated by an AI model.",
  challengeMore: "How it is computed and tested",
  repo: "Code and method",
};

export const TEXT = { es, en };
export type Text = typeof es;

export const FIRMS_ACK = "We acknowledge the use of data and/or imagery from NASA's Fire Information for Resource Management System (FIRMS) (https://earthdata.nasa.gov/firms), part of NASA's Earth Science Data and Information System (ESDIS).";
export const REPO = "https://github.com/Loddrik/goliat-fire-calendar";
export const METHOD = `${REPO}/blob/main/docs/method.md`;
export const LANCE_URL = "https://www.earthdata.nasa.gov/data/projects/lance/disclaimer";
