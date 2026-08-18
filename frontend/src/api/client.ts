import axios from "axios";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE + "/api/v1",
  timeout: 8000,
});

export const pollInterval = Number(import.meta.env.VITE_POLL_INTERVAL_MS || 5000);
