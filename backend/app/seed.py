"""Seed dataset — realistic RU food suppliers.

Used as the demo fallback when there's no API key and the query isn't in the
cache. Hand-curated so the prototype always returns something sensible. These
are illustrative entries for demonstration, not a live directory.
"""
from __future__ import annotations

from .models import Supplier

SEED: list[Supplier] = [
    Supplier(
        name="АгроПродукт Урал",
        category="ingredients",
        description="Оптовые поставки муки, круп, сахара и растительных масел.",
        city="Екатеринбург",
        region="Свердловская область",
        delivery_regions=["Свердловская область", "УрФО", "Россия"],
        website="agroprodukt-ural.ru",
        email="sales@agroprodukt-ural.ru",
        phone="+7 (343) 200-11-22",
        source_url="https://agroprodukt-ural.ru",
        min_order="от 500 кг",
        price_note="мука в/с ~32 ₽/кг",
        certificates=["ГОСТ", "Декларация ЕАЭС"],
        delivery_terms="самовывоз или доставка по УрФО от 1 т",
        confidence=0.9,
    ),
    Supplier(
        name="СибХлеб Ингредиенты",
        category="ingredients",
        description="Хлебопекарные смеси, дрожжи, улучшители, закваски.",
        city="Новосибирск",
        region="Новосибирская область",
        delivery_regions=["СФО", "Россия"],
        website="sibhleb-ingr.ru",
        email="info@sibhleb-ingr.ru",
        phone="+7 (383) 311-44-55",
        source_url="https://sibhleb-ingr.ru",
        min_order="от 200 кг",
        price_note="по запросу",
        certificates=["ISO 22000", "ГОСТ"],
        delivery_terms="ТК по России, от 3–5 дней",
        confidence=0.85,
    ),
    Supplier(
        name="ПакЛайн",
        category="packaging",
        description="Пищевая упаковка: контейнеры, плёнка, крафт-пакеты, этикетка.",
        city="Москва",
        region="Москва",
        delivery_regions=["ЦФО", "Россия"],
        website="pakl-line.ru",
        email="order@pakl-line.ru",
        phone="+7 (495) 120-33-44",
        source_url="https://pakl-line.ru",
        min_order="от 1 короба",
        price_note="контейнер ПП 500 мл ~6 ₽/шт",
        certificates=["Сертификат пищевой безопасности"],
        delivery_terms="доставка по Москве и области, ТК по России",
        confidence=0.8,
    ),
    Supplier(
        name="МолКом Поставка",
        category="finished_products",
        description="Молочная продукция и сыры от региональных заводов.",
        city="Казань",
        region="Татарстан",
        delivery_regions=["ПФО", "Россия"],
        website="molkom-postavka.ru",
        email="opt@molkom-postavka.ru",
        phone="+7 (843) 250-66-77",
        source_url="https://molkom-postavka.ru",
        min_order="от 1 паллеты",
        price_note="по прайсу, обновляется еженедельно",
        certificates=["ГОСТ", "Меркурий/ВетИС"],
        delivery_terms="рефрижератор, по ПФО 1–2 дня",
        confidence=0.82,
    ),
    Supplier(
        name="ФрешОвощБаза",
        category="ingredients",
        description="Овощи и фрукты оптом, сезонные позиции, заморозка.",
        city="Краснодар",
        region="Краснодарский край",
        delivery_regions=["ЮФО", "ЦФО", "Россия"],
        website="freshovosch.ru",
        email="zakaz@freshovosch.ru",
        phone="+7 (861) 205-88-99",
        source_url="https://freshovosch.ru",
        min_order="от 300 кг",
        price_note="сезонная, по запросу",
        certificates=["Декларация ЕАЭС"],
        delivery_terms="доставка по ЮФО, отгрузка со склада",
        confidence=0.78,
    ),
    Supplier(
        name="ТаараЭкоПак",
        category="packaging",
        description="Эко-упаковка из крафта и сахарного тростника для HoReCa.",
        city="Санкт-Петербург",
        region="Санкт-Петербург",
        delivery_regions=["СЗФО", "Россия"],
        website="taara-ecopak.ru",
        email="hello@taara-ecopak.ru",
        phone="+7 (812) 240-12-34",
        source_url="https://taara-ecopak.ru",
        min_order="от 5 000 шт",
        price_note="крафт-стакан 300 мл ~7,5 ₽/шт",
        certificates=["FSC", "Сертификат пищевой безопасности"],
        delivery_terms="доставка по РФ, бесплатно от 30 000 ₽",
        confidence=0.8,
    ),
    Supplier(
        name="МясоТорг Опт",
        category="finished_products",
        description="Мясо и полуфабрикаты для общепита и переработки.",
        city="Челябинск",
        region="Челябинская область",
        delivery_regions=["УрФО", "Россия"],
        website="myasotorg-opt.ru",
        email="opt@myasotorg-opt.ru",
        phone="+7 (351) 270-55-66",
        source_url="https://myasotorg-opt.ru",
        min_order="от 1 паллеты",
        price_note="по прайсу",
        certificates=["ГОСТ", "Меркурий/ВетИС", "ХАССП"],
        delivery_terms="рефрижератор по УрФО, под заказ по РФ",
        confidence=0.83,
    ),
    Supplier(
        name="БакалеяПро",
        category="ingredients",
        description="Бакалея оптом: специи, сухофрукты, орехи, бобовые.",
        city="Ростов-на-Дону",
        region="Ростовская область",
        delivery_regions=["ЮФО", "ЦФО", "Россия"],
        website="bakaleya-pro.ru",
        email="sales@bakaleya-pro.ru",
        phone="+7 (863) 210-77-88",
        source_url="https://bakaleya-pro.ru",
        min_order="от 100 кг",
        price_note="по запросу, скидки от объёма",
        certificates=["Декларация ЕАЭС", "ГОСТ"],
        delivery_terms="ТК по России, самовывоз со склада",
        confidence=0.79,
    ),
]


def seed_for(category: str | None, region: str | None) -> list[Supplier]:
    """Filter the seed set by category/region for a believable demo result."""
    items = SEED
    if category:
        c = category.strip().lower()
        items = [
            s for s in items
            if c in s.category.lower() or c in (s.description or "").lower()
        ] or items  # fall back to all if the filter empties the list
    return items
