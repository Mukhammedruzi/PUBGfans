import requests

print("=== PUBG + MLBB Redeem Bot ===")

sources = [
    "https://www.pubgmobile.com/",
    "https://m.mobilelegends.com/"
]

for url in sources:
    try:
        r = requests.get(url, timeout=10)
        print(f"{url} -> {r.status_code}")
    except Exception as e:
        print(f"{url} -> Xatolik: {e}")

print("Tekshirish tugadi.")
