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

SITES = {
    "PUBG Esports": "https://esports.pubgmobile.com/",
    "MLBB News": "https://m.mobilelegends.com/en/news",
    "MLBB Events": "https://m.mobilelegends.com/en/events"
}

SOURCES = {
    "PUBG X": "https://x.com/PUBGMOBILE",
    "MLBB X": "https://x.com/MobileLegendsOL"
}

RSS_SOURCES = [
    "https://www.reddit.com/r/PUBGMobile/.rss",
    "https://www.reddit.com/r/MobileLegendsGame/.rss"
]

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    text += f"\n\n🕒 {time_now}"

    requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": text
    })

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        CODE_FILE = "codes.json"

def load_codes():
    if os.path.exists(CODE_FILE):
        with open(CODE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def is_new_code(code):
    codes = load_codes()
    if code in codes:
        return False
    codes.append(code)
    with open(CODE_FILE, "w", encoding="utf-8") as f:
        json.dump(codes, f, ensure_ascii=False, indent=2)
    return True
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


def check_sites():
    old = load_data()
    new = {}

    message = "📰 PUBG + MLBB Yangiliklari\n\n"
    changed = False

    for name, url in SITES.items():
        try:
            html = get_page(url)
            title = get_title(html)

            new[name] = title

            if old.get(name) != title:
                changed = True
                message += f"📢 {name}\n"
                message += f"{title}\n"
                message += f"{url}\n\n"

        except Exception as e:
            message += f"❌ {name}\n{e}\n\n"

    if changed:
        send_message(message)
        save_data(new)
def check_codes():
    message = "🎁 Redeem kodlarni tekshirish\n\n"

    keywords = [
        "redeem",
        "redeem code",
        "gift code",
        "exchange code",
        "cdkey",
        "code",
        "gift",
        "reward",
        "free skin",
        "兑换码"
    ]

    for name, url in SOURCES.items():
        try:
            html = get_page(url).lower()

            found = False

            for word in keywords:
                if word.lower() in html:
                    message += f"✅ {name}\n"
                    message += f"🔎 Kalit so'z: {word}\n"
                    message += f"🌐 {url}\n\n"
                    found = True
                    break

            if not found:
                message += f"ℹ️ {name}\n"
                message += f"🌐 {url}\n"
                message += "Kod topilmadi.\n\n"

        except Exception as e:
            message += f"❌ {name}\n{e}\n\n"

    send_message(message)


def check_rss():
    message = "📰 RSS yangiliklari\n\n"

    keywords = [
        "redeem",
        "redeem code",
        "gift code",
        "exchange code",
        "cdkey"
    ]

    for url in RSS_SOURCES:
        try:
            feed = feedparser.parse(url)

            for post in feed.entries[:5]:
                text = (post.title + " " + post.link).lower()
                codes = re.findall(r"\b[A-Z0-9]{10,20}\b", post.title.upper())
                for word in keywords:
                   if word in text:
                    if codes:
                        if is_new_code(codes[0]):
                            message += "🎁 Yangi redeem kod topildi!\n"
                            message += f"🎫 Kod: {codes[0]}\n"
                            message += f"📰 {post.title}\n"
                            message += f"🔗 {post.link}\n\n"
                    else:
                        message += f"📰 {post.title}\n"
                    message += f"🔗 {post.link}\n\n"
                    break

        except Exception as e:
            message += f"❌ {url}\n{e}\n\n"

            send_message(message)
if __name__ == "__main__":
    try:
        check_sites()
    except Exception as e:
        send_message(f"❌ check_sites xatosi:\n{e}")

    try:
        check_codes()
    except Exception as e:
        send_message(f"❌ check_codes xatosi:\n{e}")

    try:
        check_rss()
    except Exception as e:
        send_message(f"❌ check_rss xatosi:\n{e}")
