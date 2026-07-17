import os
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

DATA_FILE = "data.json"
REDEEM_DATA_FILE = "redeem_data.json"
REDEEM_URL = "https://www.pubgmobile.com/redeem/"
SITES = {
    
    "PUBG Esports": "https://esports.pubgmobile.com/",
    "MLBB News": "https://m.mobilelegends.com/en/news",
    "MLBB Events": "https://m.mobilelegends.com/en/events"
}
SOURCES = {
    "PUBG Facebook": "https://www.facebook.com/PUBGMOBILE",
    "PUBG X": "https://x.com/PUBGMOBILE",
    "MLBB Facebook": "https://www.facebook.com/MobileLegendsGame",
    "MLBB X": "https://x.com/MobileLegendsOL"
}
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

def get_page(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    r = requests.get(url, headers=headers, timeout=15)
    r.raise_for_status()
    return r.text
def get_title(html):
    soup = BeautifulSoup(html, "html.parser")

    if soup.title:
        return soup.title.text.strip()
    else:
        return "Sarlavha topilmadi"
def check_redeem():
    message = "🎁 PUBG Redeem kodlari\n\n"

    try:
        url = REDEEM_URL
        html = get_page(url)

        if "redeem" in html.lower():
            message += "✅ Redeem sahifasi ishlayapti."
        else:
            message += "⚠️ Redeem sahifasi tekshirildi."

    except Exception as e:
        message += f"❌ Xatolik: {e}"

    send_message(message)   
def check_sources():
    old = load_data()
    new = {}

    message = "📱 Ijtimoiy tarmoqlar\n\n"
    changed = False

    for name, url in SOURCES.items():
        try:
            html = get_page(url)
            title = get_title(html)

            new[name] = title

            if old.get(name) != title:
                changed = True
                message += f"{name}\n{title}\n{url}\n\n"

        except Exception as e:
            message += f"❌ Xatolik ({name}): {e}\n\n"

    if changed:
        send_message(message)
        save_data(new)  
def check_sites():
    old = load_data()
    new = {}

    message = "PUBG + MLBB Yangiliklari\n\n"
    changed = False

    for name, url in SITES.items():
        try:
            html = get_page(url)
            soup = BeautifulSoup(html, "html.parser")

            if soup.title:
                title = soup.title.text.strip()
            else:
                title = "Sarlavha topilmadi"
            new[name] = title

            if old.get(name) != title:
                changed = True
                message += f"{name}\n{title}\n{url}\n\n"

        except Exception as e:
            message += f"Xatolik ({name}): {e}\n\n"

    if changed:
        send_message(message)
        save_data(new)
        print("Yangi yangilik yuborildi.")
    else:
        print("Yangi yangilik topilmadi.")
def check_redeem():
    codes = [
        "PUBG2026",
        "PUBGMOBILE",
        "MLBB2026"
    ]

    message = "🎁 Redeem kodlarni tekshirish\n\n"

    for code in codes:
        message += f"• {code}\n"

    send_message(message)
if __name__ == "__main__":
    check_sites()
    check_redeem()
    check_sources()
