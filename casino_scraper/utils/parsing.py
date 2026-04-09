import re

BONUS_KW = re.compile(
    r"bonus|promo|welcome|deposit|free\s*spin|cashback|reload|re-?up", re.I
)
RATING_KW = re.compile(
    r"leaderboard|winner|rating|score|rank|top\s+\d|prize|place", re.I
)
VALUE_RE = [
    re.compile(r"(\d{1,3}%\s+(?:up\s+to\s+)?\$[\d,]+)", re.I),   # "250% up to $5,000"
    re.compile(r"(\d{1,3}%)", re.I),                               # "250%"
    re.compile(r"(\$[\d,]+)", re.I),                               # "$5,000"
    re.compile(r"(\d+\s*(?:free\s*spin|FS)s?)", re.I),            # "50 free spins"
]

JUNK_CLASSES = re.compile(
    r"footer|header|nav|menu|cookie|social|copyright|contact|tel:|phone|chat",
    re.I,
)


def extract_value(text: str) -> str:
    parts = []
    for pat in VALUE_RE:
        for m in pat.finditer(text):
            v = m.group(0).strip()
            if not any(v in p for p in parts):
                parts.append(v)
        if len(parts) >= 3:
            break
    return " | ".join(parts[:3]) if parts else "Check site"


def classify_bonus(text: str) -> str:
    t = text.lower()
    if any(k in t for k in ("welcome", "sign up", "first deposit", "new player")):
        return "welcome"
    if any(k in t for k in ("reload", "re-up", "redeposit")):
        return "reload"
    if any(k in t for k in ("free spin", " fs ", "freespin")):
        return "free_spin"
    if any(k in t for k in ("cashback", "money back", "refund")):
        return "cashback"
    return "promo"


def is_cf_page(html: str) -> bool:
    if len(html) < 8000:
        return True
    markers = [
        "just a moment", "checking your browser", "verifying you are human",
        "verify you are human", "cf-browser-verification", "turnstile",
    ]
    return sum(1 for m in markers if m in html.lower()) >= 2


def is_junk_element(el) -> bool:
    classes = " ".join(el.get("class", []))
    if JUNK_CLASSES.search(classes):
        return True
    parent = el.parent
    for _ in range(4):
        if parent is None:
            break
        p_classes = " ".join(parent.get("class", []) if hasattr(parent, "get") else [])
        p_id = parent.get("id", "") if hasattr(parent, "get") else ""
        if JUNK_CLASSES.search(p_classes) or JUNK_CLASSES.search(p_id):
            return True
        parent = parent.parent
    return False
