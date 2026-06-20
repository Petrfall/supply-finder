"""LLM provider abstraction.

Two implementations behind one interface:
  - AnthropicProvider: real web search + structured extraction via the Anthropic API.
  - MockProvider: returns nothing live; the service falls back to cache/seed.

The split keeps the service runnable with no API key (the demo path) while the
same code path serves live results when ANTHROPIC_API_KEY is set. This mirrors
the provider pattern from the resume-scorer project.

Why a two-step pipeline (search, then extract) rather than one call:
the Anthropic web-search tool and structured output (output_config.format)
cannot be combined in a single request. So step 1 runs web search and lets the
model write a plain-text digest of the suppliers it found; step 2 is a separate
structured call that parses that digest into the Supplier schema. Code — not the
model — then scores and ranks.
"""
from __future__ import annotations

import os
from typing import Protocol

from .models import SearchRequest, Supplier

MODEL = "claude-opus-4-8"


class Provider(Protocol):
    def is_live(self) -> bool: ...

    def find_suppliers(self, req: SearchRequest) -> list[Supplier]:
        """Return raw (un-scored) suppliers, or [] if unavailable."""
        ...


def _search_prompt(req: SearchRequest) -> str:
    region = req.region or req.filters.region or ""
    lang_note = (
        "Отвечай по-русски." if req.lang == "ru" else "Respond in English."
    )
    region_clause = f" в регионе «{region}»" if region else ""
    return (
        f"Найди реальных поставщиков по категории «{req.category}»{region_clause} "
        f"(food-направление: ингредиенты, готовая продукция, упаковка и т.п.). "
        f"Для каждого поставщика собери: название, город/регион, сайт, контакты "
        f"(email/телефон), минимальный объём заказа, ориентир по цене, "
        f"сертификаты, условия доставки, регионы поставки. "
        f"Дай 6–10 поставщиков. Для каждого укажи источник (URL). {lang_note}"
    )


class MockProvider:
    """No live calls. Forces the service onto the cache/seed path."""

    def is_live(self) -> bool:
        return False

    def find_suppliers(self, req: SearchRequest) -> list[Supplier]:
        return []


class AnthropicProvider:
    def __init__(self, api_key: str):
        import anthropic  # imported lazily so the package is optional

        self._client = anthropic.Anthropic(api_key=api_key)

    def is_live(self) -> bool:
        return True

    def find_suppliers(self, req: SearchRequest) -> list[Supplier]:
        digest = self._web_search(req)
        if not digest.strip():
            return []
        return self._extract(digest, req)

    # Step 1 — web search → plain-text digest
    def _web_search(self, req: SearchRequest) -> str:
        resp = self._client.messages.create(
            model=MODEL,
            max_tokens=8000,
            thinking={"type": "adaptive"},
            tools=[{"type": "web_search_20260209", "name": "web_search"}],
            messages=[{"role": "user", "content": _search_prompt(req)}],
        )
        return "".join(
            b.text for b in resp.content if getattr(b, "type", None) == "text"
        )

    # Step 2 — structured extraction into Supplier[]
    def _extract(self, digest: str, req: SearchRequest) -> list[Supplier]:
        from pydantic import BaseModel

        class SupplierList(BaseModel):
            suppliers: list[Supplier]

        resp = self._client.messages.parse(
            model=MODEL,
            max_tokens=8000,
            messages=[
                {
                    "role": "user",
                    "content": (
                        "Извлеки поставщиков из текста ниже в структуру. "
                        "Не выдумывай данные: если поля нет — оставь пустым. "
                        "Поле confidence — насколько ты уверен, что это реальная "
                        "релевантная компания (0..1).\n\n" + digest
                    ),
                }
            ],
            output_format=SupplierList,
        )
        parsed = resp.parsed_output
        return parsed.suppliers if parsed else []


def get_provider() -> Provider:
    key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not key:
        return MockProvider()
    try:
        return AnthropicProvider(key)
    except Exception:
        # anthropic package missing or client init failed — degrade gracefully
        return MockProvider()
