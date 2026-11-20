#!/usr/bin/env python3
"""Collect per-repo evidence for the deep analysis.

Gathers verifiable facts (title, lead paragraph, structure, git history,
licenses, CI, non-English counts) into one JSON file so the analysis dossiers
cite real evidence rather than memory.
"""

from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ORG_DIR = Path("/workspace/github/organization/org-morluto")
ANALYSIS_DIR = Path("/workspace/github/organization/org-morluto-analysis")
META_TSV = Path("/tmp/recon/meta.tsv")
OUT = ANALYSIS_DIR / "_inventory" / "repo-evidence.json"


def git(repo: Path, *args: str) -> str:
    try:
        return subprocess.run(["git", "-C", str(repo), *args],
                              capture_output=True, text=True, timeout=30).stdout.strip()
    except Exception:
        return ""


def clean_lead(text: str) -> str:
    lines = []
    for ln in text.splitlines():
        s = ln.strip()
        if not s:
            if lines:
                break
            continue
        if s.startswith(("#", "<", "![", "[![", ">", "---", "|", "```", "<img")):
            continue
        s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)
        s = re.sub(r"[*_`>#]+", "", s).strip()
        if s:
            lines.append(s)
    return " ".join(lines)[:400]


def read_readme(repo: Path) -> tuple[str, str]:
    for name in ("README.md", "readme.md", "README.rst", "README.txt", "README"):
        p = repo / name
        if p.is_file():
            try:
                txt = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            title = ""
            for ln in txt.splitlines():
                m = re.match(r"^#{1,3}\s+(.+)", ln.strip())
                if m:
                    title = re.sub(r"\[!\[.*?\]\(.*?\)\]", "", m.group(1)).strip()
                    break
            return title[:120], clean_lead(txt)
    return "", ""


def main() -> None:
    meta = {}
    if META_TSV.is_file():
        for line in META_TSV.read_text().splitlines():
            parts = line.split("\t")
            if len(parts) >= 9:
                meta[parts[0]] = {
                    "language": parts[1], "size_kb": parts[2],
                    "default_branch": parts[3], "created": parts[4],
                    "pushed": parts[5], "license": parts[6],
                    "topics": parts[7], "description": parts[8],
                }

    inv_summary = json.loads((ANALYSIS_DIR / "_inventory" / "_summary.json").read_text())
    inv_by_repo = {r["repo"]: r for r in inv_summary["repos"]}

    repos = []
    for d in sorted(ORG_DIR.iterdir()):
        if not d.is_dir() or d.name.startswith("_") or not (d / ".git").is_dir():
            continue
        title, lead = read_readme(d)
        top = sorted(p.name for p in d.iterdir()
                     if p.name != ".git")
        commits = git(d, "rev-list", "--count", "HEAD")
        first = git(d, "log", "--reverse", "--format=%ad", "--date=short").splitlines()
        last = git(d, "log", "-1", "--format=%ad", "--date=short")
        sha = git(d, "rev-parse", "HEAD")[:12]
        branch = git(d, "rev-parse", "--abbrev-ref", "HEAD")
        tracked = git(d, "ls-files").splitlines()
        authors = {}
        for a in git(d, "log", "--format=%an").splitlines():
            authors[a] = authors.get(a, 0) + 1
        ci = len(list((d / ".github" / "workflows").glob("*.y*ml"))) \
            if (d / ".github" / "workflows").is_dir() else 0
        m = meta.get(d.name, {})
        repos.append({
            "repo": d.name,
            "title": title,
            "lead": lead,
            "language": m.get("language") or "",
            "license": m.get("license") or "",
            "size_kb": m.get("size_kb") or "",
            "default_branch": branch or m.get("default_branch") or "",
            "created": m.get("created", "")[:10],
            "pushed": m.get("pushed", "")[:10],
            "topics": m.get("topics") or "",
            "description": m.get("description") or "",
            "commits": int(commits) if commits.isdigit() else 0,
            "first_commit": first[0] if first else "",
            "last_commit": last,
            "head_sha": sha,
            "tracked_files": len(tracked),
            "authors": dict(sorted(authors.items(), key=lambda kv: -kv[1])[:5]),
            "top_level": top[:30],
            "has_agents_md": (d / "AGENTS.md").is_file(),
            "has_contributing": any((d / n).is_file() for n in
                                    ("CONTRIBUTING.md", "CONTRIBUTING.rst")),
            "has_ci": ci > 0,
            "ci_workflows": ci,
            "docs": inv_by_repo.get(d.name, {}).get("documents", 0),
            "non_english": inv_by_repo.get(d.name, {}).get("non_english", 0),
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "org": "org-morluto",
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "repo_count": len(repos),
        "repos": repos,
    }, indent=2), encoding="utf-8")
    print(f"wrote {OUT} with {len(repos)} repos")


if __name__ == "__main__":
    main()
