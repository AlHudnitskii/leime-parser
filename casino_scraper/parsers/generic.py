import re
from bs4 import BeautifulSoup

from casino_scraper.models import BonusItem, RatingItem
from casino_scraper.utils.parsing import (
    extract_value, classify_bonus, BONUS_KW, RATING_KW, is_junk_element
)


def parse_bonuses(html: str, site: str, url: str) -> list[BonusItem]:
    soup = BeautifulSoup(html, "lxml")
    items: list[BonusItem] = []
    seen: set[str] = set()

    for el in soup.find_all(["div", "section", "article", "li"]):
        if is_junk_element(el):
            continue

        text = el.get_text(" ", strip=True)
        if not (60 < len(text) < 3000):
            continue
        if not BONUS_KW.search(text):
            continue

        header = el.find(["h1", "h2", "h3", "h4", "h5", "strong", "b"])
        title = (header.get_text(" ", strip=True) if header else text[:100]).strip()[:150]
        key = re.sub(r"\s+", " ", title.lower())[:80]

        if key in seen or len(key) < 5:
            continue
        seen.add(key)

        items.append(BonusItem(
            site=site,
            title=title,
            description=text[:500],
            bonus_type=classify_bonus(text),
            value=extract_value(text),
            promo_code="",
            url=url,
        ))

    unique: list[BonusItem] = []
    for it in items:
        if not any(
            it.title != u.title and it.title in u.description
            for u in unique
        ):
            unique.append(it)
    return unique


def parse_ratings(html: str, site: str, url: str) -> list[RatingItem]:
    soup = BeautifulSoup(html, "lxml")
    items: list[RatingItem] = []

    for table in soup.find_all("table"):
        if is_junk_element(table):
            continue
        rows = table.find_all("tr")
        for i, row in enumerate(rows[1:], 1):
            cols = [c.get_text(" ", strip=True) for c in row.find_all(["td", "th"])]
            if len(cols) >= 2 and cols[0]:
                if re.search(r"tel:|mailto:|\(888\)|Login", cols[0]):
                    continue
                items.append(RatingItem(
                    site=site, rank=i,
                    player=cols[0][:100],
                    score=cols[-1][:50],
                    tournament="",
                    url=url,
                ))

    for el in soup.find_all(class_=re.compile(
        r"leader|leaderboard|rank|top-player|winner|podium|prize", re.I
    )):
        if is_junk_element(el):
            continue
        text = el.get_text(" ", strip=True)
        if 5 < len(text) < 200 and RATING_KW.search(text):
            if not re.search(r"tel:|mailto:|\(888\)|Login", text):
                items.append(RatingItem(
                    site=site, rank=len(items) + 1,
                    player=text[:100], score="",
                    tournament="", url=url,
                ))

    return items[:50]
