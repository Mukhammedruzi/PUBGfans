import os
import re
import json
import requests
import feedparser
from bs4 import BeautifulSoup
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

DATA_FILE = "data.json"
CODES_FILE = "codes.json"

SITES = {
    "PUBG Esports": "https://esports.pubgmobile.com/",
    "MLBB News": "https://m.mobilelegends.com/en/news",
    "MLBB Events": "https://m.mobilelegends.com/en/events"
}

RSS_SOURCES = [
    "https://www.reddit.com/r/PUBGMobile/.rss",
    "https://www.reddit.com/r/MobileLegendsGame/.rss"
]

KEYWORDS = [
    "redeem",
    "redeem code",
    "gift code",
    "exchange code",
    "cdkey",
    "gift",
    "reward",
    "coupon",
    "兑换码"
]


def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    requests.post(
        url,
        json={
            "chat_id": CHAT_ID,
            "text": f"{text}\n\n🕒 {now}"
        },
        timeout=20
    )
def load_json(filename, default):
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return default
    return default


def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_page(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    r = requests.get(url, headers=headers, timeout=20)
    r.raise_for_status()
    return r.text


def get_title(html):
    soup = BeautifulSoup(html, "html.parser")

    if soup.title:
        return soup.title.text.strip()

    return "Sarlavha topilmadi"


def find_codes(text):
    patterns = [
        r"\b[A-Z0-9]{10,20}\b",
        r"\bPUBG[A-Z0-9]{4,16}\b",
        r"\bMLBB[A-Z0-9]{4,16}\b"
    ]

    found = set()

    text = text.upper()

    for pattern in patterns:
        for code in re.findall(pattern, text):
            found.add(code)

    return list(found)
def is_new_code(code):
    codes = load_json(CODES_FILE, [])

    if code in codes:
        return False

    codes.append(code)
    save_json(CODES_FILE, codes)

    return True


def check_sites():
    message = "📰 PUBG + MLBB Yangiliklari\n\n"

    for name, url in SITES.items():
        try:
            html = get_page(url)
            title = get_title(html)

            message += f"📢 {name}\n"
            message += f"{title}\n"
            message += f"{url}\n\n"

        except Exception as e:
            message += f"❌ {name}\n{e}\n\n"

    send_message(message)
