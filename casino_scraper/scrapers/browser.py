import asyncio
import os
import random
from typing import Optional
from urllib.parse import urlparse

from playwright.async_api import Browser, TimeoutError as PlaywrightTimeout

from casino_scraper.utils.parsing import is_cf_page
from casino_scraper.utils import captcha as captcha_solver


async def fetch_page(
    url: str,
    browser: Browser,
    cfg: dict,
    captcha_api_key: str = "",
) -> Optional[str]:
    domain = urlparse(url).netloc
    context = await browser.new_context(
        viewport={"width": 1920, "height": 1080},
        locale="en-US",
        timezone_id="America/New_York",
    )
    page = await context.new_page()

    try:
        print(f"{domain}")
        await page.goto(url, wait_until="domcontentloaded", timeout=45_000)
        await asyncio.sleep(3)

        html = await page.content()

        if not is_cf_page(html):
            print(f"Загружено ({len(html):,} chars)")

        elif cfg.get("needs_captcha") and cfg.get("turnstile_sitekey"):
            token = await captcha_solver.solve_turnstile(
                url, cfg["turnstile_sitekey"], captcha_api_key
            )
            if not token:
                return None

            await captcha_solver.inject_token(page, token)
            try:
                await page.wait_for_load_state("domcontentloaded", timeout=15_000)
            except PlaywrightTimeout:
                pass

            html = await page.content()
            if is_cf_page(html):
                print("CF не прошёл после токена")
                await _save_screenshot(page, domain)
                return None
            print(f"CF пройден с токеном ({len(html):,} chars)")

        else:
            for i in range(10):
                await asyncio.sleep(3)
                html = await page.content()
                if not is_cf_page(html):
                    print(f"CF прошёл за {(i+1)*3}s")
                    break
                print(f"CF challenge... {(i+1)*3}s")
            else:
                await _save_screenshot(page, domain)
                return None

        for _ in range(4):
            await page.mouse.wheel(0, random.randint(300, 700))
            await asyncio.sleep(0.7)

        selector = cfg.get("wait_selector", "h2")
        try:
            await page.wait_for_selector(selector, timeout=8_000)
        except PlaywrightTimeout:
            pass

        return await page.content()

    except Exception as e:
        print(f"Ошибка: {str(e)[:120]}")
        return None
    finally:
        await page.close()
        await context.close()


async def _save_screenshot(page, domain: str) -> None:
    os.makedirs("output", exist_ok=True)
    path = f"output/debug_{domain}.png"
    await page.screenshot(path=path, full_page=True)
    print(f"Скриншот → {path}")
