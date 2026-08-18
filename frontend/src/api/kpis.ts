import { api } from "./client";
import type { KPISummary, SimulationResult } from "../types/domain";

export const getKPISummary = () => api.get<KPISummary>("/kpis/summary").then((r) => r.data);

export const runSimulation = (scenario: string, district?: string) =>
  api
    .post<SimulationResult>("/digital-twin/simulate", { scenario, district, event_multiplier: 2.5 })
    .then((r) => r.data);
