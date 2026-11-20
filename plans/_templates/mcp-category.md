# Template — MCP Category Document (`mcp/M##-<slug>.md`)

Produce a **single** Markdown document cataloguing the MCP servers the company
needs in one category. Write it like a technology architect: precise, opinionated,
and useful to a reader deciding what to adopt.

Use **exactly** the structure below. Replace every `<...>` with real content.

---

```markdown
# M## — <Category Name>

**Scope:** <what this category covers, one line>

## 1. Overview

<3–5 sentences. Why this category matters, how it fits the two-plane MCP model
(shared tools-plane gateway vs. local data-plane servers), and the main adoption
consideration for the category.>

## 2. Servers

| # | MCP Server | Purpose | Used by squads | Auth | Transport | Criticality | Free tier |
|---|---|---|---|---|---|---|---|
| 1 | <real server/product> | <one short phrase> | <e.g. S01, S06> | <API key/OAuth2/Service account/Token/None> | <stdio/HTTP/SSE> | <Critical/High/Medium/Low> | <Free / Freemium / Paid / Open source> |
| 2 | ... | | | | | | |
... at least 8 rows, all real and relevant ...

## 3. Notes

| # | Note |
|---|---|
| 1 | <a short, high-level note on adoption, dependency, or risk> |
... 2–4 rows ...

## 4. Deployment notes

<A short paragraph or 3–4 bullets saying which of these servers belong on the
shared gateway (tools plane) and which must run locally (data plane), and why.>
```

---

## Hard rules

1. **At least 8 server rows**, every one a **real, well-known** MCP server or a
   well-known product with an official/community MCP server. No invented vendors.
2. **Purpose** is one short phrase.
3. **Used by squads** lists real squad IDs from the corporation (S01–S39).
4. **Auth** is one of: `API key`, `OAuth2`, `Service account`, `Token`, `None`.
5. **Transport** is one of: `stdio`, `HTTP`, `SSE`.
6. **Criticality** is one of: `Critical`, `High`, `Medium`, `Low`.
7. **Free tier** states the licensing/cost reality, using one of:
   `Free`, `Freemium`, `Open source`, `Paid`. Add a short qualifier in parentheses
   where it helps (e.g. `Freemium (API limits)`, `Paid (seat)`).
8. Keep everything **high level** — no configuration, no code, no endpoints.
9. **Write only the document.** No preamble, no code fences around the file.
