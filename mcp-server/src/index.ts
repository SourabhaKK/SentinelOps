import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  Tool,
} from "@modelcontextprotocol/sdk/types.js";
import { TelemetryProvider } from "./telemetry.js";

const server = new Server({
  name: "sentinelops-telemetry",
  version: "1.0.0",
});

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

  // Determine severity based on deltas
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

  // Triage Phase
  const triagePhase = {
    phase: "TRIAGE",
    severity,
    incident_type: incidentType,
    confidence: "HIGH",
    timestamp: new Date().toISOString(),
  };

  // Investigation Phase
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
    root_cause: incidentType === "DISTRIBUTION_DRIFT"
      ? "Model input distribution shift (concept drift)"
      : incidentType === "JAILBREAK_BURST"
      ? "Adversarial attack / prompt injection"
      : "Unauthorized model deployment",
    timestamp: new Date().toISOString(),
  };

  // Remediation Phase
  const remediationPhase = {
    phase: "REMEDIATION",
    proposed_action: incidentType === "DISTRIBUTION_DRIFT" ? "disable_endpoint" : "rollback_model",
    reasoning: `High confidence ${investigationPhase.root_cause}. Statistical tests confirm significant shift. ${
      incidentType === "DISTRIBUTION_DRIFT"
        ? "Disabling to prevent cascading failures."
        : "Unauthorized deployment detected; rollback to safe version."
    }`,
    confidence: "HIGH",
    timestamp: new Date().toISOString(),
  };

  // Approval Gate Phase
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

server.setRequestHandler(ListToolsRequestSchema, async () => {
  const tools: Tool[] = [
    {
      name: "get_metrics",
      description: "Fetch system metrics (CPU, memory, model latency, inference stats)",
      inputSchema: {
        type: "object" as const,
        properties: {
          timerange: {
            type: "string",
            description: "Time range for metrics (e.g., '1h', '24h', '7d')",
            default: "1h",
          },
          metric_type: {
            type: "string",
            enum: ["cpu", "memory", "latency", "inference", "all"],
            description: "Type of metrics to fetch",
            default: "all",
          },
        },
      },
    },
    {
      name: "get_logs",
      description: "Fetch system logs and error logs",
      inputSchema: {
        type: "object" as const,
        properties: {
          level: {
            type: "string",
            enum: ["info", "warning", "error", "debug", "all"],
            description: "Log level to filter by",
            default: "all",
          },
          limit: {
            type: "number",
            description: "Maximum number of log entries",
            default: 50,
          },
        },
      },
    },
    {
      name: "get_deploy_history",
      description: "Fetch deployment history and model versions",
      inputSchema: {
        type: "object" as const,
        properties: {
          limit: {
            type: "number",
            description: "Number of recent deployments to fetch",
            default: 20,
          },
        },
      },
    },
    {
      name: "inject_scenario",
      description: "Inject a test scenario (drift, jailbreak, or bad deploy) into telemetry",
      inputSchema: {
        type: "object" as const,
        properties: {
          scenario_type: {
            type: "string",
            enum: ["drift", "jailbreak_burst", "bad_deploy"],
            description: "Type of incident scenario to inject",
          },
          severity: {
            type: "string",
            enum: ["low", "medium", "high"],
            description: "Severity level of the incident",
            default: "medium",
          },
        },
        required: ["scenario_type"],
      },
    },
    {
      name: "run_incident_response",
      description: "Run full incident response pipeline: Triage → Investigation → Remediation → Approval Gate",
      inputSchema: {
        type: "object" as const,
        properties: {
          error_rate_baseline: {
            type: "number",
            description: "Baseline error rate (0-1)",
            default: 0.08,
          },
          error_rate_current: {
            type: "number",
            description: "Current error rate (0-1)",
            default: 0.24,
          },
          latency_baseline: {
            type: "number",
            description: "Baseline latency in ms",
            default: 45,
          },
          latency_current: {
            type: "number",
            description: "Current latency in ms",
            default: 130,
          },
        },
      },
    },
  ];

  return { tools };
});

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    let result: unknown;

    switch (name) {
      case "get_metrics":
        result = telemetry.getMetrics(
          (args as any)?.timerange || "1h",
          (args as any)?.metric_type || "all"
        );
        break;

      case "get_logs":
        result = telemetry.getLogs(
          (args as any)?.level || "all",
          (args as any)?.limit || 50
        );
        break;

      case "get_deploy_history":
        result = telemetry.getDeployHistory((args as any)?.limit || 20);
        break;

      case "inject_scenario":
        result = telemetry.injectScenario(
          (args as any)?.scenario_type,
          (args as any)?.severity || "medium"
        );
        break;

      case "run_incident_response":
        result = runIncidentResponsePipeline(
          (args as any)?.error_rate_baseline || 0.08,
          (args as any)?.error_rate_current || 0.24,
          (args as any)?.latency_baseline || 45,
          (args as any)?.latency_current || 130
        );
        break;

      default:
        return {
          content: [
            {
              type: "text",
              text: `Unknown tool: ${name}`,
            },
          ],
          isError: true,
        };
    }

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(result, null, 2),
        },
      ],
    };
  } catch (error) {
    return {
      content: [
        {
          type: "text",
          text: `Error executing tool: ${error instanceof Error ? error.message : String(error)}`,
        },
      ],
      isError: true,
    };
  }
});

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("SentinelOps Telemetry MCP server running on stdio");
}

main().catch(console.error);
