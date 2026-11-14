import type { ComunaDoc } from "./types";

export function seriesCsv(doc: ComunaDoc): string {
  const head = ["cut", "comuna", "season", "year", "month", "celldays_viirs_scale", "state", "platform", "provisional", "band_mae", "aqua_celldays", "cutoff", "r_const"];
  const lines = doc.series.map((r) => [doc.cut, doc.comuna, r.season, r.y, r.m, r.value ?? "", r.state, r.sat ?? (r.state === "estimated" ? "Aqua" : ""), r.provisional ? 1 : 0, r.band ?? "", r.aqua ?? "", doc.cutoff, doc.r_const].join(","));
  const meta = [
    "# GOLIAT - detected fire activity (cell-days, 0.01 deg, daytime, VIIRS scale). NOT fires, NOT hectares.",
    "# observed = VIIRS S-NPP (seasons 2012-2017) / NOAA-20 (2018+); estimated = MODIS Aqua x r_const; not_enabled = reconstruction did not pass gates.",
    "# Source: NASA FIRMS (MODIS C6.1, VIIRS 375 m). We acknowledge the use of data from NASA FIRMS, part of NASA EOSDIS.",
    `# Method: https://github.com/Loddrik/goliat-fire-calendar · cutoff ${doc.cutoff}`,
  ];
  return [...meta, head.join(","), ...lines].join("\n");
}

export function download(name: string, text: string, type = "text/csv;charset=utf-8") {
  const a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob([text], { type }));
  a.download = name; a.click(); setTimeout(() => URL.revokeObjectURL(a.href), 1000);
}
