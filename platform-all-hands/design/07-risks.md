# 07 — Risks and Mitigations

Every design choice has a failure mode. This document lists them with the
detection signal and the mitigation, so the plan is robust, not optimistic.

## 1. Risk register

| # | Risk | Likelihood | Impact | Detection | Mitigation |
|---|---|---|---|---|---|
| R1 | **Analyzer stall** — blocking commands serialise on the shared shell | Medium | High | no progress + high CPU on one PID | brief forbids blocking loops; kill by PID; capacity guard; per-analyzer scratch |
| R2 | **Oversubscription** — too many conversations per 4-CPU box | Medium | Medium | `loadavg` high, RAM low | cap 3–5 analyzers/sandbox; capacity guard before start |
| R3 | **Context blow-up** — one repo exceeds the model's context | Medium | High | analyzer truncates or loops | tier large repos to squad lead; split by subdirectory |
| R4 | **Fragmentation** — personas produce disconnected fragments | Medium | High | findings contradict, no reconciliation | lens mode default; lead reconciliation; synthesizer |
| R5 | **Secret leak** — a session key or token lands in an artifact | Low | Critical | Gate G3 | regex scan blocks publish; report location only |
| R6 | **Quota exhaustion** — need > 20 new sandboxes in a day | Medium | Medium | `/api/quota/status` `remaining == 0` | reuse paused sandboxes; wait for reset; never exceed pool |
| R7 | **Clone storm** — every worker clones the org | Low | Medium | network/disk spike at wave start | one clone → bundles; workers fetch a bundle |
| R8 | **Merge conflicts** — many workers write the same files | Low | Medium | conflict on integration | one branch per repo; results are small and disjoint |
| R9 | **LLM rate limits** | Medium | Medium | 429s | bounded concurrency; backoff; reduce `P` |
| R10 | **Gate failure loop** — a repo fails gates repeatedly | Low | Low | `attempts` > 2 | escalate to squad lead / human review |
| R11 | **Unverified core claim** — the analysis asserts what it did not check | Medium | High | Gate G2 | evidence labels; "unknown" + resolution path |
| R12 | **Sandbox death** mid-wave | Low | Medium | health check fails | re-provision slot; replay repos |
| R13 | **Non-determinism** — two runs disagree | Medium | Low | diff between runs | pin revisions; deterministic synthesizer |
| R14 | **Persona drift** — personas applied inconsistently across repos | Medium | Medium | schema + glossary checks | one schema; one glossary; lens checklist |

## 2. Deep dives on the top risks

### R1 — Analyzer stall (the known incident)

The org already hit this: 8 sub-agents stalled with the machine idle. Root cause
was blocking, unbounded agent loops serialising on one shell.

**Mitigations, layered:**

1. **Brief rule:** "No long blocking commands. No agent loops, servers, or long
   builds." (Spec 01)
2. **Per-analyzer isolation:** each analyzer gets its own scratch dir (worktree),
   so a runaway process does not starve siblings.
3. **Capacity guard:** never start more conversations than the box can hold
   (Spec 05 §5).
4. **Kill by PID:** the orchestrator detects a hung PID and kills it specifically
   (never `pkill -f python`).
5. **Retry with a stricter brief** if the same repo stalls twice.

### R3 — Context blow-up

A very large repo cannot be analyzed in one pass without truncation, and
truncation silently degrades quality.

**Mitigations:** promote to a squad lead (Spec 01 size variants); split the repo by
top-level directory, one child per directory; have the lead merge. The brief for a
large repo explicitly says "produce a preliminary pass and flag for promotion".

### R4 — Fragmentation

The quality risk that most easily hides. A set of clean-looking but disconnected
findings is worse than a messy coherent one.

**Mitigations:** the lens model (one mind per repo); the lead reconciliation for
child-mode repos; the synthesizer for cross-repo coherence; the cross-examination
step in the skill's method.

### R5 — Secret leak

The platform hands out `session_api_key`s; the inventory holds them; an analyzer
might quote one.

**Mitigations:** the brief forbids copying secrets; Gate G3 scans every artifact;
the inventory JSON is chmod `0600` and lives outside the artifacts repo; findings
report location and type only.

## 3. Assumptions (and what invalidates them)

| Assumption | If false |
|---|---|
| The quota is per sandbox, not per conversation | The math collapses; fall back to ≤20 repos/run |
| 3–5 analyzers fit on a 4-CPU box for I/O-bound work | Reduce to 1–2; waves take longer |
| Bundles are fast to fetch locally | Revert to network clones; accept the latency |
| The model can hold one repo's analysis | Promote more repos to squad leads |
| Gates are cheap enough to run inline | Run gates at the end of each wave instead |

## 4. Kill switches

| Switch | Action |
|---|---|
| Quota exhausted | pause all; wait for reset |
| Rate limit sustained | halve `analyzers_per_sandbox` |
| Two consecutive wave failures | halt; human review |
| Secret detected | block publish; redact; audit the source |
| A sandbox unhealthy twice | re-provision; quarantine the slot |

## 5. What we deliberately accept

| Accepted risk | Why |
|---|---|
| Token cost scales with depth | Quality requires reading; cost is the price |
| Critical repos are slow | Depth is concentrated where errors are costly |
| Some unknowns remain | Honest "unknown + resolution path" beats invented fact |
| Manual review for critical disagreements | Some judgements should not be automated |

## 6. Monitoring

| Metric | Alert if |
|---|---|
| Repos `running` with no progress > 2× T | stall suspected |
| Sandbox `loadavg` > 0.8 × CPU | oversubscription |
| Quota `remaining` < 2 | near exhaustion |
| Gate failures per wave | > 10% |
| Secret hits | > 0 |
| Repos without results at wave end | > 0 |
