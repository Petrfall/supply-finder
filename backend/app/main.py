"""FastAPI service: search & compare food suppliers.

Pipeline per request:
    cache → (live web-search + LLM extraction | seed fallback)
          → normalize + dedupe → deterministic scoring → cache → respond

The scoring is in code (auditable); the LLM only extracts and, when live,
writes the short per-supplier reason. With no API key the service still works
off the seed dataset, so the prototype opens and runs for anyone.
"""
from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from . import cache, store
from .dedup import dedupe
from .models import ScoredSupplier, SearchRequest, SearchResponse
from .providers import get_provider
from .scoring import score_and_rank
from .seed import seed_for

app = FastAPI(title="Food Supplier Finder", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

provider = get_provider()


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "live": provider.is_live()}


@app.post("/api/search", response_model=SearchResponse)
def search(req: SearchRequest) -> SearchResponse:
    warnings: list[str] = []

    # 1. Cache hit → return immediately.
    cached = cache.get(req)
    if cached:
        suppliers, summary = cached
        return SearchResponse(
            query_id=cache.query_key(req),
            category=req.category,
            region=req.region,
            source="cache",
            summary=summary,
            suppliers=_apply_filters(suppliers, req)[: req.limit],
            warnings=warnings,
        )

    # 2. Live search if a provider is configured; else seed fallback.
    raw = provider.find_suppliers(req) if provider.is_live() else []
    source = "live"
    if not raw:
        raw = seed_for(req.category, req.region or req.filters.region)
        source = "seed"
        if not provider.is_live():
            warnings.append(
                "Демо-режим: показаны примерные данные (ANTHROPIC_API_KEY не задан)."
            )

    # 3. Normalize + dedupe + deterministic scoring.
    deduped = dedupe(raw)
    scored = score_and_rank(deduped, req)
    scored = _apply_filters(scored, req)

    summary = _summary(scored, req)

    # 4. Cache the computed result (so repeat queries are instant).
    cache.put(req, scored, summary)

    return SearchResponse(
        query_id=cache.query_key(req),
        category=req.category,
        region=req.region,
        source=source,
        summary=summary,
        suppliers=scored[: req.limit],
        warnings=warnings,
    )


def _apply_filters(
    suppliers: list[ScoredSupplier], req: SearchRequest
) -> list[ScoredSupplier]:
    out = suppliers
    if req.filters.needs_certificates:
        out = [s for s in out if s.certificates]
    if req.filters.keyword:
        kw = req.filters.keyword.lower()
        out = [
            s for s in out
            if kw in s.name.lower() or kw in (s.description or "").lower()
        ]
    return out


def _summary(suppliers: list[ScoredSupplier], req: SearchRequest) -> str:
    """A short, deterministic 'who to contact first' summary.

    Code-generated (not the model) so the demo path produces it too; the live
    provider can later replace this with an LLM-written version per supplier.
    """
    if not suppliers:
        return "Подходящих поставщиков не найдено — измените категорию или регион."
    top = suppliers[0]
    n_certs = sum(1 for s in suppliers if s.certificates)
    bits = [
        f"Найдено {len(suppliers)} поставщиков.",
        f"Лучший по соответствию — «{top.name}» (score {top.score}).",
    ]
    if n_certs:
        bits.append(f"{n_certs} из них с сертификатами.")
    if req.region:
        bits.append(f"Учтён регион «{req.region}».")
    return " ".join(bits)


# ---------------------------------------------------------------------------
# Per-client storage: saved suppliers + message presets.
# client_id is an opaque id the browser generates — a registration-free "LK".
# ---------------------------------------------------------------------------


class SaveSupplierBody(BaseModel):
    client_id: str
    supplier: ScoredSupplier


class PresetBody(BaseModel):
    client_id: str
    preset: dict[str, Any]  # { name, fields: [...], template, ... } — UI-defined


@app.get("/api/saved")
def get_saved(client_id: str) -> list[dict]:
    return store.list_saved(client_id)


@app.post("/api/saved")
def post_saved(body: SaveSupplierBody) -> dict:
    store.save_supplier(body.client_id, body.supplier.model_dump())
    return {"ok": True}


@app.delete("/api/saved")
def del_saved(client_id: str, name: str) -> dict:
    store.delete_saved(client_id, name)
    return {"ok": True}


@app.get("/api/presets")
def get_presets(client_id: str) -> list[dict]:
    return store.list_presets(client_id)


@app.post("/api/presets")
def post_preset(body: PresetBody) -> dict:
    store.save_preset(body.client_id, body.preset)
    return {"ok": True}


@app.delete("/api/presets")
def del_preset(client_id: str, name: str) -> dict:
    store.delete_preset(client_id, name)
    return {"ok": True}
