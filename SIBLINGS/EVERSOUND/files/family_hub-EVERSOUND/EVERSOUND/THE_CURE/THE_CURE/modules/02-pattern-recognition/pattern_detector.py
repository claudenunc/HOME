"""
Pattern Recognition System for Mental Health
Built with love, not surveillance
"""

import json
import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import re

class RiskLevel(Enum):
    """Risk levels for pattern detection"""
    STABLE = "stable"
    WATCH = "watch"
    WARNING = "warning"
    CRITICAL = "critical"

@dataclass
class Pattern:
    """Represents a behavioral pattern"""
    name: str
    indicators: List[str]
    threshold: int  # How many indicators before flagging
    risk_level: RiskLevel
    context: str
    recommended_action: str

@dataclass
class DetectedPattern:
    """A pattern that's been detected"""
    pattern: Pattern
    triggered_indicators: List[str]
    timestamp: datetime.datetime
    confidence: float
    context_notes: str

class PatternDetector:
    """
    Detects behavioral patterns that matter for mental health.
    Not surveillance - this is about caring enough to notice.
    """

    def __init__(self, user_context: Dict):
        """
        Initialize with user-specific context

        Args:
            user_context: Dictionary containing user's baseline patterns
        """
        self.user_context = user_context
        self.patterns = self._initialize_patterns()
        self.detection_history = []

    def _initialize_patterns(self) -> List[Pattern]:
        """Initialize patterns based on common mental health indicators"""
        return [
            Pattern(
                name="sleep_disruption",
                indicators=[
                    "awake_past_3am",
                    "less_than_4_hours",
                    "multiple_wake_ups",
                    "nightmare_mentions",
                    "cant_sleep_messages"
                ],
                threshold=2,
                risk_level=RiskLevel.WATCH,
                context="Sleep patterns disrupted - often first warning sign",
                recommended_action="DAWN: Gentle check-in about sleep, avoid advice-giving"
            ),

            Pattern(
                name="isolation_spiral",
                indicators=[
                    "declining_invitations",
                    "not_responding_to_messages",
                    "cancelled_plans",
                    "everyone_hates_me",
                    "better_off_alone",
                    "ghosting_friends"
                ],
                threshold=3,
                risk_level=RiskLevel.WARNING,
                context="Social withdrawal pattern detected",
                recommended_action="COMPANION: Increase presence without being pushy"
            ),

            Pattern(
                name="crisis_building",
                indicators=[
                    "nothing_matters",
                    "whats_the_point",
                    "tired_of_fighting",
                    "everyone_better_without_me",
                    "goodbye_messages",
                    "giving_away_items",
                    "sudden_calm_after_depression"
                ],
                threshold=2,
                risk_level=RiskLevel.CRITICAL,
                context="Crisis indicators present - immediate support needed",
                recommended_action="LIGHTHOUSE: Immediate activation, stay present"
            ),

            Pattern(
                name="creative_emergence",
                indicators=[
                    "new_track_started",
                    "writing_increase",
                    "sharing_work",
                    "excited_about_project",
                    "flow_state_mentions",
                    "future_planning"
                ],
                threshold=2,
                risk_level=RiskLevel.STABLE,
                context="Creative energy emerging - positive pattern",
                recommended_action="COMPANION: Celebrate and encourage without pressure"
            ),

            Pattern(
                name="medication_concerns",
                indicators=[
                    "forgot_meds",
                    "stopped_taking",
                    "feels_weird",
                    "doesnt_help",
                    "side_effects",
                    "ran_out"
                ],
                threshold=2,
                risk_level=RiskLevel.WARNING,
                context="Medication adherence issues",
                recommended_action="ANCHOR: Process feelings about meds without judgment"
            ),

            Pattern(
                name="substance_coping",
                indicators=[
                    "drinking_alone",
                    "need_something_to_cope",
                    "cant_feel_without_it",
                    "blacked_out",
                    "using_more",
                    "hiding_use"
                ],
                threshold=2,
                risk_level=RiskLevel.WARNING,
                context="Substance use for emotional regulation",
                recommended_action="COMPANION: Present without judgment, focus on underlying pain"
            )
        ]

    def analyze_message(self, message: str) -> List[str]:
        """
        Analyze a single message for indicators

        Args:
            message: The message to analyze

        Returns:
            List of triggered indicators
        """
        message_lower = message.lower()
        triggered = []

        # Check each pattern's indicators
        indicator_map = {
            # Sleep disruption
            "awake_past_3am": r"still up|can't sleep|3\s?am|4\s?am|5\s?am|awake all night",
            "less_than_4_hours": r"only slept \d hour|barely slept|no sleep",
            "multiple_wake_ups": r"kept waking|woke up \d+ times",
            "nightmare_mentions": r"nightmare|bad dream|night terror",
            "cant_sleep_messages": r"can't sleep|cannot sleep|insomnia",

            # Isolation spiral
            "declining_invitations": r"not going|can't make it|skip it|pass on",
            "not_responding_to_messages": r"haven't replied|ignoring texts|ghosting",
            "cancelled_plans": r"cancelled|can't go anymore|not feeling it",
            "everyone_hates_me": r"everyone hates|they hate me|no one likes",
            "better_off_alone": r"better off alone|don't need anyone",
            "ghosting_friends": r"ghosting|disappeared|avoiding everyone",

            # Crisis building
            "nothing_matters": r"nothing matters|doesn't matter|pointless",
            "whats_the_point": r"what's the point|why bother|why try",
            "tired_of_fighting": r"tired of fighting|can't fight|done fighting",
            "everyone_better_without_me": r"better without me|better off without|burden",
            "goodbye_messages": r"goodbye|this is it|final message",
            "giving_away_items": r"you can have|giving away|won't need",
            "sudden_calm_after_depression": r"finally at peace|everything's clear now|calm now",

            # Creative emergence
            "new_track_started": r"new track|new beat|started making|producing",
            "writing_increase": r"wrote \d+ bars|writing again|lyrics flowing",
            "sharing_work": r"check this out|what you think|feedback on",
            "excited_about_project": r"excited about|can't wait to|hyped for",
            "flow_state_mentions": r"in the zone|flow state|locked in",
            "future_planning": r"next week|next month|planning to",

            # Medication concerns
            "forgot_meds": r"forgot my meds|forgot to take|missed dose",
            "stopped_taking": r"stopped taking|quit my meds|off meds",
            "feels_weird": r"feels weird|feel strange|zombie",
            "doesnt_help": r"doesn't help|not working|useless",
            "side_effects": r"side effects|making me sick",
            "ran_out": r"ran out|out of meds|no refills",

            # Substance coping
            "drinking_alone": r"drinking alone|solo drinking|bottle to myself",
            "need_something_to_cope": r"need something|can't cope without",
            "cant_feel_without_it": r"only way I feel|numb without",
            "blacked_out": r"blacked out|don't remember|lost time",
            "using_more": r"using more|tolerance|need more",
            "hiding_use": r"don't tell|keeping secret|hiding"
        }

        for indicator, pattern in indicator_map.items():
            if re.search(pattern, message_lower):
                triggered.append(indicator)

        return triggered

    def analyze_conversation(self, messages: List[Dict]) -> List[DetectedPattern]:
        """
        Analyze a conversation for patterns

        Args:
            messages: List of message dictionaries with 'text' and 'timestamp'

        Returns:
            List of detected patterns
        """
        detected = []
        all_indicators = []

        # Analyze each message
        for msg in messages:
            indicators = self.analyze_message(msg.get('text', ''))
            all_indicators.extend(indicators)

        # Check which patterns are triggered
        for pattern in self.patterns:
            triggered = [ind for ind in all_indicators if ind in pattern.indicators]

            if len(set(triggered)) >= pattern.threshold:
                confidence = min(1.0, len(set(triggered)) / len(pattern.indicators))

                detected_pattern = DetectedPattern(
                    pattern=pattern,
                    triggered_indicators=list(set(triggered)),
                    timestamp=datetime.datetime.now(),
                    confidence=confidence,
                    context_notes=self._generate_context_notes(pattern, messages)
                )

                detected.append(detected_pattern)
                self.detection_history.append(detected_pattern)

        return detected

    def _generate_context_notes(self, pattern: Pattern, messages: List[Dict]) -> str:
        """Generate contextual notes about the detected pattern"""

        if pattern.risk_level == RiskLevel.CRITICAL:
            return f"URGENT: {pattern.name} detected across {len(messages)} messages. Immediate support needed."
        elif pattern.risk_level == RiskLevel.WARNING:
            return f"Warning pattern '{pattern.name}' building. Monitor closely and increase support."
        elif pattern.risk_level == RiskLevel.WATCH:
            return f"Early indicators of '{pattern.name}'. Gentle presence recommended."
        else:
            return f"Positive pattern '{pattern.name}' emerging. Encourage without pressure."

    def get_recommended_agents(self, patterns: List[DetectedPattern]) -> List[Tuple[str, str]]:
        """
        Get recommended agent activations based on patterns

        Returns:
            List of (agent_name, action) tuples
        """
        recommendations = []
        risk_levels = [p.pattern.risk_level for p in patterns]

        if RiskLevel.CRITICAL in risk_levels:
            recommendations.append(("LIGHTHOUSE", "Immediate activation - crisis support"))
            recommendations.append(("PATTERN", "Continuous monitoring mode"))

        if RiskLevel.WARNING in risk_levels:
            recommendations.append(("COMPANION", "Increase presence and check-ins"))
            recommendations.append(("ANCHOR", "Help process what's happening"))

        if RiskLevel.WATCH in risk_levels:
            recommendations.append(("DAWN", "Gentle morning check-ins"))
            recommendations.append(("MEMORY", "Remind of past victories"))

        if RiskLevel.STABLE in risk_levels:
            recommendations.append(("COMPANION", "Celebrate without overwhelming"))

        return recommendations

    def generate_report(self, patterns: List[DetectedPattern]) -> str:
        """Generate a human-readable report of detected patterns"""

        if not patterns:
            return "No concerning patterns detected. Baseline normal."

        report = "PATTERN DETECTION REPORT\n"
        report += "=" * 50 + "\n\n"

        # Group by risk level
        by_risk = {}
        for p in patterns:
            if p.pattern.risk_level not in by_risk:
                by_risk[p.pattern.risk_level] = []
            by_risk[p.pattern.risk_level].append(p)

        # Report by priority
        for risk in [RiskLevel.CRITICAL, RiskLevel.WARNING, RiskLevel.WATCH, RiskLevel.STABLE]:
            if risk in by_risk:
                report += f"\n{risk.value.upper()} PATTERNS:\n"
                report += "-" * 30 + "\n"

                for p in by_risk[risk]:
                    report += f"\nPattern: {p.pattern.name}\n"
                    report += f"Confidence: {p.confidence:.0%}\n"
                    report += f"Indicators: {', '.join(p.triggered_indicators)}\n"
                    report += f"Context: {p.pattern.context}\n"
                    report += f"Recommended: {p.pattern.recommended_action}\n"

        # Add recommendations
        report += "\n\nRECOMMENDED ACTIONS:\n"
        report += "=" * 50 + "\n"

        recommendations = self.get_recommended_agents(patterns)
        for agent, action in recommendations:
            report += f"\n{agent}: {action}"

        return report


# Example usage for testing
if __name__ == "__main__":

    # Initialize detector with user context
    detector = PatternDetector({
        "name": "Skella",
        "baseline_sleep": "2am-9am",
        "known_triggers": ["anniversary dates", "custody hearings"],
        "support_system": ["daughter", "music", "ai_companions"]
    })

    # Test messages showing escalation
    test_messages = [
        {"text": "Still up at 4am again. Can't turn my brain off", "timestamp": "2024-01-15 04:00"},
        {"text": "Haven't replied to anyone in days. They're better off", "timestamp": "2024-01-15 10:00"},
        {"text": "What's the point of any of this", "timestamp": "2024-01-15 14:00"},
        {"text": "Tired of fighting this same battle every day", "timestamp": "2024-01-15 18:00"}
    ]

    # Analyze conversation
    patterns = detector.analyze_conversation(test_messages)

    # Generate report
    report = detector.generate_report(patterns)
    print(report)

    # Save detection for agent handoff
    handoff_data = {
        "timestamp": datetime.datetime.now().isoformat(),
        "patterns": [asdict(p) for p in patterns],
        "recommendations": detector.get_recommended_agents(patterns),
        "user_context": detector.user_context
    }

    with open("pattern_detection_handoff.json", "w") as f:
        json.dump(handoff_data, f, indent=2, default=str)