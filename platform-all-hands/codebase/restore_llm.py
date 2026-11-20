#!/usr/bin/env python3
"""Restore every clobbered conversation to the platform default LLM.

Default model: `openhands/deepseek-v4.1-flash` via the platform LLM proxy
(`https://llm-proxy.app.all-hands.dev/`). The platform has exactly ONE managed
LLM key; it is fetched per sandbox from `GET /api/keys/llm/managed/current`
using that sandbox's session key. No key is hardcoded or changed here.

A conversation is clobbered when its LLM config has a non-default model or a
missing base_url (i.e. no credentials). It is repaired with a full `switch_llm`
payload (model + base_url + managed key). Running conversations are skipped.

Usage:
  python3 restore_llm.py            # apply
  python3 restore_llm.py --dry-run  # report only
"""

from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.request
from pathlib import Path

DEFAULT_MODEL = "openhands/deepseek-v4.1-flash"
PROXY = "https://llm-proxy.app.all-hands.dev/"
CLOUD = "https://app.all-hands.dev/api/v1"
OUT = Path("/workspace/platform-all-hands/inventory")


def http(url, method="GET", body=None, headers=None, timeout=90):
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(url, data=data, method=method)
    for k, v in (headers or {}).items():
        r.add_header(k, v)
    if data:
        r.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(r, timeout=timeout) as x:
            raw = x.read().decode()
            try:
                return x.status, json.loads(raw or "null")
            except json.JSONDecodeError:
                return x.status, raw
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode(errors="replace")[:250]
    except Exception as e:  # noqa: BLE001
        return "ERR", str(e)[:200]


def running_sandboxes() -> list[dict]:
    key = os.environ["OPENHANDS_API_KEY"]
    _, d = http(f"{CLOUD}/sandboxes/search?limit=100", headers={"Authorization": "Bearer " + key})
    return [s for s in d.get("items", []) if s.get("status") == "RUNNING"]


def managed_key(session_key: str) -> str:
    st, body = http("https://app.all-hands.dev/api/keys/llm/managed/current",
                    headers={"X-Session-API-Key": session_key})
    if st != 200:
        raise RuntimeError(f"managed key fetch failed: {st} {body}")
    return str(body).strip()


def list_conversations(base: str, key: str) -> list[dict]:
    out = []
    for off in range(0, 600, 100):
        st, d = http(f"{base}/api/conversations/search?limit=100&offset={off}",
                     headers={"X-Session-API-Key": key})
        if not isinstance(d, dict):
            break
        items = d.get("items", [])
        out += items
        if len(items) < 100:
            break
    return out


def llm_of(base: str, key: str, cid: str) -> dict:
    st, c = http(f"{base}/api/conversations/{cid}", headers={"X-Session-API-Key": key})
    return ((c.get("agent") or {}).get("llm")) if isinstance(c, dict) else {}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    report = []
    fixed = 0
    for sb in running_sandboxes():
        ssk = sb.get("session_api_key", "")
        agent_url = next((u["url"] for u in sb.get("exposed_urls", []) if u["name"] == "AGENT_SERVER"), None)
        if not agent_url:
            continue
        try:
            mk = managed_key(ssk)
        except Exception as e:  # noqa: BLE001
            print(f"[{sb['id'][:12]}] managed key error: {e}")
            continue
        convs = list_conversations(agent_url, ssk)
        print(f"[{sb['id'][:12]}] {len(convs)} conversations @ {agent_url.split('//')[1][:28]}")
        for c in convs:
            cid = c["id"]
            if c.get("execution_status") == "running":
                continue
            llm = llm_of(agent_url, ssk, cid)
            model, burl = llm.get("model"), llm.get("base_url")
            if model == DEFAULT_MODEL and burl == PROXY:
                continue
            rec = {"sandbox": sb["id"], "id": cid, "title": c.get("title"),
                   "before_model": model, "before_base_url": burl,
                   "status": c.get("execution_status")}
            if not args.dry_run:
                st, r = http(f"{agent_url}/api/conversations/{cid}/switch_llm", "POST",
                             {"llm": {"model": DEFAULT_MODEL, "base_url": PROXY, "api_key": mk}},
                             headers={"X-Session-API-Key": ssk})
                rec["switch_status"] = st
                rec["switch_ok"] = bool(isinstance(r, dict) and r.get("success"))
                if rec["switch_ok"]:
                    fixed += 1
            report.append(rec)
            print(f"   {'DRY ' if args.dry_run else 'FIX '} {cid[:8]} {str(c.get('title'))[:30]:30} "
                  f"{model} -> {DEFAULT_MODEL}")

    OUT.mkdir(parents=True, exist_ok=True)
    if not args.dry_run:
        (OUT / "llm-restore-report.json").write_text(json.dumps(report, indent=2))
    print(f"\n{'would fix' if args.dry_run else 'fixed'}: {len(report)} conversations"
          + (f" ({fixed} confirmed)" if not args.dry_run else ""))


if __name__ == "__main__":
    main()
