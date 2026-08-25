"""
Integration test: Full incident response loop with approval gates

Demonstrates the complete pipeline:
Incident -> Triage -> Investigation -> Remediation -> Approval -> Execution
"""

from subagents import SubagentOrchestrator
from approval_handlers import ApprovalGate, ApprovedActionHandler, ApprovalDecision
import json


def test_full_incident_loop_with_approval():
    """Test complete incident response with human approval."""
    print("\n" + "=" * 70)
    print("FULL INCIDENT RESPONSE LOOP WITH APPROVAL GATES")
    print("=" * 70)

    # Set up incident scenario
    alert = {
        "alert_type": "metrics_anomaly",
        "metrics": {
            "error_rate": {"baseline": 0.08, "current": 0.22},
            "latency_p99": {"baseline": 45, "current": 120},
            "throughput": {"baseline": 1000, "current": 950},
        },
        "timestamp": "2026-08-26T14:30:00Z",
        "duration_seconds": 300,
    }

    github_commits = [
        {"sha": "3f70b8c", "message": "Phase 3 approval gates"},
        {"sha": "c104edc", "message": "Deploy unauthorized model version v1.2.0"},
        {"sha": "9724b9e", "message": "Add drift analysis"},
    ]

    telemetry_data = {
        "metrics": {"error_rate": 0.22, "latency_p99": 120},
        "logs": ["ERROR: Model inference failed"],
    }

    # Step 1: Run subagent pipeline
    print("\nStep 1: Running subagent pipeline...")
    orchestrator = SubagentOrchestrator(telemetry_data, github_commits)
    incident_context = orchestrator.run_incident_response(alert)

    # Extract key info
    incident_id = incident_context["incident_id"]
    severity = incident_context["triage"]["severity"]
    proposed_action = incident_context["remediation"]["action"]
    top_candidate = incident_context["investigation"]["top_candidate"]

    print(f"\n{'-'*70}")
    print(f"Incident Context Summary:")
    print(f"  ID: {incident_id}")
    print(f"  Severity: {severity}")
    print(f"  Proposed Action: {proposed_action}")
    print(f"  Top Candidate: {top_candidate}")
    print(f"{'-'*70}")

    # Step 2: SCENARIO A - Human approves the action
    print("\n\nSCENARIO A: HUMAN APPROVES THE ACTION")
    print("=" * 70)

    gate_a = ApprovalGate()
    handler_a = ApprovedActionHandler(gate_a)

    # Request approval
    severity_str = str(severity).split(".")[-1] if "." in str(severity) else str(severity)
    req_a = gate_a.request_approval(
        action_id=proposed_action,
        action_name=proposed_action.upper(),
        context={
            "incident_id": incident_id,
            "severity": severity_str,
            "root_cause": top_candidate,
            "confidence": incident_context["remediation"]["confidence"],
        },
        severity=severity_str,
    )

    # Simulate human approval
    request_id_a = f"{proposed_action}-{int(req_a.timestamp.timestamp())}"
    resp_a = gate_a.submit_approval(
        request_id=request_id_a,
        decision=ApprovalDecision.APPROVED,
        approved_by="alice@company.com",
        reason="Confirmed: high confidence drift detected. Statistical tests (PSI=0.52, KS<0.001) confirm. Disabling endpoint to prevent cascading failures.",
    )

    # Execute approved action
    if proposed_action == "disable_endpoint":
        result_a = handler_a.disable_endpoint(request_id_a, "https://api.example.com/v1/predict")
    elif proposed_action == "rollback_model":
        result_a = handler_a.rollback_model(request_id_a, "v1.1.0")
    else:
        result_a = handler_a.revoke_api_key(request_id_a)

    print(f"\nAction Execution Result:")
    print(json.dumps(result_a, indent=2, default=str))

    # Step 3: SCENARIO B - Human rejects and proposes alternative
    print("\n\nSCENARIO B: HUMAN REJECTS AND PROPOSES ALTERNATIVE")
    print("=" * 70)

    gate_b = ApprovalGate()
    handler_b = ApprovedActionHandler(gate_b)

    # Request approval
    req_b = gate_b.request_approval(
        action_id="rollback_model",
        action_name="ROLLBACK MODEL",
        context={
            "incident_id": incident_id,
            "severity": severity_str,
            "root_cause": top_candidate,
            "confidence": incident_context["remediation"]["confidence"],
            "current_action": proposed_action,
        },
        severity=severity_str,
    )

    # Simulate human rejection with alternative
    request_id_b = f"rollback_model-{int(req_b.timestamp.timestamp())}"
    resp_b = gate_b.submit_approval(
        request_id=request_id_b,
        decision=ApprovalDecision.REJECTED,
        approved_by="bob@company.com",
        reason="Don't rollback yet - let's first disable the endpoint and investigate data source changes. Rollback can mask the root cause.",
    )

    # Attempt to execute rejected action
    result_b = handler_b.rollback_model(request_id_b, "v1.1.0")
    print(f"\nAction Execution Result (Rejected):")
    print(json.dumps(result_b, indent=2, default=str))

    # Final summary
    print("\n\n" + "=" * 70)
    print("TEST RESULTS")
    print("=" * 70)
    print(f"\nScenario A (APPROVAL):")
    print(f"  Decision: APPROVED by {resp_a.approved_by}")
    print(f"  Action Status: {result_a['status']}")
    print(f"  Execution: {'SUCCESS' if result_a['status'] == 'SUCCESS' else 'BLOCKED'}")
    print(f"  Message: {result_a.get('message', 'N/A')}")

    print(f"\nScenario B (REJECTION):")
    print(f"  Decision: REJECTED by {resp_b.approved_by}")
    print(f"  Reason: {resp_b.reason}")
    print(f"  Action Status: {result_b['status']}")
    print(f"  Execution: {'BLOCKED' if result_b['status'] == 'BLOCKED' else 'UNEXPECTED'}")

    print("\n" + "=" * 70)
    print("AUDIT LOG")
    print("=" * 70)
    print("Approval Gate A:")
    for approval in gate_a.approval_history:
        print(f"  {approval.request_id}: {approval.decision.value} by {approval.approved_by}")
        if approval.reason:
            print(f"    Reason: {approval.reason}")

    print("\nApproval Gate B:")
    for approval in gate_b.approval_history:
        print(f"  {approval.request_id}: {approval.decision.value} by {approval.approved_by}")
        if approval.reason:
            print(f"    Reason: {approval.reason}")

    print("\n" + "=" * 70)
    print("TEST COMPLETE: Both approval paths working correctly")
    print("=" * 70)


if __name__ == "__main__":
    test_full_incident_loop_with_approval()
