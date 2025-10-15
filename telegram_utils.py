import requests
import json

def load_telegram_credentials(path="telegram_credentials.json"):
    with open(path, "r") as f:
        creds = json.load(f)
    return creds

def send_telegram_message(message):
    creds = load_telegram_credentials()
    token = creds["bot_token"]
    chat_id = creds["chat_id"]
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    resp = requests.post(url, data=payload)
    print(f"Telegram mesajı gönderildi: {resp.status_code}")

# Kullanım örneği:
# send_telegram_message("BTC %3 yükseldi!")
