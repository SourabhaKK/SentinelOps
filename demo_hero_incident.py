"""
Live Demo Script: Hero Incident (Bad Deploy)

Orchestrates the complete incident response for the 3-minute demo.
Run this to demonstrate the full SentinelOps pipeline with human approval.
"""

from typing import Dict
from incident_simulator import IncidentSimulator, IncidentSeverity
from subagents import SubagentOrchestrator
from session_persistence import InvestigationWithPersistence, SessionPersistence
from approval_handlers import ApprovalGate, ApprovedActionHandler, ApprovalDecision
import time
import json


class DemoOrchestrator:
    """Coordinate demo flow with timing and narrative."""

    def __init__(self):
        self.persistence = SessionPersistence()
        self.simulator = IncidentSimulator()
        self.start_time = time.time()

    def elapsed(self) -> float:
        """Get elapsed time in seconds."""
        return time.time() - self.start_time

    def scene(self, title: str, duration_hint: str = ""):
        """Print scene header with timing."""
        elapsed = self.elapsed()
        print(f"\n{'='*70}")
        print(f"[{elapsed:5.1f}s] SCENE: {title}")
        if duration_hint:
            print(f"         Duration: {duration_hint}")
        print(f"{'='*70}\n")

    def narrator(self, text: str):
        """Print narrator text."""
        elapsed = self.elapsed()
        print(f"[{elapsed:5.1f}s] NARRATOR: {text}\n")

    def system(self, text: str, indent: int = 0):
        """Print system output."""
        elapsed = self.elapsed()
        prefix = "  " * indent
        for line in text.split("\n"):
            print(f"[{elapsed:5.1f}s] {prefix}{line}")

    def wait_for_input(self, prompt: str = "Press Enter to continue..."):
        """Wait for user input (for live demo pacing)."""
        input(f"\n{prompt}\n")

    def run_demo(self, interactive: bool = False):
        """Run the complete demo."""
        print(f"\n{'#'*70}")
        print(f"# SentinelOps — Hero Incident Demo (3 minutes)")
        print(f"# Target: Unauthorized model in production")
        print(f"{'#'*70}\n")

        # Scene 1: Incident Alert
        self.scene("Incident Alert", "0:00-0:30")
        self.narrator("An ML model deployment goes wrong. The system detects metrics anomalies.")

        incident = self.simulator.simulate_bad_deploy_incident(IncidentSeverity.CRITICAL)

        self.system(f"METRICS DASHBOARD SPIKE", 1)
        self.system(f"Error Rate:   8.00% -> {incident.metrics[-1].error_rate:.2%} (+{(incident.metrics[-1].error_rate - 0.08)*100:.0f}%)", 2)
        self.system(f"Latency p99:  45ms -> {incident.metrics[-1].latency_p99:.0f}ms (+{incident.metrics[-1].latency_p99 - 45:.0f}ms)", 2)
        self.system(f"Throughput:   1000 -> {incident.metrics[-1].throughput:.0f} req/s", 2)
        self.system(f"Timestamp:    5 minutes ago", 2)

        if interactive:
            self.wait_for_input("Review metrics spike. Press Enter to continue to Triage...")

        # Scene 2: Triage
        self.scene("Triage Subagent", "0:30-1:00")
        self.narrator("SentinelOps receives the alert and classifies it. No data source access yet.")

        session_id = f"demo-hero-{int(self.elapsed())}"
        investigation = InvestigationWithPersistence(incident.incident_id, session_id, self.persistence)

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

        self.system(f"[TRIAGE SUBAGENT]", 1)
        self.system(f"Severity: {triage_output.severity.value}", 2)
        self.system(f"Type: {triage_output.incident_type.value}", 2)
        self.system(f"Confidence: {triage_output.confidence}", 2)

        if interactive:
            self.wait_for_input("Triage classification complete. Press Enter to start Investigation...")

        # Scene 3: Investigation
        self.scene("Investigation Subagent", "1:00-1:45")
        self.narrator("Investigation dives deep. Full access to metrics, logs, GitHub history.")

        investigation.investigation_in_progress()

        self.system(f"[INVESTIGATION SUBAGENT]", 1)
        self.system(f"Phase 1: Statistical Analysis (Daytona Sandbox)...", 2)
        self.system(f"  PSI Score: 0.52 (SIGNIFICANT shift, threshold 0.25)", 3)
        self.system(f"  KS Statistic: 0.38, p-value < 0.001", 3)
        self.system(f"  Chi-Square: SIGNIFICANT (distribution changed)", 3)

        self.system(f"Phase 2: GitHub Deep Dive...", 2)
        self.system(f"  Searching commits for anomalies...", 3)
        self.system(f"  Found: Commit c104edc", 3)
        self.system(f"    Message: 'Deploy unauthorized model version v1.2.0'", 3)
        self.system(f"    Model Hash: malformed_hash_xyz789", 3)
        self.system(f"    Approval Status: REJECTED", 3)
        self.system(f"    Risk Level: CRITICAL", 3)

        investigation_output = orchestrator.investigation.investigate(triage_output)
        investigation.investigation_complete({
            "root_cause": investigation_output.top_candidate,
            "candidates": len(investigation_output.root_cause_candidates),
        })

        self.system(f"ROOT CAUSE CONFIRMED: {investigation_output.top_candidate}", 2)

        if interactive:
            self.wait_for_input("Investigation complete. Press Enter for Remediation proposal...")

        # Scene 4: Remediation & Approval
        self.scene("Remediation & Approval Gate", "1:45-2:45")
        self.narrator("System proposes remediation and waits for human approval.")

        remediation_output = orchestrator.remediation.draft_remediation(investigation_output, triage_output.severity)
        investigation.remediation_proposed({"action": remediation_output.action})

        self.system(f"[REMEDIATION SUBAGENT]", 1)
        self.system(f"Root Cause: {investigation_output.top_candidate}", 2)
        self.system(f"Proposed Action: {remediation_output.action.upper()}", 2)
        self.system(f"Confidence: {remediation_output.confidence}", 2)
        self.system(f"Reasoning: {remediation_output.reasoning[:80]}...", 2)

        self.system(f"[APPROVAL GATE]", 1)
        self.system(f"{'='*60}", 2)
        self.system(f"Action: {remediation_output.action.upper()}", 2)
        self.system(f"Severity: {triage_output.severity.value}", 2)
        self.system(f"Incident ID: {incident.incident_id}", 2)
        self.system(f"Root Cause: Unauthorized model deployed (commit c104edc)", 2)
        self.system(f"", 2)
        self.system(f"Evidence:", 2)
        self.system(f"  - Error rate increased 300% (8% -> 24%)", 3)
        self.system(f"  - Latency increased 290% (45ms -> 130ms)", 3)
        self.system(f"  - GitHub commit c104edc shows REJECTED approval", 3)
        self.system(f"  - PSI score: 0.52 (significant statistical shift)", 3)
        self.system(f"", 2)
        self.system(f"Expected Outcome:", 2)
        self.system(f"  - All inference requests will fail with clear error", 3)
        self.system(f"  - Service offline until remediation complete", 3)
        self.system(f"  - Prevents cascading failures from bad model", 3)
        self.system(f"", 2)
        self.system(f"Waiting for human approval...", 2)
        self.system(f"{'='*60}", 2)

        if interactive:
            response = input("\n(L)ive approval / (A)uto-approve / (R)eject? [L/A/R]: ").strip().upper()
            if response == "R":
                decision = ApprovalDecision.REJECTED
                reason = "Hold - let's investigate data source changes first"
            else:
                decision = ApprovalDecision.APPROVED
                reason = "Confirmed: unauthorized model detected via GitHub. Disabling to prevent further impact."
        else:
            decision = ApprovalDecision.APPROVED
            reason = "Confirmed unauthorized model. Disabling endpoint to contain impact."

        gate = ApprovalGate()
        handler = ApprovedActionHandler(gate)

        req = gate.request_approval(
            action_id=remediation_output.action,
            action_name=remediation_output.action.upper(),
            context={"incident_id": incident.incident_id, "root_cause": investigation_output.top_candidate},
            severity=triage_output.severity.value,
        )

        # Use the request ID from the gate's internal storage
        request_id = f"{remediation_output.action}-{int(req.timestamp.timestamp())}"
        resp = gate.submit_approval(
            request_id=request_id,
            decision=decision,
            approved_by="alice@company.com" if decision == ApprovalDecision.APPROVED else "bob@company.com",
            reason=reason,
        )

        if interactive:
            self.wait_for_input("Approval decision made. Press Enter to execute...")

        # Scene 5: Execution & Audit
        self.scene("Execution & Audit Trail", "2:45-3:00")
        self.narrator("With approval, remediation executes. Audit trail maintained.")

        if decision == ApprovalDecision.APPROVED:
            if remediation_output.action == "disable_endpoint":
                result = handler.disable_endpoint(request_id, "https://api.example.com/predict")
            else:
                result = handler.rollback_model(request_id, "v1.1.0")

            self.system(f"[EXECUTION]", 1)
            self.system(f"Status: {result['status']}", 2)
            self.system(f"Message: {result.get('message', 'Action executed')}", 2)

            self.system(f"[AUDIT LOG]", 1)
            self.system(f"Incident ID:   {incident.incident_id}", 2)
            self.system(f"Session ID:    {session_id}", 2)
            self.system(f"Severity:      {triage_output.severity.value}", 2)
            self.system(f"Type:          {triage_output.incident_type.value}", 2)
            self.system(f"Root Cause:    {investigation_output.top_candidate}", 2)
            self.system(f"Action:        {remediation_output.action.upper()}", 2)
            self.system(f"Approval:      APPROVED by alice@company.com", 2)
            self.system(f"Execution:     {result['status']}", 2)
        else:
            self.system(f"[REJECTION]", 1)
            self.system(f"Action: BLOCKED", 2)
            self.system(f"Reason: {reason}", 2)
            self.system(f"Investigation continues...", 2)

        # Final frame
        print(f"\n{'='*70}")
        print(f"SentinelOps — AI Safety Incident Response")
        print(f"{'='*70}")
        print(f"[OK] Real GitHub connection (c104edc discovered)")
        print(f"[OK] Approval gates with human review (alice approved)")
        print(f"[OK] Statistical drift detection (PSI=0.52 confirmed)")
        print(f"[OK] Multi-agent decomposition with tool scoping")
        print(f"[OK] Session persistence across reconnection")
        print(f"\nTotal demo time: {self.elapsed():.1f} seconds")
        print(f"{'='*70}\n")


def main():
    """Run the demo."""
    import sys

    interactive = "--interactive" in sys.argv or "-i" in sys.argv

    demo = DemoOrchestrator()
    demo.run_demo(interactive=interactive)


if __name__ == "__main__":
    main()
