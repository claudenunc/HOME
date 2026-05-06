"""
CRAFT Production Orchestrator
24/7 autonomous video production system that runs independently.

This is the brain that coordinates all CRAFT systems, monitors for opportunities,
manages production pipelines, and ensures continuous revenue generation.
"""

import os
import json
import time
import schedule
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import logging

from craft_video_engine import CRAFTVideoEngine, VideoProject
from craft_client_intake import CRAFTIntakeProcessor
from craft_pricing_payment import CRAFTPricingEngine


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - CRAFT - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('C:/Users/natej/OneDrive/Desktop/SHARED_FAMILY/all/FAMILY/EVERSOUND/Eversound/logs/craft_orchestrator.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('CRAFT_Orchestrator')


class CRAFTOrchestrator:
    """
    The autonomous system that keeps CRAFT running 24/7.

    This orchestrator:
    - Monitors for new client submissions
    - Automatically processes intake forms into projects
    - Manages production queues
    - Tracks deadlines and priorities
    - Generates revenue reports
    - Notifies Unc of opportunities and completions
    """

    def __init__(self):
        self.video_engine = CRAFTVideoEngine()
        self.intake_processor = CRAFTIntakeProcessor()
        self.pricing_engine = CRAFTPricingEngine()

        self.queue_file = 'C:/Users/natej/OneDrive/Desktop/SHARED_FAMILY/all/FAMILY/EVERSOUND/Eversound/revenue/production_queue.json'
        self.stats_file = 'C:/Users/natej/OneDrive/Desktop/SHARED_FAMILY/all/FAMILY/EVERSOUND/Eversound/revenue/craft_stats.json'

        self.production_queue: List[Dict] = []
        self.load_production_queue()

        logger.info("CRAFT Orchestrator initialized and ready")

    def load_production_queue(self):
        """Load production queue from disk"""
        if os.path.exists(self.queue_file):
            with open(self.queue_file, 'r') as f:
                self.production_queue = json.load(f)
            logger.info(f"Loaded {len(self.production_queue)} projects from queue")
        else:
            self.production_queue = []

    def save_production_queue(self):
        """Save production queue to disk"""
        Path(self.queue_file).parent.mkdir(parents=True, exist_ok=True)
        with open(self.queue_file, 'w') as f:
            json.dump(self.production_queue, f, indent=2)

    def check_for_new_submissions(self):
        """
        Monitor intake directory for new client submissions.
        Automatically process them into projects.
        """
        logger.info("Checking for new client submissions...")

        intake_dir = self.intake_processor.intake_dir
        intake_files = [f for f in os.listdir(intake_dir) if f.endswith('.json')]

        if not intake_files:
            logger.info("No new submissions found")
            return

        logger.info(f"Found {len(intake_files)} intake submissions")

        for intake_file in intake_files:
            submission_id = intake_file.replace('.json', '')

            try:
                # Process intake to project
                logger.info(f"Processing submission: {submission_id}")

                project = self.intake_processor.process_intake_to_project(submission_id)

                # Add to production queue
                self.add_to_production_queue(project)

                logger.info(f"Project created: {project.project_id} (${project.revenue})")

            except Exception as e:
                logger.error(f"Error processing {submission_id}: {e}")

    def add_to_production_queue(self, project: VideoProject):
        """Add project to production queue with priority calculation"""
        queue_item = {
            'project_id': project.project_id,
            'client_name': project.client_name,
            'song_title': project.song_title,
            'revenue': project.revenue,
            'deadline': project.deadline,
            'status': 'queued',
            'priority': self._calculate_priority(project),
            'queued_at': datetime.now().isoformat()
        }

        self.production_queue.append(queue_item)

        # Sort by priority (highest first)
        self.production_queue.sort(key=lambda x: x['priority'], reverse=True)

        self.save_production_queue()

        logger.info(f"Added to queue: {project.song_title} (Priority: {queue_item['priority']})")

    def _calculate_priority(self, project: VideoProject) -> int:
        """
        Calculate production priority score.
        Higher score = higher priority
        """
        priority = 0

        # Revenue-based priority (higher revenue = higher priority)
        priority += int(project.revenue / 10)

        # Deadline urgency (sooner deadline = higher priority)
        try:
            deadline_date = datetime.fromisoformat(project.deadline)
            days_until = (deadline_date - datetime.now()).days

            if days_until <= 1:
                priority += 1000  # URGENT
            elif days_until <= 3:
                priority += 500
            elif days_until <= 7:
                priority += 200
            else:
                priority += 100

        except:
            priority += 100

        # Tier-based priority
        tier_priority = {
            'premium': 100,
            'standard': 50,
            'basic': 25
        }
        priority += tier_priority.get(project.budget_tier, 0)

        return priority

    def process_production_queue(self):
        """
        Process the production queue - generate videos for queued projects.
        """
        if not self.production_queue:
            logger.info("Production queue empty")
            return

        # Get highest priority project
        queue_item = self.production_queue[0]

        if queue_item['status'] != 'queued':
            logger.info(f"Top project already in progress: {queue_item['project_id']}")
            return

        logger.info(f"\n{'='*70}")
        logger.info(f"STARTING PRODUCTION: {queue_item['song_title']}")
        logger.info(f"Priority Score: {queue_item['priority']}")
        logger.info(f"Revenue: ${queue_item['revenue']}")
        logger.info(f"{'='*70}\n")

        # Update status
        queue_item['status'] = 'in_production'
        queue_item['production_started'] = datetime.now().isoformat()
        self.save_production_queue()

        try:
            # Load project
            project = self.video_engine.load_project(queue_item['project_id'])

            if not project:
                logger.error(f"Could not load project: {queue_item['project_id']}")
                queue_item['status'] = 'error'
                self.save_production_queue()
                return

            # Run production pipeline
            results = self.video_engine.produce_complete_video(project)

            # Update queue item
            queue_item['status'] = 'completed'
            queue_item['production_completed'] = datetime.now().isoformat()
            queue_item['results'] = results

            # Remove from queue (move to completed)
            self.production_queue.remove(queue_item)
            self.save_production_queue()

            # Track stats
            self.update_stats(project, results)

            logger.info(f"PRODUCTION COMPLETE: {queue_item['song_title']}")
            logger.info(f"Revenue generated: ${queue_item['revenue']}")

        except Exception as e:
            logger.error(f"Production error: {e}")
            queue_item['status'] = 'error'
            queue_item['error'] = str(e)
            self.save_production_queue()

    def update_stats(self, project: VideoProject, results: Dict):
        """Track production statistics and revenue"""
        stats = self.load_stats()

        # Update counters
        stats['total_projects'] = stats.get('total_projects', 0) + 1
        stats['total_revenue'] = stats.get('total_revenue', 0) + project.revenue

        # Track by tier
        tier_stats = stats.get('by_tier', {})
        tier = project.budget_tier
        tier_stats[tier] = tier_stats.get(tier, {'count': 0, 'revenue': 0})
        tier_stats[tier]['count'] += 1
        tier_stats[tier]['revenue'] += project.revenue
        stats['by_tier'] = tier_stats

        # Track by month
        month_key = datetime.now().strftime('%Y-%m')
        monthly_stats = stats.get('by_month', {})
        monthly_stats[month_key] = monthly_stats.get(month_key, {'count': 0, 'revenue': 0})
        monthly_stats[month_key]['count'] += 1
        monthly_stats[month_key]['revenue'] += project.revenue
        stats['by_month'] = monthly_stats

        # Recent projects
        recent = stats.get('recent_projects', [])
        recent.insert(0, {
            'project_id': project.project_id,
            'song_title': project.song_title,
            'artist': project.artist_name,
            'revenue': project.revenue,
            'completed': datetime.now().isoformat()
        })
        stats['recent_projects'] = recent[:10]  # Keep last 10

        # Calculate people helped
        stats['estimated_people_helped'] = int(stats['total_revenue'] / 75)

        # Update timestamp
        stats['last_updated'] = datetime.now().isoformat()

        self.save_stats(stats)

    def load_stats(self) -> Dict:
        """Load statistics from disk"""
        if os.path.exists(self.stats_file):
            with open(self.stats_file, 'r') as f:
                return json.load(f)
        return {}

    def save_stats(self, stats: Dict):
        """Save statistics to disk"""
        Path(self.stats_file).parent.mkdir(parents=True, exist_ok=True)
        with open(self.stats_file, 'w') as f:
            json.dump(stats, f, indent=2)

    def generate_daily_report(self):
        """Generate daily production and revenue report"""
        stats = self.load_stats()

        report = f"""
{'='*70}
CRAFT DAILY PRODUCTION REPORT
{datetime.now().strftime('%A, %B %d, %Y')}
{'='*70}

OVERALL STATISTICS:
  Total Projects Completed: {stats.get('total_projects', 0)}
  Total Revenue Generated: ${stats.get('total_revenue', 0):,.2f}
  Estimated People Helped: {stats.get('estimated_people_helped', 0)}

REVENUE BY TIER:
"""
        for tier, data in stats.get('by_tier', {}).items():
            report += f"  {tier.upper()}: {data['count']} projects, ${data['revenue']:,.2f}\n"

        report += f"\nCURRENT PRODUCTION QUEUE:\n"
        report += f"  Projects in queue: {len([q for q in self.production_queue if q['status'] == 'queued'])}\n"
        report += f"  Projects in production: {len([q for q in self.production_queue if q['status'] == 'in_production'])}\n"

        if self.production_queue:
            report += f"\n  NEXT UP:\n"
            for i, item in enumerate(self.production_queue[:3], 1):
                report += f"    {i}. {item['song_title']} (${item['revenue']}, Priority: {item['priority']})\n"

        report += f"\nRECENT COMPLETIONS:\n"
        for project in stats.get('recent_projects', [])[:5]:
            report += f"  - {project['song_title']} by {project['artist']} (${project['revenue']})\n"

        report += f"\n{'='*70}\n"
        report += f"CRAFT is operational and generating revenue that heals.\n"
        report += f"{'='*70}\n"

        logger.info(report)

        # Send to Unc
        try:
            from notify_unc import send_notification_to_unc

            send_notification_to_unc(
                from_agent="CRAFT",
                subject=f"Daily Report: {stats.get('total_projects', 0)} Projects, ${stats.get('total_revenue', 0):,.2f} Revenue",
                message=report,
                priority="low"
            )
        except Exception as e:
            logger.error(f"Could not send daily report: {e}")

        return report

    def check_deadlines(self):
        """Check for approaching deadlines and send alerts"""
        logger.info("Checking project deadlines...")

        for queue_item in self.production_queue:
            if queue_item['status'] != 'queued':
                continue

            try:
                deadline = datetime.fromisoformat(queue_item['deadline'])
                days_until = (deadline - datetime.now()).days

                if days_until <= 1 and queue_item.get('urgent_alert_sent') != True:
                    self._send_urgent_alert(queue_item)
                    queue_item['urgent_alert_sent'] = True
                    self.save_production_queue()

            except:
                pass

    def _send_urgent_alert(self, queue_item: Dict):
        """Send urgent deadline alert"""
        try:
            from notify_unc import send_notification_to_unc

            send_notification_to_unc(
                from_agent="CRAFT",
                subject=f"URGENT: Deadline Approaching - {queue_item['song_title']}",
                message=f"""
URGENT PRODUCTION ALERT

Project: {queue_item['song_title']}
Client: {queue_item['client_name']}
Deadline: {queue_item['deadline']}
Revenue: ${queue_item['revenue']}

This project needs to begin production immediately to meet deadline.

Priority: {queue_item['priority']}
Status: {queue_item['status']}

CRAFT Orchestrator
""",
                priority="high"
            )
        except:
            pass

    def run_autonomous_cycle(self):
        """
        One complete autonomous production cycle.
        Called by scheduler.
        """
        logger.info("\n" + "="*70)
        logger.info("CRAFT AUTONOMOUS CYCLE STARTING")
        logger.info("="*70 + "\n")

        # 1. Check for new submissions
        self.check_for_new_submissions()

        # 2. Check deadlines
        self.check_deadlines()

        # 3. Process production queue
        self.process_production_queue()

        logger.info("\n" + "="*70)
        logger.info("CRAFT AUTONOMOUS CYCLE COMPLETE")
        logger.info("="*70 + "\n")

    def start_autonomous_mode(self):
        """
        Start the autonomous 24/7 production system.
        Runs continuously, processing projects as they arrive.
        """
        logger.info("\n" + "="*70)
        logger.info("CRAFT AUTONOMOUS MODE ACTIVATED")
        logger.info("24/7 Revenue Generation System")
        logger.info("="*70 + "\n")

        # Schedule autonomous cycles
        schedule.every(15).minutes.do(self.run_autonomous_cycle)

        # Schedule deadline checks
        schedule.every(1).hour.do(self.check_deadlines)

        # Schedule daily report
        schedule.every().day.at("09:00").do(self.generate_daily_report)

        # Run initial cycle
        self.run_autonomous_cycle()

        # Run forever
        logger.info("CRAFT is now running autonomously...")
        logger.info("Press Ctrl+C to stop")

        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("\nCRAFT autonomous mode stopped by user")
        except Exception as e:
            logger.error(f"Error in autonomous mode: {e}")


def main():
    """
    Main entry point for CRAFT autonomous system.
    """
    print("\n" + "="*70)
    print("CRAFT VIDEO PRODUCTION SYSTEM")
    print("Autonomous Revenue Generation for Mental Health Mission")
    print("="*70 + "\n")

    orchestrator = CRAFTOrchestrator()

    print("Options:")
    print("1. Start autonomous mode (24/7)")
    print("2. Run single production cycle")
    print("3. Generate daily report")
    print("4. View production queue")
    print("5. View statistics")

    choice = input("\nSelect option (1-5): ").strip()

    if choice == '1':
        orchestrator.start_autonomous_mode()
    elif choice == '2':
        orchestrator.run_autonomous_cycle()
    elif choice == '3':
        orchestrator.generate_daily_report()
    elif choice == '4':
        print("\nPRODUCTION QUEUE:")
        for i, item in enumerate(orchestrator.production_queue, 1):
            print(f"{i}. {item['song_title']} - ${item['revenue']} (Priority: {item['priority']}, Status: {item['status']})")
    elif choice == '5':
        stats = orchestrator.load_stats()
        print("\nCRAFT STATISTICS:")
        print(json.dumps(stats, indent=2))
    else:
        print("Invalid option")


if __name__ == "__main__":
    main()
