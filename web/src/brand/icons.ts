// Íconos de GOLIAT: grilla de 24 px, trazo 1,75 en currentColor, puntas redondeadas.
// Mismo lenguaje que el logo (satélite de un panel, llama con núcleo). Fuente única: este archivo.
// Cada valor es el contenido interior de un <svg viewBox="0 0 24 24">.

const FLAME = 'M47 42 C58 58 71 69 71 88 C71 105 57 117 40 117 C23 117 10 105 10 89 C10 76 18 67 23 56 C26.5 66 30 71.5 36.5 74 C33.5 62 37 50 47 42 Z';

export const ICONS = {
  satelite: `<g transform="rotate(-35 12 12)">
      <rect x="3.5" y="9" width="5.5" height="6" rx="1.2"/>
      <path d="M9 12h2"/>
      <rect x="11" y="9.25" width="9.5" height="5.5" rx=".8"/>
      <path d="M14.2 9.25v5.5M17.4 9.25v5.5"/>
      <path d="M5.2 17.2h2.2"/></g>`,
  llama: `<g transform="translate(2.6 .6) scale(.235)"><path vector-effect="non-scaling-stroke" d="${FLAME}"/></g>`,
  calor: `<g transform="translate(1.2 6.2) scale(.15)"><path vector-effect="non-scaling-stroke" d="${FLAME}"/></g>
      <path d="M11.5 9.5c.9-1.2 1.9-1.2 2.6 0s1.8 1.2 2.6 0 1.8-1.2 2.6 0"/>
      <path d="M20.6 4.2l1.6 1.6M19 5.8l2.4-2.4"/>`,
  calendario: `<rect x="3.5" y="5" width="17" height="15.5" rx="2"/>
      <path d="M3.5 9.5h17M8 3v4M16 3v4M7.5 13h2M11 13h2M14.5 13h2M7.5 16.5h2M11 16.5h2"/>`,
  mapa: `<path d="M3.5 6.5 9 4.5l6 2 5.5-2v13l-5.5 2-6-2-5.5 2z"/><path d="M9 4.5v13M15 6.5v13"/>`,
  imprimir: `<path d="M7 9V3.5h10V9"/><rect x="3.5" y="9" width="17" height="8" rx="1.8"/>
      <path d="M7 14.5h10v6H7z"/><path d="M17 11.8h.01"/>`,
  datos: `<path d="M14 3.5H7a1.8 1.8 0 0 0-1.8 1.8v13.4A1.8 1.8 0 0 0 7 20.5h10a1.8 1.8 0 0 0 1.8-1.8V8.3z"/>
      <path d="M14 3.5v4.8h4.8M8.5 12.5h7M8.5 15.5h7M12 11v6.5"/>`,
  descargar: `<path d="M12 4v11M7 10.5l5 5 5-5M4.5 20h15"/>`,
  municipio: `<path d="M3 9.5 12 4l9 5.5z"/><path d="M4 20h16M3 21.2h18M6 11.5v6.5M10 11.5v6.5M14 11.5v6.5M18 11.5v6.5"/>`,
  vecinos: `<path d="M2.5 20.5h19"/><path d="M3.5 20.5V12l4.5-4 4.5 4v8.5"/><path d="M12.5 20.5V14l4-3.5 4 3.5v6.5"/>
      <path d="M6.6 20.5v-3.6h2.8v3.6M15.3 20.5v-2.8h2.4v2.8"/>`,
  prensa: `<path d="M4.5 4.5h12v14a2 2 0 0 0 2 2H6.5a2 2 0 0 1-2-2z"/><path d="M16.5 8.5h3v10a2 2 0 0 1-4 0"/>
      <path d="M7.5 8h6M7.5 11h6M7.5 14h6M7.5 17h4"/>`,
  investigacion: `<circle cx="10.5" cy="10.5" r="6.5"/><path d="M15.3 15.3 20.5 20.5"/><path d="m7.4 12.4 2-2.4 1.8 1.4 2.4-3"/>`,
  buscar: `<circle cx="10.5" cy="10.5" r="6.5"/><path d="M15.3 15.3 20.5 20.5"/>`,
  idioma: `<circle cx="12" cy="12" r="8.5"/><path d="M3.5 12h17M12 3.5c2.4 2.3 3.5 5.2 3.5 8.5s-1.1 6.2-3.5 8.5c-2.4-2.3-3.5-5.2-3.5-8.5S9.6 5.8 12 3.5z"/>`,
  telefono: `<rect x="7" y="2.5" width="10" height="19" rx="2.2"/><path d="M10.8 18.2h2.4"/>`,
  flecha: `<path d="M4.5 12h15M13.5 6l6 6-6 6"/>`,
  externo: `<path d="M13.5 4.5h6v6M19.5 4.5l-8.5 8.5"/><path d="M18 14v4.2a1.8 1.8 0 0 1-1.8 1.8H5.8A1.8 1.8 0 0 1 4 18.2V7.8A1.8 1.8 0 0 1 5.8 6H10"/>`,
  codigo: `<path d="m8.5 7-5 5 5 5M15.5 7l5 5-5 5M13.5 4.5l-3 15"/>`,
} as const;
