# Spec 08 — Quality Gates

Executable checks that run before any artifact is published. Each gate is a
script with a pass/fail exit code and a machine-readable report.

## 1. The six gates

| # | Gate | Checks | Fail action |
|---|---|---|---|
| G1 | **Schema** | every `repo-result.json` validates against Spec 02 | re-run that repo |
| G2 | **Evidence** | every `fact` has ≥1 citation; every `inference` has a confidence | re-run with feedback |
| G3 | **Secret** | no secret-shaped strings in any artifact | block publish; redact |
| G4 | **Coverage** | every repo in the manifest has a result; every result has `coverage` | re-run missing |
| G5 | **Reconciliation** | every `disagreement` has a `resolution`; none open | escalate to human |
| G6 | **Links** | every relative link in the Markdown resolves | fix or flag |

## 2. Gate G1 — Schema

```python
def gate_schema(result: dict) -> list[str]:
    import jsonschema
    errors = list(jsonschema.Draft202012Validator(SCHEMA).iter_errors(result))
    # extra structural checks
    personas = {l["persona"] for l in result.get("lenses", [])}
    if len(personas) != 12:
        errors.append("lenses must contain all 12 personas")
    ids = [f["id"] for f in result.get("findings", [])]
    if len(ids) != len(set(ids)):
        errors.append("finding ids must be unique")
    return [str(e) for e in errors]
```

## 3. Gate G2 — Evidence

```python
def gate_evidence(result: dict) -> list[str]:
    problems = []
    for f in result.get("findings", []):
        if f["label"] == "fact" and not f.get("evidence"):
            problems.append(f"{f['id']}: fact without citation")
        if f["label"] == "inference" and f.get("confidence") in (None, "n/a"):
            problems.append(f"{f['id']}: inference without confidence")
        if f["label"] == "prediction" and f.get("confidence") in (None, "n/a"):
            problems.append(f"{f['id']}: prediction without confidence")
        if f["label"] == "unknown" and not f.get("detail"):
            problems.append(f"{f['id']}: unknown without resolution path")
    return problems
```

## 4. Gate G3 — Secret

```python
import re
PATTERNS = [
    r"ghp_[A-Za-z0-9]{36}", r"github_pat_[A-Za-z0-9_]{20,}",
    r"sk-[A-Za-z0-9_\-]{16,}", r"AKIA[0-9A-Z]{16}",
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
    r"(?i)(password|secret|token)\s*[:=]\s*['\"][^'\"]{8,}['\"]",
]

def gate_secrets(text_blobs: dict[str, str]) -> list[str]:
    hits = []
    for path, text in text_blobs.items():
        for pat in PATTERNS:
            for m in re.finditer(pat, text):
                hits.append(f"{path}: secret-shaped match at offset {m.start()}")
    return hits
```

Any hit **blocks publish** and must be redacted, with the finding rewritten to
report location and type only.

## 5. Gate G4 — Coverage

```python
def gate_coverage(manifest: dict, results: dict[str, dict]) -> list[str]:
    problems = []
    for repo in manifest["repos"]:
        r = results.get(repo["name"])
        if r is None:
            problems.append(f"{repo['name']}: no result")
        elif not r.get("coverage"):
            problems.append(f"{repo['name']}: no coverage statement")
    return problems
```

## 6. Gate G5 — Reconciliation

```python
def gate_reconciliation(results: dict[str, dict]) -> list[str]:
    problems = []
    for repo, r in results.items():
        for d in r.get("disagreements", []):
            if not d.get("resolution"):
                problems.append(f"{repo}: unresolved disagreement {d.get('between')}")
    return problems
```

An unresolved disagreement is not a failure of the pipeline; it is a signal for
human review. The gate records it and, for a critical repo, blocks publish.

## 7. Gate G6 — Links

```python
import os, re, glob

def gate_links(root: str) -> list[str]:
    broken = []
    for path in glob.glob(f"{root}/**/*.md", recursive=True):
        d = os.path.dirname(path)
        for m in re.finditer(r"\]\(([^)]+)\)", open(path, encoding="utf-8").read()):
            t = m.group(1).split("#")[0].strip()
            if not t or t.startswith(("http", "mailto:")):
                continue
            if not os.path.exists(os.path.normpath(os.path.join(d, t))):
                broken.append(f"{path} -> {t}")
    return broken
```

## 8. Gate report

Each run emits `_meta/gate-report.json`:

```jsonc
{
  "run_id": "...",
  "gates": {
    "schema":        { "pass": true,  "problems": [] },
    "evidence":      { "pass": false, "problems": ["SEC-1: fact without citation"] },
    "secrets":       { "pass": true,  "problems": [] },
    "coverage":      { "pass": true,  "problems": [] },
    "reconciliation":{ "pass": true,  "problems": [] },
    "links":         { "pass": true,  "problems": [] }
  },
  "publish_allowed": false
}
```

`publish_allowed` is true only if **all** gates pass.

## 9. Where gates run

```
analyzer/lead pushes result branch
        │
        ▼
orchestrator runs G1–G6 on the branch
        │
   ┌────┴─────┐
 pass       fail
   │          │
merge to    re-run repo with feedback
main        (≤2) → escalate to lead
```

## 10. Continuous quality

At speed, quality is protected by the gates, not by slowing down. The gates are
cheap (schema + regex + link checks) and run in parallel with the next wave, so
they add latency only to the failing repo, never to the whole run.
