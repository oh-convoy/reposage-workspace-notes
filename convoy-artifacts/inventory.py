"""Inventory every git repo under /workspace: remote, branch, dirty state, unpushed work."""

import json
import subprocess
from pathlib import Path

ROOT = Path("/workspace")


def git(repo, *args):
    try:
        out = subprocess.run(
            ["git", "-C", str(repo), *args],
            capture_output=True,
            text=True,
            timeout=60,
            env={"GIT_TERMINAL_PROMPT": "0", "HOME": "/home/openhands", "PATH": "/usr/local/bin:/usr/bin:/bin"},
        )
        return out.stdout.strip(), out.returncode
    except Exception:
        return "", 1


repos = sorted(p.parent for p in ROOT.rglob(".git") if p.is_dir() and "node_modules" not in str(p))

with_remote, without_remote = [], []
for repo in repos:
    url, _ = git(repo, "remote", "get-url", "origin")
    branch, _ = git(repo, "rev-parse", "--abbrev-ref", "HEAD")
    dirty, _ = git(repo, "status", "--porcelain")
    ahead, rc = git(repo, "rev-list", "--count", "@{u}..HEAD")
    entry = {
        "path": str(repo),
        "rel": str(repo.relative_to(ROOT)),
        "branch": branch,
        "dirty_files": len([l for l in dirty.splitlines() if l.strip()]),
        "unpushed": int(ahead) if rc == 0 and ahead.isdigit() else None,
    }
    if url:
        entry["remote"] = url
        with_remote.append(entry)
    else:
        without_remote.append(entry)

print(f"TOTAL REPOS: {len(repos)}")
print(f"WITH REMOTE: {len(with_remote)}")
print(f"WITHOUT REMOTE: {len(without_remote)}")
print()
print("=== WITH REMOTE ===")
for e in with_remote:
    print(f"{e['rel']}\n    {e['remote']}  [{e['branch']}] dirty={e['dirty_files']} unpushed={e['unpushed']}")
print()
print("=== WITHOUT REMOTE ===")
for e in without_remote:
    print(f"{e['rel']}  [{e['branch']}] dirty={e['dirty_files']} commits={git(ROOT/e['rel'],'rev-list','--count','HEAD')[0]}")

Path("/workspace/.convoy/inventory.json").write_text(
    json.dumps({"with_remote": with_remote, "without_remote": without_remote}, indent=2)
)
