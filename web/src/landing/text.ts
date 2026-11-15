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
  hLead: "Usa lo que vieron los satélites para",
  hWords: ["tu plan comunal", "preparar tu sector", "cuidar a tu comunidad"],
  hFull: "¿En qué meses se detecta fuego en tu comuna? Usa lo que vieron los satélites para tu plan comunal, para preparar tu sector y para cuidar a tu comunidad.",
  sub: "Lo que los satélites de la NASA han visto desde 2012 en Biobío y Ñuble, mes a mes y sector por sector.",
  alert: "No es una alerta. Si ves fuego, llama al 130 (CONAF) o al 132 (Bomberos) y sigue los avisos de SENAPRED.",
  searchLabel: "Busca tu comuna",
  searchPlaceholder: "Escribe el nombre de tu comuna…",
  dataFrom: (y: number) => `datos desde ${y}`,
  ofWord: "de",
  mapTapAgain: "Toca de nuevo para abrir",
  noResults: "No hay una comuna con ese nombre en Biobío o Ñuble.",
  meta: (n: number, cutoff: string) => `${n} comunas · datos hasta el ${cutoff}`,
  allLink: (n: number) => `Ver las ${n}`,
  mapTitle: (a: string, b: string, cut: string) => `Dónde se ha detectado y en cuántas temporadas · ${a} a ${b} (la última hasta el ${cut}, provisional)`,
  mapNote: "Cada cuadro es un sector de ~1 km donde el satélite VIIRS detectó calor de día desde 2012, sin fuentes fijas como industrias o volcanes. No es un predio, una empresa ni un incendio, y no dice quién lo provocó.",
  mapHint: "Toca una comuna para abrirla.",
  mapAria: "Mapa de Biobío y Ñuble con los sectores donde el satélite VIIRS detectó calor desde 2012, por número de temporadas.",
  legend: "temporadas con detección en el sector",
  legendClasses: ["1", "2", "3–4", "5–7", "8 o más"],
  mapLoading: "Cargando el mapa…",
  mapError: "No se pudo cargar el mapa. Busca tu comuna arriba.",
  open: (c: string) => `Abrir ${c}`,

  qTitle: "Lo que puedes saber de tu comuna",
  qIntro: "Un ejemplo con datos reales.",
  pickLabel: "Comuna",
  unit: "Una celda-día es un cuadrado de ~1 km donde el satélite vio calor un día: no es un incendio ni una hectárea.",
  q1: "¿En qué meses se concentra?",
  q1short: (n: number) => `Barra: la mediana de ${n} temporadas · raya: el máximo · abajo: en cuántas hubo detección. Incluye quemas agrícolas: una detección no es un incendio.`,
  howToRead: "¿Cómo se lee?",
  q1note: (n: number, a: string, b: string) => `Barra y número arriba: la mediana de las ${n} temporadas observadas (${a} a ${b}), es decir, el valor del medio. Raya y número chico: el valor más alto de ese mes en las ${n} temporadas (un solo año). Abajo: en cuántas de las ${n} temporadas hubo detección ese mes. Celdas-día por mes, satélite VIIRS (S-NPP hasta 2017, NOAA-20 desde 2018), pasada de día. Incluye quemas agrícolas: una detección no es un incendio.`,
  monthsShort: ["Jul", "Ago", "Sep", "Oct", "Nov", "Dic", "Ene", "Feb", "Mar", "Abr", "May", "Jun"],
  ofSeasonsAria: (m: string, med: string, max: string, k: number, n: number) => `${m}: mediana ${med}, máximo ${max}, con detección en ${k} de ${n} temporadas`,
  q2: "¿Cómo va esta temporada?",
  q2sentence: (c: string, s: string, cut: string, cur: string, n: number, a: string, b: string, med: string | null) =>
    `${c}, temporada ${s}, hasta el ${cut}: ${cur} celdas-día con detección (provisional). En las ${n} temporadas observadas (${a} a ${b}), al mismo día, la mediana fue ${med ?? "—"}.`,
  q2note: (n: number) => `Es lo que ya pasó: no anticipa cómo seguirá. Con ${n} temporadas, compara con cuidado; las cifras recientes son preliminares.`,
  loading: "Cargando…",

  usesTitle: "Para qué sirve",
  uses: [
    { icon: "municipio", t: "Tu plan comunal", d: "Imprime una hoja A4 o descarga el CSV, con fuente y fecha de corte." },
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
  notIs: "Una detección no es un incendio: puede ser un incendio, una quema agrícola o un falso positivo. Una celda-día no es una hectárea. Un mes en cero puede haber estado nublado.",

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
  hLead: "Use what the satellites saw to",
  hWords: ["back your municipal plan", "get your sector ready", "look after your community"],
  hFull: "In which months is fire detected in your commune? Use what the satellites saw to back your municipal plan, get your sector ready and look after your community.",
  sub: "What NASA satellites have seen since 2012 in Biobío and Ñuble, Chile, month by month and sector by sector.",
  alert: "Not an alert. If you see fire in Chile, call 130 (CONAF) or 132 (Firefighters) and follow SENAPRED notices.",
  searchLabel: "Find your commune",
  searchPlaceholder: "Type your commune's name…",
  dataFrom: (y: number) => `data from ${y}`,
  ofWord: "of",
  mapTapAgain: "Tap again to open",
  noResults: "No commune with that name in Biobío or Ñuble.",
  meta: (n: number, cutoff: string) => `${n} communes · data through ${cutoff}`,
  allLink: (n: number) => `See all ${n}`,
  mapTitle: (a: string, b: string, cut: string) => `Where heat was detected, and in how many seasons · ${a} to ${b} (the last one through ${cut}, provisional)`,
  mapNote: "Each square is a ~1 km sector where the VIIRS satellite detected daytime heat since 2012, excluding fixed sources such as industry or volcanoes. It is not a property, a company or a fire, and it does not say who started it.",
  mapHint: "Tap a commune to open it.",
  mapAria: "Map of Biobío and Ñuble showing sectors where VIIRS detected heat since 2012, by number of seasons.",
  legend: "seasons with a detection in the sector",
  legendClasses: ["1", "2", "3–4", "5–7", "8 or more"],
  mapLoading: "Loading map…",
  mapError: "The map could not load. Search for your commune above.",
  open: (c: string) => `Open ${c}`,

  qTitle: "What you can learn about your commune",
  qIntro: "An example with real data.",
  pickLabel: "Commune",
  unit: "A cell-day is a ~1 km square where the satellite saw heat on one day: not a fire, not a hectare.",
  q1: "Which months concentrate activity?",
  q1short: (n: number) => `Bar: the median of ${n} seasons · tick: the maximum · below: in how many there was a detection. Includes agricultural burns: a detection is not a fire.`,
  howToRead: "How to read it",
  q1note: (n: number, a: string, b: string) => `Bar and top number: the median of the ${n} observed seasons (${a} to ${b}), the middle value. Tick and small number: the highest value for that month across the ${n} seasons (a single year). Below: in how many of the ${n} seasons that month had a detection. Cell-days per month, VIIRS satellite (S-NPP through 2017, NOAA-20 from 2018), daytime pass. Includes agricultural burns: a detection is not a fire.`,
  monthsShort: ["Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar", "Apr", "May", "Jun"],
  ofSeasonsAria: (m: string, med: string, max: string, k: number, n: number) => `${m}: median ${med}, maximum ${max}, detections in ${k} of ${n} seasons`,
  q2: "How is this season going?",
  q2sentence: (c: string, s: string, cut: string, cur: string, n: number, a: string, b: string, med: string | null) =>
    `${c}, season ${s}, through ${cut}: ${cur} cell-days with a detection (provisional). Across the ${n} observed seasons (${a} to ${b}), on the same day, the median was ${med ?? "—"}.`,
  q2note: (n: number) => `This is what already happened: it does not anticipate what comes next. With ${n} seasons, compare with care; recent figures are preliminary.`,
  loading: "Loading…",

  usesTitle: "What it is for",
  uses: [
    { icon: "municipio", t: "Your municipal plan", d: "Print one A4 page or download the CSV, with source and cutoff date." },
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
  notIs: "A detection is not a fire: it can be a wildfire, an agricultural burn or a false positive. A cell-day is not a hectare. A month at zero may have been cloudy.",

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
