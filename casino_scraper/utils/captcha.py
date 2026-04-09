import asyncio
import json
import urllib.request
import urllib.parse
from typing import Optional


def _http_get(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=10) as r:
        return json.loads(r.read().decode())


async def solve_turnstile(
    page_url: str,
    sitekey: str,
    api_key: str,
) -> Optional[str]:
    if not api_key:
        print("[captcha] API ключ не задан")
        return None

    print("[captcha] Отправляем Turnstile в 2captcha...")

    params = urllib.parse.urlencode({
        "key": api_key,
        "method": "turnstile",
        "sitekey": sitekey,
        "pageurl": page_url,
        "json": 1,
    })

    try:
        resp = _http_get(f"https://2captcha.com/in.php?{params}")
    except Exception as e:
        print(f"[captcha] Ошибка отправки: {e}")
        return None

    if resp.get("status") != 1:
        print(f"[captcha] Ошибка 2captcha: {resp}")
        return None

    task_id = resp["request"]
    print(f"[captcha] Task {task_id}, ждём решения...")

    for attempt in range(24):   # до 120 секунд
        await asyncio.sleep(5)
        try:
            result = _http_get(
                f"https://2captcha.com/res.php"
                f"?key={api_key}&action=get&id={task_id}&json=1"
            )
        except Exception as e:
            print(f"[captcha] Ошибка поллинга: {e}")
            continue

        if result.get("status") == 1:
            print(f"[captcha] Решено за ~{(attempt+1)*5}s")
            return result["request"]

        if result.get("request") != "CAPCHA_NOT_READY":
            print(f"[captcha] Ошибка: {result}")
            return None

    print("[captcha] Timeout: не решено за 120s")
    return None


async def inject_token(page, token: str) -> None:
    await page.evaluate("""
        (token) => {
            const el = document.querySelector('[name="cf-turnstile-response"]');
            if (el) el.value = token;
            for (const cb of ['tsCallback', 'turnstileCallback', 'cfCallback']) {
                if (typeof window[cb] === 'function') { window[cb](token); break; }
            }
        }
    """, token)
    await asyncio.sleep(2)
