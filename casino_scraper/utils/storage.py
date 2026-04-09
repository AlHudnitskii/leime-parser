import csv
import os
from dataclasses import asdict
from datetime import datetime

from casino_scraper.models import BonusItem, RatingItem


def save_results(
    bonuses: list[BonusItem],
    ratings: list[RatingItem],
    output_dir: str = "output",
) -> tuple[str, str]:
    os.makedirs(output_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    b_path = _save_csv(bonuses, f"{output_dir}/bonuses_{ts}.csv", "бонусы")
    r_path = _save_csv(ratings, f"{output_dir}/ratings_{ts}.csv", "рейтинги")

    return b_path, r_path


def _save_csv(items: list, path: str, label: str) -> str:
    if not items:
        print(f"{label.capitalize()} не собраны")
        return ""

    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=asdict(items[0]).keys())
        writer.writeheader()
        writer.writerows([asdict(i) for i in items])

    print(f"{label.capitalize()} → {path} ({len(items)} строк)")
    return path
