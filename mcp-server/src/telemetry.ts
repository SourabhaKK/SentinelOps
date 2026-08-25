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
        value: i,
      });
    }

    // Normal baseline metrics
    const cpu = points.map((p, i) => ({
      timestamp: p.timestamp,
      value: 45 + Math.sin(i / 10) * 15 + Math.random() * 5,
    }));

    const memory = points.map((p, i) => ({
      timestamp: p.timestamp,
      value: 55 + Math.cos(i / 12) * 10 + Math.random() * 4,
    }));

    const latency = points.map((p, i) => ({
      timestamp: p.timestamp,
      value: 85 + Math.sin(i / 8) * 20 + Math.random() * 10,
    }));

    const throughput = points.map((p, i) => ({
      timestamp: p.timestamp,
      value: 800 + Math.cos(i / 15) * 150 + Math.random() * 50,
    }));

    // Normal error rate (low baseline)
    const errorRate = points.map((p, i) => ({
      timestamp: p.timestamp,
      value: 0.008 + Math.random() * 0.005,
    }));

    return {
      cpu,
      memory,
      model_latency_ms: latency,
      inference_throughput: throughput,
      error_rate: errorRate,
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
    // Simulate gradual distribution drift in input features
    // Shift the latency distribution (proxy for input feature distribution)
    const factor = severity === "high" ? 0.8 : severity === "medium" ? 0.5 : 0.3;

    this.metrics.model_latency_ms = this.metrics.model_latency_ms.map((point, i) => {
      // Gradual shift: later points have higher latency (distribution drift)
      const driftAmount = (i / this.metrics.model_latency_ms.length) * factor * 100;
      return {
        ...point,
        value: Math.max(50, point.value + driftAmount + (Math.random() - 0.5) * 10),
      };
    });

    // Error rate increases with drift
    this.metrics.error_rate = this.metrics.error_rate.map((point, i) => {
      const baseIncrease = factor * 0.08;
      return {
        ...point,
        value: Math.min(0.3, point.value + baseIncrease * (i / this.metrics.error_rate.length)),
      };
    });
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

    // Add bad deployment record
    this.deployments.push({
      deployment_id: "deploy-bad-001",
      timestamp: now.toISOString(),
      model_version: "v1.2.0-MALFORMED",
      model_hash: "malformed_hash_xyz",
      commit_sha: "c3d4e5f6g7h8i9j0k1l2",
      status: "success",
      endpoint: "https://api.sentinelops.local/predict",
    });

    // Log deployment error
    this.logs.push({
      timestamp: now.toISOString(),
      level: "error",
      service: "deployment",
      message: "Unauthorized model version deployed",
      error: "Model hash mismatch with approved registry",
    });

    // Increase error rate dramatically after bad deploy
    const errorFactor = severity === "high" ? 0.25 : severity === "medium" ? 0.15 : 0.08;
    this.metrics.error_rate = this.metrics.error_rate.map((point, i) => ({
      ...point,
      value: Math.min(0.4, point.value + errorFactor),
    }));

    // Latency spikes
    this.metrics.model_latency_ms = this.metrics.model_latency_ms.map((point) => ({
      ...point,
      value: point.value * 1.5 + Math.random() * 50,
    }));
  }
}
