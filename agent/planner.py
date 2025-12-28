"""
planner.py - Simple Agentic Planner

Generates a sequence of steps (tools + params + expected outcomes) based on
intent, goal, and customer context. This enables a plan-execute-verify loop.
"""

from typing import Any, Dict, List


class Planner:
    """Produces executable plans for supported intents."""

    def plan(self, intent: str, goal: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        customer_id = context.get("customer_id")

        if intent == "missed_appointment_rebook":
            return [
                {
                    "tool": "check_eligibility",
                    "params": {"customer_id": customer_id},
                    "expect": {"eligible": True},
                    "on_fail": {
                        "tool": "escalate_to_human",
                        "params": {
                            "customer_id": customer_id,
                            "reason": "Customer not eligible for rebooking",
                        },
                    },
                },
                {
                    "tool": "get_available_slots",
                    "params": {"customer_id": customer_id, "limit": 5},
                    "expect": {"slots_non_empty": True},
                    "on_fail": {
                        "tool": "escalate_to_human",
                        "params": {
                            "customer_id": customer_id,
                            "reason": "No available slots",
                        },
                    },
                },
                {
                    "tool": "rebook_appointment",
                    "params_from_prev": {
                        "slot_id": ("get_available_slots", "slots", 0, "slot_id"),
                    },
                    "fixed_params": {"customer_id": customer_id},
                    "expect": {"success": True},
                },
                {
                    "tool": "send_confirmation",
                    "params_from_prev": {
                        "appointment_details": ("rebook_appointment", "appointment_details"),
                    },
                    "fixed_params": {"customer_id": customer_id},
                    "expect": {"success": True},
                },
            ]

        # Default plan: escalate unknown intents
        return [
            {
                "tool": "escalate_to_human",
                "params": {"customer_id": customer_id, "reason": "Intent unknown"},
                "expect": {"success": True},
            }
        ]
