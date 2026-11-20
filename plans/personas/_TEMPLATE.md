# Persona document — canonical template

Every `S##-<slug>.md` document under this folder follows this exact structure.
Copy the headings and tables verbatim; replace only the content.

---

```markdown
# S## — <Squad Name>

- **Division:** <Division name> (<CODE>)
- **Mission:** <one line>
- **Headcount:** <n> personas
- **Reports to:** <the role this squad reports to>

## 1. Purpose

<2–4 sentences: why this squad exists and what it owns. No task detail.>

## 2. Personas

| # | Name | Gender | Country | Role | Skills | Responsibilities |
|---|---|---|---|---|---|---|
| 1 | <Full Name> | <Female/Male/Non-binary> | <Country> | <Role title> | <skill 1>; <skill 2>; <skill 3>; <skill 4> | <responsibility 1>; <responsibility 2>; <responsibility 3> |
| ... | | | | | | |

Rules for the table:
- **Name** — a real, culture-appropriate human name. No placeholders.
- **Gender** — Female, Male, or Non-binary.
- **Country** — the persona's home country.
- **Role** — a single seniority-qualified title.
- **Skills** — 4–7 high-level skills, semicolon-separated, no detail.
- **Responsibilities** — 3–6 high-level responsibilities, semicolon-separated,
  no detail.

## 3. Diversity

| Dimension | Composition |
|---|---|
| Gender | <e.g. 4F / 2M / 1NB> |
| Countries | <list> |
| Regions | <list> |
| Seniority mix | <e.g. 2 principal, 3 senior, 2 mid> |

## 4. Interfaces

| Direction | Counterpart | What is exchanged |
|---|---|---|
| Up | <manager> | <high-level> |
| Across | <peer squad> | <high-level> |
| Out | <customer/partner> | <high-level> |
```

---

## Formatting rules

1. **Numbered tables only** for the persona roster — no bullet lists of people.
2. **High level, no detail.** Skills and responsibilities are short phrases, not
   paragraphs.
3. **Consistent role ordering** — lead first, then seniors, then others.
4. **No secrets, no real personal data** beyond a plausible name and country.
