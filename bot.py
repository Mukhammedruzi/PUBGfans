import os
import re
import json
import requests
import feedparser
from bs4 import BeautifulSoup
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

CONFIG_FILE = "config.json"
SOURCES_FILE = "sources.json"
KEYWORDS_FILE = "keywords.json"
CODES_FILE = "codes.json"
REDEEM_FILE = "redeem.json"
def load_json(filename, default):
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default
    return default


def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_config():
    return load_json(CONFIG_FILE, {})


def load_sources():
    return load_json(SOURCES_FILE, {})


def load_keywords():
    data = load_json(KEYWORDS_FILE, {})
    return data.get("keywords", [])

CONFIG = load_config()
SOURCES = load_sources()
KEYWORDS = load_keywords()

SITES = {
    item["name"]: item["url"]
    for item in SOURCES.get("websites", [])
}

RSS_SOURCES = SOURCES.get("rss", [])
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
def get_page(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (RedeemBot)"
    }

    response = requests.get(url, headers=headers, timeout=20)
    response.raise_for_status()
    return response.text


def get_title(html):
    soup = BeautifulSoup(html, "html.parser")

    if soup.title:
        return soup.title.get_text(strip=True)

    return "Sarlavha topilmadi"


def is_new_code(code):
    codes = load_json(CODES_FILE, [])

    if code in codes:
        return False

    codes.append(code)
    save_json(CODES_FILE, codes)

    return True


def find_codes(text):
    text = text.upper()

    patterns = [
        r"\b[A-Z0-9]{16}\b",
        r"\b[A-Z0-9]{15}\b",
        r"\bPUBG[A-Z0-9]{6,12}\b",
        r"\bMLBB[A-Z0-9]{6,12}\b",
    ]

    found = set()

    for pattern in patterns (
        found.update(re.findall(pattern, text))

    return sorted(found)
def check_sites():
    message = "📰 PUBG + MLBB Yangiliklari\n\n"

    for name, url in SITES.items():
        try:
            html = get_page(url)
            title = get_title(html)

            message += (
                f"📢 {name}\n"
                f"{title}\n"
                f"{url}\n\n"
            )

        except Exception as e:
            message += (
                f"❌ {name}\n"
                f"{e}\n\n"
            )

    if message != "📰 PUBG + MLBB Yangiliklari\n\n":
        send_message(message)
def check_codes():
    message = "🎁 Yangi redeem kodlar\n\n"

    for name, url in SITES.items():
        try:
            html = get_page(url)
            text = BeautifulSoup(html, "html.parser").get_text(" ")

            codes = find_codes(text)

            new_codes = []

            for code in codes:
                if is_new_code(code):
                    new_codes.append(code)

            if new_codes:
                message += f"📢 {name}\n"

                for code in new_codes:
                    message += f"🔑 {code}\n"

                message += f"🌐 {url}\n\n"

        except Exception as e:
            message += f"❌ {name}\n{e}\n\n"

    if message != "🎁 Yangi redeem kodlar\n\n":
        send_message(message)
def check_rss():
    for url in RSS_SOURCES:
        try:
            feed = feedparser.parse(url)

            for post in feed.entries[:5]:
                text = (
                    post.title + " " +
                    getattr(post, "summary", "")
                )

                codes = find_codes(text)

                if not codes:
                    continue

                for code in codes:
                    if is_new_code(code):
                        send_message(
                            f"🎁 Yangi redeem kod topildi!\n\n"
                            f"🔑 {code}\n"
                            f"📰 {post.title}\n"
                            f"🔗 {post.link}"
                        )

        except Exception as e:
            print(f"RSS xatosi: {e}")
import time


def main():
    send_message("🤖 Redeem Code Bot ishga tushdi!")

    while True:
        try:
            check_codes()
            check_rss()
            check_sites()

        except Exception as e:
            send_message(f"❌ Xatolik:\n{e}")

        time.sleep(CONFIG.get("check_interval", 900))


if __name__ == "__main__":
    main()
