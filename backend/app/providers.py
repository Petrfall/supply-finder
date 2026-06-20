"""LLM provider abstraction.

Three implementations behind one interface:
  - AnthropicProvider: real web search + structured extraction (native web tool).
  - OpenAIProvider: OpenAI-compatible endpoint (e.g. an apinet.cloud proxy with
    gpt-4o). No built-in web search on most proxies, so it works over the seed
    candidate pool: the model filters, enriches, ranks, and writes a per-supplier
    reason — a live demo of the LLM pipeline with a widely-available key.
  - MockProvider: returns nothing live; the service falls back to cache/seed.

The split keeps the service runnable with no key (demo) while serving live
results when a key is set. Same provider pattern as the resume-scorer project.

Selection order in get_provider(): Anthropic key → OpenAI-compatible key → mock.
"""
from __future__ import annotations

import json
import os
from typing import Protocol

from .models import SearchRequest, Supplier
from .seed import seed_for

ANTHROPIC_MODEL = "claude-opus-4-8"


class Provider(Protocol):
    def is_live(self) -> bool: ...

    def find_suppliers(self, req: SearchRequest) -> list[Supplier]:
        """Return raw (un-scored) suppliers, or [] if unavailable."""
        ...


def _region(req: SearchRequest) -> str:
    return req.region or req.filters.region or ""


def _search_prompt(req: SearchRequest) -> str:
    lang_note = "Отвечай по-русски." if req.lang == "ru" else "Respond in English."
    region_clause = f" в регионе «{_region(req)}»" if _region(req) else ""
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
        import anthropic  # lazy import — package optional

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
            model=ANTHROPIC_MODEL,
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
            model=ANTHROPIC_MODEL,
            max_tokens=8000,
            messages=[
                {
                    "role": "user",
                    "content": (
                        "Извлеки поставщиков из текста ниже в структуру. "
                        "Не выдумывай данные: если поля нет — оставь пустым. "
                        "confidence — насколько ты уверен, что это реальная "
                        "релевантная компания (0..1).\n\n" + digest
                    ),
                }
            ],
            output_format=SupplierList,
        )
        parsed = resp.parsed_output
        return parsed.suppliers if parsed else []


class OpenAIProvider:
    """OpenAI-compatible endpoint (proxy such as apinet.cloud, model gpt-4o).

    Most OpenAI-compatible proxies don't expose a web-search tool, so we don't
    fake one. The model reasons over the seed candidate pool: it picks the
    relevant suppliers for the query, normalizes them, and writes a short
    `reason` per supplier. Output is constrained to JSON (response_format).
    """

    def __init__(self, api_key: str, base_url: str, model: str):
        from openai import OpenAI  # lazy import

        # Bounded timeout + one retry: if the upstream model is slow/overloaded,
        # fail fast so main.py falls back to the seed path instead of hanging.
        self._client = OpenAI(
            api_key=api_key, base_url=base_url, timeout=90.0, max_retries=1
        )
        self._model = model

    def is_live(self) -> bool:
        return True

    def find_suppliers(self, req: SearchRequest) -> list[Supplier]:
        candidates = seed_for(req.category, _region(req))
        by_name = {c.name: c for c in candidates}

        # Send the model a compact view (name + a few signals), not the whole
        # object. Smaller payload = faster + better format-following on a slow
        # proxy. We only ask the model to RANK and EXPLAIN; full supplier data
        # is merged back from our pool afterward, so contacts can't be altered.
        compact = [
            {
                "name": c.name,
                "category": c.category,
                "region": c.region,
                "certificates": c.certificates,
                "min_order": c.min_order,
            }
            for c in candidates
        ]

        sys = (
            "Ты ранжируешь поставщиков продуктов питания под запрос. "
            "Верни СТРОГО JSON-объект без пояснений вида:\n"
            '{"ranked": [{"name": "<точное имя из списка>", '
            '"reason": "<1 короткое предложение, почему связаться именно с ним>"}]}\n'
            "Порядок — от самого релевантного. Используй только имена из списка. "
            "Поле reason ОБЯЗАТЕЛЬНО для каждого. Пиши reason по-русски."
        )
        user = (
            f"Запрос: категория «{req.category}», регион «{_region(req)}».\n"
            f"Поставщики: {json.dumps(compact, ensure_ascii=False)}"
        )
        try:
            resp = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": sys},
                    {"role": "user", "content": user},
                ],
                response_format={"type": "json_object"},
                temperature=0.2,
            )
            data = json.loads(resp.choices[0].message.content or "{}")
        except Exception:
            return []  # any failure → fall back to seed path in main.py

        # Merge ranking+reason back onto the full supplier records from our pool.
        out: list[Supplier] = []
        for item in data.get("ranked", []):
            base = by_name.get((item or {}).get("name", ""))
            if not base:
                continue
            s = base.model_copy()
            s.reason = (item.get("reason") or "").strip() or None
            out.append(s)
        return out


def get_provider() -> Provider:
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if anthropic_key:
        try:
            return AnthropicProvider(anthropic_key)
        except Exception:
            pass

    openai_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if openai_key:
        base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").strip()
        model = os.environ.get("OPENAI_MODEL", "gpt-4o").strip()
        try:
            return OpenAIProvider(openai_key, base_url, model)
        except Exception:
            pass

    return MockProvider()
