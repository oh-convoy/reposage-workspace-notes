# 05 — Quality Model

How quality is protected *while* running fast. Quality here is not a feeling; it
is a set of measurable properties enforced by the pipeline.

## 1. The quality dimensions

| Dimension | Definition | Enforced by |
|---|---|---|
| **Coherence** | The analysis reads as one mind, not fragments | Lens mode; squad challenge |
| **Evidence** | Every claim is labelled and cited | Gate G2; skill evidence rules |
| **Coverage** | Every repo analyzed; each states what it skipped | Gate G4; brief |
| **Independence** | Critical findings are adversarially tested | Child mode; adversarial pass |
| **Consistency** | Same vocabulary and structure across repos | Schema; glossary; synthesizer |
| **Safety** | No secrets; no repo mutation | Gate G3; read-only rule |
| **Reproducibility** | Results pinned to a revision | Manifest `revision` |

## 2. The coherence problem (and its solution)

The single biggest quality risk at scale is **fragmentation**: many workers each
producing a partial, context-free view. The skill's own method warns against it
(`05-squad-orchestration.md` §5, "single-lens tunnel vision").

**Solution: two-level coherence.**

1. **Within a repo:** personas are lenses in one pass, so the Business Analyst's
   view informs the Architect's. Cross-examination happens inline.
2. **Across repos:** the org synthesizer holds all repo results and produces the
   global view, de-duplicating and promoting cross-repo findings.

A child-mode repo adds a third level: the **lead** reconciles its children before
the synthesizer sees anything. So coherence is enforced at every level up the
tree.

## 3. Tiering: spend quality where it matters

Not all repos deserve the same depth. Tiering is how speed and quality coexist.

| Criticality | Depth | Cost |
|---|---|---|
| Low (small utility) | 1 pass, 12 lenses, brief findings | cheap |
| Medium | 1 pass, 12 lenses, full findings | default |
| High | Squad lead + 5 children + reconciliation | ~6× a pass |
| Critical | High + adversarial pass + human review flag | ~8× + review |

Criticality is assigned from the domain and size (Spec 03 §2): security, payments,
identity, and health are always critical. This concentrates the expensive,
high-quality treatment on the repos where an error is costly.

## 4. Evidence discipline

From the skill's `02-evidence.md`, enforced mechanically by Gate G2:

- **fact** → must cite a path (and a ref where possible).
- **inference** → must carry a confidence.
- **prediction** → must carry a confidence and a basis.
- **unknown** → must state what would resolve it.

A finding without evidence is not a finding. The gate rejects it, so the analyzer
cannot silently produce opinion dressed as fact.

## 5. Adversarial quality (child mode)

For large/critical repos, independence is the quality lever:

- Each persona group works in isolation (its own worktree, its own conversation).
- The lead runs the **squad challenge**: force each group to challenge the
  others' claims; record or resolve disagreements.
- Unresolved disagreements are surfaced, never smoothed over (Gate G5).

This reproduces, at the repo level, the "squad of experts who challenge each
other" that the skill defines.

## 6. Consistency at scale

With hundreds of repos, inconsistent output is a quality defect.

- **One schema** for every repo result (Spec 02).
- **One glossary** maintained by the synthesizer; repos reference it, not their
  own definitions.
- **One document structure** (the seven-file Markdown set) so any repo is
  navigable the same way.
- **One evidence vocabulary** (fact/inference/prediction/unknown; four severity
  levels).

## 7. Speed without quality loss

| Speed lever | Why it does not hurt quality |
|---|---|
| Repo-level parallelism | Each repo is analyzed independently; parallelism adds no interference |
| Sandbox reuse | Warm caches remove setup time, not analysis depth |
| Worktree isolation | Prevents file collisions (the stall incident), improving quality |
| Bundles | Faster starts; the analyzer still sees the whole repo |
| Gates in parallel with the next wave | Failing repos are re-run; passing repos are not delayed |

**What we explicitly do *not* do to go faster:** reduce the persona set, skip the
cross-examination, skip evidence, or lower the tier of critical repos.

## 8. Measuring quality

| Metric | Target | Source |
|---|---|---|
| Schema validity | 100% | Gate G1 |
| Findings with evidence | 100% | Gate G2 |
| Repos with coverage statement | 100% | Gate G4 |
| Secret leaks | 0 | Gate G3 |
| Unresolved disagreements | flagged, ≤ N for non-critical | Gate G5 |
| Broken links | 0 | Gate G6 |
| Cross-repo contradictions surfaced | all | Synthesizer |

These are checkable automatically, so "high quality" is a gate result, not a
claim.

## 9. The quality contract

A run is **publishable** only when:

1. every repo in the manifest has a schema-valid, evidence-complete result;
2. no artifact contains a secret;
3. every disagreement is resolved or explicitly flagged;
4. the org synthesis exists and cites its sources;
5. all links resolve.

Otherwise the failing units are re-run (≤2) or escalated. Speed never overrides
this contract.
