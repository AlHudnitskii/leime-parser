CDP_URL = "http://localhost:9222"

# API ключ 2captcha — взять на https://2captcha.com → Dashboard
# Нужен только для stake.us и jackbit.co
CAPTCHA_API_KEY = "ВАШ_КЛЮЧ_2CAPTCHA"

TARGETS: dict = {
    "betus.com.pa": {
        "bonus_url":         "https://www.betus.com.pa/online-casino/promotions/",
        "rating_url":        "https://www.betus.com.pa/online-casino/tournaments/",
        "wait_selector":     "#daily-promotions, #signup-bonus, h2",
        "needs_captcha":     False,
        "turnstile_sitekey": "",
    },
    "stake.us": {
        "bonus_url":         "https://stake.us/promotions",
        "rating_url":        "https://stake.us/promotions",
        "wait_selector":     "h1, h2, [class*='promo']",
        "needs_captcha":     True,
        "turnstile_sitekey": "0x4AAAAAAAC3DHQFLr1GjB8h",
    },
    "jackbit.co": {
        "bonus_url":         "https://jackbit.co/promotions",
        "rating_url":        "https://jackbit.co/casino/tournaments",
        "wait_selector":     "h2, [class*='card'], [class*='promo']",
        "needs_captcha":     True,
        "turnstile_sitekey": "0x4AAAAAAADnPIDROrmt1Wwj",
    },
}
