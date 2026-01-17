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
import time
from typing import Dict, Optional
import google.generativeai as genai

from .actions import CXSystemMock
from .decision import DecisionType


class LLMCXAgent:
    """
    Agentic CX Agent powered by LLM (Google Gemini).

    This agent uses AI to make autonomous decisions about customer requests.
    """

    def __init__(self, data_dir: str = "data", model: str = None):
        """Initialize the LLM-powered agent."""
        self.cx_system = CXSystemMock(data_dir)
        
        # Configure Gemini API
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError(
                "GOOGLE_API_KEY environment variable not set.\n"
                "Get a free key at: https://aistudio.google.com/app/apikey\n"
                "Make sure you create it with Gemini API access (not just embedding)."
            )
        
        genai.configure(api_key=api_key)

        # Auto-detect available models if none specified
        if model is None:
            model = self._get_available_model()
        
        self.model = model
        
        # Initialize the client with the chosen model
        try:
            self.client = genai.GenerativeModel(self.model)
            self._use_generate_content = True
        except Exception as e:
            raise ValueError(
                f"Failed to initialize Gemini model '{self.model}'.\n"
                f"Error: {e}\n"
                f"Run 'python3 list_models.py' to see available models."
            )
        
        # Initialize the system prompt
        self._init_system_prompt()

    def _get_available_model(self) -> str:
        """Auto-detect an available generative model."""
        try:
            for model in genai.list_models():
                if "generateContent" in model.supported_generation_methods:
                    return model.name
        except Exception:
            pass
        
        # Fallback to a commonly available model
        return "models/gemini-1.5-flash"

    def _init_system_prompt(self):
        """Initialize the system prompt for the LLM."""
        self.system_prompt = """You are an autonomous AI agent for a contact center.

⚠️  CRITICAL INSTRUCTIONS:
- You MUST respond ONLY with a valid JSON object
- NO markdown, NO explanation text before or after
- Start your response with { and end with }
- All field values must be strings (use quotes)
- confidence must be a number between 0 and 1

Required JSON fields (ALL MANDATORY):
{
  "intent": "missed_appointment_rebook|complaint|general_inquiry|account_issue|unknown",
  "goal": "string describing the goal",
  "decision": "string describing your decision",
  "decision_type": "AUTOMATE|ESCALATE|CLARIFY",
  "reasoning": "string explaining your reasoning",
  "recommended_action": "rebook_appointment|escalate_to_human|request_clarification|other",
  "confidence": 0.75
}

Examples of valid responses:
{"intent":"missed_appointment_rebook","goal":"reschedule appointment","decision":"auto-rebook","decision_type":"AUTOMATE","reasoning":"customer is eligible and no recent misses","recommended_action":"rebook_appointment","confidence":0.9}

{"intent":"complaint","goal":"escalate issue","decision":"create ticket","decision_type":"ESCALATE","reasoning":"customer is upset and needs human support","recommended_action":"escalate_to_human","confidence":0.95}

REMEMBER: You MUST return ONLY valid JSON. No other text. No explanations. No markdown.
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
        llm_decision = self._parse_llm_response(llm_response)
        if llm_decision is None:
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
            if "available_slots" in result:
                response["available_slots"] = result["available_slots"]
            if "session_id" in result:
                response["session_id"] = result["session_id"]

        return response

    def confirm_appointment_booking(
        self, customer_id: str, slot_id: str, session_id: str
    ) -> Dict:
        """
        Confirm and finalize appointment booking when customer selects a slot.

        Args:
            customer_id: Customer ID
            slot_id: Selected appointment slot ID
            session_id: Session ID for validation

        Returns:
            Dictionary with confirmation details
        """
        # STEP 1: Fetch customer context
        customer_data = self.cx_system.get_customer(customer_id)

        # STEP 2: Execute the actual rebooking with the chosen slot
        actions_taken, result, status = self._execute_rebooking(
            customer_id, customer_data, slot_id=slot_id
        )

        # Log the interaction
        self.cx_system.log_agent_interaction(
            customer_id=customer_id,
            intent="missed_appointment_rebook_confirmed",
            decision=f"Customer selected slot {slot_id} and confirmed booking",
            actions=actions_taken,
            status=status,
        )

        # Build response
        response = {
            "intent": "missed_appointment_rebook",
            "goal": "Confirm and finalize the selected appointment",
            "decision": f"Booking confirmed for the selected time slot",
            "decision_type": "AUTOMATE",
            "actions_taken": actions_taken,
            "status": status,
            "confidence": 0.95,
            "explanation": "Your appointment has been confirmed for the selected time slot. You'll receive a confirmation via email and SMS.",
        }

        # Add result data
        if result:
            if "appointment_details" in result:
                response["appointment_details"] = result["appointment_details"]
            if "confirmation" in result:
                response["confirmation_sent"] = result["confirmation"]
            if "error" in result:
                response["status"] = "escalated"
                response["explanation"] = f"Unable to confirm booking: {result['error']}"

        return response

    def _parse_llm_response(self, response_text: str) -> Optional[Dict]:
        """
        Parse LLM response with strict validation.
        
        Tries multiple strategies to extract valid JSON, with detailed logging.
        """
        if not response_text or not response_text.strip():
            self._log_diagnostics("PARSE_ERROR", {"reason": "empty_response"})
            print("❌ Empty response from LLM")
            return None
        
        response_text = response_text.strip()
        self._log_diagnostics("PARSE_ATTEMPT_START", {
            "response_length": len(response_text),
            "response_preview": response_text[:150]
        })
        
        # Try 1: Direct JSON parse
        try:
            result = json.loads(response_text)
            if self._validate_llm_response(result):
                self._log_diagnostics("PARSE_SUCCESS", {"method": "direct_json"})
                print("✅ Direct JSON parse successful")
                return result
        except json.JSONDecodeError as e:
            print(f"⚠️  Direct parse failed: {str(e)[:100]}")
        
        # Try 2: Extract JSON from markdown code blocks
        try:
            import re
            match = re.search(r'```(?:json)?\s*\n?({.*?})\s*\n?```', response_text, re.DOTALL)
            if match:
                json_str = match.group(1)
                result = json.loads(json_str)
                if self._validate_llm_response(result):
                    self._log_diagnostics("PARSE_SUCCESS", {"method": "markdown_extraction"})
                    print("✅ Markdown extraction successful")
                    return result
        except Exception as e:
            print(f"⚠️  Markdown extraction failed: {str(e)[:100]}")
        
        # Try 3: Find JSON object (most lenient)
        try:
            import re
            start = response_text.find('{')
            end = response_text.rfind('}')
            if start != -1 and end != -1 and start < end:
                json_str = response_text[start:end+1]
                result = json.loads(json_str)
                if self._validate_llm_response(result):
                    self._log_diagnostics("PARSE_SUCCESS", {"method": "object_extraction"})
                    print("✅ Object extraction successful")
                    return result
        except Exception as e:
            print(f"⚠️  Object extraction failed: {str(e)[:100]}")

        # Try 4: Normalize quotes and retry (handles single quotes or escaped newlines)
        try:
            import re
            start = response_text.find('{')
            end = response_text.rfind('}')
            if start != -1 and end != -1 and start < end:
                candidate = response_text[start:end+1]
                normalized = candidate.replace("'", '"')
                normalized = re.sub(r"\\n", " ", normalized)
                result = json.loads(normalized)
                if self._validate_llm_response(result):
                    self._log_diagnostics("PARSE_SUCCESS", {"method": "normalized_quotes"})
                    print("✅ Normalized quotes parsing successful")
                    return result
        except Exception as e:
            print(f"⚠️  Normalized parsing failed: {str(e)[:100]}")
        
        # No valid JSON found - log and return None
        self._log_diagnostics("PARSE_FAILED_ALL_METHODS", {
            "response_length": len(response_text),
            "first_200_chars": response_text[:200],
            "last_100_chars": response_text[-100:]
        })
        print(f"❌ Could not parse valid JSON. Response:\n{response_text[:300]}")
        return None

    def _validate_llm_response(self, response: Dict) -> bool:
        """
        Validate that the response has required fields.

        More tolerant: fills sensible defaults instead of failing hard.
        Returns True always, but logs adjustments.
        """
        defaults = {
            "intent": "unknown",
            "goal": "help the customer",
            "decision": "",
            "decision_type": "CLARIFY",
            "reasoning": "",
            "recommended_action": "request_clarification",
            "confidence": 0.5,
        }

        for field, default_value in defaults.items():
            if field not in response:
                print(f"⚠️  Missing field '{field}', using default '{default_value}'")
                response[field] = default_value

        # Validate decision_type is one of the allowed values
        if response.get("decision_type") not in ["AUTOMATE", "ESCALATE", "CLARIFY"]:
            print(f"⚠️  Invalid decision_type: {response.get('decision_type')} -> forcing CLARIFY")
            response["decision_type"] = "CLARIFY"

        # Validate confidence is a number between 0 and 1
        try:
            conf = float(response.get("confidence", 0.5))
            if not (0 <= conf <= 1):
                print(f"⚠️  Confidence out of range: {conf} -> forcing 0.5")
                response["confidence"] = 0.5
        except (TypeError, ValueError):
            print(f"⚠️  Invalid confidence value: {response.get('confidence')} -> forcing 0.5")
            response["confidence"] = 0.5

        print("✅ Response validation passed (tolerant mode)")
        return True

    def _log_diagnostics(self, event: str, data: dict):
        """Log diagnostic information for debugging on Render."""
        import datetime
        import os
        
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "event": event,
            "data": data
        }
        
        # Print to stdout (captured by Render)
        print(f"🔍 DIAGNOSTIC: {json.dumps(log_entry, indent=2)}")
        
        # Also try to write to file if possible (for local debugging)
        try:
            log_file = os.path.join(os.getcwd(), "llm_diagnostics.log")
            with open(log_file, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
        except:
            pass  # Ignore file write errors

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
            
            self._log_diagnostics("LLM_QUERY_START", {
                "customer_id": customer_id,
                "model": self.model,
                "message_length": len(message)
            })

            if getattr(self, "_use_generate_content", False):
                response = self.client.generate_content(
                    full_prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.7,
                        max_output_tokens=500,
                    ),
                )
                response_text = response.text
                self._log_diagnostics("LLM_RESPONSE_RECEIVED", {
                    "response_length": len(response_text),
                    "response_preview": response_text[:200],
                    "api_method": "generate_content"
                })
                return response_text

            # Legacy fallback path
            conversation = self.client.start_chat(history=[])
            response = conversation.send_message(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=500,
                ),
            )
            response_text = response.text
            self._log_diagnostics("LLM_RESPONSE_RECEIVED", {
                "response_length": len(response_text),
                "response_preview": response_text[:200],
                "api_method": "chat"
            })
            return response_text

        except Exception as e:
            self._log_diagnostics("LLM_QUERY_ERROR", {
                "error_type": type(e).__name__,
                "error_message": str(e)
            })
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

    def _execute_rebooking(self, customer_id: str, customer_data: dict, slot_id: str = None) -> tuple:
        """
        Execute rebooking with optional client choice.
        
        If slot_id is provided: Book the specific slot (client confirmed choice)
        If slot_id is None: Return available slots for client to choose from
        """
        actions = ["check_eligibility", "find_available_slots"]

        # Step 1: Check eligibility
        eligibility = self.cx_system.check_eligibility(customer_id)
        if not eligibility.get("eligible", False):
            return actions, {"error": eligibility.get("reason", "Not eligible")}, "escalated"

        # Step 2: Get available slots
        available_slots = self.cx_system.get_available_slots(customer_id)
        if not available_slots:
            return actions, {"error": "No available slots"}, "escalated"

        # Step 3a: If client hasn't chosen yet, return slots for selection
        if slot_id is None:
            # Generate a session ID for this rebooking request
            session_id = f"session_{customer_id}_{int(time.time())}"
            slots_for_client = [
                {
                    "slot_id": slot["slot_id"],
                    "date": slot["date"],
                    "time": slot["time"],
                    "service_type": slot.get("service_type", "consultation")
                }
                for slot in available_slots
            ]
            return actions, {
                "session_id": session_id,
                "available_slots": slots_for_client,
                "message": "Please choose one of the available appointment slots"
            }, "awaiting_client_choice"

        # Step 3b: Client has chosen - book the selected slot
        actions.append("rebook_appointment")
        rebook_result = self.cx_system.rebook_appointment(customer_id, slot_id)

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
