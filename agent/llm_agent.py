"""
llm_agent.py - LLM-powered Agent using Google Gemini

This agent uses a Large Language Model for:
- Intent detection with nuance handling
- Goal understanding with context
- Autonomous decision-making with reasoning
- Action planning and execution

The agent is truly "agentic" because it:
1. Uses AI to reason about decisions (not just rules)
2. Generates explanations for its choices
3. Can handle novel/unexpected customer requests
4. Learns from prompts (via prompt engineering)
"""

import os
import json
from typing import Dict, Optional
import google.generativeai as genai

from .actions import CXSystemMock
from .decision import DecisionType


class LLMCXAgent:
    """
    Agentic CX Agent powered by LLM (Google Gemini).

    This agent uses AI to make autonomous decisions about customer requests.
    """

    def __init__(self, data_dir: str = "data", model: str = "gemini-1.5-flash"):
        """Initialize the LLM-powered agent."""
        self.cx_system = CXSystemMock(data_dir)
        self.model = model
        
        # Configure Gemini API
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set. Get a free key at https://makersuite.google.com/app/apikey")
        
        genai.configure(api_key=api_key)

        # Support current google-generativeai (>=0.8.x)
        try:
            self.client = genai.GenerativeModel(model_name=model)
            self._use_generate_content = True
        except Exception:
            # Fallback for older packages if still present
            if hasattr(genai, "GenerativeModel"):
                self.client = genai.GenerativeModel(model)
                self._use_generate_content = False
            else:
                raise

        self.system_prompt = """You are an autonomous AI agent for a contact center.
Your role is to:
1. Understand customer intents from their messages
2. Make decisions about how to help them
3. Explain your reasoning clearly

You can:
- Rebook missed appointments (if customer is eligible)
- Escalate complex issues to humans
- Request clarification when needed

For each customer message, respond in JSON:
{
  "intent": "missed_appointment_rebook|other_request|complaint|...",
  "goal": "what you're trying to achieve",
  "decision": "automate|escalate|clarify",
  "decision_type": "AUTOMATE|ESCALATE|CLARIFY",
  "reasoning": "explain why you made this decision",
  "recommended_action": "what to do (rebook_appointment, escalate_to_human, etc.)",
  "confidence": 0.0-1.0
}

Always be helpful, professional, and prioritize customer satisfaction.
"""

    def process_customer_message(self, customer_id: str, message: str) -> Dict:
        """
        Process a customer message using LLM-based reasoning.

        Returns a structured agent response with decision, reasoning, and actions.
        """

        # STEP 1: Fetch customer context
        customer_data = self.cx_system.get_customer(customer_id)

        # STEP 2: Call LLM for intent, goal, and decision
        llm_response = self._query_llm(customer_id, message, customer_data)

        # STEP 3: Parse LLM response
        try:
            llm_decision = json.loads(llm_response)
        except json.JSONDecodeError:
            return self._error_response("Failed to parse LLM response")

        intent = llm_decision.get("intent", "unknown")
        goal = llm_decision.get("goal", "help customer")
        decision_type = llm_decision.get("decision_type", "CLARIFY").upper()
        reasoning = llm_decision.get("reasoning", "")
        recommended_action = llm_decision.get("recommended_action", "")

        # STEP 4: Execute decision
        actions_taken = []
        status = "unknown"
        result = {}

        if decision_type == "AUTOMATE":
            # Try to automate the action
            if intent == "missed_appointment_rebook" or "rebook" in recommended_action.lower():
                actions_taken, result, status = self._execute_rebooking(
                    customer_id, customer_data
                )
            else:
                actions_taken = ["process_request"]
                status = "resolved"

        elif decision_type == "ESCALATE":
            actions_taken, result, status = self._execute_escalation(
                customer_id, reasoning
            )

        elif decision_type == "CLARIFY":
            actions_taken = ["request_clarification"]
            status = "clarification_needed"

        # Log the interaction
        self.cx_system.log_agent_interaction(
            customer_id=customer_id,
            intent=intent,
            decision=reasoning,
            actions=actions_taken,
            status=status,
        )

        # STEP 5: Build response
        response = {
            "intent": intent,
            "goal": goal,
            "decision": reasoning,
            "decision_type": decision_type,
            "actions_taken": actions_taken,
            "status": status,
            "confidence": llm_decision.get("confidence", 0.5),
            "explanation": self._generate_explanation(intent, decision_type, reasoning, actions_taken),
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

    def _query_llm(self, customer_id: str, message: str, customer_data: dict) -> str:
        """Query the LLM for intent, goal, and decision."""
        user_prompt = f"""Customer ID: {customer_id}
Customer Info: {json.dumps(customer_data, indent=2)}

Customer Message: "{message}"

Analyze this customer message and decide:
1. What is their intent?
2. What is your goal?
3. Should you automate, escalate, or clarify?
4. What's your reasoning?
5. What action do you recommend?

Respond in JSON format."""

        try:
            full_prompt = f"{self.system_prompt}\n\n{user_prompt}"

            if getattr(self, "_use_generate_content", False):
                response = self.client.generate_content(
                    full_prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.7,
                        max_output_tokens=500,
                    ),
                )
                return response.text

            # Legacy fallback path
            conversation = self.client.start_chat(history=[])
            response = conversation.send_message(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=500,
                ),
            )
            return response.text

        except Exception as e:
            print(f"LLM query error: {e}")
            return json.dumps({
                "intent": "error",
                "goal": "recover from LLM failure",
                "decision": "clarify",
                "decision_type": "CLARIFY",
                "reasoning": f"I encountered an issue: {str(e)}",
                "recommended_action": "request_clarification",
                "confidence": 0.0,
            })

    def _execute_rebooking(self, customer_id: str, customer_data: dict) -> tuple:
        """Execute rebooking autonomously."""
        actions = ["check_eligibility", "find_available_slots", "rebook_appointment"]

        eligibility = self.cx_system.check_eligibility(customer_id)
        if not eligibility.get("eligible", False):
            return actions, {"error": eligibility.get("reason", "Not eligible")}, "escalated"

        available_slots = self.cx_system.get_available_slots(customer_id)
        if not available_slots:
            return actions, {"error": "No available slots"}, "escalated"

        # Rebook into the first available slot
        slot = available_slots[0]
        rebook_result = self.cx_system.rebook_appointment(customer_id, slot["slot_id"])

        if not rebook_result["success"]:
            return actions, {"error": rebook_result["reason"]}, "escalated"

        actions.append("send_confirmation")
        appointment_details = rebook_result["appointment_details"]
        confirmation = self.cx_system.send_confirmation(customer_id, appointment_details)

        return actions, {
            "appointment_details": appointment_details,
            "confirmation": confirmation,
        }, "resolved"

    def _execute_escalation(self, customer_id: str, reasoning: str) -> tuple:
        """Escalate to human agent."""
        actions = ["escalate_to_human"]

        escalation = self.cx_system.escalate_to_human(customer_id, reasoning)

        return actions, {
            "escalation_ticket": escalation["escalation_ticket"],
            "message": escalation["message"],
        }, "escalated"

    def _generate_explanation(
        self, intent: str, decision_type: str, reasoning: str, actions: list
    ) -> str:
        """Generate a human-readable explanation."""
        if decision_type == "AUTOMATE":
            return f"I've analyzed your request and taken action: {reasoning}. Status: Completed automatically."
        elif decision_type == "ESCALATE":
            return f"I've reviewed your request: {reasoning}. Escalating to a specialist for better support."
        elif decision_type == "CLARIFY":
            return f"I need to understand your request better: {reasoning}. Could you provide more details?"
        return "Processing your request..."

    def _error_response(self, error: str) -> Dict:
        """Return a structured error response."""
        return {
            "intent": "error",
            "goal": "recover",
            "decision": error,
            "decision_type": "CLARIFY",
            "actions_taken": [],
            "status": "clarification_needed",
            "confidence": 0.0,
            "explanation": f"I encountered an issue: {error}. Please try again.",
        }
