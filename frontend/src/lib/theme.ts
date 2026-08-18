export function dcpiColor(v: number) {
  if (v >= 75) return "#ef4444";
  if (v >= 55) return "#e85d25";
  if (v >= 35) return "#f59e0b";
  return "#3dcc7a";
}

export function dcpiLabel(v: number) {
  if (v >= 75) return "Critical";
  if (v >= 55) return "High";
  if (v >= 35) return "Watch";
  return "Stable";
}

export const FEATURE_LABELS: Record<string, string> = {
  fill_pct: "Fill level",
  predicted_fill_pct: "4h forecast",
  heat_index: "Heat index",
  gas_index: "Gas / methane",
  event_boost: "City event",
};

export const DARK_TILES =
  "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png";
