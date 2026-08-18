import { api } from "./client";
import type { Bin } from "../types/domain";

export const listBins = () => api.get<Bin[]>("/bins").then((r) => r.data);
