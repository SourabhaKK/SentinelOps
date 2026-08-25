# Phase 4 Summary: Subagent Decomposition

## Overview

Phase 4 (Aug 27) splits the incident-response agent into three specialized subagents with strictly scoped tool access, working in concert to triage, investigate, and propose remediation.

---

## Architecture

### Three-Tier Decomposition

```
Raw Incident Alert (metrics spike)
        ↓
    [TRIAGE SUBAGENT] (no data access)
    - Classify severity: CRITICAL | HIGH | MEDIUM | LOW
    - Classify type: DISTRIBUTION_DRIFT | JAILBREAK_BURST | BAD_DEPLOY | UNKNOWN
    - Route to Investigation
        ↓
    [INVESTIGATION SUBAGENT] (full data access)
    - get_metrics: time-series analysis
    - get_logs: error pattern detection
    - get_deploy_history: version tracking
    - GitHub MCP: commit/PR analysis
    - Daytona: statistical drift tests
    - Return: root cause + candidates + evidence
        ↓
    [REMEDIATION SUBAGENT] (findings-only access)
    - No direct data access; works from Investigation output
    - Proposes one of: disable_endpoint, rollback_model, revoke_api_key, publish_report
    - Provides reasoning, expected outcome, rollback plan
        ↓
    [APPROVAL GATE] (human)
    - Presents context with full investigation findings
    - Decision: APPROVE | REJECT | MODIFY
    - Audit: timestamp, approver, reason
        ↓
    [EXECUTION] (if approved)
    - Action executes only after explicit approval
```

### Tool Scoping (TrueForge-Enforced)

| Tool | Triage | Investigation | Remediation |
|------|--------|----------------|-------------|
| get_metrics | ❌ | ✅ | ❌ |
| get_logs | ❌ | ✅ | ❌ |
| get_deploy_history | ❌ | ✅ | ❌ |
| GitHub MCP | ❌ | ✅ | ❌ |
| Daytona/drift_analysis | ❌ | ✅ | ❌ |
| Approval gates | ✅ | ✅ | ✅ |

**Design principle:** Investigation is the only subagent with data-source access. Triage classifies quickly; Remediation thinks strategically. No single subagent can discover data AND propose actions (separation of concerns).

---

## Files Built

### 1. Documentation
- **subagent-prompts.md** — Detailed prompts and scoping for each subagent, with exemplar flow
- **PHASE_4_SUMMARY.md** — This file

### 2. Python Implementation
- **subagents.py** — Three subagent classes + orchestrator
  - `TriageSubagent`: Classifies alerts into severity/type
  - `InvestigationSubagent`: Correlates data across sources
  - `RemediationSubagent`: Proposes actions from findings
  - `SubagentOrchestrator`: Coordinates pipeline
  
- **test_full_incident_loop.py** — Integration test
  - Full incident pipeline: Triage → Investigation → Remediation → Approval
  - Demonstrates both APPROVE and REJECT approval paths
  - Shows audit logging

---

## Test Results

### End-to-End Incident Response

**Incident:** Metrics anomaly (error rate 8% → 22%, latency 45ms → 120ms)

**Triage Output:**
```
Severity: CRITICAL
Type: DISTRIBUTION_DRIFT
Confidence: HIGH
Recommendation: Fetch metrics time-series; run statistical drift tests
```

**Investigation Output:**
```
Root cause: Model input distribution shift (concept drift)
Evidence: PSI=0.52 (>0.25), KS p-value<0.001
Candidates: Distribution shift (HIGH), Data source change (MEDIUM)
Actions needed: Disable endpoint, Investigate data source, Consider rollback
```

**Remediation Output:**
```
Proposed action: disable_endpoint
Reasoning: High confidence drift; statistical tests confirm; prevent cascading failures
Expected outcome: Service OFFLINE, no bad predictions
Rollback plan: Re-enable after model remediation
Confidence: HIGH
```

**Approval Gate:**
- Scenario A (APPROVAL): ✅ Endpoint disabled successfully
- Scenario B (REJECTION): ✅ Rollback blocked, alternative suggested

---

## Key Features

✅ **Clear Separation of Concerns**
- Triage: "What type of incident?" (no data)
- Investigation: "What caused it?" (all data)
- Remediation: "What should we do?" (findings only)

✅ **Tool Scoping Enforced**
- Only Investigation accesses data sources
- Remediation cannot access data directly; must work from findings
- Prevents accidental data leaks or inconsistent analysis

✅ **Full Audit Trail**
- Each subagent output timestamped
- Approval decision logged with approver + reason
- Complete incident context available for post-incident review

✅ **Flexible Approval Workflow**
- Accept: Action executes immediately
- Reject: Action blocked, alternative suggested
- Modify: (stub support for future enhancement)

✅ **Extensible Design**
- Easy to add new subagent types (e.g., "escalation", "communication")
- Easy to add new approval-required actions
- Easy to add new incident types (classification in Triage)

---

## Next Phase

**Phase 5 (Aug 28):** Persistence & hardening

Run all three incidents end-to-end:
1. Incident 1: Distribution drift (synthetic)
2. Incident 2: Jailbreak burst (synthetic)
3. Incident 3: Bad deploy (hero incident, real commit)

Test session reconnection:
- Investigation mid-run
- Force disconnect
- Resume and verify state intact

---

## Implementation Notes

### Subagent Prompts

Each subagent receives a detailed system prompt (in subagent-prompts.md) that:
1. Explains its role and constraints
2. Lists available tools (or explicitly states none)
3. Provides input/output format examples
4. Guides decision-making without over-constraining

### Data Flow

```python
alert = {"metrics": {...}, "timestamp": "...", "duration": 300}
triage_output = TriageSubagent().classify(alert)
investigation_output = InvestigationSubagent(telemetry, github).investigate(triage_output)
remediation_output = RemediationSubagent().draft_remediation(investigation_output, severity)
incident_context = {triage, investigation, remediation}
approval_request = ApprovalGate().request_approval(...incident_context...)
```

### Orchestrator

`SubagentOrchestrator` coordinates the pipeline:
1. Calls Triage with raw alert
2. Calls Investigation with Triage output + tool access
3. Calls Remediation with Investigation output (no tools)
4. Returns complete incident context for approval gate
5. Prints human-readable progress at each stage

---

## Testing Coverage

✅ Three subagents tested individually (unit tests via direct calls)
✅ Full pipeline tested end-to-end (integration test)
✅ Approval ACCEPT path verified (action executes)
✅ Approval REJECT path verified (action blocked)
✅ Audit logging verified (decisions recorded)
✅ Multiple incident types handled (drift, jailbreak, bad-deploy classification)

---

## Files Changed

```
subagent-prompts.md             NEW — Detailed prompts and scoping
subagents.py                    NEW — Three subagents + orchestrator
test_full_incident_loop.py      NEW — Integration test with approval gates
PHASE_4_SUMMARY.md              NEW — This file
```

## Commits

TBD (pending git push)
