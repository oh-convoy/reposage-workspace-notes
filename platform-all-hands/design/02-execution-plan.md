# 02 — Execution Plan

The concrete, runnable plan: phases, waves, scheduling, the warm base, and the
quota math.

## 1. Phase overview

```
P0  PREP      build base image · clone org once · build repo bundles · write run manifest
P1  WAVE 1    ≤20 sandboxes · 3–5 analyzers each · repos 1..K
P2  WAVE 2..N reuse paused sandboxes · next K repos · 0 quota
P3  DEPTH     large/critical repos → squad leads + child fan-out
P4  SYNTH     org synthesizer → org-level documents
P5  GATE      quality gates → publish
```

## 2. P0 — Prep (once per organization)

**Goal:** pay all fixed costs once so every wave starts warm.

| Task | Detail | Output |
|---|---|---|
| Base image | agent-server image + toolchain + warm caches (`PIP_CACHE_DIR`, `npm_config_cache`, …) | `base` sandbox spec |
| Clone org once | `git clone --mirror` each repo | `repos/<repo>.bundle` per repo |
| Size repos | file count, LOC, languages, doc ratio | sizing table |
| Assign tiers | analyzer vs lead per repo | run manifest |
| Write manifest | repo → tier → wave → sandbox slot | `manifests/run-<id>.json` |
| Load skills | copy the `repo-deep-analysis-skills` into each sandbox's skills dir | skill available to agents |

**Why bundles.** A worker `git clone repos/<repo>.bundle` is fast and needs no
network clone. The org is cloned **once**, not per sandbox.

## 3. P1–P2 — The waves

### 3.1 Scheduling

```
for wave in waves:
    for slot in 1..20:                      # 20 sandboxes, reused every wave
        sandbox = pool.acquire(slot)        # resume if PAUSED
        for repo in wave.repos_for(slot):   # 3–5 repos per sandbox
            sandbox.start_analyzer(repo)    # one conversation per repo
    pool.pause_all()                        # pause, do not destroy → 0 quota next wave
```

- **Sandbox pool = 20**, acquired once, **paused** between waves.
- **Analyzer conversations = repos per wave**, spread 3–5 per sandbox.
- **Wave size ≤ 20 × 4 = 80 repos** at the default; scale the per-sandbox count
  up for small repos (LLM/IO-bound work tolerates 6–8).

### 3.2 Per-analyzer brief

Each analyzer receives a **self-contained brief** (it cannot see the orchestrator's
history). The brief is the contract in
[`03-specs/01-analyzer-brief.md`](03-specs/01-analyzer-brief.md). Minimum fields:

- the repo bundle path and target revision;
- the skill path and the 12 persona documents;
- the deliverable schema (Repo Result);
- the output location (the result branch / artifacts repo);
- the hard rules: read-only, no long blocking loops, no secrets, label every claim.

### 3.3 Concurrency limits (hard)

| Limit | Value | Reason |
|---|---|---|
| Sandboxes in flight | 20 | platform budget |
| Analyzers per sandbox (LLM/IO) | 3–5 | 4 CPU / 16 GiB |
| Analyzers per sandbox (heavy compute) | 1–2 | avoid oversubscription |
| Child conversations per lead | ≤ 5 | the stall incident |
| Long blocking commands | **forbidden** | shared-shell serialisation |

## 4. P3 — Depth pass

For repos flagged large or critical:

```
squad-lead(repo) →
   child G1 intent      (worktree)
   child G2 structure   (worktree)
   child G3 implementation (worktree)
   child G4 operations  (worktree)
   child G5 knowledge   (worktree)
→ lead reconciles → repo-result
```

- Children are `isolation: worktree` (needs a git base commit — the bundle gives
  it).
- Each child loads only its group's persona documents (narrow context = faster,
  sharper).
- The lead performs the **squad challenge**: force each group to challenge the
  others; record disagreements.

## 5. P4 — Synthesis

One **Org Synthesizer** conversation:

- reads every `results/<repo>/repo-result.json`;
- builds the cross-repo relationship map (dependencies, duplication, drift);
- writes `org/*.md`: overview, relationships, risks, glossary, business view;
- flags cross-repo contradictions for human review.

## 6. P5 — Quality gates

Run before publish (full detail in [`05-quality-model.md`](05-quality-model.md)):

1. **Schema gate** — every Repo Result validates against the schema.
2. **Evidence gate** — every fact/inference has a citation; no unsupported facts.
3. **Secret gate** — no secret values anywhere in results.
4. **Coverage gate** — every repo in the manifest has a result.
5. **Reconciliation gate** — every recorded disagreement is resolved or flagged.
6. **Link gate** — every relative link resolves.

## 7. Quota and time math

### 7.1 Quota

| Item | Cost |
|---|---|
| Wave-1 sandboxes | 20 |
| Wave-2..N sandboxes | **0** (reuse paused) |
| Analyzer conversations | **0** (reuse sandboxes) |
| Child conversations | **0** (reuse sandboxes) |
| Org synthesizer | 0 if it reuses a sandbox, else 1 |

**Total new sandboxes for any number of waves: 20.** The limit is a *sandbox*
quota, not a conversation quota (verified: `/api/quota/status`).

### 7.2 Time (illustrative)

Let `T` = average per-repo analysis wall-clock, `R` = repos, `P` = parallel
analyzers per sandbox, `S` = 20 sandboxes.

```
wall_clock ≈ ceil(R / (S × P)) × T
```

| R (repos) | P | S | waves | ≈ wall clock (at T=10 min) |
|---|---:|---:|---:|---:|
| 100 | 4 | 20 | 2 | ~20 min |
| 200 | 4 | 20 | 3 | ~30 min |
| 500 | 6 | 20 | 5 | ~50 min |
| 1000 | 8 | 20 | 7 | ~70 min |

The fixed prep cost (clone + base image) dominates for small orgs; for large orgs
the waves dominate and the reuse makes it linear in repos / (S×P).

## 8. Failure handling

| Failure | Response |
|---|---|
| Analyzer stalls (blocking loop) | kill by PID; the brief forbids blocking loops; retry with a stricter brief |
| Sandbox dies | re-provision from the base image (costs 1 quota); resume its repos |
| A repo is huge | promote it to a squad lead; split by subdirectory |
| A result fails a gate | re-run that repo's analyzer with the gate feedback |
| Rate limit (LLM) | bounded concurrency + backoff; reduce `P` temporarily |
| Child collision | worktrees are isolated; ensure a git base commit exists |

## 9. Runbook (copy this)

```
P0  1. Build the base sandbox image with toolchain + warm caches.
    2. git clone --mirror each org repo -> repos/<repo>.bundle.
    3. Size every repo; assign tier (analyzer | lead).
    4. Write manifests/run-<id>.json (repo -> tier -> wave -> slot).
    5. Copy repo-deep-analysis-skills into the base skills dir.

P1  6. Provision 20 sandboxes from the base image.
    7. For each wave: resume sandboxes; start 3-5 analyzers each;
       each analyzer: fetch bundle -> worktree -> 12 lenses -> repo-result.
    8. Push each repo-result to the artifacts repo.
    9. Pause all sandboxes (do NOT destroy).

P3 10. For each large/critical repo: start a squad lead; fan out 5 children;
       reconcile -> repo-result.

P4 11. Start the org synthesizer; read all results; write org/*.md.

P5 12. Run the six gates. Fix failures. Publish.
```
