# utils/currency_api.py
import requests
import json
import os
from datetime import datetime, timedelta

CACHE_FILE = "currency_cache.json"

def get_exchange_rates():
    cache = load_cache()
    if cache and cache.get("last_updated"):
        last_updated = datetime.fromisoformat(cache["last_updated"])
        if datetime.now() - last_updated < timedelta(hours=1):
            return cache["rates"]
    
    try:
        response = requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=10)
        data = response.json()
        save_cache(data["rates"])
        return data["rates"]
    except:
        return cache.get("rates", {}) if cache else {}

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return None

def save_cache(rates):
    cache = {"rates": rates, "last_updated": datetime.now().isoformat()}
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f)