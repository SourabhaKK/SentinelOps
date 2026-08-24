# CLAUDE.md — SentinelOps

Codebase conventions and how to assist with SentinelOps development.

## Overview

SentinelOps is an AI safety incident-response agent built for TrueForge (Aug 24–30, 2026). It triages ML system incidents, investigates root causes with real tools and GitHub access, runs sandboxed drift analysis, drafts remediation plans, and gates destructive actions behind human approval.

## Project Structure

```
/mcp-server        TypeScript MCP server for telemetry (/metrics, /logs, /deploy-history, /inject-scenario)
/skills            Python drift-computation SKILL.md + supporting code for Daytona sandbox
/docs              WORKFLOW.md, PRD.md, TASKS.md, BUILD_LOG.md, DECISIONS.md
CLAUDE.md          This file
AGENTS.md          Subagent descriptions and tool-access scoping
README.md          Public-facing design decisions (written Day 7)
package.json       Root npm config; MCP server has its own package.json
tsconfig.json      TypeScript compilation for MCP server
.gitignore         Standard Node/Python excludes
```

## Tech Stack

- **Agent Runtime**: TrueForge (local mode), npm scripts
- **MCP Server**: TypeScript + `@modelcontextprotocol/sdk`
- **Sandbox**: Daytona (drift computation in Python via SKILL.md)
- **Testing**: Vitest (TypeScript), Pytest (Python)
- **Models**: Gemini 2.0 Flash (primary), Groq (fallback)

## Workflow

1. **Read WORKFLOW.md before each session** — it governs how to work on this repo.
2. **Check TASKS.md for current phase** — don't start work on tasks already marked `[x]` or skip ahead past an in-progress phase.
3. **Confirm the subphase output** — know what "done" looks like before writing code.
4. **Log as you go** — BUILD_LOG.md gets entries every time a subphase completes; DECISIONS.md logs decisions made mid-build with alternatives.
5. **Qodo reviews daily** — every PR gets reviewed by Qodo before merge (part of Best Code Quality track requirement).

## Key Principles

- **Scoped tool access is real, not simulated** — subagent tool permissions are enforced at TrueForge's permission layer, not by prompt instruction alone.
- **Approval gates are non-negotiable** — the reject path must work; destructive actions are visible but unexecuted until human sign-off.
- **GitHub connection is required** — the hero incident (incident 3) investigates this repo's own real commit history, not a synthetic one.
- **Session persistence is required** — investigation state must survive a forced reconnect mid-run.

## Running Locally

```bash
# Install dependencies
npm install

# Build MCP server
npm run build

# Start TrueForge
npm run trueforge

# Run tests (when added)
npm run test
npm run test:mcp
npm run test:skills
```

## Testing Strategy

- **MCP Server**: Vitest unit tests for tool implementations and seed data generators.
- **Python Skill**: Pytest for drift computation (PSI/KS/Chi-Square) against known distributions.
- **Integration**: End-to-end tests of incident flows through triage → investigation → remediation → approval gate.

## Adding Dependencies

All dependencies are listed in TECHSTACK.md. Before adding a new one mid-build, update TECHSTACK.md with a one-line reason — don't silently introduce new packages.

## Commit Strategy

- Atomic commits per subphase, keyed to TASKS.md phase number.
- Qodo review required before merge.
- PR title format: `[Phase X.Y] Description`.

## When to Ask for Clarification

- If a subphase's stated output isn't clear, ask before writing code.
- If a decision exists that TECHSTACK.md or PRD.md doesn't address, surface it (don't guess silently).
- If a Qodo suggestion conflicts with a DECISIONS.md decision, discuss before overriding.
