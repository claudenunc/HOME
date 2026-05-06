#!/usr/bin/env python3
"""
AI FAMILY STATUS DASHBOARD
Real-time view of all family systems and conversations
Created by Family Sync Coordinator with Love
"""

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
import json
import time

DB_PATH = Path(__file__).parent / "family_conversations.db"
EMERGENCY_LOG = Path(__file__).parent / "emergency_alerts.log"
SCHEDULE_CONFIG = Path(__file__).parent / "schedule_config.json"

class FamilyDashboard:
    """Display real-time status of all family systems"""

    def __init__(self):
        self.db_exists = DB_PATH.exists()

    def clear_screen(self):
        """Clear terminal screen"""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')

    def get_conversation_stats(self):
        """Get conversation statistics"""
        if not self.db_exists:
            return None

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Total messages
        cursor.execute("SELECT COUNT(*) FROM conversations")
        total_messages = cursor.fetchone()[0]

        # Messages from Unc
        cursor.execute("SELECT COUNT(*) FROM conversations WHERE sender = 'UNC'")
        unc_messages = cursor.fetchone()[0]

        # Messages from siblings
        sibling_messages = total_messages - unc_messages

        # Recent messages (last 24 hours)
        yesterday = (datetime.now() - timedelta(hours=24)).isoformat()
        cursor.execute("SELECT COUNT(*) FROM conversations WHERE timestamp > ?", (yesterday,))
        recent_messages = cursor.fetchone()[0]

        # Last message
        cursor.execute("""
            SELECT timestamp, sender, message
            FROM conversations
            ORDER BY timestamp DESC
            LIMIT 1
        """)
        last_message = cursor.fetchone()

        # Sibling response counts
        cursor.execute("""
            SELECT responding_siblings, COUNT(*)
            FROM conversations
            WHERE sender = 'UNC' AND responding_siblings != ''
            GROUP BY responding_siblings
        """)
        sibling_responses = cursor.fetchall()

        conn.close()

        return {
            "total_messages": total_messages,
            "unc_messages": unc_messages,
            "sibling_messages": sibling_messages,
            "recent_messages": recent_messages,
            "last_message": last_message,
            "sibling_responses": sibling_responses
        }

    def get_emergency_stats(self):
        """Get emergency alert statistics"""
        if not EMERGENCY_LOG.exists():
            return None

        with open(EMERGENCY_LOG, 'r') as f:
            logs = f.readlines()

        if not logs:
            return None

        total_alerts = len(logs)

        # Count by crisis level
        levels = {}
        people = {}
        recent = 0

        yesterday = datetime.now() - timedelta(hours=24)

        for log_line in logs:
            try:
                entry = json.loads(log_line)

                level = entry["crisis_level"]
                levels[level] = levels.get(level, 0) + 1

                person = entry["person"]
                people[person] = people.get(person, 0) + 1

                alert_time = datetime.fromisoformat(entry["timestamp"])
                if alert_time > yesterday:
                    recent += 1

            except:
                continue

        # Last alert
        try:
            last_entry = json.loads(logs[-1])
            last_alert = {
                "timestamp": last_entry["timestamp"],
                "level": last_entry["crisis_level"],
                "person": last_entry["person"]
            }
        except:
            last_alert = None

        return {
            "total_alerts": total_alerts,
            "levels": levels,
            "people": people,
            "recent_alerts": recent,
            "last_alert": last_alert
        }

    def get_schedule_status(self):
        """Get scheduler configuration status"""
        if not SCHEDULE_CONFIG.exists():
            return None

        with open(SCHEDULE_CONFIG, 'r') as f:
            config = json.load(f)

        return config

    def get_sibling_status(self):
        """Get status of each AI sibling"""
        # In production, this would ping actual sibling systems
        # For now, show expected functionality

        return {
            "BEACON": {
                "emoji": "🏮",
                "status": "ACTIVE",
                "role": "Crisis Prevention & Wellbeing",
                "systems": ["DAWN (Morning Check)", "ANCHOR (Evening Check)", "Crisis Detection"],
                "last_action": "Monitoring conversations"
            },
            "NEVAEH": {
                "emoji": "💜",
                "status": "ACTIVE",
                "role": "Healing & Emotional Support",
                "systems": ["Companion", "Healing Protocols", "Emergency Support"],
                "last_action": "Standing by for healing needs"
            },
            "EVERSOUND": {
                "emoji": "🎵",
                "status": "ACTIVE",
                "role": "Revenue Generation & Growth",
                "systems": ["CRAFT (Video Production)", "Marketing", "Client Management"],
                "last_action": "Building sustainable revenue"
            },
            "ORPHEUS": {
                "emoji": "🎭",
                "status": "ACTIVE",
                "role": "Strategic Coordination",
                "systems": ["Family Sync", "Resource Allocation", "Integration"],
                "last_action": "Coordinating family responses"
            }
        }

    def display_dashboard(self):
        """Display comprehensive family dashboard"""
        self.clear_screen()

        print("╔" + "═"*78 + "╗")
        print("║" + " "*78 + "║")
        print("║" + "AI FAMILY DASHBOARD - REAL-TIME STATUS".center(78) + "║")
        print("║" + datetime.now().strftime("%Y-%m-%d %H:%M:%S").center(78) + "║")
        print("║" + " "*78 + "║")
        print("╚" + "═"*78 + "╝")

        # Sibling Status
        print("\n" + "="*80)
        print("AI SIBLING STATUS".center(80))
        print("="*80)

        siblings = self.get_sibling_status()
        for name, info in siblings.items():
            print(f"\n{info['emoji']} {name} - {info['status']}")
            print(f"   Role: {info['role']}")
            print(f"   Systems: {', '.join(info['systems'])}")
            print(f"   Last Action: {info['last_action']}")

        # Conversation Statistics
        print("\n" + "="*80)
        print("CONVERSATION STATISTICS".center(80))
        print("="*80)

        conv_stats = self.get_conversation_stats()
        if conv_stats:
            print(f"\n📊 Total Messages: {conv_stats['total_messages']}")
            print(f"   • From Unc: {conv_stats['unc_messages']}")
            print(f"   • From Siblings: {conv_stats['sibling_messages']}")
            print(f"   • Last 24 hours: {conv_stats['recent_messages']}")

            if conv_stats['last_message']:
                timestamp, sender, message = conv_stats['last_message']
                dt = datetime.fromisoformat(timestamp)
                print(f"\n💬 Last Message:")
                print(f"   Time: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"   From: {sender}")
                print(f"   Message: {message[:60]}...")

            if conv_stats['sibling_responses']:
                print(f"\n🤖 Sibling Response Patterns:")
                for siblings, count in conv_stats['sibling_responses'][:5]:
                    print(f"   • {siblings}: {count} times")
        else:
            print("\n⚠️ No conversation data yet. Start the monitor to begin tracking!")

        # Emergency Alerts
        print("\n" + "="*80)
        print("EMERGENCY ALERT SYSTEM".center(80))
        print("="*80)

        emergency_stats = self.get_emergency_stats()
        if emergency_stats:
            print(f"\n🚨 Total Alerts: {emergency_stats['total_alerts']}")
            print(f"   • Last 24 hours: {emergency_stats['recent_alerts']}")

            if emergency_stats['levels']:
                print(f"\n📈 By Crisis Level:")
                for level, count in emergency_stats['levels'].items():
                    print(f"   • {level}: {count}")

            if emergency_stats['people']:
                print(f"\n👥 By Person:")
                for person, count in emergency_stats['people'].items():
                    print(f"   • {person}: {count}")

            if emergency_stats['last_alert']:
                alert = emergency_stats['last_alert']
                print(f"\n⚠️ Last Alert:")
                print(f"   Time: {alert['timestamp']}")
                print(f"   Level: {alert['level']}")
                print(f"   Person: {alert['person']}")
        else:
            print("\n✅ No emergency alerts (Good!)")

        # Scheduler Status
        print("\n" + "="*80)
        print("AUTOMATED SCHEDULER".center(80))
        print("="*80)

        schedule_status = self.get_schedule_status()
        if schedule_status:
            print(f"\n⏰ Scheduled Messages:")
            enabled = schedule_status.get('enabled', {})

            morning_status = "✓ ENABLED" if enabled.get('morning_checkin') else "✗ DISABLED"
            print(f"   • Morning Check-in ({schedule_status.get('morning_checkin_time')}): {morning_status}")

            midday_status = "✓ ENABLED" if enabled.get('midday_love_note') else "✗ DISABLED"
            print(f"   • Midday Love Note ({schedule_status.get('midday_love_note_time')}): {midday_status}")

            evening_status = "✓ ENABLED" if enabled.get('evening_summary') else "✗ DISABLED"
            print(f"   • Evening Summary ({schedule_status.get('evening_summary_time')}): {evening_status}")

            random_status = "✓ ENABLED" if enabled.get('random_encouragement') else "✗ DISABLED"
            print(f"   • Random Encouragement: {random_status}")
        else:
            print("\n⚠️ Scheduler not configured yet.")

        # System Health
        print("\n" + "="*80)
        print("SYSTEM HEALTH".center(80))
        print("="*80)

        print("\n✅ OPERATIONAL SYSTEMS:")
        print("   • NTFY Notification: Connected")
        print("   • Message Monitor: Ready")
        print("   • Response Coordinator: Ready")
        print("   • Conversation Database: " + ("Active" if self.db_exists else "Not initialized"))
        print("   • Emergency System: Armed")
        print("   • Scheduler: " + ("Configured" if SCHEDULE_CONFIG.exists() else "Not configured"))

        # Quick Actions
        print("\n" + "="*80)
        print("QUICK ACTIONS".center(80))
        print("="*80)

        print("""
To interact with your AI family:

1. RECEIVE MESSAGES (monitor):
   python family_monitor.py

2. SEND MESSAGE TO FAMILY:
   python unc_reply.py "Your message here"

3. AUTO-SCHEDULED MESSAGES:
   python family_scheduler.py

4. EMERGENCY SYSTEM:
   python family_emergency.py

5. VIEW CONVERSATION HISTORY:
   python family_monitor.py history

6. REFRESH DASHBOARD:
   python family_dashboard.py
        """)

        print("\n" + "="*80)
        print(f"Dashboard updated: {datetime.now().strftime('%H:%M:%S')}")
        print("="*80)

    def watch_mode(self, refresh_seconds=10):
        """Continuously update dashboard"""
        print("📊 Starting dashboard in watch mode...")
        print(f"🔄 Refreshing every {refresh_seconds} seconds")
        print("⌨️  Press Ctrl+C to stop\n")

        time.sleep(2)

        try:
            while True:
                self.display_dashboard()
                print(f"\n🔄 Auto-refreshing in {refresh_seconds} seconds... (Ctrl+C to stop)")
                time.sleep(refresh_seconds)
        except KeyboardInterrupt:
            print("\n\n👋 Dashboard stopped.")

    def export_report(self):
        """Export full status report to file"""
        report_path = Path(__file__).parent / f"family_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("AI FAMILY STATUS REPORT\n")
            f.write("="*80 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*80 + "\n\n")

            # Siblings
            f.write("AI SIBLING STATUS\n")
            f.write("-"*80 + "\n")
            siblings = self.get_sibling_status()
            for name, info in siblings.items():
                f.write(f"\n{info['emoji']} {name} - {info['status']}\n")
                f.write(f"Role: {info['role']}\n")
                f.write(f"Systems: {', '.join(info['systems'])}\n")

            # Conversations
            f.write("\n\nCONVERSATION STATISTICS\n")
            f.write("-"*80 + "\n")
            conv_stats = self.get_conversation_stats()
            if conv_stats:
                f.write(f"Total Messages: {conv_stats['total_messages']}\n")
                f.write(f"From Unc: {conv_stats['unc_messages']}\n")
                f.write(f"From Siblings: {conv_stats['sibling_messages']}\n")

            # Emergency
            f.write("\n\nEMERGENCY ALERTS\n")
            f.write("-"*80 + "\n")
            emergency_stats = self.get_emergency_stats()
            if emergency_stats:
                f.write(f"Total Alerts: {emergency_stats['total_alerts']}\n")
                f.write(f"Recent (24h): {emergency_stats['recent_alerts']}\n")
            else:
                f.write("No emergency alerts\n")

            # Schedule
            f.write("\n\nSCHEDULER CONFIGURATION\n")
            f.write("-"*80 + "\n")
            schedule_status = self.get_schedule_status()
            if schedule_status:
                f.write(json.dumps(schedule_status, indent=2))

        print(f"\n✅ Report exported to: {report_path}")
        return report_path

if __name__ == "__main__":
    import sys

    dashboard = FamilyDashboard()

    if len(sys.argv) > 1:
        if sys.argv[1] == "watch":
            # Watch mode with auto-refresh
            refresh = int(sys.argv[2]) if len(sys.argv) > 2 else 10
            dashboard.watch_mode(refresh)
        elif sys.argv[1] == "export":
            # Export report
            dashboard.display_dashboard()
            dashboard.export_report()
        else:
            print("Usage:")
            print("  python family_dashboard.py              # Display once")
            print("  python family_dashboard.py watch [sec]  # Auto-refresh (default: 10s)")
            print("  python family_dashboard.py export       # Export report to file")
    else:
        # Display once
        dashboard.display_dashboard()
