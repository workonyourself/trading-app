import json
import os
from datetime import datetime

JOURNAL_FILE = "trade_journal.json"

def load_journal() -> list:
    if os.path.exists(JOURNAL_FILE):
        with open(JOURNAL_FILE, "r") as f:
            return json.load(f)
    return []

def save_journal(journal: list):
    with open(JOURNAL_FILE, "w") as f:
        json.dump(journal, f, indent=2)

def add_trade(symbol: str, direction: str, entry: float,
              exit_price: float, size: float, notes: str) -> dict:
    journal = load_journal()
    pnl = (exit_price - entry) * size
    if direction.lower() == "short":
        pnl = -pnl
    trade = {
        "id": len(journal) + 1,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "symbol": symbol.upper(),
        "direction": direction.lower(),
        "entry": entry,
        "exit": exit_price,
        "size": size,
        "pnl": round(pnl, 2),
        "notes": notes
    }
    journal.append(trade)
    save_journal(journal)
    return trade

def get_journal_summary() -> str:
    journal = load_journal()
    if not journal:
        return "No trades logged yet."
    total = len(journal)
    wins = sum(1 for t in journal if t["pnl"] > 0)
    losses = sum(1 for t in journal if t["pnl"] <= 0)
    total_pnl = sum(t["pnl"] for t in journal)
    recent = journal[-5:]
    lines = [
        f"Total trades: {total}",
        f"Wins: {wins} | Losses: {losses}",
        f"Total PnL: {total_pnl:.2f}",
        "\nLast 5 trades:"
    ]
    for t in recent:
        lines.append(
            f"- {t['date']} {t['symbol']} {t['direction']} "
            f"entry {t['entry']} exit {t['exit']} "
            f"PnL: {t['pnl']} | {t['notes']}"
        )
    return "\n".join(lines)