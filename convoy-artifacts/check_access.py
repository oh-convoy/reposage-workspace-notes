"""Check, per repo remote, whether GITHUB_TOKEN has push permission."""

import json
import os
import subprocess
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path("/workspace")
TOKEN = os.environ["GITHUB_TOKEN"]
data = json.loads((ROOT / ".convoy/inventory.json").read_text())


def api(slug):
    req = urllib.request.Request(
        f"https://api.github.com/repos/{slug}",
        headers={"Authorization": f"Bearer {TOKEN}", "Accept": "application/vnd.github+json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as exc:
        return {"_status": exc.code}
    except Exception as exc:
        return {"_status": str(exc)}


results = []
for entry in data["with_remote"]:
    url = entry["remote"]
    slug = url.replace("https://github.com/", "").removesuffix(".git")
    info = api(slug)
    if "_status" in info:
        results.append((entry["rel"], slug, f"HTTP {info['_status']}", "-"))
        continue
    perms = info.get("permissions", {})
    results.append(
        (entry["rel"], slug, "push" if perms.get("push") else "read-only", info.get("visibility", "?"))
    )

by_status = {}
for _, _, status, _ in results:
    by_status.setdefault(status, []).append(1)

print("=== ACCESS SUMMARY ===")
for status, items in sorted(by_status.items()):
    print(f"{status}: {len(items)}")
print()
print("=== NOT PUSHABLE ===")
for rel, slug, status, vis in results:
    if status != "push":
        print(f"{rel}  ->  {slug}  [{status}]")

(ROOT / ".convoy/access.json").write_text(json.dumps(results, indent=2))
