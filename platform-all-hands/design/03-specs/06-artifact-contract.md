# Spec 06 — Artifact Contract

Where analysis artifacts live, how they travel between tiers, and the rules for
branches, commits, and secrets.

## 1. Layout

One **artifacts repository** per organization (e.g. `<org>-analysis`):

```
<org>-analysis/
  repos/
    <repo>.bundle            # bare mirror bundle, one per repo (the only clone)
  results/
    <repo>/
      repo-result.json       # machine-readable (Spec 02)
      00-overview.md
      01-method-and-coverage.md
      02-business-view.md
      03-technical-view.md
      04-findings.md
      05-risks-and-recommendations.md
      06-evidence-index.md
  org/
    00-organization-overview.md
    02-cross-repo-relationships.md
    03-risks-and-findings.md
    04-glossary.md
    05-business-view.md
  manifests/
    run-<id>.json            # the run manifest (Spec 03)
  _meta/
    README.md                # provenance, schema, how to regenerate
    run-log.json             # per-repo status, timing, cost
```

## 2. What travels, and how

| Artifact | Producer | Consumer | Transport |
|---|---|---|---|
| `<repo>.bundle` | prep phase | analyzers | already in the artifacts repo; workers fetch it |
| `repo-result.json` | analyzer / lead | synthesizer | pushed to a result branch |
| Markdown set | analyzer / lead | synthesizer, humans | pushed to a result branch |
| `org/*.md` | synthesizer | humans | pushed to `analysis/org-synthesis` |
| manifest | orchestrator | orchestrator | committed to `main` |

**Rule:** the organization is cloned **once** (into bundles). Workers never clone
the whole org; they clone one bundle.

## 3. Branch and commit rules

| Branch | Written by | Merged by |
|---|---|---|
| `main` | orchestrator (manifest), maintainers | — |
| `analysis/<repo>` | that repo's analyzer/lead | orchestrator after the gates pass |
| `analysis/org-synthesis` | the synthesizer | orchestrator after the gates pass |

- One branch per repo → results merge independently; a conflict in one repo never
  blocks another.
- Commit message: `analysis: <repo> (tier)` or `analysis: org synthesis`.
- The orchestrator opens one integration branch (`analysis/run-<id>`) that merges
  all `analysis/*` branches after the gates pass, then merges to `main`.

## 4. Idempotency

- Re-running a repo **replaces** `results/<repo>/` on its branch (force-with-lease
  on the result branch only).
- The manifest records `attempts` and the revision, so a re-run is traceable.
- The synthesizer is deterministic given the set of repo results: same inputs →
  same org documents (modulo the timestamp).

## 5. Secrets

- **Never** commit a `session_api_key`, token, or credential to the artifacts
  repo.
- The inventory JSON (`../inventory/sandboxes.json`) holds session keys; it lives
  **outside** the artifacts repo and is chmod `0600`.
- The secret gate (Spec 08) scans every artifact for secret-shaped strings before
  publish.

## 6. Provenance

Each `repo-result.json` carries `revision` (the exact commit analyzed), so the
analysis is reproducible against a specific state. `_meta/run-log.json` records,
per repo: tier, slot, start/end time, tokens, cost, and status.

## 7. Sizing

| Artifact | Typical size | Notes |
|---|---|---|
| `<repo>.bundle` | MBs–GBs | the bulk; stored once |
| `repo-result.json` | KBs | small; aggregates cheaply |
| Markdown set | KBs | small |
| `org/*.md` | KBs | small |

The **only** large artifacts are the bundles, and they are stored once — not
copied per sandbox.

## 8. Retention

- Keep `repos/*.bundle` for reproducibility.
- Keep `results/` and `org/` as the analysis record.
- Rotate `_meta/run-log.json` per run; keep the last N runs.
