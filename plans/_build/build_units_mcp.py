"""Build the fan-out unit list for the MCP server catalogue.

One unit per catalogue category. Each writes a document with a numbered table.
"""

from __future__ import annotations

import json
from pathlib import Path

OUT = Path("/workspace/plans/mcp")

# id, category, slug, scope, example servers to consider
CATS = [
    ("M01", "Code & Version Control", "code-version-control",
     "repositories, code review, package registries, code search",
     "GitHub, GitLab, Bitbucket, filesystem, ripgrep/code-search, npm/PyPI registries, Docker Hub, Sonatype Nexus"),
    ("M02", "Developer Productivity & CI/CD", "dev-productivity-cicd",
     "delivery pipelines, issue trackers, terminals, scaffolding",
     "GitHub Actions, Jenkins, CircleCI, Argo CD, Jira, Linear, shell/terminal, Playwright, test runners"),
    ("M03", "Cloud & Infrastructure", "cloud-infrastructure",
     "cloud providers, containers, orchestration, infrastructure as code",
     "AWS, Google Cloud, Azure, Kubernetes, Docker, Terraform, Helm, Cloudflare, Vercel"),
    ("M04", "Data & Databases", "data-databases",
     "relational/NoSQL stores, warehouses, streaming, data catalogs",
     "PostgreSQL, MySQL, MongoDB, Redis, Snowflake, BigQuery, Kafka, dbt, Elasticsearch, Great Expectations"),
    ("M05", "Observability & Monitoring", "observability-monitoring",
     "logs, metrics, traces, errors, uptime",
     "Sentry, Grafana, Prometheus, Datadog, New Relic, OpenTelemetry, PagerDuty, Elastic APM"),
    ("M06", "Collaboration & Project Management", "collaboration-pm",
     "chat, docs, wikis, whiteboards, calendars",
     "Slack, Microsoft Teams, Notion, Confluence, Miro, Google Workspace, Zoom, Atlassian"),
    ("M07", "Marketing, Ads & Analytics", "marketing-ads-analytics",
     "web/product analytics, ad platforms, email/CRM, attribution",
     "Google Analytics, Google Ads, Meta Ads, LinkedIn Ads, HubSpot, Mailchimp, Segment, Amplitude, Mixpanel"),
    ("M08", "Social Media & Community", "social-community",
     "publishing, engagement, community, listening",
     "X/Twitter, LinkedIn, Instagram/Threads, TikTok, YouTube, Reddit, Discord, Pinterest, Brandwatch"),
    ("M09", "Content, CMS & SEO", "content-cms-seo",
     "content platforms, editorial, search optimization",
     "WordPress, Contentful, Sanity, Webflow, Ghost, Google Search Console, SEMrush, Ahrefs, Screaming Frog"),
    ("M10", "Design, Media & Creative", "design-media-creative",
     "design tools, asset management, video/audio pipelines, generative media",
     "Figma, Canva, Adobe Firefly, Miro, Cloudinary, Mux, Vimeo, YouTube Studio, ElevenLabs, OpenAI Whisper/TTS, Descript"),
    ("M11", "AI, LLM & Vector", "ai-llm-vector",
     "model providers, agent runtimes, embeddings, vector stores, evaluation",
     "OpenAI, Anthropic, Google Gemini, Hugging Face, OpenHands agent-server, Pinecone, Weaviate, Qdrant, pgvector, LangSmith, Weights & Biases"),
    ("M12", "Security, Identity & Compliance", "security-identity-compliance",
     "SAST/DAST, secrets, identity, vulnerability and compliance scanning",
     "Snyk, Semgrep, Trivy, Grype, HashiCorp Vault, 1Password, Okta, Auth0, Snyk IaC, OWASP ZAP, Vanta"),
    ("M13", "Finance, HR & Legal Ops", "finance-hr-legal",
     "billing, accounting, payroll, e-signature, contract lifecycle",
     "Stripe, NetSuite, QuickBooks, Workday, BambooHR, Gusto, DocuSign, Ironclad, Greenhouse"),
    ("M14", "Customer Support & CRM", "customer-support-crm",
     "ticketing, chat support, CRM, knowledge base, feedback",
     "Zendesk, Intercom, Salesforce, HubSpot CRM, Freshdesk, Pylon, Canny, Gainsight"),
]

TASK = """You are an expert technology architect writing ONE catalogue document for a corporate technology plan.

Write the file EXACTLY at this path: {path}

The document catalogues the MCP (Model Context Protocol) servers the company
needs in the category "{cat}" ({scope}).

Read the template at /workspace/plans/_templates/mcp-category.md and follow its
structure EXACTLY. Produce this document:

# {mid} — {cat}

**Scope:** {scope}

## 1. Overview
3-5 sentences: why this category matters, how it fits the two-plane MCP model
(shared tools-plane gateway vs. local data-plane servers), and the main adoption
consideration for the category.

## 2. Servers

| # | MCP Server | Purpose | Used by squads | Auth | Transport | Criticality | Free tier |
|---|---|---|---|---|---|---|---|
| 1 | ... | ... | ... | ... | ... | ... | ... |
... at least 8 rows ...

## 3. Notes

| # | Note |
|---|---|
| 1 | ... |
... 2-4 rows ...

## 4. Deployment notes
A short paragraph or 3-4 bullets saying which of these servers belong on the
shared gateway (tools plane) and which must run locally (data plane), and why.

HARD RULES
- Provide AT LEAST 8 MCP server rows, each a REAL, well-known product or an
  official/community MCP server relevant to the category. Consider these
  examples (use the ones that fit, and add more): {examples}.
- "Purpose" is one short phrase.
- "Used by squads" lists real squad IDs from the corporation (S01-S39).
- "Auth" is one of: API key, OAuth2, Service account, Token, None.
- "Transport" is one of: stdio, HTTP, SSE.
- "Criticality" is one of: Critical, High, Medium, Low.
- "Free tier" MUST state the real licensing/cost reality using one of:
  Free, Freemium, Open source, Paid — add a short qualifier in parentheses where
  useful (e.g. "Freemium (API limits)", "Paid (per seat)", "Open source (self-host)").
  Be accurate: open-source self-hostable servers are "Open source"; managed SaaS
  with a free plan is "Freemium"; fully paid is "Paid"; no-cost with no account
  is "Free".
- Keep everything HIGH LEVEL. No configuration detail, no code.
- Write ONLY the document. No preamble, no commentary, no code fences.

Write the file with the file editor, then reply DONE.
"""


def main() -> None:
    units = []
    for mid, cat, slug, scope, examples in CATS:
        path = str(OUT / f"{mid}-{slug}.md")
        units.append({
            "id": mid,
            "title": f"mcp-{mid}",
            "path": path,
            "task": TASK.format(path=path, mid=mid, cat=cat, scope=scope, examples=examples),
        })
    Path("/workspace/plans/_build/units_mcp.json").write_text(json.dumps(units, indent=2))
    print(f"wrote {len(units)} mcp units")


if __name__ == "__main__":
    main()
