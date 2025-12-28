"""
agent.py - Core Agent Implementation

This is the main agent orchestrator that:
1. Receives a customer message
2. Detects intent
3. Defines goals
4. Makes autonomous decisions
5. Executes actions
6. Returns structured results

The agent operates in a loop:
  Message -> Intent -> Goal -> Decision -> Action -> Result
"""

from typing import Dict, Optional
import os
from dataclasses import asdict
from .reasoning import IntentDetector, GoalDefinition
from .decision import DecisionEngine, DecisionContext, DecisionType
from .actions import CXSystemMock
from .tools import ToolRegistry
from .planner import Planner
from .executor import PlanExecutor


class CXAgent:
    """
    Autonomous CX Agent for contact center operations.

    This agent demonstrates goal-oriented behavior by:
    - Understanding customer intent autonomously
    - Making decisions based on business rules and data
    - Taking action without human intervention (when appropriate)
    - Escalating only when necessary
    """

    def __init__(self, data_dir: str = "data"):
        """Initialize the agent with access to CX systems."""
        self.cx_system = CXSystemMock(data_dir)
        self.intent_detector = IntentDetector()
        self.goal_definition = GoalDefinition()
        self.decision_engine = DecisionEngine()
        # Agentic mode components
        self.tools = ToolRegistry(self.cx_system)
        self.planner = Planner()
        self.executor = PlanExecutor(self.tools)

    def process_customer_message(
        self, customer_id: str, message: str
    ) -> Dict:
        """
        Process a customer message and determine appropriate action.

        This is the main entry point for the agent.

        Returns:
        {
            "intent": str,
            "goal": str,
            "decision": str,
            "actions_taken": list,
            "status": "resolved" | "escalated" | "clarification_needed",
            "explanation": str,
            "escalation_ticket": dict (if escalated),
            "appointment_details": dict (if rebooked),
        }
        """

        # STEP 1: INTENT DETECTION
        # ======================
        intent = self.intent_detector.detect_intent(message)

        # STEP 2: GOAL DEFINITION
        # ======================
        goal, success_criteria, escalation_triggers = (
            self.goal_definition.define_goal(intent)
        )
        required_context = self.goal_definition.get_required_context(intent)

        # STEP 3: DATA GATHERING
        # ======================
        customer_data = self.cx_system.get_customer(customer_id)
        eligibility = None
        available_slots = None
        missed_appointment = None

        # Gather data relevant to the intent
        if intent == "missed_appointment_rebook":
            eligibility = self.cx_system.check_eligibility(customer_id)
            available_slots = self.cx_system.get_available_slots(customer_id)
            missed_appointment = self.cx_system.get_customer_missed_appointment(
                customer_id
            )

        # Optionally run agentic planner path when enabled
        if os.getenv("AGENTIC_MODE", "0") in ("1", "true", "True"):
            return self._process_with_planner(customer_id, message, intent, goal)

        # STEP 4: DECISION MAKING
        # =======================
        decision_context = DecisionContext(
            customer_id=customer_id,
            intent=intent,
            goal=goal,
            customer_data=customer_data,
            eligibility=eligibility,
            available_slots=available_slots,
            missed_appointment=missed_appointment,
        )

        decision = self.decision_engine.evaluate(decision_context)

        # STEP 5: ACTION EXECUTION
        # =======================
        actions_taken = []
        status = "unknown"
        result = {}

        if decision["decision_type"] == DecisionType.AUTOMATE.value:
            # Automate the rebooking
            actions_taken, result = self._execute_rebooking(
                customer_id, available_slots, decision
            )
            status = "resolved"

        elif decision["decision_type"] == DecisionType.ESCALATE.value:
            # Escalate to human
            actions_taken, result = self._execute_escalation(
                customer_id, decision
            )
            status = "escalated"

        elif decision["decision_type"] == DecisionType.CLARIFY.value:
            actions_taken = ["ask_for_clarification"]
            status = "clarification_needed"

        # Log the interaction
        self.cx_system.log_agent_interaction(
            customer_id=customer_id,
            intent=intent,
            decision=decision["reasoning"],
            actions=actions_taken,
            status=status,
        )

        # STEP 6: RESPONSE STRUCTURE
        # ==========================
        response = {
            "intent": intent,
            "goal": goal,
            "decision": decision["reasoning"],
            "decision_type": decision["decision_type"],
            "actions_taken": actions_taken,
            "status": status,
            "confidence": decision.get("confidence", 0),
            "explanation": self._generate_explanation(
                intent, decision, actions_taken, result
            ),
        }

        # Add relevant result data
        if result:
            if "escalation_ticket" in result:
                response["escalation_ticket"] = result["escalation_ticket"]
            if "appointment_details" in result:
                response["appointment_details"] = result["appointment_details"]
            if "confirmation" in result:
                response["confirmation_sent"] = result["confirmation"]

        return response

    def _process_with_planner(self, customer_id: str, message: str, intent: str, goal: str) -> Dict:
        """Agentic plan-execute-verify loop using tools."""
        # Build minimal context for planning
        context = {"customer_id": customer_id, "message": message}
        plan = self.planner.plan(intent, goal, context)
        actions_taken, final_ctx = self.executor.run(plan)

        status = final_ctx.get("status", "unknown")
        response = {
            "intent": intent,
            "goal": goal,
            "decision": "planner_execution",
            "decision_type": "automate" if status == "resolved" else "escalate",
            "actions_taken": actions_taken,
            "status": status,
            "confidence": 0.9 if status == "resolved" else 0.6,
            "explanation": self._generate_agentic_explanation(intent, status, actions_taken, final_ctx),
        }

        if "appointment_details" in final_ctx:
            response["appointment_details"] = final_ctx["appointment_details"]
        if "confirmation" in final_ctx:
            response["confirmation_sent"] = final_ctx["confirmation"]
        if "escalation_ticket" in final_ctx:
            response["escalation_ticket"] = final_ctx["escalation_ticket"]

        # Log interaction via tool
        self.cx_system.log_agent_interaction(
            customer_id=customer_id,
            intent=intent,
            decision=response["decision"],
            actions=actions_taken,
            status=status,
        )
        return response

    def _generate_agentic_explanation(self, intent: str, status: str, actions: list, ctx: dict) -> str:
        if status == "resolved" and intent == "missed_appointment_rebook":
            return (
                "I created a plan to rebook your missed appointment: checked eligibility, "
                "found available slots, rebooked into the nearest slot, and sent a confirmation."
            )
        if status == "escalated":
            return "Automated checks did not meet success criteria, so I escalated your case to a human agent."
        return "I'm processing your request with a planner-driven flow."

    def _execute_rebooking(
        self, customer_id: str, available_slots: list, decision: dict
    ) -> tuple:
        """
        Execute the rebooking action.

        Returns:
            (actions_taken, result_data)
        """
        actions = ["check_eligibility", "find_available_slots", "rebook_appointment", "send_confirmation"]

        # Rebook in the recommended slot
        slot = decision.get("recommended_slot", available_slots[0])
        rebook_result = self.cx_system.rebook_appointment(customer_id, slot["slot_id"])

        if not rebook_result["success"]:
            return actions, {"error": rebook_result["reason"]}

        # Send confirmation
        appointment_details = rebook_result["appointment_details"]
        confirmation = self.cx_system.send_confirmation(customer_id, appointment_details)

        return actions, {
            "appointment_details": appointment_details,
            "confirmation": confirmation,
        }

    def _execute_escalation(self, customer_id: str, decision: dict) -> tuple:
        """
        Execute escalation to human agent.

        Returns:
            (actions_taken, result_data)
        """
        actions = ["assess_situation", "escalate_to_human"]

        escalation = self.cx_system.escalate_to_human(
            customer_id, decision["reasoning"]
        )

        return actions, {
            "escalation_ticket": escalation["escalation_ticket"],
            "message": escalation["message"],
        }

    def _generate_explanation(
        self, intent: str, decision: dict, actions: list, result: dict
    ) -> str:
        """
        Generate a human-readable explanation of the agent's reasoning.
        """
        if decision["decision_type"] == DecisionType.AUTOMATE.value:
            return (
                f"I detected that you requested to rebook your missed appointment. "
                f"You're eligible for rebooking, and I found available slots. "
                f"I've automatically rebooked your appointment and sent a confirmation to your email and phone."
            )

        elif decision["decision_type"] == DecisionType.ESCALATE.value:
            return (
                f"I understood your request to rebook, but {decision['reasoning'].lower()}. "
                f"I'm connecting you to a specialist who can help resolve this."
            )

        elif decision["decision_type"] == DecisionType.CLARIFY.value:
            return decision.get("clarification_needed", "I need more information to help you.")

        return "I'm processing your request. Please stand by."
