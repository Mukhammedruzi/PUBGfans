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
def load_config():
    return load_json("config.json", {})

def load_sources():
    return load_json("sources.json", {})

def load_keywords():
    data = load_json("keywords.json", {})
    return data.get("keywords", [])
CONFIG = load_config()
SOURCES = load_sources()

SITES = {
    item["name"]: item["url"]
    for item in SOURCES.get("websites", [])
}

RSS_SOURCES = SOURCES.get("rss", [])

KEYWORDS = load_keywords()
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
        r"\bMLBB[A-Z0-9]{4,16}\b",
        r"\bCDK[A-Z0-9]{4,16}\b",
        r"\b[A-Z]{3,6}-[A-Z0-9]{4,10}\b",
    ]

    found = set()

    text = text.upper()

    for pattern in patterns:
        for code in re.findall(pattern, text):
            found.add(code)

    return list(found)
def check_rss():
    message = "📰 RSS yangiliklari\n\n"

    for url in RSS_SOURCES:
        try:
            feed = feedparser.parse(url)

            for post in feed.entries[:5]:
                text = (
                    post.title + " " +
                    getattr(post, "summary", "") + " " +
                    post.link
                ).lower()

                if not any(word.lower() in text for word in KEYWORDS):
                    continue

                codes = find_codes(
                    post.title + " " +
                    getattr(post, "summary", "")
                )

                if codes:
                    for code in codes:
                        if is_new_code(code):
                            message += (
                                f"🎁 Yangi redeem kod topildi!\n"
                                f"🔑 {code}\n"
                                f"📰 {post.title}\n"
                                f"🔗 {post.link}\n\n"
                            )
                else:
                    message += (
                        f"📰 {post.title}\n"
                        f"🔗 {post.link}\n\n"
                    )

        except Exception as e:
            message += f"❌ RSS xatosi:\n{url}\n{e}\n\n"

    send_message(message)
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
def check_codes():
    message = "🎁 Redeem kodlarni tekshirish\n\n"

    for name, url in SITES.items():
        try:
            html = get_page(url)

            text = BeautifulSoup(html, "html.parser").get_text(" ")

            codes = find_codes(text)

            if not codes:
                continue

            new_codes = []

            for code in codes:
                if is_new_code(code):
                    new_codes.append(code)
            if new_codes:
                message += f"✅ {name}\n"

                for code in new_codes:
                    message += f"🎫 {code}\n"

                message += f"🌐 {url}\n\n"

        except Exception as e:
            message += f"❌ {name}\n"
            message += f"{e}\n\n"

    if message != "🎁 Redeem kodlarni tekshirish\n\n":
        send_message(message)
if message != "🎁 Redeem kodlarni tekshirish\n\n":
    send_message(message)

import time

def main():
    send_message("🤖 Bot ishga tushdi")

    try:
        check_codes()
        check_rss()
    except Exception as e:
        send_message(f"❌ Xatolik:\n{e}")

if __name__ == "__main__":
    main()
