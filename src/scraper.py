"""Scrape the public Quotes to Scrape practice website."""
from __future__ import annotations

import time
from typing import Any
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com/"
HEADERS = {
    "User-Agent": "DataAnalystPortfolioDemo/1.0 (educational scraping project)"
}


def scrape_quotes(max_pages: int = 5, delay_seconds: float = 1.0) -> list[dict[str, Any]]:
    """Collect quote, author, tags, and source page from up to max_pages pages."""
    if max_pages < 1:
        raise ValueError("max_pages must be at least 1")

    session = requests.Session()
    session.headers.update(HEADERS)
    current_url = BASE_URL
    records: list[dict[str, Any]] = []

    for page_number in range(1, max_pages + 1):
        response = session.get(current_url, timeout=20)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        quote_cards = soup.select("div.quote")
        if not quote_cards:
            break

        for card in quote_cards:
            quote_el = card.select_one("span.text")
            author_el = card.select_one("small.author")
            tag_els = card.select("a.tag")

            if not quote_el or not author_el:
                continue

            records.append({
                "quote": quote_el.get_text(" ", strip=True),
                "author": author_el.get_text(" ", strip=True),
                "tags": ", ".join(tag.get_text(" ", strip=True) for tag in tag_els),
                "source_page": current_url,
            })

        next_link = soup.select_one("li.next a")
        if not next_link:
            break

        current_url = urljoin(current_url, next_link.get("href", ""))
        if page_number < max_pages:
            time.sleep(delay_seconds)

    return records
