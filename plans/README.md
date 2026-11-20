# Corporate Plan — Squads, Personas, MCP Servers

A complete organizational blueprint for a software-and-media corporation covering
**software development, AI, digital marketing, social media, multimedia & design,
and video/audio production**, plus corporate shared services.

| Folder | Contents |
|---|---|
| [`squads/`](squads/corporation-squads.md) | The 39-squad catalogue (divisions, missions, headcount, persona-doc map) |
| [`personas/`](personas/README.md) | 39 documents, one per squad, each with a numbered roster of named personas |
| [`mcp/`](mcp/README.md) | The MCP server catalogue: 15 categories, 178 servers, plus the shared-gateway model |

## At a glance

| Metric | Value |
|---|---|
| Divisions | 7 |
| Squads | 39 |
| Personas | 236 |
| MCP server categories | 15 |
| MCP servers catalogued | 178 |
| Distinct persona countries | 41 |
| Gender mix | 114 Female · 102 Male · 20 Non-binary |

## How the MCP servers are deployed

The 178 servers are not all installed on every sandbox. They are split into two
planes:

- **Tools plane** — external, stateless, credential-bearing servers (GitHub,
  Slack, Jira, Snowflake, Figma…). These are fronted by **one shared MCP gateway
  sandbox** that holds all credentials and exposes a single namespaced endpoint.
- **Data plane** — servers bound to the local repo/machine (filesystem,
  code-graph, per-repo index). These run **locally** in each sandbox as stdio
  servers.

See [`mcp/M15-gateway-aggregation.md`](mcp/M15-gateway-aggregation.md) for the
gateway servers and the full plan in
[`../platform-all-hands/design/08-mcp-gateway-plan.md`](../platform-all-hands/design/08-mcp-gateway-plan.md).

## How this was produced — the parallel pattern

The mission was distributed across the platform using the **workshop pattern**
from the OpenHands sandbox model: one orchestrator conversation (this one) fanning
out **child conversations** on the local agent-server, each producing one document
in parallel.

```
        ┌────────────────────────────┐
        │ ORCHESTRATOR (this conv.)  │
        │  builds units → fans out   │
        └──────────────┬─────────────┘
                       │  child conversations (N at a time)
     ┌─────────┬───────┼───────┬─────────┬─────────┐
     ▼         ▼       ▼       ▼         ▼         ▼
  S01 doc   S02 doc  S03 doc  ...      M13 doc   M14 doc
     └─────────┴───────┴───────┴─────────┴─────────┘
                       │
              collect → validate → assemble
```

**Pattern chosen:** *fan-out over child conversations, bounded by a semaphore.*
This is the optimal pattern for this mission because:

- Each document is **independent** (no cross-writes) → perfectly parallelizable.
- The work is **LLM/IO-bound** → a modest concurrency fits the 4-CPU / 16-GiB box
  without oversubscription (the documented stall risk).
- One **shared workspace** (`isolation: shared`) lets children write straight into
  the target folders — no merge step needed.
- Deterministic assembly afterwards guarantees **consistent structure** across all
  53 documents.

### Why not the alternatives

| Alternative | Verdict | Reason |
|---|---|---|
| One giant single-conversation generation | Rejected | Context blow-up; serial; slow |
| One sandbox per document | Rejected | Wastes the sandbox budget on trivial units |
| Sandboxes-as-MCP servers | Rejected | Adds hops/state-sync for no gain (see design/06) |
| **Fan-out child conversations** | **Chosen** | Fast, isolated, bounded, one shared workspace |

## Execution and measurement

| Run | Units | Concurrency | Wall clock | Avg unit | Success |
|---|---|---|---|---|---|
| Persona documents | 39 | 6 | **262.6 s** | 35.1 s | 39/39 |
| MCP catalogue documents | 14 | 5 | **63.0 s** | ~24 s | 14/14 |
| **Total** | **53** | — | **≈ 326 s** | — | **53/53** |

- A 2-unit pilot ran first (48.9 s) to validate the loop before the full fan-out.
- Total documents: **53** produced in **≈ 5.4 minutes** wall-clock.
- Serial equivalent (sum of unit times): ≈ 39×35 + 14×24 ≈ **1 700 s ≈ 28 min**.
  So the fan-out achieved a **≈ 5.2× speed-up** at concurrency 6, with no quality
  loss.

## Quality gates (all passed)

| Gate | Check | Result |
|---|---|---|
| G1 Structure | Every doc has the required sections and numbered tables | ✅ |
| G2 Roster size | Every squad doc has exactly its target headcount | ✅ 236/236 |
| G3 Content depth | ≥4 skills and ≥3 responsibilities per persona | ✅ 0 violations |
| G4 Diversity | Mixed genders; ≥3 countries per squad | ✅ 41 countries |
| G5 Name integrity | Real full names; no duplicates within or across squads | ✅ 0 duplicates |
| G6 MCP completeness | ≥8 real servers per category with all 7 columns | ✅ 168 servers |
| G7 Link integrity | All relative links resolve | ✅ |

## Diversity standard

Every squad mixes genders and draws people from at least three countries; names
are real and culture-appropriate. Company-wide: **41 countries** across all
continents, **114 women / 102 men / 20 non-binary** personas, spanning
early-career to principal level.

## Reproduce

```bash
cd /workspace/plans/_build
python3 build_units.py && python3 build_units_mcp.py          # build unit lists
python3 fanout.py --units units_personas.json --concurrency 6 --results results_personas.json
python3 fanout.py --units units_mcp.json      --concurrency 5 --results results_mcp.json
```

`fanout.py` creates one child conversation per unit on the local agent-server
(`http://127.0.0.1:60000`, session-key auth), waits for each to finish, and
records timing and status.

## Folder map

```
plans/
  README.md                 ← this file
  squads/corporation-squads.md   ← the 39-squad catalogue
  personas/
    README.md               ← index + diversity summary
    _TEMPLATE.md            ← the canonical document template
    S01-*.md … S39-*.md     ← 39 squad documents
  mcp/
    README.md               ← consolidated 168-server catalogue
    M01-*.md … M14-*.md     ← 14 category documents
  _build/                   ← the generator (units, fan-out driver, results)
```
