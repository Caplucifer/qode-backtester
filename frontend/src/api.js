import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000/api",
  timeout: 60000,
});

export async function runBacktest(payload) {
  const { data } = await api.post("/backtest", payload);
  return data;
}

export async function getAvailableMetrics() {
  const { data } = await api.get("/metrics");
  return data;
}

export async function getCompanies() {
  const { data } = await api.get("/companies");
  return data;
}

export default api;
