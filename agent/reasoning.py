"""
reasoning.py - Intent Detection and Goal Definition

This module is responsible for:
1. Extracting customer intent from natural language
2. Defining the agent's goal based on intent
3. Identifying required context and data
"""

from typing import Optional, Tuple


class IntentDetector:
    """Detects customer intent from messages using pattern matching and heuristics."""

    # Intent keywords mapped to intent types
    INTENT_KEYWORDS = {
        "missed": ["missed", "missed my", "didn't make", "couldn't make", "no-show"],
        "rebook": ["rebook", "reschedule", "new appointment", "different time"],
        "cancel": ["cancel", "cancel appointment", "don't want"],
        "reschedule": ["reschedule", "move", "change time"],
        "unavailable": ["unavailable", "can't attend", "not available"],
    }

    @staticmethod
    def detect_intent(message: str) -> Optional[str]:
        """
        Detect the primary intent from a customer message.

        Returns:
            intent_type: 'missed_appointment_rebook', 'cancel', 'reschedule', etc.
        """
        message_lower = message.lower()

        # Check for missed + rebook combined intent
        has_missed = any(kw in message_lower for kw in IntentDetector.INTENT_KEYWORDS["missed"])
        has_rebook = any(kw in message_lower for kw in IntentDetector.INTENT_KEYWORDS["rebook"])

        if has_missed and has_rebook:
            return "missed_appointment_rebook"

        if has_missed:
            return "acknowledge_missed"

        if any(
            kw in message_lower
            for kw in IntentDetector.INTENT_KEYWORDS["cancel"]
        ):
            return "cancel_appointment"

        if any(
            kw in message_lower
            for kw in IntentDetector.INTENT_KEYWORDS["reschedule"]
        ):
            return "reschedule_appointment"

        return "unknown"

    @staticmethod
    def is_rebooking_request(message: str) -> bool:
        """Check if the message contains a rebooking request."""
        message_lower = message.lower()
        return any(
            missed in message_lower
            for missed in IntentDetector.INTENT_KEYWORDS["missed"]
        ) and any(
            rebook in message_lower
            for rebook in IntentDetector.INTENT_KEYWORDS["rebook"]
        )


class GoalDefinition:
    """Defines the agent's goal based on detected intent."""

    GOAL_MAP = {
        "missed_appointment_rebook": {
            "goal": "Rebook the missed appointment with minimal customer effort",
            "success_criteria": [
                "Customer is eligible for rebooking",
                "Available slot is found",
                "Appointment is confirmed",
                "Confirmation is sent to customer",
            ],
            "escalation_triggers": [
                "Customer not eligible",
                "No slots available",
                "Customer account suspended",
            ],
        },
        "cancel_appointment": {
            "goal": "Cancel appointment and record cancellation reason",
            "success_criteria": ["Appointment cancelled", "Reason recorded"],
            "escalation_triggers": ["Already cancelled", "Appointment in progress"],
        },
        "reschedule_appointment": {
            "goal": "Reschedule existing appointment to new time",
            "success_criteria": [
                "New slot selected",
                "Old appointment cancelled",
                "New appointment confirmed",
            ],
            "escalation_triggers": ["No slots available", "Customer preference unclear"],
        },
        "unknown": {
            "goal": "Understand customer intent and route appropriately",
            "success_criteria": ["Intent clarified"],
            "escalation_triggers": ["Intent remains unclear after clarification"],
        },
    }

    @staticmethod
    def define_goal(intent: str) -> Tuple[str, list, list]:
        """
        Define the goal and success criteria for a detected intent.

        Returns:
            Tuple of (goal_description, success_criteria, escalation_triggers)
        """
        goal_data = GoalDefinition.GOAL_MAP.get(
            intent, GoalDefinition.GOAL_MAP["unknown"]
        )
        return (
            goal_data["goal"],
            goal_data["success_criteria"],
            goal_data["escalation_triggers"],
        )

    @staticmethod
    def get_required_context(intent: str) -> list:
        """Return the list of required data/context for the given intent."""
        required_context_map = {
            "missed_appointment_rebook": [
                "customer_id",
                "customer_account_status",
                "eligibility_check",
                "available_slots",
                "missed_appointment_details",
            ],
            "cancel_appointment": [
                "customer_id",
                "appointment_id",
                "cancellation_reason",
            ],
            "reschedule_appointment": [
                "customer_id",
                "existing_appointment_id",
                "available_slots",
                "preferred_times",
            ],
            "unknown": ["customer_id", "clarification"],
        }
        return required_context_map.get(intent, [])
