# 06 — MCP Evaluation

Should we convert each sandbox into an MCP server and drive the analysis from one
sandbox? This document evaluates the option honestly and states where MCP helps
and where it does not.

## 1. What the option proposes

The user's third proposal:

> Convert each sandbox to act as an MCP server and use them from one sandbox to
> analyze all repos.

Concretely: stand up N sandboxes, each exposing its persona/agent as MCP tools;
run one orchestrator sandbox that calls those tools to analyze every repo.

## 2. What MCP is good at (verified capability)

From `all-hands-dev/documentation/03-guides/08-sandboxes-as-workers.md` §3:

- A sandbox **is** an agent (its agent-server exposes an agent API and an
  OpenAI-compatible `/v1`).
- A sandbox **can serve MCP**: `fastmcp` is installed; a few lines expose tools.
- Other agents consume it by adding an `mcpServers` entry.
- The pattern "**specialist-as-MCP**" is documented and works.

So the option is *technically valid*. The question is whether it is *optimal for
this goal*.

## 3. Evaluation for the analysis path

| Criterion | Lenses/children (in-process) | Personas-as-MCP | Winner |
|---|---|---|---|
| Latency per persona call | none (in-context) | +1 network hop per call | in-process |
| Failure modes | 1 (the conversation) | 1 + N (each MCP server can be down) | in-process |
| State sync | none (one mind) | must fetch/push conversation state | in-process |
| Coherence (cross-examination) | native (one pass) | requires a reconciler anyway | in-process |
| Reuse of a heavy capability | rebuild per repo | build once, call many | **MCP** |
| Isolation of expertise | good (worktrees) | good | tie |
| Operational complexity | low | high (N servers to run/health-check) | in-process |

**Finding.** For *personas* — which are prompts plus skills — MCP adds cost and
failure surface with **no quality gain**. The persona is cheaper to load inside
the conversation than to reach over the network.

## 4. Where MCP *does* pay

MCP is the right tool when a capability is **heavy**, **stateful**, and
**reused** across many repos. Candidates:

| Capability | Why MCP helps | Reuse factor |
|---|---|---|
| **Code graph / index** | Build once per repo, query many times | high (all personas query it) |
| **Dependency scanner** | One scan serves Security, Compliance, Cost | high |
| **Fetch / web reader** | One egress-controlled reader | medium |
| **Static analysis (SAST)** | One engine, many languages | medium |

Stand these up **once** as capability servers and let every analyzer call them.
That is the documented "specialist-as-MCP" pattern, applied to *tools*, not to
*personas*.

## 5. Recommended hybrid

```
┌─────────────────────────────┐
│ ANALYZER conversation        │  ← personas as lenses (no MCP)
│  uses tools:                 │
│    • code-graph  (MCP)  ─────┼──▶ capability sandbox (built once)
│    • dep-scanner (MCP)  ─────┼──▶ capability sandbox (built once)
│    • fetch       (MCP)  ─────┼──▶ capability sandbox (built once)
└─────────────────────────────┘
```

- **Personas:** lenses or children (in-process). No MCP.
- **Heavy capabilities:** 1–3 capability MCP servers, reused across all repos.
- **Orchestration:** the platform conversation API (Spec 07), not MCP.

## 6. Cost/benefit

| Approach | Extra sandboxes | Extra hops | Quality | Complexity |
|---|---|---|---|---|
| All personas as MCP | up to 12 | N× repos | none | high |
| Hybrid (recommended) | 1–3 capability servers | 1 per heavy call | equal or better | medium |
| No MCP | 0 | 0 | equal | low |

The hybrid wins only if the shared capability is genuinely expensive enough to
amortise. For pure text analysis (which most of the 12 personas do), even the
hybrid is unnecessary.

## 7. Decision

**Do not convert persona sandboxes into MCP servers.** Use in-process lenses (and
children for large repos). Reserve MCP for a small number of reusable heavy
capabilities, and only when measurement shows they amortise.

**Refinement (see [`08-mcp-gateway-plan.md`](08-mcp-gateway-plan.md)).** MCP *does*
belong in the architecture for **shared external tool servers** (GitHub, Slack,
Jira, Snowflake, Figma…) — but behind **one aggregating gateway**, not one server
per sandbox. The refined two-plane model is:

| Plane | Where it runs | Transport |
|---|---|---|
| **Tools plane** — external, stateless, credential-bearing | **the shared gateway sandbox** | HTTPS |
| **Data plane** — local to the repo/machine | **each worker sandbox** (stdio) | loopback |

So "sandbox as MCP server" is worth it in exactly two cases: the **shared
gateway**, and a **heavy specialist engine** reused by many workers. It is never
worth it for personas.

## 8. When to revisit

Reconsider personas-as-MCP if:

- a persona needs a **very large** fixed context that is wasteful to reload per
  repo (then a warm server helps);
- the platform adds native "conversation as tool" support that removes the state
  sync burden;
- measurements show a specific persona dominates cost and benefits from caching.

Until then, the simpler in-process design is faster, more coherent, and less
fragile.
