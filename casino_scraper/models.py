from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class BonusItem:
    site: str
    title: str
    description: str
    bonus_type: str   # welcome | reload | free_spin | cashback | promo
    value: str        # "250% | up to $5,000 | min $100"
    promo_code: str   # "CAS250" или ""
    url: str
    scraped_at: str = field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )


@dataclass
class RatingItem:
    site: str
    rank: int
    player: str
    score: str
    tournament: str   # название турнира
    url: str
    scraped_at: str = field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
