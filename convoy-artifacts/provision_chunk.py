"""Provision a slice of the fleet through the Convoy API, resumably.

Usage: python provision_chunk.py <size> <offset>
Already-provisioned sandboxes short-circuit, so re-running a slice is cheap.
"""

import json
import sys
import urllib.request

BASE = "http://127.0.0.1:12001"


def call(method, path, body=None, timeout=3600):
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(body).encode() if body is not None else None,
        method=method,
        headers={"content-type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


size = int(sys.argv[1]) if len(sys.argv) > 1 else 6
offset = int(sys.argv[2]) if len(sys.argv) > 2 else 0

sandboxes = call("GET", "/v1/fleet/sandboxes?limit=200")["items"]
slice_ids = [s["id"] for s in sandboxes][offset : offset + size]

report = call("POST", "/v1/fleet/provision", {"sandbox_ids": slice_ids, "install_cli": True})
print(f"requested={report['requested']} provisioned={report['provisioned']} failed={report['failed']}")
for row in report["results"]:
    ok = row.get("tooling_ok")
    sdk = row.get("sdk", {}).get("version", "")[:32]
    cli = row.get("cli", {}).get("version", "")[:28]
    note = row.get("error", {}).get("message", "")[:50] if not ok else ""
    print(f"  {row['sandbox_id']} ok={ok} {sdk} {cli} {note}")
