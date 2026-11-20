#!/usr/bin/env python3
"""Inventory documents and non-code files in cloned repositories.

Design goals (prompt 01, Step 3):
  * Walk every cloned repository under <root>/<org>/.
  * Find all documents and non-code files (markdown, text, PDFs, office docs,
    diagrams, images, configs-as-docs, wikis).
  * Exclude .git, dependency folders, and build output.
  * Write ONE inventory document per repository to
    <root>/<org>-analysis/_inventory/<repo-name>.md (the analysis folder, not the
    clone folder).
  * Each inventory lists every file with relative path, type, size, and a
    NON-ENGLISH FLAG.
  * Mark every file containing non-ASCII letters/scripts and record the detected
    script/language where possible. Never skip a file; extract text from binary
    and office formats before checking.

Usage:
    python3 inventory_repos.py --org org-morluto
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree

DEFAULT_ROOT = "/workspace/github/organization"

# Directories that are never scanned (dependency / build / VCS output).
EXCLUDE_DIRS = {
    ".git", ".hg", ".svn", "node_modules", "bower_components", "vendor",
    "dist", "build", "out", "target", "bin", "obj", ".next", ".nuxt",
    "__pycache__", ".venv", "venv", ".env", ".tox", ".mypy_cache",
    ".pytest_cache", ".gradle", ".idea", ".vscode", "coverage", ".cache",
    "site-packages", ".terraform", ".dart_tool", "Pods", ".svn-base",
}

# Document / non-code extensions we inventory.
DOC_EXTENSIONS = {
    # prose / docs
    ".md", ".markdown", ".mdx", ".rst", ".txt", ".text", ".adoc", ".asciidoc",
    ".org", ".tex", ".wiki", ".creole", ".pod", ".rdoc",
    # web / config-as-docs
    ".html", ".htm", ".css", ".yaml", ".yml", ".json", ".toml", ".ini",
    ".cfg", ".conf", ".env.example", ".properties", ".csv", ".tsv", ".xml",
    ".svg", ".drawio", ".puml", ".plantuml", ".mmd",
    # office / binary docs
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".odt",
    ".ods", ".odp", ".rtf", ".epub",
    # images that may contain docs
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".tif", ".webp",
    # misc docs
    ".po", ".pot", ".resx", ".strings", ".srt", ".vtt", ".ipynb", ".rmd",
    ".qmd", ".dita", ".ditamap", ".help", ".nfo", ".man",
}

# Extensions we treat as source code (not inventoried as documents).
CODE_EXTENSIONS = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".c", ".h", ".cpp", ".cc",
    ".hpp", ".cs", ".go", ".rs", ".rb", ".php", ".swift", ".kt", ".kts",
    ".scala", ".sh", ".bash", ".zsh", ".fish", ".ps1", ".bat", ".cmd", ".pl",
    ".pm", ".lua", ".r", ".m", ".mm", ".sql", ".dart", ".ex", ".exs", ".erl",
    ".hs", ".clj", ".groovy", ".gradle", ".vue", ".svelte", ".asm", ".s",
    ".v", ".vhd", ".f", ".f90", ".jl", ".nim", ".zig", ".elm", ".ml",
}

# Unicode script ranges used to describe detected non-Latin content.
SCRIPT_RANGES = [
    ("CJK Unified Ideographs", [(0x4E00, 0x9FFF), (0x3400, 0x4DBF), (0xF900, 0xFAFF)]),
    ("Hiragana", [(0x3040, 0x309F)]),
    ("Katakana", [(0x30A0, 0x30FF)]),
    ("Hangul", [(0xAC00, 0xD7AF), (0x1100, 0x11FF), (0x3130, 0x318F)]),
    ("Cyrillic", [(0x0400, 0x04FF), (0x0500, 0x052F)]),
    ("Arabic", [(0x0600, 0x06FF), (0x0750, 0x077F), (0xFB50, 0xFDFF), (0xFE70, 0xFEFF)]),
    ("Hebrew", [(0x0590, 0x05FF)]),
    ("Greek", [(0x0370, 0x03FF), (0x1F00, 0x1FFF)]),
    ("Devanagari", [(0x0900, 0x097F)]),
    ("Thai", [(0x0E00, 0x0E7F)]),
    ("Bengali", [(0x0980, 0x09FF)]),
    ("Georgian", [(0x10A0, 0x10FF)]),
    ("Armenian", [(0x0530, 0x058F)]),
    ("Tamil", [(0x0B80, 0x0BFF)]),
    ("Telugu", [(0x0C00, 0x0C7F)]),
    ("Ethiopic", [(0x1200, 0x137F)]),
]


def detect_scripts(text: str) -> dict[str, int]:
    """Return a mapping of script name -> count of characters in that script."""
    counts: dict[str, int] = {}
    for ch in text:
        cp = ord(ch)
        if cp < 0x80:
            continue
        for name, ranges in SCRIPT_RANGES:
            if any(lo <= cp <= hi for lo, hi in ranges):
                counts[name] = counts.get(name, 0) + 1
                break
    return counts


def has_non_english(text: str) -> tuple[bool, bool]:
    """Return (has_non_ascii_letters, has_non_latin_script)."""
    has_letters = False
    has_script = False
    for ch in text:
        if ord(ch) < 0x80:
            continue
        if ch.isalpha() or unicodedata.category(ch).startswith("L"):
            has_letters = True
        cp = ord(ch)
        for _, ranges in SCRIPT_RANGES:
            if any(lo <= cp <= hi for lo, hi in ranges):
                has_script = True
                break
        if has_letters and has_script:
            break
    return has_letters, has_script


def classify(text: str) -> dict:
    """Classify how non-English a file is.

    Returns letter counts and a `substantial`/`incidental` verdict so reports can
    separate genuinely foreign documents from English files that merely contain a
    few accented characters or typographic symbols.
    """
    letters = nonlatin = accented = 0
    script_chars = 0
    for ch in text:
        if not (ch.isalpha() or unicodedata.category(ch).startswith("L")):
            continue
        letters += 1
        cp = ord(ch)
        if cp > 0x7F:
            accented += 1
            in_script = any(lo <= cp <= hi for _, rs in SCRIPT_RANGES for lo, hi in rs)
            if in_script:
                nonlatin += 1
                script_chars += 1
    ratio = (nonlatin / letters) if letters else 0.0
    # Substantial: a meaningful share of non-Latin letters, or many such letters.
    substantial = (ratio >= 0.10 and nonlatin >= 20) or nonlatin >= 200
    verdict = "substantial" if substantial else (
        "incidental" if accented else "none")
    return {
        "letters": letters, "nonlatin_letters": nonlatin,
        "accented_letters": accented, "nonlatin_ratio": round(ratio, 4),
        "verdict": verdict,
    }


def read_text_file(path: Path, limit: int = 2_000_000) -> str | None:
    """Read a text file defensively; return None if it looks binary."""
    try:
        raw = path.read_bytes()[:limit]
    except OSError:
        return None
    if b"\x00" in raw[:4096]:
        return None
    for enc in ("utf-8", "utf-16", "latin-1"):
        try:
            return raw.decode(enc)
        except (UnicodeDecodeError, UnicodeError):
            continue
    return None


def extract_office_text(path: Path) -> str:
    """Extract text from docx/xlsx/pptx/odt (zip-based) via the XML payloads."""
    texts: list[str] = []
    try:
        with zipfile.ZipFile(path) as zf:
            for name in zf.namelist():
                if not name.endswith(".xml"):
                    continue
                if not re.search(r"(document|slide|sheet|content|sharedStrings|"
                                 r"notesSlide|header|footer|comments)", name):
                    continue
                try:
                    xml = zf.read(name)
                except (KeyError, zipfile.BadZipFile):
                    continue
                try:
                    root = ElementTree.fromstring(xml)
                except ElementTree.ParseError:
                    continue
                for node in root.iter():
                    if node.text:
                        texts.append(node.text)
    except (zipfile.BadZipFile, OSError):
        return ""
    return "\n".join(texts)


def extract_pdf_text(path: Path) -> str:
    """Best-effort PDF text extraction using pypdf if available, else None."""
    try:
        from pypdf import PdfReader  # type: ignore
    except ImportError:
        return ""
    try:
        reader = PdfReader(str(path))
        return "\n".join((pg.extract_text() or "") for pg in reader.pages[:200])
    except Exception:
        return ""


def guess_language(text: str) -> str:
    """Very light heuristic language hint from the dominant script."""
    counts = detect_scripts(text)
    if not counts:
        return "latin (accented/other)"
    top = max(counts, key=counts.get)
    return top


def is_document(path: Path) -> bool:
    ext = path.suffix.lower()
    if ext in DOC_EXTENSIONS:
        return True
    # Extension-less files that are commonly docs.
    if not ext and path.name.lower() in {"readme", "license", "licence", "notice",
                                         "changelog", "authors", "contributing",
                                         "copying", "makefile", "dockerfile"}:
        return True
    return False


def iter_files(repo: Path):
    for p in repo.rglob("*"):
        if p.is_dir():
            continue
        if any(part in EXCLUDE_DIRS for part in p.relative_to(repo).parts[:-1]):
            continue
        yield p


def inventory_repo(repo: Path) -> dict:
    rows = []
    non_english_count = 0
    for path in sorted(iter_files(repo)):
        rel = path.relative_to(repo).as_posix()
        try:
            size = path.stat().st_size
        except OSError:
            size = -1
        ext = path.suffix.lower()
        kind = "doc" if is_document(path) else ("code" if ext in CODE_EXTENSIONS else "other")
        if kind != "doc":
            continue

        text = ""
        extraction = "text"
        if ext in {".docx", ".xlsx", ".pptx", ".odt", ".ods", ".odp"}:
            text = extract_office_text(path)
            extraction = "office-xml"
        elif ext == ".pdf":
            text = extract_pdf_text(path)
            extraction = "pdf" if text else "pdf-no-extractor"
        elif ext in {".doc", ".xls", ".ppt"}:
            extraction = "legacy-binary-no-extractor"
        elif ext in {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".tif",
                     ".webp"}:
            extraction = "image-no-ocr"
        else:
            t = read_text_file(path)
            if t is None:
                extraction = "binary-skipped"
            else:
                text = t

        non_ascii = sum(1 for ch in text if ord(ch) > 0x7F)
        cls = classify(text)
        flag = "YES" if cls["nonlatin_letters"] > 0 else "no"
        if flag == "YES":
            non_english_count += 1
        lang = guess_language(text) if flag == "YES" else ""
        rows.append({
            "path": rel,
            "type": ext.lstrip(".") or "no-ext",
            "size": size,
            "non_english": flag,
            "lang": lang,
            "non_ascii": non_ascii,
            "extraction": extraction,
            "verdict": cls["verdict"],
            "nonlatin_letters": cls["nonlatin_letters"],
            "nonlatin_ratio": cls["nonlatin_ratio"],
        })
    return {"repo": repo.name, "rows": rows, "non_english": non_english_count}


def write_inventory(org: str, inv: dict, out_dir: Path, generated: str) -> None:
    rows = inv["rows"]
    total = len(rows)
    ne = inv["non_english"]
    substantial = sum(1 for r in rows if r.get("verdict") == "substantial")
    lines = [
        f"# Inventory — {inv['repo']}",
        "",
        f"- **Organization:** {org}",
        f"- **Generated (UTC):** {generated}",
        f"- **Documents / non-code files inventoried:** {total}",
        f"- **Files containing non-Latin characters:** {ne}",
        f"- **Files that are substantially non-English:** {substantial}",
        "",
        "Flag legend: `YES` = contains non-Latin letters/scripts; `no` = none detected.",
        "Verdict: `substantial` = genuinely foreign text (many non-Latin letters or",
        "a high ratio); `incidental` = mostly-English file with a few non-Latin",
        "letters (names, symbols, accents); `none` = no non-Latin letters.",
        "Extraction: `text` = read directly, `office-xml` = extracted from office XML,",
        "`pdf` = extracted, `pdf-no-extractor` = PDF text not extracted (tool missing),",
        "`image-no-ocr` = image, OCR not performed, `binary-skipped` = binary, not read.",
        "",
        "| # | Path | Type | Size (B) | Non-English | Verdict | Non-Latin letters | Non-Latin ratio | Detected script | Extraction |",
        "|---|------|------|---------:|-------------|---------|------------------:|----------------:|-----------------|------------|",
    ]
    for i, r in enumerate(rows, 1):
        lang = r["lang"] if r["non_english"] == "YES" else ""
        lines.append(
            f"| {i} | `{r['path']}` | {r['type']} | {r['size']} | "
            f"{r['non_english']} | {r.get('verdict', '')} | {r.get('nonlatin_letters', '')} | "
            f"{r.get('nonlatin_ratio', '')} | {lang} | {r['extraction']} |"
        )
    if not rows:
        lines.append("| — | _(no documents found)_ | | | | | | | | |")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"{inv['repo']}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--org", required=True)
    ap.add_argument("--root", default=DEFAULT_ROOT)
    ap.add_argument("--out-org", help="org folder that receives _inventory/ "
                    "(default: <org>-analysis)")
    ap.add_argument("--json-out", help="also write a machine-readable JSON summary")
    args = ap.parse_args()

    org_dir = Path(args.root) / args.org
    out_org = args.out_org or f"{args.org}-analysis"
    out_dir = Path(args.root) / out_org / "_inventory"
    if not org_dir.is_dir():
        print(f"FATAL: no such org directory: {org_dir}", file=sys.stderr)
        return 2

    repos = [d for d in sorted(org_dir.iterdir())
             if d.is_dir() and not d.name.startswith("_")]
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    summaries = []
    for repo in repos:
        inv = inventory_repo(repo)
        write_inventory(args.org, inv, out_dir, generated)
        substantial = sum(1 for r in inv["rows"] if r.get("verdict") == "substantial")
        summaries.append({"repo": inv["repo"], "documents": len(inv["rows"]),
                          "non_english": inv["non_english"],
                          "substantial": substantial})
        print(f"inventoried {repo.name}: {len(inv['rows'])} docs, "
              f"{inv['non_english']} non-Latin, {substantial} substantial")

    if args.json_out:
        Path(args.json_out).write_text(
            json.dumps({"org": args.org, "generated": generated,
                        "repos": summaries}, indent=2), encoding="utf-8")
    print(f"total repos: {len(summaries)}; "
          f"total docs: {sum(s['documents'] for s in summaries)}; "
          f"total non-English: {sum(s['non_english'] for s in summaries)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
