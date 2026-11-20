# Template — Persona Document (`personas/S##-<slug>.md`)

Produce a **single** Markdown document that fully describes one squad and every
persona in it. Write flowing, professional prose and well-formed tables. This is
a real corporate staffing document, not a skeleton.

Use **exactly** the section order and headings below. Replace every `<...>`
placeholder with real content. Do not add extra top-level sections.

---

```markdown
# S## — <Squad Name>

- **Division:** <Division> (<CODE>)
- **Mission:** <one crisp sentence>
- **Headcount:** <n> personas
- **Reports to:** <a plausible executive title>
- **Operating model:** <e.g. "one cross-functional team, product-aligned, hybrid">

## 1. Purpose

<A rich paragraph of 4–6 sentences. Explain why the squad exists, what it owns
end to end, how it creates value for the company, and what "good" looks like for
it. Write like an experienced operator, not a spec. No task-level detail.>

## 2. Operating principles

<3–5 bullets. Each a short, sharp principle the squad lives by.>

## 3. Persona roster

| # | Name | Gender | Country | Seniority | Role | Core skills | Key responsibilities |
|---|---|---|---|---|---|---|---|
| 1 | <Full Name> | <Female/Male> | <Country> | <Principal/Senior/Mid/Junior> | <seniority-qualified title> | <skill 1>; <skill 2>; <skill 3>; <skill 4>; <skill 5> | <responsibility 1>; <responsibility 2>; <responsibility 3>; <responsibility 4> |
| 2 | ... | | | | | | |
... exactly <n> rows, one per persona ...

## 4. Diversity & coverage

| Dimension | Composition |
|---|---|
| Gender | <e.g. 4 women / 3 men> |
| Countries | <list every country represented> |
| Regions | <e.g. South Asia, Latin America, West Africa> |
| Seniority mix | <e.g. 1 principal, 3 senior, 3 mid> |

## 5. Interfaces

| Direction | Counterpart | What is exchanged |
|---|---|---|
| Up | <executive the squad reports to> | <what flows up> |
| Across | <peer squad> | <what flows sideways> |
| Out | <customer, partner, or vendor> | <what flows outward> |
```

---

## Hard rules

1. **Roster size is exact.** The table must have exactly the stated number of
   personas — no more, no fewer.
2. **Gender is binary.** Use only `Female` or `Male`. Include a genuine mix
   (both women and men) in every squad.
3. **Names are real and culture-appropriate.** Full names (first + last) that fit
   the persona's country. No placeholders, no duplicates within the squad.
4. **Countries.** Draw from the country palette given for the squad, and make the
   name match the country.
5. **Seniority.** A realistic spread. The **first** persona is the squad lead
   (typically Principal or Senior).
6. **Skills and responsibilities are high level.** Short semicolon-separated
   phrases (4–7 skills, 3–6 responsibilities). No paragraphs inside cells.
7. **Tables only** for the roster — never a bulleted list of people.
8. **No secrets, no real personal data.** Invent plausible professional personas.
9. **Write only the document.** No code fences around the whole file, no
   commentary, no preamble.
