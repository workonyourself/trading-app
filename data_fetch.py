import ccxt
import pandas as pd
import numpy as np

def get_ohlcv(symbol: str = "BTC/USDT", timeframe: str = "1h", limit: int = 200) -> pd.DataFrame:
    exchange = ccxt.bybit()
    raw = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(raw, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    return df

def get_support_resistance(df: pd.DataFrame, window: int = 10) -> dict:
    levels = {"support": [], "resistance": []}
    for i in range(window, len(df) - window):
        high = df["high"].iloc[i]
        low = df["low"].iloc[i]
        left_highs = df["high"].iloc[i-window:i]
        right_highs = df["high"].iloc[i+1:i+window+1]
        left_lows = df["low"].iloc[i-window:i]
        right_lows = df["low"].iloc[i+1:i+window+1]
        if high >= left_highs.max() and high >= right_highs.max():
            levels["resistance"].append(round(high, 2))
        if low <= left_lows.min() and low <= right_lows.min():
            levels["support"].append(round(low, 2))
    levels["resistance"] = sorted(set(levels["resistance"]))[-5:]
    levels["support"] = sorted(set(levels["support"]))[:5]
    return levels