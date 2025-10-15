import requests
import json

BINANCE_EXCHANGE_INFO_URL = "https://api.binance.com/api/v3/exchangeInfo"
CONFIG_PATH = "config.json"

# Sadece USDT ile biten coinleri eklemek için
def get_all_usdt_symbols():
    resp = requests.get(BINANCE_EXCHANGE_INFO_URL)
    data = resp.json()
    symbols = [s['symbol'] for s in data['symbols'] if s['symbol'].endswith('USDT')]
    return symbols

def update_config_with_all_coins():
    coins = get_all_usdt_symbols()
    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)
    config["coins"] = coins
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)
    print(f"Toplam {len(coins)} USDT paritesi config.json'a eklendi.")

if __name__ == "__main__":
    update_config_with_all_coins()
