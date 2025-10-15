def trim_price(price_str):
    return price_str.rstrip('0').rstrip('.') if '.' in price_str else price_str
def format_price(price):
    if price >= 10:
        return f"{price:.2f}"
    elif price >= 1:
        return f"{price:.4f}"
    elif price >= 0.09:
        return f"{price:.4f}"
    else:
        return f"{price:.8f}"

import requests
import time
import json
from datetime import datetime
from telegram_utils import send_telegram_message

CONFIG_PATH = "config.json"

# Load config
with open(CONFIG_PATH, "r") as f:
    config = json.load(f)
COINS = config["coins"]
THRESHOLD = config["threshold_percent"]


BINANCE_ALL_PRICES_URL = "https://api.binance.com/api/v3/ticker/price"

def get_all_prices():
    resp = requests.get(BINANCE_ALL_PRICES_URL)
    data = resp.json()
    # Sadece takip edilen coinleri filtrele
    prices = {item["symbol"]: item["price"] for item in data if item["symbol"] in COINS}
    return prices

def main():
    last_prices = get_all_prices()
    print(f"Başlangıç fiyatları: {last_prices}")
    while True:
        time.sleep(5)
        new_prices = get_all_prices()
        for symbol in COINS:
            if symbol not in new_prices or symbol not in last_prices:
                continue
            new_price = new_prices[symbol]
            old_price = last_prices[symbol]
            try:
                new_price_float = float(new_price)
                old_price_float = float(old_price)
            except Exception:
                last_prices[symbol] = new_price
                continue
            if old_price_float == 0:
                last_prices[symbol] = new_price
                continue
            change = ((new_price_float - old_price_float) / old_price_float) * 100
            if abs(change) >= THRESHOLD:
                utc_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
                coin_name = symbol.replace('USDT', '/USDT')
                price = trim_price(new_price)  # gereksiz sıfırları ve noktayı kaldırıyoruz
                direction = '🟢⬆️' if change > 0 else '🔴⬇️'
                if change > 0:
                    mesaj = f"🚨 #{coin_name} Last Price: {price}\n🟢⬆️ Last 1 Minute: %{abs(change):.2f}\n⏰Time: {utc_time}"
                else:
                    mesaj = f"🚨 #{coin_name} Last Price: {price}\n🔴⬇️ Last 1 Minute: %{abs(change):.2f}\n⏰Time: {utc_time}"
                print(mesaj)
                send_telegram_message(mesaj)
            last_prices[symbol] = new_price

if __name__ == "__main__":
    main()
