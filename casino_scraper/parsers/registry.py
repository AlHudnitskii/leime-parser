from casino_scraper.parsers import betus, generic

REGISTRY = {
    "betus.com.pa": betus,
    "stake.us": generic,
    "jackbit.co": generic,
}


def get_parser(site_key: str):
    return REGISTRY.get(site_key, generic)
