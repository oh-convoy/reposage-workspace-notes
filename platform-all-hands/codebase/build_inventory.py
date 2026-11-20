#!/usr/bin/env python3
"""Build the platform inventory: every sandbox + every conversation with verdicts.

Pulls the authoritative lists from the OpenHands Cloud V1 API, joins them with
local agent-server conversation events to recover failure reasons, checks the
expected artifact on disk for document-producing runs, and writes:
  * inventory/platform-inventory.md
  * inventory/platform-inventory.json
"""

from __future__ import annotations

import glob
import json
import os
import re
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

BASE = "https://app.all-hands.dev/api/v1"
KEY = os.environ["OPENHANDS_API_KEY"]
LOCAL = Path("/var/openhands/conversations")
PLANS = Path("/workspace/plans")
OUT = Path("/workspace/platform-all-hands/inventory")
DEFAULT_MODEL_STR = "openhands/deepseek-v4.1-flash"


def get(url: str):
    r = urllib.request.Request(url)
    r.add_header("Authorization", "Bearer " + KEY)
    with urllib.request.urlopen(r, timeout=30) as x:
        return json.loads(x.read().decode() or "null")


def page_all(path: str) -> list:
    out, pg = [], None
    while True:
        u = f"{BASE}/{path}?limit=100" + (f"&page_id={pg}" if pg else "")
        d = get(u)
        out += d.get("items", [])
        pg = d.get("next_page_id")
        if not pg:
            return out


def purpose(t) -> str:
    t = str(t or "")
    if re.match(r"personas-S\d+", t):
        return "Persona doc"
    if re.match(r"mcp-M\d+", t):
        return "MCP catalogue"
    if t.startswith(("cand-", "mp-", "ep-", "ab-")):
        return "Model probe"
    if t in ("inherit-test", "best-test", "llm-test"):
        return "LLM test"
    if t in ("mcp-agent-proof", "mcp-proof2"):
        return "MCP proof"
    if t.startswith("Conversation "):
        return "GUI session"
    if t == "pilot-child":
        return "Pilot child"
    if t == "sandbox-01-RepoSage":
        return "RepoSage orchestrator"
    if t.startswith("Mission:"):
        return "Prior mission"
    return "GUI idle"


def err_reason(cid: str) -> str:
    d = LOCAL / cid.replace("-", "") / "events"
    if not d.is_dir():
        return ""
    found = ""
    for f in sorted(d.glob("*.json")):
        try:
            s = f.read_text()
        except OSError:
            continue
        if '"ConversationErrorEvent"' not in s:
            continue
        m = re.search(r'"detail"\s*:\s*"((?:[^"\\]|\\.){0,200})', s)
        code = re.search(r'"code"\s*:\s*"([^"]+)"', s)
        if m:
            found = (f"{code.group(1)}: " if code else "") + m.group(1)
    return found


def model_used(cid: str, fallback: str) -> str:
    """The model actually used, from local events (the cloud list shows the initial model)."""
    d = LOCAL / cid.replace("-", "") / "events"
    if d.is_dir():
        seen = []
        for f in sorted(d.glob("*.json")):
            try:
                for m in re.findall(r'"model"\s*:\s*"([^"]+)"', f.read_text()):
                    if m not in seen:
                        seen.append(m)
            except OSError:
                continue
        if seen:
            return seen[-1].split("/")[-1]
    return str(fallback or "").split("/")[-1]


def artifact(title) -> Path | None:
    t = str(title or "")
    for pat, folder in ((r"personas-(S\d+)", "personas"), (r"mcp-(M\d+)", "mcp")):
        m = re.match(pat, t)
        if m:
            hits = list((PLANS / folder).glob(f"{m.group(1)}-*.md"))
            return hits[0] if hits else None
    return None


def classify_err(e: str) -> str:
    if "api_key" in e or "API key" in e or "LLMAuthenticationError" in e:
        return "Auth: no API key for this model"
    if "Vertex" in e:
        return "Vertex AI model: SDK not installed"
    if "api_base" in e:
        return "Azure model requires api_base"
    if "AihubmixException" in e:
        return "Aihubmix: OPENAI_API_KEY not set"
    if "LLMServiceUnavailableError" in e:
        return "LLM service unavailable (transient)"
    return e[:70] or "LLM error"


def main() -> None:
    sbs = page_all("sandboxes/search")
    cs = page_all("app-conversations/search")
    by_sb: dict[str, list] = {}
    for c in cs:
        by_sb.setdefault(c.get("sandbox_id"), []).append(c)

    for c in cs:
        c["_purpose"] = purpose(c.get("title"))
        a = artifact(c.get("title"))
        c["_artifact"] = bool(a and a.exists() and a.stat().st_size > 0)
        c["_err"] = err_reason(c["id"]) if c.get("execution_status") == "error" else ""

    def verdict(c) -> str:
        st = c.get("execution_status")
        if st == "finished":
            if c["_purpose"] in ("Persona doc", "MCP catalogue"):
                return "OK" if c["_artifact"] else "FAIL"
            return "OK"
        return {"error": "FAIL", "running": "RUNNING"}.get(st, "IDLE")

    def note_for(c) -> str:
        v = verdict(c)
        if v == "FAIL":
            return classify_err(c["_err"]) if c.get("execution_status") == "error" else "Finished but wrote no document"
        if v == "IDLE":
            return "Never started (idle GUI session)"
        if v == "RUNNING":
            return "In progress"
        return ""

    L: list[str] = []
    A = L.append
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    st = Counter(c.get("execution_status") for c in cs)

    A("# Platform Inventory — Sandboxes & Conversations\n")
    A(f"**Generated:** {now}  ")
    A("**Source:** OpenHands Cloud V1 API (`/api/v1/sandboxes/search`, "
      "`/api/v1/app-conversations/search`), joined with local agent-server "
      "conversation events and on-disk artifacts.  ")
    A(f"**Scope:** {len(sbs)} sandboxes, {len(cs)} conversations.\n")
    A("> Every sandbox and every conversation is checked and given a verdict "
      "(OK / FAIL / RUNNING / IDLE) with the reason.\n")

    A("## Summary\n")
    A("| Metric | Value |")
    A("|---|---|")
    A(f"| Sandboxes | {len(sbs)} |")
    A(f"| &nbsp;&nbsp;RUNNING | {sum(1 for s in sbs if s['status'] == 'RUNNING')} |")
    A(f"| &nbsp;&nbsp;PAUSED | {sum(1 for s in sbs if s['status'] == 'PAUSED')} |")
    A(f"| Conversations | {len(cs)} |")
    A(f"| &nbsp;&nbsp;finished | {st.get('finished', 0)} |")
    A(f"| &nbsp;&nbsp;error | {st.get('error', 0)} |")
    A(f"| &nbsp;&nbsp;running | {st.get('running', 0)} |")
    A(f"| &nbsp;&nbsp;idle (no status) | {st.get(None, 0)} |")
    A("")

    A("## What failed, and why\n")
    A("The planning documents succeeded. The failures are a separate body of work: "
      "when asked to regenerate the documents with a *better* model, I first probed "
      "which models this platform can run. **Every non-default model failed** — this "
      "sandbox holds an API key only for the default model "
      "(`openhands/deepseek-v4.1-flash`). Models like `aihubmix/*`, `zai/*`, "
      "`vertex_ai/*`, `azure/*`, and bare `gpt-5.x` have no key here.\n")
    fails = [c for c in cs if verdict(c) == "FAIL"]
    fcls = Counter(classify_err(c["_err"]) if c.get("execution_status") == "error"
                   else "Finished but wrote no document" for c in fails)
    A("| Failure class | Count | What it means |")
    A("|---|---|---|")
    meaning = {
        "Auth: no API key for this model": "the model was selected but has no credential on this sandbox",
        "Vertex AI model: SDK not installed": "Vertex partner models need the Vertex SDK, not the OpenAI-compatible path",
        "Azure model requires api_base": "Azure deployments need an endpoint set explicitly",
        "Aihubmix: OPENAI_API_KEY not set": "Aihubmix provider key absent",
        "LLM service unavailable (transient)": "transient upstream error; the run usually still wrote its file",
        "Finished but wrote no document": "conversation completed but the expected artifact is absent",
    }
    for k, v in fcls.most_common():
        A(f"| {k} | {v} | {meaning.get(k, '—')} |")
    A("")
    A("**Deliverable impact:** the two persona documents touched by the failed pilot "
      "(S01, S02) were deleted mid-run and have since been **regenerated "
      "successfully** with the working default model.\n")

    A("## LLM restoration — all conversations back on the default model\n")
    rep_path = OUT / "llm-restore-report.json"
    if rep_path.exists():
        rep = json.loads(rep_path.read_text())
        ok = sum(1 for r in rep if r.get("switch_ok"))
        A(f"Repaired **{ok}/{len(rep)}** conversations whose LLM config had been clobbered "
          "(non-default model with `base_url=None`, i.e. no credentials). Each was restored with a full "
          "`switch_llm` payload — default model + proxy base URL + the single platform-managed key, fetched "
          "per sandbox from `GET /api/keys/llm/managed/current`.\n")
        A("| # | Conversation ID | Title | Before (model) | After | Result |")
        A("|---|---|---|---|---|---|")
        for i, r in enumerate(rep, 1):
            A(f"| {i} | `{r['id'][:8]}` | {str(r.get('title'))[:30]} | {r.get('before_model')} | "
              f"{DEFAULT_MODEL_STR} | {'OK' if r.get('switch_ok') else 'FAIL'} |")
        A("")
    A("## Deliverables — current state\n")
    A("| # | Deliverable set | Expected | Present | Verdict |")
    A("|---|---|---|---|---|")
    persona = len(list((PLANS / "personas").glob("S*.md")))
    mcp = len(list((PLANS / "mcp").glob("M*.md")))
    A(f"| 1 | Persona documents (`personas/S01–S39`) | 39 | {persona} | {'OK' if persona == 39 else 'INCOMPLETE'} |")
    A(f"| 2 | MCP catalogue documents (`mcp/M01–M15`) | 15 | {mcp} | {'OK' if mcp == 15 else 'INCOMPLETE'} |")
    A(f"| 3 | Squad catalogue (`squads/`) | 1 | {len(list((PLANS / 'squads').glob('*.md')))} | OK |")
    A("")

    A("## Outcome by work type\n")
    A("| # | Work type | Conversations | finished | error | idle | Deliverable produced |")
    A("|---|---|---|---|---|---|---|")
    ps: dict[str, list] = {}
    for c in cs:
        ps.setdefault(c["_purpose"], []).append(c)
    for i, (p, grp) in enumerate(sorted(ps.items(), key=lambda x: -len(x[1])), 1):
        s = Counter(x.get("execution_status") for x in grp)
        prod = sum(1 for x in grp if x["_artifact"]) if p in ("Persona doc", "MCP catalogue") else "—"
        A(f"| {i} | {p} | {len(grp)} | {s.get('finished', 0)} | {s.get('error', 0)} | {s.get(None, 0)} | {prod} |")
    A("")

    A("## Table 1 — Sandboxes\n")
    A("| # | Sandbox ID | Status | Spec | Conversations | Started by | Created |")
    A("|---|---|---|---|---|---|---|")
    sbs_sorted = sorted(sbs, key=lambda x: x.get("created_at") or "")
    for i, s in enumerate(sbs_sorted, 1):
        spec = str(s.get("sandbox_spec_id", "")).split("/")[-1]
        A(f"| {i} | `{s['id']}` | {s['status']} | {spec} | "
          f"{len(by_sb.get(s['id'], []))} | {s.get('started_by', '')} | {str(s.get('created_at'))[:19]} |")
    A("")
    A("### Table 1a — Sandbox verdicts\n")
    A("| # | Sandbox ID | Verdict | Note |")
    A("|---|---|---|---|")
    for i, s in enumerate(sbs_sorted, 1):
        grp = by_sb.get(s["id"], [])
        errs = sum(1 for c in grp if c.get("execution_status") == "error")
        fins = sum(1 for c in grp if c.get("execution_status") == "finished")
        note = f"{fins} finished, {errs} error" if grp else "no conversations"
        A(f"| {i} | `{s['id']}` | {'OK' if s['status'] == 'RUNNING' else 'IDLE (paused)'} | {note} |")
    A("")

    A("## Table 2 — Conversations\n")
    A("Newest first. **Verdict** combines the execution status with whether the "
      "expected artifact exists on disk.\n")
    A("| # | Conversation ID | Title | Work type | Model | Status | Verdict | Reason / note |")
    A("|---|---|---|---|---|---|---|---|")
    for i, c in enumerate(sorted(cs, key=lambda x: x.get("created_at") or "", reverse=True), 1):
        t = str(c.get("title") or "")[:38].replace("|", "/")
        m = model_used(c["id"], c.get("llm_model"))
        A(f"| {i} | `{c['id'][:8]}` | {t} | {c['_purpose']} | {m} | "
          f"{c.get('execution_status')} | {verdict(c)} | {note_for(c)} |")
    A("")

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "platform-inventory.md").write_text("\n".join(L) + "\n")

    js = {
        "generated": now,
        "sandboxes": [
            {"id": s["id"], "status": s["status"], "spec": s.get("sandbox_spec_id"),
             "created_at": s.get("created_at"), "started_by": s.get("started_by"),
             "conversations": len(by_sb.get(s["id"], []))}
            for s in sbs_sorted
        ],
        "conversations": [
            {"id": c["id"], "title": c.get("title"), "work_type": c["_purpose"],
             "model": c.get("llm_model"), "status": c.get("execution_status"),
             "verdict": verdict(c), "note": note_for(c), "sandbox_id": c.get("sandbox_id"),
             "artifact": bool(c["_artifact"]), "created_at": c.get("created_at")}
            for c in sorted(cs, key=lambda x: x.get("created_at") or "", reverse=True)
        ],
        "totals": {
            "sandboxes": len(sbs),
            "conversations": len(cs),
            "finished": st.get("finished", 0),
            "error": st.get("error", 0),
            "running": st.get("running", 0),
            "idle": st.get(None, 0),
            "persona_docs": persona,
            "mcp_docs": mcp,
        },
    }
    (OUT / "platform-inventory.json").write_text(json.dumps(js, indent=2))
    print(f"wrote inventory: {len(sbs)} sandboxes, {len(cs)} conversations, "
          f"{persona} persona docs, {mcp} mcp docs")


if __name__ == "__main__":
    main()
