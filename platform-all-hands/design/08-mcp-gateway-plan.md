# 08 — MCP Gateway Plan

> **Question this answers:** *"Use one sandbox as an MCP gateway — one machine with
> all MCP servers installed, one endpoint consumed by all other sandboxes. Is that
> a good plan? If not, what is the optimal implementation?"*

## 1. Verdict

**Your instinct is right in shape, but too broad in scope.**

A single gateway is the **correct** pattern for **shared, stateless,
credential-bearing tool servers** — the SaaS/API servers (GitHub, Slack, Jira,
Snowflake, Figma, Stripe…). Centralizing them gives one place for credentials,
one config to maintain, one audit trail, and one amortized startup cost.

It is the **wrong** pattern for **sandbox-local capabilities** — filesystem
access, a repo code-graph, a per-repo index — because those must run *where the
data is*. Routing them across the network adds latency, a failure mode, and an
egress cost for zero benefit.

**So the optimal design is two tiers, not one machine:**

```
┌─────────────────────────┐        ┌───────────────────────────────┐
│ SHARED-DATA GATEWAY     │        │ SANDBOX (each worker)          │
│ (1 sandbox, 1 endpoint) │◀──TLS──▶│  MCP client config:           │
│  GitHub · Slack · Jira  │        │   • shared gateway  (HTTP)     │
│  Snowflake · Figma …    │        │   • local servers   (stdio)    │
│  holds all credentials  │        │   • (optional) heavy engines   │
└─────────────────────────┘        └───────────────────────────────┘
```

The sandbox's MCP client lists **both**: the remote gateway for shared tools and
local stdio servers for data-resident tools. One config, two planes.

## 2. Your proposal, assessed honestly

**What it gets right**

| Merit | Why it matters |
|---|---|
| One credential store | Sandboxes never hold SaaS tokens — the gateway does |
| One config surface | Register a server once, every sandbox gets it |
| One audit point | All external tool calls pass through one chokepoint |
| Amortized startup | MCP servers are spawned per conversation; a warm gateway avoids that |
| Central allow-listing | Egress control and rate limits in one place |

**What breaks**

| Problem | Detail | Severity |
|---|---|---|
| **Single point of failure** | Gateway down ⇒ every sandbox loses all tools | High |
| **Throughput bottleneck** | One box (4 CPU / 16 GiB) proxies every tool call from every sandbox | High |
| **Data-resident tools cannot move** | Filesystem, code-graph, per-repo index must run beside the code; they cannot be centralized | Critical |
| **Tool-list explosion** | 168 catalogued servers × ~10 tools ≈ 1 700 tools; an unfiltered gateway would destroy the agent's context | Critical |
| **Credential tenancy** | One gateway with one set of credentials means every sandbox acts as the same principal — no least privilege | High |
| **Egress cost/latency** | Local work (read a file) becomes a network round-trip | Medium |

The last two are the ones that sink the naive version: **an agent must see a
*narrow* tool list**, and **local data must stay local**.

## 3. How MCP actually works in OpenHands (verified)

Grounded in the platform's own schema (`MCPServer` in the agent-server OpenAPI)
and the `all-hands-dev` guide *Sandboxes as Workers* (§3):

- OpenHands is an **MCP client** out of the box. A sandbox's agent loads
  `mcp_servers` from its settings; each server is spawned (stdio) or connected
  (HTTP/SSE) **at conversation start**.
- An `MCPServer` entry has: `url`, `transport` (stdio | sse | http), `command`,
  `args`, `env`, `headers`, `auth`, `timeout`, `sse_read_timeout`, `keep_alive`,
  `enabled`.
- The agent-server exposes `/api/mcp/test` to validate a server and list its
  tools, and `/api/settings/mcp/{key}` to add/update/remove servers.
- A sandbox **can itself serve MCP** — `fastmcp` is installed in the standard
  sandbox image (the guide documents it). So any sandbox can host the gateway.
- **Cross-sandbox reachability exists**: a sandbox's `exposed_urls` carry
  externally reachable HTTPS URLs for named ports. In the live inventory:

  ```json
  [
    { "name": "AGENT_SERVER", "url": "https://<host>.prod-runtime.all-hands.dev", "port": 60000 },
    { "name": "WORKER_1",     "url": "https://work-1-<host>/",                  "port": 12000 },
    { "name": "WORKER_2",     "url": "https://work-2-<host>/",                  "port": 12001 }
  ]
  ```

  A gateway listening on an exposed port is reachable from every other sandbox at
  that HTTPS URL. **This is what makes your plan technically feasible.**

> Note: `fastmcp` was *not* importable in this particular build's site-packages.
> Treat it as "installed in the image per the docs; if absent, install with
> `uv pip install fastmcp`". The `mcp` SDK or any HTTP/SSE server works equally.

## 4. The two planes (the core idea)

Every MCP server belongs to exactly one plane. The plane decides **where it runs**.

| Plane | Property | Where it runs | Examples | Transport |
|---|---|---|---|---|
| **Tools plane** | Stateless, external, credential-bearing, shared by all | **The gateway sandbox** | GitHub, Slack, Jira, Snowflake, Figma, Stripe | HTTPS → gateway |
| **Data plane** | Stateful, bound to the local repo/machine, per-sandbox | **The worker sandbox** | filesystem, code-graph, ripgrep, per-repo index, local DB | stdio (loopback) |

**Rule of thumb:** *If the tool reads or writes data that lives on this sandbox,
it is data-plane and must stay local. If the tool talks to an external service
with a credential, it is tools-plane and belongs on the gateway.*

## 5. Recommended architecture

### 5.1 Tier 0 — Shared-data gateway (your idea, scoped correctly)

- **One sandbox**, one HTTPS endpoint, running an **aggregating MCP gateway**.
- Hosts the tools-plane servers: the SaaS/API servers from
  `plans/mcp/M01–M14` that are stateless and shared.
- Holds **all external credentials** (via the gateway's secret store or the
  platform's OAuth flow). Sandboxes hold none.
- Namespaces every tool by server (`github__create_issue`) so names never collide.

### 5.2 Tier 1 — Per-sandbox local servers (data plane)

- stdio servers spawned inside each worker, next to the code.
- Filesystem, code-graph, ripgrep, per-repo index, local test runner.
- Zero network hop; zero shared credential; scoped to that sandbox's workspace.

### 5.3 Tier 2 — Optional specialist engines

- A genuinely heavy, reusable engine (e.g. a repo-wide SAST or a model server)
  that many workers need and that is expensive to rebuild.
- Its own sandbox, exposed as **one** MCP endpoint, consumed by workers that need
  it. This is the *only* place "sandbox as MCP server" earns its keep (see
  [`06-mcp-evaluation.md`](06-mcp-evaluation.md) §4).

### 5.4 The decision tree

```
Does the tool touch data on this sandbox (files, repo, local index)?
├── yes → LOCAL stdio server in the worker              (Tier 1)
└── no
    └── Does it call an external service with a credential?
        ├── yes, and it is shared/stateless → GATEWAY     (Tier 0)
        └── yes, and it is heavy + reused   → SPECIALIST  (Tier 2)
```

### 5.5 What each sandbox's MCP client config looks like

```jsonc
{
  "mcpServers": {
    "corp-gateway": {                       // Tier 0 — one endpoint, many tools
      "url": "https://<gateway-host>:<port>/mcp",
      "transport": "http",
      "headers": { "Authorization": "Bearer ${GATEWAY_TOKEN}" },
      "timeout": 30
    },
    "fs": { "command": "npx", "args": ["-y", "@modelcontextprotocol/server-filesystem", "/workspace/project"] },
    "codegraph": { "command": "uvx", "args": ["code-graph-mcp"] }
  },
  "filter_tools_regex": "^(corp-gateway__github|fs__|codegraph__).*"
}
```

Two things to notice: the gateway is **one** entry, and `filter_tools_regex`
keeps the agent's tool list **narrow** (the antidote to tool-list explosion).

## 6. How to implement the gateway

Two viable routes. Start with A; graduate to B when you need RBAC and audit.

### Option A — Thin aggregator built with `fastmcp` (recommended start)

`fastmcp` supports **mounting** other servers and **proxying** them, so an
aggregator is a few lines:

```python
from fastmcp import FastMCP

gw = FastMCP("corp-gateway")

# Each upstream server is mounted under a namespace prefix.
gw.mount("github",    FastMCP.as_proxy("https://mcp.github.example/sse"))
gw.mount("slack",     FastMCP.as_proxy({"command": "npx", "args": ["-y", "slack-mcp"]}))
gw.mount("snowflake", FastMCP.as_proxy({"command": "uvx", "args": ["snowflake-mcp"]}))

if __name__ == "__main__":
    gw.run(transport="http", host="0.0.0.0", port=12000)   # exposed_urls port
```

- Tools appear as `github__*`, `slack__*`, `snowflake__*`.
- Run it as a service in the gateway sandbox; expose port 12000.
- Verify from any sandbox with `POST /api/mcp/test`.

### Option B — A product gateway (when you outgrow A)

For RBAC, per-tenant credentials, quotas, audit logs, and OAuth brokering, adopt
a dedicated MCP gateway (the category is maturing fast — e.g. Docker's MCP
Gateway, IBM's ContextForge/MCP Gateway, MCPProxy, Lasso). These give you
federation, virtual servers, and policy out of the box. Add this in **Phase 3**,
not on day one.

### Option C — Federate, don't aggregate everything

If the tool list is still too large, **shard the gateway by domain** (an
"engineering gateway", a "marketing gateway", a "data gateway") and point each
squad at only the shards it needs. Fewer tools per agent, smaller blast radius.

## 7. Security model (the crux)

A gateway concentrates risk. Mitigate deliberately:

| Concern | Mitigation |
|---|---|
| **Single point of compromise** | Gateway is the only holder of SaaS tokens; sandboxes get scoped, short-lived gateway tokens, not upstream creds |
| **Least privilege / tenancy** | Per-tenant credential slots in the gateway; a worker authenticates as *its* principal, not a shared admin |
| **Read vs write** | Split tools: expose read-only tools broadly; gate write tools behind an allow-list and (for critical ones) human confirmation |
| **Egress** | Gateway is the only sandbox with broad egress; workers keep egress restricted |
| **Rate limiting / abuse** | Central quotas per token, per tool, per sandbox |
| **Audit** | Every tool call logged with principal, tool, args-hash, result-status |
| **Secrets at rest** | Gateway secrets in the platform secret store / vault; never in config files or the artifacts repo |
| **Transport** | HTTPS only; the platform's `session_api_key` and gateway token are secrets — never commit or print |

> The single most important control: **sandboxes must never hold upstream
> credentials.** If a worker is compromised, it can call only the tools its
> gateway token allows — nothing more.

## 8. Availability and scale

A gateway is a bottleneck by design, so treat it like a production service:

| Concern | Mitigation |
|---|---|
| SPOF | Run **2 gateway replicas** behind one endpoint; health-check and fail over |
| Throughput | Stateless HTTP + connection pooling; scale replicas horizontally |
| Backpressure | Timeouts + circuit breakers per upstream; return a clean tool error |
| Cold start | `keep_alive` on upstream connections; warm the gateway before a wave |
| Version drift | Pin upstream server versions; the gateway is the single upgrade point |
| Blast radius | Shard by domain (Option C) so one bad upstream cannot take down all tools |

**Quota:** the gateway costs **1 sandbox** (reuse an existing paused one from the
inventory). Because it is long-lived and shared, it is the best possible use of
one sandbox unit.

## 9. Does this change the earlier decision?

[`06-mcp-evaluation.md`](06-mcp-evaluation.md) concluded *"do not convert persona
sandboxes into MCP servers."* **That still holds.** This plan refines it:

| Earlier statement | Refined position |
|---|---|
| Personas are not MCP servers | **Unchanged** — personas are lenses/children |
| MCP only for a few shared heavy capabilities | **Extended** — shared *tools* (SaaS) also belong on MCP, **via one gateway**, not per sandbox |
| "Sandbox as MCP server" is rarely worth it | **Refined** — it *is* worth it for (a) the shared gateway and (b) heavy specialist engines; not for personas |

See the updated ADR-3 note in `06-mcp-evaluation.md`.

## 10. Implementation plan

| Phase | Deliverable | Gate |
|---|---|---|
| **P0 — Spike (½ day)** | One sandbox runs a `fastmcp` aggregator mounting 2 servers; `/api/mcp/test` returns their tools | Tools list from a second sandbox |
| **P1 — Gateway v1 (2–3 days)** | Gateway mounts the top ~10 tools-plane servers; namespacing; sandbox config template; token auth | A worker calls a gateway tool end-to-end |
| **P2 — Harden (1 week)** | Per-tenant creds, read/write split, quotas, audit log, 2 replicas, health checks | Chaos test: kill a replica, tools stay up |
| **P3 — Federate (ongoing)** | Shard by domain; adopt a product gateway for RBAC/OAuth; onboard squads incrementally | Each squad sees only its shard |

## 11. Verification checklist

- [ ] Gateway reachable from a second sandbox over its exposed HTTPS URL.
- [ ] `/api/mcp/test` on a worker lists the gateway's tools.
- [ ] `filter_tools_regex` keeps the agent's tool list under ~50 tools.
- [ ] Data-plane tools (filesystem, code-graph) run **locally**, not via the gateway.
- [ ] No upstream credential present on any worker sandbox.
- [ ] Read-only vs write tools are distinguishable; write tools are allow-listed.
- [ ] Kill one gateway replica → tools still respond.
- [ ] Every tool call appears in the audit log with principal + tool.

## 12. Risks

| Risk | Mitigation |
|---|---|
| Gateway becomes the whole company's bottleneck | Replicas + sharding + connection pooling |
| Tool-list explosion degrades agents | Namespacing + `filter_tools_regex` + domain shards |
| One credential set ⇒ no least privilege | Per-tenant credential slots; scoped gateway tokens |
| Local tools wrongly centralized | Enforce the two-plane rule in review |
| Upstream server breakage cascades | Circuit breakers, pinned versions, shard isolation |
| Secrets leak via config | Secret store only; never in the artifacts repo |

## 13. Bottom line

Build **one shared-data gateway** (your idea) **plus local per-sandbox servers**,
not one machine for everything. The gateway is the right home for external,
credential-bearing, shared tools; local stdio servers are the right home for
data-resident tools; heavy reusable engines are the only "sandbox-as-MCP" worth
standing up. Namespace and filter the tools so agents stay sharp, run two
replicas so the gateway is not a single point of failure, and never let a worker
hold an upstream credential.

See the contract in [`03-specs/09-mcp-gateway-spec.md`](03-specs/09-mcp-gateway-spec.md)
and the server inventory in [`../../plans/mcp/M15-gateway-aggregation.md`](../../plans/mcp/M15-gateway-aggregation.md).
