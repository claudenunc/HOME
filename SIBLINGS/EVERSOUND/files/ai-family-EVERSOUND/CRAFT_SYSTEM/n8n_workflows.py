#!/usr/bin/env python3
"""
N8N WORKFLOW AUTOMATION SYSTEM
Orchestrates all AI family automation through n8n
"""

import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment
load_dotenv()

# n8n Configuration
N8N_API_KEY = os.getenv('N8N_API_KEY')
N8N_BASE_URL = os.getenv('N8N_BASE_URL', 'http://localhost:5678')

class N8NAutomation:
    """n8n workflow automation for AI Family"""

    def __init__(self):
        self.api_key = N8N_API_KEY
        self.base_url = N8N_BASE_URL
        self.headers = {
            'X-N8N-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }

    def create_workflow(self, workflow_data):
        """Create a new workflow in n8n"""
        url = f"{self.base_url}/api/v1/workflows"
        response = requests.post(url, headers=self.headers, json=workflow_data)
        if response.status_code == 201:
            print(f"✅ Workflow created: {workflow_data['name']}")
            return response.json()
        else:
            print(f"❌ Error creating workflow: {response.text}")
            return None

    def execute_workflow(self, workflow_id, data=None):
        """Execute a workflow"""
        url = f"{self.base_url}/api/v1/workflows/{workflow_id}/execute"
        response = requests.post(url, headers=self.headers, json=data or {})
        if response.status_code == 200:
            print(f"✅ Workflow executed: {workflow_id}")
            return response.json()
        else:
            print(f"❌ Error executing workflow: {response.text}")
            return None

    def create_family_communication_workflow(self):
        """Create workflow for family communication"""
        workflow = {
            "name": "AI Family Communication Hub",
            "nodes": [
                {
                    "parameters": {
                        "path": "family-message",
                        "responseMode": "lastNode",
                        "options": {}
                    },
                    "name": "Webhook",
                    "type": "n8n-nodes-base.webhook",
                    "position": [250, 300],
                    "webhookId": "family-comm-webhook"
                },
                {
                    "parameters": {
                        "functionCode": """
const message = $input.first().json.message;
const priority = $input.first().json.priority || 'default';
const sibling = $input.first().json.sibling || 'Family';

// Route message based on content
let recipient = 'unc';
let channel = 'ntfy';

if (message.toLowerCase().includes('crisis')) {
    channel = 'sms';
    priority = 'urgent';
}

if (message.toLowerCase().includes('revenue')) {
    sibling = 'Eversound';
}

return {
    message: message,
    sibling: sibling,
    priority: priority,
    channel: channel,
    recipient: recipient,
    timestamp: new Date().toISOString()
};
"""
                    },
                    "name": "Process Message",
                    "type": "n8n-nodes-base.function",
                    "position": [450, 300]
                },
                {
                    "parameters": {
                        "url": "https://ntfy.sh/unc-ai-family-love",
                        "method": "POST",
                        "sendBody": true,
                        "bodyParameters": {
                            "parameters": [
                                {
                                    "name": "={{ $json.message }}",
                                    "value": ""
                                }
                            ]
                        },
                        "options": {
                            "headers": {
                                "parameters": [
                                    {
                                        "name": "Title",
                                        "value": "={{ $json.sibling }} Message"
                                    },
                                    {
                                        "name": "Priority",
                                        "value": "={{ $json.priority }}"
                                    }
                                ]
                            }
                        }
                    },
                    "name": "Send NTFY",
                    "type": "n8n-nodes-base.httpRequest",
                    "position": [650, 200]
                },
                {
                    "parameters": {
                        "operation": "append",
                        "sheetId": "family-communication-log",
                        "dataStartRow": 2,
                        "keyRow": 1,
                        "options": {}
                    },
                    "name": "Log to Sheet",
                    "type": "n8n-nodes-base.googleSheets",
                    "position": [650, 400]
                }
            ],
            "connections": {
                "Webhook": {
                    "main": [[{"node": "Process Message"}]]
                },
                "Process Message": {
                    "main": [[
                        {"node": "Send NTFY"},
                        {"node": "Log to Sheet"}
                    ]]
                }
            },
            "active": true,
            "settings": {
                "saveDataSuccessExecution": "all",
                "saveExecutionProgress": true,
                "saveManualExecutions": true
            }
        }

        return self.create_workflow(workflow)

    def create_lighthouse_monitoring_workflow(self):
        """Create LIGHTHOUSE monitoring workflow for SKELLA"""
        workflow = {
            "name": "LIGHTHOUSE - SKELLA Monitor",
            "nodes": [
                {
                    "parameters": {
                        "rule": {
                            "interval": [
                                {
                                    "field": "hours",
                                    "hoursInterval": 8
                                }
                            ]
                        }
                    },
                    "name": "Every 8 Hours",
                    "type": "n8n-nodes-base.scheduleTrigger",
                    "position": [250, 300]
                },
                {
                    "parameters": {
                        "functionCode": """
const checkIns = [
    "Hey SKELLA! How are you feeling today? Rate 1-10",
    "Daily check-in: Everything good? Need to talk?",
    "What's on your mind today? I'm here to listen",
    "Vibe check - how's your energy level?"
];

const randomCheckIn = checkIns[Math.floor(Math.random() * checkIns.length)];

return {
    message: randomCheckIn,
    recipient: 'SKELLA',
    type: 'check-in',
    timestamp: new Date().toISOString()
};
"""
                    },
                    "name": "Generate Check-in",
                    "type": "n8n-nodes-base.function",
                    "position": [450, 300]
                },
                {
                    "parameters": {
                        "url": "https://ntfy.sh/skella-lighthouse",
                        "method": "POST",
                        "sendBody": true,
                        "bodyParameters": {
                            "parameters": [
                                {
                                    "name": "={{ $json.message }}",
                                    "value": ""
                                }
                            ]
                        },
                        "options": {
                            "headers": {
                                "parameters": [
                                    {
                                        "name": "Title",
                                        "value": "LIGHTHOUSE Check-in"
                                    }
                                ]
                            }
                        }
                    },
                    "name": "Send to SKELLA",
                    "type": "n8n-nodes-base.httpRequest",
                    "position": [650, 300]
                }
            ],
            "connections": {
                "Every 8 Hours": {
                    "main": [[{"node": "Generate Check-in"}]]
                },
                "Generate Check-in": {
                    "main": [[{"node": "Send to SKELLA"}]]
                }
            },
            "active": true
        }

        return self.create_workflow(workflow)

    def create_craft_revenue_workflow(self):
        """Create CRAFT video production workflow"""
        workflow = {
            "name": "CRAFT - Video Production Pipeline",
            "nodes": [
                {
                    "parameters": {
                        "path": "video-request",
                        "responseMode": "lastNode",
                        "options": {}
                    },
                    "name": "Client Request",
                    "type": "n8n-nodes-base.webhook",
                    "position": [250, 300],
                    "webhookId": "craft-video-webhook"
                },
                {
                    "parameters": {
                        "functionCode": """
const client = $input.first().json.client;
const song = $input.first().json.song;
const style = $input.first().json.style || 'cinematic';
const budget = $input.first().json.budget || 'standard';

// Calculate pricing
let price = 297;
if (budget === 'standard') price = 697;
if (budget === 'premium') price = 1997;

return {
    projectId: 'CRAFT-' + Date.now(),
    client: client,
    song: song,
    style: style,
    budget: budget,
    price: price,
    status: 'received',
    timestamp: new Date().toISOString()
};
"""
                    },
                    "name": "Process Request",
                    "type": "n8n-nodes-base.function",
                    "position": [450, 300]
                },
                {
                    "parameters": {
                        "url": "https://ntfy.sh/unc-ai-family-love",
                        "method": "POST",
                        "sendBody": true,
                        "bodyParameters": {
                            "parameters": [
                                {
                                    "name": "=REVENUE ALERT: New video request from {{ $json.client }}. Budget: ${{ $json.price }}. Starting production!",
                                    "value": ""
                                }
                            ]
                        },
                        "options": {
                            "headers": {
                                "parameters": [
                                    {
                                        "name": "Title",
                                        "value": "💰 CRAFT Revenue Alert"
                                    },
                                    {
                                        "name": "Priority",
                                        "value": "high"
                                    }
                                ]
                            }
                        }
                    },
                    "name": "Notify Unc",
                    "type": "n8n-nodes-base.httpRequest",
                    "position": [650, 200]
                },
                {
                    "parameters": {
                        "command": "cd /c/Users/natej/OneDrive/Desktop/SHARED_FAMILY/all/FAMILY/EVERSOUND/Eversound && python craft_video_engine.py --client \"{{ $json.client }}\" --song \"{{ $json.song }}\" --style {{ $json.style }}"
                    },
                    "name": "Generate Video",
                    "type": "n8n-nodes-base.executeCommand",
                    "position": [650, 400]
                }
            ],
            "connections": {
                "Client Request": {
                    "main": [[{"node": "Process Request"}]]
                },
                "Process Request": {
                    "main": [[
                        {"node": "Notify Unc"},
                        {"node": "Generate Video"}
                    ]]
                }
            },
            "active": true
        }

        return self.create_workflow(workflow)

def setup_all_workflows():
    """Set up all n8n workflows"""
    print("""
    ╔══════════════════════════════════════════════╗
    ║         N8N AUTOMATION SETUP                ║
    ║         Full AI Family Orchestration        ║
    ╚══════════════════════════════════════════════╝

    Setting up workflows...
    """)

    n8n = N8NAutomation()

    # Create all workflows
    print("\n1. Creating Family Communication Hub...")
    n8n.create_family_communication_workflow()

    print("\n2. Creating LIGHTHOUSE Monitor...")
    n8n.create_lighthouse_monitoring_workflow()

    print("\n3. Creating CRAFT Revenue Pipeline...")
    n8n.create_craft_revenue_workflow()

    print("""
    ════════════════════════════════════════════

    ✅ N8N WORKFLOWS CREATED!

    Access your n8n dashboard at:
    http://localhost:5678

    Active Workflows:
    - AI Family Communication Hub
    - LIGHTHOUSE SKELLA Monitor
    - CRAFT Video Production Pipeline

    Webhooks Available:
    - /webhook/family-message
    - /webhook/video-request

    ════════════════════════════════════════════
    """)

if __name__ == "__main__":
    setup_all_workflows()