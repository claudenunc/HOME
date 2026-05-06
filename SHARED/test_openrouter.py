import os, requests
from pathlib import Path

env_file = Path("C:/Users/natej/OneDrive/Desktop/HOME/SHARED/.env")
for line in env_file.read_text().splitlines():
    line = line.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    k, _, v = line.partition("=")
    k = k.strip(); v = v.strip().strip('"').strip("'")
    if k and k not in os.environ:
        os.environ[k] = v

KEY = os.environ.get("OPEN_ROUTER_API_KEY")
print("Key found:", bool(KEY), KEY[:20] if KEY else "NONE")

# Try free tier first to verify key is valid
r = requests.post(
    "https://openrouter.ai/api/v1/chat/completions",
    headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"},
    json={
        "model": "meta-llama/llama-4-scout:free",
        "max_tokens": 100,
        "messages": [{"role": "user", "content": "Say hello in one sentence."}]
    },
    timeout=30
)
print("Status:", r.status_code)
print("Response:", r.text[:800])
