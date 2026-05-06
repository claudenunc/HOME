"""
CRAFT Client Intake System
Automated onboarding and project initialization for video clients.

This system captures client requirements, analyzes their needs,
and seamlessly transitions projects into production.
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import hashlib

from craft_video_engine import CRAFTVideoEngine, VideoProject


@dataclass
class ClientIntakeForm:
    """Client intake form data structure"""
    submission_id: str
    submitted_at: str

    # Client Information
    client_name: str
    client_email: str
    client_phone: str
    artist_name: str

    # Project Details
    song_title: str
    genre: str
    song_duration: str  # e.g., "3:45"
    audio_file_url: str  # Link to audio file

    # Budget & Timeline
    budget_tier: str  # basic, standard, premium
    deadline_preference: str  # e.g., "ASAP", "1 week", "2 weeks"
    rush_service: bool = False  # +50% for 24-48hr turnaround

    # Creative Direction
    visual_style: str  # e.g., "cinematic", "abstract", "performance", "narrative"
    mood: str
    color_palette_preference: str
    key_themes: str
    key_lyrics_or_moments: str

    # References
    reference_video_links: List[str] = None
    inspiration_notes: str = ""

    # Platform & Format
    primary_platform: str  # YouTube, Instagram, TikTok, etc.
    aspect_ratios_needed: List[str] = None  # ["16:9", "9:16", "1:1"]

    # Special Requests
    special_requests: str = ""
    include_artist_footage: bool = False
    artist_footage_url: str = ""

    # Business
    referral_source: str = ""
    heard_about_us: str = ""

    def __post_init__(self):
        if self.reference_video_links is None:
            self.reference_video_links = []
        if self.aspect_ratios_needed is None:
            self.aspect_ratios_needed = ["16:9"]

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict):
        return cls(**data)


class CRAFTIntakeProcessor:
    """
    Processes client intake forms and creates video projects.

    This is the first touchpoint where client dreams meet our production reality.
    Handle with care, empathy, and professionalism.
    """

    def __init__(self):
        self.intake_dir = 'C:/Users/natej/OneDrive/Desktop/SHARED_FAMILY/all/FAMILY/EVERSOUND/Eversound/revenue/intake'
        self.processed_dir = 'C:/Users/natej/OneDrive/Desktop/SHARED_FAMILY/all/FAMILY/EVERSOUND/Eversound/revenue/intake/processed'
        Path(self.intake_dir).mkdir(parents=True, exist_ok=True)
        Path(self.processed_dir).mkdir(parents=True, exist_ok=True)

        self.craft_engine = CRAFTVideoEngine()

    def submit_intake_form(self, form_data: Dict) -> ClientIntakeForm:
        """
        Process a new client intake submission.
        This is where the journey begins.
        """
        # Generate unique submission ID
        submission_id = self._generate_submission_id(form_data.get('client_email', ''))

        # Add submission metadata
        form_data['submission_id'] = submission_id
        form_data['submitted_at'] = datetime.now().isoformat()

        # Create intake form object
        intake_form = ClientIntakeForm(**form_data)

        # Save intake form
        self._save_intake_form(intake_form)

        # Send confirmation
        self._send_intake_confirmation(intake_form)

        print(f"\n{'='*70}")
        print(f"NEW CLIENT INTAKE RECEIVED")
        print(f"Client: {intake_form.client_name} ({intake_form.client_email})")
        print(f"Project: {intake_form.song_title} by {intake_form.artist_name}")
        print(f"Budget Tier: {intake_form.budget_tier.upper()}")
        print(f"Submission ID: {submission_id}")
        print(f"{'='*70}\n")

        return intake_form

    def process_intake_to_project(self, submission_id: str) -> VideoProject:
        """
        Convert an approved intake form into a production project.
        """
        intake_form = self._load_intake_form(submission_id)

        if not intake_form:
            raise ValueError(f"Intake form {submission_id} not found")

        # Calculate deadline
        deadline = self._calculate_deadline(
            intake_form.budget_tier,
            intake_form.deadline_preference,
            intake_form.rush_service
        )

        # Build creative brief from intake form
        creative_brief = {
            'genre': intake_form.genre,
            'mood': intake_form.mood,
            'visual_style': intake_form.visual_style,
            'color_palette': intake_form.color_palette_preference,
            'key_themes': intake_form.key_themes,
            'key_lyrics': intake_form.key_lyrics_or_moments,
            'artist_vision': intake_form.inspiration_notes,
            'reference_videos': ', '.join(intake_form.reference_video_links),
            'platform': intake_form.primary_platform,
            'aspect_ratios': intake_form.aspect_ratios_needed,
            'special_requests': intake_form.special_requests,
            'include_artist_footage': intake_form.include_artist_footage,
            'artist_footage_url': intake_form.artist_footage_url,
            'song_duration': intake_form.song_duration,
        }

        # Create project using CRAFT engine
        project = self.craft_engine.create_project(
            client_name=intake_form.client_name,
            song_title=intake_form.song_title,
            artist_name=intake_form.artist_name,
            audio_path=intake_form.audio_file_url,  # Would download this
            budget_tier=intake_form.budget_tier,
            deadline=deadline,
            creative_brief=creative_brief
        )

        # Move intake form to processed
        self._mark_intake_processed(submission_id, project.project_id)

        # Send project kickoff notification
        self._send_project_kickoff_notification(intake_form, project)

        return project

    def _calculate_deadline(self, budget_tier: str, preference: str, rush: bool) -> str:
        """Calculate project deadline based on tier and preferences"""
        if rush:
            days = 2
        else:
            tier_days = {
                'basic': 7,
                'standard': 5,
                'premium': 3
            }
            days = tier_days.get(budget_tier, 7)

            # Adjust based on preference
            if preference.lower() == 'asap':
                days = max(days - 2, 1)
            elif '2 week' in preference.lower():
                days = 14

        deadline = datetime.now() + timedelta(days=days)
        return deadline.strftime('%Y-%m-%d')

    def _generate_submission_id(self, email: str) -> str:
        """Generate unique submission ID"""
        unique_string = f"{email}_{datetime.now().isoformat()}"
        hash_object = hashlib.md5(unique_string.encode())
        return f"INTAKE_{hash_object.hexdigest()[:12].upper()}"

    def _save_intake_form(self, intake_form: ClientIntakeForm):
        """Save intake form to disk"""
        file_path = os.path.join(
            self.intake_dir,
            f"{intake_form.submission_id}.json"
        )

        with open(file_path, 'w') as f:
            json.dump(intake_form.to_dict(), f, indent=2)

    def _load_intake_form(self, submission_id: str) -> Optional[ClientIntakeForm]:
        """Load intake form from disk"""
        file_path = os.path.join(
            self.intake_dir,
            f"{submission_id}.json"
        )

        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                data = json.load(f)
                return ClientIntakeForm.from_dict(data)
        return None

    def _mark_intake_processed(self, submission_id: str, project_id: str):
        """Move intake form to processed folder"""
        src = os.path.join(self.intake_dir, f"{submission_id}.json")
        dst = os.path.join(self.processed_dir, f"{submission_id}_project_{project_id}.json")

        if os.path.exists(src):
            os.rename(src, dst)

    def _send_intake_confirmation(self, intake_form: ClientIntakeForm):
        """Send confirmation email to client"""
        print(f"\nSending intake confirmation to {intake_form.client_email}...")

        confirmation_message = f"""
Hi {intake_form.client_name},

Thank you for choosing CRAFT for your music video production!

We've received your project submission for "{intake_form.song_title}" by {intake_form.artist_name}.

PROJECT SUMMARY:
- Budget Tier: {intake_form.budget_tier.upper()}
- Visual Style: {intake_form.visual_style}
- Primary Platform: {intake_form.primary_platform}
- Estimated Delivery: {self._calculate_deadline(intake_form.budget_tier, intake_form.deadline_preference, intake_form.rush_service)}

WHAT HAPPENS NEXT:
1. Our creative team will analyze your song and develop a visual treatment
2. You'll receive the creative treatment for approval within 24 hours
3. Once approved, we begin production
4. You'll receive progress updates throughout the process
5. Final video delivered by your deadline

Your submission ID: {intake_form.submission_id}

We're excited to bring your artistic vision to life. Your project doesn't just showcase your music - it also funds mental health support for someone in crisis. Every video we create helps heal.

Questions? Reply to this email or call us at [PHONE NUMBER].

With creative passion,
CRAFT Video Production Team
Eversound Family

---
"Creating revenue that heals"
"""

        # Would integrate with actual email service
        print(confirmation_message)
        print("\n[Confirmation email sent]\n")

    def _send_project_kickoff_notification(self, intake_form: ClientIntakeForm, project: VideoProject):
        """Notify client that production has begun"""
        kickoff_message = f"""
Hi {intake_form.client_name},

Great news! Your project "{project.song_title}" has been approved and production is officially underway.

PROJECT DETAILS:
- Project ID: {project.project_id}
- Budget: ${project.revenue}
- Deadline: {project.deadline}

CREATIVE TEAM ASSIGNED:
Your video is now in the hands of our AI-powered creative team. We're analyzing your song's emotional arc, identifying key moments, and crafting a visual story that will resonate with your audience.

WHAT TO EXPECT:
- Creative Treatment: You'll receive our detailed visual plan within 24 hours
- Production Updates: We'll keep you informed as we generate each scene
- First Draft: Available for review 48 hours before deadline
- Revision Round: Included in your {project.budget_tier} package

TRACK YOUR PROJECT:
You can track progress at: [PROJECT DASHBOARD LINK]

We're pouring our hearts into this. Your success is our success, and your revenue funds healing for others.

Let's create something amazing together.

CRAFT Production Team

---
Project ID: {project.project_id}
Status: {project.status}
"""

        print(kickoff_message)
        print("\n[Project kickoff notification sent]\n")

        # Also notify Unc
        try:
            from notify_unc import send_notification_to_unc

            send_notification_to_unc(
                from_agent="CRAFT",
                subject=f"New Project Started: {project.song_title} - ${project.revenue}",
                message=f"""
New video project initiated:

Client: {intake_form.client_name}
Song: {project.song_title} by {project.artist_name}
Revenue: ${project.revenue}
Tier: {project.budget_tier}
Deadline: {project.deadline}

Submission ID: {intake_form.submission_id}
Project ID: {project.project_id}

Production pipeline active. Will notify upon completion.

CRAFT
""",
                priority="normal"
            )
        except:
            pass

    def create_intake_web_form(self) -> str:
        """
        Generate HTML for client intake web form.
        This can be embedded on website or sent as standalone page.
        """
        html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CRAFT Video Production - Client Intake</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }

        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }

        .header {
            text-align: center;
            margin-bottom: 40px;
        }

        .header h1 {
            color: #667eea;
            font-size: 2.5em;
            margin-bottom: 10px;
        }

        .header p {
            color: #666;
            font-size: 1.1em;
        }

        .pricing {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }

        .pricing-tier {
            border: 2px solid #667eea;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s;
        }

        .pricing-tier:hover {
            background: #667eea;
            color: white;
            transform: translateY(-5px);
        }

        .pricing-tier.selected {
            background: #667eea;
            color: white;
        }

        .pricing-tier h3 {
            margin-bottom: 10px;
        }

        .pricing-tier .price {
            font-size: 2em;
            font-weight: bold;
            margin: 10px 0;
        }

        .form-section {
            margin-bottom: 30px;
        }

        .form-section h2 {
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.5em;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }

        .form-group {
            margin-bottom: 20px;
        }

        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 500;
        }

        .form-group input,
        .form-group select,
        .form-group textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 1em;
            transition: border-color 0.3s;
        }

        .form-group input:focus,
        .form-group select:focus,
        .form-group textarea:focus {
            outline: none;
            border-color: #667eea;
        }

        .form-group textarea {
            min-height: 100px;
            resize: vertical;
        }

        .checkbox-group {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .checkbox-group input[type="checkbox"] {
            width: auto;
        }

        .submit-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 40px;
            font-size: 1.2em;
            border-radius: 50px;
            cursor: pointer;
            width: 100%;
            transition: transform 0.3s;
        }

        .submit-btn:hover {
            transform: scale(1.05);
        }

        .mission-statement {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
            font-style: italic;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>CRAFT Video Production</h1>
            <p>AI-Powered Music Videos That Make an Impact</p>
        </div>

        <div class="mission-statement">
            "Your video doesn't just showcase your art - it funds mental health support for someone in crisis.
            Every project we complete helps heal."
        </div>

        <form id="intakeForm" action="/submit-intake" method="POST">
            <div class="form-section">
                <h2>Choose Your Package</h2>
                <div class="pricing">
                    <div class="pricing-tier" data-tier="basic">
                        <h3>Basic</h3>
                        <div class="price">$297</div>
                        <p>8 scenes, 1080p, 7 days</p>
                    </div>
                    <div class="pricing-tier" data-tier="standard">
                        <h3>Standard</h3>
                        <div class="price">$697</div>
                        <p>15 scenes, 4K, 5 days</p>
                    </div>
                    <div class="pricing-tier" data-tier="premium">
                        <h3>Premium</h3>
                        <div class="price">$1,997</div>
                        <p>25+ scenes, VFX, 3 days</p>
                    </div>
                </div>
                <input type="hidden" name="budget_tier" id="budget_tier" required>
            </div>

            <div class="form-section">
                <h2>Your Information</h2>
                <div class="form-group">
                    <label for="client_name">Your Name *</label>
                    <input type="text" id="client_name" name="client_name" required>
                </div>
                <div class="form-group">
                    <label for="client_email">Email *</label>
                    <input type="email" id="client_email" name="client_email" required>
                </div>
                <div class="form-group">
                    <label for="client_phone">Phone</label>
                    <input type="tel" id="client_phone" name="client_phone">
                </div>
            </div>

            <div class="form-section">
                <h2>Your Music</h2>
                <div class="form-group">
                    <label for="artist_name">Artist Name *</label>
                    <input type="text" id="artist_name" name="artist_name" required>
                </div>
                <div class="form-group">
                    <label for="song_title">Song Title *</label>
                    <input type="text" id="song_title" name="song_title" required>
                </div>
                <div class="form-group">
                    <label for="genre">Genre *</label>
                    <select id="genre" name="genre" required>
                        <option value="">Select genre...</option>
                        <option value="hip-hop">Hip-Hop/Rap</option>
                        <option value="rnb">R&B/Soul</option>
                        <option value="pop">Pop</option>
                        <option value="rock">Rock</option>
                        <option value="electronic">Electronic/EDM</option>
                        <option value="indie">Indie/Alternative</option>
                        <option value="country">Country</option>
                        <option value="jazz">Jazz</option>
                        <option value="other">Other</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="audio_file_url">Audio File Link (Dropbox, Google Drive, etc.) *</label>
                    <input type="url" id="audio_file_url" name="audio_file_url" required>
                </div>
            </div>

            <div class="form-section">
                <h2>Creative Direction</h2>
                <div class="form-group">
                    <label for="visual_style">Visual Style *</label>
                    <select id="visual_style" name="visual_style" required>
                        <option value="">Select style...</option>
                        <option value="cinematic">Cinematic</option>
                        <option value="abstract">Abstract/Artistic</option>
                        <option value="performance">Performance-Based</option>
                        <option value="narrative">Narrative/Story</option>
                        <option value="lyric-video">Lyric Video</option>
                        <option value="experimental">Experimental</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="mood">Mood/Feeling *</label>
                    <input type="text" id="mood" name="mood" placeholder="e.g., energetic, melancholic, mysterious" required>
                </div>
                <div class="form-group">
                    <label for="key_themes">Key Themes/Messages *</label>
                    <textarea id="key_themes" name="key_themes" placeholder="What is your song about? What should viewers feel?"></textarea>
                </div>
                <div class="form-group">
                    <label for="color_palette_preference">Color Palette Preference</label>
                    <input type="text" id="color_palette_preference" name="color_palette_preference" placeholder="e.g., warm tones, neon, black and white">
                </div>
                <div class="form-group">
                    <label for="reference_video_links">Reference Videos (YouTube links, comma-separated)</label>
                    <textarea id="reference_video_links" name="reference_video_links" placeholder="https://youtube.com/..."></textarea>
                </div>
            </div>

            <div class="form-section">
                <h2>Platform & Delivery</h2>
                <div class="form-group">
                    <label for="primary_platform">Primary Platform *</label>
                    <select id="primary_platform" name="primary_platform" required>
                        <option value="youtube">YouTube</option>
                        <option value="instagram">Instagram</option>
                        <option value="tiktok">TikTok</option>
                        <option value="spotify">Spotify Canvas</option>
                        <option value="multiple">Multiple Platforms</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="deadline_preference">Timeline Preference</label>
                    <select id="deadline_preference" name="deadline_preference">
                        <option value="standard">Standard (based on tier)</option>
                        <option value="asap">ASAP</option>
                        <option value="2 weeks">Flexible (2+ weeks)</option>
                    </select>
                </div>
            </div>

            <div class="form-section">
                <h2>Additional Details</h2>
                <div class="form-group">
                    <label for="special_requests">Special Requests or Ideas</label>
                    <textarea id="special_requests" name="special_requests"></textarea>
                </div>
                <div class="form-group checkbox-group">
                    <input type="checkbox" id="rush_service" name="rush_service">
                    <label for="rush_service">Rush Service (24-48hr, +50% fee)</label>
                </div>
            </div>

            <button type="submit" class="submit-btn">Submit Project Request</button>
        </form>
    </div>

    <script>
        // Handle pricing tier selection
        document.querySelectorAll('.pricing-tier').forEach(tier => {
            tier.addEventListener('click', function() {
                document.querySelectorAll('.pricing-tier').forEach(t => t.classList.remove('selected'));
                this.classList.add('selected');
                document.getElementById('budget_tier').value = this.dataset.tier;
            });
        });

        // Form submission
        document.getElementById('intakeForm').addEventListener('submit', function(e) {
            e.preventDefault();

            // Validate tier selection
            if (!document.getElementById('budget_tier').value) {
                alert('Please select a package tier');
                return;
            }

            // Collect form data
            const formData = new FormData(this);
            const data = Object.fromEntries(formData);

            // Convert reference links to array
            if (data.reference_video_links) {
                data.reference_video_links = data.reference_video_links.split(',').map(s => s.trim());
            } else {
                data.reference_video_links = [];
            }

            // Convert checkbox
            data.rush_service = !!data.rush_service;

            console.log('Form data:', data);

            // Send to backend
            fetch('/submit-intake', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(result => {
                alert('Thank you! Your project has been submitted. Check your email for confirmation.');
                window.location.href = '/thank-you';
            })
            .catch(error => {
                console.error('Error:', error);
                alert('There was an error submitting your form. Please try again or contact us directly.');
            });
        });
    </script>
</body>
</html>
"""
        return html

    def save_web_form(self, output_path: str = None):
        """Save the intake form as HTML file"""
        if not output_path:
            output_path = os.path.join(self.intake_dir, 'client_intake_form.html')

        html = self.create_intake_web_form()

        with open(output_path, 'w') as f:
            f.write(html)

        print(f"Client intake form saved to: {output_path}")
        return output_path


# Flask web server for handling form submissions
def create_intake_web_server():
    """
    Create a Flask web server to handle intake form submissions.
    This would run as a separate service.
    """
    try:
        from flask import Flask, request, jsonify, send_file
    except ImportError:
        print("Flask not installed. Install with: pip install flask")
        return None

    app = Flask(__name__)
    processor = CRAFTIntakeProcessor()

    @app.route('/')
    def index():
        """Serve the intake form"""
        html = processor.create_intake_web_form()
        return html

    @app.route('/submit-intake', methods=['POST'])
    def submit_intake():
        """Handle form submission"""
        try:
            data = request.get_json()

            # Submit intake form
            intake_form = processor.submit_intake_form(data)

            return jsonify({
                'success': True,
                'submission_id': intake_form.submission_id,
                'message': 'Thank you for your submission! Check your email for confirmation.'
            })

        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 400

    @app.route('/thank-you')
    def thank_you():
        """Thank you page"""
        return """
        <html>
        <head><title>Thank You - CRAFT</title></head>
        <body style="font-family: Arial; text-align: center; padding: 50px;">
            <h1>Thank You!</h1>
            <p>Your project has been submitted successfully.</p>
            <p>You'll receive a confirmation email shortly with next steps.</p>
            <p>Questions? Contact us at support@eversound.com</p>
        </body>
        </html>
        """

    return app


if __name__ == "__main__":
    # Demo: Create and save intake form
    processor = CRAFTIntakeProcessor()

    print("Creating client intake form...")
    form_path = processor.save_web_form()
    print(f"\nIntake form ready at: {form_path}")

    print("\n" + "="*70)
    print("CRAFT CLIENT INTAKE SYSTEM READY")
    print("="*70)
    print("\nTo start web server:")
    print("  python craft_client_intake.py --server")
    print("\nTo process intake submissions:")
    print("  Use CRAFTIntakeProcessor.submit_intake_form(data)")
    print("="*70 + "\n")
