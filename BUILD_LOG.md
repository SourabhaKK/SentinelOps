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
