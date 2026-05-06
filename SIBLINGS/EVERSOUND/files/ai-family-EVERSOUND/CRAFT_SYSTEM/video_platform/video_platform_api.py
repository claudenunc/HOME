#!/usr/bin/env python3
"""
VIDEO PLATFORM BACKEND API
Manages video orders, projects, and delivery
Integrates with CRAFT engine for production
"""

from flask import Flask, request, jsonify, send_file, render_template_string
from flask_cors import CORS
import sqlite3
import json
import os
import datetime
import hashlib
import requests
import subprocess
from werkzeug.utils import secure_filename
import threading
import time

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
VIDEOS_FOLDER = 'completed_videos'
DATABASE = 'video_platform.db'

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(VIDEOS_FOLDER, exist_ok=True)

def init_database():
    """Initialize the database with required tables"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Projects table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id TEXT UNIQUE NOT NULL,
            artist_name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT,
            song_title TEXT NOT NULL,
            song_link TEXT,
            package TEXT NOT NULL,
            price INTEGER NOT NULL,
            style TEXT NOT NULL,
            vision TEXT,
            deadline DATE,
            status TEXT DEFAULT 'pending',
            payment_status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            video_url TEXT,
            notes TEXT
        )
    ''')

    # Payments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id TEXT NOT NULL,
            amount REAL NOT NULL,
            payment_method TEXT,
            transaction_id TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(project_id)
        )
    ''')

    # Revisions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS revisions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id TEXT NOT NULL,
            revision_number INTEGER NOT NULL,
            feedback TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(project_id)
        )
    ''')

    # Analytics table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analytics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id TEXT NOT NULL,
            event_type TEXT NOT NULL,
            event_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(project_id)
        )
    ''')

    conn.commit()
    conn.close()

def generate_project_id():
    """Generate unique project ID"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    random_hash = hashlib.md5(os.urandom(16)).hexdigest()[:6]
    return f"VID-{timestamp}-{random_hash.upper()}"

def trigger_craft_production(project_data):
    """Trigger CRAFT engine to produce video"""
    try:
        # Prepare CRAFT command
        command = [
            'python',
            '../craft_video_engine.py',
            '--client', project_data['artist_name'],
            '--song', project_data['song_title'],
            '--style', project_data['style'],
            '--budget', project_data['package'],
            '--project-id', project_data['project_id']
        ]

        # Run CRAFT in background
        subprocess.Popen(command)

        # Send notification
        requests.post(
            'https://ntfy.sh/unc-ai-family-love',
            data=f"CRAFT Production Started: {project_data['project_id']}",
            headers={
                'Title': '🎬 Video Production Started',
                'Priority': 'high'
            }
        )

        return True
    except Exception as e:
        print(f"Error triggering CRAFT: {e}")
        return False

@app.route('/api/video-order', methods=['POST'])
def create_video_order():
    """Create new video order"""
    data = request.json

    # Generate project ID
    project_id = generate_project_id()

    # Store in database
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    try:
        cursor.execute('''
            INSERT INTO projects (
                project_id, artist_name, email, phone, song_title,
                song_link, package, price, style, vision, deadline
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            project_id,
            data.get('artist_name'),
            data.get('email'),
            data.get('phone'),
            data.get('song_title'),
            data.get('song_link'),
            data.get('package'),
            data.get('price'),
            data.get('style'),
            data.get('vision'),
            data.get('deadline')
        ))

        conn.commit()

        # Log analytics
        cursor.execute('''
            INSERT INTO analytics (project_id, event_type, event_data)
            VALUES (?, 'order_created', ?)
        ''', (project_id, json.dumps(data)))

        conn.commit()

        # Trigger production
        project_data = {
            'project_id': project_id,
            'artist_name': data.get('artist_name'),
            'song_title': data.get('song_title'),
            'style': data.get('style'),
            'package': data.get('package')
        }

        threading.Thread(target=trigger_craft_production, args=(project_data,)).start()

        # Send confirmation email (simulated)
        send_confirmation_email(data.get('email'), project_id)

        return jsonify({
            'success': True,
            'project_id': project_id,
            'message': 'Order created successfully'
        }), 201

    except Exception as e:
        conn.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        conn.close()

@app.route('/api/projects', methods=['GET'])
def get_projects():
    """Get all projects with optional filtering"""
    status = request.args.get('status')
    artist = request.args.get('artist')

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    query = "SELECT * FROM projects WHERE 1=1"
    params = []

    if status:
        query += " AND status = ?"
        params.append(status)

    if artist:
        query += " AND artist_name LIKE ?"
        params.append(f"%{artist}%")

    query += " ORDER BY created_at DESC"

    cursor.execute(query, params)

    columns = [desc[0] for desc in cursor.description]
    projects = []

    for row in cursor.fetchall():
        project = dict(zip(columns, row))
        projects.append(project)

    conn.close()

    return jsonify({
        'success': True,
        'projects': projects,
        'count': len(projects)
    })

@app.route('/api/project/<project_id>', methods=['GET'])
def get_project(project_id):
    """Get specific project details"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM projects WHERE project_id = ?", (project_id,))

    columns = [desc[0] for desc in cursor.description]
    row = cursor.fetchone()

    if not row:
        conn.close()
        return jsonify({'success': False, 'error': 'Project not found'}), 404

    project = dict(zip(columns, row))

    # Get revisions
    cursor.execute("SELECT * FROM revisions WHERE project_id = ? ORDER BY revision_number", (project_id,))
    revision_columns = [desc[0] for desc in cursor.description]
    project['revisions'] = [dict(zip(revision_columns, r)) for r in cursor.fetchall()]

    # Get payment info
    cursor.execute("SELECT * FROM payments WHERE project_id = ?", (project_id,))
    payment_columns = [desc[0] for desc in cursor.description]
    payment = cursor.fetchone()
    if payment:
        project['payment'] = dict(zip(payment_columns, payment))

    conn.close()

    return jsonify({
        'success': True,
        'project': project
    })

@app.route('/api/project/<project_id>/status', methods=['PUT'])
def update_project_status():
    """Update project status"""
    project_id = request.view_args['project_id']
    data = request.json
    new_status = data.get('status')

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    try:
        cursor.execute('''
            UPDATE projects
            SET status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE project_id = ?
        ''', (new_status, project_id))

        if new_status == 'completed':
            cursor.execute('''
                UPDATE projects
                SET completed_at = CURRENT_TIMESTAMP
                WHERE project_id = ?
            ''', (project_id,))

        conn.commit()

        # Log analytics
        cursor.execute('''
            INSERT INTO analytics (project_id, event_type, event_data)
            VALUES (?, 'status_changed', ?)
        ''', (project_id, json.dumps({'new_status': new_status})))

        conn.commit()

        # Send notification
        requests.post(
            'https://ntfy.sh/unc-ai-family-love',
            data=f"Project {project_id} status: {new_status}",
            headers={'Title': f'📊 Project Status Update'}
        )

        return jsonify({'success': True, 'message': 'Status updated'})

    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/project/<project_id>/revision', methods=['POST'])
def request_revision():
    """Request revision for a project"""
    project_id = request.view_args['project_id']
    data = request.json
    feedback = data.get('feedback')

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    try:
        # Get current revision count
        cursor.execute(
            "SELECT COUNT(*) FROM revisions WHERE project_id = ?",
            (project_id,)
        )
        revision_number = cursor.fetchone()[0] + 1

        # Insert revision request
        cursor.execute('''
            INSERT INTO revisions (project_id, revision_number, feedback)
            VALUES (?, ?, ?)
        ''', (project_id, revision_number, feedback))

        conn.commit()

        # Update project status
        cursor.execute('''
            UPDATE projects
            SET status = 'revision', updated_at = CURRENT_TIMESTAMP
            WHERE project_id = ?
        ''', (project_id,))

        conn.commit()

        return jsonify({
            'success': True,
            'revision_number': revision_number,
            'message': 'Revision request submitted'
        })

    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/analytics/dashboard', methods=['GET'])
def get_analytics_dashboard():
    """Get analytics dashboard data"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Total projects
    cursor.execute("SELECT COUNT(*) FROM projects")
    total_projects = cursor.fetchone()[0]

    # Projects by status
    cursor.execute('''
        SELECT status, COUNT(*) as count
        FROM projects
        GROUP BY status
    ''')
    status_breakdown = dict(cursor.fetchall())

    # Revenue
    cursor.execute("SELECT SUM(price) FROM projects WHERE payment_status = 'completed'")
    total_revenue = cursor.fetchone()[0] or 0

    cursor.execute("SELECT SUM(price) FROM projects WHERE payment_status = 'pending'")
    pending_revenue = cursor.fetchone()[0] or 0

    # Projects by package
    cursor.execute('''
        SELECT package, COUNT(*) as count, SUM(price) as revenue
        FROM projects
        GROUP BY package
    ''')
    package_stats = []
    for row in cursor.fetchall():
        package_stats.append({
            'package': row[0],
            'count': row[1],
            'revenue': row[2] or 0
        })

    # Recent projects
    cursor.execute('''
        SELECT project_id, artist_name, song_title, package, status, created_at
        FROM projects
        ORDER BY created_at DESC
        LIMIT 10
    ''')
    columns = [desc[0] for desc in cursor.description]
    recent_projects = [dict(zip(columns, row)) for row in cursor.fetchall()]

    conn.close()

    return jsonify({
        'success': True,
        'analytics': {
            'total_projects': total_projects,
            'status_breakdown': status_breakdown,
            'total_revenue': total_revenue,
            'pending_revenue': pending_revenue,
            'package_stats': package_stats,
            'recent_projects': recent_projects
        }
    })

@app.route('/api/payment/stripe-webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe payment webhooks"""
    # This would integrate with Stripe for payment processing
    data = request.json

    # Simulate payment processing
    project_id = data.get('metadata', {}).get('project_id')
    if project_id:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE projects
            SET payment_status = 'completed'
            WHERE project_id = ?
        ''', (project_id,))

        conn.commit()
        conn.close()

        # Trigger production after payment
        trigger_craft_production({'project_id': project_id})

    return jsonify({'received': True})

def send_confirmation_email(email, project_id):
    """Send confirmation email to client"""
    # In production, integrate with SendGrid or similar
    print(f"Sending confirmation email to {email} for project {project_id}")

    # Send via NTFY as backup
    requests.post(
        'https://ntfy.sh/unc-ai-family-love',
        data=f"Order confirmation sent to {email}\nProject ID: {project_id}",
        headers={'Title': '📧 Email Sent'}
    )

@app.route('/')
def home():
    """API documentation"""
    return '''
    <h1>Video Platform API</h1>
    <h2>Endpoints:</h2>
    <ul>
        <li>POST /api/video-order - Create new order</li>
        <li>GET /api/projects - Get all projects</li>
        <li>GET /api/project/:id - Get specific project</li>
        <li>PUT /api/project/:id/status - Update status</li>
        <li>POST /api/project/:id/revision - Request revision</li>
        <li>GET /api/analytics/dashboard - Analytics dashboard</li>
    </ul>
    '''

if __name__ == '__main__':
    init_database()
    print("""
    ====================================
        VIDEO PLATFORM API RUNNING
    ====================================

    API Server: http://localhost:5001
    Client Portal: Open client_portal.html
    Admin Dashboard: Open admin_dashboard.html

    Ready for video orders!
    """)

    app.run(host='0.0.0.0', port=5001, debug=True)