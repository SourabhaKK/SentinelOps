# TASKS.md — SentinelOps

Phases map to the locked day-by-day plan. Do not reorder phases without updating DECISIONS.md with why. Each subphase ends with a checkable output — if the output isn't there, the subphase isn't done regardless of how much code was written.

Status legend: `[ ]` not started, `[~]` in progress, `[x]` done, `[!]` blocked/cut — note why in BUILD_LOG.md when marking either of the last two.

## Phase 0 — Pre-work (before Aug 24)

- [ ] 0.1 Read TrueForge quickstart and MCP-server-registration docs end to end. Output: you can explain the agent loop (model call → tool call → sandbox → approval → session state) without looking anything up.
- [ ] 0.2 Set up Daytona account/API key.
- [ ] 0.3 Get Gemini 2.0 Flash and Groq API keys, isolated, not shared.
- [ ] 0.4 Confirm GitHub MCP server registration method (catalog entry vs. URL registration) before Day 1 so it isn't a Day 1 discovery.

## Phase 1 — Core loop (Day 1, Aug 24)

- [~] 1.1 Repo init, npm project scaffolded per TECHSTACK.md layout. Install Qodo. Open PR #1 (scaffold). Output: Qodo active on the repo before any feature code exists.
- [x] 1.2 Draft CLAUDE.md/AGENTS.md fresh against the real repo structure. Output: a file that's actually true of this repo, not adapted-in-name-only from the Allica pattern.
- [x] 1.3 TrueForge running locally, Claude (Anthropic) connected as primary model, Gemini/Groq as fallback. Output: a basic chat turn works end to end. ✅ COMPLETE — Agent responding in real-time via http://localhost:8790
- [ ] 1.4 GitHub MCP server registered, pointed at this repo. Output: agent can pull a real commit/PR from this repo's own live history.
- [x] 1.5 Telemetry MCP server built (TypeScript, `@modelcontextprotocol/sdk`), exposing `/metrics`, `/logs`, `/deploy-history`, `/inject-scenario` with static seed data. Skeleton registered, ready for Phase 1.3 integration. Output: agent can call it and get real responses back.
- **Stop condition:** if 1.4 or 1.5 isn't working cleanly by end of day, this is the point to invoke the risk-register fallback (plain OpenAI-compatible tool endpoint instead of full MCP server) rather than let it bleed into Day 2. Log the call in DECISIONS.md either way.

## Phase 2 — Incidents and sandbox skill (Day 2, Aug 25)

- [ ] 2.1 PR + Qodo checkpoint.
- [ ] 2.2 Build `/inject-scenario` and real underlying data shapes for all three incidents (not flavor text — actual distributions that produce real PSI/KS deltas).
- [ ] 2.3 Make the real bad commit on a branch in this repo for incident 3 (the hero). Output: a real, inspectable commit that the investigation subagent will root-cause against.
- [ ] 2.4 Write the drift-computation SKILL.md (Python), ported from ml-model-monitoring-drift-detection. Output: sandbox loads it and executes against live `/metrics` output, producing a real PSI/KS/Chi-Square result, not a stub.

## Phase 3 — Approval gates (Day 3, Aug 26)

- [ ] 3.1 PR + Qodo checkpoint.
- [ ] 3.2 Identify and configure the 3–4 destructive tool calls (disable endpoint, rollback, revoke key, publish report) as approval-required.
- [ ] 3.3 Build stub handlers for each — visible non-execution without sign-off is the requirement, not real destructive capability.
- [ ] 3.4 Test both the accept path and the reject path explicitly. Output: a rejected approval demonstrably halts the action.

## Phase 4 — Subagent decomposition (Day 4, Aug 27)

- [ ] 4.1 PR + Qodo checkpoint.
- [ ] 4.2 Split into triage / investigation / remediation-drafting subagents.
- [ ] 4.3 Configure scoped tool access: only investigation touches GitHub and `/deploy-history`; remediation-drafting works from investigation's findings only, no direct data-source access.
- [ ] 4.4 Run one full incident end to end through all three subagents into a proposed action sitting at the approval gate. Output: a complete triage → investigate → draft → gate loop on real data.

## Phase 5 — Persistence and hardening (Day 5, Aug 28)

- [ ] 5.1 PR + Qodo checkpoint.
- [ ] 5.2 Run all three incidents end to end.
- [ ] 5.3 Deliberate reconnect mid-run on the hero incident specifically. Output: investigation resumes correctly after a forced disconnect, not just after a clean pause.
- [ ] 5.4 Fix whatever breaks under 5.2/5.3 — this phase exists specifically to find the gap between "works once" and "works reliably in front of judges."

## Phase 6 — Stretch and rehearsal start (Day 6, Aug 29)

- [ ] 6.1 PR + Qodo checkpoint.
- [ ] 6.2 Exa/Tavily external corroboration — stretch only. Skip entirely if behind schedule; do not compress Phase 1–5 scope to fit this in.
- [ ] 6.3 Begin rehearsing the demo storyboard against the actual running system, not just reading it.

## Phase 7 — Submission (Day 7, Aug 30)

- [ ] 7.1 Final PR + Qodo checkpoint.
- [ ] 7.2 README written forward-facing as design decisions (why hybrid-target, why self-repo, why TypeScript+Python split), not as a chronological audit trail.
- [ ] 7.3 One factual Claude Code disclosure sentence added to the README.
- [ ] 7.4 30–45 minute unaided codebase walkthrough — run local setup and commands from memory, no notes.
- [ ] 7.5 Record the demo against the storyboard, hero incident only, inside the three-minute window.
- [ ] 7.6 Submit: public repo, demo video, short write-up.

## Cut list, in order, if time runs short

1. Exa/Tavily stretch (Phase 6.2) — already deprioritized, cut first without discussion.
2. Incidents 1 and 2 reduced to "built but not polished" if Phase 5 hardening runs long — the hero incident (3) is the one that must work.
3. Subagent count drops from three to two (merge remediation-drafting into investigation) only if Phase 4 isn't solid by end of Day 4 — log this in DECISIONS.md if it happens, it changes FR4.
4. Never cut: the approval gate reject path, the GitHub connection, session persistence on the hero incident. These three are what the round-1 and round-2 council audits identified as the highest-leverage, non-negotiable primitives.
