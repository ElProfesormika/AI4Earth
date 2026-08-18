import { api } from "./client";
import type { DCPIItem, DCPIDetail } from "../types/domain";

export const listDCPI = () => api.get<DCPIItem[]>("/dcpi").then((r) => r.data);
export const getDCPI = (id: number) => api.get<DCPIDetail>(`/dcpi/${id}`).then((r) => r.data);
