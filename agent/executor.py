"""
executor.py - Plan Execution and Verification Loop

Runs planned steps, wires parameters between steps, verifies expected outcomes,
and handles failures via specified on_fail branches.
"""

from typing import Any, Dict, List, Tuple

from .tools import ToolRegistry


class PlanExecutor:
    def __init__(self, tools: ToolRegistry):
        self.tools = tools
        self.artifacts: Dict[str, Dict[str, Any]] = {}

    def _resolve_params(self, step: Dict[str, Any]) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Fixed params
        for k, v in step.get("params", {}).items():
            params[k] = v
        for k, v in step.get("fixed_params", {}).items():
            params[k] = v
        # Params from previous step outputs
        for k, spec in step.get("params_from_prev", {}).items():
            if len(spec) == 2:
                src_step, src_key = spec
                params[k] = self.artifacts[src_step][src_key]
            elif len(spec) == 4:
                src_step, src_key, idx, inner_key = spec
                params[k] = self.artifacts[src_step][src_key][idx][inner_key]
        return params

    def _verify(self, result: Dict[str, Any], expect: Dict[str, Any]) -> bool:
        if not expect:
            return True
        # Simple expectation checks
        for key, val in expect.items():
            if key == "slots_non_empty":
                if not result.get("slots"):
                    return False
                if len(result["slots"]) == 0:
                    return False
            else:
                if result.get(key) != val:
                    return False
        return True

    def run(self, plan: List[Dict[str, Any]]) -> Tuple[List[str], Dict[str, Any]]:
        actions_taken: List[str] = []
        final_ctx: Dict[str, Any] = {}

        for step in plan:
            tool_name = step["tool"]
            params = self._resolve_params(step)
            result = self.tools.run(tool_name, params)
            self.artifacts[tool_name] = result
            actions_taken.append(tool_name)

            if not self._verify(result, step.get("expect", {})):
                # Handle failure case
                on_fail = step.get("on_fail")
                if on_fail:
                    fail_result = self.tools.run(on_fail["tool"], on_fail["params"])
                    self.artifacts[on_fail["tool"]] = fail_result
                    actions_taken.append(on_fail["tool"])
                    final_ctx["escalation_ticket"] = fail_result.get("escalation_ticket")
                    final_ctx["status"] = "escalated"
                    return actions_taken, final_ctx
                else:
                    final_ctx["status"] = "failed"
                    final_ctx["reason"] = result.get("reason", "Step failed")
                    return actions_taken, final_ctx

        # Success path: propagate useful outputs
        final_ctx["status"] = "resolved"
        # If rebook + confirm were executed, expose details
        if "rebook_appointment" in self.artifacts:
            rb = self.artifacts["rebook_appointment"]
            final_ctx["appointment_details"] = rb.get("appointment_details")
        if "send_confirmation" in self.artifacts:
            sc = self.artifacts["send_confirmation"]
            final_ctx["confirmation"] = sc
        return actions_taken, final_ctx
