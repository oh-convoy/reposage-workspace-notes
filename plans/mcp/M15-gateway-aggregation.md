# M15 — Gateway & Aggregation

**Scope:** MCP aggregation gateways, proxies, registries, and the shared endpoint
that fronts the tools-plane servers.

## Servers

| # | MCP Server | Purpose | Used by squads | Auth | Transport | Criticality |
|---|---|---|---|---|---|---|
| 1 | FastMCP Aggregator | Mount/proxy many upstream servers behind one endpoint | All (S01–S39) | Token | HTTP | Critical |
| 2 | MCPProxy | Local proxy/federation with tool filtering and logging | S01, S06, S08, S10 | Token | stdio, HTTP | High |
| 3 | Docker MCP Gateway | Container-based gateway with secrets and RBAC | S01, S06, S08, S13 | Service account | HTTP | High |
| 4 | IBM ContextForge MCP Gateway | Federated gateway, virtual servers, policy | S01, S06, S08 | OAuth2 | HTTP | Medium |
| 5 | MCP Registry Server | Discover and version MCP servers internally | S01, S06, S07, S13 | Token | HTTP | Medium |
| 6 | OpenHands Agent-Server (as MCP) | Expose a sandbox's tools as an MCP endpoint | S01, S06, S10, S13 | Session key | HTTP | High |
| 7 | Gateway Auth Broker | Mint scoped, short-lived per-sandbox gateway tokens | S01, S08, S10 | OAuth2 | HTTP | Critical |
| 8 | Tool-Allow-List Policy Server | Enforce read/write/admin tool classes per tenant | S01, S08, S14 | Service account | HTTP | High |
| 9 | MCP Audit Sink | Collect per-call audit records from the gateway | S01, S08, S36 | Token | HTTP | High |
| 10 | MCP Health/Metrics Exporter | Export gateway and upstream health to monitoring | S01, S05, S06 | Token | HTTP | Medium |

## Notes

| # | Note |
|---|---|
| 1 | One shared gateway sandbox holds the tools-plane servers and all upstream credentials; worker sandboxes hold only scoped gateway tokens and their own local (data-plane) stdio servers. |
| 2 | Namespace every tool (`server__tool`) and filter the agent's tool list with `filter_tools_regex` to avoid context blow-up. |
| 3 | Run at least two gateway replicas; treat the gateway as a production service with health checks, circuit breakers, and per-token quotas. |
| 4 | Data-resident tools (filesystem, code-graph, per-repo index) must run locally in each sandbox, never through the gateway. |
