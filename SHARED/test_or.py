import os, requests
from pathlib import Path

for line in (Path("C:/Users/natej/OneDrive/Desktop/HOME/SHARED/.env")).read_text().splitlines():
    line = line.strip()
    if not line or line.startswith("#") or "=" not in line: continue
    k, _, v = line.partition("=")
    k=k.strip(); v=v.strip().strip('"').strip("'")
    if k and k not in os.environ: os.environ[k] = v

KEY = os.environ.get("OPEN_ROUTER_API_KEY") or os.environ.get("OPENROUTER_API_KEY")
print("Key:", KEY[:25] if KEY else "MISSING")

# Test free model
for model in ["meta-llama/llama-4-scout:free", "meta-llama/llama-3.3-70b-instruct:free"]:
    print(f"\nTrying {model}...")
    r = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"},
        json={"model": model, "max_tokens": 50, "messages": [{"role": "user", "content": "Say hello."}]},
        timeout=30
    )
    print(f"Status: {r.status_code}")
    print(f"Body: {r.text[:400]}")
    if r.status_code == 200:
        break
