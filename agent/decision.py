"""
decision.py - Decision Engine

This module implements the agent's decision logic:
1. Assess available data against goal requirements
2. Evaluate options (automate, clarify, escalate)
3. Select and execute the best action
4. Provide reasoning for the decision
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class DecisionType(Enum):
    """Possible decision outcomes for the agent."""
    AUTOMATE = "automate"
    CLARIFY = "clarify"
    ESCALATE = "escalate"
    REJECT = "reject"


@dataclass
class DecisionContext:
    """Context for making a decision."""
    customer_id: str
    intent: str
    goal: str
    customer_data: Optional[Dict] = None
    eligibility: Optional[Dict] = None
    available_slots: Optional[List[Dict]] = None
    missed_appointment: Optional[Dict] = None


class DecisionEngine:
    """
    Core decision-making logic for the CX agent.

    The engine evaluates the situation and decides whether to:
    - AUTOMATE: Take action directly
    - CLARIFY: Ask the customer for more information
    - ESCALATE: Hand off to a human agent
    - REJECT: Decline the request with explanation
    """

    @staticmethod
    def evaluate(context: DecisionContext) -> Dict:
        """
        Evaluate the situation and make a decision.

        Returns a decision with:
        - decision_type: AUTOMATE, CLARIFY, ESCALATE, REJECT
        - reasoning: Why this decision was made
        - next_action: What to do next
        - confidence: How confident the agent is (0-1)
        """

        # Decision logic for missed appointment rebooking
        if context.intent == "missed_appointment_rebook":
            return DecisionEngine._decide_rebooking(context)

        # Default to escalation for unknown intents
        return {
            "decision_type": DecisionType.ESCALATE.value,
            "reasoning": "Intent not recognized; escalating to specialist",
            "next_action": "escalate_to_human",
            "confidence": 0.3,
        }

    @staticmethod
    def _decide_rebooking(context: DecisionContext) -> Dict:
        """
        Decide whether to automatically rebook, ask clarification, or escalate.

        Logic:
        1. Is customer eligible? If no -> ESCALATE
        2. Are slots available? If no -> ESCALATE
        3. Is customer data complete? If no -> CLARIFY
        4. Otherwise -> AUTOMATE
        """

        # Check 1: Customer eligibility
        if context.eligibility is None:
            return {
                "decision_type": DecisionType.ESCALATE.value,
                "reasoning": "Unable to verify customer eligibility",
                "next_action": "escalate_to_human",
                "confidence": 0.4,
            }

        if not context.eligibility.get("eligible", False):
            return {
                "decision_type": DecisionType.ESCALATE.value,
                "reasoning": f"Customer not eligible: {context.eligibility.get('reason')}",
                "next_action": "escalate_to_human",
                "confidence": 0.9,
            }

        # Check 2: Available slots
        if context.available_slots is None or len(context.available_slots) == 0:
            return {
                "decision_type": DecisionType.ESCALATE.value,
                "reasoning": "No available appointment slots in the near future",
                "next_action": "escalate_to_human",
                "confidence": 0.85,
            }

        # Check 3: Customer data completeness
        if context.customer_data is None:
            return {
                "decision_type": DecisionType.CLARIFY.value,
                "reasoning": "Need to verify customer identity",
                "next_action": "ask_for_confirmation",
                "confidence": 0.6,
                "clarification_needed": "Can you confirm your name and account number?",
            }

        # Check 4: All conditions met - AUTOMATE
        return {
            "decision_type": DecisionType.AUTOMATE.value,
            "reasoning": "Customer is eligible, slots are available, and data is complete. Proceeding with rebooking.",
            "next_action": "rebook_appointment",
            "confidence": 0.95,
            "recommended_slot": context.available_slots[0],  # Recommend nearest slot
        }

    @staticmethod
    def should_escalate(decision: Dict) -> bool:
        """Check if the decision requires escalation."""
        return decision.get("decision_type") == DecisionType.ESCALATE.value

    @staticmethod
    def can_automate(decision: Dict) -> bool:
        """Check if the agent can proceed with automation."""
        return decision.get("decision_type") == DecisionType.AUTOMATE.value

    @staticmethod
    def needs_clarification(decision: Dict) -> bool:
        """Check if clarification is needed."""
        return decision.get("decision_type") == DecisionType.CLARIFY.value
