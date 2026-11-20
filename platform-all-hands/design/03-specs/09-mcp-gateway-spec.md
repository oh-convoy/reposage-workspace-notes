# Spec 09 — MCP Gateway

The concrete contract for the shared-data MCP gateway described in
[`../08-mcp-gateway-plan.md`](../08-mcp-gateway-plan.md).

## 1. Scope

| In scope | Out of scope |
|---|---|
| The gateway sandbox: lifecycle, endpoints, namespacing | Per-sandbox local (data-plane) servers |
| Credential and token model | Persona-as-MCP (rejected — see `../06-mcp-evaluation.md`) |
| The sandbox-side MCP client config | Upstream vendor APIs themselves |
| Health, failover, quotas, audit | |

## 2. Gateway service

```
GATEWAY_SANDBOX   = 1 sandbox (reuse a PAUSED one from the inventory)
GATEWAY_PORT      = 12000          (must be an exposed_urls port)
GATEWAY_TRANSPORT = http           (MCP over HTTP; SSE also supported)
GATEWAY_REPLICAS  = 2              (behind one endpoint)
```

- The gateway runs an aggregator (e.g. `fastmcp`) that **mounts** upstream
  servers under namespace prefixes.
- It is long-lived: provision once, keep it running across waves.
- It is the **only** sandbox with broad egress and upstream credentials.

## 3. Endpoints

| Endpoint | Purpose |
|---|---|
| `POST /mcp` | MCP JSON-RPC over HTTP (the tool surface) |
| `GET  /mcp` | SSE stream (for clients that prefer SSE) |
| `GET  /healthz` | Liveness — `{"status":"ok","upstreams":N}` |
| `GET  /readyz` | Readiness — all critical upstreams connected |
| `GET  /tools` | Debug: the aggregated tool list (namespaced) |

## 4. Namespacing

Every upstream server is mounted under a prefix; every tool is exposed as
`<server>__<tool>`:

| Upstream | Example tool exposed |
|---|---|
| github | `github__create_issue`, `github__list_prs` |
| slack | `slack__post_message` |
| snowflake | `snowflake__run_query` |
| figma | `figma__export_frame` |

Rules:

1. Prefixes are stable and unique.
2. On collision, the later server's tools are rejected at startup (fail loud).
3. `filter_tools_regex` on the client narrows what each agent sees.

## 5. Credential model

```
sandbox ──(gateway token, scoped)──▶ gateway ──(upstream creds)──▶ SaaS
```

| Credential | Held by | Lifetime | Scope |
|---|---|---|---|
| Upstream SaaS tokens | **gateway only** | rotated by ops | per tenant |
| Gateway token | each sandbox | short-lived (≤ 8 h) | per sandbox + per tool allow-list |

- **No upstream credential ever exists on a worker sandbox.**
- The gateway maps a gateway token → a **tenant/principal** → that tenant's
  upstream credentials. This is where least privilege lives.
- Tokens are minted per sandbox and revoked when the sandbox pauses.

## 6. Read/write split

Every tool is classified:

| Class | Exposure | Extra control |
|---|---|---|
| `read` | exposed broadly | none |
| `write` | allow-list per tenant | audit + optional human confirmation |
| `admin` | not exposed to agents | operator-only |

The gateway enforces the class before proxying the call.

## 7. Client configuration (per sandbox)

```jsonc
{
  "mcpServers": {
    "corp-gateway": {
      "url": "https://<gateway-host>:12000/mcp",
      "transport": "http",
      "headers": { "Authorization": "Bearer ${GATEWAY_TOKEN}" },
      "timeout": 30,
      "sse_read_timeout": 300,
      "keep_alive": true
    },
    "fs":        { "command": "npx", "args": ["-y", "@modelcontextprotocol/server-filesystem", "/workspace/project"] },
    "codegraph": { "command": "uvx", "args": ["code-graph-mcp"] }
  },
  "filter_tools_regex": "^(corp-gateway__|fs__|codegraph__).*"
}
```

- Register servers via `POST /api/settings/mcp/{key}`; validate via
  `POST /api/mcp/test`.
- Data-plane servers are **stdio** and local; the gateway is **http** and remote.

## 8. Availability

| Control | Setting |
|---|---|
| Replicas | 2 |
| Health check interval | 10 s |
| Unhealthy threshold | 3 → fail over |
| Per-upstream timeout | 30 s |
| Circuit breaker | open after 5 consecutive failures; half-open after 30 s |
| Connection reuse | `keep_alive: true` |

## 9. Quotas and limits

| Limit | Default |
|---|---|
| Calls per gateway token / minute | 600 |
| Calls per upstream / minute | 300 |
| Concurrent upstream connections | 50 |
| Max tool result size | 1 MiB |

Exceeding a limit returns a clean MCP tool error (never a hang).

## 10. Audit record

```jsonc
{
  "ts": "2026-11-18T02:00:00Z",
  "principal": "sandbox:24nWgqBo",
  "tenant": "eng",
  "server": "github",
  "tool": "github__create_issue",
  "class": "write",
  "args_hash": "sha256:…",
  "status": "ok",
  "latency_ms": 412
}
```

Never log arguments or results in full (they may contain secrets/PII).

## 11. Startup contract

At gateway start, for each configured upstream:

1. Connect (spawn stdio or dial HTTP).
2. List its tools.
3. Check namespace collisions; fail loud on a collision.
4. Classify each tool read/write/admin.
5. Only then mark `/readyz` healthy.

## 12. Testing

| Test | Assertion |
|---|---|
| Reachability | a second sandbox lists the gateway's tools via `/api/mcp/test` |
| Namespacing | tool names are prefixed and unique |
| Isolation | a worker holds no upstream credential |
| Least privilege | a worker's token cannot call tools outside its allow-list |
| Failover | killing one replica keeps tools available |
| Backpressure | a slow upstream returns a timeout error, not a hang |
| Audit | every call produces an audit record |

## 13. Invariants

1. Workers never hold upstream credentials.
2. Every tool name is namespaced and unique.
3. Data-resident tools never route through the gateway.
4. The gateway is never a single point of failure (≥ 2 replicas).
5. Agents see a filtered, narrow tool list.
6. Secrets live only in the secret store.
