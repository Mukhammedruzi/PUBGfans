import os
import re
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

CODES_FILE = "codes.json"
REDEEM_FILE = "redeem.json"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 Chrome/138.0 Safari/537.36"
    )
}

SOURCES = [
    {
        "name": "PUBG Mobile News",
        "game": "PUBG",
        "url": "https://www.pubgmobile.com/news.shtml"
    },
    {
        "name": "PUBG Mobile Events",
        "game": "PUBG",
        "url"
"https://www.pubgmobile.com"
    },
    {
         "name": "MLBB News",
         "game": "MLBB"
         "url":
"https://m.mobilelegends.com/en/news"
    }
]
# ===============================
# JSON bilan ishlash
# ===============================

def load_json(filename, default):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return default


def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


if not os.path.exists(CODES_FILE):
    save_json(CODES_FILE, [])

if not os.path.exists(REDEEM_FILE):
    save_json(REDEEM_FILE, [])


# ===============================
# Telegram
# ===============================

def send_message(text):
    if not BOT_TOKEN or not CHAT_ID:
        return

    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={
            "chat_id": CHAT_ID,
            "text": text
        },
        timeout=30
    )


# ===============================
# Saytni yuklash
# ===============================

def get_html(url):

    r = requests.get(
        url,
        headers=HEADERS,
        timeout=30
    )
    r.raise_for_status()

    return r.text
# ===============================
# Redeem kodlarni topish
# ===============================

PATTERNS = [
    r"\b[A-Z0-9]{10,16}\b",
    r"\bPUBG[A-Z0-9]{4,12}\b",
    r"\bMLBB[A-Z0-9]{4,12}\b"
]


def find_codes(text):

    text = text.upper()

    found = set()

    for pattern in PATTERNS:

        for code in re.findall(pattern, text):

            if any(c.isdigit() for c in code):
                found.add(code)

    return sorted(found)


# ===============================
# Yangi kodni tekshirish
# ===============================

def is_new_code(code):

    codes = load_json(CODES_FILE, [])

    if code in codes:
        return False

    codes.append(code)

    save_json(CODES_FILE, codes)
    return True

# ===============================
# redeem.json ga yozish
# ===============================

def save_redeem(code, source, game):

    data = load_json(REDEEM_FILE, [])

    data.insert(0, {
        "game": game,
        "code": code,
        "source": source,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    save_json(REDEEM_FILE, data)
# ===============================
# Saytlarni tekshirish
# ===============================

def check_sites():

    for site in SOURCES:

        try:

            html = get_html(site["url"])

            soup = BeautifulSoup(html, "html.parser")

            text = soup.get_text(" ")

            codes = find_codes(text)

            if not codes:
                continue

            for code in codes:

                if is_new_code(code):

                    save_redeem(
                        code,
                        site["name"],
                        site["game"]
                    )

                    send_message(
                        "🎁 YANGI REDEEM KOD TOPILDI!\n\n"
                        f"🎮 O'yin: {site['game']}\n"
                        f"🔑 Kod: {code}\n"
                        f"🌐 Manba: {site['name']}"
                    )

        except Exception as e:

            print(f"Xatolik ({site['name']}): {e}")
# ===============================
# Asosiy funksiya
# ===============================

def main():

    send_message("🤖 Redeem bot ishga tushdi.")

    check_sites()

    send_message("✅ Tekshirish yakunlandi.")


# ===============================
# Ishga tushirish
# ===============================

if __name__ == "__main__":

    try:

        main()

    except Exception as e:

        print(e)

        send_message(
            f"❌ Bot xatolik bilan to'xtadi.\n\n{e}"
        )
