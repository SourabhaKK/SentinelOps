# WORKFLOW.md — how to run a session on this project

This file governs how Claude Code operates on this repo. Read this, PRD.md, TASKS.md, and TECHSTACK.md before touching code in a new session. DECISIONS.md and BUILD_LOG.md are write targets during the session, not required reading beforehand — check them only if picking up mid-phase and needing the last state.

## Before writing any code

1. Check TASKS.md for the current phase and subphase status. Don't start a subphase marked `[x]`. Don't skip ahead to a later phase while an earlier one is `[~]` unless TASKS.md's cut list explicitly allows it.
2. Confirm the subphase's stated output before starting — know what "done" looks like before writing toward it.
3. If a decision is needed that TECHSTACK.md or PRD.md doesn't already answer, stop and surface it rather than picking silently. Small implementation details don't need this; anything that changes what gets built, what tool gets used, or what gets demoed does.

## The decision-confirmation process

Before implementing any phase or subphase that involves a real choice (not just following an already-locked decision), explain: what you're about to do, why, and what the rejected alternative was. This mirrors the process already used successfully on the Allica take-home — the goal is that every choice in this repo can be defended in a follow-up conversation, not just that the code works.

Do not re-litigate decisions already locked in TECHSTACK.md, PRD.md, or DECISIONS.md. "Why TypeScript and not Python for the MCP server" is answered — don't re-ask it. A genuinely new decision inside a subphase (e.g., "how exactly should the drift-computation SKILL.md format its output for the agent to consume") does need this process.

## Logging as you go, not after

**BUILD_LOG.md** gets an entry every time a subphase in TASKS.md moves from `[ ]`/`[~]` to `[x]` or `[!]`. Log what was actually built, what broke, what the fix was — written like a real build log, not a status report. Keep entries factual and dated; this is a record, not marketing copy (that's what the README is for, separately, on Day 7). If Qodo's PR summary already captures the diff-level "what changed," don't duplicate it here — reference it and spend the entry on what Qodo can't see: why the subphase was approached that way, what broke during testing, what the fix actually was.

**DECISIONS.md** gets an entry any time a real choice gets made mid-build that wasn't already locked — including cuts (see TASKS.md's cut list), scope changes, and anything where a plausible alternative existed and got rejected. Log the decision, the alternative, and the one-line reason. Do not log decisions that were already made in TECHSTACK.md/PRD.md — only new ones. This includes overriding a Qodo suggestion: if Qodo flags something in a PR review and the call is made to reject or defer it rather than fix it, that's a real decision with a real alternative on the table, and it belongs here, not just resolved silently in the PR thread.

Update both files in the same session as the work, not retroactively at the end of the week. A build log written from memory on Day 7 is worth less than one written as it happens, and it's also exactly the kind of thing the round-3 council audit flagged — the README should read as designed, but this internal record should read as it actually happened, because that's the version useful for an interview conversation later.

## Qodo's role versus these docs

Qodo reviews diffs — code quality, bugs, security issues in what a specific PR changed. It has no visibility into why the project is scoped this way, which primitives are non-negotiable, or what got rejected and why. It's a code reviewer, not a project record. Don't treat a clean Qodo review as a substitute for logging a decision or a build-log entry, and don't treat these docs as a substitute for Qodo's review — they operate at different layers and both are needed.

## Stop conditions

Phase 1 (Day 1) has an explicit stop condition in TASKS.md: if the custom MCP server or GitHub connection isn't working cleanly by end of day, invoke the documented fallback rather than pushing forward on a broken foundation. Don't silently work around a broken core loop — surface it, log the decision, then proceed with the fallback.

If a session runs out of time mid-subphase, leave TASKS.md accurately marked `[~]` with a note on exactly where it stopped, so the next session doesn't have to rediscover state by reading code.

## What not to do

Don't add dependencies, frameworks, or infrastructure not listed in TECHSTACK.md without flagging it first — see TECHSTACK.md's own instruction on this. Don't write Docker or CI configuration — explicitly out of scope, see PRD.md non-goals. Don't defer Qodo PR review to "catch up later" — it's a daily habit per TASKS.md, and falling behind on it risks the Best Code Quality track by the hackathon's own stated rule.

Don't write the public README as a chronological narrative of fixes and audits. That framing belongs in DECISIONS.md and BUILD_LOG.md, which are internal working documents. The README is Day 7 work, written forward-facing, and is covered separately in TASKS.md Phase 7.
