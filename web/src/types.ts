export type State = "observed" | "estimated" | "not_enabled";

export interface MonthRow {
  season: number;
  y: number;
  m: number;
  value: number | null;
  state: State;
  sat?: "SNPP" | "NOAA20";
  provisional?: boolean;
  band?: number;
  aqua?: number;
}

export interface SeasonCompare {
  season: number;
  months: number[];
  current: number;
  observed_seasons: Record<string, number>;
  median: number | null;
  p25: number | null;
  p75: number | null;
  p90: number | null;
}

export interface RecurrenceCell { x: number; y: number; n: number; d: number; f: number; l: number }

export interface ComunaDoc {
  cut: string;
  comuna: string;
  region: string;
  cutoff: string;
  r_const: number;
  reconstruction_enabled: boolean;
  gates: { mae_const: number; mae_clim: number; wins_vs_clim: number; of: number; aqua_train: number; snpp_train: number };
  series: MonthRow[];
  season_compare: SeasonCompare;
  recurrence: RecurrenceCell[];
}

export interface IndexEntry { cut: string; comuna: string; region: string; enabled: boolean; observed_2012_2025: number; current: number; median: number | null }
export interface IndexDoc { generated: string; cutoff: string; current_season: number; r_const: number; comunas: IndexEntry[] }

export const MONTHS_SEASON = [7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6];
export const seasonLabel = (s: number) => `${s}-${String(s + 1).slice(2)}`;
