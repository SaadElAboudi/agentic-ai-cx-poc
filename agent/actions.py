"""
actions.py - Mocked CX System Actions

This module mocks interactions with external CX systems:
- Appointment management
- Customer data access
- Notifications
- Escalation to human agents
"""

import json
import os
from typing import Dict, List, Optional
from datetime import datetime


class CXSystemMock:
    """
    Mocks interactions with CX platform systems (e.g., Genesys, Twilio, etc.).
    In production, these would be real API calls to the CX platform.
    """

    def __init__(self, data_dir: str = "data"):
        """Initialize the mock system with data from JSON files."""
        self.data_dir = data_dir
        self.customers = self._load_json("customers.json").get("customers", [])
        self.appointments_data = self._load_json("appointments.json")
        self.available_slots = self.appointments_data.get("available_slots", [])
        self.customer_appointments = self.appointments_data.get(
            "customer_appointments", {}
        )

    def _load_json(self, filename: str) -> dict:
        """Load JSON data from the data directory."""
        filepath = os.path.join(self.data_dir, filename)
        try:
            with open(filepath, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: {filepath} not found")
            return {}

    # ==================== CUSTOMER ACTIONS ====================

    def get_customer(self, customer_id: str) -> Optional[Dict]:
        """Retrieve customer information from CX system."""
        for customer in self.customers:
            if customer["customer_id"] == customer_id:
                return customer
        return None

    def check_eligibility(self, customer_id: str) -> Dict:
        """
        Check if customer is eligible for rebooking.

        Returns eligibility status with reason.
        """
        customer = self.get_customer(customer_id)
        if not customer:
            return {"eligible": False, "reason": "Customer not found"}

        # Eligibility rules
        if customer["account_status"] != "active":
            return {
                "eligible": False,
                "reason": f"Account status is {customer['account_status']}",
            }

        if customer["missed_appointment_count"] > 2:
            return {
                "eligible": False,
                "reason": "Customer has exceeded missed appointment limit (max 2)",
            }

        if customer["loyalty_tier"] == "bronze" and customer["missed_appointment_count"] > 0:
            return {
                "eligible": False,
                "reason": "Bronze tier customers cannot rebook after a miss",
            }

        return {"eligible": True, "reason": "Customer is eligible for rebooking"}

    # ==================== APPOINTMENT ACTIONS ====================

    def get_available_slots(self, customer_id: str, limit: int = 5) -> List[Dict]:
        """
        Get available appointment slots for a customer.

        In production, this would filter by customer preferences, location, etc.
        """
        customer = self.get_customer(customer_id)
        if not customer:
            return []

        # Return available slots (mocked as first N slots)
        return self.available_slots[:limit]

    def get_customer_missed_appointment(self, customer_id: str) -> Optional[Dict]:
        """Retrieve the most recent missed appointment for a customer."""
        appointments = self.customer_appointments.get(customer_id, [])
        missed = [a for a in appointments if a["status"] == "missed"]
        if missed:
            return missed[-1]  # Return most recent
        return None

    def rebook_appointment(
        self, customer_id: str, slot_id: str
    ) -> Dict:
        """
        Rebook an appointment for a customer in the available slot.

        In production, this would call the appointment scheduling system.
        """
        customer = self.get_customer(customer_id)
        if not customer:
            return {
                "success": False,
                "reason": "Customer not found",
                "appointment_id": None,
            }

        # Find the slot
        slot = next((s for s in self.available_slots if s["slot_id"] == slot_id), None)
        if not slot:
            return {
                "success": False,
                "reason": "Slot not found",
                "appointment_id": None,
            }

        # Generate new appointment ID
        appointment_id = f"apt_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # Create new appointment (in production, this would be persisted)
        new_appointment = {
            "appointment_id": appointment_id,
            "customer_id": customer_id,
            "service_type": slot["service_type"],
            "scheduled_date": slot["date_time"],
            "status": "confirmed",
            "duration_minutes": slot["duration_minutes"],
            "rebooked_from": "missed_appointment",
        }

        return {
            "success": True,
            "reason": "Appointment successfully rebooked",
            "appointment_id": appointment_id,
            "appointment_details": new_appointment,
        }

    # ==================== NOTIFICATION ACTIONS ====================

    def send_confirmation(self, customer_id: str, appointment_details: Dict) -> Dict:
        """
        Send appointment confirmation to customer via email/SMS.

        In production, this would integrate with email/SMS providers.
        """
        customer = self.get_customer(customer_id)
        if not customer:
            return {"success": False, "reason": "Customer not found"}

        # Mock notification
        confirmation = {
            "success": True,
            "method": "email + SMS",
            "recipient": {
                "email": customer["email"],
                "phone": customer["phone"],
            },
            "appointment_details": {
                "id": appointment_details.get("appointment_id"),
                "date_time": appointment_details.get("scheduled_date"),
                "service_type": appointment_details.get("service_type"),
            },
            "timestamp": datetime.now().isoformat(),
        }

        return confirmation

    # ==================== ESCALATION ACTIONS ====================

    def escalate_to_human(self, customer_id: str, reason: str) -> Dict:
        """
        Escalate the issue to a human agent in the contact center.

        In production, this would route to Genesys/Twilio IVR queue.
        """
        customer = self.get_customer(customer_id)

        escalation_ticket = {
            "ticket_id": f"esc_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "customer_id": customer_id,
            "customer_name": customer["name"] if customer else "Unknown",
            "priority": "normal",
            "reason": reason,
            "timestamp": datetime.now().isoformat(),
            "queue": "missed_appointment_specialist",
            "estimated_wait_time_minutes": 5,
        }

        return {
            "success": True,
            "escalation_ticket": escalation_ticket,
            "message": f"Issue escalated to human agent. Ticket ID: {escalation_ticket['ticket_id']}",
        }

    # ==================== LOGGING & ANALYTICS ====================

    def log_agent_interaction(
        self,
        customer_id: str,
        intent: str,
        decision: str,
        actions: List[str],
        status: str,
    ) -> Dict:
        """
        Log agent interaction for analytics and compliance.

        In production, this would send to a data warehouse.
        """
        interaction_log = {
            "timestamp": datetime.now().isoformat(),
            "customer_id": customer_id,
            "intent": intent,
            "decision": decision,
            "actions": actions,
            "status": status,
        }

        # In production, this would be persisted to a database or analytics system
        print(f"[ANALYTICS] {json.dumps(interaction_log, indent=2)}")

        return {"logged": True, "interaction": interaction_log}
