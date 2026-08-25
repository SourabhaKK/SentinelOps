# Phase 3 Summary: Approval Gates

## Overview

Phase 3 (Aug 26) implements human approval gates for destructive remediation actions. The agent can now propose critical actions but cannot execute them without explicit human authorization.

---

## What Was Built

### 3.1-3.2: Approval Configuration

**File:** `approval-gates.json`

Four approval-required actions:

1. **Disable Endpoint** — Take model inference offline
   - Severity: CRITICAL
   - Consequences: Service degradation, customer impact
   - Rollback action: `enable_endpoint`

2. **Rollback Model** — Revert to previous model version
   - Severity: CRITICAL
   - Consequences: Behavior shift, metrics anomalies
   - Requires investigation first

3. **Revoke API Key** — Invalidate authentication tokens
   - Severity: CRITICAL
   - Consequences: Service disruption, re-authentication required
   - Rollback action: `issue_new_api_key`

4. **Publish Incident Report** — Notify stakeholders
   - Severity: HIGH
   - Consequences: Public visibility, incident procedures triggered
   - Audit trail created

**Workflow:**
```
Remediation agent proposes action
        ↓
Approval gate presents to human with full context
        ↓
Human decision: APPROVE | REJECT | MODIFY
        ↓
Action executes only after explicit approval
        ↓
Audit log: timestamp, decision, reason
```

### 3.3: Stub Handlers

**File:** `approval_handlers.py`

Python module with approval-gate implementation:

**Classes:**
- `ApprovalDecision` — Enum (PENDING, APPROVED, REJECTED, MODIFIED)
- `ApprovalRequest` — Dataclass capturing action + incident context
- `ApprovalResponse` — Dataclass with decision + approver + reason
- `ApprovalGate` — Central gate managing pending/historical requests
- `ApprovedActionHandler` — Stub implementations of destructive actions

**Key Methods:**
- `gate.request_approval()` — Propose action, display to human
- `gate.submit_approval()` — Human submits decision
- `gate.can_execute()` — Check if request was approved
- `handler.disable_endpoint()` — Execute if approved, else BLOCKED
- `handler.rollback_model()` — Execute if approved, else BLOCKED
- `handler.revoke_api_key()` — Execute if approved, else BLOCKED
- `handler.publish_incident_report()` — Execute if approved, else BLOCKED

### 3.4: Comprehensive Test

**Test scenarios completed:**

**Scenario 1: High Drift → APPROVAL**
```
Incident: High PSI drift detected (0.52)
Error rate: 8% -> 22%
Proposed action: Disable endpoint
Human decision: APPROVED by alice@company.com
Result: Endpoint disabled (200), service now OFFLINE
```

**Scenario 2: Bad Deploy → REJECTION**
```
Incident: Unauthorized model v1.2.0-malformed
Commit: c104edc
Proposed action: Rollback model
Human decision: REJECTED by bob@company.com
Reason: "Investigate commit first, disable endpoint first"
Result: Action BLOCKED (400), rollback does not execute
```

**Output:**
Both paths verified end-to-end:
- Approval accepted: Handler executes, returns SUCCESS
- Approval rejected: Handler returns BLOCKED, no destructive action occurs

---

## Integration Points

### With TrueForge Orchestrator
- Approval gate sits between Remediation subagent and action execution
- Orchestrator presents approval request in UI with incident context
- Human approval stored in session state
- Audit trail maintained for compliance

### With Incident Scenarios
- Drift incident → Propose disable_endpoint
- Jailbreak burst → Propose revoke_api_key
- Bad deploy → Propose rollback_model + publish_report

### With Subagents (Phase 4)
- Triage → No approval access
- Investigation → No approval access
- Remediation → Only proposes; cannot execute without approval

---

## Testing

All paths verified:
```bash
cd SentinelOps
python approval_handlers.py
```

Output: 2 scenarios (APPROVE + REJECT) demonstrating:
- ✅ Approval accepted → Action executes
- ✅ Approval rejected → Action blocked
- ✅ Audit history maintained
- ✅ Clear human-readable request + decision logging

---

## Impact

- **Safety First:** No destructive action executes without human review
- **Full Context:** Approval request includes incident details, severity, consequences
- **Audit Trail:** All decisions logged with timestamp + approver + reason
- **Clear Paths:** Both approval and rejection paths work reliably
- **Extensible:** Easy to add new approval-required actions or decision options (MODIFY)

---

## Next Phase

**Phase 4 (Aug 27):** Subagent decomposition

Split agent into three specialized roles:
1. **Triage:** Classify incidents, no data-source access
2. **Investigation:** Deep dive into metrics/logs/commits, full data access
3. **Remediation:** Propose actions based on investigation, proposes approvals

End state: Full incident → gate loop with three-tier evidence gathering and decision-making.

---

## Files Changed

```
approval-gates.json              NEW — Approval configuration + scenarios
approval_handlers.py             NEW — Gate + handler + test implementation
PHASE_3_SUMMARY.md              NEW — This file
```

## Commits

TBD (pending git push)
