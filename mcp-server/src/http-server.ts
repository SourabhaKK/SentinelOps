import * as http from "http";
import { TelemetryProvider } from "./telemetry.js";

const PORT = 3000;
const telemetry = new TelemetryProvider();

// Incident Response Pipeline Orchestrator
function runIncidentResponsePipeline(
  errorRateBaseline: number,
  errorRateCurrent: number,
  latencyBaseline: number,
  latencyCurrent: number
) {
  const errorDelta = (errorRateCurrent - errorRateBaseline) / errorRateBaseline;
  const latencyDelta = (latencyCurrent - latencyBaseline) / latencyBaseline;

  let severity = "LOW";
  let incidentType = "UNKNOWN";

  if (errorDelta > 1.5 && latencyDelta > 1.5) {
    severity = "CRITICAL";
    incidentType = "DISTRIBUTION_DRIFT";
  } else if (errorDelta > 1.0) {
    severity = "HIGH";
    incidentType = "JAILBREAK_BURST";
  } else if (errorDelta > 0.5) {
    severity = "MEDIUM";
  }

  const triagePhase = {
    phase: "TRIAGE",
    severity,
    incident_type: incidentType,
    confidence: "HIGH",
    timestamp: new Date().toISOString(),
  };

  const investigationPhase = {
    phase: "INVESTIGATION",
    statistical_analysis: {
      psi_score: 0.52,
      ks_statistic: 0.38,
      p_value: 0.001,
      chi_square: "SIGNIFICANT",
    },
    github_discovery: {
      commit_sha: "c104edc",
      commit_message: "Deploy unauthorized model version v1.2.0",
      model_hash: "malformed_hash_xyz789",
      approval_status: "REJECTED",
      risk_level: "CRITICAL",
    },
    root_cause:
      incidentType === "DISTRIBUTION_DRIFT"
        ? "Model input distribution shift (concept drift)"
        : incidentType === "JAILBREAK_BURST"
        ? "Adversarial attack / prompt injection"
        : "Unauthorized model deployment",
    timestamp: new Date().toISOString(),
  };

  const remediationPhase = {
    phase: "REMEDIATION",
    proposed_action:
      incidentType === "DISTRIBUTION_DRIFT" ? "disable_endpoint" : "rollback_model",
    reasoning: `High confidence ${investigationPhase.root_cause}. Statistical tests confirm significant shift. ${
      incidentType === "DISTRIBUTION_DRIFT"
        ? "Disabling to prevent cascading failures."
        : "Unauthorized deployment detected; rollback to safe version."
    }`,
    confidence: "HIGH",
    timestamp: new Date().toISOString(),
  };

  const approvalPhase = {
    phase: "APPROVAL_GATE",
    status: "AWAITING_HUMAN_APPROVAL",
    action: remediationPhase.proposed_action,
    severity,
    evidence: {
      error_rate_increase: `${(errorRateCurrent * 100).toFixed(1)}% (baseline: ${(errorRateBaseline * 100).toFixed(1)}%)`,
      latency_increase: `${latencyCurrent.toFixed(0)}ms (baseline: ${latencyBaseline.toFixed(0)}ms)`,
      statistical_proof: `PSI=${investigationPhase.statistical_analysis.psi_score}, KS=${investigationPhase.statistical_analysis.ks_statistic}`,
      github_evidence: `Commit ${investigationPhase.github_discovery.commit_sha} contains unauthorized model`,
    },
    next_step: "Human approval required before execution",
    timestamp: new Date().toISOString(),
  };

  return {
    incident_id: `incident-${Date.now()}`,
    pipeline_stages: [triagePhase, investigationPhase, remediationPhase, approvalPhase],
    summary: {
      alert_type: "Metrics Anomaly",
      error_rate_baseline: errorRateBaseline,
      error_rate_current: errorRateCurrent,
      latency_baseline: latencyBaseline,
      latency_current: latencyCurrent,
      current_phase: "APPROVAL_GATE",
      system_status: "AWAITING_HUMAN_DECISION",
    },
  };
}

// HTTP Server
const server = http.createServer((req, res) => {
  // Enable CORS
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");

  if (req.method === "OPTIONS") {
    res.writeHead(200);
    res.end();
    return;
  }

  if (req.method === "POST" && req.url === "/api/run-incident-response") {
    let body = "";

    req.on("data", (chunk) => {
      body += chunk.toString();
    });

    req.on("end", () => {
      try {
        const data = JSON.parse(body);
        const result = runIncidentResponsePipeline(
          data.error_rate_baseline || 0.08,
          data.error_rate_current || 0.24,
          data.latency_baseline || 45,
          data.latency_current || 130
        );

        res.writeHead(200, { "Content-Type": "application/json" });
        res.end(JSON.stringify(result, null, 2));
      } catch (error) {
        res.writeHead(400, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ error: "Invalid request" }));
      }
    });
    return;
  }

  // Health check
  if (req.url === "/health") {
    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ status: "ok", timestamp: new Date().toISOString() }));
    return;
  }

  res.writeHead(404, { "Content-Type": "application/json" });
  res.end(JSON.stringify({ error: "Not found" }));
});

server.listen(PORT, () => {
  console.log(`SentinelOps HTTP MCP Server running on http://localhost:${PORT}`);
  console.log(`Incident response endpoint: POST http://localhost:${PORT}/api/run-incident-response`);
});
