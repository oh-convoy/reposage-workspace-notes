# Spec 03 — Run Manifest Schema

The run manifest is the orchestrator's plan: which repository goes to which tier,
which wave, and which sandbox slot. It is the single source of truth for a run.

## 1. JSON Schema (Draft 2020-12)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "openhands.analysis.run-manifest.v1",
  "type": "object",
  "required": ["schema", "run_id", "org", "created_at", "config", "repos"],
  "properties": {
    "schema": { "const": "openhands.analysis.run-manifest.v1" },
    "run_id": { "type": "string" },
    "org": { "type": "string" },
    "created_at": { "type": "string", "format": "date-time" },
    "config": {
      "type": "object",
      "required": ["sandbox_pool_size", "analyzers_per_sandbox", "wave_size"],
      "properties": {
        "sandbox_pool_size": { "type": "integer", "default": 20 },
        "analyzers_per_sandbox": { "type": "integer", "default": 4 },
        "max_children_per_lead": { "type": "integer", "default": 5 },
        "wave_size": { "type": "integer" },
        "base_image": { "type": "string" },
        "skills_path": { "type": "string" }
      }
    },
    "repos": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["name", "bundle", "revision", "tier", "wave", "slot"],
        "properties": {
          "name": { "type": "string" },
          "bundle": { "type": "string" },
          "revision": { "type": "string" },
          "size": {
            "type": "object",
            "properties": {
              "files": { "type": "integer" },
              "loc": { "type": "integer" }
            }
          },
          "criticality": { "enum": ["low", "medium", "high", "critical"] },
          "tier": { "enum": ["analyzer", "lead"] },
          "wave": { "type": "integer" },
          "slot": { "type": "integer", "minimum": 1, "maximum": 20 },
          "personas": {
            "type": "array",
            "items": { "type": "string" },
            "description": "In lens mode: all 12. In lead mode: the child groups."
          },
          "status": {
            "enum": ["pending", "running", "done", "failed", "gated"]
          },
          "attempts": { "type": "integer", "default": 0 }
        }
      }
    }
  }
}
```

## 2. Tier assignment rules

```
criticality = f(domain, size, data_sensitivity)
  - domain in {security, payments, identity, health} → critical
  - files > 400 or loc > 40_000                    → high
  - otherwise                                       → low/medium

tier = "lead" if (criticality in {high, critical}) else "analyzer"
```

## 3. Wave/slot assignment

```
repos_sorted = repos sorted by (criticality desc, size desc)
wave_size    = sandbox_pool_size × analyzers_per_sandbox
for i, repo in enumerate(repos_sorted):
    repo.wave = i // wave_size + 1
    repo.slot = (i % sandbox_pool_size) + 1
```

- `slot` is the sandbox index (1..20); it repeats across waves so the **same 20
  sandboxes are reused**.
- `analyzers_per_sandbox` is reduced to 1–2 for repos flagged heavy-compute.

## 4. Status lifecycle

```
pending → running → done
                 ↘ failed → (retry ≤ 2) → pending
                 ↘ gated  → (gate feedback) → running
```

The orchestrator persists the manifest after every state change, so a run is
resumable.

## 5. Example (fragment)

```json
{
  "schema": "openhands.analysis.run-manifest.v1",
  "run_id": "2026-11-18T02:00Z-oh-convoy",
  "org": "oh-convoy",
  "created_at": "2026-11-18T02:00:00Z",
  "config": {
    "sandbox_pool_size": 20,
    "analyzers_per_sandbox": 4,
    "max_children_per_lead": 5,
    "wave_size": 80,
    "base_image": "ghcr.io/openhands/agent-server:1.62.0-python",
    "skills_path": "/workspace/skills"
  },
  "repos": [
    {
      "name": "Convoy-OpenHands-Orchestration",
      "bundle": "repos/Convoy-OpenHands-Orchestration.bundle",
      "revision": "main@2ffa3e5",
      "size": { "files": 180, "loc": 12000 },
      "criticality": "high",
      "tier": "lead",
      "wave": 1,
      "slot": 1,
      "personas": ["intent", "structure", "implementation", "operations", "knowledge"],
      "status": "pending",
      "attempts": 0
    }
  ]
}
```
