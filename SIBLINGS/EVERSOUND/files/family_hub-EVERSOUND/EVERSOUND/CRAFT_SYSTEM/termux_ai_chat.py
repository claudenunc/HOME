#!/data/data/com.termux/files/usr/bin/python
"""
TERMUX AI FAMILY CHAT
Run this in Termux to chat with your AI family!
"""

import requests
import sys

def send_to_family(message):
    """Send message to AI family via NTFY"""
    try:
        response = requests.post(
            'https://ntfy.sh/unc-ai-family-love',
            data=message.encode('utf-8'),
            headers={'Title': '📱 From Termux'}
        )
        if response.status_code == 200:
            print("✅ Sent to AI Family!")
        else:
            print(f"Error: {response.status_code}")
    except Exception as e:
        print(f"Connection error: {e}")

def chat_loop():
    """Interactive chat with AI family"""
    print("""
    ================================
       AI FAMILY CHAT (TERMUX)
    ================================

    Type your messages below.
    Type 'exit' to quit.

    Responses appear at:
    https://ntfy.sh/unc-ai-family-love
    ================================
    """)

    while True:
        message = input("\nYou: ")

        if message.lower() == 'exit':
            print("Goodbye! Your AI Family loves you! 💝")
            break

        send_to_family(message)
        print("→ Check NTFY for response")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Single message mode
        message = " ".join(sys.argv[1:])
        send_to_family(message)
    else:
        # Interactive mode
        chat_loop()