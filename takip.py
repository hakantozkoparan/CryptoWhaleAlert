import requests
import time
import json
from datetime import datetime
from telegram_utils import send_telegram_message

CONFIG_PATH = "config.json"

with open(CONFIG_PATH, "r") as f:
    config = json.load(f)

COINS = config["coins"]
THRESHOLD = config["threshold_percent"]

BINANCE_ALL_PRICES_URL = "https://api.binance.com/api/v3/ticker/price"

def trim_price(price_str):
    """Gereksiz sıfırları ve noktayı kaldır."""
    return price_str.rstrip('0').rstrip('.') if '.' in price_str else price_str

def get_all_prices():
    """Binance'ten fiyatları al (sadece takip edilen coinler)."""
    resp = requests.get(BINANCE_ALL_PRICES_URL)
    data = resp.json()
    prices = {item["symbol"]: item["price"] for item in data if item["symbol"] in COINS}
    return prices

def main():
    price_history = {coin: [] for coin in COINS}  # coin -> [(timestamp, price)]
    print("Fiyat değişimi takibi başlatıldı...")

    while True:
        now = time.time()
        prices = get_all_prices()

        for symbol in COINS:
            if symbol not in prices:
                continue

            price_str_raw = prices[symbol]  # Binance’ten geldiği hali
            try:
                price = float(price_str_raw)
            except ValueError:
                continue

            # Geçmiş fiyat listesine ekle
            price_history[symbol].append((now, price))

            # Yalnızca son 5 dakikadaki (300 saniye) verileri tut
            price_history[symbol] = [
                (t, p) for (t, p) in price_history[symbol] if now - t <= 300
            ]

            # En eski ve yeni fiyat farkını kontrol et
            if len(price_history[symbol]) > 1:
                old_price = price_history[symbol][0][1]
                new_price = price
                if old_price > 0:
                    change = ((new_price - old_price) / old_price) * 100
                    if abs(change) >= THRESHOLD:
                        utc_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
                        coin_name = symbol.replace('USDT', '/USDT')
                        price_str = trim_price(price_str_raw)
                        direction = '🟢⬆️' if change > 0 else '🔴⬇️'

                        msg = (
                            f"🚨 #{coin_name}\n"
                            f"Last 1 Minute Change: %{abs(change):.2f} {direction}\n"
                            f"Last Price: {price_str}\n"
                            f"⏰ {utc_time}"
                        )
                        print(msg)
                        send_telegram_message(msg)

        price_history = {symbol: [] for symbol in COINS}
        last_alert = {symbol: {'price': None, 'direction': None} for symbol in COINS}
        print("Başlangıç fiyatları alınıyor...")
        while True:
            time.sleep(10)  # 10 saniyede bir fiyat al
            new_prices = get_all_prices()
            for symbol in COINS:
                if symbol not in new_prices:
                    continue
                new_price = new_prices[symbol]
                try:
                    new_price_float = float(new_price)
                except Exception:
                    continue
                # Fiyat geçmişini güncelle
                price_history[symbol].append(new_price_float)
                if len(price_history[symbol]) > 5:
                    price_history[symbol].pop(0)
                # Son 5 dakikadaki değişimi kontrol et
                if len(price_history[symbol]) == 5:
                    old_price_float = price_history[symbol][0]
                    change = ((new_price_float - old_price_float) / old_price_float) * 100 if old_price_float != 0 else 0
                    direction = 'up' if change > 0 else 'down'
                    # Sadece yeni eşiği geçtiğinde veya yön değiştiğinde bildirim gönder
                    if abs(change) >= THRESHOLD:
                        last_alert_price = last_alert[symbol]['price']
                        last_alert_direction = last_alert[symbol]['direction']
                        # Eğer ilk kez bildiriliyorsa veya yön değiştiyse veya fiyat yeni bir eşiğe ulaştıysa
                        if (last_alert_price is None or last_alert_direction != direction or
                            (direction == 'up' and new_price_float > last_alert_price) or
                            (direction == 'down' and new_price_float < last_alert_price)):
                            utc_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
                            coin_name = symbol.replace('USDT', '/USDT')
                            price = trim_price(new_price)
                            if direction == 'up':
                                mesaj = f"🚨 #{coin_name} Last Price: {price}\n🟢⬆️ Last 5 Minute: %{abs(change):.2f}\n⏰Time: {utc_time}"
                            else:
                                mesaj = f"🚨 #{coin_name} Last Price: {price}\n🔴⬇️ Last 5 Minute: %{abs(change):.2f}\n⏰Time: {utc_time}"
                            print(mesaj)
                            send_telegram_message(mesaj)
                            last_alert[symbol]['price'] = new_price_float
                            last_alert[symbol]['direction'] = direction

if __name__ == "__main__":
    main()