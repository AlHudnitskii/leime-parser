import asyncio
import random
import time

from playwright.async_api import async_playwright

from casino_scraper.config import CDP_URL, CAPTCHA_API_KEY, TARGETS
from casino_scraper.models import BonusItem, RatingItem
from casino_scraper.scrapers.site_scraper import scrape_site
from casino_scraper.utils.storage import save_results


async def main() -> None:
    t0 = time.time()

    captcha_ready = bool(CAPTCHA_API_KEY and CAPTCHA_API_KEY != "ВАШ_КЛЮЧ_2CAPTCHA")

    print("=" * 60)
    print("Casino Scraper")
    print(f"2captcha: {'настроен' if captcha_ready else 'не настроен (stake/jackbit пропустят капчу)'}")
    print("=" * 60)

    all_bonuses: list[BonusItem] = []
    all_ratings: list[RatingItem] = []

    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp(CDP_URL)
            print(f"Chrome подключён на {CDP_URL}\n")
        except Exception:
            print(f"Chrome не найден на {CDP_URL}")
            print()
            print('Запустите Chrome:')
            print('  "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" ^')
            print("    --remote-debugging-port=9222 --user-data-dir=C:\\temp\\cf_profile")
            return

        for key, cfg in TARGETS.items():
            bonuses, ratings = await scrape_site(
                key, cfg, browser,
                captcha_api_key=CAPTCHA_API_KEY if captcha_ready else "",
            )
            all_bonuses.extend(bonuses)
            all_ratings.extend(ratings)
            await asyncio.sleep(random.uniform(4, 8))

    print()
    save_results(all_bonuses, all_ratings)
    print(f"\nВремя: {time.time() - t0:.1f}s | "
          f"Бонусов: {len(all_bonuses)} | Рейтингов: {len(all_ratings)}")


if __name__ == "__main__":
    asyncio.run(main())
