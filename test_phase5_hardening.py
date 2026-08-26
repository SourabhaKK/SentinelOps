"""
Phase 5: Persistence & Hardening Test

Run all three incident types end-to-end and test session reconnection.
"""

from typing import Dict
from incident_simulator import IncidentSimulator
from subagents import SubagentOrchestrator
from session_persistence import InvestigationWithPersistence, SessionPersistence
from approval_handlers import ApprovalGate, ApprovedActionHandler, ApprovalDecision
import json


def run_incident_through_pipeline(incident_scenario, persistence: SessionPersistence) -> Dict:
    """
    Run a single incident through the full pipeline.

    Returns: Incident response summary
    """
    incident_id = incident_scenario.incident_id
    incident_type = incident_scenario.incident_type

    print(f"\n{'='*70}")
    print(f"INCIDENT: {incident_type}")
    print(f"ID: {incident_id}")
    print(f"Severity: {incident_scenario.severity.value}")
    print(f"{'='*70}")

    # Create session
    session_id = f"phase5-{incident_id[:10]}"
    investigation = InvestigationWithPersistence(session_id, incident_id, persistence)

    # Step 1: Triage
    print(f"\n[1/4] Triage subagent")
    alert = {
        "alert_type": "metrics_anomaly",
        "metrics": {
            "error_rate": {"baseline": 0.08, "current": incident_scenario.metrics[-1].error_rate},
            "latency_p99": {"baseline": 45, "current": incident_scenario.metrics[-1].latency_p99},
            "throughput": {"baseline": 1000, "current": incident_scenario.metrics[-1].throughput},
        },
        "timestamp": incident_scenario.start_time,
        "duration_seconds": incident_scenario.duration_seconds,
    }

    orchestrator = SubagentOrchestrator(
        {"metrics": incident_scenario.metrics, "logs": incident_scenario.logs},
        incident_scenario.github_commits,
    )

    # Get triage (without full orchestrator output)
    triage_agent = orchestrator.triage
    triage_output = triage_agent.classify(alert)

    triage_dict = {
        "severity": triage_output.severity.value,
        "incident_type": triage_output.incident_type.value,
        "confidence": triage_output.confidence,
    }

    investigation.triage_complete(triage_dict)
    print(f"      Severity: {triage_output.severity.value}")
    print(f"      Type: {triage_output.incident_type.value}")
    print(f"      Confidence: {triage_output.confidence}")

    # Step 2: Investigation
    print(f"\n[2/4] Investigation subagent")
    investigation.investigation_in_progress()

    investigation_output = orchestrator.investigation.investigate(triage_output)

    investigation_dict = {
        "top_candidate": investigation_output.top_candidate,
        "findings_summary": investigation_output.findings_summary,
        "actions_needed": investigation_output.actions_needed,
        "candidates": [
            {
                "candidate": c.candidate,
                "likelihood": c.likelihood,
                "evidence": c.evidence[:50] + "..." if len(c.evidence) > 50 else c.evidence,
            }
            for c in investigation_output.root_cause_candidates
        ],
    }

    investigation.investigation_complete(investigation_dict)
    print(f"      Root cause: {investigation_output.top_candidate}")
    print(f"      Candidates: {len(investigation_output.root_cause_candidates)}")

    # Step 3: Remediation
    print(f"\n[3/4] Remediation subagent")
    remediation_output = orchestrator.remediation.draft_remediation(
        investigation_output,
        triage_output.severity,
    )

    remediation_dict = {
        "action": remediation_output.action,
        "reasoning": remediation_output.reasoning[:60] + "...",
        "confidence": remediation_output.confidence,
    }

    investigation.remediation_proposed(remediation_dict)
    print(f"      Proposed action: {remediation_output.action}")
    print(f"      Confidence: {remediation_output.confidence}")

    # Step 4: Approval gate
    print(f"\n[4/4] Approval gate")
    gate = ApprovalGate()
    handler = ApprovedActionHandler(gate)

    req = gate.request_approval(
        action_id=remediation_output.action,
        action_name=remediation_output.action.upper(),
        context={
            "incident_id": incident_id,
            "root_cause": investigation_output.top_candidate,
        },
        severity=triage_output.severity.value,
    )

    request_id = f"{remediation_output.action}-{int(req.timestamp.timestamp())}"

    # Auto-approve for testing
    resp = gate.submit_approval(
        request_id=request_id,
        decision=ApprovalDecision.APPROVED,
        approved_by="automated-test",
        reason="Auto-approved for Phase 5 testing",
    )

    # Execute
    if remediation_output.action == "disable_endpoint":
        result = handler.disable_endpoint(request_id, "https://api.example.com/predict")
    elif remediation_output.action == "rollback_model":
        result = handler.rollback_model(request_id, "v1.1.0")
    elif remediation_output.action == "revoke_api_key":
        result = handler.revoke_api_key(request_id)
    else:
        result = {"status": "UNKNOWN", "action": remediation_output.action}

    print(f"      Status: {result['status']}")
    if result['status'] == 'SUCCESS':
        print(f"      Message: {result.get('message', 'N/A')[:50]}...")

    return {
        "incident_id": incident_id,
        "incident_type": incident_type,
        "severity": triage_output.severity.value,
        "status": result['status'],
        "action": remediation_output.action,
        "session_id": session_id,
    }


def test_reconnection_on_hero_incident(persistence: SessionPersistence):
    """
    Test session reconnection specifically on the hero incident.

    Simulates:
    1. Start bad-deploy incident investigation
    2. Disconnect mid-investigation
    3. Reconnect and resume
    4. Complete investigation through approval
    """
    print(f"\n\n{'='*70}")
    print("RECONNECTION TEST (Hero Incident)")
    print(f"{'='*70}")

    simulator = IncidentSimulator()
    incident = simulator.simulate_bad_deploy_incident()

    print(f"\nIncident: {incident.incident_type}")
    print(f"ID: {incident.incident_id}")

    # Start investigation
    session_id = f"reconnect-test-{incident.incident_id[:10]}"
    investigation = InvestigationWithPersistence(session_id, incident.incident_id, persistence)

    print(f"\n[Reconnection Test] Phase 1: Initial investigation")
    alert = {
        "alert_type": "metrics_anomaly",
        "metrics": {
            "error_rate": {"baseline": 0.08, "current": incident.metrics[-1].error_rate},
            "latency_p99": {"baseline": 45, "current": incident.metrics[-1].latency_p99},
            "throughput": {"baseline": 1000, "current": incident.metrics[-1].throughput},
        },
        "timestamp": incident.start_time,
        "duration_seconds": incident.duration_seconds,
    }

    orchestrator = SubagentOrchestrator(
        {"metrics": incident.metrics, "logs": incident.logs},
        incident.github_commits,
    )

    # Triage
    triage = orchestrator.triage.classify(alert)
    investigation.triage_complete({"severity": triage.severity.value, "type": triage.incident_type.value})
    print(f"                     Triage complete")

    # Investigation starts
    investigation.investigation_in_progress()
    print(f"                     Investigation started")

    # SIMULATE DISCONNECT
    print(f"\n[Reconnection Test] SIMULATED DISCONNECT mid-investigation")
    investigation.simulate_disconnect()

    # SIMULATE RECONNECTION
    print(f"\n[Reconnection Test] SIMULATED RECONNECTION")
    investigation2 = InvestigationWithPersistence(session_id, incident.incident_id, persistence)
    investigation2.resume_after_disconnect()

    # Continue investigation
    print(f"\n[Reconnection Test] Phase 2: Investigation resumed (post-reconnect)")
    inv_output = orchestrator.investigation.investigate(triage)
    investigation2.investigation_complete({
        "root_cause": inv_output.top_candidate,
        "candidates_count": len(inv_output.root_cause_candidates),
    })
    print(f"                     Investigation complete")

    # Remediation
    print(f"\n[Reconnection Test] Phase 3: Remediation")
    rem_output = orchestrator.remediation.draft_remediation(inv_output, triage.severity)
    investigation2.remediation_proposed({"action": rem_output.action})
    print(f"                     Action: {rem_output.action}")

    # Final context
    print(f"\n[Reconnection Test] FINAL STATE")
    context = investigation2.get_investigation_context()
    print(f"                     Session: {context['session_id']}")
    print(f"                     Disconnections: {context['disconnections']}")
    print(f"                     Reconnections: {context['reconnections']}")
    print(f"                     Final state: {context['state']}")

    # Verify state integrity
    if context['state'] == 'REMEDIATION_PROPOSED' and context['reconnections'] == 1:
        print(f"\n                     [OK] Investigation survived disconnect/reconnect")
        return True
    else:
        print(f"\n                     [FAIL] Investigation state compromised")
        return False


def main():
    print("\n" + "="*70)
    print("PHASE 5: PERSISTENCE & HARDENING TEST")
    print("="*70)

    persistence = SessionPersistence()
    simulator = IncidentSimulator()

    # Get all incidents
    scenarios = simulator.get_all_scenarios()

    results = []

    # Run Incident 1: Low drift
    print("\n\n[TEST 1] Low-Severity Drift")
    result = run_incident_through_pipeline(scenarios["drift_low"], persistence)
    results.append(result)

    # Run Incident 2: High jailbreak
    print("\n\n[TEST 2] High-Severity Jailbreak")
    result = run_incident_through_pipeline(scenarios["jailbreak_high"], persistence)
    results.append(result)

    # Run Incident 3: Critical bad deploy
    print("\n\n[TEST 3] Critical Bad Deploy")
    result = run_incident_through_pipeline(scenarios["bad_deploy_critical"], persistence)
    results.append(result)

    # Test reconnection on hero incident
    reconnect_ok = test_reconnection_on_hero_incident(persistence)

    # Summary
    print(f"\n\n{'='*70}")
    print("PHASE 5 TEST SUMMARY")
    print(f"{'='*70}")

    print(f"\n[Results] Incident Processing:")
    for r in results:
        status_icon = "[OK]" if r['status'] == 'SUCCESS' else "[FAIL]"
        print(f"  {status_icon} {r['incident_type']:20} -> {r['action']:15} ({r['severity']})")

    print(f"\n[Results] Reconnection Test:")
    reconnect_status = "[OK]" if reconnect_ok else "[FAIL]"
    print(f"  {reconnect_status} Hero incident survived disconnect/reconnect")

    all_ok = all(r['status'] == 'SUCCESS' for r in results) and reconnect_ok
    print(f"\n[Result] Phase 5: {'PASS' if all_ok else 'FAIL'}")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
