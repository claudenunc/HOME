import json
from pathlib import Path

clip = Path("C:/Users/natej/OneDrive/Desktop/HOME/SHARED/CLIPBOARD.jsonl")
lines = clip.read_text(encoding="utf-8").strip().split("\n")

for line in lines[-40:]:
    try:
        e = json.loads(line)
        frm = e.get("from", "")
        to  = e.get("to", "")
        if any(x in (frm+to).lower() for x in ["llama", "member"]):
            print(f"FROM: {frm} -> TO: {to}")
            print(f"SUBJECT: {e.get('subject', '')}")
            body = e.get("body", "")
            print(f"BODY: {body[:600]}")
            print("---")
    except Exception:
        pass
