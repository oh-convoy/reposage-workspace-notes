# 04 — Decision Record

The three options the user proposed, evaluated against the goal, with the
decision and its consequences. Format: ADR (Architecture Decision Record).

The goal, restated: **highest-quality ultra-deep analysis of hundreds of GitHub
repos, in the fastest and shortest time, without degrading quality.**

---

## ADR-1 — One sandbox per persona, or multiple personas per sandbox?

**Context.** The skill defines 12 personas. A naive reading maps one persona to
one worker, and one worker to one sandbox.

**Options.**

| Option | Shape | Quota | Quality | Speed |
|---|---|---|---|---|
| A. One sandbox per persona | 12 sandboxes = 12 personas | 12 | **Low** (fragmented) | Slow to fill a pool |
| B. Multiple personas per sandbox (lenses) | 1 conversation wears all 12 lenses | ~0 extra | **High** (coherent) | Fast |
| C. Persona groups as children of a lead | 5 children per large repo | ~0 extra | **Highest** (independent) | Fast |

**Analysis.**

- The skill's own method (`05-squad-orchestration.md` §3–4) requires the personas
  to **cross-examine each other** and reconcile. That cross-examination needs one
  mind holding the whole repository. Option A *destroys* it: 12 disconnected
  fragments with no reconciler.
- Sandboxes are the scarce resource (20). Spending them on *roles* rather than
  *repos* caps the org at 12 repos in flight instead of 20 sandboxes × 4 repos.
- Conversations are effectively free (0 quota). The depth budget is
  conversations, not sandboxes.

**Decision.** **Option B as the default; Option C for large/critical repos.**
Personas are *lenses* inside an analyzer conversation, or *children* of a squad
lead — never a sandbox each.

**Consequences.**

- Positive: 20 sandboxes cover 80+ repos per wave; reasoning stays coherent;
  cross-examination is preserved.
- Negative: a single analyzer must hold all 12 personas in context — mitigated by
  the skill documents being references, not inlined text, and by promoting big
  repos to Option C.

---

## ADR-2 — Full org clone per sandbox, or one clone distributed by reference?

**Context.** Each analyzer needs the repository. The naive approach clones the
whole organization into every sandbox.

**Options.**

| Option | Shape | Cost | Merge |
|---|---|---|---|
| A. Full org clone per sandbox | 20 × org size | 20× storage/clone | hard (20 divergent clones) |
| B. One clone, bundles distributed | 1 × org size + bundles | 1× storage | easy (results merge) |
| C. Network clone per worker from origin | 1 repo per worker | network-bound | easy |

**Analysis.**

- Option A multiplies clone time by 20 and disk by 20 for **zero** quality gain.
  The analysis only needs *one* repo per analyzer.
- Option B clones once (into bundles), and a worker's `git clone <bundle>` is
  local and fast.
- Option C is viable if the network is fast, but the mirror approach removes the
  network dependency and lets workers start in seconds.

**Decision.** **Option B.** Clone the organization **once** into `repos/*.bundle`
in the artifacts repo; workers fetch a single bundle.

**Consequences.**

- Positive: minimal storage; fast starts; results merge cleanly (one branch per
  repo).
- Negative: the prep phase must build bundles before wave 1 (a fixed, one-time
  cost).

---

## ADR-3 — Convert each sandbox into an MCP server, or not?

**Context.** A sandbox can serve MCP (`fastmcp` is installed). It is tempting to
make every persona-sandbox an MCP server and drive them from one orchestrator.

**Options.**

| Option | Shape | Latency | Quality | Complexity |
|---|---|---|---|---|
| A. Every sandbox an MCP server | N MCP endpoints | +1 hop per call | no gain | high |
| B. A few capability MCP servers | e.g. code-graph, fetch | +1 hop where it pays | + for shared heavy tools | medium |
| C. No MCP for personas; lenses/children | in-process | none | high | low |

**Analysis.**

- For **personas**, MCP adds a network hop, a state-sync burden (the specialist's
  conversation state must be fetched), and a new failure mode (server down), for
  **no quality gain**: the persona is just a prompt + skill, which is cheaper to
  load in-process.
- MCP **does** pay for a small number of **reusable heavy capabilities** shared
  across many repos: a code-graph builder, a dependency scanner, a fetch server.
  There, standing it up once and calling it many times saves N× compute.
- The orchestration plane (scheduling, collecting) is better served by the
  platform's own conversation API than by wrapping every sandbox as a tool.

**Decision.** **Option C for personas; Option B for a few shared heavy
capabilities.** Do not convert persona sandboxes into MCP servers. See
[`06-mcp-evaluation.md`](06-mcp-evaluation.md) for the full evaluation.

**Consequences.**

- Positive: fewer moving parts; no extra hop; the persona logic stays where it is
  cheapest (in the conversation).
- Negative: a genuinely heavy capability (e.g. a repo-wide static analysis) must
  be explicitly stood up as a server — which is the right place for the
  complexity anyway.

---

## ADR-4 — Where does the org-level synthesis happen?

**Context.** Cross-repo relationships are invisible from inside a single repo.

**Options.**

| Option | Shape | Quality |
|---|---|---|
| A. Each repo writes its own org fragments | no global view | Low |
| B. One synthesizer conversation reads all results | global view | High |

**Decision.** **Option B.** One org synthesizer conversation, fed by every
`repo-result.json`.

**Consequences.** Positive: the fragmentation findings (the oh-convoy story) are
only visible here. Negative: the synthesizer must not re-read raw repos (it works
from results), keeping its context bounded.

---

## ADR-5 — Speed vs quality: how to get both

**Context.** The goal demands *both* maximum speed and *maximum* quality.

**Decision.** Decouple them:

- **Speed** comes from **parallelism at the repo level** (20 sandboxes × 4 repos)
  and **reuse** (paused sandboxes, warm caches) — not from cutting analysis
  depth.
- **Quality** comes from the **gates** (Spec 08), the **cross-examination** (lens
  mode) or **independence** (child mode), and the **evidence standard**.
- Depth is **tiered by criticality**: small repos get one coherent pass; critical
  repos get the full adversarial fan-out.

**Consequences.** Speed and quality are orthogonal knobs; the design turns the
speed knob with parallelism and the quality knob with tiering and gates, so
neither degrades the other.

---

## Summary of decisions

| ADR | Decision |
|---|---|
| 1 | Personas are **lenses** (default) or **children** (large repos), never a sandbox each |
| 2 | **One clone**, distributed as bundles — not a full org clone per sandbox |
| 3 | **No MCP for personas**; MCP only for a few shared heavy capabilities |
| 4 | **One org synthesizer** for cross-repo coherence |
| 5 | Speed = repo-level parallelism + reuse; quality = gates + tiering + evidence |
