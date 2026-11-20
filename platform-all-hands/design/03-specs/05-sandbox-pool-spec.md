# Spec 05 — Sandbox Pool

How the 20 sandboxes are provisioned, reused, paused, and kept warm. This is the
component that converts the platform's sandbox quota into throughput.

## 1. The pool

```
POOL_SIZE = 20            # the platform's sandbox budget
SANDBOX = one agent-server container (4 CPU / ~16 GiB)
SLOTS   = 1..20           # stable slot → sandbox mapping, reused across waves
```

- The pool is created **once** per run.
- Sandboxes are **paused, not destroyed**, between waves. A paused sandbox costs
  **no quota** to resume, and keeps its warm filesystem and caches.
- Only a **new** sandbox consumes quota. Conversations on existing sandboxes are
  free.

## 2. Lifecycle

```
provision (1 quota each) → RUNNING → [wave] → PAUSE → [next wave] → RESUME → ...
                                                                        ↓ end
                                                                     PAUSE/keep
```

| Transition | API call | Quota |
|---|---|---|
| provision | `POST /api/v1/app-conversations` (no `sandbox_id`) | **1** |
| add conversation | `POST /api/v1/app-conversations` (with `sandbox_id`) | 0 |
| pause | `POST /api/v1/sandboxes/{id}/pause` | 0 |
| resume | `POST /api/v1/sandboxes/{id}/resume` | 0 |
| list | `GET /api/v1/sandboxes/search` | 0 |
| conversations | `GET /api/v1/app-conversations/search` | 0 |

> Verified against the platform: the quota is a **sandbox** quota
> (`/api/quota/status` → `daily_limit: 20`), and a conversation created on an
> existing sandbox does not consume it.

## 3. Warm base

Before the first wave, one sandbox bakes the base:

| Step | Command / action | Why |
|---|---|---|
| Toolchain | ensure language runtimes, git, analysis tools | no per-worker installs |
| Warm caches | set `PIP_CACHE_DIR`, `npm_config_cache`, `CARGO_HOME`, `GOCACHE` to a shared dir | first worker downloads, rest hit cache |
| Clone once | `git clone --mirror <repo>` → `repos/<repo>.bundle` | no network clone per worker |
| Skills | copy `repo-deep-analysis-skills` into the base skills dir | available to every agent |
| Services | start shared services (e.g. a code-index server) on localhost | reuse across workers |

The base is captured as a sandbox spec so all 20 pool members are identical.

## 4. Slot allocation

```
slots = [1..20]
for wave in waves:
    for repo in wave.repos:
        slot = repo.slot          # fixed by the manifest
        sandbox = pool[slot]
        if sandbox.status == PAUSED: resume(sandbox)
        start_analyzer(sandbox, repo)   # a new conversation on the sandbox
    wait_for_wave()
    for sandbox in pool: pause(sandbox)
```

- `repo.slot` is stable across waves (Spec 03 §3), so each sandbox always owns the
  same set of repos → consistent warm state.

## 5. Capacity guard

Before starting an analyzer, check the sandbox's live load:

```
allow_start(sandbox) :=
    running_conversations(sandbox) < max_analyzers(sandbox)
    AND loadavg(sandbox)[0] < 0.8 * cpu_count
    AND free_mem(sandbox) > 2 GiB
```

- `max_analyzers` = 4 for LLM/IO-bound repos, 1–2 for heavy-compute repos.
- If the guard fails, the orchestrator defers the repo to the next wave.

This is the direct mitigation for the parallel-agent stall incident.

## 6. Reuse rules

| Situation | Action |
|---|---|
| Same repo, another pass | add a conversation to the **same** sandbox |
| New wave | **resume** the paused sandbox (0 quota) |
| A sandbox died | re-provision (1 quota) and replay its repos |
| Finished a run | pause all; keep for the next run |
| Need > 20 sandboxes | **wait** for the quota reset; do not exceed the pool |

## 7. Inventory integration

The pool is seeded from the sandbox inventory (`../inventory/sandboxes.json`):

- Reuse **existing paused** sandboxes where possible (they already count against
  no future quota and are warm).
- Only provision the shortfall up to `POOL_SIZE`.
- Record each sandbox's `session_api_key` (secret) for the orchestrator to reach
  the agent server; never write it to any non-secret artifact.

## 8. Failure handling

| Failure | Detection | Response |
|---|---|---|
| Provision fails | HTTP error | retry once; reduce pool size |
| Quota exhausted | `/api/quota/status` `remaining == 0` | pause and wait for reset |
| Sandbox unhealthy | health check / load guard | re-provision; replay repos |
| Analyzer hangs | no progress + high CPU | kill by PID; retry with stricter brief |
| Resume fails | HTTP error | re-provision the slot |

## 9. Invariants

1. Never more than `POOL_SIZE` running sandboxes.
2. Never more than `max_analyzers` conversations started concurrently per sandbox.
3. Always pause (never destroy) a healthy sandbox between waves.
4. Never exceed the daily sandbox quota; wait for the reset instead.
5. Never write a `session_api_key` to a non-secret artifact.
