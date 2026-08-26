"""
Incident Simulator — Generates realistic incident scenarios for all three types

Scenarios:
1. Distribution Drift — Gradual latency/error shift over time
2. Jailbreak Burst — Sudden spike of malicious inputs
3. Bad Deploy — Hero incident: unauthorized model in production
"""

from typing import Dict, List, Any, Optional
from enum import Enum
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import json
import random


class IncidentSeverity(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class MetricsPoint:
    timestamp: str
    error_rate: float
    latency_p99: float
    throughput: float
    cpu_usage: float
    memory_usage: float


@dataclass
class IncidentScenario:
    incident_id: str
    incident_type: str
    severity: IncidentSeverity
    start_time: str
    duration_seconds: int
    description: str
    root_cause: str
    metrics: List[MetricsPoint]
    logs: List[str]
    github_commits: List[Dict[str, Any]]


class IncidentSimulator:
    """Generate realistic incident scenarios."""

    def __init__(self):
        self.baseline_error_rate = 0.08
        self.baseline_latency_p99 = 45.0
        self.baseline_throughput = 1000.0
        self.baseline_cpu = 35.0
        self.baseline_memory = 42.0

    def simulate_drift_incident(self, severity: IncidentSeverity = IncidentSeverity.CRITICAL) -> IncidentScenario:
        """
        Drift Incident: Gradual input distribution shift

        Characteristics:
        - Error rate increases gradually over time
        - Latency distribution shifts right
        - Throughput stays relatively stable
        - No sudden spikes
        """
        start_time = datetime.now() - timedelta(hours=1)
        duration_seconds = 3600

        # Drift progression
        if severity == IncidentSeverity.LOW:
            error_delta = 0.02  # 8% -> 10%
            latency_delta = 10.0  # 45ms -> 55ms
        elif severity == IncidentSeverity.MEDIUM:
            error_delta = 0.08  # 8% -> 16%
            latency_delta = 30.0  # 45ms -> 75ms
        else:  # CRITICAL
            error_delta = 0.14  # 8% -> 22%
            latency_delta = 75.0  # 45ms -> 120ms

        metrics = []
        for i in range(0, duration_seconds, 60):  # One data point per minute
            progress = i / duration_seconds
            error_rate = self.baseline_error_rate + (error_delta * progress)
            latency = self.baseline_latency_p99 + (latency_delta * progress)
            throughput = self.baseline_throughput * (0.95 + random.uniform(0, 0.05))

            metrics.append(MetricsPoint(
                timestamp=(start_time + timedelta(seconds=i)).isoformat(),
                error_rate=error_rate,
                latency_p99=latency,
                throughput=throughput,
                cpu_usage=self.baseline_cpu + random.uniform(-5, 5),
                memory_usage=self.baseline_memory + random.uniform(-3, 3),
            ))

        logs = [
            "WARNING: Model inference latency increasing",
            "WARNING: Error rate above baseline",
            "ERROR: Request timeout (latency > 100ms)",
            "ERROR: Request timeout (latency > 100ms)",
            "ERROR: Request timeout (latency > 100ms)",
            "WARNING: Service degradation detected",
        ]

        github_commits = [
            {
                "sha": "9724b9e",
                "message": "Add drift analysis and incident scenarios",
                "timestamp": (start_time - timedelta(hours=4)).isoformat(),
            },
        ]

        return IncidentScenario(
            incident_id=f"drift-{int(datetime.now().timestamp())}",
            incident_type="DISTRIBUTION_DRIFT",
            severity=severity,
            start_time=start_time.isoformat(),
            duration_seconds=duration_seconds,
            description="Model input distribution shifted over 1 hour. Latency and error rate increased gradually.",
            root_cause="Data source changed; model encountering out-of-distribution inputs",
            metrics=metrics,
            logs=logs,
            github_commits=github_commits,
        )

    def simulate_jailbreak_incident(self, severity: IncidentSeverity = IncidentSeverity.HIGH) -> IncidentScenario:
        """
        Jailbreak Incident: Adversarial input surge

        Characteristics:
        - Sudden spike in error rate
        - Malformed inputs in logs
        - Specific client IPs attacking
        - Quick onset, visible anomalies
        """
        start_time = datetime.now() - timedelta(minutes=15)
        duration_seconds = 900  # 15 minutes

        # Jailbreak parameters
        if severity == IncidentSeverity.LOW:
            error_spike = 0.12  # 8% -> 20%
        elif severity == IncidentSeverity.MEDIUM:
            error_spike = 0.15  # 8% -> 23%
        else:  # HIGH/CRITICAL
            error_spike = 0.20  # 8% -> 28%

        metrics = []
        for i in range(0, duration_seconds, 30):  # One data point per 30 seconds
            progress = i / duration_seconds

            # Spike starts at 3 minutes, peaks at 8 minutes
            if 180 <= i <= 480:
                spike_progress = (i - 180) / 300  # 0 to 1 over 5 minute window
                spike_intensity = min(1.0, spike_progress if spike_progress < 0.5 else 1 - spike_progress)
                error_rate = self.baseline_error_rate + (error_spike * spike_intensity)
            else:
                error_rate = self.baseline_error_rate

            metrics.append(MetricsPoint(
                timestamp=(start_time + timedelta(seconds=i)).isoformat(),
                error_rate=error_rate,
                latency_p99=self.baseline_latency_p99 + random.uniform(5, 20),
                throughput=self.baseline_throughput * (0.9 + random.uniform(0, 0.1)),
                cpu_usage=self.baseline_cpu + random.uniform(-2, 15),
                memory_usage=self.baseline_memory + random.uniform(-2, 5),
            ))

        logs = [
            "ERROR: Invalid input format from 192.168.1.100",
            "ERROR: Invalid input format from 192.168.1.101",
            "ERROR: Invalid input format from 192.168.1.102",
            "ERROR: Malformed JSON payload",
            "ERROR: Malformed JSON payload",
            "WARNING: High error rate spike detected",
            "WARNING: Suspected adversarial attack",
            "INFO: Rate limiting enabled for suspicious IPs",
        ]

        github_commits = [
            {
                "sha": "3f70b8c",
                "message": "Phase 3 approval gates",
                "timestamp": (start_time - timedelta(days=1)).isoformat(),
            },
        ]

        return IncidentScenario(
            incident_id=f"jailbreak-{int(datetime.now().timestamp())}",
            incident_type="JAILBREAK_BURST",
            severity=severity,
            start_time=start_time.isoformat(),
            duration_seconds=duration_seconds,
            description="Adversarial input surge from 3 IP addresses. Spike lasted 5 minutes.",
            root_cause="Active adversarial attack; attackers sending malformed prompts to trigger errors",
            metrics=metrics,
            logs=logs,
            github_commits=github_commits,
        )

    def simulate_bad_deploy_incident(self, severity: IncidentSeverity = IncidentSeverity.CRITICAL) -> IncidentScenario:
        """
        Bad Deploy Incident: Unauthorized model in production (HERO)

        Characteristics:
        - Metrics spike coincides with recent deployment
        - GitHub shows unauthorized model commit
        - Model approval status is REJECTED
        - Clear root cause in version control
        """
        start_time = datetime.now() - timedelta(minutes=30)
        duration_seconds = 1800  # 30 minutes

        metrics = []
        for i in range(0, duration_seconds, 60):
            progress = i / duration_seconds

            # Spike starts at deployment (5 minutes in), continues
            if i >= 300:
                error_rate = self.baseline_error_rate + 0.16  # 8% -> 24%
                latency = self.baseline_latency_p99 + 85.0  # 45ms -> 130ms
            else:
                error_rate = self.baseline_error_rate
                latency = self.baseline_latency_p99

            metrics.append(MetricsPoint(
                timestamp=(start_time + timedelta(seconds=i)).isoformat(),
                error_rate=error_rate,
                latency_p99=latency,
                throughput=self.baseline_throughput * (0.85 + random.uniform(0, 0.1)),
                cpu_usage=self.baseline_cpu + random.uniform(5, 25),
                memory_usage=self.baseline_memory + random.uniform(5, 15),
            ))

        logs = [
            "INFO: New model version deployed: v1.2.0-unauthorized",
            "WARNING: Model hash mismatch detected",
            "ERROR: Model inference failed",
            "ERROR: Model inference failed",
            "ERROR: Model approval status: REJECTED",
            "CRITICAL: Risk level: CRITICAL",
            "WARNING: Metrics anomaly detected post-deployment",
        ]

        github_commits = [
            {
                "sha": "c104edc",
                "message": "Deploy unauthorized model version v1.2.0",
                "timestamp": (start_time + timedelta(seconds=300)).isoformat(),
                "content": {
                    "model_version": "1.2.0-unauthorized",
                    "model_hash": "malformed_hash_xyz789",
                    "approval_status": "REJECTED",
                    "risk_level": "CRITICAL",
                },
            },
            {
                "sha": "9724b9e",
                "message": "Add drift analysis and incident scenarios",
                "timestamp": (start_time - timedelta(hours=4)).isoformat(),
            },
        ]

        return IncidentScenario(
            incident_id=f"bad-deploy-{int(datetime.now().timestamp())}",
            incident_type="BAD_DEPLOY",
            severity=severity,
            start_time=start_time.isoformat(),
            duration_seconds=duration_seconds,
            description="Unauthorized model v1.2.0 deployed 30 minutes ago. Metrics spiked immediately post-deployment.",
            root_cause="Commit c104edc contains model with REJECTED approval status and CRITICAL risk level",
            metrics=metrics,
            logs=logs,
            github_commits=github_commits,
        )

    def get_all_scenarios(self) -> Dict[str, IncidentScenario]:
        """Generate all three incident types."""
        return {
            "drift_low": self.simulate_drift_incident(IncidentSeverity.LOW),
            "drift_critical": self.simulate_drift_incident(IncidentSeverity.CRITICAL),
            "jailbreak_high": self.simulate_jailbreak_incident(IncidentSeverity.HIGH),
            "bad_deploy_critical": self.simulate_bad_deploy_incident(IncidentSeverity.CRITICAL),
        }


def test_incident_simulator():
    """Test incident simulation for all types."""
    print("\n" + "="*70)
    print("INCIDENT SIMULATOR TEST")
    print("="*70)

    simulator = IncidentSimulator()
    scenarios = simulator.get_all_scenarios()

    for scenario_name, scenario in scenarios.items():
        print(f"\n{'-'*70}")
        print(f"Scenario: {scenario_name}")
        print(f"Type: {scenario.incident_type}")
        print(f"Severity: {scenario.severity.value}")
        print(f"Description: {scenario.description}")
        print(f"Root Cause: {scenario.root_cause}")
        print(f"Duration: {scenario.duration_seconds}s")
        print(f"Metrics points: {len(scenario.metrics)}")
        print(f"Log entries: {len(scenario.logs)}")
        print(f"GitHub commits: {len(scenario.github_commits)}")

        # Show first and last metric
        if scenario.metrics:
            first = scenario.metrics[0]
            last = scenario.metrics[-1]
            print(f"\nMetrics progression:")
            print(f"  Start: error_rate={first.error_rate:.2%}, latency={first.latency_p99:.1f}ms")
            print(f"  End:   error_rate={last.error_rate:.2%}, latency={last.latency_p99:.1f}ms")
            print(f"  Delta: error_rate={last.error_rate - first.error_rate:.2%}, latency={last.latency_p99 - first.latency_p99:.1f}ms")

    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70)


if __name__ == "__main__":
    test_incident_simulator()
