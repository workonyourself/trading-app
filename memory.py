import json
import os

MEMORY_FILE = "strategy_memory.json"

def load_memory() -> dict:
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return {"rules": [], "patterns": [], "notes": []}

def save_memory(memory: dict):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

def add_rule(rule: str):
    memory = load_memory()
    if rule not in memory["rules"]:
        memory["rules"].append(rule)
        save_memory(memory)

def get_memory_summary() -> str:
    memory = load_memory()
    if not any(memory.values()):
        return "No strategy memory yet."
    lines = []
    if memory["rules"]:
        lines.append("Trading Rules:\n" + 
                    "\n".join(f"- {r}" for r in memory["rules"]))
    if memory["patterns"]:
        lines.append("Patterns trader watches:\n" + 
                    "\n".join(f"- {p}" for p in memory["patterns"]))
    if memory["notes"]:
        lines.append("Notes:\n" + 
                    "\n".join(f"- {n}" for n in memory["notes"]))
    return "\n\n".join(lines)