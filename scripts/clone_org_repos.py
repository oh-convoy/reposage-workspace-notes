#!/usr/bin/env python3
"""Clone every repository of a GitHub organization, rate-limit safely.

Design goals (prompt 01, Step 2):
  * Authenticated, paginated repository listing.
  * Respect GitHub rate-limit headers and Retry-After; backoff with retries.
  * Throttled, sequential cloning (one repo at a time) to avoid secondary limits.
  * Safe resume: skip repos already cloned, `git fetch` instead of re-cloning.
  * Credentials are read from the environment only and never printed or logged.

Usage:
    export GH_PAT=...            # or GITHUB_TOKEN
    python3 clone_org_repos.py --org org-morluto

Exit codes: 0 success (all repos present), 1 partial failure, 2 fatal.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

API = "https://api.github.com"
DEFAULT_ROOT = "/workspace/github/organization"
USER_AGENT = "RepoSage-clone/1.0"


def log(msg: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"[{ts}] {msg}", flush=True)


def redact(text: str) -> str:
    """Strip anything that looks like a token from a string before logging."""
    text = re.sub(r"gh[pousr]_[A-Za-z0-9]+", "<REDACTED>", text)
    text = re.sub(r"github_pat_[A-Za-z0-9_]+", "<REDACTED>", text)
    text = re.sub(r"x-access-token:[^@\s]+@", "x-access-token:<REDACTED>@", text)
    return text


def get_token() -> str:
    token = os.environ.get("GH_PAT") or os.environ.get("GITHUB_TOKEN")
    if not token:
        log("FATAL: no token in GH_PAT or GITHUB_TOKEN")
        sys.exit(2)
    return token


def api_get(url: str, token: str, attempt: int = 0) -> tuple[list | dict, dict]:
    """GET a GitHub API URL with rate-limit handling and backoff.

    Returns (parsed_json, response_headers).
    """
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": USER_AGENT,
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data, dict(resp.headers)
    except urllib.error.HTTPError as exc:
        headers = dict(exc.headers or {})
        # Secondary / primary rate limit handling.
        if exc.code in (403, 429):
            remaining = headers.get("X-RateLimit-Remaining")
            reset = headers.get("X-RateLimit-Reset")
            retry_after = headers.get("Retry-After")
            if retry_after:
                wait = int(retry_after) + 1
            elif remaining == "0" and reset:
                wait = max(1, int(reset) - int(time.time())) + 1
            else:
                wait = min(60, 2 ** attempt)
            if attempt < 6:
                log(f"rate limited ({exc.code}); sleeping {wait}s (attempt {attempt + 1})")
                time.sleep(wait)
                return api_get(url, token, attempt + 1)
        raise
    except urllib.error.URLError as exc:
        if attempt < 5:
            wait = min(60, 2 ** attempt)
            log(f"network error ({redact(str(exc))}); retrying in {wait}s")
            time.sleep(wait)
            return api_get(url, token, attempt + 1)
        raise


def list_repos(org: str, token: str) -> list[dict]:
    """List all repos in the org, following pagination."""
    repos: list[dict] = []
    page = 1
    while True:
        url = f"{API}/orgs/{org}/repos?per_page=100&page={page}&type=all"
        data, headers = api_get(url, token)
        if not isinstance(data, list):
            raise RuntimeError(f"unexpected API response: {type(data)}")
        repos.extend(data)
        log(f"listed page {page}: {len(data)} repos (total {len(repos)})")
        if len(data) < 100:
            break
        page += 1
        time.sleep(1)  # gentle pacing between listing pages
    return repos


def run_git(args: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
    """Run git with token auth injected via an ephemeral askpass-free URL env.

    We use the header-based extraheader mechanism so the token never appears in
    argv, the remote URL, or on-disk config.
    """
    env = os.environ.copy()
    return subprocess.run(args, cwd=cwd, env=env, capture_output=True, text=True)


def clone_url(repo: str, org: str) -> str:
    # Tokenless HTTPS URL; auth is supplied via the git credential helper
    # configured for github.com, or via extraheader (see configure_auth).
    return f"https://github.com/{org}/{repo}.git"


def configure_auth(token: str) -> dict:
    """Return env vars that inject the token as a Basic Authorization header.

    GitHub git-over-HTTPS expects Basic auth with the username
    `x-access-token`. Using GIT_CONFIG_* keeps the token out of argv, the remote
    URL and on-disk config.
    """
    import base64

    basic = base64.b64encode(f"x-access-token:{token}".encode()).decode()
    return {
        "GIT_CONFIG_COUNT": "1",
        "GIT_CONFIG_KEY_0": "http.https://github.com/.extraheader",
        "GIT_CONFIG_VALUE_0": f"Authorization: Basic {basic}",
    }


def is_cloned(path: Path) -> bool:
    return (path / ".git").is_dir()


def clone_or_fetch(repo: dict, dest_root: Path, token: str) -> str:
    """Clone a repo if absent, else fetch. Returns a status string."""
    name = repo["name"]
    dest = dest_root / name
    auth_env = configure_auth(token)
    url = clone_url(name, repo["owner"]["login"])

    if is_cloned(dest):
        env = os.environ.copy()
        env.update(auth_env)
        res = subprocess.run(
            ["git", "-C", str(dest), "fetch", "--all", "--prune"],
            env=env, capture_output=True, text=True,
        )
        if res.returncode == 0:
            return "fetched"
        log(f"fetch failed for {name}: {redact(res.stderr.strip()[:300])}")
        return "fetch-failed"

    env = os.environ.copy()
    env.update(auth_env)
    # Shallow-less full clone so history is available for deep analysis.
    res = subprocess.run(
        ["git", "clone", "--quiet", url, str(dest)],
        env=env, capture_output=True, text=True,
    )
    if res.returncode == 0:
        return "cloned"
    log(f"clone failed for {name}: {redact(res.stderr.strip()[:300])}")
    return "clone-failed"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--org", required=True, help="GitHub organization login")
    ap.add_argument("--root", default=DEFAULT_ROOT, help="clone root directory")
    ap.add_argument("--throttle", type=float, default=1.0,
                    help="seconds to sleep between clones")
    ap.add_argument("--only", nargs="*", help="clone only these repo names")
    args = ap.parse_args()

    token = get_token()
    dest_root = Path(args.root) / args.org
    dest_root.mkdir(parents=True, exist_ok=True)
    log(f"target directory: {dest_root}")

    repos = list_repos(args.org, token)
    if args.only:
        wanted = set(args.only)
        repos = [r for r in repos if r["name"] in wanted]
    log(f"repositories to process: {len(repos)}")

    summary: dict[str, list[str]] = {
        "cloned": [], "fetched": [], "clone-failed": [], "fetch-failed": [],
    }
    for i, repo in enumerate(sorted(repos, key=lambda r: r["name"]), 1):
        name = repo["name"]
        status = clone_or_fetch(repo, dest_root, token)
        summary[status].append(name)
        size_mb = repo.get("size", 0) / 1024
        log(f"[{i}/{len(repos)}] {name} ({size_mb:.1f} MB): {status}")
        if i < len(repos):
            time.sleep(args.throttle)

    log("summary: " + json.dumps({k: len(v) for k, v in summary.items()}))
    failures = summary["clone-failed"] + summary["fetch-failed"]
    if failures:
        log("failures: " + ", ".join(failures))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
