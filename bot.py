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

import os

if not os.path.exists(CODES_FILE):
    with open(CODES_FILE, "w") as f:
        f.write("[]")
        
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
    import re

    text = text.upper()

    patterns = [
        r"\b[A-Z0-9]{10,16}\b",
        r"\bPUBG[A-Z0-9]{4,12}\b",
        r"\bMLBB[A-Z0-9]{4,12}\b",
    ]

    found = set()

    for pattern in patterns:
        for code in re.findall(pattern, text):
            if any(ch.isdigit() for ch in code):
                found.add(code)

    return sorted(found)
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

            if not feed.entries:
                continue

            post = feed.entries[0]  
            post_id = post.link
            if not is_new_code(post_id):
               continue  
            text = (
                post.title + " " +
                getattr(post, "summary", "")
            )

            codes = list(set(find_codes(text)))

            for code in codes:
                if is_new_code(code):
                    send_message(
                        f"🎁 YANGI REDEEM KOD!\n\n"
                        f"🔑 {code}"
                    )

        except Exception as e:
            print(f"RSS xatosi: {e}")
import time


def main():
    send_message("🤖 Redeem Code Bot ishga tushdi!")
    
    try:
        check_codes()
        check_rss()
        check_sites()

    except Exception as e:
            send_message(f"❌ Xatolik:\n{e}")
if __name__ == "__main__":
    main()
