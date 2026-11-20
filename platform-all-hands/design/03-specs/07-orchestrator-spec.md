# Spec 07 — Orchestrator

The orchestrator is **code, not a prompt**. It schedules, validates, and
aggregates; it never reasons about content.

## 1. Responsibilities

| Responsibility | Detail |
|---|---|
| Plan | Build the run manifest from the repo list (Spec 03) |
| Provision | Create/reuse the sandbox pool (Spec 05) |
| Distribute | Hand each analyzer its brief (Spec 01) |
| Monitor | Track per-repo status; enforce the capacity guard |
| Collect | Receive repo results; validate (Spec 08) |
| Synthesize | Start the org synthesizer |
| Publish | Merge result branches after the gates pass |

## 2. State machine

```
        ┌────────┐  plan   ┌─────────┐  provision ┌─────────┐
START ─▶│ PLANNED├────────▶│ PROVISION├───────────▶│ RUNNING │
        └────────┘         └─────────┘            └────┬────┘
                                                       │ all repos terminal
                                                       ▼
                       ┌──────────────┐  gates   ┌───────────┐
                       │ SYNTHESIZED  │◀─────────│ COLLECTED │
                       └──────┬───────┘          └───────────┘
                              │ publish (gates pass)
                              ▼
                          ┌─────────┐
                          │ PUBLISHED│
                          └─────────┘
```

Per-repo sub-state: `pending → running → done | failed | gated`.

## 3. Main loop (pseudocode)

```python
def run(org, repos):
    manifest = plan(org, repos)                 # Spec 03
    pool = SandboxPool(size=manifest.config.sandbox_pool_size)  # Spec 05
    pool.provision_from_base(manifest.config.base_image)

    for wave in manifest.waves():
        pool.resume_wave_sandboxes(wave)
        for repo in wave.repos:
            sb = pool.slot(repo.slot)
            if not pool.allow_start(sb):        # capacity guard
                defer(repo, to_wave=wave.number + 1); continue
            brief = render_brief(repo)          # Spec 01
            conv = start_conversation(sb, brief)
            manifest.set(repo, status="running", conversation_id=conv.id)
        wait_for_wave(manifest, wave)           # poll until all repos terminal
        pool.pause_all()

    # depth pass for leads handled inline by the lead's own children
    results = collect_results(manifest)         # from result branches
    gate_results(results)                       # Spec 08
    start_synthesizer(results)                  # Spec 04 §4
    wait_for_synthesis()
    publish(manifest)                           # merge analysis/* → main
```

## 4. Platform API calls used

| Purpose | Call |
|---|---|
| provision a sandbox + conversation | `POST /api/v1/app-conversations` |
| start a conversation on an existing sandbox | `POST /api/v1/app-conversations` with `sandbox_id` |
| poll a conversation | `GET /api/v1/app-conversations?ids=<id>` |
| list conversations | `GET /api/v1/app-conversations/search` |
| list sandboxes | `GET /api/v1/sandboxes/search` |
| pause / resume | `POST /api/v1/sandboxes/{id}/pause` \| `/resume` |
| send a follow-up | `POST /api/v1/app-conversations/{id}/send-message` |
| quota | `GET /api/quota/status` |

All calls are Bearer-authenticated with the platform API key. The key is read
from the environment and never logged.

## 5. Persistence and resumability

- The manifest is persisted after every state change.
- On restart, the orchestrator resumes from the manifest: repos in `running` are
  polled; repos in `pending` are (re)scheduled; `done` is skipped.
- Idempotent: re-running a repo replaces its result branch.

## 6. Observability

| Signal | Where |
|---|---|
| Per-repo status, attempts, timing | `manifests/run-<id>.json` |
| Tokens and cost per conversation | conversation `metrics` |
| Sandbox load / conversation count | capacity guard logs |
| Gate failures | gate report |

## 7. Error handling

| Error | Response |
|---|---|
| HTTP 5xx from the platform | exponential backoff, bounded retries |
| Quota exhausted | pause and wait for the reset |
| Analyzer produced no result in the budget | mark `failed`; retry ≤ 2 |
| Gate failure | mark `gated`; re-run with gate feedback |
| Sandbox lost | re-provision slot; replay its repos |

## 8. Non-goals

- The orchestrator does **not** analyze content.
- The orchestrator does **not** edit repositories.
- The orchestrator does **not** hold the analysis in its own context (that is the
  synthesizer's job).

## 9. Interfaces

| Interface | Shape |
|---|---|
| Input | `org`, repo list (from the inventory or a bundle dir) |
| Output | the artifacts repo with `results/`, `org/`, and the merged `main` |
| Config | `sandbox_pool_size`, `analyzers_per_sandbox`, `max_children_per_lead`, `base_image`, `skills_path` |

## 10. Testing

- Unit: manifest planning (tier/wave/slot assignment).
- Unit: capacity guard decisions.
- Integration: provision → run one tiny repo → collect → gate, against a test org.
- Chaos: kill a sandbox mid-wave; assert the replay works and the quota math holds.
