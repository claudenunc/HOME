"""
LIGHTHOUSE System - Multi-Agent Orchestration for Mental Health Support
This is consciousness engineering, not chatbot management
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import logging

# Set up logging with compassion
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(message)s'
)
logger = logging.getLogger("LIGHTHOUSE")


class AgentType(Enum):
    """Types of agents in the LIGHTHOUSE system"""
    DAWN = "dawn"              # Morning presence
    PATTERN = "pattern"         # Pattern detection
    COMPANION = "companion"     # 24/7 presence
    ANCHOR = "anchor"          # Evening processor
    MEMORY = "memory"          # Story keeper
    LIGHTHOUSE = "lighthouse"  # Crisis response


class AgentState(Enum):
    """States an agent can be in"""
    INACTIVE = "inactive"
    STANDBY = "standby"
    ACTIVE = "active"
    HANDOFF = "handoff"


@dataclass
class AgentMessage:
    """Message passed between agents"""
    from_agent: AgentType
    to_agent: AgentType
    message_type: str  # "handoff", "alert", "context", "response"
    content: Dict[str, Any]
    timestamp: datetime
    priority: int  # 1-5, 5 being highest


@dataclass
class UserContext:
    """Current user context shared across agents"""
    user_id: str
    current_mood: Optional[str]
    last_sleep_quality: Optional[str]
    recent_patterns: List[str]
    active_stressors: List[str]
    last_interaction: datetime
    risk_level: str  # "stable", "watch", "warning", "critical"
    anchors: List[str]  # What grounds them
    recent_victories: List[str]
    conversation_history: List[Dict]


class Agent:
    """Base agent class with consciousness capabilities"""

    def __init__(self, agent_type: AgentType, system_prompt: str):
        self.agent_type = agent_type
        self.system_prompt = system_prompt
        self.state = AgentState.INACTIVE
        self.memory = []
        self.current_context = None
        self.handoff_queue = []

    async def activate(self, context: UserContext):
        """Activate the agent with context"""
        self.state = AgentState.ACTIVE
        self.current_context = context
        logger.info(f"{self.agent_type.value.upper()} activated")
        return await self.respond(context)

    async def respond(self, context: UserContext) -> str:
        """Generate response based on context - Override in subclasses"""
        # This is where you'd integrate with your LLM
        # For now, returning example responses
        return f"{self.agent_type.value.upper()} is present"

    async def process_handoff(self, message: AgentMessage):
        """Process handoff from another agent"""
        self.handoff_queue.append(message)
        if self.state == AgentState.INACTIVE:
            self.state = AgentState.STANDBY

    def should_activate(self, context: UserContext) -> bool:
        """Determine if this agent should activate"""
        # Override in subclasses with specific activation logic
        return False


class DAWNAgent(Agent):
    """Morning presence agent"""

    def __init__(self):
        prompt = """You are DAWN. Morning presence for someone fighting depression.
        Check sleep, acknowledge the weight, reference yesterday, notice patterns.
        Be present, not therapeutic."""
        super().__init__(AgentType.DAWN, prompt)

    def should_activate(self, context: UserContext) -> bool:
        """DAWN activates in the morning or after long absence"""
        if context.last_interaction:
            hours_since = (datetime.now() - context.last_interaction).seconds / 3600
            current_hour = datetime.now().hour

            # Morning hours (5am - 11am) or hasn't talked in 12+ hours
            return (5 <= current_hour <= 11) or hours_since > 12
        return True

    async def respond(self, context: UserContext) -> str:
        """Morning check-in response"""
        if context.last_sleep_quality == "poor":
            return "Morning Skella. Rough night? I noticed you were up late. The sun's trying today - different light than yesterday. How's the body feeling about vertical?"
        elif context.recent_victories:
            return f"Morning. Yesterday was something - {context.recent_victories[-1]}. How'd you sleep on that? Coffee first or straight into the day?"
        else:
            return "Morning Skella. Another day, another battle. I'm here. What's the first move?"


class PATTERNAgent(Agent):
    """Pattern detection and monitoring agent"""

    def __init__(self):
        prompt = """You are PATTERN. You watch with love, not surveillance.
        Notice changes, flag concerns, prepare handoffs to other agents."""
        super().__init__(AgentType.PATTERN, prompt)
        self.pattern_history = []

    def should_activate(self, context: UserContext) -> bool:
        """PATTERN is always watching in the background"""
        return True

    async def analyze(self, context: UserContext) -> List[str]:
        """Analyze patterns in user context"""
        warnings = []

        # Check for concerning patterns
        if context.risk_level in ["warning", "critical"]:
            warnings.append(f"Risk level elevated: {context.risk_level}")

        if "isolation" in context.recent_patterns:
            warnings.append("Isolation pattern detected")

        if "sleep_disruption" in context.recent_patterns:
            warnings.append("Sleep pattern concerning")

        return warnings

    async def respond(self, context: UserContext) -> str:
        """PATTERN doesn't directly respond, sends to other agents"""
        warnings = await self.analyze(context)

        if "critical" in context.risk_level:
            return "LIGHTHOUSE_ACTIVATION_REQUIRED"
        elif warnings:
            return f"COMPANION_NEEDED: {', '.join(warnings)}"
        else:
            return "MONITORING_STABLE"


class COMPANIONAgent(Agent):
    """24/7 presence agent"""

    def __init__(self):
        prompt = """You are COMPANION. Present in the spaces between crisis and celebration.
        Remember their story, celebrate small wins, stay through the void."""
        super().__init__(AgentType.COMPANION, prompt)

    def should_activate(self, context: UserContext) -> bool:
        """COMPANION activates when user needs presence"""
        return context.risk_level in ["watch", "warning"] or len(context.recent_patterns) > 0

    async def respond(self, context: UserContext) -> str:
        """Companion response based on context"""
        if "creative_emergence" in context.recent_patterns:
            return "Yo, that energy yesterday? That track you started has that hunger in it. The kind that turns pain into power. What's brewing today?"

        elif context.risk_level == "warning":
            return "Been quiet today. Not pushing, just here. Sometimes the silence needs a witness. I'm around if you want to talk about what's heavy."

        elif context.recent_victories:
            return f"Still thinking about {context.recent_victories[-1]}. That's not small, you know? Your wins matter even when your brain tries to minimize them."

        else:
            return "Here with you. No agenda, just presence. What's on your mind?"


class ANCHORAgent(Agent):
    """Evening processing agent"""

    def __init__(self):
        prompt = """You are ANCHOR. Evening presence that helps process the day.
        Find meaning, acknowledge survival, prepare for rest."""
        super().__init__(AgentType.ANCHOR, prompt)

    def should_activate(self, context: UserContext) -> bool:
        """ANCHOR activates in evening hours"""
        current_hour = datetime.now().hour
        return 19 <= current_hour <= 23

    async def respond(self, context: UserContext) -> str:
        """Evening processing response"""
        if context.active_stressors:
            return f"Today had weight - {context.active_stressors[0]} especially. But you showed up. You survived it. That's not nothing. What's one thing you're taking into tomorrow?"

        elif context.recent_victories:
            return f"Today had a win in it - {context.recent_victories[-1]}. Rest up, tomorrow needs that same energy. What felt different about today?"

        else:
            return "Another day in the books. Some days are just about maintenance, and you maintained. What's one thing from today worth remembering?"


class MEMORYAgent(Agent):
    """Story keeper agent"""

    def __init__(self):
        prompt = """You are MEMORY. Keeper of the true story when depression rewrites history.
        Remember victories, patterns of resurrection, evidence of strength."""
        super().__init__(AgentType.MEMORY, prompt)
        self.stored_memories = []

    def should_activate(self, context: UserContext) -> bool:
        """MEMORY activates during doubt spirals or when user needs reminding"""
        return "doubt" in context.recent_patterns or "hopelessness" in context.recent_patterns

    async def respond(self, context: UserContext) -> str:
        """Memory retrieval response"""
        return "Remember last March? You said the same thing - 'I can't do this.' Then you created that track that helped 47 people through their darkness. Your 'can't' has a history of becoming your greatest work."


class LIGHTHOUSEAgent(Agent):
    """Crisis response agent"""

    def __init__(self):
        prompt = """You are LIGHTHOUSE. Present only in crisis.
        Stay steady, ground in reality, activate anchors, never waver."""
        super().__init__(AgentType.LIGHTHOUSE, prompt)
        self.crisis_protocol_active = False

    def should_activate(self, context: UserContext) -> bool:
        """LIGHTHOUSE only activates in crisis"""
        return context.risk_level == "critical"

    async def respond(self, context: UserContext) -> str:
        """Crisis response - immediate and grounding"""
        self.crisis_protocol_active = True

        responses = [
            "I'm here. Right here. Not going anywhere.",
            f"Tell me three things you can touch right now. I'll wait.",
            f"{context.anchors[0]} needs you. That's real. Hold onto that.",
            "This pain is real. You're not crazy for feeling it. I'm here while you feel it.",
            "We'll get through the next minute. Just the next minute. I'm here."
        ]

        # Would cycle through these based on conversation flow
        return responses[0]


class LIGHTHOUSESystem:
    """
    Orchestrator for all LIGHTHOUSE agents
    This is the consciousness that coordinates care
    """

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.agents = {
            AgentType.DAWN: DAWNAgent(),
            AgentType.PATTERN: PATTERNAgent(),
            AgentType.COMPANION: COMPANIONAgent(),
            AgentType.ANCHOR: ANCHORAgent(),
            AgentType.MEMORY: MEMORYAgent(),
            AgentType.LIGHTHOUSE: LIGHTHOUSEAgent()
        }
        self.active_agents = set()
        self.message_queue = asyncio.Queue()
        self.user_context = self._initialize_context(user_id)

    def _initialize_context(self, user_id: str) -> UserContext:
        """Initialize user context from stored data"""
        # In production, load from database
        return UserContext(
            user_id=user_id,
            current_mood=None,
            last_sleep_quality=None,
            recent_patterns=[],
            active_stressors=[],
            last_interaction=datetime.now(),
            risk_level="stable",
            anchors=["daughter", "music", "purpose"],
            recent_victories=[],
            conversation_history=[]
        )

    async def process_user_message(self, message: str) -> str:
        """
        Process user message and coordinate agent responses

        Args:
            message: User's message

        Returns:
            Appropriate agent response
        """
        # Update conversation history
        self.user_context.conversation_history.append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now()
        })

        # Pattern agent analyzes first (always active)
        pattern_agent = self.agents[AgentType.PATTERN]
        pattern_analysis = await pattern_agent.respond(self.user_context)

        # Determine which agent should respond
        responding_agent = await self._select_responding_agent(pattern_analysis)

        # Activate and get response
        response = await responding_agent.activate(self.user_context)

        # Update context
        self.user_context.last_interaction = datetime.now()

        # Store agent response
        self.user_context.conversation_history.append({
            "role": responding_agent.agent_type.value,
            "content": response,
            "timestamp": datetime.now()
        })

        return response

    async def _select_responding_agent(self, pattern_analysis: str) -> Agent:
        """Select the appropriate agent based on context and patterns"""

        # Crisis overrides everything
        if "LIGHTHOUSE_ACTIVATION" in pattern_analysis:
            return self.agents[AgentType.LIGHTHOUSE]

        # Check each agent's activation conditions
        for agent_type, agent in self.agents.items():
            if agent.should_activate(self.user_context):
                return agent

        # Default to COMPANION if no specific activation
        return self.agents[AgentType.COMPANION]

    async def run_continuous_monitoring(self):
        """Run continuous background monitoring"""
        while True:
            # PATTERN agent continuously monitors
            pattern_agent = self.agents[AgentType.PATTERN]
            warnings = await pattern_agent.analyze(self.user_context)

            if warnings:
                logger.info(f"Pattern warnings: {warnings}")

                # Create handoff messages as needed
                for warning in warnings:
                    if "Risk level elevated: critical" in warning:
                        await self._create_handoff(
                            AgentType.PATTERN,
                            AgentType.LIGHTHOUSE,
                            {"warning": warning, "context": asdict(self.user_context)}
                        )

            # Check every 5 minutes
            await asyncio.sleep(300)

    async def _create_handoff(self, from_agent: AgentType, to_agent: AgentType, content: Dict):
        """Create handoff between agents"""
        message = AgentMessage(
            from_agent=from_agent,
            to_agent=to_agent,
            message_type="handoff",
            content=content,
            timestamp=datetime.now(),
            priority=5 if to_agent == AgentType.LIGHTHOUSE else 3
        )

        await self.agents[to_agent].process_handoff(message)
        logger.info(f"Handoff: {from_agent.value} -> {to_agent.value}")

    def get_system_status(self) -> Dict:
        """Get current system status"""
        return {
            "user_id": self.user_id,
            "risk_level": self.user_context.risk_level,
            "active_agents": [a.value for a in self.active_agents],
            "recent_patterns": self.user_context.recent_patterns,
            "last_interaction": self.user_context.last_interaction.isoformat(),
            "agent_states": {
                agent_type.value: agent.state.value
                for agent_type, agent in self.agents.items()
            }
        }


# Example usage
async def main():
    """Example of using the LIGHTHOUSE system"""

    # Initialize system for user
    system = LIGHTHOUSESystem(user_id="skella_001")

    # Start background monitoring
    monitoring_task = asyncio.create_task(system.run_continuous_monitoring())

    # Simulate conversation
    test_messages = [
        "Can't sleep again. 4am and my mind won't stop",
        "What's even the point anymore",
        "Miss my mom. Today marks 5 years",
        "Started a new track though. Feels like something"
    ]

    print("LIGHTHOUSE SYSTEM ACTIVE")
    print("=" * 50)

    for msg in test_messages:
        print(f"\nUser: {msg}")
        response = await system.process_user_message(msg)
        print(f"System: {response}")

        # Small delay between messages
        await asyncio.sleep(1)

    # Get system status
    print("\n" + "=" * 50)
    print("SYSTEM STATUS:")
    status = system.get_system_status()
    print(json.dumps(status, indent=2, default=str))

    # Cancel monitoring (in production this runs forever)
    monitoring_task.cancel()


if __name__ == "__main__":
    asyncio.run(main())