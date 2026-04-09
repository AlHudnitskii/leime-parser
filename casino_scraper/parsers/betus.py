import re
from bs4 import BeautifulSoup, Tag

from casino_scraper.models import BonusItem, RatingItem
from casino_scraper.utils.parsing import extract_value, classify_bonus


def parse_bonuses(html: str, site: str, url: str) -> list[BonusItem]:
    soup = BeautifulSoup(html, "lxml")
    items: list[BonusItem] = []
    seen: set[str] = set()

    daily = soup.find(id="daily-promotions")
    if daily:
        for card in daily.find_all("div", class_=re.compile(r"place-content-between")):
            title_el = card.find(
                "div", class_=re.compile(r"font-extrabold")
            )
            if not title_el:
                continue
            title = title_el.get_text(strip=True)
            if not title or title.lower() in seen:
                continue
            seen.add(title.lower())

            parent = card.parent.parent if card.parent else card
            full_text = parent.get_text(" ", strip=True) if parent else title

            items.append(BonusItem(
                site=site,
                title=title,
                description=title,
                bonus_type=classify_bonus(title),
                value=extract_value(full_text),
                promo_code="",
                url=url,
            ))

    signup = soup.find(id="signup-bonus")
    if signup:
        for btn in signup.find_all("button", onclick=re.compile(r"promoDeposit")):
            promo_match = re.search(r"promoDeposit\('([^']+)'\)", btn.get("onclick", ""))
            promo_code = promo_match.group(1).strip() if promo_match else ""

            card = btn.parent
            for _ in range(6):
                if card is None:
                    break
                title_el = card.find("a", class_=re.compile(r"font-extrabold"))
                if title_el:
                    break
                card = card.parent

            if not card or not title_el:
                continue

            title = title_el.get_text(strip=True)
            if not title or title.lower() in seen:
                continue
            seen.add(title.lower())

            conditions = [
                li.get_text(strip=True)
                for li in card.find_all("li")
                if li.get_text(strip=True)
            ]

            desc_parts = conditions.copy()
            if promo_code:
                desc_parts.append(f"Promo code: {promo_code}")
            description = " | ".join(desc_parts) if desc_parts else title

            value_text = title + " " + " ".join(conditions)
            value = extract_value(value_text)

            items.append(BonusItem(
                site=site,
                title=title,
                description=description[:600],
                bonus_type=classify_bonus(title),
                value=value,
                promo_code=promo_code,
                url=url,
            ))

    return items


def parse_ratings(html: str, site: str, url: str) -> list[RatingItem]:
    soup = BeautifulSoup(html, "lxml")
    items: list[RatingItem] = []

    tournament_name = ""
    h1 = soup.find("h1")
    if h1:
        tournament_name = h1.get_text(strip=True)

    for table in soup.find_all("table"):
        parent_id = ""
        p = table.parent
        for _ in range(5):
            if p is None:
                break
            parent_id += " ".join(p.get("class", []) if hasattr(p, "get") else [])
            parent_id += p.get("id", "") if hasattr(p, "get") else ""
            p = p.parent
        if re.search(r"footer|nav|menu|sidebar", parent_id, re.I):
            continue

        rows = table.find_all("tr")
        if len(rows) < 2:
            continue

        headers = [th.get_text(strip=True) for th in rows[0].find_all(["th", "td"])]

        for i, row in enumerate(rows[1:], 1):
            cols = [td.get_text(" ", strip=True) for td in row.find_all(["td", "th"])]
            if len(cols) < 2:
                continue
            player = cols[0]
            score  = cols[-1] if len(cols) > 1 else ""

            if re.search(r"\d{3}[-.\s]\d{3}|\@|Login|Register|FAQ", player):
                continue

            items.append(RatingItem(
                site=site,
                rank=i,
                player=player[:100],
                score=score[:50],
                tournament=tournament_name,
                url=url,
            ))

    if not items:
        place_re = re.compile(r"^(\d+)(?:st|nd|rd|th)?[\.\s]+(.+)", re.I)
        prize_re = re.compile(r"\$[\d,]+|[\d,]+\s*(?:points?|pts?|credits?)", re.I)

        for el in soup.find_all(["li", "div", "p", "span"]):
            text = el.get_text(" ", strip=True)
            if re.search(r"tel:|mailto:|Login|Register|\(888\)", text):
                continue
            m = place_re.match(text)
            if m and len(text) < 200:
                prize_m = prize_re.search(text)
                items.append(RatingItem(
                    site=site,
                    rank=int(m.group(1)),
                    player=m.group(2)[:100].strip(),
                    score=prize_m.group(0) if prize_m else "",
                    tournament=tournament_name,
                    url=url,
                ))

    seen: set[str] = set()
    unique: list[RatingItem] = []
    for it in items:
        key = f"{it.rank}:{it.player.lower()[:40]}"
        if key not in seen:
            seen.add(key)
            unique.append(it)

    return unique[:100]
