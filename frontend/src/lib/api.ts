import type { SearchRequest, SearchResponse } from "./types";

// In dev, Vite proxies /api → backend (see vite.config.ts). In prod, set
// VITE_API_BASE to the deployed backend URL.
const BASE = import.meta.env.VITE_API_BASE ?? "";

export async function search(req: SearchRequest): Promise<SearchResponse> {
  const r = await fetch(`${BASE}/api/search`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });
  if (!r.ok) throw new Error(`Search failed: ${r.status}`);
  return r.json();
}

export async function health(): Promise<{ status: string; live: boolean }> {
  const r = await fetch(`${BASE}/api/health`);
  return r.json();
}
