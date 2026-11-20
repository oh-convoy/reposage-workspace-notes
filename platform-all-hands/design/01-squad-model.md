# 01 — Squad Model

How the 12 expert personas map onto the platform's sandboxes and conversations.

## 1. The personas (from the skill)

Defined in `_ai-context/organized/skills/repo-deep-analysis-skills/personas/`:

| # | Persona | Lens focus |
|---|---|---|
| 01 | Business Analyst | Problem, users, value, rules, scope |
| 02 | Domain Expert | Does the solution match the field |
| 03 | Principal Architect | Structure, boundaries, patterns |
| 04 | Senior Software Engineer | Code quality, correctness |
| 05 | Platform / DevOps / SRE | Build, deploy, operate |
| 06 | Security Engineer | AuthN/AuthZ, secrets, surface |
| 07 | Data / Integration Engineer | Data models, flows, contracts |
| 08 | QA / Test Engineer | Tests, coverage, gates |
| 09 | Technical Writer | Docs accuracy, completeness |
| 10 | Compliance / Risk | Licenses, regulation, governance |
| 11 | Engineering Historian | Evolution, bus factor |
| 12 | Cost / FinOps | Cost drivers, waste |

Plus the core method: overview, method, evidence, deliverable, repository-types,
squad-orchestration.

## 2. The three invocation modes

A persona is never a *place*. It is an *invocation*. There are exactly three
ways to invoke one, and each has a cost and a quality profile.

| Mode | Shape | Quota | Quality | Use when |
|---|---|---|---|---|
| **Lens** | the analyzer *wears* the persona for a section of one pass | 0 | High (cross-examination inline) | default; small/medium repos |
| **Child** | a separate conversation runs one persona in isolation | 0 | Highest (independent, adversarial) | large/critical repos; true independence needed |
| **Specialist** | a persona lives in its own sandbox, called via MCP or remote conversation | 1 (once) | High, reusable | many repos need the *same* heavy tool (e.g. code-graph) |

**Decision rule.**

```
if repo is small/medium and not critical:
    use LENSES  (one analyzer conversation, 12 lenses)
elif repo is large or critical:
    use CHILDREN (squad lead + one child per persona or persona-group)
if the same heavy capability is needed by many repos:
    stand up a SPECIALIST sandbox once and call it  (see 06-mcp-evaluation.md)
```

## 3. Persona grouping (for child fan-out)

Twelve children per lead is too many for a 4-CPU box (the stall incident). Group
personas that share a reading of the same artifacts, so each child is one
coherent pass:

| Group | Personas | Reads mainly |
|---|---|---|
| **G1 — Intent** | Business Analyst, Domain Expert, Compliance/Risk | docs, purpose, rules, licenses |
| **G2 — Structure** | Principal Architect, Data/Integration | layout, interfaces, schemas |
| **G3 — Implementation** | Senior Software Engineer, QA/Test | code, tests |
| **G4 — Operations** | Platform/DevOps/SRE, Security, Cost/FinOps | build, deploy, config, infra |
| **G5 — Knowledge** | Technical Writer, Engineering Historian | docs, history |

So a **squad lead fans out 5 children**, not 12. Each child returns a structured
finding set; the lead reconciles them (the squad-challenge step). This keeps the
box within its 3–5 conversation budget while preserving independence.

> **Why grouping is not a quality loss.** The personas inside a group are
> complementary (they read the same artifacts and rarely conflict), while the
> *groups* are the ones that genuinely challenge each other (intent vs structure
> vs implementation vs operations). The cross-examination that matters happens
> **between groups**, and the lead runs it.

## 4. Mapping to the platform

### 4.1 A small/medium repo (lens mode)

```
SANDBOX  (workshop)
 ├─ analyzer(repoA)   ← 12 lenses in one pass → repo-result.json + *.md
 ├─ analyzer(repoB)
 └─ analyzer(repoC)
```
One conversation per repo. No children. Zero extra quota.

### 4.2 A large/critical repo (child mode)

```
SANDBOX  (workshop)
 └─ squad-lead(repoL)
     ├─ child G1 (worktree) → findings-intent.json
     ├─ child G2 (worktree) → findings-structure.json
     ├─ child G3 (worktree) → findings-impl.json
     ├─ child G4 (worktree) → findings-ops.json
     └─ child G5 (worktree) → findings-knowledge.json
     → lead reconciles → repo-result.json + *.md
```

### 4.3 The whole organization

```
ORG SYNTHESIZER (1 conversation, its own sandbox)
 reads results/*/repo-result.json
 writes org/*.md  (overview, relationships, risks, glossary, business-view)
```

## 5. Persona-to-artifact contract

Every persona invocation — lens or child — returns the **same structured shape**,
so results are machine-mergeable regardless of mode. See
[`03-specs/02-repo-result-schema.md`](03-specs/02-repo-result-schema.md).

```jsonc
{
  "persona": "security-engineer",
  "findings": [
    { "id": "SEC-1", "claim": "...", "label": "fact|inference|prediction|unknown",
      "severity": "critical|high|medium|low", "confidence": "high|medium|low",
      "evidence": [{"path": "...", "ref": "..."}], "detail": "..." }
  ],
  "strengths": [ ... ],
  "open_questions": [ ... ]
}
```

The lead (or the analyzer, in lens mode) concatenates the per-persona sets into
the Repo Result and runs reconciliation.

## 6. Reuse across repos

The personas are **skills**, and skills are cheap to load. Reuse them by:

- **Lens mode:** the analyzer loads all persona documents once at start.
- **Child mode:** each child loads only its group's persona documents (narrower
  context, faster, better focus).
- **Specialist mode:** a heavy capability (e.g. a static-analysis or code-graph
  server) is stood up **once** and called by every repo that needs it.

This is why "one sandbox per persona" is the wrong reading: personas are the
*reusable intellectual capital*; sandboxes are the *compute*. You reuse the
former across the latter.

## 7. Worked example — 200 repos

| Step | Assignment | Count |
|---|---|---|
| Warm base | one sandbox bakes the base + bundles | 1 |
| Wave 1 | 20 sandboxes × 4 analyzers = 80 repos | 20 sandboxes |
| Wave 2 | 20 sandboxes × 4 analyzers = 80 repos | reuse same 20 |
| Wave 3 | 20 sandboxes × 4 analyzers = 40 repos | reuse same 20 |
| Large/critical | 5 of the above run as squad-leads with 5 children each | same sandboxes |
| Synthesis | 1 org synthesizer | 1 conversation |

**Quota used:** 20 new sandboxes (day 1) + 1 synthesizer = **21**, under the
20/day limit if the synthesizer reuses a wave sandbox. Waves 2–3 cost **0 quota**
because they reuse the paused sandboxes.

## 8. Anti-patterns

| Anti-pattern | Why it fails |
|---|---|
| Sandbox per persona | Wastes the 20-pool on roles; fragments reasoning; loses cross-examination |
| 12 children per lead | Oversubscribes 4 CPU; the stall incident repeats |
| Persona-as-MCP for every repo | Network hop + state sync + failure mode; no quality gain |
| One conversation for all repos | Context blow-up; no parallelism |
| Full clone per sandbox | N× storage/clone; harder merges |
| Blocking loops in analyzers | Serialise on the shared shell → stall |
