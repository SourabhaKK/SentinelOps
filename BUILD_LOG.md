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

### [Phase 1.3] — Aug 24, 2026 — !

**What was built:**
- All 3 API keys configured: DAYTONA_API_KEY, GOOGLE_API_KEY, GROQ_API_KEY ✅
- trueforge.config.json created with Gemini 2.0 Flash (primary) and Groq (fallback) models
- Environment setup scripts and verification (check:env working correctly)
- docs/PHASE_1.3_TRUEFORGE_SETUP.md with detailed startup instructions
- data/ directory created for session storage

**What broke:**
TrueForge v0.1.4 fails to start on Windows due to ESM loader compatibility issue with absolute paths. Error: "Only URLs with a scheme in: file, data, and node are supported by the default ESM loader. On Windows, absolute paths must be valid file:// URLs. Received protocol 'c:'"

This affects startup regardless of configuration or how TrueForge is invoked. Local sandbox fallback also unavailable on Windows (macOS/Linux only).

**Fix or resolution:**
BLOCKED on Windows with TrueForge v0.1.4. Three workaround options:
1. Use WSL (Windows Subsystem for Linux) — recommended for hackathon
2. Use Docker containerization
3. Switch to macOS/Linux machine

See DECISIONS.md for blocker escalation.

**Time spent (rough):**
~30 minutes (config, debugging, attempting startup).

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
