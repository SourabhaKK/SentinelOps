# TECHSTACK.md — locked

Every choice below is decided. If a build step needs something not listed here, stop and add it to this file with a one-line reason before writing code against it — don't silently introduce a new dependency mid-build.

## Agent runtime

TrueForge (`@truefoundry/trueforge`), run locally via `npx @truefoundry/trueforge`. Not the Docker Compose / hosted-mode path — this project runs in standalone local mode for the full build week, since nothing here needs multi-replica production deployment. SQLite backing store (TrueForge's local-mode default), not Postgres/Redis.

## Model providers

Primary: Gemini 2.0 Flash, free tier.
Fallback: Groq, free tier.
Isolated API keys for each, set from day 1 — this is the exact pattern that fixed cross-provider rate-limit contention on ChronoScholar; reused deliberately, not reinvented.
Tool-calling reliability (function calling under TrueForge's harness specifically, not just chat generation) gets tested explicitly during day-1/day-2 smoke tests. If either provider's tool-calling proves unreliable under the harness, that's escalated immediately, not discovered at demo time.

## MCP servers

**Custom telemetry server** — TypeScript, using the official `@modelcontextprotocol/sdk`. Exposes `/metrics`, `/logs`, `/deploy-history`, `/inject-scenario`. No web framework beyond what the MCP SDK's transport requires — don't add Express or similar unless the SDK genuinely needs it.

**GitHub** — the official public GitHub MCP server, registered by URL through TrueForge's catalog, pointed at the SentinelOps repo itself. Not a custom wrapper. Scoping (investigation subagent only, read-only) is enforced at TrueForge's subagent tool-permission layer, not by restricting the server's own surface — same mechanism already used for `/deploy-history` access.

**Exa/Tavily** — stretch only, built-in catalog entries, not required for the submission to be complete.

## Sandbox

Daytona, TrueForge's shipped sandbox provider. Not a choice — this is what the harness provides.

## Sandbox skill language

Python, for the drift-computation SKILL.md specifically. This is a direct port of existing, tested PSI/KS/Chi-Square logic from ml-model-monitoring-drift-detection (pandas/scipy) — rewriting working statistical code into TypeScript for consistency with the rest of the stack would be pure risk with no payoff. Every other piece of custom code in this repo is TypeScript; this one piece is the deliberate exception, and the README should say so plainly rather than leave it looking inconsistent.

## Package management

npm. TrueForge's own quickstart is npx-based — no reason to introduce pnpm/yarn friction against a tool built around npm.

## Testing

Vitest for the TypeScript telemetry server. Pytest for the Python sandbox skill. Every PR that touches either should carry a corresponding test, both because Qodo needs something real to review and because this matches the TDD discipline already proven on FinSight (183 pytest cases) and the drift-detection project (138 pytest cases) — this project should read as the same engineer, not a different one.

## Repo layout

Single repo, not split across multiple repos:
```
/mcp-server      — telemetry server, TypeScript
/skills          — SKILL.md + Python drift-computation code
/docs            — WORKFLOW.md, PRD.md, TASKS.md, BUILD_LOG.md, DECISIONS.md
CLAUDE.md
AGENTS.md
README.md
```

## Explicitly not doing

No Docker. No CI pipeline. Nothing here gets deployed — judges clone and run locally against `npx trueforge`. Both would be scope creep against a six-day solo build with no judging-criterion payoff, even though FinSight and the drift-detection project both shipped Docker/CI. Reusing that pattern here would be consistency for its own sake, not a decision earning its place. If this changes (e.g., a judge specifically asks for a hosted demo), revisit — don't build it preemptively.
