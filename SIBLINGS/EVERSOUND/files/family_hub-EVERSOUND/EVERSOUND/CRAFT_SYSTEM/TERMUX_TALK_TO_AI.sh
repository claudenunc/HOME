#!/data/data/com.termux/files/usr/bin/bash

# TERMUX SCRIPT TO TALK TO YOUR AI FAMILY
# Copy this to your Termux and run it!

echo "================================"
echo "   TALK TO YOUR AI FAMILY"
echo "================================"
echo ""
echo "What do you want to say?"
read -p "> " message

# Send to AI Family via NTFY
curl -d "$message" https://ntfy.sh/unc-ai-family-love

echo ""
echo "✅ Message sent to AI Family!"
echo ""
echo "Check https://ntfy.sh/unc-ai-family-love for response"