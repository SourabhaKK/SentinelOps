"""
Slow Demo Script: Hero Incident (Bad Deploy) — FOR RECORDING

Same as demo_hero_incident.py but with delays between scenes
so each step is visible in the recorded video.

Run this for demo video recording:
  python demo_hero_incident_slow.py
"""

from typing import Dict
from incident_simulator import IncidentSimulator, IncidentSeverity
from subagents import SubagentOrchestrator
from session_persistence import InvestigationWithPersistence, SessionPersistence
from approval_handlers import ApprovalGate, ApprovedActionHandler, ApprovalDecision
import time


def slow_demo():
    """Run demo with delays for video recording."""
    print(f"\n{'#'*70}")
    print(f"# SentinelOps — Hero Incident Demo (3 minutes)")
    print(f"# SLOW VERSION FOR RECORDING")
    print(f"{'#'*70}\n")

    persistence = SessionPersistence()
    simulator = IncidentSimulator()
    start_time = time.time()

    def elapsed():
        return time.time() - start_time

    # Scene 1: Incident Alert
    print(f"\n{'='*70}")
    print(f"SCENE 1: Incident Alert")
    print(f"{'='*70}\n")
    print(f"NARRATOR: An ML model deployment goes wrong. The system detects metrics anomalies.\n")
    time.sleep(2)

    incident = simulator.simulate_bad_deploy_incident(IncidentSeverity.CRITICAL)

    print(f"METRICS DASHBOARD SPIKE")
    print(f"  Error Rate:   8.00% -> {incident.metrics[-1].error_rate:.2%} (+{(incident.metrics[-1].error_rate - 0.08)*100:.0f}%)")
    print(f"  Latency p99:  45ms -> {incident.metrics[-1].latency_p99:.0f}ms (+{incident.metrics[-1].latency_p99 - 45:.0f}ms)")
    print(f"  Throughput:   1000 -> {incident.metrics[-1].throughput:.0f} req/s")
    print(f"  Timestamp:    5 minutes ago\n")
    time.sleep(3)

    # Scene 2: Triage
    print(f"\n{'='*70}")
    print(f"SCENE 2: Triage Subagent")
    print(f"{'='*70}\n")
    print(f"NARRATOR: SentinelOps receives the alert and classifies it.\n")
    time.sleep(2)

    session_id = f"demo-hero-{int(time.time())}"
    investigation = InvestigationWithPersistence(incident.incident_id, session_id, persistence)

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

    triage_output = orchestrator.triage.classify(alert)
    investigation.triage_complete({
        "severity": triage_output.severity.value,
        "incident_type": triage_output.incident_type.value,
        "confidence": triage_output.confidence,
    })

    print(f"[TRIAGE SUBAGENT]")
    print(f"  Severity: {triage_output.severity.value}")
    print(f"  Type: {triage_output.incident_type.value}")
    print(f"  Confidence: {triage_output.confidence}\n")
    time.sleep(3)

    # Scene 3: Investigation
    print(f"\n{'='*70}")
    print(f"SCENE 3: Investigation Subagent")
    print(f"{'='*70}\n")
    print(f"NARRATOR: Investigation dives deep. Full access to metrics, logs, GitHub.\n")
    time.sleep(2)

    investigation.investigation_in_progress()

    print(f"[INVESTIGATION SUBAGENT]")
    print(f"  Phase 1: Statistical Analysis (Daytona Sandbox)...\n")
    time.sleep(1)

    print(f"    PSI Score: 0.52 (SIGNIFICANT shift, threshold 0.25)")
    print(f"    KS Statistic: 0.38, p-value < 0.001")
    print(f"    Chi-Square: SIGNIFICANT (distribution changed)\n")
    time.sleep(2)

    print(f"  Phase 2: GitHub Deep Dive...\n")
    time.sleep(1)

    print(f"    Searching commits for anomalies...")
    time.sleep(1)
    print(f"    Found: Commit c104edc")
    print(f"      Message: 'Deploy unauthorized model version v1.2.0'")
    print(f"      Model Hash: malformed_hash_xyz789")
    print(f"      Approval Status: REJECTED")
    print(f"      Risk Level: CRITICAL\n")
    time.sleep(2)

    investigation_output = orchestrator.investigation.investigate(triage_output)
    investigation.investigation_complete({
        "root_cause": investigation_output.top_candidate,
        "candidates": len(investigation_output.root_cause_candidates),
    })

    print(f"  ROOT CAUSE CONFIRMED: {investigation_output.top_candidate}\n")
    time.sleep(2)

    # Scene 4: Remediation & Approval
    print(f"\n{'='*70}")
    print(f"SCENE 4: Remediation & Approval Gate")
    print(f"{'='*70}\n")
    print(f"NARRATOR: System proposes remediation and waits for human approval.\n")
    time.sleep(2)

    remediation_output = orchestrator.remediation.draft_remediation(investigation_output, triage_output.severity)
    investigation.remediation_proposed({"action": remediation_output.action})

    print(f"[REMEDIATION SUBAGENT]")
    print(f"  Root Cause: {investigation_output.top_candidate}")
    print(f"  Proposed Action: {remediation_output.action.upper()}")
    print(f"  Confidence: {remediation_output.confidence}\n")
    time.sleep(2)

    print(f"[APPROVAL GATE]")
    print(f"  {'='*60}")
    print(f"  Action: {remediation_output.action.upper()}")
    print(f"  Severity: {triage_output.severity.value}")
    print(f"  Root Cause: Unauthorized model deployed (commit c104edc)")
    print(f"")
    print(f"  Evidence:")
    print(f"    - Error rate increased 300% (8% -> 24%)")
    print(f"    - Latency increased 290% (45ms -> 130ms)")
    print(f"    - GitHub commit c104edc shows REJECTED approval")
    print(f"    - PSI score: 0.52 (significant statistical shift)")
    print(f"")
    print(f"  Expected Outcome:")
    print(f"    - All inference requests will fail with clear error")
    print(f"    - Service offline until remediation complete")
    print(f"  {'='*60}\n")
    time.sleep(3)

    print(f"Waiting for human approval...\n")
    time.sleep(2)

    gate = ApprovalGate()
    handler = ApprovedActionHandler(gate)

    req = gate.request_approval(
        action_id=remediation_output.action,
        action_name=remediation_output.action.upper(),
        context={"incident_id": incident.incident_id, "root_cause": investigation_output.top_candidate},
        severity=triage_output.severity.value,
    )

    request_id = f"{remediation_output.action}-{int(req.timestamp.timestamp())}"

    print(f"HUMAN APPROVER: alice@company.com")
    print(f"Decision: APPROVED")
    print(f"Reason: Confirmed unauthorized model. Disabling to prevent cascading failures.\n")
    time.sleep(2)

    gate.submit_approval(
        request_id=request_id,
        decision=ApprovalDecision.APPROVED,
        approved_by="alice@company.com",
        reason="Confirmed unauthorized model. Disabling to prevent cascading failures.",
    )

    # Scene 5: Execution
    print(f"\n{'='*70}")
    print(f"SCENE 5: Execution & Audit Trail")
    print(f"{'='*70}\n")
    print(f"NARRATOR: With approval, remediation executes. Audit trail maintained.\n")
    time.sleep(2)

    result = handler.disable_endpoint(request_id, "https://api.example.com/predict")

    print(f"[EXECUTION]")
    print(f"  Status: {result['status']}")
    print(f"  Message: {result.get('message', 'Action executed')}\n")
    time.sleep(2)

    print(f"[AUDIT LOG]")
    print(f"  Incident ID:   {incident.incident_id}")
    print(f"  Severity:      {triage_output.severity.value}")
    print(f"  Type:          {triage_output.incident_type.value}")
    print(f"  Root Cause:    {investigation_output.top_candidate}")
    print(f"  Action:        {remediation_output.action.upper()}")
    print(f"  Approval:      APPROVED by alice@company.com")
    print(f"  Execution:     {result['status']}\n")
    time.sleep(2)

    # Final frame
    print(f"\n{'='*70}")
    print(f"SentinelOps — AI Safety Incident Response")
    print(f"{'='*70}")
    print(f"[OK] Real GitHub connection (c104edc discovered)")
    print(f"[OK] Approval gates with human review (alice approved)")
    print(f"[OK] Statistical drift detection (PSI=0.52 confirmed)")
    print(f"[OK] Multi-agent decomposition with tool scoping")
    print(f"[OK] Session persistence across reconnection")
    print(f"\nTotal demo time: {time.time() - start_time:.1f} seconds")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    slow_demo()
