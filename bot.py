import requests
from bs4 import BeautifulSoup

print("=== PUBG + MLBB yangiliklar boti ===")

saytlar = {
    "PUBG Mobile": "https://www.pubgmobile.com/news.shtml",
    "Mobile Legends": "https://m.mobilelegends.com/news"
}

headers = {
    "User-Agent": "Mozilla/5.0"
}

for nom, url in saytlar.items():
    print(f"\nTekshirilmoqda: {nom}")

    try:
        javob = requests.get(url, headers=headers, timeout=15)

        if javob.status_code == 200:
            print("✅ Sayt ochildi")
            soup = BeautifulSoup(javob.text, "html.parser")
            print(f"Sahifa uzunligi: {len(javob.text)} ta belgi")
        else:
            print(f"❌ Xatolik: {javob.status_code}")

    except Exception as xato:
        print(f"❌ Xatolik: {xato}")

print("\n✅ Tekshirish tugadi.")
