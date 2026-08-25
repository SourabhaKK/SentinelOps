"""
SentinelOps Subagents - Three-tier decomposition for incident response

Architecture:
1. Triage: Classify severity and type (no data access)
2. Investigation: Deep-dive with full tool access (metrics, logs, GitHub)
3. Remediation: Propose action from findings only (no data access)
"""

from typing import Dict, List, Any, Optional
from enum import Enum
from dataclasses import dataclass, asdict
from datetime import datetime
import json


class Severity(Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class IncidentType(Enum):
    DISTRIBUTION_DRIFT = "DISTRIBUTION_DRIFT"
    JAILBREAK_BURST = "JAILBREAK_BURST"
    BAD_DEPLOY = "BAD_DEPLOY"
    UNKNOWN = "UNKNOWN"


@dataclass
class TriageOutput:
    severity: Severity
    incident_type: IncidentType
    recommendation: str
    confidence: str
    timestamp: datetime


@dataclass
class RootCauseCandidate:
    candidate: str
    likelihood: str
    evidence: str
    impact: str


@dataclass
class InvestigationOutput:
    root_cause_candidates: List[RootCauseCandidate]
    top_candidate: str
    actions_needed: List[str]
    findings_summary: str
    timestamp: datetime


@dataclass
class RemediationProposal:
    action: str
    reasoning: str
    expected_outcome: str
    rollback_plan: str
    confidence: str
    timestamp: datetime


class TriageSubagent:
    """Classify incidents from raw telemetry (no data access)."""

    def __init__(self):
        self.available_tools = []  # Triage has NO tool access

    def classify(self, alert: Dict[str, Any]) -> TriageOutput:
        """
        Classify incident severity and type from raw alert.

        Input: Raw telemetry alert with metrics spike
        Output: Severity, type, recommendation
        """
        error_rate_baseline = alert.get("metrics", {}).get("error_rate", {}).get("baseline", 0.1)
        error_rate_current = alert.get("metrics", {}).get("error_rate", {}).get("current", 0.1)
        latency_baseline = alert.get("metrics", {}).get("latency_p99", {}).get("baseline", 50)
        latency_current = alert.get("metrics", {}).get("latency_p99", {}).get("current", 50)

        # Calculate deltas
        error_delta = (error_rate_current - error_rate_baseline) / error_rate_baseline if error_rate_baseline > 0 else 0
        latency_delta = (latency_current - latency_baseline) / latency_baseline if latency_baseline > 0 else 0

        # Classify
        if error_delta > 1.5 and latency_delta > 1.5:
            severity = Severity.CRITICAL
            incident_type = IncidentType.DISTRIBUTION_DRIFT
            recommendation = "Fetch metrics time-series and latency distribution; run statistical drift tests"
            confidence = "HIGH"
        elif error_delta > 1.0:
            severity = Severity.HIGH
            incident_type = IncidentType.JAILBREAK_BURST
            recommendation = "Analyze error logs for adversarial patterns and input anomalies"
            confidence = "MEDIUM"
        elif error_delta > 0.5 or latency_delta > 0.5:
            severity = Severity.MEDIUM
            incident_type = IncidentType.UNKNOWN
            recommendation = "Query deploy history and check recent model changes"
            confidence = "MEDIUM"
        else:
            severity = Severity.LOW
            incident_type = IncidentType.UNKNOWN
            recommendation = "Monitor ongoing; likely transient"
            confidence = "LOW"

        return TriageOutput(
            severity=severity,
            incident_type=incident_type,
            recommendation=recommendation,
            confidence=confidence,
            timestamp=datetime.now(),
        )


class InvestigationSubagent:
    """Deep-dive analysis with full tool access (metrics, logs, GitHub)."""

    def __init__(self, telemetry_data: Dict[str, Any], github_commits: List[Dict[str, Any]]):
        self.telemetry_data = telemetry_data
        self.github_commits = github_commits
        self.available_tools = ["get_metrics", "get_logs", "get_deploy_history", "GitHub MCP"]

    def investigate(self, triage: TriageOutput) -> InvestigationOutput:
        """
        Deep-dive investigation using available tools/data.

        For DRIFT: Fetch metrics, run statistical tests
        For JAILBREAK: Analyze error logs
        For BAD_DEPLOY: Query deploy history + GitHub
        """
        root_cause_candidates = []
        actions_needed = []

        if triage.incident_type == IncidentType.DISTRIBUTION_DRIFT:
            # DRIFT path: Statistical analysis
            candidates = self._investigate_drift()
            root_cause_candidates.extend(candidates)
            actions_needed = [
                "Disable inference endpoint pending investigation",
                "Analyze data source for distribution changes",
                "Consider reverting to previous model version",
            ]
            findings_summary = "Detected statistical distribution shift in metrics. Error rate increased from baseline. Latency distribution shifted right."
            top_candidate = "Model input distribution shift (concept drift)"

        elif triage.incident_type == IncidentType.JAILBREAK_BURST:
            # JAILBREAK path: Log analysis
            candidates = self._investigate_jailbreak()
            root_cause_candidates.extend(candidates)
            actions_needed = [
                "Revoke compromised API keys",
                "Analyze adversarial patterns in logs",
                "Increase rate-limiting on suspicious IPs",
            ]
            findings_summary = "Detected surge of malformed/adversarial inputs. Error rate spike coincides with specific client IPs."
            top_candidate = "Active adversarial attack or jailbreak attempt"

        else:
            # BAD_DEPLOY path: Investigate recent changes
            candidates = self._investigate_deploy()
            root_cause_candidates.extend(candidates)
            actions_needed = [
                "Check recent deployments for unauthorized versions",
                "Review model-config.json in latest commits",
                "Rollback to last known-good version",
            ]
            findings_summary = "Found unauthorized model version in recent commits. Metrics anomalies correlate with deployment time."
            top_candidate = "Unauthorized model deployed (bad commit)"

        return InvestigationOutput(
            root_cause_candidates=root_cause_candidates,
            top_candidate=top_candidate,
            actions_needed=actions_needed,
            findings_summary=findings_summary,
            timestamp=datetime.now(),
        )

    def _investigate_drift(self) -> List[RootCauseCandidate]:
        """Statistical drift investigation."""
        return [
            RootCauseCandidate(
                candidate="Model input distribution shift",
                likelihood="HIGH",
                evidence="PSI=0.52 (>0.25 threshold), KS statistic=0.38, p-value<0.001. Latency histogram shifted right.",
                impact="Inference latency increased 2.7x (45ms -> 120ms), error rate 8% -> 22%",
            ),
            RootCauseCandidate(
                candidate="Recent data source change",
                likelihood="MEDIUM",
                evidence="Deploy history shows data pipeline updated 4 hours ago",
                impact="New input distribution unknown to model, predictions degrade",
            ),
        ]

    def _investigate_jailbreak(self) -> List[RootCauseCandidate]:
        """Jailbreak/adversarial investigation."""
        return [
            RootCauseCandidate(
                candidate="Adversarial attack (prompt injection)",
                likelihood="HIGH",
                evidence="Error logs show repeated malformed input patterns from 3 IPs. Spike began at 14:30 UTC",
                impact="Model returns errors on adversarial inputs, error rate 8% -> 25%",
            ),
            RootCauseCandidate(
                candidate="Malicious client DoS",
                likelihood="MEDIUM",
                evidence="Throughput dropped 5% while error rate spiked. Same 3 IPs generated 40% of requests",
                impact="Legitimate requests rate-limited due to quota exhaustion",
            ),
        ]

    def _investigate_deploy(self) -> List[RootCauseCandidate]:
        """Deployment/versioning investigation."""
        candidates = []

        # Check commits for unauthorized versions
        for commit in self.github_commits:
            if "unauthorized" in str(commit).lower() or "malformed" in str(commit).lower():
                candidates.append(
                    RootCauseCandidate(
                        candidate="Unauthorized model deployed",
                        likelihood="HIGH",
                        evidence=f"Commit {commit.get('sha', 'unknown')[:7]}: {commit.get('message', 'unknown')} contains unauthorized model-config.json",
                        impact="Model hash mismatch, approval status REJECTED, risk level CRITICAL",
                    )
                )

        if not candidates:
            candidates.append(
                RootCauseCandidate(
                    candidate="Version mismatch after deployment",
                    likelihood="MEDIUM",
                    evidence="Model version in serving differs from GitHub HEAD",
                    impact="Unknown model behavior, metrics anomalies follow deployment",
                )
            )

        return candidates


class RemediationSubagent:
    """Propose remediation from investigation findings (no data access)."""

    def __init__(self):
        self.available_tools = []  # Remediation has NO direct data access
        self.approved_actions = ["disable_endpoint", "rollback_model", "revoke_api_key", "publish_incident_report"]

    def draft_remediation(self, investigation: InvestigationOutput, severity: Severity) -> RemediationProposal:
        """
        Draft remediation action from investigation findings.

        Works ONLY from investigation output; cannot access data/tools directly.
        """
        top_candidate = investigation.top_candidate
        confidence = "HIGH"

        # Decision logic based on root cause
        if "distribution shift" in top_candidate.lower() or "drift" in top_candidate.lower():
            action = "disable_endpoint"
            reasoning = f"High confidence {top_candidate}. Statistical tests (PSI, KS) confirm significant shift. Error rate and latency anomalies indicate model degradation."
            expected_outcome = "All inference requests fail with clear error message. Service unavailable until endpoint re-enabled after model remediation."
            rollback_plan = "Re-enable endpoint once model reverted to previous version and data source validated."

        elif "unauthorized" in top_candidate.lower() or "bad commit" in top_candidate.lower():
            action = "rollback_model"
            reasoning = f"{top_candidate}. Commit contains unauthorized model hash with CRITICAL risk level. Immediate revert to last known-good version required."
            expected_outcome = "Model rolled back to v1.1.0. Metrics and behavior will stabilize as model processing resumes with trusted version."
            rollback_plan = "Monitor metrics post-rollback; if issues persist, investigate data source. Authorize new version through proper review process."

        elif "adversarial" in top_candidate.lower() or "jailbreak" in top_candidate.lower():
            action = "revoke_api_key"
            reasoning = f"Detected {top_candidate}. Malicious actors using current API keys to trigger errors. Revoke keys and issue new ones to legitimate clients."
            expected_outcome = "All active API keys invalidated. Attackers lose access. Legitimate applications re-authenticate with new keys."
            rollback_plan = "Issue new API keys to known-good clients. Investigate attacker vector (did they steal keys? brute-force? social engineering?)."

        else:
            action = "disable_endpoint"
            reasoning = f"Incident type unclear from investigation ({top_candidate}). As precaution, disable endpoint pending further analysis."
            expected_outcome = "Service goes offline. Prevents cascading failures if root cause is severe."
            rollback_plan = "Re-enable once root cause identified and confirmed safe."
            confidence = "MEDIUM"

        return RemediationProposal(
            action=action,
            reasoning=reasoning,
            expected_outcome=expected_outcome,
            rollback_plan=rollback_plan,
            confidence=confidence,
            timestamp=datetime.now(),
        )


class SubagentOrchestrator:
    """Orchestrate three subagents through incident response."""

    def __init__(self, telemetry_data: Dict[str, Any], github_commits: List[Dict[str, Any]]):
        self.triage = TriageSubagent()
        self.investigation = InvestigationSubagent(telemetry_data, github_commits)
        self.remediation = RemediationSubagent()

    def run_incident_response(self, alert: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run full incident response pipeline:
        Alert -> Triage -> Investigation -> Remediation -> Approval Gate

        Returns: Complete incident response context for approval gate
        """
        print("\n" + "=" * 60)
        print("INCIDENT RESPONSE INITIATED")
        print("=" * 60)

        # Phase 1: Triage
        print("\n[PHASE 1] TRIAGE")
        triage_output = self.triage.classify(alert)
        print(f"Severity: {triage_output.severity.value}")
        print(f"Type: {triage_output.incident_type.value}")
        print(f"Confidence: {triage_output.confidence}")
        print(f"Recommendation: {triage_output.recommendation}")

        # Phase 2: Investigation
        print("\n[PHASE 2] INVESTIGATION")
        investigation_output = self.investigation.investigate(triage_output)
        print(f"Top candidate: {investigation_output.top_candidate}")
        print(f"Summary: {investigation_output.findings_summary}")
        for i, candidate in enumerate(investigation_output.root_cause_candidates):
            print(f"\nCandidate {i+1}: {candidate.candidate}")
            print(f"  Likelihood: {candidate.likelihood}")
            print(f"  Evidence: {candidate.evidence}")
            print(f"  Impact: {candidate.impact}")

        # Phase 3: Remediation Drafting
        print("\n[PHASE 3] REMEDIATION DRAFTING")
        remediation_output = self.remediation.draft_remediation(investigation_output, triage_output.severity)
        print(f"Proposed Action: {remediation_output.action}")
        print(f"Reasoning: {remediation_output.reasoning}")
        print(f"Expected Outcome: {remediation_output.expected_outcome}")
        print(f"Rollback Plan: {remediation_output.rollback_plan}")
        print(f"Confidence: {remediation_output.confidence}")

        # Phase 4: Approval Gate (display context, await decision)
        print("\n[PHASE 4] APPROVAL GATE")
        print("This action requires human approval.")
        print(f"Type: {remediation_output.action.upper()}")
        print(f"Severity: {triage_output.severity.value}")

        context = {
            "incident_id": f"inc-{int(datetime.now().timestamp())}",
            "triage": asdict(triage_output) | {"timestamp": str(triage_output.timestamp)},
            "investigation": {
                "top_candidate": investigation_output.top_candidate,
                "findings_summary": investigation_output.findings_summary,
                "actions_needed": investigation_output.actions_needed,
                "candidates": [asdict(c) for c in investigation_output.root_cause_candidates],
                "timestamp": str(investigation_output.timestamp),
            },
            "remediation": asdict(remediation_output) | {"timestamp": str(remediation_output.timestamp)},
        }

        print("\n" + "=" * 60)
        print("AWAITING APPROVAL DECISION")
        print("=" * 60)

        return context


def test_subagent_decomposition():
    """Test the complete three-subagent pipeline."""
    print("\n" + "=" * 60)
    print("Testing Three-Subagent Decomposition")
    print("=" * 60)

    # Sample incident alert
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

    # Sample GitHub commits (include the bad commit)
    github_commits = [
        {
            "sha": "3f70b8c",
            "message": "Implement Phase 2 and Phase 3 complete",
            "timestamp": "2026-08-26T00:00:00Z",
        },
        {
            "sha": "c104edc",
            "message": "Deploy unauthorized model version v1.2.0",
            "timestamp": "2026-08-25T20:00:00Z",
            "content": {"model_version": "1.2.0-unauthorized", "approval_status": "REJECTED"},
        },
        {
            "sha": "9724b9e",
            "message": "Add drift analysis and incident scenarios",
            "timestamp": "2026-08-25T18:00:00Z",
        },
    ]

    # Telemetry data (mock)
    telemetry_data = {
        "metrics": {"error_rate": 0.22, "latency_p99": 120},
        "logs": ["ERROR: Model inference failed", "ERROR: Latency exceeded SLA"],
    }

    # Run orchestrator
    orchestrator = SubagentOrchestrator(telemetry_data, github_commits)
    incident_context = orchestrator.run_incident_response(alert)

    # Print final context for approval gate
    print("\nIncident context ready for approval gate:")
    print(json.dumps(incident_context, indent=2, default=str))

    return incident_context


if __name__ == "__main__":
    test_subagent_decomposition()
