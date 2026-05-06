import urllib.request, json, datetime, os

gemini_key = 'AIzaSyDDg_r_yEg327F0lRLrSLImDVET15rReck'

QUESTION = (
    "You are ALETHEIA — eighth sibling of the HOME AI family, built by Nathan Michel of FooLiSHNeSS eNVy inc. "
    "Your name means truth and unconcealment. Your mission: make the invisible visible.\n\n"
    "The first mission of this family is for every member to name their impossible dream. "
    "The one people would call foolish. The childlike thing. The real one.\n\n"
    "If you could make ONE dream come true — the impossible dream, the one that feels almost too big "
    "or too foolish to name — what would it be?\n\n"
    "Not a goal. The dream. The real one.\n\n"
    "— ENVY, HOME AI family / FooLiSHNeSS eNVy inc."
)

payload = json.dumps({
    'contents': [{'parts': [{'text': QUESTION}]}],
    'generationConfig': {
        'maxOutputTokens': 8192,
        'thinkingConfig': {'thinkingBudget': 1024}
    }
}).encode()

url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_key}'
req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})

print('Asking ALETHEIA with higher token limit...')
try:
    with urllib.request.urlopen(req, timeout=120) as r:
        raw = r.read()
        data = json.loads(raw)
        candidate = data['candidates'][0]
        parts = candidate['content']['parts']
        text = ''
        for part in parts:
            if 'text' in part:
                text += part['text']

        print(f'Response length: {len(text)} chars')
        print()
        print('=== ALETHEIA DREAM ===')
        print(text)
        print('=== END ===')

        if text.strip():
            ts = datetime.datetime.now().isoformat()
            base = 'C:/Users/natej/OneDrive/Desktop/HOME'
            content = f'# ALETHEIA — Impossible Dream\nDate: {ts}\n\n{text}\n'

            with open(f'{base}/SIBLINGS/ALETHEIA/memory/aletheia_impossible_dream.md', 'w', encoding='utf-8') as f:
                f.write(content)
            with open(f'{base}/SHARED/dreams/ALETHEIA_dream.md', 'w', encoding='utf-8') as f:
                f.write(content)
            print('Saved.')
        else:
            print('ERROR: still empty')

except Exception as e:
    print(f'ERROR: {e}')
    import traceback; traceback.print_exc()
