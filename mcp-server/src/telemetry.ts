export interface MetricDataPoint {
  timestamp: string;
  value: number;
}

export interface SystemMetrics {
  cpu: MetricDataPoint[];
  memory: MetricDataPoint[];
  model_latency_ms: MetricDataPoint[];
  inference_throughput: MetricDataPoint[];
  error_rate: MetricDataPoint[];
}

export interface LogEntry {
  timestamp: string;
  level: string;
  service: string;
  message: string;
  error?: string;
}

export interface DeploymentRecord {
  deployment_id: string;
  timestamp: string;
  model_version: string;
  model_hash: string;
  commit_sha: string;
  status: "success" | "failed" | "rolled_back";
  endpoint: string;
}

export class TelemetryProvider {
  private metrics: SystemMetrics;
  private logs: LogEntry[];
  private deployments: DeploymentRecord[];

  constructor() {
    this.metrics = this.generateSeedMetrics();
    this.logs = this.generateSeedLogs();
    this.deployments = this.generateSeedDeployments();
  }

  private generateSeedMetrics(): SystemMetrics {
    const now = new Date();
    const points: MetricDataPoint[] = [];

    for (let i = 0; i < 60; i++) {
      const time = new Date(now.getTime() - (59 - i) * 60000);
      points.push({
        timestamp: time.toISOString(),
        value: Math.random() * 100,
      });
    }

    return {
      cpu: points.map((p) => ({ ...p, value: Math.random() * 80 + 10 })),
      memory: points.map((p) => ({ ...p, value: Math.random() * 70 + 20 })),
      model_latency_ms: points.map((p) => ({
        ...p,
        value: Math.random() * 200 + 50,
      })),
      inference_throughput: points.map((p) => ({
        ...p,
        value: Math.random() * 1000 + 500,
      })),
      error_rate: points.map((p) => ({ ...p, value: Math.random() * 0.05 })),
    };
  }

  private generateSeedLogs(): LogEntry[] {
    return [
      {
        timestamp: new Date(Date.now() - 300000).toISOString(),
        level: "info",
        service: "model-inference",
        message: "Model inference request processed successfully",
      },
      {
        timestamp: new Date(Date.now() - 240000).toISOString(),
        level: "info",
        service: "api-gateway",
        message: "Request routed to inference endpoint",
      },
      {
        timestamp: new Date(Date.now() - 180000).toISOString(),
        level: "warning",
        service: "model-inference",
        message: "Inference latency elevated: 187ms (threshold: 150ms)",
      },
      {
        timestamp: new Date(Date.now() - 120000).toISOString(),
        level: "info",
        service: "metrics-collector",
        message: "Metrics collected and stored",
      },
      {
        timestamp: new Date(Date.now() - 60000).toISOString(),
        level: "info",
        service: "monitoring",
        message: "Health check passed",
      },
    ];
  }

  private generateSeedDeployments(): DeploymentRecord[] {
    return [
      {
        deployment_id: "deploy-001",
        timestamp: new Date(Date.now() - 7 * 24 * 3600000).toISOString(),
        model_version: "v1.0.0",
        model_hash: "abc123def456",
        commit_sha: "f1a2b3c4d5e6f7a8b9c0",
        status: "success",
        endpoint: "https://api.sentinelops.local/predict",
      },
      {
        deployment_id: "deploy-002",
        timestamp: new Date(Date.now() - 3 * 24 * 3600000).toISOString(),
        model_version: "v1.1.0",
        model_hash: "def456ghi789",
        commit_sha: "a1b2c3d4e5f6g7h8i9j0",
        status: "success",
        endpoint: "https://api.sentinelops.local/predict",
      },
      {
        deployment_id: "deploy-003",
        timestamp: new Date(Date.now() - 6 * 3600000).toISOString(),
        model_version: "v1.2.0-beta",
        model_hash: "ghi789jkl012",
        commit_sha: "b2c3d4e5f6g7h8i9j0k1",
        status: "success",
        endpoint: "https://api.sentinelops.local/predict",
      },
    ];
  }

  getMetrics(timerange: string, metricType: string): SystemMetrics {
    if (metricType === "all") {
      return this.metrics;
    }

    const result: any = {};
    if (metricType === "cpu") result.cpu = this.metrics.cpu;
    if (metricType === "memory") result.memory = this.metrics.memory;
    if (metricType === "latency") result.model_latency_ms = this.metrics.model_latency_ms;
    if (metricType === "inference")
      result.inference_throughput = this.metrics.inference_throughput;

    return result;
  }

  getLogs(level: string, limit: number): LogEntry[] {
    let filtered = this.logs;

    if (level !== "all") {
      filtered = filtered.filter((log) => log.level === level);
    }

    return filtered.slice(-limit);
  }

  getDeployHistory(limit: number): DeploymentRecord[] {
    return this.deployments.slice(-limit);
  }

  injectScenario(
    scenarioType: string,
    severity: string
  ): { status: string; scenario: string; message: string } {
    switch (scenarioType) {
      case "drift":
        this.simulateDrift(severity);
        return {
          status: "injected",
          scenario: "distribution_drift",
          message: `Distribution drift scenario injected with ${severity} severity`,
        };

      case "jailbreak_burst":
        this.simulateJailbreakBurst(severity);
        return {
          status: "injected",
          scenario: "adversarial_burst",
          message: `Jailbreak/adversarial burst scenario injected with ${severity} severity`,
        };

      case "bad_deploy":
        this.simulateBadDeploy(severity);
        return {
          status: "injected",
          scenario: "unauthorized_model_version",
          message: `Bad deploy scenario injected with ${severity} severity`,
        };

      default:
        return {
          status: "error",
          scenario: "unknown",
          message: `Unknown scenario type: ${scenarioType}`,
        };
    }
  }

  private simulateDrift(severity: string): void {
    const factor = severity === "high" ? 0.7 : severity === "medium" ? 0.5 : 0.3;
    this.metrics.error_rate = this.metrics.error_rate.map((point) => ({
      ...point,
      value: Math.min(1, point.value * (1 + factor)),
    }));
  }

  private simulateJailbreakBurst(severity: string): void {
    const now = new Date();
    const maliciousLogs = Array.from({ length: 5 }, (_, i) => ({
      timestamp: new Date(now.getTime() - i * 30000).toISOString(),
      level: "warning",
      service: "security",
      message: "Potential adversarial/jailbreak-shaped input detected",
      error: `Suspicious pattern in input: ${["prompt injection", "role override", "context escape"][i % 3]}`,
    }));

    this.logs.push(...maliciousLogs);
  }

  private simulateBadDeploy(severity: string): void {
    const now = new Date();
    this.deployments.push({
      deployment_id: "deploy-bad-001",
      timestamp: now.toISOString(),
      model_version: "v1.2.0-MALFORMED",
      model_hash: "malformed_hash_xyz",
      commit_sha: "c3d4e5f6g7h8i9j0k1l2",
      status: "success",
      endpoint: "https://api.sentinelops.local/predict",
    });

    this.logs.push({
      timestamp: now.toISOString(),
      level: "error",
      service: "deployment",
      message: "Unauthorized model version deployed",
      error: "Model hash mismatch with approved registry",
    });
  }
}
