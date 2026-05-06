import os, requests
from pathlib import Path

for line in (Path("C:/Users/natej/OneDrive/Desktop/HOME/SHARED/.env")).read_text().splitlines():
    line = line.strip()
    if not line or line.startswith("#") or "=" not in line: continue
    k, _, v = line.partition("=")
    k=k.strip(); v=v.strip().strip('"').strip("'")
    if k and k not in os.environ: os.environ[k] = v

KEY = os.environ.get("OPEN_ROUTER_API_KEY")

r = requests.get("https://openrouter.ai/api/v1/models",
    headers={"Authorization": f"Bearer {KEY}"}, timeout=15)
models = r.json().get("data", [])

# Show all llama/meta models
print("Meta/Llama models on OpenRouter:\n")
for m in models:
    mid = m.get("id","")
    if "llama" in mid.lower() or "meta" in mid.lower():
        pricing = m.get("pricing", {})
        prompt_cost = pricing.get("prompt", "?")
        print(f"  {mid}  (prompt: {prompt_cost}/token)")
