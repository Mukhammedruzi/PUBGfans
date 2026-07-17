import os
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_message(text):
    if not BOT_TOKEN or not CHAT_ID:
        print("BOT_TOKEN yoki CHAT_ID topilmadi.")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": text
    })

def check_sites():
    sites = {
    "PUBG News": "https://www.pubgmobile.com/news.shtml",
    "PUBG Esports": "https://esports.pubgmobile.com/",
    "MLBB News": "https://m.mobilelegends.com/en/news",
    "MLBB Events": "https://m.mobilelegends.com/en/events"
    }
    result = "🎮 PUBG + MLBB Bot\n\n"

    for name, url in sites.items():
        try:
            r = requests.get(url, timeout=10)

            if r.status_code == 200:
                result += f"✅ {name} ishlayapti.\n"
            else:
                result += f"❌ {name} xato: {r.status_code}\n"

        except Exception as e:
            result += f"❌ {name}: {e}\n"

    send_message(result)
    print(result)

if __name__ == "__main__":
    check_sites()
