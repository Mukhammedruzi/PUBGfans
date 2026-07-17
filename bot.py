import requests

print("Bot ishga tushdi!")

url = "https://www.google.com"
r = requests.get(url)

print("Status:", r.status_code)
