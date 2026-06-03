import { getIdToken } from "./auth";

const BASE = import.meta.env.VITE_API_ENDPOINT?.replace(/\/$/, "");

async function authHeaders() {
  const token = await getIdToken();
  return { Authorization: token, "Content-Type": "application/json" };
}

async function request(method, path, body) {
  const headers = await authHeaders();
  const res = await fetch(`${BASE}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) throw new Error(`${method} ${path} → ${res.status}`);
  return res.json();
}

export const getAlerts  = ()         => request("GET",  "/alerts");
export const getTenants = ()         => request("GET",  "/tenants");
export const postTenant = (data)     => request("POST", "/tenants", data);
export const postIngest = (data)     => request("POST", "/ingest",  data);
