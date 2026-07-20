import os
import re
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import base64
GH_TOKEN = os.getenv("GH_TOKEN")
GITHUB_USER = "Mukhammedruzi"
GITHUB_REPO = "PUBGfans"
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

CODES_FILE = "codes.json"
REDEEM_FILE = "redeem.json"
LAST_NEWS_FILE = "last_news.json"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 Chrome/138.0 Safari/537.36"
    )
}
SOURCES = [

    # =========================
    # PUBG MOBILE
    # =========================

    {
        "name": "PUBG Mobile News",
        "game": "PUBG",
        "url": "https://www.pubgmobile.com/news.shtml"
    },

    {
        "name": "PUBG Mobile",
        "game": "PUBG",
        "url": "https://www.pubgmobile.com/"
    },

    {
        "name": "PUBG Mobile Security",
        "game": "PUBG",
        "url": "https://www.pubgmobile.com/security.shtml"
    },

    # =========================
    # MOBILE LEGENDS
    # =========================

    {
        "name": "MLBB News",
        "game": "MLBB",
        "url": "https://m.mobilelegends.com/en/news"
    },

    {
        "name": "MLBB Events",
        "game": "MLBB",
        "url": "https://m.mobilelegends.com/en/events"
    },

    {
        "name": "MLBB Home",
        "game": "MLBB",
        "url": "https://m.mobilelegends.com/"
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

if not os.path.exists(LAST_NEWS_FILE):
    save_json(LAST_NEWS_FILE, {})
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
# Oxirgi yangilikni saqlash
# ===============================

def get_last_news(site_name):

    data = load_json(LAST_NEWS_FILE, {})

    return data.get(site_name)


def set_last_news(site_name, value):

    data = load_json(LAST_NEWS_FILE, {})

    data[site_name] = value

    save_json(LAST_NEWS_FILE, data)
# ===============================
# Saytlarni tekshirish
# ===============================
# ===============================
# GitHub faylini yangilash
# ===============================

def github_headers():
    return {
        "Authorization": f"token {GH_TOKEN}",
        "Accept": "application/vnd.github+json"
    }


def update_github_file(path, content, message):

    url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/{path}"

    r = requests.get(url, headers=github_headers(), timeout=30)
    r.raise_for_status()

    data = r.json()

    sha = data["sha"]

    encoded = base64.b64encode(
        content.encode("utf-8")
    ).decode()

    requests.put(
        url,
        headers=github_headers(),
        json={
            "message": message,
            "content": encoded,
            "sha": sha
        },
        timeout=30
    ).raise_for_status()
# ===============================
# redeem.html yaratish
# ===============================

def build_redeem_page():

    data = load_json(REDEEM_FILE, [])

    html = """<!DOCTYPE html>
<html lang="uz">
<head>
<meta charset="UTF-8">
<title>Redeem Codes</title>
</head>
<body>

<h1>🎁 Eng so'nggi Redeem Kodlar</h1>

<table border="1" cellpadding="8">
<tr>
<th>O'yin</th>
<th>Kod</th>
<th>Manba</th>
<th>Vaqt</th>
</tr>
"""

    for item in data:

        html += f"""
<tr>
<td>{item['game']}</td>
<td>{item['code']}</td>
<td>{item['source']}</td>
<td>{item['time']}</td>
</tr>
"""

    html += """
</table>

</body>
</html>
"""

    return html
def check_sites():

    for site in SOURCES:

        try:

            html = get_html(site["url"])
            soup = BeautifulSoup(html, "html.parser")

            title = soup.title.text.strip() if soup.title else site["name"]

            last = get_last_news(site["name"])
 
            if title != last:

                   set_last_news(site["name"], title)

                send_message(
                   f"📰 YANGI YANGILIK!\n\n"
                   f"🎮 {site['game']}\n"
                   f"📢 {title}\n"
                   f"🔗 {site['url']}"
            )

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
                    html = build_redeem_page()
                    
                    update_github_file(
                             "redeem.html",
                             html,
                             f"Redeem update: {code}"
                    )
                    
                    send_message("🌐 Sayt avtomatik yangilandi.")
        except Exception as e:
            print(f"Xatolik ({site['name']}): {e}")
# ===============================
# Asosiy funksiya
# ===============================

def main():

    send_message(
        "🤖 Redeem Bot ishga tushdi.\n"
        "👀 Yangi redeem kodlar kuzatilmoqda..."
    )

    check_sites()

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
