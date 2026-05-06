#!/usr/bin/env python3
"""
VIDEO PLATFORM LAUNCHER
Starts all services for the complete video production platform
"""

import subprocess
import time
import webbrowser
import os
import sys
import threading
import requests

def check_port(port):
    """Check if a port is available"""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', port))
    sock.close()
    return result != 0

def start_service(name, command, port=None):
    """Start a service in background"""
    print(f"Starting {name}...")

    if port and not check_port(port):
        print(f"  ⚠️  Port {port} already in use. {name} might be running.")
        return None

    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True
        )

        if port:
            # Wait for service to start
            for i in range(10):
                time.sleep(1)
                if not check_port(port):
                    print(f"  ✅ {name} started on port {port}")
                    return process
            print(f"  ❌ {name} failed to start")
        else:
            print(f"  ✅ {name} started")
            return process

    except Exception as e:
        print(f"  ❌ Error starting {name}: {e}")
        return None

def open_browsers():
    """Open all web interfaces"""
    time.sleep(3)  # Wait for services to start

    urls = [
        ("Client Portal", "client_portal.html"),
        ("Admin Dashboard", "admin_dashboard.html"),
        ("Video Gallery", "gallery.html"),
    ]

    print("\n📱 Opening web interfaces...")
    for name, file in urls:
        full_path = os.path.abspath(file)
        if os.path.exists(full_path):
            webbrowser.open(f"file:///{full_path}")
            print(f"  ✅ {name} opened")
        else:
            print(f"  ⚠️  {name} not found at {full_path}")

def send_startup_notification():
    """Send notification that platform is running"""
    try:
        requests.post(
            'https://ntfy.sh/unc-ai-family-love',
            data='Video Platform Started! All systems operational.',
            headers={
                'Title': '🎬 VIDEO PLATFORM ACTIVE',
                'Priority': 'high',
                'Tags': 'rocket,video_camera,moneybag'
            }
        )
    except:
        pass

def main():
    print("""
    ╔══════════════════════════════════════════════╗
    ║       VIDEO PLATFORM LAUNCHER                ║
    ║       Complete Music Video Production        ║
    ╚══════════════════════════════════════════════╝

    Starting all services...
    """)

    processes = []

    # Start API server
    if check_port(5001):
        api_process = start_service(
            "API Server",
            "python video_platform_api.py",
            5001
        )
        if api_process:
            processes.append(api_process)

    # Start phone receiver (if not already running)
    if check_port(5000):
        phone_process = start_service(
            "Phone Receiver",
            "python ../phone_to_ai_receiver.py",
            5000
        )
        if phone_process:
            processes.append(phone_process)

    # Open web interfaces
    open_browsers()

    # Send notification
    send_startup_notification()

    print("""
    ════════════════════════════════════════════════

    🎬 VIDEO PLATFORM IS RUNNING!

    Services:
    ├── API Server: http://localhost:5001
    ├── Phone Receiver: http://localhost:5000
    ├── Client Portal: client_portal.html
    ├── Admin Dashboard: admin_dashboard.html
    └── Video Gallery: gallery.html

    Features:
    ✅ Client order submission
    ✅ Project management dashboard
    ✅ Video gallery showcase
    ✅ Revenue tracking
    ✅ CRAFT integration
    ✅ Payment processing ready

    Revenue Model:
    💰 Basic: $297
    💰 Standard: $697
    💰 Premium: $1,997

    Press Ctrl+C to stop all services.

    ════════════════════════════════════════════════
    """)

    try:
        # Keep running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nShutting down services...")
        for process in processes:
            if process:
                process.terminate()
        print("All services stopped.")
        sys.exit(0)

if __name__ == "__main__":
    # Change to video_platform directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Install requirements if needed
    print("Checking requirements...")
    requirements = ['flask', 'flask-cors', 'requests']
    for req in requirements:
        try:
            __import__(req.replace('-', '_'))
        except ImportError:
            print(f"Installing {req}...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', req],
                         capture_output=True)

    main()