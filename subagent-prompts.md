# Subagent Prompts and Scoping

## Architecture

Three subagents with strictly scoped tool access, coordinated by the orchestrator:

```
Raw Incident Alert
        ↓
    TRIAGE (no data-source access)
        ↓ Severity classification, type
    INVESTIGATION (full data access)
        ↓ Root cause analysis
    REMEDIATION DRAFTING (findings-only access)
        ↓ Proposed action
    APPROVAL GATE (human)
        ↓ Decision
    EXECUTION (if approved)
```

---

## 1. Triage Subagent

**Role:** Classify incident severity and type from raw telemetry

**Available Tools:** None (telemetry data passed as context only)

**Input:** Raw incident signal
```json
{
  "alert_type": "metrics_anomaly",
  "metrics": {
    "error_rate": {"baseline": 0.08, "current": 0.22},
    "latency_p99": {"baseline": 45, "current": 120},
    "throughput": {"baseline": 1000, "current": 950}
  },
  "timestamp": "2026-08-26T14:30:00Z",
  "duration_seconds": 300
}
```

**Prompt Template:**
```
You are the Triage subagent for SentinelOps. You receive raw incident alerts with minimal context.

Your job: Classify the incident quickly.

Answer these questions:
1. Severity: CRITICAL | HIGH | MEDIUM | LOW
2. Incident type: DISTRIBUTION_DRIFT | JAILBREAK_BURST | BAD_DEPLOY | UNKNOWN
3. Recommendation: Which investigation path (Investigation subagent)?
   - For DRIFT: "Fetch metrics time-series and latency distribution"
   - For JAILBREAK: "Analyze error logs for patterns"
   - For BAD_DEPLOY: "Query deploy history and compare model versions"
4. Confidence: HIGH | MEDIUM | LOW (based on signal strength)

Be concise. Do not make decisions; only triage.
```

**Output:**
```json
{
  "severity": "CRITICAL",
  "type": "DISTRIBUTION_DRIFT",
  "recommendation": "Fetch metrics time-series; compare baseline to current distribution",
  "confidence": "HIGH"
}
```

---

## 2. Investigation Subagent

**Role:** Deep-dive analysis with access to all data sources

**Available Tools:**
- `get_metrics` — Fetch time-series metrics
- `get_logs` — System logs with filtering
- `get_deploy_history` — Deployment records with model versions
- GitHub MCP connector — Read commits, PRs, file history

**Input:** Triage output + access to above tools

**Prompt Template:**
```
You are the Investigation subagent for SentinelOps. You have full access to metrics, logs, deploy history, and GitHub.

Triage classified this incident as: {{TYPE}} ({{SEVERITY}})

Your job: Investigate root cause.

Steps:
1. Fetch relevant data using available tools (call them as needed)
2. Correlate signals across sources
3. Identify root cause candidates
4. For each candidate, estimate likelihood and impact

Guidelines:
- Use get_metrics to fetch time-series for {{TYPE}}-relevant metrics
- Use get_logs to find error patterns or anomalies
- Use get_deploy_history to check recent deployments
- Use GitHub MCP to find commits related to metrics changes
- Be thorough but time-conscious (this is live incident response)

Return your findings as:
{
  "root_cause_candidates": [
    {
      "candidate": "...",
      "likelihood": "HIGH|MEDIUM|LOW",
      "evidence": "...",
      "impact": "..."
    }
  ],
  "top_candidate": "...",
  "actions_needed": ["..."]
}
```

**Output:**
```json
{
  "root_cause_candidates": [
    {
      "candidate": "Model distribution shift (input data changed)",
      "likelihood": "HIGH",
      "evidence": "PSI=0.52 (>0.25 threshold), KS p-value=0.001, latency histogram shifted right",
      "impact": "Inference latency increased 2.7x, error rate 8% -> 22%"
    },
    {
      "candidate": "Unauthorized model deployed",
      "likelihood": "MEDIUM",
      "evidence": "Commit c104edc contains model-config.json with CRITICAL risk level",
      "impact": "Model version mismatch could explain metrics anomalies"
    }
  ],
  "top_candidate": "Model distribution shift (confirmed by statistical tests)",
  "actions_needed": [
    "Disable inference endpoint pending investigation",
    "Revert to previous model version",
    "Investigate data source changes"
  ]
}
```

---

## 3. Remediation Drafting Subagent

**Role:** Propose remediation actions based on investigation findings

**Available Tools:** None (works from Investigation output only)

**Input:** Investigation output + Approval Gate config

**Prompt Template:**
```
You are the Remediation Drafting subagent for SentinelOps. You do NOT have direct access to tools or data; you work only from the Investigation subagent's findings.

Investigation found: {{ROOT_CAUSE}}

Your job: Draft a remediation action.

Constraints:
- Must match one of the pre-approved actions: disable_endpoint, rollback_model, revoke_api_key, publish_incident_report
- If none fit, propose a new action with clear justification
- Consider consequence and risk
- Be specific about what, when, how

Return:
{
  "action": "...",
  "reasoning": "...",
  "expected_outcome": "...",
  "rollback_plan": "...",
  "confidence": "HIGH|MEDIUM|LOW"
}
```

**Output:**
```json
{
  "action": "disable_endpoint",
  "reasoning": "High confidence drift detected (PSI=0.52, KS p-value=0.001). Error rate 8% -> 22%. Endpoint offline will prevent cascading failures downstream.",
  "expected_outcome": "All inference requests fail with clear error message. Service unavailable until endpoint re-enabled after root cause remediation.",
  "rollback_plan": "Re-enable endpoint once model reverted to v1.1.0",
  "confidence": "HIGH"
}
```

---

## Tool Scoping (Enforced at TrueForge Layer)

| Tool | Triage | Investigation | Remediation | Notes |
|------|--------|----------------|-------------|-------|
| get_metrics | ❌ | ✅ | ❌ | Only Investigation has data access |
| get_logs | ❌ | ✅ | ❌ | Only Investigation has data access |
| get_deploy_history | ❌ | ✅ | ❌ | Only Investigation discovers bad commits |
| GitHub MCP | ❌ | ✅ | ❌ | Only Investigation digs into history |
| Daytona/drift_analysis | ❌ | ✅ | ❌ | Statistical tests run in Investigation |
| Approval gates | ✅ | ✅ | ✅ | All propose actions, orchestrator gates approval |

---

## End-to-End Flow (Exemplar)

**Incident Alert:**
```
Error rate spike: 8% -> 22%
Latency p99: 45ms -> 120ms
Duration: 5 minutes ongoing
```

**Triage Output:**
```
Severity: CRITICAL
Type: DISTRIBUTION_DRIFT
Confidence: HIGH
```

**Investigation (full workflow):**
1. Calls get_metrics → fetches latency/error/throughput time-series
2. Runs drift_analysis in Daytona → PSI=0.52 (SIGNIFICANT)
3. Calls get_deploy_history → finds commit c104edc (model-config.json)
4. Calls GitHub MCP → reads commit, finds unauthorized hash
5. Returns: Root cause = unauthorized model, confidence HIGH

**Remediation Drafting:**
```
Proposed action: disable_endpoint
Reasoning: High confidence unauthorized model, metrics confirm drift
Expected outcome: Service offline, no more bad predictions
Rollback: Revert to v1.1.0 after endpoint disabled
```

**Approval Gate:**
- Orchestrator presents full context to human
- Human approves: disable_endpoint executes
- Audit logged with timestamp + approver + reason

**Execution:**
- Endpoint marked OFFLINE
- Subsequent inference requests fail with clear message
- Investigation continues to identify data source

---

## Testing Strategy

**Unit test per subagent:**
- Triage: Feed various alert shapes, verify classification accuracy
- Investigation: Mock tool responses, verify correlation logic
- Remediation: Feed investigation outputs, verify action selection

**Integration test (end-to-end):**
- Inject one incident (drift/jailbreak/bad-deploy)
- Run all three subagents in sequence
- Verify action reaches approval gate

**Gate test:**
- Verify human approval triggers action execution
- Verify human rejection blocks execution
