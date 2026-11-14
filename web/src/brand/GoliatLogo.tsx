/**
 * Logo de GOLIAT. Los SVG viven en /brand (generados por design/logo/export.mjs desde design/logo/mark.js).
 * - variant="horizontal": ícono + nombre, para cabeceras (alto recomendado 28–40 px).
 * - variant="lema": ícono + nombre + "Actividad de fuego · detectada por satélite" (o su versión en inglés).
 * - variant="icon": solo el ícono; bajo 48 px usa la versión chica, sin detalles finos.
 * tone="dark" es para fondos oscuros (azul noche).
 */
type Variant = "horizontal" | "lema" | "icon";

export function GoliatLogo({ variant = "horizontal", tone = "light", height = 32, lang = "es", className }: {
  variant?: Variant;
  tone?: "light" | "dark";
  height?: number;
  lang?: "es" | "en";
  className?: string;
}) {
  const dark = tone === "dark" ? "-oscuro" : "";
  let src: string;
  if (variant === "icon") src = `/brand/goliat-icono${height < 48 ? "-chico" : ""}${dark}.svg`;
  else if (variant === "lema") src = `/brand/goliat-logo-lema${lang === "en" ? "-en" : ""}${dark}.svg`;
  else src = `/brand/goliat-logo${dark}.svg`;
  const alt = lang === "en" ? "GOLIAT · Satellite-detected fire activity" : "GOLIAT · Actividad de fuego detectada por satélite";
  return <img className={className} src={src} alt={alt} height={height} style={{ height, width: "auto", display: "block" }} />;
}
