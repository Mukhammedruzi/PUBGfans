import requests

print("=== PUBG + MLBB News Bot ===")

sites = {
    "PUBG Mobile": "https://www.pubgmobile.com/news.shtml",
    "Mobile Legends": "https://m.mobilelegends.com/news"
}

headers = {
    "User-Agent": "Mozilla/5.0"
}

for game, url in sites.items():
    print(f"\nTekshirilmoqda: {game}")

    try:
        response = requests.get(url, headers=headers, timeout=15)

        if response.status_code == 200:
            print(f"✅ {game} sayti ochildi.")
            print("Sahifa hajmi:", len(response.text), "ta belgi")
        else:
            print(f"❌ Xatolik: {response.status_code}")

    except Exception as e:
        print("❌ Xatolik:", e)

print("\nTekshirish tugadi.")
