"""A minimal data-plane MCP server: it serves tools over the data it can see.

Run in a container with the target repo mounted read-only. Exposes two tools:
  - repo_stats(path)  : file/line counts for a directory
  - find_todos(path)  : lines containing TODO/FIXME

Transport: stdio (default) or streamable-http when MCP_TRANSPORT=http.
"""

from __future__ import annotations

import os
from pathlib import Path

from fastmcp import FastMCP

mcp = FastMCP("data-plane-demo")


def _iter_files(root: Path, limit: int = 20000):
    n = 0
    for p in root.rglob("*"):
        if p.is_file():
            yield p
            n += 1
            if n >= limit:
                return


@mcp.tool()
def repo_stats(path: str) -> dict:
    """Return file and line counts for a directory tree."""
    root = Path(path)
    if not root.is_dir():
        return {"error": f"not a directory: {path}"}
    files = lines = 0
    for p in _iter_files(root):
        try:
            with p.open("rb") as fh:
                lines += sum(1 for _ in fh)
            files += 1
        except OSError:
            continue
    return {"path": path, "files": files, "lines": lines}


@mcp.tool()
def find_todos(path: str, max_hits: int = 50) -> list[dict]:
    """Find TODO/FIXME markers under a directory."""
    root = Path(path)
    hits: list[dict] = []
    for p in _iter_files(root):
        try:
            for i, line in enumerate(p.open("r", errors="ignore"), 1):
                if "TODO" in line or "FIXME" in line:
                    hits.append({"file": str(p), "line": i, "text": line.strip()[:120]})
                    if len(hits) >= max_hits:
                        return hits
        except OSError:
            continue
    return hits


if __name__ == "__main__":
    transport = os.getenv("MCP_TRANSPORT", "stdio")
    if transport == "http":
        mcp.run(transport="http", host="0.0.0.0", port=int(os.getenv("MCP_PORT", "12000")))
    else:
        mcp.run(transport="stdio")
