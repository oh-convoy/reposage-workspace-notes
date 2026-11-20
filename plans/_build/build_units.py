"""Build the fan-out unit list for the persona documents.

Emits a JSON list of {"id", "title", "path", "task"} — one unit per squad.
"""

from __future__ import annotations

import json
from pathlib import Path

OUT = Path("/workspace/plans/personas")

# id, name, division, code, mission, headcount, slug, country palette
SQUADS = [
    ("S01", "Platform & Core Services Squad", "Software Engineering", "ENG",
     "Build and run the shared platform and core services every product depends on", 7,
     "platform-core-services", "India, Poland, Brazil, Nigeria"),
    ("S02", "Web Frontend Squad", "Software Engineering", "ENG",
     "Deliver the web user experiences, components, and design systems", 6,
     "web-frontend", "Ukraine, Vietnam, Spain, Mexico"),
    ("S03", "Mobile Engineering Squad", "Software Engineering", "ENG",
     "Build and ship the iOS and Android applications", 6,
     "mobile-engineering", "South Korea, Turkey, Egypt, Colombia"),
    ("S04", "API & Integrations Squad", "Software Engineering", "ENG",
     "Design, expose, and integrate the public and partner APIs", 6,
     "api-integrations", "Germany, Philippines, Argentina, Kenya"),
    ("S05", "Data Engineering Squad", "Software Engineering", "ENG",
     "Build the pipelines, storage, and data platform the company runs on", 6,
     "data-engineering", "China, Romania, Chile, Ghana"),
    ("S06", "DevOps & Site Reliability Squad", "Software Engineering", "ENG",
     "Automate delivery and keep production reliable, observable, and fast", 7,
     "devops-sre", "United States, Portugal, Indonesia, Peru"),
    ("S07", "Quality Engineering Squad", "Software Engineering", "ENG",
     "Protect quality with test strategy, automation, and release gates", 6,
     "quality-engineering", "United Kingdom, Malaysia, South Africa, Ecuador"),
    ("S08", "Security Engineering Squad", "Software Engineering", "ENG",
     "Secure the products, data, and supply chain end to end", 6,
     "security-engineering", "Israel, Ireland, Thailand, Morocco"),
    ("S09", "AI Research Squad", "Artificial Intelligence", "AI",
     "Advance the company's core AI methods and publish the science", 6,
     "ai-research", "United States, France, India, Canada"),
    ("S10", "LLM & Agent Engineering Squad", "Artificial Intelligence", "AI",
     "Build the LLM, agent, and orchestration capabilities in the products", 7,
     "llm-agent-engineering", "China, Germany, Nigeria, Japan"),
    ("S11", "Machine Learning Engineering Squad", "Artificial Intelligence", "AI",
     "Train, evaluate, and serve production ML models", 6,
     "ml-engineering", "Russia, Brazil, South Korea, Turkey"),
    ("S12", "Data Science Squad", "Artificial Intelligence", "AI",
     "Turn data into insight, forecasts, and decisions", 6,
     "data-science", "Spain, Egypt, Mexico, Poland"),
    ("S13", "MLOps Squad", "Artificial Intelligence", "AI",
     "Industrialize the ML lifecycle: data, training, serving, monitoring", 6,
     "mlops", "India, Netherlands, Indonesia, Argentina"),
    ("S14", "AI Safety & Governance Squad", "Artificial Intelligence", "AI",
     "Keep AI systems safe, fair, explainable, and compliant", 6,
     "ai-safety-governance", "United Kingdom, Kenya, Sweden, Singapore"),
    ("S15", "Growth & Performance Marketing Squad", "Digital Marketing", "MKT",
     "Acquire and retain users through measurable growth programs", 7,
     "growth-performance-marketing", "United States, Philippines, Colombia, Nigeria"),
    ("S16", "Content Marketing Squad", "Digital Marketing", "MKT",
     "Produce the editorial content that attracts and educates the market", 6,
     "content-marketing", "Canada, India, South Africa, Ireland"),
    ("S17", "SEO & Organic Search Squad", "Digital Marketing", "MKT",
     "Grow durable organic search visibility and traffic", 5,
     "seo-organic-search", "United Kingdom, Vietnam, Peru, Ukraine"),
    ("S18", "Marketing Analytics & CRO Squad", "Digital Marketing", "MKT",
     "Measure marketing, attribute results, and optimize conversion", 6,
     "marketing-analytics-cro", "Germany, Brazil, Thailand, Egypt"),
    ("S19", "Brand & Communications Squad", "Digital Marketing", "MKT",
     "Own the brand narrative, voice, and public communication", 5,
     "brand-communications", "France, Mexico, Japan, Ghana"),
    ("S20", "Social Strategy Squad", "Social Media", "SOC",
     "Set social channel strategy, calendars, and campaigns", 5,
     "social-strategy", "United States, Nigeria, Indonesia, Poland"),
    ("S21", "Community Management Squad", "Social Media", "SOC",
     "Grow and care for the community across channels", 6,
     "community-management", "Brazil, Philippines, Kenya, Romania"),
    ("S22", "Creator & Influencer Partnerships Squad", "Social Media", "SOC",
     "Source, contract, and run creator partnerships", 5,
     "creator-influencer-partnerships", "United Kingdom, South Korea, Mexico, Turkey"),
    ("S23", "Social Content Studio Squad", "Social Media", "SOC",
     "Produce the native short-form content each platform rewards", 6,
     "social-content-studio", "United States, India, Colombia, Spain"),
    ("S24", "Product Design (UX) Squad", "Multimedia & Design", "MMD",
     "Research users and design end-to-end product experiences", 6,
     "product-design-ux", "Sweden, Japan, Argentina, South Africa"),
    ("S25", "UI & Visual Design Squad", "Multimedia & Design", "MMD",
     "Craft interfaces, visual systems, and design tokens", 6,
     "ui-visual-design", "Ukraine, Canada, Egypt, Vietnam"),
    ("S26", "Motion & Graphics Squad", "Multimedia & Design", "MMD",
     "Produce motion graphics, animation, and marketing graphics", 6,
     "motion-graphics", "South Korea, Brazil, Italy, Philippines"),
    ("S27", "3D, AR & VR Squad", "Multimedia & Design", "MMD",
     "Build 3D assets and immersive AR/VR experiences", 6,
     "3d-ar-vr", "United States, France, India, Nigeria"),
    ("S28", "Brand & Identity Design Squad", "Multimedia & Design", "MMD",
     "Design and govern the corporate identity system", 5,
     "brand-identity-design", "Denmark, Mexico, Japan, Kenya"),
    ("S29", "Video Production Squad (Live Action)", "Video & Audio Production", "VAP",
     "Plan, shoot, and capture live-action video", 7,
     "video-production-live-action", "United States, Poland, Thailand, Colombia"),
    ("S30", "Video Post-Production Squad", "Video & Audio Production", "VAP",
     "Edit, color, and finish video to broadcast quality", 6,
     "video-post-production", "United Kingdom, India, Argentina, Romania"),
    ("S31", "Audio Production & Podcast Squad", "Video & Audio Production", "VAP",
     "Record, edit, and publish audio and podcasts", 6,
     "audio-production-podcast", "Germany, Brazil, South Korea, South Africa"),
    ("S32", "Animation Studio Squad", "Video & Audio Production", "VAP",
     "Create 2D/3D animated films and explainer content", 6,
     "animation-studio", "Japan, Spain, Mexico, Philippines"),
    ("S33", "Music & Sound Design Squad", "Video & Audio Production", "VAP",
     "Compose music and design sound for all media", 5,
     "music-sound-design", "United States, Nigeria, Sweden, Vietnam"),
    ("S34", "People & Talent Squad", "Corporate & Shared Services", "COR",
     "Hire, onboard, grow, and retain the people", 7,
     "people-talent", "United States, India, Kenya, Poland"),
    ("S35", "Finance & Accounting Squad", "Corporate & Shared Services", "COR",
     "Plan, account for, and control the money", 6,
     "finance-accounting", "United Kingdom, Singapore, Brazil, Egypt"),
    ("S36", "Legal, Risk & Compliance Squad", "Corporate & Shared Services", "COR",
     "Protect the company legally and keep it compliant", 6,
     "legal-risk-compliance", "Germany, Canada, Nigeria, Japan"),
    ("S37", "Sales & Partnerships Squad", "Corporate & Shared Services", "COR",
     "Win customers and build channel partnerships", 7,
     "sales-partnerships", "United States, Brazil, Indonesia, Spain"),
    ("S38", "Customer Success & Support Squad", "Corporate & Shared Services", "COR",
     "Onboard, support, and retain customers", 7,
     "customer-success-support", "Philippines, Mexico, India, South Africa"),
    ("S39", "Operations & Program Management Squad", "Corporate & Shared Services", "COR",
     "Run the company's programs, process, and operations", 6,
     "operations-program-management", "Netherlands, Colombia, Vietnam, Nigeria"),
]

TASK_TMPL = """You are an expert organizational designer writing ONE document for a corporate staffing plan.

Write the file EXACTLY at this path: {path}

The document fully describes squad {sid} — "{name}" (division: {division} / {code}).
Mission: {mission}
Headcount: {headcount} personas.
Country palette to draw from: {countries}

Read the template at /workspace/plans/_templates/persona.md and follow its
structure EXACTLY. Produce a polished, professional document with these sections:

# {sid} — {name}

- **Division:** {division} ({code})
- **Mission:** {mission}
- **Headcount:** {headcount} personas
- **Reports to:** <a plausible executive title>
- **Operating model:** <one short phrase>

## 1. Purpose
A rich paragraph of 4-6 sentences: why this squad exists, what it owns end to end,
how it creates value, and what "good" looks like. Write like an experienced
operator. No task-level detail.

## 2. Operating principles
3-5 short, sharp bullets this squad lives by.

## 3. Persona roster

| # | Name | Gender | Country | Seniority | Role | Core skills | Key responsibilities |
|---|---|---|---|---|---|---|---|
| 1 | ... | ... | ... | ... | ... | ... | ... |
... exactly {headcount} rows ...

## 4. Diversity & coverage

| Dimension | Composition |
|---|---|
| Gender | ... |
| Countries | ... |
| Regions | ... |
| Seniority mix | ... |

## 5. Interfaces

| Direction | Counterpart | What is exchanged |
|---|---|---|
| Up | ... | ... |
| Across | ... | ... |
| Out | ... | ... |

HARD RULES
- The roster MUST have EXACTLY {headcount} personas — no more, no fewer.
- Gender MUST be binary: only "Female" or "Male". Include a genuine mix of both
  in every squad. Never write "Non-binary".
- Names MUST be real, culture-appropriate full names (first + last) that fit the
  persona's country. No placeholders. No duplicate names within the squad.
- Draw countries from this palette: {countries}. Match each name to its country.
- Seniority: realistic spread. The FIRST persona is the squad lead
  (Principal or Senior). Use Principal/Senior/Mid/Junior.
- Core skills: 4-7 HIGH-LEVEL skills, semicolon-separated, short phrases.
- Key responsibilities: 3-6 HIGH-LEVEL responsibilities, semicolon-separated,
  short phrases. No paragraphs inside cells.
- Make the prose specific, vivid, and professional. Avoid generic filler.
- Write ONLY the document. No preamble, no commentary, no code fences.

Write the file with the file editor, then reply DONE.
"""

def main() -> None:
    units = []
    headcounts = {}
    for sid, name, division, code, mission, hc, slug, countries in SQUADS:
        path = str(OUT / f"{sid}-{slug}.md")
        headcounts[sid] = hc
        units.append({
            "id": sid,
            "title": f"personas-{sid}",
            "path": path,
            "task": TASK_TMPL.format(
                path=path, sid=sid, name=name, division=division, code=code,
                mission=mission, headcount=hc, countries=countries,
            ),
        })
    Path("/workspace/plans/_build/units_personas.json").write_text(json.dumps(units, indent=2))
    Path("/workspace/plans/_build/headcounts.json").write_text(json.dumps(headcounts, indent=2))
    print(f"wrote {len(units)} persona units")


if __name__ == "__main__":
    main()
