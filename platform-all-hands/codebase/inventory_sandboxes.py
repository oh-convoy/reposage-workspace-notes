#!/usr/bin/env python3
"""Inventory every sandbox (and conversation) on an OpenHands platform.

This is a small, dependency-free automation app. It calls the OpenHands Cloud
V1 API, walks the paginated sandbox and app-conversation listings, joins them,
and writes two artifacts:

* ``inventory/sandboxes.json`` — machine-readable inventory for code.
* ``inventory/sandboxes.md``   — the same inventory, human-readable.

Design notes (learned from the Convoy orchestration codebase):
  * The API is Bearer-authenticated with an OpenHands API key.
  * ``GET /api/v1/sandboxes/search`` lists sandboxes; ``GET
    /api/v1/app-conversations/search`` lists conversations; both page with
    ``next_page_id`` and a ``limit``.
  * ``session_api_key`` on a sandbox is a live credential. It is written to the
    JSON (needed to reconnect) but **never** to the human-readable Markdown.
  * Nothing here shells out; it is plain HTTP with the standard library.

Authentication: read the API key from ``OPENHANDS_API_KEY`` (preferred) or pass
``--api-key``. The key is never printed, logged, or written to any artifact.

Usage:
    python3 inventory_sandboxes.py                 # write both artifacts
    python3 inventory_sandboxes.py --out-dir DIR   # choose output directory
    python3 inventory_sandboxes.py --base-url URL  # choose the platform
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_BASE_URL = os.environ.get("OPENHANDS_BASE_URL", "https://app.all-hands.dev")
DEFAULT_OUT_DIR = Path(__file__).resolve().parent.parent / "inventory"
PAGE_LIMIT = 100
MAX_PAGES = 200  # safety stop; far above any realistic page count


class InventoryError(RuntimeError):
    """Raised when the platform API cannot be reached or returns an error."""


class PlatformClient:
    """Minimal, dependency-free client for the OpenHands V1 listing API."""

    def __init__(self, api_key: str, base_url: str = DEFAULT_BASE_URL, timeout: float = 30.0):
        if not api_key:
            raise InventoryError(
                "No API key. Set OPENHANDS_API_KEY or pass --api-key."
            )
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _get(self, path: str, query: dict[str, Any] | None = None) -> Any:
        url = f"{self.base_url}{path}"
        if query:
            url += "?" + urllib.parse.urlencode(query)
        req = urllib.request.Request(url, method="GET")
        req.add_header("Authorization", f"Bearer {self.api_key}")
        req.add_header("Accept", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                payload = resp.read().decode()
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode(errors="replace")[:300]
            raise InventoryError(f"GET {path} -> HTTP {exc.code}: {detail}") from exc
        except urllib.error.URLError as exc:
            raise InventoryError(f"GET {path} -> {exc.reason}") from exc
        if not payload:
            return None
        try:
            return json.loads(payload)
        except json.JSONDecodeError:
            return payload

    def _page_all(self, path: str, *, limit: int = PAGE_LIMIT) -> list[dict]:
        """Walk a paginated ``/search`` endpoint and return every item."""
        collected: list[dict] = []
        page: str | None = None
        for _ in range(MAX_PAGES):
            query: dict[str, Any] = {"limit": limit}
            if page:
                query["page_id"] = page
            resp = self._get(path, query) or {}
            items = resp.get("items") or []
            collected.extend(items)
            page = resp.get("next_page_id")
            if not page or not items:
                break
        return collected

    def sandboxes(self) -> list[dict]:
        return self._page_all("/api/v1/sandboxes/search")

    def conversations(self) -> list[dict]:
        return self._page_all("/api/v1/app-conversations/search")


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _redact_sandbox(sb: dict) -> dict:
    """A copy of a sandbox record with the session key removed."""
    out = dict(sb)
    out.pop("session_api_key", None)
    return out


def build_inventory(
    sandboxes: list[dict], conversations: list[dict], base_url: str
) -> dict:
    """Join sandboxes and conversations into one inventory document."""
    convs_by_sandbox: dict[str, list[dict]] = {}
    for c in conversations:
        sid = c.get("sandbox_id")
        if sid:
            convs_by_sandbox.setdefault(sid, []).append(c)

    sandbox_rows = []
    for sb in sandboxes:
        sid = sb.get("id")
        linked = convs_by_sandbox.get(sid, [])
        sandbox_rows.append(
            {
                **sb,
                "conversation_count": len(linked),
                "conversation_ids": [c.get("id") for c in linked],
            }
        )

    # Conversations whose sandbox is not in the sandbox listing (orphans).
    known = {sb.get("id") for sb in sandboxes}
    orphan_convs = [c for c in conversations if c.get("sandbox_id") not in known]

    status_counts = dict(Counter(sb.get("status") for sb in sandboxes))
    spec_counts = dict(Counter(sb.get("sandbox_spec_id") for sb in sandboxes))

    return {
        "schema": "openhands.sandbox-inventory.v1",
        "generated_at": _iso_now(),
        "source": {
            "base_url": base_url,
            "endpoints": [
                "/api/v1/sandboxes/search",
                "/api/v1/app-conversations/search",
            ],
        },
        "summary": {
            "sandbox_count": len(sandboxes),
            "conversation_count": len(conversations),
            "orphan_conversation_count": len(orphan_convs),
            "sandbox_status_counts": status_counts,
            "sandbox_spec_counts": spec_counts,
        },
        "sandboxes": sandbox_rows,
        "orphan_conversations": orphan_convs,
        "conversations": conversations,
    }


def render_markdown(inv: dict) -> str:
    """Render the inventory as human-readable Markdown (secrets redacted)."""
    s = inv["summary"]
    out: list[str] = []
    out.append("# OpenHands Sandbox Inventory")
    out.append("")
    out.append(f"- **Generated:** {inv['generated_at']}")
    out.append(f"- **Platform:** {inv['source']['base_url']}")
    out.append(f"- **Schema:** `{inv['schema']}`")
    out.append("")
    out.append("## Summary")
    out.append("")
    out.append("| Metric | Value |")
    out.append("|---|---|")
    out.append(f"| Sandboxes | {s['sandbox_count']} |")
    out.append(f"| Conversations | {s['conversation_count']} |")
    out.append(f"| Orphan conversations (no listed sandbox) | {s['orphan_conversation_count']} |")
    for status, n in sorted(s["sandbox_status_counts"].items(), key=lambda kv: str(kv[0])):
        out.append(f"| Sandboxes {status or 'UNKNOWN'} | {n} |")
    out.append("")
    out.append("### Sandbox images")
    out.append("")
    out.append("| Image | Count |")
    out.append("|---|---|")
    for spec, n in sorted(s["sandbox_spec_counts"].items(), key=lambda kv: str(kv[0])):
        out.append(f"| `{spec}` | {n} |")
    out.append("")

    out.append("## Sandboxes")
    out.append("")
    out.append(
        "| Sandbox ID | Status | Image | Started by | Created (UTC) | Conversations |"
    )
    out.append("|---|---|---|---|---|---|")
    for sb in sorted(inv["sandboxes"], key=lambda x: str(x.get("created_at") or "")):
        out.append(
            "| `{id}` | {status} | `{spec}` | {by} | {created} | {n} |".format(
                id=sb.get("id", ""),
                status=sb.get("status", ""),
                spec=sb.get("sandbox_spec_id", ""),
                by=sb.get("started_by") or "—",
                created=(sb.get("created_at") or "")[:19],
                n=sb.get("conversation_count", 0),
            )
        )
    out.append("")

    out.append("## Conversations")
    out.append("")
    out.append("| Conversation ID | Title | Model | Agent | Sandbox | Sandbox status | Execution | Created (UTC) |")
    out.append("|---|---|---|---|---|---|---|---|")
    for c in sorted(inv["conversations"], key=lambda x: str(x.get("created_at") or "")):
        out.append(
            "| `{id}` | {title} | {model} | {agent} | `{sb}` | {sbs} | {ex} | {created} |".format(
                id=c.get("id", ""),
                title=(c.get("title") or "").replace("|", "\\|")[:60],
                model=c.get("llm_model") or "—",
                agent=c.get("agent_kind") or "—",
                sb=c.get("sandbox_id") or "—",
                sbs=c.get("sandbox_status") or "—",
                ex=c.get("execution_status") or "—",
                created=(c.get("created_at") or "")[:19],
            )
        )
    out.append("")

    if inv.get("orphan_conversations"):
        out.append("## Orphan conversations (sandbox not listed)")
        out.append("")
        out.append("| Conversation ID | Sandbox ID | Title | Created (UTC) |")
        out.append("|---|---|---|---|")
        for c in inv["orphan_conversations"]:
            out.append(
                "| `{id}` | `{sb}` | {title} | {created} |".format(
                    id=c.get("id", ""),
                    sb=c.get("sandbox_id") or "—",
                    title=(c.get("title") or "").replace("|", "\\|")[:60],
                    created=(c.get("created_at") or "")[:19],
                )
            )
        out.append("")

    out.append("---")
    out.append("")
    out.append(
        "> Session API keys are intentionally omitted from this Markdown. They are "
        "present only in `sandboxes.json`, which must be treated as a secret."
    )
    out.append("")
    return "\n".join(out)


def write_artifacts(inv: dict, out_dir: Path) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "sandboxes.json"
    md_path = out_dir / "sandboxes.md"
    json_path.write_text(json.dumps(inv, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(render_markdown(inv), encoding="utf-8")
    # The JSON carries live session keys; keep it owner-only.
    try:
        os.chmod(json_path, 0o600)
    except OSError:
        pass
    return json_path, md_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Inventory OpenHands sandboxes.")
    parser.add_argument("--api-key", default=os.environ.get("OPENHANDS_API_KEY", ""))
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)

    def log(msg: str) -> None:
        if not args.quiet:
            print(msg, file=sys.stderr)

    try:
        client = PlatformClient(args.api_key, args.base_url)
        log(f"listing sandboxes from {args.base_url} ...")
        sandboxes = client.sandboxes()
        log(f"  {len(sandboxes)} sandboxes")
        log("listing conversations ...")
        conversations = client.conversations()
        log(f"  {len(conversations)} conversations")

        inv = build_inventory(sandboxes, conversations, args.base_url)
        json_path, md_path = write_artifacts(inv, Path(args.out_dir))
        log(f"wrote {json_path}")
        log(f"wrote {md_path}")
    except InventoryError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
