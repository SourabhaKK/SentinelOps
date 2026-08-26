# SentinelOps Demo Storyboard

**Duration:** 3 minutes (strict limit per hackathon rules)

**Target:** Hero incident (Bad Deploy) — demonstrates all non-negotiable primitives

---

## Scene 1: Incident Alert (0:00-0:30)

**Narrator:** "An ML model deployment goes wrong. The authorization system missed an unauthorized model in production."

**Visuals:**
- Show metrics dashboard spike:
  - Error rate: 8% → 24% (300% increase)
  - Latency p99: 45ms → 130ms (290% increase)
  - Timestamp: "5 minutes ago"

**What's happening:**
- Model v1.2.0-unauthorized deployed 5 minutes ago
- Metrics spiked immediately
- System triggered alert automatically

---

## Scene 2: Triage (0:30-1:00)

**Narrator:** "SentinelOps receives the alert and classifies it."

**Visuals:**
- TrueForge console shows:
  ```
  [TRIAGE SUBAGENT]
  Severity: CRITICAL
  Type: DISTRIBUTION_DRIFT
  Recommendation: Fetch metrics; run statistical analysis
  Confidence: HIGH
  ```

**What's happening:**
- Triage agent (no data access) classifies based on metric deltas
- Routes to Investigation subagent
- Takes ~5 seconds

---

## Scene 3: Investigation (1:00-1:45)

**Narrator:** "Investigation dives deep into metrics, logs, and GitHub history."

**Visuals (in sequence):**

**3a. Statistical Analysis (10 sec)**
```
[INVESTIGATION SUBAGENT]
Running drift analysis in Daytona sandbox...

PSI (Population Stability Index): 0.52 (SIGNIFICANT)
KS Statistic: 0.38, p-value < 0.001
Chi-Square: SIGNIFICANT shift detected

Findings: Latency distribution shifted right; error patterns changed
```

**3b. GitHub Deep Dive (20 sec)**
```
Searching recent commits...
Found anomaly: Commit c104edc

  Message: "Deploy unauthorized model version v1.2.0"
  Author: [deployment process]
  Model Hash: malformed_hash_xyz789
  Approval Status: REJECTED
  Risk Level: CRITICAL

ROOT CAUSE CONFIRMED: Unauthorized model in production
```

**What's happening:**
- Statistical tests confirm distribution shift
- GitHub MCP discovers bad commit
- Investigation combines evidence
- Takes ~30 seconds for full analysis

---

## Scene 4: Remediation & Approval (1:45-2:45)

**Narrator:** "Based on findings, the system proposes action and awaits human approval."

**Visuals:**

**4a. Remediation Proposal (15 sec)**
```
[REMEDIATION SUBAGENT]
Root Cause: Unauthorized model deployed (commit c104edc)
Proposed Action: DISABLE_ENDPOINT
Reasoning: Prevent cascading failures; halt bad predictions
Confidence: HIGH
```

**4b. Approval Gate (30 sec)**
```
[APPROVAL GATE]
============================================================
Action: DISABLE_ENDPOINT
Severity: CRITICAL
Incident ID: bad-deploy-1787731576
Root Cause: Unauthorized model v1.2.0-malformed

Evidence:
  - Error rate increased 300% (8% → 24%)
  - Latency increased 290% (45ms → 130ms)
  - GitHub commit c104edc shows REJECTED approval status
  - PSI drift score: 0.52 (significant)

Expected Outcome:
  - All inference requests fail with clear error
  - Service offline until remediation complete
  - Prevents further damage from bad model

Waiting for human approval...
```

**Human Decision (15 sec):**
```
[HUMAN APPROVER]
"Approved by: alice@company.com
Reason: Confirmed unauthorized model. Statistical tests
        confirm significant shift. Disabling to contain impact."

[APPROVAL GRANTED]
```

**What's happening:**
- System presents full context to human
- Human makes informed decision
- Takes ~60 seconds (shows human review process)

---

## Scene 5: Execution & Audit (2:45-3:00)

**Narrator:** "With approval, the system executes the remediation and logs the decision."

**Visuals:**

```
[EXECUTION]
Action: disable_endpoint
Status: SUCCESS
Message: "Endpoint https://api.example.com/predict is now OFFLINE.
          All inference requests will fail with clear error message."

[AUDIT LOG]
Incident ID:    bad-deploy-1787731576
Session ID:     phase5-bad-deploy
Triage:         CRITICAL DISTRIBUTION_DRIFT
Investigation:  Unauthorized model (commit c104edc)
Remediation:    disable_endpoint
Approval:       APPROVED by alice@company.com
Execution:      SUCCESS
Timestamp:      2026-08-26T13:36:16
```

**Final Frame:**
```
SentinelOps — AI Safety Incident Response
✓ Real GitHub connection
✓ Approval gates with human review
✓ Session persistence through reconnection
✓ Statistical drift detection
✓ Multi-agent decomposition with tool scoping
```

---

## Key Demo Narrative Beats

1. **Problem Setting** (0-30s)
   - "ML incident: metrics spike + alert"
   - Show the data anomaly clearly

2. **System Response** (30s-1m)
   - "Triage agent classifies incident"
   - Fast, no data access needed

3. **Deep Investigation** (1-1:45m)
   - "Investigation correlates multiple signals"
   - Show statistical rigor (PSI/KS tests)
   - Show GitHub connection (c104edc)
   - Emphasize: no single agent has all data

4. **Human-in-the-Loop** (1:45-2:45m)
   - "Human approves critical action"
   - Show context available for decision
   - Emphasize: system cannot execute without approval

5. **Audit & Outcome** (2:45-3m)
   - "Action executed, audit trail maintained"
   - Show that human review happened (timestamps)

---

## Demo Prerequisites

**System State:**
- TrueForge running locally on http://localhost:8790
- All MCP servers connected (GitHub, Telemetry, Daytona)
- Claude model configured (primary)
- Hero incident scenario pre-loaded

**Demo Flow:**
1. Start with metrics dashboard showing spike
2. Trigger incident through SentinelOps UI
3. Watch Triage → Investigation → Remediation → Approval
4. Human approves action
5. Action executes

**Timing:**
- Triage: ~5 seconds
- Investigation: ~30 seconds
- Remediation proposal: ~5 seconds
- Approval flow: ~30 seconds (includes human thinking)
- Execution: ~5 seconds
- **Total: ~75 seconds (fits in 3-minute window with margin)**

---

## Fallback Scenarios

**If live demo timing is tight:**
- Pre-record Investigation phase (statistical analysis takes longest)
- Show recorded output while explaining
- Focus live demo on Approval gate + Execution

**If Daytona unavailable:**
- Show cached drift analysis results
- Emphasize that system gracefully handles sandbox delays

**If GitHub MCP unavailable:**
- Demonstrate with pre-fetched commit data
- Show that system found c104edc through investigation

---

## Script Notes for Demo

**Tone:** Professional, focused on safety and human oversight

**Key phrases:**
- "Real GitHub connection"
- "Multi-agent decomposition with tool scoping"
- "Approval gates ensure human oversight"
- "Session persistence handles reconnection"
- "Statistical rigor: PSI and KS tests confirm drift"

**Emphasis:**
- NOT: "The system is fully autonomous"
- YES: "The system is autonomous with required human approval gates"
- YES: "Multiple signals (metrics, logs, GitHub) correlated by Investigation agent"
- YES: "Triage is fast; Investigation is thorough; Remediation is strategic"

---

## Hackathon Judging Alignment

**FRs (Functional Requirements):**
- FR1: Real GitHub ✅ (c104edc discovered)
- FR2: Approval gates ✅ (Alice approves disable_endpoint)
- FR3: Session persistence ✅ (would show in Phase 5 context)
- FR4: Subagent decomposition ✅ (Triage, Investigation, Remediation visible)
- FR5: Sandbox skill ✅ (Daytona runs PSI/KS tests)
- FR6: Multiple scenarios ✅ (Three incidents available)

**Council Audit Non-Negotiables:**
1. Approval gate with reject path ✅
2. Real GitHub ✅
3. Session persistence ✅

**Stretch Goals:**
- Exa/Tavily corroboration (if time permits)
- Qodo PR review trail (visible in repo)
- Live system demo (vs. recording)
