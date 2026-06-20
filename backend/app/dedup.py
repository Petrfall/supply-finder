"""De-duplicate extracted suppliers.

Web search surfaces the same company through several pages. We collapse by
website domain first (strongest signal), then by a normalized name. When two
records merge, we keep the more complete one and union their fields.
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from .models import Supplier


def _domain(url: str | None) -> str | None:
    if not url:
        return None
    try:
        host = urlparse(url if "//" in url else f"//{url}").netloc.lower()
    except ValueError:
        return None
    return host[4:] if host.startswith("www.") else host or None


def _norm_name(name: str) -> str:
    n = name.lower()
    n = re.sub(r'["«»“”\'`]', "", n)
    n = re.sub(r"\b(ооо|оао|зао|ип|llc|ltd|inc|gmbh|co)\b", "", n)
    return re.sub(r"\s+", " ", n).strip()


def _completeness(s: Supplier) -> int:
    fields = [
        s.website, s.email, s.phone, s.min_order, s.price_note,
        s.delivery_terms, s.region, s.description,
    ]
    return sum(1 for f in fields if f) + len(s.certificates) + len(s.delivery_regions)


def _merge(a: Supplier, b: Supplier) -> Supplier:
    """Keep the richer record, fill its gaps from the other."""
    primary, other = (a, b) if _completeness(a) >= _completeness(b) else (b, a)
    data = primary.model_dump()
    for field in ("description", "city", "region", "website", "email", "phone",
                  "source_url", "min_order", "price_note", "delivery_terms", "notes"):
        if not data.get(field) and getattr(other, field):
            data[field] = getattr(other, field)
    data["certificates"] = sorted(set(primary.certificates) | set(other.certificates))
    data["delivery_regions"] = sorted(
        set(primary.delivery_regions) | set(other.delivery_regions)
    )
    data["sources"] = primary.sources + other.sources
    data["confidence"] = max(primary.confidence, other.confidence)
    return Supplier(**data)


def dedupe(suppliers: list[Supplier]) -> list[Supplier]:
    by_key: dict[str, Supplier] = {}
    for s in suppliers:
        key = _domain(s.website) or _domain(s.source_url) or _norm_name(s.name)
        if not key:
            continue
        by_key[key] = _merge(by_key[key], s) if key in by_key else s
    return list(by_key.values())
