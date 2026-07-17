import os
import json
import requests
from bs4 import BeautifulSoup

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

DATA_FILE = "data.json"

SITES = {
    "PUBG NEWS": "https://www.pubgmobile.com/en/news/",
    "PUBG Esports": "https://esports.pubgmobile.com/",
    "MLBB News": "https://m.mobilelegends.com/en/news",
    "MLBB Events": "https://m.mobilelegends.com/en/events"
}

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
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
def check_sites():
    old = load_data()
    new = {}

    message = "PUBG + MLBB Yangiliklari\n\n"
    changed = False

    for name, url in SITES.items():
        try:
            html = get_page(url)
            soup = BeautifulSoup(html, "html.parser")

            title = soup.title.text.strip() if soup.title else "Sarlavha topilmadi"

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

if __name__ == "__main__":
    check_sites()
