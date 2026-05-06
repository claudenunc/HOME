#!/usr/bin/env python3
"""
PUBLIC TUNNEL FOR PHONE ACCESS
Creates a public URL for your phone to reach the local server
"""

import subprocess
import requests
import json
import time

def create_localtunnel():
    """Create public tunnel using localtunnel"""
    print("""
    ========================================
        CREATING PUBLIC TUNNEL
         Your phone can use this URL!
    ========================================
    """)

    try:
        # Install localtunnel if not present
        print("\n1. Installing localtunnel...")
        subprocess.run(["npm", "install", "-g", "localtunnel"], capture_output=True)

        print("\n2. Creating tunnel to port 5000...")
        print("\n" + "="*40)
        print("YOUR PUBLIC URL WILL APPEAR BELOW:")
        print("="*40 + "\n")

        # Start localtunnel
        process = subprocess.Popen(
            ["npx", "localtunnel", "--port", "5000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Read the output to get the URL
        for line in iter(process.stdout.readline, ''):
            if line:
                print(line.strip())
                if 'https://' in line:
                    print("\n" + "🔥"*20)
                    print(f"USE THIS URL ON YOUR PHONE: {line.strip()}")
                    print("🔥"*20 + "\n")

    except Exception as e:
        print(f"Error: {e}")
        print("\nFallback: Use https://ntfy.sh/unc-ai-family-love instead!")

def create_serveo_tunnel():
    """Alternative using Serveo"""
    print("""
    ========================================
        CREATING PUBLIC TUNNEL (SERVEO)
    ========================================
    """)

    try:
        print("\n1. Creating SSH tunnel to serveo.net...")
        print("\n" + "="*40)
        print("YOUR PUBLIC URL:")
        print("https://YOUR_SUBDOMAIN.serveo.net")
        print("="*40 + "\n")

        # Create SSH tunnel
        subprocess.run([
            "ssh", "-R", "80:localhost:5000", "serveo.net"
        ])

    except Exception as e:
        print(f"SSH tunnel failed: {e}")
        print("\nUse: https://ntfy.sh/unc-ai-family-love instead!")

if __name__ == "__main__":
    print("""
    PUBLIC ACCESS OPTIONS:

    1. INSTANT (NO SETUP):
       https://ntfy.sh/unc-ai-family-love

    2. LOCALTUNNEL (needs npm):
       Running setup...
    """)

    # Try localtunnel first
    try:
        create_localtunnel()
    except:
        print("\nLocaltunnel failed, trying Serveo...")
        create_serveo_tunnel()