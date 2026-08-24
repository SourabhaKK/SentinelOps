import {
  Server,
  StdioServerTransport,
} from "@modelcontextprotocol/sdk/server/index.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  TextContent,
} from "@modelcontextprotocol/sdk/types.js";
import { TelemetryProvider } from "./telemetry.js";

const server = new Server({
  name: "sentinelops-telemetry",
  version: "1.0.0",
});

const telemetry = new TelemetryProvider();

server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "get_metrics",
        description: "Fetch system metrics (CPU, memory, model latency, inference stats)",
        inputSchema: {
          type: "object",
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
          type: "object",
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
          type: "object",
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
          type: "object",
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
    ],
  };
});

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    let result: string;

    switch (name) {
      case "get_metrics":
        result = JSON.stringify(
          telemetry.getMetrics(
            (args as any).timerange || "1h",
            (args as any).metric_type || "all"
          ),
          null,
          2
        );
        break;

      case "get_logs":
        result = JSON.stringify(
          telemetry.getLogs((args as any).level || "all", (args as any).limit || 50),
          null,
          2
        );
        break;

      case "get_deploy_history":
        result = JSON.stringify(
          telemetry.getDeployHistory((args as any).limit || 20),
          null,
          2
        );
        break;

      case "inject_scenario":
        result = JSON.stringify(
          telemetry.injectScenario(
            (args as any).scenario_type,
            (args as any).severity || "medium"
          ),
          null,
          2
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
          type: "text" as const,
          text: result,
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
