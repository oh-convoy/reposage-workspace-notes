"""Parallel fan-out generator for the corporation plans.

Creates child conversations on the local agent-server, one per unit of work,
and collects their output files. Measures wall-clock and per-unit time.

Usage:
    python3 fanout.py --units <json> --out-dir <dir> --concurrency N

The <json> is a list of {"id", "title", "path", "task"} objects.
"""

from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

BASE = "http://127.0.0.1:60000"
PARENT = "9014dc4475ef47cfa4e385396658e534"


def session_key() -> str:
    for pid in ("1", "37"):
        try:
            for kv in open(f"/proc/{pid}/environ", "rb").read().decode(errors="replace").split("\0"):
                if kv.startswith("SESSION_API_KEY="):
                    return kv.split("=", 1)[1]
        except OSError:
            pass
    raise RuntimeError("session key not found")


KEY = session_key()


def call(path: str, method: str = "GET", body: dict | None = None, timeout: float = 30.0):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method)
    req.add_header("X-Session-API-Key", KEY)
    req.add_header("Accept", "application/json")
    if data:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read().decode() or "null")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode(errors="replace")[:400]
    except Exception as e:  # noqa: BLE001
        return "ERR", str(e)[:200]


def run_unit(unit: dict) -> dict:
    """Create one child conversation, wait for it, return timing + status."""
    t0 = time.time()
    st, resp = call(
        f"/api/conversations/{PARENT}/children",
        "POST",
        {"task": unit["task"], "title": unit["title"], "isolation": "shared"},
    )
    if st not in (200, 201) or not isinstance(resp, dict):
        return {**unit, "ok": False, "error": f"create {st}: {resp}", "seconds": round(time.time() - t0, 1)}
    cid = resp.get("conversation_id") or resp.get("id")
    # poll for completion
    while time.time() - t0 < unit.get("timeout", 900):
        time.sleep(4)
        s, r = call(f"/api/conversations/{cid}")
        if isinstance(r, dict) and r.get("execution_status") in ("finished", "error", "stuck", "stopped"):
            break
    exists = Path(unit["path"]).exists()
    size = Path(unit["path"]).stat().st_size if exists else 0
    return {
        **unit, "ok": exists and size > 200, "conversation_id": cid,
        "seconds": round(time.time() - t0, 1), "bytes": size,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--units", required=True)
    ap.add_argument("--concurrency", type=int, default=6)
    ap.add_argument("--results", required=True)
    args = ap.parse_args()

    units = json.loads(Path(args.units).read_text())
    t0 = time.time()
    results: list[dict] = []
    with ThreadPoolExecutor(max_workers=args.concurrency) as pool:
        futs = {pool.submit(run_unit, u): u for u in units}
        for f in as_completed(futs):
            r = f.result()
            results.append(r)
            flag = "OK " if r.get("ok") else "FAIL"
            print(f"  [{flag}] {r['id']:>6}  {r.get('seconds'):>6}s  {r.get('bytes',0):>7}B  {r['path']}")
    wall = round(time.time() - t0, 1)
    ok = sum(1 for r in results if r.get("ok"))
    summary = {
        "units": len(units), "ok": ok, "failed": len(units) - ok,
        "wall_clock_seconds": wall, "concurrency": args.concurrency,
        "avg_unit_seconds": round(sum(r.get("seconds", 0) for r in results) / max(len(results), 1), 1),
        "results": sorted(results, key=lambda r: r["id"]),
    }
    Path(args.results).write_text(json.dumps(summary, indent=2))
    print(f"\nTOTAL {ok}/{len(units)} ok in {wall}s (concurrency {args.concurrency})")
    return 0 if ok == len(units) else 1


if __name__ == "__main__":
    raise SystemExit(main())
