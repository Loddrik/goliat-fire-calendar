// Textos de la landing. Los textos compartidos con la app (título, línea, aviso, estados) son los
// acordados con la sesión de rediseño el 14-11; si cambian allá, cambian acá.
// Lenguaje (CLAUDE.md regla 1): actividad de fuego detectada, detecciones, sectores, celdas-día.


export type Lang = "es" | "en";
type Use = { who: string; what: string; get: string };

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

  // Tu comuna en tres preguntas (#40, para cualquier persona): respuesta corta en grande, detalle en chico.
  qIntro: "Un ejemplo con datos reales. Contamos celdas-día: cada día que el satélite detecta calor en un cuadrado de ~1 km suma una. No es un incendio ni una hectárea.",
  whenAsk: (c: string) => `¿Cuándo se detecta fuego en ${c}?`,
  whenFocus: (ms: string[], often: "all" | "almost" | "some") => `${cap(joinEs(ms))}${often === "all" ? ", todos los años" : often === "almost" ? ", casi todos los años" : ""}.`,
  whenSpread: (ms: string[]) => `Repartido en varios meses: ${joinEs(ms)}.`,
  whenLow: "Hay pocas detecciones y no se repiten en un mes fijo.",
  whenPeak: (m: string, y: number, v: string) => `Ojo: el mes con más detecciones de un solo año fue ${m} de ${y}, con ${v} celdas-día.`,
  monthLine: (m: string, med: string, k: number, n: number) => `${cap(m)}: hubo detecciones en ${k} de los últimos ${n} años; el valor del medio es ${med} celdas-día.`,
  whenFine: (n: number) => `Cada barra es el valor del medio (mediana) de los últimos ${n} años, observado por VIIRS de día. Toca un mes para ver su número. Incluye quemas agrícolas: una detección no siempre es un incendio.`,
  nowAsk: "¿Y este año?",
  nowLess: (k: number, n: number) => `Menos detecciones que ${k} de los ${n} años anteriores, a esta fecha.`,
  nowMore: (k: number, n: number) => `Más detecciones que ${k} de los ${n} años anteriores, a esta fecha.`,
  nowThis: "este año",
  nowFewer: "menos",
  nowMoreAx: "más",
  nowLine: (cut: string, cur: string, med: string) => `Del 1 de julio al ${cut}: ${cur} celdas-día (provisional). Cada punto es un año anterior en las mismas fechas; el del medio tuvo ${med}.`,
  nowFine: "Es lo que ya pasó: no anticipa cómo seguirá la temporada. Cada año se cuenta de julio a junio.",
  yearsAsk: "¿Qué año tuvo más?",
  yearsAnswer: (s: string) => `La temporada ${s}.`,
  yearsLine: (s: string, v: string) => `${s}: ${v} celdas-día, de julio a junio.`,
  yearsFine: (k: number) => `Cada barra es una temporada, de julio a junio, observada por VIIRS desde 2012-13. En las ${k} comunas donde la corrección desde MODIS pasó las pruebas, Explorar muestra también 2002 a 2012.`,
  sampleCta: (c: string) => `Ver ${c} completa en Explorar`,
  qTitle: "Lo que puedes saber de tu comuna",
  pickLabel: "Comuna",
  monthsShort: ["Jul", "Ago", "Sep", "Oct", "Nov", "Dic", "Ene", "Feb", "Mar", "Abr", "May", "Jun"],
  monthsLong: ["julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre", "enero", "febrero", "marzo", "abril", "mayo", "junio"],
  monthAria: (m: string, med: string, k: number, n: number) => `${m}: mediana de ${med} celdas-día, detección en ${k} de ${n} temporadas`,
  loading: "Cargando…",

  usesTitle: "Para qué sirve",
  // Para qué sirve (#40): quién, qué hace y qué se lleva. Sin tarjetas ni íconos.
  uses: [
    { who: "Si trabajas en emergencias del municipio", what: "Imprime la hoja A4 de tu comuna para el plan comunal: meses, sectores, fuente y fecha de corte.", get: "Hoja A4 · CSV" },
    { who: "Si eres de una junta de vecinos", what: "Mira qué meses y qué sectores de tu comuna se repiten año a año, y llévalo a la reunión o al municipio.", get: "Mapa de sectores" },
    { who: "Si eres periodista o investigas", what: "Compara esta temporada con las anteriores en las mismas fechas y descarga cada detección.", get: "Comparación · CSV" },
  ] as Use[],
  usesCta: "Busca tu comuna",
  usesOr: "o abre Explorar",

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

  qIntro: "An example with real data. We count cell-days: each day the satellite detects heat in a ~1 km square adds one. Not a fire, not a hectare.",
  whenAsk: (c: string) => `When is fire detected in ${c}?`,
  whenFocus: (ms: string[], often: "all" | "almost" | "some") => `${joinEn(ms)}${often === "all" ? ", every year" : often === "almost" ? ", almost every year" : ""}.`,
  whenSpread: (ms: string[]) => `Spread over several months: ${joinEn(ms)}.`,
  whenLow: "Few detections, and they do not recur in a fixed month.",
  whenPeak: (m: string, y: number, v: string) => `Note: the month with the most detections in a single year was ${m} ${y}, with ${v} cell-days.`,
  monthLine: (m: string, med: string, k: number, n: number) => `${m}: detections in ${k} of the last ${n} years; the middle value is ${med} cell-days.`,
  whenFine: (n: number) => `Each bar is the middle value (median) of the last ${n} years, observed by VIIRS in daytime. Tap a month to see its number. Includes agricultural burns: a detection is not always a fire.`,
  nowAsk: "And this year?",
  nowLess: (k: number, n: number) => `Fewer detections than ${k} of the ${n} previous years, by this date.`,
  nowMore: (k: number, n: number) => `More detections than ${k} of the ${n} previous years, by this date.`,
  nowThis: "this year",
  nowFewer: "fewer",
  nowMoreAx: "more",
  nowLine: (cut: string, cur: string, med: string) => `July 1 to ${cut}: ${cur} cell-days (provisional). Each dot is a previous year over the same dates; the middle one had ${med}.`,
  nowFine: "This is what already happened: it does not anticipate how the season will go. Each year runs July to June.",
  yearsAsk: "Which year had the most?",
  yearsAnswer: (s: string) => `The ${s} season.`,
  yearsLine: (s: string, v: string) => `${s}: ${v} cell-days, July to June.`,
  yearsFine: (k: number) => `Each bar is a season, July to June, observed by VIIRS from 2012-13. In the ${k} communes where the correction from MODIS passed the tests, the explorer also shows 2002 to 2012.`,
  sampleCta: (c: string) => `See all of ${c} in the explorer`,
  qTitle: "What you can learn about your commune",
  pickLabel: "Commune",
  monthsShort: ["Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar", "Apr", "May", "Jun"],
  monthsLong: ["July", "August", "September", "October", "November", "December", "January", "February", "March", "April", "May", "June"],
  monthAria: (m: string, med: string, k: number, n: number) => `${m}: median of ${med} cell-days, detections in ${k} of ${n} seasons`,
  loading: "Loading…",

  usesTitle: "What it is for",
  uses: [
    { who: "If you work in municipal emergency management", what: "Print your commune's A4 sheet for the municipal plan: months, sectors, source and cutoff date.", get: "A4 sheet · CSV" },
    { who: "If you are part of a neighbourhood council", what: "See which months and which sectors of your commune come back year after year, and take it to the meeting or the municipality.", get: "Sector map" },
    { who: "If you are a journalist or researcher", what: "Compare this season with previous ones over the same dates and download every detection.", get: "Comparison · CSV" },
  ] as Use[],
  usesCta: "Find your commune",
  usesOr: "or open the explorer",

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
