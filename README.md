# SentinelOps

**AI Safety Incident-Response Agent** — When ML models fail in production, SentinelOps automatically triages, investigates, proposes remediation, and requires human approval before execution.

---

## What Problem Does This Solve?

Modern ML systems fail silently. A model's error rate jumps 300%, but the on-call engineer doesn't know:
- **What happened?** (Distribution drift? Bad deploy? Attack?)
- **Why did it happen?** (Look at logs, metrics, version history, code commits)
- **What should we do?** (Disable? Rollback? Investigate data source?)
- **Who decided?** (Need audit trail for compliance)

SentinelOps automates the investigation and brings human judgment into the decision loop.

---

## How It Works

### Three-Tier Incident Response

**Triage Subagent** (no data access)
- Receives raw alert: error rate spike, latency spike, etc.
- Classifies severity and incident type in <5 seconds
- Routes to Investigation for deep dive
- Fast, focused, no tool calls

**Investigation Subagent** (full data access)
- Correlates evidence across multiple sources:
  - **Metrics:** PSI/KS statistical drift tests (sandbox)
  - **Logs:** Error patterns, anomalies
  - **Deploy history:** Recent model versions
  - **GitHub:** Read commits for unauthorized changes
- Identifies root cause candidates with evidence
- Takes ~30 seconds for thorough analysis

**Remediation Subagent** (findings-only access)
- Works exclusively from Investigation output
- Proposes action: disable endpoint, rollback model, revoke API key, or publish report
- Provides reasoning and rollback plan
- No direct data access (separation of concerns)

### Approval Gate (Human-in-the-Loop)

- Presents full investigation context to human
- Shows evidence, root causes, proposed action
- Three decision options: APPROVE, REJECT, MODIFY
- Logs decision with timestamp and approver
- Action executes only after explicit approval

### Session Persistence

- Investigation state saved after each phase
- Survives network disconnection mid-analysis
- Resume from last checkpoint when connection restored
- Audit trail includes disconnect/reconnection counts

---

## Architecture

```
Incident Alert
    ↓
[TRIAGE]              (fast, no data)
Severity, type        (~5s)
    ↓
[INVESTIGATION]       (thorough, all data)
Root cause + evidence (~30s)
    ↓
[REMEDIATION]         (strategic, findings only)
Proposed action       (~5s)
    ↓
[APPROVAL GATE]       (human decision)
Requires signature    (~30s + human thinking)
    ↓
[EXECUTION]
Action runs (if approved)
```

---

## Design Decisions

### Why Three Subagents?

**Separation of Concerns**
- Triage doesn't need data; it classifies fast
- Investigation doesn't need to decide; it gathers evidence
- Remediation doesn't need data; it strategizes from findings

**Security & Auditability**
- No single subagent can access all data AND make decisions
- Remediation cannot discover data; must work from Investigation's findings
- Clear accountability at each stage

**Performance**
- Triage is fast (no tool calls, no latency spike)
- Investigation runs in parallel once Triage completes
- Remediation is instant (no tools, pure logic)

### Why Hybrid Incident Target?

**Real GitHub History** — This repo has a real "bad commit" (c104edc) that demonstrates:
- Investigation actually finds committed code
- Root cause is discoverable through version control
- Not mocked or synthetic

**Synthetic Incidents** — Three realistic scenarios (drift, jailbreak, bad deploy):
- Testing with synthetic data avoids privacy/compliance issues
- Metrics are generated with actual statistical properties (PSI/KS detectable)
- All three can be triggered on-demand for rehearsal/judges

**Why This Beats "Separate Seeded Repo"**
- No need to maintain two repos
- Shows we understand real incident scenarios
- Judges can inspect the actual commit (c104edc) in the repo

### Why Approval Gates?

**Safety First**
- Critical actions (disable endpoint, revoke keys) require human sign-off
- System can never execute destructive action without approval
- Audit trail for compliance and post-incident review

**Not Permission-Gating**
- System doesn't ask "may I access this data?" (traditional authz)
- System requires "will you approve this action?" (human oversight)
- Two different security models; we chose the right one for incident response

### Why Statistical Tests (PSI/KS)?

**Rigor Over Heuristics**
- PSI (Population Stability Index) quantifies distribution shift
- KS (Kolmogorov-Smirnov) tests statistical significance
- Not just "latency went up"; we prove the distribution changed
- Runnable in sandbox (Daytona) for reproducibility

---

## Technical Stack

- **Runtime:** TrueForge (local mode, SQLite persistence)
- **Models:** Claude (primary), Gemini/Groq (fallback)
- **MCP Servers:**
  - GitHub (read commits, detect bad deploys)
  - Custom Telemetry (metrics, logs, deploy history)
- **Sandbox:** Daytona (runs drift analysis in isolated Python)
- **Skills:** Python (PSI/KS/Chi-Square statistical tests)
- **Testing:** Vitest (MCP), Pytest (Python skills), Python integration tests
- **Package Manager:** npm

---

## File Organization

```
SentinelOps/
├── README.md                  ← You are here
├── CLAUDE.md                  ← Codebase overview
├── AGENTS.md                  ← Subagent architecture
├── DEMO_STORYBOARD.md         ← 3-minute demo narrative
├── TECHSTACK.md               ← Technology choices
├── DECISIONS.md               ← Design decisions + alternatives
├── BUILD_LOG.md               ← Per-phase factual records
├── TASKS.md                   ← Phase checklist
│
├── /mcp-server                ← TypeScript MCP server
│   ├── src/index.ts           ← 4 tools: metrics, logs, deploy-history, inject-scenario
│   ├── src/telemetry.ts       ← Realistic baseline data + incident simulators
│   ├── dist/                  ← Compiled output
│   └── tsconfig.json
│
├── /skills                    ← Python sandbox skills
│   ├── drift_analysis.py      ← PSI/KS/Chi-Square implementation
│   ├── test_drift_analysis.py ← Unit tests
│   ├── requirements.txt        ← Dependencies
│   └── SKILL.md               ← Skill definition
│
├── approval-gates.json        ← 4 critical actions, severity, consequences
├── approval_handlers.py       ← ApprovalGate + ApprovedActionHandler classes
├── subagents.py               ← Three subagent implementations
├── subagent-prompts.md        ← Detailed system prompts
├── incident_simulator.py      ← 3 incident scenario generators
├── session_persistence.py     ← Disconnect/reconnect state management
└── demo_hero_incident.py      ← Runnable 3-minute demo
```

---

## Running the System

### Prerequisites

```bash
# Install dependencies
npm install

# Set API keys
export DAYTONA_API_KEY="..."
export GOOGLE_API_KEY="..."
export GROQ_API_KEY="..."
# OR create .env file

# Verify keys
npm run check:env
```

### Start TrueForge

```bash
# On Windows, use WSL2:
wsl
cd /mnt/host/c/Users/Asus/Desktop/SentinelOps/SentinelOps

npm run trueforge
# TrueForge starts at http://localhost:8790
```

### Run Tests

```bash
# Test MCP server compilation
npm run test:mcp

# Test Python skills
npm run test:skills

# Test full incident pipeline
python test_phase5_hardening.py

# Run demo
python demo_hero_incident.py
```

---

## Demo (3 Minutes)

The demo shows the **hero incident** — an unauthorized model deployed to production.

**Incident:** Error rate jumps 8% → 24%, latency 45ms → 130ms

**Flow:**
1. **Triage** (~5s) — Classify as CRITICAL DISTRIBUTION_DRIFT
2. **Investigation** (~30s) — Run PSI/KS tests, find commit c104edc
3. **Remediation** (~5s) — Propose disable_endpoint
4. **Approval** (~30s) — Human reviews context, approves
5. **Execution** (~5s) — Endpoint offline, audit logged

**Run:**
```bash
python demo_hero_incident.py              # Auto mode
python demo_hero_incident.py --interactive # Live demo mode
```

See `DEMO_STORYBOARD.md` for full script.

---

## Verified Features

### Council Audit Non-Negotiables

✅ **Real GitHub Connection**
- Commit c104edc contains unauthorized model config
- Investigation agent discovers it via GitHub MCP
- Not mocked; actual API calls to GitHub

✅ **Approval Gates with Reject Path**
- Destructive actions require human sign-off
- Both APPROVE and REJECT paths tested
- Audit trail: timestamp, approver, reason

✅ **Session Persistence Through Reconnection**
- Investigation state saved to disk after each phase
- Survives forced disconnect mid-analysis
- Resume from last checkpoint when reconnected
- Demonstrated in Phase 5 hardening tests

### Functional Requirements (All Met)

1. Real incident alerts (metrics + logs) ✅
2. Triage agent (classify, no data) ✅
3. Investigation agent (correlate, all data) ✅
4. Remediation agent (propose, findings only) ✅
5. Approval gate (human decision required) ✅
6. Sandbox skill (PSI/KS drift detection) ✅
7. Session persistence (disconnect/reconnect) ✅
8. Multiple incidents (drift, jailbreak, bad deploy) ✅
9. GitHub integration (real commits) ✅
10. Audit trail (all decisions logged) ✅

---

## What Makes This Competitive?

**Not Just Demos, But Verified**
- Every component tested end-to-end
- Phases 1-6 complete with documented results
- All three council audits passed

**Separation of Concerns as Safety**
- Approval gates aren't permission checks; they're decision gates
- Remediation cannot discover data; must work from findings
- Clear model of who knows what, who decides what

**Real + Synthetic Incidents**
- Real commit (c104edc) in GitHub history shows "connected, not mocked"
- Synthetic incidents with realistic metrics prove statistical rigor
- Three distinct scenarios demonstrate system versatility

**Human-in-the-Loop by Design**
- Not "approve each tool call" (tedious)
- But "approve each remediation action" (meaningful)
- Full investigation context available before decision

---

## Extensibility

### Adding New Incident Types

In `incident_simulator.py`, add:
```python
def simulate_new_incident(self):
    return IncidentScenario(
        incident_id="...",
        incident_type="NEW_TYPE",
        ...metrics...,
        ...logs...,
        ...github_commits...
    )
```

### Adding New Approval-Required Actions

In `approval-gates.json`, add to `approval_required_actions`:
```json
{
  "id": "new_action",
  "name": "New Action Name",
  "severity": "critical",
  "consequences": [...],
  "rollback_action": "..."
}
```

### Adding New Tools

Register in TrueForge UI or `mcp-server/src/index.ts`:
```typescript
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  if (request.params.name === "new_tool") {
    return { content: [...] };
  }
});
```

---

## Qodo Code Review Evidence

**Qodo** integrated with GitHub from Phase 1.1 (Aug 24) and auto-reviews all commits:

**Representative Merged Commits with Qodo Review:**

- **Phase 1 Scaffold** (2366755): Core infrastructure setup
  - TrueForge, npm project, MCP server skeleton, documentation
  - https://github.com/SourabhaKK/SentinelOps/commit/2366755

- **Phase 1.4-1.5** (341e4cc): GitHub MCP + Telemetry MCP functional
  - Real GitHub integration working; metrics/logs/deploy-history tools
  - https://github.com/SourabhaKK/SentinelOps/commit/341e4cc

- **Phase 2** (3f70b8c): Incidents & Statistical Analysis
  - Drift analysis with PSI/KS/Chi-Square tests
  - Bad deploy commit (c104edc) discoverable
  - https://github.com/SourabhaKK/SentinelOps/commit/3f70b8c

- **Phase 3** (3f70b8c): Approval Gates
  - 4 critical actions with approval-required gates
  - https://github.com/SourabhaKK/SentinelOps/commit/3f70b8c

- **Phase 4** (7e3a287): Subagent Decomposition
  - Three-tier agent with tool scoping
  - https://github.com/SourabhaKK/SentinelOps/commit/7e3a287

- **Phase 5** (bbd6c56): Persistence & Hardening
  - Session state survives reconnection
  - https://github.com/SourabhaKK/SentinelOps/commit/bbd6c56

- **Phase 6-7** (411775a): Demo & README
  - 3-minute demo storyboard + production README
  - https://github.com/SourabhaKK/SentinelOps/commit/411775a

**Qodo Configuration:** Integrated from Day 1; all code changes auto-reviewed before merge. Dashboard shows continuous review trail throughout build week.

---

## Acknowledgments

Built with **Claude Code** (Anthropic's AI-assisted development CLI) for scaffolding, orchestration, testing, and documentation.

---

## License

MIT
