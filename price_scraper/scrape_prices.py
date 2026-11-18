#!/usr/bin/env python3
"""Fetch public Cardmarket offers and completed eBay ES sales for configured targets."""

from __future__ import annotations

import json
import os
import re
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote_plus

from scrapling.fetchers import Fetcher

MAX_TARGETS = 30
MAX_OFFERS = 5
USER_AGENT = "ScalperLV-price-research/1.0 (public price pages)"


def parse_eur(value: str) -> float | None:
    if "€" not in value and "EUR" not in value.upper():
        return None
    match = re.search(r"\d[\d.,\s]*", value)
    if not match:
        return None
    number = match.group().replace(" ", "").replace("\xa0", "")
    if "," in number and "." in number:
        number = number.replace(".", "").replace(",", ".") if number.rfind(",") > number.rfind(".") else number.replace(",", "")
    elif "," in number:
        number = number.replace(",", ".")
    try:
        price = float(number)
        return price if price > 0 and price < 10_000_000 else None
    except ValueError:
        return None


def text(element, selector: str) -> str:
    return " ".join(part.strip() for part in element.css(f"{selector}::text").getall() if part.strip())


def median(values: list[float]) -> float | None:
    return round(statistics.median(values), 2) if values else None


def fetch(url: str):
    return Fetcher.get(
        url,
        timeout=25,
        headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml"},
    )


def scrape_target(target: dict) -> dict:
    result: dict = {"id": str(target.get("id", "")), "name": str(target.get("name", ""))}
    cardmarket_url = target.get("cardmarket_url")
    if cardmarket_url:
        try:
            page = fetch(cardmarket_url)
            offers = []
            for row in page.css("#table .article-row, #UserOffersTable .article-row, tr.article-row, .article-row"):
                price_text = text(row, ".price, [class*=price], [data-testid*=price]")
                price = parse_eur(price_text)
                if price:
                    offers.append(price)
            offers.sort()
            result["cardmarket"] = {
                "state": "available" if offers else "no_visible_offers",
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "offers_seen": len(offers),
                "lowest_eur": offers[0] if offers else None,
                "mean_lowest_eur": median(offers[:MAX_OFFERS]),
                "source_url": cardmarket_url,
            }
        except Exception as exc:  # retain other source results when one site fails
            result["cardmarket"] = {"state": "unavailable", "error": type(exc).__name__}

    ebay_query = target.get("ebay_query")
    if ebay_query:
        url = "https://www.ebay.es/sch/i.html?_nkw=" + quote_plus(str(ebay_query)) + "&_sop=13&LH_Sold=1&LH_Complete=1&LH_PrefLoc=3&_ipg=60"
        try:
            page = fetch(url)
            prices = []
            for row in page.css("li.s-item"):
                title = text(row, ".s-item__title")
                if not title or "shop on ebay" in title.lower():
                    continue
                price = parse_eur(text(row, ".s-item__price"))
                row_text = " ".join(row.css("::text").getall())
                if price and not re.search(r"best offer|mejor oferta|meilleure offre", row_text, re.I):
                    prices.append(price)
            prices.sort()
            result["ebay_sold"] = {
                "state": "available" if prices else "no_visible_sales",
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "sales_seen": len(prices),
                "median_eur": median(prices),
                "lowest_eur": prices[0] if prices else None,
                "highest_eur": prices[-1] if prices else None,
                "source_url": url,
                "note": "Solo importes visibles; las ofertas aceptadas pueden ocultar el precio final.",
            }
        except Exception as exc:
            result["ebay_sold"] = {"state": "unavailable", "error": type(exc).__name__}
    return result


def main() -> int:
    raw = os.environ.get("PRICE_TARGETS") or "[]"
    try:
        targets = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"PRICE_TARGETS no contiene JSON válido: {exc}", file=sys.stderr)
        return 2
    if not isinstance(targets, list) or len(targets) > MAX_TARGETS:
        print(f"PRICE_TARGETS debe ser una lista con máximo {MAX_TARGETS} productos", file=sys.stderr)
        return 2

    output = []
    for index, target in enumerate(targets):
        if not isinstance(target, dict) or not (target.get("cardmarket_url") or target.get("ebay_query")):
            continue
        output.append(scrape_target(target))
        if index < len(targets) - 1:
            time.sleep(3)  # be gentle to public sites

    destination = Path(os.environ.get("PRICE_OUTPUT", "price-results.json"))
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps({
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "products": output,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Resultados guardados: {len(output)} productos -> {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
