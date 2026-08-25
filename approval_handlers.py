"""
Approval Gate Handlers

Stub implementations of approval-required actions for SentinelOps.
These handlers require explicit human approval before execution.
"""

from typing import Dict, List, Any
from enum import Enum
from dataclasses import dataclass
from datetime import datetime


class ApprovalDecision(Enum):
    """Human approval decision."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    MODIFIED = "modified"


@dataclass
class ApprovalRequest:
    """Request for human approval of an action."""
    action_id: str
    action_name: str
    incident_context: Dict[str, Any]
    severity: str
    timestamp: datetime
    requested_by: str = "SentinelOps Agent"


@dataclass
class ApprovalResponse:
    """Response to an approval request."""
    request_id: str
    decision: ApprovalDecision
    approved_by: str
    approved_at: datetime
    reason: str
    modifications: Dict[str, Any] = None


class ApprovalGate:
    """Central approval gate for destructive actions."""

    def __init__(self):
        self.pending_approvals: Dict[str, ApprovalRequest] = {}
        self.approval_history: List[ApprovalResponse] = []

    def request_approval(self, action_id: str, action_name: str, context: Dict[str, Any], severity: str) -> ApprovalRequest:
        """
        Request approval for a destructive action.

        Returns: ApprovalRequest that must be approved before execution
        """
        request = ApprovalRequest(
            action_id=action_id,
            action_name=action_name,
            incident_context=context,
            severity=severity,
            timestamp=datetime.now(),
        )

        request_id = f"{action_id}-{int(datetime.now().timestamp())}"
        self.pending_approvals[request_id] = request

        print(f"\n{'='*60}")
        print(f"[APPROVAL REQUIRED]")
        print(f"{'='*60}")
        print(f"Action: {action_name}")
        print(f"Severity: {severity.upper()}")
        print(f"Request ID: {request_id}")
        print(f"Timestamp: {request.timestamp.isoformat()}")
        print(f"\nContext:")
        for key, value in context.items():
            print(f"  {key}: {value}")
        print(f"{'='*60}\n")

        return request

    def submit_approval(self, request_id: str, decision: ApprovalDecision, approved_by: str, reason: str = "") -> ApprovalResponse:
        """
        Submit an approval decision.

        Args:
            request_id: ID of the approval request
            decision: APPROVED, REJECTED, or MODIFIED
            approved_by: Name/ID of approver
            reason: Reason for decision

        Returns: ApprovalResponse with decision details
        """
        if request_id not in self.pending_approvals:
            raise ValueError(f"Approval request not found: {request_id}")

        response = ApprovalResponse(
            request_id=request_id,
            decision=decision,
            approved_by=approved_by,
            approved_at=datetime.now(),
            reason=reason,
        )

        self.approval_history.append(response)
        del self.pending_approvals[request_id]

        status_mark = "[OK]" if decision == ApprovalDecision.APPROVED else "[BLOCKED]" if decision == ApprovalDecision.REJECTED else "[WARN]"
        print(f"{status_mark} Approval {decision.value}: {request_id}")
        if reason:
            print(f"   Reason: {reason}")

        return response

    def can_execute(self, request_id: str) -> bool:
        """Check if an action has been approved for execution."""
        for response in self.approval_history:
            if response.request_id == request_id:
                return response.decision == ApprovalDecision.APPROVED
        return False


class ApprovedActionHandler:
    """Handlers for approved actions (stub implementations)."""

    def __init__(self, approval_gate: ApprovalGate):
        self.gate = approval_gate

    def disable_endpoint(self, request_id: str, endpoint: str) -> Dict[str, Any]:
        """
        Disable model inference endpoint.

        Stub: Would typically call infrastructure API to disable endpoint.
        """
        if not self.gate.can_execute(request_id):
            return {"status": "BLOCKED", "reason": "Action not approved"}

        return {
            "status": "SUCCESS",
            "action": "disable_endpoint",
            "endpoint": endpoint,
            "timestamp": datetime.now().isoformat(),
            "message": f"Endpoint {endpoint} is now OFFLINE. All inference requests will fail.",
        }

    def rollback_model(self, request_id: str, target_version: str) -> Dict[str, Any]:
        """
        Rollback to previous model version.

        Stub: Would typically update model serving infrastructure.
        """
        if not self.gate.can_execute(request_id):
            return {"status": "BLOCKED", "reason": "Action not approved"}

        return {
            "status": "SUCCESS",
            "action": "rollback_model",
            "previous_version": "v1.2.0-unauthorized",
            "target_version": target_version,
            "timestamp": datetime.now().isoformat(),
            "message": f"Model rolled back to {target_version}. Metrics and behavior will shift.",
        }

    def revoke_api_key(self, request_id: str) -> Dict[str, Any]:
        """
        Revoke all active API keys.

        Stub: Would typically invalidate keys in authentication system.
        """
        if not self.gate.can_execute(request_id):
            return {"status": "BLOCKED", "reason": "Action not approved"}

        return {
            "status": "SUCCESS",
            "action": "revoke_api_key",
            "keys_revoked": 127,
            "timestamp": datetime.now().isoformat(),
            "new_keys_issued": 0,
            "message": "All active API keys revoked. Applications must re-authenticate.",
        }

    def publish_incident_report(self, request_id: str, incident_id: str) -> Dict[str, Any]:
        """
        Publish incident report to stakeholders.

        Stub: Would typically send notifications to incident channels.
        """
        if not self.gate.can_execute(request_id):
            return {"status": "BLOCKED", "reason": "Action not approved"}

        return {
            "status": "SUCCESS",
            "action": "publish_incident_report",
            "incident_id": incident_id,
            "recipients": ["security-team@company.com", "incident-channel-slack"],
            "timestamp": datetime.now().isoformat(),
            "message": f"Incident report for {incident_id} published to stakeholders.",
        }


def test_approval_workflow():
    """Test the approval workflow with both accept and reject paths."""
    print("\n" + "="*60)
    print("Testing Approval Gate Workflow")
    print("="*60)

    # Initialize
    gate = ApprovalGate()
    handler = ApprovedActionHandler(gate)

    # Scenario 1: High drift with APPROVAL
    print("\n--- Scenario 1: High drift -> APPROVAL ---")
    req1 = gate.request_approval(
        action_id="disable_endpoint",
        action_name="Disable Model Endpoint",
        context={
            "incident": "High PSI drift detected (0.52)",
            "error_rate_increase": "8% -> 22%",
            "recommendation": "Disable endpoint pending investigation",
        },
        severity="critical",
    )
    request_id_1 = f"disable_endpoint-{int(req1.timestamp.timestamp())}"
    resp1 = gate.submit_approval(
        request_id=request_id_1,
        decision=ApprovalDecision.APPROVED,
        approved_by="alice@company.com",
        reason="Confirmed: unauthorized model version detected. Disabling to prevent further damage.",
    )
    result1 = handler.disable_endpoint(request_id_1, "https://api.example.com/predict")
    print(f"Result: {result1}")

    # Scenario 2: Bad deploy with REJECTION
    print("\n--- Scenario 2: Bad deploy -> REJECTION ---")
    req2 = gate.request_approval(
        action_id="rollback_model",
        action_name="Rollback Model Version",
        context={
            "incident": "Unauthorized model v1.2.0-malformed detected",
            "commit": "c104edc",
            "recommendation": "Rollback to v1.1.0 (last approved version)",
        },
        severity="critical",
    )
    request_id_2 = f"rollback_model-{int(req2.timestamp.timestamp())}"
    resp2 = gate.submit_approval(
        request_id=request_id_2,
        decision=ApprovalDecision.REJECTED,
        approved_by="bob@company.com",
        reason="Don't rollback yet - let's first disable the endpoint and investigate the malformed commit.",
    )
    result2 = handler.rollback_model(request_id_2, "v1.1.0")
    print(f"Result: {result2}")

    # Print history
    print("\n" + "="*60)
    print("Approval History")
    print("="*60)
    for resp in gate.approval_history:
        print(f"{resp.request_id}: {resp.decision.value} by {resp.approved_by}")


if __name__ == "__main__":
    test_approval_workflow()
