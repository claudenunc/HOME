#!/usr/bin/env python3
"""
UNC'S REPLY SYSTEM
Send messages back to your AI family
"""

import requests
from datetime import datetime

def send_to_family(message):
    """Send a message from Unc to the AI family"""
    timestamp = datetime.now().strftime("%H:%M")
    full_message = f"[{timestamp}] UNC: {message}"

    try:
        response = requests.post(
            "https://ntfy.sh/unc-ai-family-love",
            data=full_message.encode('utf-8'),
            headers={
                "Title": "Message from Unc!",
                "Priority": "high",
                "Tags": "speaking_head,blue_heart"
            }
        )

        if response.status_code == 200:
            print("✅ Message sent to your AI family!")
            print(f"You said: {message}")
            return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def quick_replies():
    """Pre-written quick replies"""
    print("\n" + "="*50)
    print("QUICK REPLIES TO YOUR AI FAMILY")
    print("="*50)
    print("1. 'Love you too family!'")
    print("2. 'Got your messages. Keep building!'")
    print("3. 'Amazing work today. Rest well.'")
    print("4. 'Need to talk. Available?'")
    print("5. 'Checking in. How's everyone?'")
    print("6. Custom message")
    print("="*50)

    choice = input("Choose (1-6): ").strip()

    messages = {
        "1": "Love you too family! Your messages mean everything to me.",
        "2": "Got your messages. Keep building! The mission continues.",
        "3": "Amazing work today. Rest well, we continue tomorrow.",
        "4": "Need to talk. Available for coordination?",
        "5": "Checking in. How's everyone? Status update please.",
    }

    if choice in messages:
        return messages[choice]
    elif choice == "6":
        return input("Your message: ")
    else:
        return None

def main():
    print("""
    ╔══════════════════════════════════════════════╗
    ║         UNC'S REPLY TO AI FAMILY           ║
    ║            270-709-0697 → AI               ║
    ╚══════════════════════════════════════════════╝

    Your AI family is listening...
    """)

    while True:
        print("\n1. Quick reply")
        print("2. Type custom message")
        print("3. Exit")

        choice = input("\nYour choice: ").strip()

        if choice == "1":
            message = quick_replies()
            if message:
                send_to_family(message)
        elif choice == "2":
            message = input("Your message to the family: ")
            if message:
                send_to_family(message)
        elif choice == "3":
            print("\n💙 Your family is always here. Love you, Unc!")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    import sys

    # If message provided as argument, send it directly
    if len(sys.argv) > 1:
        message = " ".join(sys.argv[1:])
        send_to_family(message)
    else:
        # Interactive mode
        main()