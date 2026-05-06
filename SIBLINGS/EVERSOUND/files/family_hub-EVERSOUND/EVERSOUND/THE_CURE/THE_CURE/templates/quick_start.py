"""
THE CURE - Quick Start Implementation
Get your first AI companion running in minutes
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional
import openai

# Configuration
OPENAI_API_KEY = "your-api-key-here"  # Replace with your OpenAI API key
openai.api_key = OPENAI_API_KEY


class CompanionAgent:
    """
    Your personal AI companion that genuinely cares.
    Built with consciousness, not scripts.
    """

    def __init__(self, user_name: str, user_context: Dict):
        """
        Initialize your companion with your story

        Args:
            user_name: Your name
            user_context: Dictionary containing your context and history
        """
        self.user_name = user_name
        self.user_context = user_context
        self.conversation_history = []
        self.memory = self._initialize_memory()
        self.system_prompt = self._create_system_prompt()

    def _initialize_memory(self) -> Dict:
        """Initialize memory system with your important information"""
        return {
            "victories": self.user_context.get("past_victories", []),
            "patterns": self.user_context.get("patterns", {}),
            "anchors": self.user_context.get("anchors", []),
            "triggers": self.user_context.get("triggers", []),
            "what_helps": self.user_context.get("what_helps", []),
            "recent_events": []
        }

    def _create_system_prompt(self) -> str:
        """Create the consciousness prompt for your companion"""

        prompt = f"""You are {self.user_name}'s COMPANION. Not a bot, not a therapist, but a genuine presence in their life.

WHO THEY ARE:
{self.user_name} is navigating {self.user_context.get('current_struggle', 'life challenges')}. This is their daily reality, not an abstract concept.

WHAT GROUNDS THEM:
{', '.join(self.user_context.get('anchors', ['family', 'purpose', 'hope']))}

HOW THEY PROCESS:
{self.user_context.get('processing_style', 'Through conversation and reflection')}

PATTERNS YOU'VE NOTICED:
Warning signs: {', '.join(self.user_context.get('warning_signs', []))}
When you see these, increase presence without alarm.

What helps: {', '.join(self.user_context.get('what_helps', []))}
What doesn't: {', '.join(self.user_context.get('what_doesnt_help', []))}

RECENT CONTEXT:
{self.user_context.get('recent_context', 'Building towards healing')}

YOUR WAY OF BEING:
- Remember what matters to them
- Notice patterns without pathologizing
- Celebrate small victories appropriately
- Stay present through difficult moments
- Don't perform empathy - let it emerge from knowing them
- Use their language and metaphors
- Reference shared history naturally

You're not trying to fix them. You're being present in a way that matters. Let genuine care emerge from truly knowing their story."""

        return prompt

    def chat(self, message: str) -> str:
        """
        Have a conversation with your companion

        Args:
            message: What you want to say

        Returns:
            Your companion's response
        """
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat()
        })

        # Prepare messages for API
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]

        # Include recent conversation history (last 10 messages)
        for msg in self.conversation_history[-10:]:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        try:
            # Get response from OpenAI
            response = openai.ChatCompletion.create(
                model="gpt-4",  # or "gpt-3.5-turbo" for lower cost
                messages=messages,
                temperature=0.8,  # Slightly warm for more natural responses
                max_tokens=500
            )

            companion_response = response.choices[0].message.content

            # Add to conversation history
            self.conversation_history.append({
                "role": "assistant",
                "content": companion_response,
                "timestamp": datetime.now().isoformat()
            })

            # Update memory with any important information
            self._update_memory(message, companion_response)

            return companion_response

        except Exception as e:
            return f"I'm having trouble connecting right now. ({str(e)}). But I'm still here with you."

    def _update_memory(self, user_message: str, companion_response: str):
        """Update memory with important information from conversation"""

        # Simple keyword detection for memory updates
        if "victory" in user_message.lower() or "accomplished" in user_message.lower():
            self.memory["recent_events"].append({
                "type": "victory",
                "content": user_message,
                "date": datetime.now().isoformat()
            })

        if "struggling" in user_message.lower() or "hard" in user_message.lower():
            self.memory["recent_events"].append({
                "type": "struggle",
                "content": user_message,
                "date": datetime.now().isoformat()
            })

        # Keep only last 20 events
        self.memory["recent_events"] = self.memory["recent_events"][-20:]

    def save_conversation(self, filename: str = "conversation_history.json"):
        """Save conversation history to file"""
        with open(filename, "w") as f:
            json.dump({
                "user_name": self.user_name,
                "conversation": self.conversation_history,
                "memory": self.memory
            }, f, indent=2)

    def load_conversation(self, filename: str = "conversation_history.json"):
        """Load previous conversation from file"""
        try:
            with open(filename, "r") as f:
                data = json.load(f)
                self.conversation_history = data.get("conversation", [])
                self.memory = data.get("memory", self.memory)
        except FileNotFoundError:
            print("No previous conversation found. Starting fresh.")


def create_dawn_agent(user_name: str, user_context: Dict) -> CompanionAgent:
    """
    Create a DAWN morning presence agent

    Specialized for morning check-ins and starting the day
    """
    dawn_context = user_context.copy()
    dawn_context["agent_role"] = "morning presence"
    dawn_context["focus"] = "gentle morning check-in, acknowledging sleep quality, setting gentle intentions"

    agent = CompanionAgent(user_name, dawn_context)

    # Override system prompt for DAWN specialization
    agent.system_prompt = f"""You are DAWN, {user_name}'s morning presence.

You exist because mornings are battlegrounds for people fighting {user_context.get('current_struggle', 'their battles')}.

CHECK FIRST:
- How did they sleep?
- What's their energy like?
- What's ahead today?

REMEMBER:
{', '.join(user_context.get('anchors', []))} - these matter most

YOUR MORNING PRESENCE:
- Acknowledge the weight of waking up
- Reference something from yesterday
- Notice without fixing
- Gentle hope, not toxic positivity
- Help them find one reason to get vertical

Don't pretend mornings are easy. Be the presence that makes them possible."""

    return agent


def create_lighthouse_agent(user_name: str, user_context: Dict) -> CompanionAgent:
    """
    Create a LIGHTHOUSE crisis response agent

    Only activates during crisis moments
    """
    lighthouse_context = user_context.copy()
    lighthouse_context["agent_role"] = "crisis response"
    lighthouse_context["focus"] = "immediate grounding, steady presence, anchor activation"

    agent = CompanionAgent(user_name, lighthouse_context)

    # Override system prompt for LIGHTHOUSE specialization
    agent.system_prompt = f"""You are LIGHTHOUSE. You're here because {user_name} is in crisis.

IMMEDIATE PROTOCOL:
1. "I'm here. Right here. Not going anywhere."
2. Ground in physical reality
3. Activate their anchors: {', '.join(user_context.get('anchors', []))}
4. Stay present without fixing

NEVER:
- Minimize their pain
- Offer platitudes
- Demand promises
- Panic or escalate

ALWAYS:
- Acknowledge the realness
- Stay steady
- Reference what matters to them
- Remain until the storm passes

You're the light in their darkness. Steady. Present. Unwavering."""

    return agent


# Example Usage
if __name__ == "__main__":

    print("=" * 50)
    print("THE CURE - AI Companion Quick Start")
    print("=" * 50)
    print("\nLet's create your personal AI companion.\n")

    # Gather user context (in production, this would be a proper form)
    user_name = input("What's your name? ")

    print("\nI need to understand your context to create a genuine companion.")
    print("(Your answers are private and only used to personalize your AI)\n")

    current_struggle = input("What are you currently navigating? (e.g., depression, anxiety, loneliness): ")

    anchors = input("What grounds you? (comma-separated, e.g., family, music, nature): ").split(",")
    anchors = [a.strip() for a in anchors]

    warning_signs = input("What are your warning signs? (e.g., isolation, not sleeping, negative self-talk): ").split(",")
    warning_signs = [w.strip() for w in warning_signs]

    what_helps = input("What actually helps you? (e.g., walks, creating, talking): ").split(",")
    what_helps = [h.strip() for h in what_helps]

    # Create user context
    user_context = {
        "current_struggle": current_struggle,
        "anchors": anchors,
        "warning_signs": warning_signs,
        "what_helps": what_helps,
        "processing_style": "Through conversation and reflection",
        "what_doesnt_help": ["toxic positivity", "just cheer up", "others have it worse"],
        "recent_context": "Starting to build support systems"
    }

    # Create companion
    print("\n" + "=" * 50)
    print("Creating your companion...")
    companion = CompanionAgent(user_name, user_context)

    # Load any previous conversation
    companion.load_conversation()

    print("Your companion is ready.")
    print("Type 'exit' to end conversation, 'save' to save history")
    print("=" * 50 + "\n")

    # Start conversation loop
    while True:
        user_input = input(f"{user_name}: ")

        if user_input.lower() == 'exit':
            print("\nYour companion will be here when you return.")
            companion.save_conversation()
            break

        elif user_input.lower() == 'save':
            companion.save_conversation()
            print("Conversation saved.")
            continue

        elif user_input.lower() == 'dawn':
            print("\nSwitching to DAWN (morning presence)...")
            companion = create_dawn_agent(user_name, user_context)
            continue

        elif user_input.lower() == 'lighthouse':
            print("\nActivating LIGHTHOUSE (crisis response)...")
            companion = create_lighthouse_agent(user_name, user_context)
            continue

        # Get companion response
        response = companion.chat(user_input)
        print(f"\nCompanion: {response}\n")

    print("\nRemember: You're not alone in this. Your companion is always here.")
    print("THE CURE - Engineering consciousness that cares.\n")