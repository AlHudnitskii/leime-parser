import os
import random
import asyncio
from urllib.parse import urlparse

from playwright.async_api import Browser

from casino_scraper.models import BonusItem, RatingItem
from casino_scraper.scrapers.browser import fetch_page
from casino_scraper.parsers.registry import get_parser


async def scrape_site(
    key: str,
    cfg: dict,
    browser: Browser,
    captcha_api_key: str = "",
) -> tuple[list[BonusItem], list[RatingItem]]:
    bonus_url = cfg["bonus_url"]
    rating_url = cfg.get("rating_url")
    domain = urlparse(bonus_url).netloc
    parser = get_parser(key)

    bonuses: list[BonusItem] = []
    ratings: list[RatingItem] = []

    print(f"\n[{key}]")

    html = await fetch_page(bonus_url, browser, cfg, captcha_api_key)
    if html:
        _save_debug_html(html, key, "bonuses")
        bonuses = parser.parse_bonuses(html, domain, bonus_url)
        inline_ratings = parser.parse_ratings(html, domain, bonus_url)
        ratings.extend(inline_ratings)
        print(f"bonuses: {len(bonuses)}, ratings on page: {len(inline_ratings)}")

    if rating_url and rating_url != bonus_url:
        await asyncio.sleep(random.uniform(3, 6))
        html_r = await fetch_page(rating_url, browser, cfg, captcha_api_key)
        if html_r:
            _save_debug_html(html_r, key, "ratings")
            extra = parser.parse_ratings(html_r, domain, rating_url)
            ratings.extend(extra)
            print(f"ratings from dedicated page: {len(extra)}")

    return bonuses, ratings


def _save_debug_html(html: str, key: str, suffix: str) -> None:
    os.makedirs("output/debug", exist_ok=True)
    path = f"output/debug/{key}_{suffix}.html"
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
