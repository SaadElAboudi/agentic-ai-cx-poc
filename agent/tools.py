"""
tools.py - Tool Registry for Agentic Control

Defines a unified interface for the agent's capabilities (tools) and a registry
to execute them. Tools wrap the underlying CXSystemMock methods to provide
consistent inputs/outputs for planning and execution.
"""

from typing import Any, Dict, Callable, Optional

from .actions import CXSystemMock


class Tool:
    """A single capability the agent can execute."""

    def __init__(
        self,
        name: str,
        description: str,
        runner: Callable[[Dict[str, Any]], Dict[str, Any]],
    ):
        self.name = name
        self.description = description
        self._runner = runner

    def run(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return self._runner(params)


class ToolRegistry:
    """Registry and facade for all available tools."""

    def __init__(self, cx_system: CXSystemMock):
        self.cx = cx_system
        self.tools: Dict[str, Tool] = {}
        self._register_all()

    def _register(self, tool: Tool) -> None:
        self.tools[tool.name] = tool

    def _register_all(self) -> None:
        # Check eligibility
        self._register(
            Tool(
                name="check_eligibility",
                description="Check if customer is eligible to rebook",
                runner=lambda p: self.cx.check_eligibility(p["customer_id"]),
            )
        )

        # Get available slots
        self._register(
            Tool(
                name="get_available_slots",
                description="List next available appointment slots",
                runner=lambda p: {
                    "success": True,
                    "slots": self.cx.get_available_slots(p["customer_id"], p.get("limit", 5)),
                },
            )
        )

        # Get most recent missed appointment
        self._register(
            Tool(
                name="get_missed_appointment",
                description="Fetch most recent missed appointment details",
                runner=lambda p: {
                    "success": True,
                    "missed": self.cx.get_customer_missed_appointment(p["customer_id"]),
                },
            )
        )

        # Rebook appointment in a specific slot
        self._register(
            Tool(
                name="rebook_appointment",
                description="Rebook the appointment into a selected slot",
                runner=lambda p: self.cx.rebook_appointment(p["customer_id"], p["slot_id"]),
            )
        )

        # Send confirmation to customer
        self._register(
            Tool(
                name="send_confirmation",
                description="Send SMS/email confirmation with appointment details",
                runner=lambda p: self.cx.send_confirmation(p["customer_id"], p["appointment_details"]),
            )
        )

        # Escalate to human
        self._register(
            Tool(
                name="escalate_to_human",
                description="Create escalation ticket and route to queue",
                runner=lambda p: self.cx.escalate_to_human(p["customer_id"], p.get("reason", "Escalation")),
            )
        )

        # Log interaction (utility)
        self._register(
            Tool(
                name="log_interaction",
                description="Log agent interaction for analytics",
                runner=lambda p: self.cx.log_agent_interaction(
                    p["customer_id"], p["intent"], p["decision"], p.get("actions", []), p.get("status", "unknown")
                ),
            )
        )

    def run(self, name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        tool = self.tools.get(name)
        if not tool:
            return {"success": False, "reason": f"Unknown tool: {name}"}
        return tool.run(params)
