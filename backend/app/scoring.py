"""Deterministic fit-scoring.

The score is computed in plain Python from explicit weighted signals, NOT asked
from the model. That keeps the ranking auditable: every point is traceable to a
rule, and the same supplier+query always scores the same. The LLM only writes
the human-readable `reason` afterwards.
"""
from __future__ import annotations

from .models import ScoredSupplier, SearchRequest, Supplier

# Each signal contributes up to `max` points. Weights are intentionally simple
# and visible — tweak here, not in a prompt.
WEIGHTS = {
    "region_match": 30,     # supplier reaches the requested region
    "category_match": 15,   # category lines up with the request
    "has_contacts": 15,     # there is a way to actually reach them
    "certificates": 15,     # certs present (and required, if the user asked)
    "min_order": 10,        # MOQ is known (and within preference, if given)
    "price_known": 8,       # some price signal exists
    "delivery_terms": 7,    # delivery terms are spelled out
}


def _region_match(s: Supplier, region: str | None) -> int:
    if not region:
        return WEIGHTS["region_match"]  # no preference → don't penalize anyone
    region_l = region.strip().lower()

    # Direct hit: the requested place appears in the supplier's location or
    # delivery regions. A city the user typed (e.g. "Зеленокумск") sits *inside*
    # a region ("Ставропольский край"), so we also scan the free-text delivery
    # terms and description, where "доставка в <город>" usually lives.
    direct = [s.region, s.city, *s.delivery_regions]
    for h in direct:
        if h and region_l in h.lower():
            return WEIGHTS["region_match"]

    text = f"{s.delivery_terms or ''} {s.description or ''}".lower()
    if region_l in text:
        # covered via delivery, not the home base → strong but not full
        return int(WEIGHTS["region_match"] * 0.8)

    # "delivers across Russia" style note still counts, partially
    if any(h and ("росс" in h.lower() or "russia" in h.lower()) for h in direct):
        return int(WEIGHTS["region_match"] * 0.6)
    return 0


def _category_match(s: Supplier, category: str) -> int:
    if not category:
        return 0
    c = category.strip().lower()
    fields = [s.category, s.description or "", s.name]
    return WEIGHTS["category_match"] if any(c in f.lower() for f in fields) else 0


def score_supplier(s: Supplier, req: SearchRequest) -> ScoredSupplier:
    b: dict[str, int] = {}

    b["region_match"] = _region_match(s, req.region or req.filters.region)
    b["category_match"] = _category_match(s, req.category)
    b["has_contacts"] = (
        WEIGHTS["has_contacts"] if (s.email or s.phone or s.website) else 0
    )

    if s.certificates:
        b["certificates"] = WEIGHTS["certificates"]
    elif req.filters.needs_certificates:
        b["certificates"] = 0  # required but absent → no points
    else:
        b["certificates"] = int(WEIGHTS["certificates"] * 0.4)  # neutral-ish

    b["min_order"] = WEIGHTS["min_order"] if s.min_order else 0
    b["price_known"] = WEIGHTS["price_known"] if s.price_note else 0
    b["delivery_terms"] = WEIGHTS["delivery_terms"] if s.delivery_terms else 0

    raw = sum(b.values())
    # Confidence from extraction gently scales the score so shaky entries sink.
    score = int(round(raw * (0.7 + 0.3 * max(0.0, min(1.0, s.confidence)))))
    score = max(0, min(100, score))

    return ScoredSupplier(**s.model_dump(), score=score, score_breakdown=b)


def score_and_rank(
    suppliers: list[Supplier], req: SearchRequest
) -> list[ScoredSupplier]:
    scored = [score_supplier(s, req) for s in suppliers]
    scored.sort(key=lambda x: x.score, reverse=True)
    return scored
