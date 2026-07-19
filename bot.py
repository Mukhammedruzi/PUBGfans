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

SITES = {
    "PUBG": "https://www.pubgmobile.com/news.shtml",
    "MLBB": "https://m.mobilelegends.com/en/news"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

if not os.path.exists(CODES_FILE):
    with open(CODES_FILE, "w", encoding="utf-8") as f:
        json.dump([], f)

if not os.path.exists(REDEEM_FILE):
    with open(REDEEM_FILE, "w", encoding="utf-8") as f:
        json.dump([], f)


def load_json(file):
    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def send_message(text):
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={
            "chat_id": CHAT_ID,
            "text": text
        },
        timeout=20
    )


def find_codes(text):
    pattern = r"\b(?=.*[A-Z])(?=.*\d)[A-Z0-9]{10,16}\b"
    return sorted(set(re.findall(pattern, text.upper())))
def get_page(url):
    response = requests.get(url, headers=HEADERS, timeout=20)
    response.raise_for_status()
    return response.text


def is_new_code(code):
    codes = load_json(CODES_FILE)

    if code in codes:
        return False

    codes.append(code)
    save_json(CODES_FILE, codes)
    return True


def save_redeem(code, source):
    data = load_json(REDEEM_FILE)

    data.append({
        "code": code,
        "source": source,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    save_json(REDEEM_FILE, data)


def check_sites():
    for name, url in SITES.items():
        try:
            html = get_page(url)

            text = BeautifulSoup(
                html,
                "html.parser"
            ).get_text(" ")

            codes = find_codes(text)

            for code in
def update_website():
    data = load_json(REDEEM_FILE)

    data = sorted(
        data,
        key=lambda x: x["time"],
        reverse=True
    )

    save_json(REDEEM_FILE, data)


def clean_old_codes():
    data = load_json(REDEEM_FILE)

    unique = []
    seen = set()

    for item in data:
        if item["code"] not in seen:
            unique.append(item)
            seen.add(item["code"])

    save_json(REDEEM_FILE, unique)


def run_bot():
    send_message("🤖 Redeem Code Bot ishga tushdi!")

    check_sites()

    clean_old_codes()

    update_website()

    send_message("✅ Tekshirish yakunlandi.")
def main():
    try:
        run_bot()
    except Exception as e:
        send_message(
            f"❌ Bot xatolikka uchradi!\n\n{e}"
        )


if __name__ == "__main__":
    main()
