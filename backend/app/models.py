"""Data contracts for the supplier-finder service.

The LLM is forced to return data that matches `Supplier` (structured output),
so everything downstream — scoring, dedup, the API response — works against a
single validated shape instead of free-form text.
"""
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field

# Product categories the service understands. Kept deliberately small and
# food-focused; the UI offers these, but free-text categories also work.
Category = Literal[
    "ingredients",
    "finished_products",
    "packaging",
    "equipment",
    "beverages",
    "other",
]


class SourceRef(BaseModel):
    """Where a particular field came from — for data transparency."""

    field: str
    url: Optional[str] = None
    note: Optional[str] = None


class Supplier(BaseModel):
    """A single supplier, as extracted from the web and normalized.

    Most fields are optional on purpose: real listings are incomplete, and a
    half-known supplier is still useful. `confidence` reflects how sure the
    extraction step is that this is a real, relevant company.
    """

    name: str
    category: str = "other"
    description: Optional[str] = None

    # Location / reach
    city: Optional[str] = None
    region: Optional[str] = None
    delivery_regions: list[str] = Field(default_factory=list)

    # Contacts / source
    website: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    source_url: Optional[str] = None

    # Commercial terms (the "extra" fields from the brief)
    min_order: Optional[str] = None
    price_note: Optional[str] = None
    certificates: list[str] = Field(default_factory=list)
    delivery_terms: Optional[str] = None

    notes: Optional[str] = None
    sources: list[SourceRef] = Field(default_factory=list)
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    # Short, LLM-written "why contact this one". On the base model so it survives
    # extraction → scoring (a provider may set it before the score is computed).
    reason: Optional[str] = None


class ScoredSupplier(Supplier):
    """A supplier enriched with a deterministic fit score."""

    score: int = 0  # 0..100
    score_breakdown: dict[str, int] = Field(default_factory=dict)


class SearchFilters(BaseModel):
    region: Optional[str] = None
    needs_certificates: bool = False
    max_min_order_units: Optional[int] = None  # soft preference, not a hard cut
    keyword: Optional[str] = None


class SearchRequest(BaseModel):
    category: str
    region: Optional[str] = None
    filters: SearchFilters = Field(default_factory=SearchFilters)
    lang: Literal["ru", "en"] = "ru"
    limit: int = Field(default=8, ge=1, le=20)


class SearchResponse(BaseModel):
    query_id: str
    category: str
    region: Optional[str]
    source: Literal["live", "cache", "seed"]  # how this result was produced
    summary: Optional[str] = None  # LLM "top picks & gaps" over the whole list
    suppliers: list[ScoredSupplier]
    warnings: list[str] = Field(default_factory=list)
