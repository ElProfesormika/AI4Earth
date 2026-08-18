import { api } from "./client";
import type { RouteInfo } from "../types/domain";

export const getTodayRoute = () => api.get<RouteInfo | null>("/routes/today").then((r) => r.data);
export const optimizeRoute = () => api.post<RouteInfo>("/routes/optimize").then((r) => r.data);
