# Optimal Squad Orchestration — Design Package

Architecture, design, and specifications for the question:

> **How do we run the ultra-deep repository analysis at the highest quality and
> the highest speed, over hundreds of GitHub repositories, without degrading
> quality?**

The analysis method is the squad of expert personas defined in
`_ai-context/organized/skills/repo-deep-analysis-skills/` (12 personas plus the
core method). This package turns that method into an executable, parallel
architecture on the OpenHands platform.

## The answer in one paragraph

**One sandbox is not one persona, and one sandbox is not one repo.** A sandbox is
a *workshop* that hosts many agent conversations on one machine for one quota
unit. The optimal design is a **three-tier, two-dimensional matrix**:

- **Tier 1 — Repo Analyzers (the width):** one *repo* per conversation. The 12
  personas are **lenses inside one analyzer conversation**, not 12 sandboxes. This
  is the single biggest quality win: analysis must be one coherent reasoning pass
  over the whole repository, not twelve disconnected fragments.
- **Tier 2 — Squad Leads (the depth):** for large or critical repos, a lead
  fans out **one child conversation per persona** (worktree-isolated), each
  returning a structured finding set that the lead reconciles.
- **Tier 3 — Org Synthesizer (the coherence):** one conversation that reads every
  repo's result and produces the organization-level analysis.

Specialist personas are *reused* across all repos by being invoked as lenses or
children, never by standing up a sandbox per persona. **Do not convert sandboxes
into MCP servers for the analysis path** — that is a control-plane optimization
for interactive use, and it adds a network hop, a state-sync burden, and a
failure mode for no quality gain. MCP is reserved for a small number of
*reusable capability* servers (fetch, code-graph), not for personas.

**One clone per repo, one worktree per persona**, a **warm base image**, and
**results shipped as artifacts to one central repo** — never a full org clone per
sandbox.

## Why this shape (the constraints that force it)

| Constraint | Value | Consequence |
|---|---|---|
| Sandboxes available | **20** | The width budget; the unit of parallel *repos* |
| Sandbox quota | **20 new machines/day** (verified: `used_today: 0`) | Conversations are effectively free; **reuse** sandboxes |
| Box size | **4 CPU / ~16 GiB** | 3–5 *heavy* conversations per box; I/O-bound work tolerates more |
| Conversations per box | **unbounded (0 quota)** | The depth budget; fan out personas freely |
| Failure mode | Blocking commands serialise on the shared shell | Never let analyzers run long blocking loops; isolate filesystems |
| Cost driver | Tokens, not sandboxes | Depth is cheap in quota, expensive in tokens; budget it |

## Documents in this package

| # | Document | What it covers |
|---|---|---|
| 00 | [`00-architecture.md`](00-architecture.md) | The three-tier architecture, the two axes (repos × personas), topology, data flow |
| 01 | [`01-squad-model.md`](01-squad-model.md) | How the 12 personas map onto sandboxes and conversations; the lens/child/specialist modes |
| 02 | [`02-execution-plan.md`](02-execution-plan.md) | The concrete run plan: waves, scheduling, concurrency, warm base, quota math |
| 03 | [`03-specs/`](03-specs/) | Granular specifications: contracts, schemas, briefs, prompts, runbooks |
| 04 | [`04-decision-record.md`](04-decision-record.md) | The three options the user proposed, evaluated and decided (ADRs) |
| 05 | [`05-quality-model.md`](05-quality-model.md) | How quality is protected at speed: gates, dedup, reconciliation, evidence |
| 06 | [`06-mcp-evaluation.md`](06-mcp-evaluation.md) | Sandbox-as-MCP-server: when it helps, when it does not |
| 07 | [`07-risks.md`](07-risks.md) | Risks, failure modes, and mitigations |
| 08 | [`08-mcp-gateway-plan.md`](08-mcp-gateway-plan.md) | The MCP gateway: one shared endpoint for external tools + local data-plane servers |

## Evidence base

This design is grounded in the `oh-convoy` clone (analysed in the `_analysis`
repo), specifically:

- `all-hands-dev/documentation/03-guides/08-sandboxes-as-workers.md` — the
  sandbox-as-workshop model, worktrees, specialists-as-MCP, hub-and-spoke.
- `all-hands-dev/documentation/04-reports/01-incident-parallel-agent-stall.md` —
  the stall incident and its root cause (shared-shell serialisation).
- `all-hands-dev/documentation/04-reports/04-forking-and-the-daily-quota.md` —
  the quota is per sandbox, not per conversation.
- `hellofleet-experiment/` — measured cost/time of three topologies.
- `Convoy-OpenHands-Orchestration/codebase/convoy/{cloud,inventory,orchestrator}.py`
  — the platform API patterns (provision, inventory, reuse, bounded concurrency).

Live values verified against `https://app.all-hands.dev` on 2026-11-18:
`daily_limit: 20, used_today: 0, remaining: 20`; 21 sandboxes, 20 conversations
(see `../inventory/`).
