export type WasteClass = "plastic" | "paper" | "glass" | "metal" | "organic" | "ewaste";

export interface Bin {
  id: number;
  name: string;
  district: string;
  lat: number;
  lon: number;
  capacity_l: number;
}

export interface DCPIItem {
  bin_id: number;
  name: string;
  district: string;
  lat: number;
  lon: number;
  dcpi: number;
  ts: string;
}

export interface DCPIDetail {
  bin_id: number;
  dcpi: number;
  ts: string;
  features: Record<string, number>;
  reasons: { feature: string; contribution: number }[];
}

export interface RouteInfo {
  id: number;
  ts: string;
  truck_id: string;
  stops: number[];
  distance_km: number;
  expected_fuel_saving_pct: number;
  expected_co2_saving_kg: number;
}

export interface PredictionPoint {
  ts_target: string;
  predicted_fill_pct: number;
  horizon_hours: number;
}

export interface PredictionCurve {
  bin_id: number;
  points: PredictionPoint[];
}

export interface KPISummary {
  bins_total: number;
  overflow_risk_avg: number;
  wqs_avg: number;
  co2_avoided_kg: number;
  cost_saved_pct: number;
  workers_active: number;
  payments_today: number;
}

export interface SimulationResult {
  scenario: string;
  district: string | null;
  bins_affected: number;
  avg_dcpi_before: number;
  avg_dcpi_after: number;
  message: string;
}

export interface TelemetryLatest {
  bin_id: number;
  bin_name?: string;
  district?: string;
  fill_pct: number;
  temp_c: number;
  gas_ppm: number;
}
