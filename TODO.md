# TODO — ad-hoc items arising during execution

Working file for the RepoSage run. Add new items here as they arise, with the
date, the reason, and the evidence/pointer. Keep it short and actionable; move
finished items to "Done" rather than deleting them.

Last updated: 2026-11-18 (UTC)

Legend: `[ ]` open · `[~]` in progress · `[x]` done · `[!]` blocked / needs a
human decision.

---

## Needs a human decision (blocking)

- [!] **Which repository should hold the reports/analysis output?**
  `_reports/` is not itself a repo. Proposed: the `org-morluto-analysis`
  organization (which now exists and holds `_developers-guide`, `_plans`,
  `rea-analysis`). Until decided, no commit/push/PR has been made.
  - Evidence: `/workspace/github/organization/org-morluto-analysis/_reports/00-reports-index.md`
    ("Proposed next step").
- [!] **Rotate credentials.** The live GitHub PAT and OpenHands API key were
  printed into the conversation log on 2026-11-18 (a `sed` redaction of the
  Markdown-table vault failed). Not committed to git, but logged. Rotate both.
  - Evidence: `/workspace/project/.openhands/memory/2026-11-17.md` (Session 3,
    "SECURITY INCIDENT").

## Ad-hoc items found during execution

- [ ] **Relocate the local `rea-analysis` clone.** Its path is still
  `/workspace/github/organization/org-morluto/rea-analysis` even though the repo
  now lives in `org-morluto-analysis`. Move it under an `org-morluto-analysis`
  directory (or leave and document).
  - Evidence: `/workspace/github/organization/org-morluto-analysis/_reports/_move-log/README.md`.
- [ ] **Report the gibberish README upstream.** `rea-agent-skills-jacky/README_ZH.md`
  is degenerate machine-generated text ("作为默认值" ×~24, "本本本本…"). Fix belongs
  upstream in `morluto`, not in the mirror.
  - Evidence: `.../org-morluto-analysis/_reports/02-translation-status.md` (Quality flags).
- [ ] **License / attribution review.** 20 of 82 repos have no detected license;
  several vendor third-party content (`rea-third-party-skills-cn`,
  `rea-kilo-mcp-marketplace`, bundled PDFs/wordlists). Needs a human/legal pass.
  - Evidence: `.../org-morluto-analysis/00-organization-overview.md` (risks).
- [ ] **Review vendored Apple certificates.** `rea-apple-knowledge-list` vendors
  100+ public Apple factory/test `.pem` files — licensing/export check before
  redistribution.
  - Evidence: `.../org-morluto-analysis/repositories/rea-apple-knowledge-list.md`.
- [ ] **Decide mirror-sync policy.** `org-morluto` is a mirror of `morluto`; any
  fix made here is overwritten on the next sync. Confirm whether the mirror is
  kept current and where corrections should go.

## Environment / tooling fixes

- [ ] **Persist `gh` auth per command.** `gh auth status` reports "not logged in";
  `GH_TOKEN` must be exported for every command. Consider a wrapper or document
  the pattern.
  - Evidence: `/workspace/project/.openhands/memory/MEMORY.md` (Secrets).
- [ ] **Record Python deps.** `pypdf` is required for PDF text extraction and is
  NOT preinstalled (`pip3 install pypdf`). Add a `requirements.txt` for the
  scripts in `/workspace/scripts/`.
- [ ] **Note missing CLI tools.** `pdftotext`, `libreoffice`, `unzip`, `column`
  are absent; extraction falls back to Python. Either install or keep the
  documented fallback.
- [ ] **Keep the vault at mode 600.** It was found at `644`; it is now `600`.
  Verify it stays that way.

## Standing workstreams (from the mission)

- [~] **Translation.** 611 substantially non-English files; 0 translated, 1
  flagged, 611 open. **Restarted from scratch** under the in-repo workflow
  (feature branch → PR → merge per repository). Priority order in
  `.../org-morluto-analysis/_reports/02-translation-status.md`.
- [ ] **Commit / PR / merge the analysis + reports.** Blocked on the repo
  decision above. Branch name to use: `docs/status-report-2026-11-17`.
- [ ] **Optional deep dossiers.** Promote any long-tail repo to a full dossier if
  requested (currently covered in the grouped catalogue).

---

## Done

- [x] 2026-11-17 — Folded prompt 02 (status reporting) into `AGENTS.md` + memory.
- [x] 2026-11-17 — Reformatted `/workspace/vault/github-organizations.md` as a
  numbered table with clone/translation/analysis/merge columns.
- [x] 2026-11-17 — Cloned all repos (82/82), ran inventory (7,980 docs).
- [x] 2026-11-17 — Deep analysis (org overview, `rea` deep-dive, full catalogue,
  dossiers).
- [x] 2026-11-17 — Wrote prompt-02 status reports `00`–`03`.
- [x] 2026-11-18 — Moved `rea-analysis` from `org-morluto` to
  `org-morluto-analysis`; verified and deleted from source (81 repos remain).
  - Evidence: `/workspace/github/organization/org-morluto-analysis/_reports/_move-log/`.
- [x] 2026-11-18 — Consolidated generated output: moved `_reports/` and merged
  `_inventory/` (83+2=85 files, no loss) from `org-morluto/` into
  `org-morluto-analysis/`; updated prompts, `AGENTS.md`, memory, scripts, tracker.
- [x] 2026-11-18 — Moved `/workspace/prompts/` into
  `org-morluto-analysis/prompts/`; updated `AGENTS.md`, `MEMORY.md`, daily log.
