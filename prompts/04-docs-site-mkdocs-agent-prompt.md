# 04 — Docs Site (MkDocs) Agent Prompt

> Suggested file name: `04-docs-site-mkdocs-agent-prompt.md`
> Give this prompt to the agent. The same operating rules as prompts 01–03 apply.

---

## 0. Operating Rules (Highest Priority — Overrides Everything Below)

- **This prompt is an instruction set, not a command to start working.** After reading it, reply with a short confirmation of what you understood, list your clarifying questions (Section 5), and wait.
- **Do only what is explicitly requested, nothing more.** Do not create repositories, folders, or files, install tools, commit, push, or open PRs until the human explicitly tells you to.
- **One step at a time.** Section 6 is a plan, not actions to take now. When a step is approved, perform only that step, report the result, **stop, and wait for confirmation** before the next.
- **No assumed approval.** Silence, an earlier approval, or a step being "obviously next" is not confirmation.
- **Never invent content.** Document only what the human tells you, points you to, or what you can verify. Mark anything else as "unknown / to be confirmed".
- **Never print or commit tokens or credentials.**

## 1. Why This Exists

The human is working across many projects, agents, and sandboxes and is losing track of what has been done. Your job is to build a **single source of truth**: a documentation website that shows what is being done, why, by whom or what, and its current status, in a structure that works like a project-management tool (the Jira concept).

## 2. Target

- **GitHub organization:** `https://github.com/org-gad-reveng-01`
- **Repository to create:** `sandbox-01-RepoSage_docs-site`
- **Technology:** a documentation website built with **MkDocs**.

## 3. What the Site Must Contain

### 3.1 Documentation of everything being done
A living record of all work: what exists, what was decided, what is in progress, and what is finished. Content comes from the human and from the work you are told to document.

### 3.2 Projects, missions, and hierarchy (Jira-like concept)
Model the work as a hierarchy, for example: **Portfolio → Project → Mission → Task**, with each item having a clear ID, title, description, owner (human or agent), status, priority, dates, and links to related items and documents. Provide overview pages (all projects, all missions, status boards or tables) so progress is visible at a glance. Propose the exact hierarchy and status vocabulary to the human and get approval before building it.

### 3.3 Visuals and diagrams
Include professional diagrams of the kind produced with Visio or draw.io: architecture, hierarchy, workflows, and relationships. Support both text-based diagrams (for example Mermaid) and draw.io diagrams, so they are version-controlled and editable. Diagrams must reflect real, verified information only.

### 3.4 Sandbox inventory
A page listing **all sandboxes**, each with: name, **role/purpose**, **status**, location or environment, owner, related projects or missions, and last-updated date. The human supplies this information; do not guess it.

## 4. Quality Expectations

- Clean, modern, easy-to-navigate design with clear navigation, search, and consistent structure.
- Content stored as Markdown and structured data in the repository, so everything is versioned and reviewable.
- Every page states what it covers and when it was last updated.
- Use numbered, lowercase, kebab-case file names for documents.

## 5. Questions to Ask First (Step 1)

Ask the human, briefly and in one list, only what you need and cannot find out yourself, for example:
- Which GitHub account or token will you use, and is the organization ready for a new repository? (Never ask for the token to be pasted into chat if there is a safer method.)
- What existing projects, missions, and sandboxes should be documented first, and where is that information?
- Do you approve the proposed hierarchy and status vocabulary?
- Which MkDocs theme and diagram approach do you prefer, or should you propose one?
- Should the site be published (for example through GitHub Pages), or stay in the repository for now? Do not publish unless told.

## 6. Execution Plan (Run Only Step by Step, After Explicit Approval)

1. **Clarify.** Ask the Section 5 questions. Wait for answers.
2. **Propose the design.** Present the site structure, the hierarchy and status model, the diagram approach, and the repository layout. Wait for approval.
3. **Create the repository** `sandbox-01-RepoSage_docs-site` in the organization. Confirm access first. Wait.
4. **Scaffold the MkDocs site** with navigation, theme, and the approved structure. Verify it builds locally and show the result. Wait.
5. **Add the project, mission, and hierarchy sections** with the content the human has provided. Wait.
6. **Add diagrams and visuals.** Verify they render. Wait.
7. **Add the sandbox inventory** using the human's data. Wait.
8. **Review.** Report what is complete, what is missing, and what is unverified. Propose next steps. Do not act on them.

## 7. Git Rules

- Never commit directly to `main`, apart from the initial repository setup the human approves.
- Use professional branch names (for example `feature/<topic>`, `docs/<topic>`).
- Write detailed commit messages: a clear imperative subject, then a body explaining what changed and why.
- Push frequently, open a pull request with a proper template (summary, changes, how it was verified, follow-ups), and merge into `main` only after the human approves.

## 8. How You Communicate

Be direct and concise. After each step report what you did, what you found, what is uncertain, and the proposed next step. Then wait for confirmation.