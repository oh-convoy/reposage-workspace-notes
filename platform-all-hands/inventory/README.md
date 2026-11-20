# platform-all-hands — inventory

Generated inventories of the OpenHands platform. Regenerate with
[`../codebase/inventory_sandboxes.py`](../codebase/inventory_sandboxes.py).

## Artifacts

| File | Audience | Secrets | Notes |
|---|---|---|---|
| `sandboxes.json` | code | **yes** — live `session_api_key` per sandbox | mode `0600`; treat as a secret |
| `sandboxes.md` | humans | no | session keys omitted by design |

## JSON schema (`openhands.sandbox-inventory.v1`)

```jsonc
{
  "schema": "openhands.sandbox-inventory.v1",
  "generated_at": "ISO-8601 UTC",
  "source": { "base_url": "...", "endpoints": ["..."] },
  "summary": {
    "sandbox_count": 21,
    "conversation_count": 20,
    "orphan_conversation_count": 0,
    "sandbox_status_counts": { "PAUSED": 20, "RUNNING": 1 },
    "sandbox_spec_counts": { "ghcr.io/openhands/agent-server:1.62.0-python": 20 }
  },
  "sandboxes": [
    {
      "id": "...",
      "created_by_user_id": "...",
      "credential_org_id": "...",
      "started_by": "APP_CONVERSATION",
      "sandbox_spec_id": "ghcr.io/openhands/agent-server:1.62.0-python",
      "status": "PAUSED",
      "session_api_key": "<secret>",
      "exposed_urls": null,
      "created_at": "2026-11-17T23:58:47.527531Z",
      "last_termination": null,
      "status_detail": null,
      "conversation_count": 1,
      "conversation_ids": ["..."]
    }
  ],
  "orphan_conversations": [],
  "conversations": [
    {
      "id": "...",
      "sandbox_id": "...",
      "title": "...",
      "llm_model": "...",
      "agent_kind": "openhands",
      "sandbox_status": "PAUSED",
      "execution_status": "finished",
      "conversation_url": "...",
      "conversation_ui_url": "...",
      "created_at": "...",
      "updated_at": "..."
    }
  ]
}
```

## Field notes

| Field | Meaning |
|---|---|
| `summary.sandbox_status_counts` | Sandboxes by lifecycle status (`RUNNING`, `PAUSED`, …) |
| `summary.sandbox_spec_counts` | Sandboxes by container image (agent-server version) |
| `sandboxes[].conversation_ids` | Conversations running on that sandbox |
| `orphan_conversations` | Conversations whose sandbox is not in the sandbox listing |
| `session_api_key` | Live credential to reconnect to the sandbox's agent server |

## Handling

- Do not commit `sandboxes.json`; it contains live credentials.
- Do not copy `session_api_key` values anywhere shared.
- Regenerate rather than edit; the files are outputs, not sources.
