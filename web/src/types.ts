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
  partial?: boolean;
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
  n: number;
  cutoff_day: number;
}

export interface RecurrenceCell { x: number; y: number; n: number; d: number; f: number; l: number }

export interface ComunaDoc {
  cut: string;
  comuna: string;
  region: string;
  cutoff: string;
  r_const: number;
  reconstruction_enabled: boolean;
  gates: { aqua_train: number; snpp_train: number; min_aqua: number; loso_mae_raw: number; loso_mae_const: number; loso_mae_clim: number; wins_vs_clim: number; wins_vs_raw: number; of: number; min_wins: number; gate_aqua: boolean; gate_vs_clim: boolean; gate_vs_raw: boolean; band_mae: number; band_coverage_1: number; band_coverage_2: number };
  series: MonthRow[];
  season_compare: SeasonCompare;
  recurrence: RecurrenceCell[];
}

export interface IndexEntry { cut: string; comuna: string; region: string; enabled: boolean; observed_2012_2025: number; current: number; median: number | null }
export interface IndexDoc { generated: string; cutoff: string; current_season: number; r_const: number; comunas: IndexEntry[] }

export const MONTHS_SEASON = [7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6];
export const seasonLabel = (s: number) => `${s}-${String(s + 1).slice(2)}`;
