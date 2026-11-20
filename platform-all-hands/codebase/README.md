# platform-all-hands — codebase

Small automation apps that talk to the OpenHands platform API.

## Apps

| App | Purpose |
|---|---|
| [`inventory_sandboxes.py`](inventory_sandboxes.py) | Inventory every sandbox and conversation on the platform; write a machine-readable JSON and a human-readable Markdown report |

## Running the inventory

```bash
# API key from the environment (preferred)
export OPENHANDS_API_KEY="<your key>"
python3 inventory_sandboxes.py

# or pass it explicitly
python3 inventory_sandboxes.py --api-key "$OPENHANDS_API_KEY"

# choose the platform and output directory
python3 inventory_sandboxes.py \
  --base-url https://app.all-hands.dev \
  --out-dir ../inventory
```

Output (written to `../inventory` by default):

| File | Audience | Contains secrets? |
|---|---|---|
| `sandboxes.json` | code | **yes** — sandbox `session_api_key` values (mode `0600`) |
| `sandboxes.md` | humans | no — session keys are omitted |

## Design

- **Dependency-free.** Python standard library only (`urllib`, `json`). No pip
  installs.
- **Bearer auth.** The API key is sent as `Authorization: Bearer <key>` and is
  never printed, logged, or written to an artifact.
- **Paginated.** Walks `next_page_id` until the listing is exhausted.
- **Joined.** Each sandbox is linked to the conversations that run on it; a
  conversation whose sandbox is absent is reported as an orphan.
- **Safe output.** The JSON is chmod `0600` because it carries live session keys;
  the Markdown never includes them.

## API surface used

| Endpoint | Method | Returns |
|---|---|---|
| `/api/v1/sandboxes/search` | GET | Sandboxes (paginated) |
| `/api/v1/app-conversations/search` | GET | Conversations (paginated) |

## Notes on credentials

- Prefer the platform's ambient `OPENHANDS_API_KEY`.
- A key stored in a secrets file may be stale; if listing returns HTTP 401
  (`NoCredentialsError`), use a current key instead. Never commit a key.

See [`../inventory/README.md`](../inventory/README.md) for the artifact schema.
