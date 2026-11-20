# 03 — Specifications

Granular, copy-ready specifications for the analysis pipeline. Each spec is a
contract that an implementer (human or agent) can build against directly.

| # | Spec | Defines |
|---|---|---|
| 01 | [`01-analyzer-brief.md`](01-analyzer-brief.md) | The self-contained brief handed to each analyzer |
| 02 | [`02-repo-result-schema.md`](02-repo-result-schema.md) | The machine-readable Repo Result (JSON) + MD layout |
| 03 | [`03-run-manifest-schema.md`](03-run-manifest-schema.md) | The run manifest (repo → tier → wave → slot) |
| 04 | [`04-prompts.md`](04-prompts.md) | The literal prompts for analyzer, squad lead, child, synthesizer |
| 05 | [`05-sandbox-pool-spec.md`](05-sandbox-pool-spec.md) | The pool: provisioning, reuse, pause/resume, warm base |
| 06 | [`06-artifact-contract.md`](06-artifact-contract.md) | Where artifacts live, how they travel, branch/commit rules |
| 07 | [`07-orchestrator-spec.md`](07-orchestrator-spec.md) | The orchestrator app: phases, state machine, API calls |
| 08 | [`08-quality-gates-spec.md`](08-quality-gates-spec.md) | The executable gate checks |

## Conventions

- All schemas use JSON Schema Draft 2020-12.
- All file paths are POSIX and relative to the artifacts repo root unless stated.
- Every claim in every artifact carries an evidence label
  (`fact|inference|prediction|unknown`) and, where applicable, a severity and a
  confidence — per the skill's evidence rules.
