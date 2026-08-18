import { api } from "./client";
import type { PredictionCurve } from "../types/domain";

export const getPredictions = (binId: number, horizon = 24) =>
  api.get<PredictionCurve>(`/predictions/${binId}`, { params: { horizon } }).then((r) => r.data);
