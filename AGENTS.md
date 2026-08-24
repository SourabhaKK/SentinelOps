# AGENTS.md — Subagent Decomposition

SentinelOps uses three specialized subagents with scoped tool access. This is real scoping enforced at TrueForge's permission layer, not simulated by prompt instruction alone.

## Triage Agent

**Role**: Initial incident classification and severity assessment.

**Input**: Raw incident alert + initial telemetry snapshot.

**Process**:
1. Classify incident type (drift, jailbreak, bad deploy, unknown).
2. Assign severity (low, medium, high, critical).
3. Extract key signals from telemetry (error spike, latency jump, log patterns).

**Output**: Structured triage report (type, severity, signals, recommended investigation depth).

**Tool Access**:
- `/metrics` (read-only, recent window)
- `/logs` (read-only, recent window)
- NO access to: `/deploy-history`, GitHub

**Rationale**: Triage should classify from observable system behavior alone, without privileged context. This prevents over-scoped early decisions and matches real on-call workflows where an alert hits before anyone knows the root cause.

---

## Investigation Agent

**Role**: Root-cause analysis using all available evidence.

**Input**: Triage report + subagent-delegated task.

**Process**:
1. Correlate metrics, logs, and deploy history to pinpoint timing and scope.
2. Query GitHub to inspect commits, PRs, and code changes around deployment time.
3. Cross-reference against drift-computation sandbox results when applicable.
4. Build a detailed incident timeline.

**Output**: Investigation findings (root cause hypothesis, evidence chain, confidence level, supporting artifacts like commit links).

**Tool Access**:
- `/metrics` (full read)
- `/logs` (full read)
- `/deploy-history` (full read)
- GitHub MCP (commits, PRs, diffs on this repo, read-only)
- Sandbox results (read-only, passed by orchestrator)
- NO access to: approval/destructive actions

**Rationale**: Only this subagent holds the keys to deployment and code history. This is the security boundary — triage and remediation-drafting work from investigation's findings only, never direct data access. Judges are primed to check for this scoping.

---

## Remediation-Drafting Agent

**Role**: Propose recovery options without executing anything.

**Input**: Investigation findings + incident context.

**Process**:
1. Evaluate remediation options: rollback to prior version, patch in place, monitor-only hold.
2. For each option, list concrete tradeoffs (risk, latency, customer impact, data consistency).
3. Recommend an option with clear reasoning.
4. Draft a human-readable remediation plan.

**Output**: Proposed action (rollback to version X, or patch with changes Y, or monitor Z), explicit tradeoffs, and recommendation rationale.

**Tool Access**:
- NO direct access to `/metrics`, `/logs`, `/deploy-history`, or GitHub
- Receives investigation findings as structured input only
- NO access to: approval/destructive actions

**Rationale**: Separation of concerns — remediation should reason over findings, not go back to sources. This prevents scope creep into investigation territory and enforces that recommendations are rooted in investigation evidence, not just telemetry. Also simplifies the responsibility chain when a human later approves or rejects the proposed action.

---

## Approval Gate

**Role**: Orchestrator-level guard for destructive actions.

**Process**:
1. Remediation plan proposes an action.
2. Orchestrator presents the action + full incident context to a human decision-maker.
3. Human approves or rejects.
4. If approved: action executes (stub implementation for hackathon).
5. If rejected: action is logged as blocked, investigation can continue or escalate.

**Enforcement**:
- Subagents cannot bypass this gate.
- Rejection path must be tested and visible (non-negotiable per council audit).
- Destructive tools (disable endpoint, rollback, revoke key, publish report) are marked approval-required at TrueForge config level.

---

## Tool Mapping

| Tool | Triage | Investigation | Remediation-Drafting |
|------|--------|---------------|-----------------------|
| `/metrics` | ✓ | ✓ | ✗ |
| `/logs` | ✓ | ✓ | ✗ |
| `/deploy-history` | ✗ | ✓ | ✗ |
| GitHub MCP | ✗ | ✓ | ✗ |
| Sandbox (drift results) | ✗ | ✓ | ✗ |
| Approval gates | ✗ | ✗ | (via orchestrator) |

---

## When to Spawn Each Subagent

1. **Triage** — Runs first, always, on every incident. Lightweight; classifies severity.
2. **Investigation** — Runs if triage severity ≥ medium, or on explicit user request. Full-access, may take time.
3. **Remediation-Drafting** — Runs after investigation completes. Takes investigation output, proposes actions.
4. **Approval Gate** — Triggered by remediation plan; orchestrator handles human interaction.

---

## Session Persistence

If a session restarts mid-investigation:
- Triage output is re-used (cached).
- Investigation state (findings so far, tool calls made) is restored from session storage.
- Remediation-drafting waits for investigation to complete in full.

This is a FR6 requirement (Phase 5 testing target).
