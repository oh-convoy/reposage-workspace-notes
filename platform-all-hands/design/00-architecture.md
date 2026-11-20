# 00 — Architecture

The reference architecture for ultra-deep analysis of hundreds of repositories at
high speed and high quality.

## 1. The core insight

Two mistakes are easy to make and both destroy the goal:

1. **One persona per sandbox.** Wastes the 20-sandbox budget on *roles* instead of
   *repositories*, and fragments the analysis: an architect who never sees the
   business context produces worse findings than one reasoning pass that holds
   both.
2. **One full org clone per sandbox.** Multiplies storage and clone time by the
   number of workers, and makes results harder to merge. The organization is
   cloned **once**, into the artifact repository, and distributed by reference.

The correct model treats the problem as a **2-D matrix**:

```
                 personas (the depth / lenses)
              BA  Dom  Arch  Eng  SRE  Sec  Data  QA  Doc  Comp  Hist  Fin
            ┌───┬────┬────┬────┬────┬────┬────┬───┬────┬────┬────┬────┐
  repo 1    │ ● │ ●  │ ●  │ ●  │ ●  │ ●  │ ●  │ ● │ ●  │ ●  │ ●  │ ●  │  ← one analyzer
  repo 2    │ ● │ ●  │ ●  │ ●  │ ●  │ ●  │ ●  │ ● │ ●  │ ●  │ ●  │ ●  │    conversation
  ...       │   │    │    │    │    │    │    │   │    │    │    │    │    covers a whole row
  repo N    │ ● │ ●  │ ●  │ ●  │ ●  │ ●  │ ●  │ ● │ ●  │ ●  │ ●  │ ●  │
            └───┴────┴────┴────┴────┴────┴────┴───┴────┴────┴────┴────┘
```

- **Rows = parallel repos** → mapped to **sandboxes** (width, bounded by 20).
- **Columns = personas** → mapped to **lenses within a conversation**, or to
  **child conversations** when a repo warrants it (depth, unbounded).
- **The org column-sum** → one **Org Synthesizer** conversation.

## 2. The three tiers

```
┌────────────────────────────────────────────────────────────────────────────┐
│ TIER 3 — ORG SYNTHESIZER (1 conversation)                                  │
│   reads every repo result; writes the org-level analysis; cross-repo map   │
└───────────────▲────────────────────────────────────────────────────────────┘
                │ structured repo results (JSON + MD)
┌───────────────┴────────────────────────────────────────────────────────────┐
│ TIER 2 — SQUAD LEAD (1 per large/critical repo, or shared across a wave)   │
│   orchestrates personas; fans out child conversations; reconciles findings │
└───────▲──────────────────────────────────▲─────────────────────────────────┘
        │ persona finding sets             │ persona finding sets
┌───────┴──────────────┐          ┌────────┴─────────────┐
│ TIER 1 — ANALYZER #1 │   ...    │ TIER 1 — ANALYZER #K │   (K ≤ 20)
│  one repo per conv.  │          │  one repo per conv.  │
│  12 personas as      │          │  12 personas as      │
│  lenses (single      │          │  lenses (single      │
│  reasoning pass)     │          │  reasoning pass)     │
└──────────────────────┘          └──────────────────────┘
        ▲                                  ▲
        └────────── shared warm base ──────┘
           (clone once · caches · services)
```

### Tier 1 — Repo Analyzer

- **Unit:** one repository.
- **Where:** a conversation on a sandbox (many analyzers share a sandbox).
- **How:** the analyzer reads the repo and applies all 12 persona *lenses* in one
  coherent pass, guided by the skill documents. It emits a **Repo Result** (see
  [`03-specs/02-repo-result-schema.md`](03-specs/02-repo-result-schema.md)).
- **Why lenses, not children:** the personas cross-examine each other
  (`05-squad-orchestration.md`). That cross-examination needs one mind holding
  the whole repo. Splitting personas into separate conversations *loses* the
  cross-examination unless a lead reconciles them (Tier 2).

### Tier 2 — Squad Lead

- **Unit:** one large or critical repository, or a batch of small repos in a wave.
- **How:** the lead runs the persona fan-out: one **child conversation** per
  persona (or per persona-group), each worktree-isolated, each returning a
  structured finding set. The lead then **reconciles** (the squad-challenge step)
  and writes the Repo Result.
- **When to use it:** when a repo is big enough that one pass exceeds a sane
  context/time budget, or when quality demands a genuine adversarial pass
  (e.g. a security-critical repo).

### Tier 3 — Org Synthesizer

- **Unit:** the whole organization.
- **How:** one conversation reads every Repo Result and writes the org-level
  documents (overview, relationships, risks, glossary, business view).
- **Why one:** cross-repo relationships (duplication, dependency graphs,
  fragmentation) are only visible from above. This is exactly the oh-convoy
  finding: three implementations and four doc sets were only evident at the org
  level.

## 3. The two axes, precisely

### 3.1 Width axis — repositories → sandboxes

- One **sandbox** runs several **analyzer conversations** (one repo each).
- The number of sandboxes in flight is bounded by the pool (20) and by CPU.
- **Rule:** a sandbox hosts **3–5 analyzers** if the work is LLM/IO-bound; **1–2**
  if any analyzer runs heavy local compute (builds, tests, indexing).

### 3.2 Depth axis — personas → lenses or children

| Repo size / criticality | Persona mapping | Rationale |
|---|---|---|
| Small (< ~50 files) | **All 12 as lenses** in one conversation | Cheap; one pass is enough |
| Medium | 12 lenses, with an explicit cross-examination step | The default |
| Large | **Squad Lead + child conversations** per persona-group | Exceeds a single pass |
| Critical (security, money, PII) | **Squad Lead + one child per persona**, adversarial | Quality demands independence |

## 4. Where code and artifacts live

**Do not clone the organization into every sandbox.** Use a single source of
truth and distribute by reference.

```
central artifacts repo (e.g. <org>-analysis)         ← the only clone that persists
  /repos/<repo>.bundle            (bare git bundles, one per repo)
  /results/<repo>/repo-result.json + *.md
  /org/*.md
  /manifests/run-<id>.json        (the run plan: which repo → which worker)
```

- **Bundles, not clones, travel.** A worker fetches `repos/<repo>.bundle`,
  creates its worktree from it, analyzes, and pushes a *result branch* back.
- **The base image** already contains the toolchain and warm caches, so no worker
  reinstalls dependencies.
- **Results are small** (Markdown + JSON), so they merge cheaply and are the only
  thing that must be centralized.

## 5. Topology — hub-and-spoke, applied

```
        ┌─────────────────────────── CENTRAL (hub) ──────────────────────────┐
        │  artifacts repo · run manifest · result aggregation · org synth    │
        └───────▲───────────────────────────────────────────────▲────────────┘
                │ results push                                   │ results push
   ┌────────────┴───────────┐                     ┌──────────────┴───────────┐
   │ SANDBOX 1 (workshop)   │      ...            │ SANDBOX K (workshop)     │
   │  analyzer(repo A)      │                     │  analyzer(repo K)        │
   │  analyzer(repo B)      │                     │  squad-lead(repo L)      │
   │  └ child(persona) ×N   │                     │   └ child(persona) ×N    │
   └────────────────────────┘                     └──────────────────────────┘
```

- **Hub** = the orchestrator + the artifacts repo.
- **Spokes** = sandboxes running analyzers.
- **Reuse:** sandboxes are **paused, not destroyed**, between waves; the warm
  base means a new wave starts in seconds at **zero quota cost**.

## 6. Data flow

```
1. ORCHESTRATOR builds the run manifest:
     list repos → size each → assign tier (analyzer | lead) → assign sandbox
2. WARM BASE: clone org once into bundles; bake the base image; start services
3. DISTRIBUTE: each worker fetches its repo bundle; creates a worktree
4. ANALYZE: Tier 1 (lenses) or Tier 2 (children) → Repo Result
5. COLLECT: worker pushes Repo Result to the artifacts repo
6. SYNTHESIZE: Org Synthesizer reads all Repo Results → org documents
7. GATE: quality gates run (see 05-quality-model.md) before publish
```

## 7. Concurrency and sizing

| Parameter | Default | Notes |
|---|---|---|
| Sandboxes in flight | **≤ 20** | The hard width budget |
| Analyzers per sandbox | **3–5** | LLM/IO-bound; reduce if any does heavy compute |
| Personas per analyzer | **12 lenses** | One pass; cross-examination inline |
| Child conversations per lead | **≤ 5** | Box has 4 CPU / 16 GiB; oversubscription stalls |
| Wave size | **≤ 20 repos** | One wave per sandbox pool |
| Blocking work | **forbidden in analyzers** | Root cause of the stall incident |

## 8. Why not the alternatives

| Alternative | Verdict | Reason |
|---|---|---|
| One persona per sandbox | **Rejected** | Burns the pool on roles; fragments reasoning; loses cross-examination |
| Full org clone per sandbox | **Rejected** | N× storage/clone cost; harder merges; no quality gain |
| Sandboxes as MCP servers (for personas) | **Rejected for analysis** | Adds a hop + state sync + failure mode; no quality gain. See `06-mcp-evaluation.md` |
| One giant single-conversation pass over all repos | **Rejected** | Context blow-up; no parallelism; quality collapses at scale |

See [`04-decision-record.md`](04-decision-record.md) for the full ADRs.
