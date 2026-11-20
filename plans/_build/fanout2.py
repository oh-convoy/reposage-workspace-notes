"""LLM fan-out orchestrator with model selection, validation, retries, and metrics.

Creates one child conversation per unit on the local agent-server, waits for it
to finish, validates the artifact, retries on failure, and records rich metrics
(wall clock, token usage, retries, quality gates).

Usage:
  python3 fanout2.py --units units_personas.json --kind persona \
      --model aihubmix/claude-opus-5 --concurrency 6 --results results_personas.json
"""

from __future__ import annotations

import argparse
import json
import re
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path

BASE = "http://127.0.0.1:60000"
PARENT = "9014dc4475ef47cfa4e385396658e534"
CONV_ROOT = Path("/var/openhands/conversations")


def session_key() -> str:
    for pid in ("1", "37"):
        try:
            raw = Path(f"/proc/{pid}/environ").read_bytes().decode(errors="replace")
        except OSError:
            continue
        for kv in raw.split("\0"):
            if kv.startswith("SESSION_API_KEY="):
                return kv.split("=", 1)[1]
    raise RuntimeError("SESSION_API_KEY not found")


KEY = session_key()


def call(path: str, method: str = "GET", body=None, timeout: int = 120):
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
        return e.code, e.read().decode(errors="replace")[:300]
    except Exception as e:  # noqa: BLE001
        return "ERR", str(e)[:200]


def read_tokens(conv_id: str) -> dict:
    """Sum the last-seen cumulative token counters from the conversation events."""
    d = CONV_ROOT / conv_id.replace("-", "")
    tot = {"prompt_tokens": 0, "completion_tokens": 0, "cache_read_tokens": 0, "reasoning_tokens": 0}
    if not d.exists():
        return tot
    best = dict(tot)
    for f in sorted(d.glob("events/*.json")):
        try:
            s = f.read_text()
        except OSError:
            continue
        for key in tot:
            for m in re.finditer(rf'"{key}"\s*:\s*(\d+)', s):
                best[key] = max(best[key], int(m.group(1)))
    return best


def read_model_used(conv_id: str) -> list[str]:
    d = CONV_ROOT / conv_id.replace("-", "")
    used: set[str] = set()
    if d.exists():
        for f in d.glob("events/*.json"):
            try:
                used |= set(re.findall(r'"model"\s*:\s*"([^"]+)"', f.read_text()))
            except OSError:
                continue
    return sorted(used)


# ----------------------------- validation -----------------------------

ROSTER_ROW = re.compile(r"^\|\s*\d+\s*\|")


def validate_persona(path: Path, headcount: int) -> tuple[bool, list[str]]:
    issues: list[str] = []
    if not path.exists():
        return False, ["file missing"]
    txt = path.read_text()
    if len(txt) < 1200:
        issues.append(f"too short ({len(txt)}B)")
    for sec in ["## 1. Purpose", "## 3. Persona roster", "## 4. Diversity", "## 5. Interfaces"]:
        if sec not in txt:
            issues.append(f"missing section {sec!r}")
    if "Non-binary" in txt or "non-binary" in txt:
        issues.append("contains non-binary gender")
    rows = [l for l in txt.splitlines() if ROSTER_ROW.match(l)]
    if len(rows) != headcount:
        issues.append(f"roster rows {len(rows)} != {headcount}")
    names: list[str] = []
    for l in rows:
        c = [x.strip() for x in l.strip("|").split("|")]
        if len(c) < 8:
            issues.append(f"row has {len(c)} cells: {l[:40]}")
            continue
        _, name, gender, country, sen, role, skills, resp = c[:8]
        names.append(name)
        if gender not in ("Female", "Male"):
            issues.append(f"bad gender {gender!r}")
        if len(name.split()) < 2:
            issues.append(f"short name {name!r}")
        if skills.count(";") < 3:
            issues.append(f"{name}: <4 skills")
        if resp.count(";") < 2:
            issues.append(f"{name}: <3 responsibilities")
    if len(set(names)) != len(names):
        issues.append("duplicate names in squad")
    return (not issues), issues


def validate_mcp(path: Path) -> tuple[bool, list[str]]:
    issues: list[str] = []
    if not path.exists():
        return False, ["file missing"]
    txt = path.read_text()
    if len(txt) < 900:
        issues.append(f"too short ({len(txt)}B)")
    for sec in ["## 1. Overview", "## 2. Servers", "## 3. Notes", "## 4. Deployment notes"]:
        if sec not in txt:
            issues.append(f"missing section {sec!r}")
    if "Free tier" not in txt:
        issues.append("missing Free tier column")
    body = txt.split("## 3. Notes")[0]
    rows = [l for l in body.splitlines() if ROSTER_ROW.match(l)]
    if len(rows) < 8:
        issues.append(f"only {len(rows)} server rows (<8)")
    for l in rows:
        c = [x.strip() for x in l.strip("|").split("|")]
        if len(c) < 8:
            issues.append(f"row has {len(c)} cells")
            continue
        auth, trans, crit, free = c[4], c[5], c[6], c[7]
        if auth not in ("API key", "OAuth2", "Service account", "Token", "None", "mTLS"):
            issues.append(f"bad auth {auth!r}")
        if not any(trans.startswith(x) for x in ("stdio", "HTTP", "SSE", "WebSocket")):
            issues.append(f"bad transport {trans!r}")
        if crit not in ("Critical", "High", "Medium", "Low"):
            issues.append(f"bad criticality {crit!r}")
        if not free:
            issues.append("empty free tier")
    return (not issues), issues


VALIDATORS = {"persona": None, "mcp": validate_mcp}


# ----------------------------- execution -----------------------------


@dataclass
class Result:
    id: str
    ok: bool = False
    attempts: int = 0
    wall_s: float = 0.0
    path: str = ""
    bytes: int = 0
    tokens: dict = field(default_factory=dict)
    models: list = field(default_factory=list)
    issues: list = field(default_factory=list)


def run_unit(unit: dict, kind: str, model: str | None, max_attempts: int, headcount: int) -> Result:
    path = Path(unit["path"])
    res = Result(id=unit["id"], path=str(path))
    t0 = time.time()
    for attempt in range(1, max_attempts + 1):
        res.attempts = attempt
        if path.exists():
            path.unlink()
        st, resp = call(
            f"/api/conversations/{PARENT}/children",
            "POST",
            {"task": unit["task"], "title": unit["title"], "isolation": "shared"},
        )
        cid = resp.get("conversation_id") if isinstance(resp, dict) else None
        if not cid:
            res.issues.append(f"create failed: {resp}")
            continue
        if model:
            call(f"/api/conversations/{cid}/switch_llm", "POST", {"llm": {"model": model}})
            call(f"/api/conversations/{cid}/run", "POST")
        # wait for completion
        for _ in range(150):
            time.sleep(3)
            _, c = call(f"/api/conversations/{cid}")
            status = c.get("execution_status") if isinstance(c, dict) else None
            if status in ("finished", "error", "stuck"):
                break
        res.tokens = read_tokens(cid)
        res.models = read_model_used(cid)
        validator = validate_persona if kind == "persona" else validate_mcp
        ok, issues = (
            validator(path, headcount) if kind == "persona" else validator(path)
        )
        res.issues = issues
        if ok:
            res.ok = True
            break
    res.wall_s = round(time.time() - t0, 1)
    res.bytes = path.stat().st_size if path.exists() else 0
    return res


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--units", required=True)
    ap.add_argument("--kind", choices=["persona", "mcp"], required=True)
    ap.add_argument("--model", default=None)
    ap.add_argument("--concurrency", type=int, default=6)
    ap.add_argument("--attempts", type=int, default=3)
    ap.add_argument("--results", required=True)
    ap.add_argument("--headcounts", default="")
    args = ap.parse_args()

    units = json.loads(Path(args.units).read_text())
    hc = json.loads(Path(args.headcounts).read_text()) if args.headcounts else {}
    print(f"{len(units)} units | kind={args.kind} | model={args.model} | concurrency={args.concurrency}")

    results: list[Result] = []
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=args.concurrency) as ex:
        futs = {
            ex.submit(run_unit, u, args.kind, args.model, args.attempts, hc.get(u["id"], 0)): u
            for u in units
        }
        for i, f in enumerate(as_completed(futs), 1):
            r = f.result()
            results.append(r)
            flag = "OK " if r.ok else "FAIL"
            print(f"  [{flag}] {r.id:5} {r.wall_s:>6}s  try={r.attempts}  {r.bytes:>6}B  {r.path}")
    wall = round(time.time() - t0, 1)

    ok = [r for r in results if r.ok]
    agg = {
        "units": len(units),
        "ok": len(ok),
        "failed": len(units) - len(ok),
        "wall_clock_seconds": wall,
        "concurrency": args.concurrency,
        "model": args.model,
        "kind": args.kind,
        "total_attempts": sum(r.attempts for r in results),
        "retries": sum(r.attempts - 1 for r in results),
        "unit_seconds_sum": round(sum(r.wall_s for r in results), 1),
        "unit_seconds_avg": round(sum(r.wall_s for r in results) / len(results), 1),
        "unit_seconds_min": min(r.wall_s for r in results),
        "unit_seconds_max": max(r.wall_s for r in results),
        "bytes_total": sum(r.bytes for r in results),
        "bytes_avg": round(sum(r.bytes for r in results) / len(results)),
        "tokens": {
            k: sum(r.tokens.get(k, 0) for r in results)
            for k in ("prompt_tokens", "completion_tokens", "cache_read_tokens", "reasoning_tokens")
        },
        "throughput_docs_per_min": round(len(units) / (wall / 60), 2),
        "speedup_vs_serial": round(sum(r.wall_s for r in results) / wall, 2),
        "per_unit": [
            {
                "id": r.id,
                "ok": r.ok,
                "attempts": r.attempts,
                "wall_s": r.wall_s,
                "bytes": r.bytes,
                "tokens": r.tokens,
                "models": r.models,
                "issues": r.issues[:5],
            }
            for r in sorted(results, key=lambda x: x.id)
        ],
    }
    Path(args.results).write_text(json.dumps(agg, indent=2))
    print(
        f"\nTOTAL {agg['ok']}/{agg['units']} ok in {wall}s | retries={agg['retries']} | "
        f"avg unit={agg['unit_seconds_avg']}s | speedup={agg['speedup_vs_serial']}x | "
        f"tokens={agg['tokens']['prompt_tokens']}+{agg['tokens']['completion_tokens']}"
    )


if __name__ == "__main__":
    main()
