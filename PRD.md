# PRD.md — SentinelOps

## What this is

An agent that sits on-call for a deployed ML system, built on TrueForge for The Agent Harness Hackathon (WeMakeDevs × TrueFoundry, Aug 24–30 2026). It receives an incident alert, investigates using real tools, runs statistical checks in a sandbox, drafts a remediation plan, and stops before doing anything irreversible until a human signs off.

## Who this is for

The immediate audience is hackathon judges scoring against six criteria: impact, creativity/originality, technical excellence, use of sponsor tools, control and safety, presentation. The secondary audience is anyone reading the repo afterward as a portfolio artifact — a hiring engineer, an interviewer, future-you.

## Prize target

Primary: Best Use of TrueForge (NVIDIA DGX Spark, $5,000). Secondary, zero marginal cost: Best Code Quality (Mac Mini, $1,000) via Qodo PR discipline. Not pursued: Best UI. Blog post and social tracks covered incidentally, no dedicated budget.

Realistic framing: low-to-moderate odds on winning the primary track outright (solo, against teams of up to four, on a tool five days old at hackathon start). The more achievable target is landing in the credible top tier that gets the "job interview at TrueFoundry" callout — awarded to strong projects generally, not gated behind a track win. Every requirement below is aimed at that bar as much as at first place.

## Functional requirements

**FR1 — Alert intake and triage.** The agent receives an incident alert (one of three canned scenarios) and a triage subagent classifies severity and type from raw telemetry. Triage has no access to `/deploy-history` or GitHub.

**FR2 — Investigation.** An investigation subagent correlates evidence across `/logs`, `/metrics`, `/deploy-history`, the GitHub connection, and sandbox statistical output. Only this subagent holds GitHub and `/deploy-history` access.

**FR3 — Sandboxed statistical analysis.** A SKILL.md loaded into the Daytona sandbox runs PSI/KS/Chi-Square drift computation over live `/metrics` data, invoked by the agent itself, not pre-computed.

**FR4 — Remediation drafting.** A remediation-drafting subagent proposes options with explicit tradeoffs (rollback vs. patch vs. monitor-only), without executing anything or holding direct access to `/deploy-history` or GitHub — it works from the investigation subagent's findings only.

**FR5 — Approval gate.** Destructive actions (disable endpoint, rollback, revoke key, publish report) require explicit human sign-off before execution. The orchestrating agent owns this gate; subagents cannot bypass it. Must demonstrably handle both approval and rejection.

**FR6 — Session persistence.** An investigation's state survives a process restart or reconnect and resumes correctly.

**FR7 — Three canned incidents.**
1. Gradual distribution drift — fully synthetic, PSI/KS-detectable, secondary demo beat.
2. Adversarial/jailbreak-shaped input burst — fully synthetic, built and tested, not demoed live.
3. Unauthorized/malformed model version in deploy history, root-caused against a real commit in the SentinelOps repo itself via the GitHub MCP connection — the hero incident, carries the "connected, not mocked" requirement for the whole submission.

**FR8 — Qodo-reviewed PR trail.** Every day of the build produces at least one PR reviewed by Qodo before merge — a daily habit, not a day-1 checkbox.

**FR9 — Documentation.** README written forward-facing as design decisions, not a chronological audit trail. One factual sentence disclosing Claude Code as the implementation tool. CLAUDE.md/AGENTS.md written fresh against this repo's actual structure.

## Non-functional requirements

- Demo fits inside roughly three minutes, per the hackathon's stated constraint, storyboarded around one hero incident (FR7.3) — see the day-7 task and the plan's demo storyboard section for the beat-by-beat breakdown.
- Repo must be public, cloneable, and runnable by a stranger without additional context beyond the README.
- No keys, tokens, or personal data committed to the repo or visible in the demo video.
- Subagent tool-access scoping must be real, not simulated by prompt instruction alone — a judge is explicitly primed to check for this.

## Explicit non-goals

- No custom UI beyond TrueForge's stock chat interface.
- No Docker, no CI pipeline — nothing here gets deployed.
- No production-grade error handling beyond what's needed for a reliable scripted demo — this is a hackathon submission, not a production service, and over-engineering here is scope creep against a six-day solo build.
- Exa/Tavily external corroboration is optional stretch, cuttable without damaging the submission.

## Success criteria

Minimum viable submission: FR1–FR6 working end to end on the hero incident (FR7.3) alone, demoed within the three-minute constraint, README and disclosure in place. Full submission: all three incidents built (even if only one is demoed), Qodo trail intact across all seven days, CLAUDE.md/AGENTS.md accurate and current.
