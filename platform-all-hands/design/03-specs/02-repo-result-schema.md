# Spec 02 — Repo Result Schema

The machine-readable output of one repo analysis, plus the Markdown set. This is
the unit that travels between tiers and is aggregated by the org synthesizer.

## 1. JSON Schema (Draft 2020-12)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "openhands.analysis.repo-result.v1",
  "title": "Repo Result",
  "type": "object",
  "required": ["schema", "org", "repo", "revision", "tier", "classification",
               "coverage", "lenses", "findings", "limits", "generated_at"],
  "additionalProperties": false,
  "properties": {
    "schema": { "const": "openhands.analysis.repo-result.v1" },
    "org": { "type": "string" },
    "repo": { "type": "string" },
    "revision": { "type": "string" },
    "tier": { "enum": ["analyzer", "lead"] },
    "generated_at": { "type": "string", "format": "date-time" },
    "classification": {
      "type": "object",
      "required": ["type", "languages", "domain", "size", "age"],
      "properties": {
        "type": { "type": "string" },
        "languages": { "type": "array", "items": { "type": "string" } },
        "domain": { "type": "string" },
        "size": {
          "type": "object",
          "properties": {
            "files": { "type": "integer" },
            "loc": { "type": "integer" },
            "doc_ratio": { "type": "number" }
          }
        },
        "age": {
          "type": "object",
          "properties": {
            "first_commit": { "type": "string" },
            "last_commit": { "type": "string" }
          }
        }
      }
    },
    "coverage": {
      "type": "object",
      "required": ["read", "skipped"],
      "properties": {
        "read": { "type": "array", "items": { "type": "string" } },
        "skipped": { "type": "array", "items": { "type": "string" } }
      }
    },
    "lenses": {
      "type": "array",
      "minItems": 12,
      "items": {
        "type": "object",
        "required": ["persona", "verdict"],
        "properties": {
          "persona": { "enum": [
            "business-analyst", "domain-expert", "principal-architect",
            "senior-software-engineer", "platform-devops-sre", "security-engineer",
            "data-integration-engineer", "qa-test-engineer", "technical-writer",
            "compliance-risk-analyst", "engineering-historian", "cost-finops-analyst"
          ] },
          "verdict": { "type": "string" },
          "finding_ids": { "type": "array", "items": { "type": "string" } }
        }
      }
    },
    "findings": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "persona", "claim", "label", "detail"],
        "properties": {
          "id": { "type": "string", "pattern": "^[A-Z]+-[0-9]+$" },
          "persona": { "type": "string" },
          "claim": { "type": "string" },
          "label": { "enum": ["fact", "inference", "prediction", "unknown"] },
          "severity": { "enum": ["critical", "high", "medium", "low", "none"] },
          "confidence": { "enum": ["high", "medium", "low", "n/a"] },
          "evidence": {
            "type": "array",
            "items": {
              "type": "object",
              "required": ["path"],
              "properties": {
                "path": { "type": "string" },
                "ref": { "type": "string" },
                "quote": { "type": "string" }
              }
            }
          },
          "detail": { "type": "string" }
        }
      }
    },
    "strengths": {
      "type": "array",
      "items": { "type": "object", "required": ["claim", "evidence"] }
    },
    "disagreements": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["between", "positions", "resolution"],
        "properties": {
          "between": { "type": "array", "items": { "type": "string" } },
          "positions": { "type": "array", "items": { "type": "string" } },
          "resolution": { "type": "string" }
        }
      }
    },
    "open_questions": { "type": "array", "items": { "type": "string" } },
    "limits": { "type": "string" },
    "metrics": {
      "type": "object",
      "properties": {
        "wall_clock_seconds": { "type": "number" },
        "tokens": { "type": "integer" },
        "cost_usd": { "type": "number" }
      }
    }
  }
}
```

## 2. Markdown set

Alongside `repo-result.json`, each repo produces:

| File | Content |
|---|---|
| `00-overview.md` | What the repo is; one-paragraph summary; classification |
| `01-method-and-coverage.md` | How it was analyzed; what was read/skipped |
| `02-business-view.md` | Problem, actors, value, rules, scope (Business Analyst + Domain) |
| `03-technical-view.md` | Architecture, data, interfaces, ops (Architect + Data + SRE) |
| `04-findings.md` | Findings by persona, with severity and evidence |
| `05-risks-and-recommendations.md` | Prioritized recommendations; predictions |
| `06-evidence-index.md` | References behind the key claims |

This mirrors the skill's deliverable structure (`03-deliverable.md`).

## 3. Aggregation rules

- The org synthesizer concatenates `findings[]` across repos, de-duplicating by
  `(claim, evidence.path)`.
- Cross-repo findings (dependency, duplication, drift) get ids prefixed `X-`.
- A finding present in more than one repo is promoted to an org-level finding.
- Disagreements that span repos are listed once at the org level.

## 4. Validation

The schema gate (Spec 08) validates every `repo-result.json` against §1. The
`lenses` array must contain exactly the 12 personas; the `findings[].id` must be
unique within a repo.

## 5. Example (illustrative; `lenses` truncated for brevity)

```json
{
  "schema": "openhands.analysis.repo-result.v1",
  "org": "example",
  "repo": "widget",
  "revision": "main@abc1234",
  "tier": "analyzer",
  "generated_at": "2026-11-18T00:00:00Z",
  "classification": {
    "type": "code+docs",
    "languages": ["python"],
    "domain": "developer tooling",
    "size": { "files": 42, "loc": 3100, "doc_ratio": 0.3 },
    "age": { "first_commit": "2026-01-01", "last_commit": "2026-11-01" }
  },
  "coverage": { "read": ["README.md", "src/", "tests/"], "skipped": ["vendor/"] },
  "lenses": [
    { "persona": "business-analyst", "verdict": "clear purpose", "finding_ids": ["BA-1"] },
    { "persona": "security-engineer", "verdict": "one issue", "finding_ids": ["SEC-1"] },
    { "persona": "domain-expert", "verdict": "ok", "finding_ids": [] }
  ],
  "findings": [
    {
      "id": "SEC-1",
      "persona": "security-engineer",
      "claim": "Credential appears in a tracked config file",
      "label": "fact",
      "severity": "high",
      "confidence": "n/a",
      "evidence": [{ "path": "config/settings.py", "ref": "L12" }],
      "detail": "A credential-shaped value is present; location reported, value not reproduced."
    }
  ],
  "strengths": [],
  "disagreements": [],
  "open_questions": [],
  "limits": "vendor/ not read."
}
```
