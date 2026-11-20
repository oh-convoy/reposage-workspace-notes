"""Build the /workspace inventory report: repos with remotes, without, and plain folders."""

import json
import subprocess
from pathlib import Path

ROOT = Path("/workspace")
ENV = {"GIT_TERMINAL_PROMPT": "0", "HOME": "/home/openhands", "PATH": "/usr/local/bin:/usr/bin:/bin"}


def git(repo, *args):
    try:
        out = subprocess.run(
            ["git", "-C", str(repo), *args], capture_output=True, text=True, timeout=60, env=ENV
        )
        return out.stdout.strip(), out.returncode
    except Exception:
        return "", 1


data = json.loads((ROOT / ".convoy/inventory.json").read_text())
with_remote = data["with_remote"]

# Plain folders: top-level entries that are not inside any git repo and not venv/cache.
repo_paths = [Path(e["path"]) for e in with_remote] + [ROOT / e["path"] for e in data["without_remote"]]


def in_repo(path: Path) -> bool:
    return any(path == r or r in path.parents for r in repo_paths)


# "github" only holds org directories that each contain repos; it is a container,
# not a standalone folder with content of its own.
skip = {".venv-docs", ".convoy", "__pycache__", ".git", "node_modules", "github"}
plain = []
for entry in sorted(ROOT.iterdir()):
    if entry.name in skip:
        continue
    if entry.is_dir() and not in_repo(entry):
        files = [p for p in entry.rglob("*") if p.is_file() and "__pycache__" not in str(p)]
        plain.append({"path": str(entry), "files": len(files)})
    elif entry.is_file():
        plain.append({"path": str(entry), "files": 1})

lines = []
lines.append("# /workspace Inventory\n")
lines.append(f"Total git repos: {len(with_remote) + len(data['without_remote'])}\n")
lines.append(f"## 1. Git repos WITH a GitHub remote ({len(with_remote)})\n")
lines.append("| Repo | Remote | Branch | Dirty | Unpushed |")
lines.append("|---|---|---|---|---|")
for e in with_remote:
    remote = e["remote"].replace("https://github.com/", "")
    lines.append(
        f"| `{e['rel']}` | {remote} | {e['branch']} | {e['dirty_files']} | {e['unpushed']} |"
    )

lines.append(f"\n## 2. Git repos WITHOUT a GitHub remote ({len(data['without_remote'])})\n")
lines.append("| Repo | Branch | Commits | Dirty |")
lines.append("|---|---|---|---|")
for e in data["without_remote"]:
    commits = git(ROOT / e["rel"], "rev-list", "--count", "HEAD")[0] or "0 (no commits)"
    lines.append(f"| `{e['rel']}` | {e['branch']} | {commits} | {e['dirty_files']} |")

lines.append(f"\n## 3. Plain folders, not git repos ({len(plain)})\n")
lines.append("| Path | Files |")
lines.append("|---|---|")
for e in plain:
    lines.append(f"| `{e['path']}` | {e['files']} |")

report = "\n".join(lines) + "\n"
(ROOT / ".convoy/INVENTORY.md").write_text(report)
print(report)
