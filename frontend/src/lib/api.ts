import type { ScoredSupplier, SearchRequest, SearchResponse } from "./types";

// In dev, Vite proxies /api → backend (see vite.config.ts). In prod, set
// VITE_API_BASE to the deployed backend URL.
const BASE = import.meta.env.VITE_API_BASE ?? "";

// A registration-free "account": a random id kept in localStorage so the
// backend can scope saved suppliers / presets to this browser.
export function clientId(): string {
  let id = localStorage.getItem("client_id");
  if (!id) {
    id = crypto.randomUUID();
    localStorage.setItem("client_id", id);
  }
  return id;
}

export async function search(req: SearchRequest): Promise<SearchResponse> {
  // Live LLM calls (esp. via a slow proxy) can take a while — allow up to 120s.
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), 120_000);
  try {
    const r = await fetch(`${BASE}/api/search`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(req),
      signal: ctrl.signal,
    });
    if (!r.ok) throw new Error(`Search failed: ${r.status}`);
    return r.json();
  } finally {
    clearTimeout(timer);
  }
}

export async function health(): Promise<{ status: string; live: boolean }> {
  const r = await fetch(`${BASE}/api/health`);
  return r.json();
}

// ---- saved suppliers -------------------------------------------------------

export async function listSaved(): Promise<ScoredSupplier[]> {
  const r = await fetch(`${BASE}/api/saved?client_id=${clientId()}`);
  return r.ok ? r.json() : [];
}

export async function saveSupplier(supplier: ScoredSupplier): Promise<void> {
  await fetch(`${BASE}/api/saved`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ client_id: clientId(), supplier }),
  });
}

export async function deleteSaved(name: string): Promise<void> {
  await fetch(
    `${BASE}/api/saved?client_id=${clientId()}&name=${encodeURIComponent(name)}`,
    { method: "DELETE" }
  );
}

// ---- message-builder presets ----------------------------------------------

export interface MessagePreset {
  name: string;
  fields: { key: string; label: string; value: string }[];
  template: string;
}

export async function listPresets(): Promise<MessagePreset[]> {
  const r = await fetch(`${BASE}/api/presets?client_id=${clientId()}`);
  return r.ok ? r.json() : [];
}

export async function savePreset(preset: MessagePreset): Promise<void> {
  await fetch(`${BASE}/api/presets`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ client_id: clientId(), preset }),
  });
}

export async function deletePreset(name: string): Promise<void> {
  await fetch(
    `${BASE}/api/presets?client_id=${clientId()}&name=${encodeURIComponent(name)}`,
    { method: "DELETE" }
  );
}
