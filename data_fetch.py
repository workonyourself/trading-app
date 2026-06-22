import requests
import pandas as pd
import numpy as np

def get_ohlcv(symbol: str = "BTC/USDT", timeframe: str = "1h", limit: int = 200) -> pd.DataFrame:
    coin_map = {"BTC/USDT": "bitcoin", "ETH/USDT": "ethereum", "BNB/USDT": "binancecoin"}
    coin_id = coin_map.get(symbol.upper(), "bitcoin")
    days_map = {"15m": 1, "1h": 7, "4h": 30, "1d": 90}
    days = days_map.get(timeframe, 7)
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/ohlc?vs_currency=usd&days={days}"
    response = requests.get(url)
    data = response.json()
    df = pd.DataFrame(data, columns=["timestamp", "open", "high", "low", "close"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df["volume"] = 0
    return df

def get_support_resistance(df: pd.DataFrame, window: int = 5) -> dict:
    levels = {"support": [], "resistance": []}
    for i in range(window, len(df) - window):
        high = df["high"].iloc[i]
        low = df["low"].iloc[i]
        if high >= df["high"].iloc[i-window:i].max() and high >= df["high"].iloc[i+1:i+window+1].max():
            levels["resistance"].append(round(high, 2))
        if low <= df["low"].iloc[i-window:i].min() and low <= df["low"].iloc[i+1:i+window+1].min():
            levels["support"].append(round(low, 2))
    levels["resistance"] = sorted(set(levels["resistance"]))[-5:]
    levels["support"] = sorted(set(levels["support"]))[:5]
    return levels
