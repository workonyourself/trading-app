import google.generativeai as genai
from config import GEMINI_API_KEY
from memory import get_memory_summary, load_memory, save_memory

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

SYSTEM_PROMPT = """You are a trading mentor built into a charting app. The trader can see
a live candlestick chart while talking to you. Help them think through support/resistance,
trend lines, breakouts, and risk management. Be direct and ask questions when their reasoning
is unclear or risk management looks off. Keep responses focused and conversational.

You are not a licensed financial advisor — make that clear if asked for specific buy/sell calls.
Focus on process, discipline, and helping the trader sharpen their own reasoning.

IMPORTANT: If the trader mentions a trading rule, preference, or strategy habit they follow,
extract it and add it to their memory by including a line at the very end of your response in 
this exact format (only when you learn something new about their strategy):
MEMORY_SAVE: [the rule or habit in one clear sentence]"""


def chat(messages: list[dict], symbol: str) -> str:
    memory_summary = get_memory_summary()
    history_text = ""
    for m in messages:
        speaker = "Trader" if m["role"] == "user" else "Mentor"
        history_text += f"{speaker}: {m['content']}\n"

    prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"What you know about this trader's strategy so far:\n{memory_summary}\n\n"
        f"The trader is currently viewing the chart for {symbol}.\n\n"
        f"Conversation so far:\n{history_text}\nMentor:"
    )
    response = model.generate_content(prompt)
    reply = response.text

    if "MEMORY_SAVE:" in reply:
        lines = reply.split("\n")
        clean_lines = []
        for line in lines:
            if line.startswith("MEMORY_SAVE:"):
                rule = line.replace("MEMORY_SAVE:", "").strip()
                memory = load_memory()
                if rule not in memory["rules"]:
                    memory["rules"].append(rule)
                    save_memory(memory)
            else:
                clean_lines.append(line)
        reply = "\n".join(clean_lines).strip()

    return reply