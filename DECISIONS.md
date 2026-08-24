# DECISIONS.md

Pre-build entries below capture decisions already made during planning, so a Claude Code session starting Phase 1 has the full history without re-reading every prior document. New entries get added during the build per WORKFLOW.md — append, don't rewrite history.

---

### [Pre-build] Target system: hybrid, not fully synthetic
**Decision:** Bad-deploy incident roots its cause in a real GitHub commit in the SentinelOps repo itself; drift and jailbreak-burst incidents stay fully synthetic.
**Alternative considered:** Fully self-built synthetic telemetry server as the only target.
**Why rejected:** Conflicts directly with the hackathon's stated bar — "connected, not mocked." A judge primed by that language discounts a target entirely under the builder's control.
**Source:** Council audit round 1.

### [Pre-build] Bad-deploy target: this repo itself, not a separate seeded repo
**Decision:** The GitHub connection points at SentinelOps' own commit history.
**Alternative considered:** A separate purpose-built example repo (or an existing repo like ml-model-monitoring-drift-detection) with a staged bad commit.
**Why rejected:** A separate repo is real but the bad commit in it is still written specifically to be found — an improvement over synthetic data, not a full solve. Targeting this repo's own organic history is more genuinely real, removes a full day of separate-repo prep, and gives the demo a stronger self-referential hook.
**Source:** Council audit round 2.

### [Pre-build] MCP server wrapper: TypeScript
**Decision:** The custom telemetry MCP server is built in TypeScript with the official `@modelcontextprotocol/sdk`.
**Alternative considered:** Python/FastAPI, matching existing muscle memory from FinSight and prior projects.
**Why rejected:** TrueForge itself is TypeScript-native and its SDK is TS-first; building the wrapper in the harness's native language reduces debugging friction against an unfamiliar, five-day-old tool.
**Source:** Original plan, confirmed round 2 (locked, no further deliberation).

### [Pre-build] Sandbox skill language: Python, as the deliberate exception
**Decision:** The drift-computation SKILL.md is Python, ported from ml-model-monitoring-drift-detection.
**Alternative considered:** TypeScript, for stack consistency.
**Why rejected:** The existing PSI/KS/Chi-Square logic is tested, working Python. Rewriting it into TypeScript for consistency alone is risk with no payoff — Daytona executes arbitrary code, so the harness doesn't force a language here.
**Source:** Techstack discussion.

### [Pre-build] Model providers: Gemini 2.0 Flash primary, Groq fallback, both free tier
**Decision:** No paid model provider for build or demo.
**Alternative considered:** Anthropic Claude as primary, given quality/reliability advantages for agentic tool-calling.
**Why rejected:** Cost-consciousness was an explicit user constraint. Free-tier primary+fallback with isolated keys is a pattern already proven on ChronoScholar (solved cross-provider rate-limit contention once already) — reused deliberately rather than reinvented. Flagged risk: tool-calling reliability under TrueForge's harness is a new stress test versus prior chat-style agent use of these providers; escalate early if it proves flaky, per WORKFLOW.md stop-condition guidance.
**Source:** Techstack discussion.

### [Pre-build] GitHub MCP: official public server, not a custom wrapper
**Decision:** Register the official public GitHub MCP server via TrueForge's catalog.
**Alternative considered:** A minimal custom-built GitHub MCP wrapper scoped to only commit/PR reads, for a tighter access-control story.
**Why rejected:** The scoping story doesn't require custom code — TrueForge's subagent tool-permission layer achieves the same result (only the investigation subagent gets GitHub access) at the configuration level, same mechanism already used for `/deploy-history`. Building custom code to solve a problem the harness already solves via config is scope creep against the day-1 timebox, which the risk register treats as the highest-leverage stop condition in the schedule.
**Source:** Techstack discussion.

### [Pre-build] No Docker, no CI pipeline
**Decision:** Neither is built for this project, despite both being present on FinSight and the drift-detection project.
**Alternative considered:** Reuse the Docker/GitHub Actions pattern from prior projects for consistency.
**Why rejected:** Nothing in this project gets deployed — judges clone and run locally via `npx trueforge`. Reusing a deployment pattern with no deployment target is consistency for its own sake, not a decision earning its place.
**Source:** Techstack discussion.

### [Pre-build] Demo: one hero incident, not all three
**Decision:** The three-minute demo is built entirely around incident 3 (self-repo bad-deploy). Incident 1 (drift) gets a brief background cut; incident 2 (jailbreak burst) gets no screen time.
**Alternative considered:** Attempt to showcase all three incidents within the time limit.
**Why rejected:** Three incidents don't fit at real depth in three minutes. A judge remembers one well-executed narrative better than three rushed ones.
**Source:** Council audit round 2.

### [Pre-build] Qodo PR review: daily habit, not a day-1 setup step
**Decision:** Every day of the build produces at least one PR reviewed by Qodo before merge.
**Alternative considered:** Install Qodo on day 1 and treat it as done.
**Why rejected:** The hackathon's own rules explicitly penalize a single PR opened the night before the deadline. A day-1-only install without daily cadence fails the Best Code Quality track by default regardless of code quality.
**Source:** Council audit round 2.

### [Pre-build] README: forward-facing design rationale, not a chronological audit trail
**Decision:** The public README explains why decisions were made, not the sequence of catching and fixing earlier mistakes.
**Alternative considered:** Document the full council-audit correction history in the README, matching the transparency style used on the Allica take-home's system design note.
**Why rejected:** A judge rewards apparent foresight, not visible self-correction, in a three-minute-attention-span context. The full audit-trail version of the story is better suited to an interview conversation, where there's time for it to read as rigor rather than as backtracking. This DECISIONS.md file and BUILD_LOG.md preserve that full history for exactly that purpose.
**Source:** Council audit round 3.

### [Pre-build] Claude Code disclosure: one factual sentence, no more
**Decision:** README states plainly that the project was built solo using Claude Code, alongside TrueForge as the agent runtime.
**Alternative considered:** No disclosure; or, alternatively, a more prominent write-up of the AI-assisted build process as a thematic angle.
**Why rejected (no disclosure):** The hackathon's own FAQ permits AI coding tools without qualification — silence risks looking evasive on a question that isn't actually sensitive.
**Why rejected (prominent angle):** Not worth the space in a document meant to explain the product, not the process. Better suited to the separate blog-post track, which already exists as a free win.
**Source:** Council audit round 3.

### [Pre-build] CLAUDE.md/AGENTS.md: adapted structure, not copied content
**Decision:** Written fresh on Day 1 against this repo's actual layout, borrowing the Allica pattern's shape (lean, tool-agnostic commands/style/testing/boundaries) but not its content.
**Alternative considered:** Copy the Allica CLAUDE.md/AGENTS.md directly and adjust as needed.
**Why rejected:** A copied file that doesn't match this repo's real structure (TypeScript MCP server, TrueForge catalog config, Daytona sandbox skill, Python sandbox skill) reads as process theater to anyone who checks it against the actual code, rather than genuine practice.
**Source:** Council audit round 3.

### [Phase 1.3] TrueForge v0.1.4 Windows compatibility blocker — escalate to WSL
**Decision:** TrueForge v0.1.4 fails to start on Windows (ESM loader absolute-path incompatibility). Recommend WSL (Windows Subsystem for Linux) as immediate workaround for hackathon continuity.
**Issue:** All 3 API keys configured and verified; TrueForge startup fails with "Only URLs with a scheme in: file, data, and node are supported... Received protocol 'c:'". Affects all Windows startup attempts regardless of config.
**Alternative considered:** (1) Debug TrueForge ESM loader issue (time-intensive, low success probability on Day 1). (2) Use Docker (adds setup, slower iteration). (3) Rewrite agent runtime (out of scope, defeats hackathon tool choice).
**Why WSL:** Fastest unblock. TrueForge and all code run identically to Linux; native Windows file integration; VSCode WSL extension for seamless IDE use. No container overhead. Proven pattern for Node.js on Windows.
**Why not pure Windows:** TrueForge v0.1.4 has a fundamental ESM+Windows incompatibility; waiting for v0.1.5 is not viable in a 6-day hackathon.
**Source:** Phase 1.3 stop condition triggered per WORKFLOW.md. All prerequisites (API keys) complete; core tool (TrueForge) is blocker.
**Next:** User should install WSL2 and proceed with Phase 1.3 in WSL terminal (same commands, same code, Linux runtime).
