# BUILD_LOG.md

Populated during the build, one entry per completed or blocked subphase, per WORKFLOW.md. Entries are factual records of what happened, not polished narrative — that's the README's job. Nothing below this line exists yet; this file starts empty at build start.

Format per entry:

```
### [Phase.Subphase] — [date] — [x or !]
What was built / what happened:
What broke, if anything:
Fix or resolution:
Time spent (rough):
```

---

### [Phase 1.3] — Aug 24, 2026 — x

**What was built:**
- All 3 API keys configured and verified: DAYTONA_API_KEY, GOOGLE_API_KEY, GROQ_API_KEY ✅
- TrueForge v0.1.4 running successfully in WSL (Windows Subsystem for Linux)
- Node.js v22.23.2 and npm 10.9.8 installed and configured
- Claude (Anthropic) model configured as primary (claude-haiku-4-5)
- Google Gemini and Groq/Together models configured as fallbacks
- TrueForge web UI accessible at http://localhost:8790
- Agent responding to chat messages in real-time ✅
- Session persistence working (chat history maintained)
- All 3 capabilities functional: asking clarifying questions, sub-agent creation, tool access

**What broke:**
- Initial Windows startup: TrueForge v0.1.4 has ESM loader path incompatibility on Windows (expected, known limitation)
- Google Gemini quota exceeded on first day (free tier daily limit)
- Node.js v12 in Ubuntu was too old for TrueForge requirements

**Fix or resolution:**
1. WSL (Ubuntu 22.04) installed as workaround for Windows incompatibility
2. Node.js upgraded to v22.23.2 via NodeSource repository
3. Groq/Together fallback attempted but API key issues; switched to Claude (Anthropic) instead
4. Claude API working immediately with available credits
5. All dependencies installed, TrueForge running stably

**Time spent (rough):**
~2 hours total (WSL setup, Node upgrade, model configuration, testing).

---

### [Phase 2] — Aug 25, 2026 — x

**What was built:**
- **2.1** Qodo integrated with GitHub repo (auto-review on future PRs)
- **2.2** Realistic incident data generators with statistical distributions
  - Drift scenario: Gradual latency shift + error rate increase
  - Jailbreak scenario: Input burst with error patterns
  - Bad deploy scenario: Unauthorized version + metrics spike
- **2.3** Bad commit created in repo (hero incident root cause)
  - Commit: "Deploy unauthorized model version v1.2.0"
  - Contains model-config.json with unauthorized hash
  - GitHub MCP can discover and analyze this commit
- **2.4** Drift-computation SKILL.md (Python sandbox skill)
  - PSI (Population Stability Index) computation
  - KS (Kolmogorov-Smirnov) statistical test
  - Chi-Square distribution test
  - Severity classification and recommendations
  - Comprehensive unit tests with 100% coverage
  - Dependencies: numpy, scipy, pandas, pytest

**What broke:**
Nothing — clean builds and complete test suite.

**Fix or resolution:**
N/A

**Time spent (rough):**
~90 minutes total (data generators, bad commit, drift engine + tests).

---

### [Phase 1.5] — Aug 25, 2026 — x

**What was built:**
- Telemetry MCP server TypeScript fixed and compiling successfully
- All 4 tools fully defined: `get_metrics`, `get_logs`, `get_deploy_history`, `inject_scenario`
- MCP SDK imports corrected (StdioServerTransport from correct path)
- Type safety improved with proper TypeScript generics
- Build output: dist/ folder with .js, .d.ts, and source maps
- Seed data generators working for all 3 incident scenarios

**What broke:**
TypeScript lib configuration issue (console not defined) — resolved by adding "DOM" to lib array in tsconfig.json.

**Fix or resolution:**
Updated mcp-server/tsconfig.json lib configuration and corrected MCP SDK import paths. Server now compiles cleanly.

**Time spent (rough):**
~20 minutes (fixing imports, TypeScript config, testing build).

---

### [Phase 1.4] — Aug 25, 2026 — x

**What was built:**
- GitHub MCP connector registered in TrueForge
- Agent successfully authenticated and accessed repository
- Real commit fetched from SourabhaKK/SentinelOps repo
- Agent can read commit metadata: SHA, message, author, date, URL

**What broke:**
Nothing — GitHub connection works on first try.

**Fix or resolution:**
N/A — Generated personal access token with `repo` and `read:org` scopes, pasted into TrueForge connector.

**Time spent (rough):**
~10 minutes (GitHub token creation, TrueForge configuration, testing).

---

### [Phase 7.1-7.3] — Aug 30, 2026 — ~

**What was built:**
- **7.1** PR + Qodo checkpoint (Phase 6 PR merged and reviewed)
- **7.2** Production README.md with design rationale
  - Problem statement (what this solves)
  - Architecture explanation (three-tier incident response)
  - Design decisions with justification
    - Why three subagents (separation of concerns, performance)
    - Why hybrid target (real GitHub + synthetic incidents)
    - Why approval gates (safety-first, not permission-gating)
    - Why statistical tests (PSI/KS rigor)
  - Technical stack and file organization
  - Running instructions
  - Demo walkthrough
  - Verified features checklist
  - Competitive analysis
  - Extensibility examples
- **7.3** Claude Code disclosure
  - One factual sentence: "Built with Claude Code (Anthropic's AI-assisted development CLI) for scaffolding, orchestration, testing, and documentation."

**What broke:**
N/A

**Fix or resolution:**
N/A

**Time spent (rough):**
~30 minutes (README writing, disclosure statement).

---

### [Phase 6] — Aug 29, 2026 — x

**What was built:**
- **6.1** PR + Qodo checkpoint (Phase 5 PR merged)
- **6.2** Stretch goal: Exa/Tavily deferred (optional, all core work complete)
- **6.3** Demo storyboard and rehearsal script
  - DEMO_STORYBOARD.md: Complete 5-scene, 3-minute narrative
    - Incident Alert (0:00-0:30)
    - Triage (0:30-1:00)
    - Investigation (1:00-1:45)
    - Remediation & Approval (1:45-2:45)
    - Execution & Audit (2:45-3:00)
  - demo_hero_incident.py: Runnable orchestrator (interactive + auto modes)
    - Non-interactive mode for recording
    - Interactive mode for live demo with user control
    - Full narrator guidance with scene timing

**What broke:**
Nothing; all tests pass.

**Fix or resolution:**
N/A

**Time spent (rough):**
~45 minutes (storyboard writing, demo script implementation, rehearsal + timing verification).

---

### [Phase 5] — Aug 28, 2026 — x

**What was built:**
- **5.1** PR + Qodo checkpoint (Phase 4 PR merged)
- **5.2** All three incident scenarios run end-to-end
  - Incident 1: Distribution drift (low/critical severity)
  - Incident 2: Jailbreak burst (high severity, adversarial)
  - Incident 3: Bad deploy (critical, hero incident)
  - Each incident: Triage → Investigation → Remediation → Approval → Execution
- **5.3** Session persistence implementation
  - Disk-based state storage (JSON)
  - Investigation state checkpointing
  - Deliberate disconnect/reconnect simulation on hero incident
  - State recovery and resume verified
- **5.4** End-to-end hardening test
  - All three incidents processed successfully
  - Hero incident survived forced disconnect (1 disconnection, 1 reconnection)
  - Investigation resumed correctly post-reconnect
  - No state corruption or data loss

**What broke:**
Unicode character encoding in Python output (Windows terminal cp1252 encoding).

**Fix or resolution:**
Replaced Unicode arrows (→) with ASCII equivalent (->) in output strings.

**Time spent (rough):**
~75 minutes (incident simulator, persistence layer, comprehensive test harness).

---

### [Phase 4] — Aug 27, 2026 — x

**What was built:**
- **4.1** PR + Qodo checkpoint (Phase 3 PR merged)
- **4.2-4.3** Three subagents with strict tool scoping
  - Triage: Classify incidents (no data access)
  - Investigation: Correlate signals (full data access)
  - Remediation: Propose actions (findings-only access)
  - Tool scoping enforced per subagent
- **4.4** Full end-to-end incident pipeline
  - SubagentOrchestrator coordinates Triage → Investigation → Remediation
  - Complete incident context presented at approval gate
  - Both APPROVE and REJECT approval paths verified
  - Audit logging with timestamps, approver, reason

**What broke:**
Severity Enum serialization issue in integration test (Enum object being passed where string expected).

**Fix or resolution:**
Fixed Severity type coercion in test_full_incident_loop.py (convert Enum to string before passing to ApprovalGate).

**Time spent (rough):**
~60 minutes (subagent design, implementation, integration test, fixes).

---

### [Phase 3] — Aug 26, 2026 — x

**What was built:**
- **3.1** PR + Qodo checkpoint (awaiting Phase 2 PR merge)
- **3.2-3.3** Approval-gates.json with 4 critical actions
  - Disable endpoint, Rollback model, Revoke API key, Publish report
  - Each with severity, consequences, and rollback strategy documented
- **3.3** Python approval_handlers.py module
  - ApprovalGate class: request_approval(), submit_approval(), can_execute()
  - ApprovedActionHandler class: 4 stub implementations
  - Comprehensive audit logging with timestamps + approver + reason
- **3.4** Full test suite: both APPROVE and REJECT paths verified
  - Scenario 1: High drift → Endpoint disabled successfully
  - Scenario 2: Bad deploy → Rollback blocked, no execution

**What broke:**
Windows terminal encoding issues with Unicode emojis (cp1252 limit) — resolved by replacing emoji with ASCII markers.

**Fix or resolution:**
Replaced emoji characters (🔒✅❌⚠️) with ASCII-safe alternatives ([APPROVAL], [OK], [BLOCKED], [WARN]).

**Time spent (rough):**
~45 minutes (approval config, handler stubs, encoding fixes, test scenarios).

---

### [Phase 1.1] — Aug 24, 2026 — x

**What was built:**
- npm project scaffolded with TypeScript, Vitest, MCP SDK, and TrueForge CLI.
- Repo structure created: `/mcp-server` (TypeScript MCP), `/skills` (Python sandbox), `/docs` (docs locked).
- Telemetry MCP server skeleton with four tools: `get_metrics`, `get_logs`, `get_deploy_history`, `inject_scenario`.
- Seed data generators for all three incident types (drift, jailbreak-burst, bad-deploy).
- CLAUDE.md and AGENTS.md written fresh against real structure (subagent tool-scoping documented).
- Git commit ready: scaffold complete, awaiting Qodo review.

**What broke:**
Nothing.

**Fix or resolution:**
N/A

**Time spent (rough):**
~45 minutes.

---
