# M09 — Content, CMS & SEO

**Scope:** content platforms, editorial, search optimization

## Servers

| # | MCP Server | Purpose | Used by squads | Auth | Transport | Criticality |
|---|---|---|---|---|---|---|
| 1 | WordPress | Editorial publishing and CMS workflows | S16, S19, S23, S38 | API key | HTTP/SSE | High |
| 2 | Contentful | Headless CMS content modelling and delivery | S02, S04, S16, S24 | OAuth2 | HTTP/SSE | High |
| 3 | Sanity | Structured content platform and real-time editing | S02, S16, S24, S26 | Token | HTTP/SSE | Medium |
| 4 | Webflow | Marketing site design, CMS, and publishing | S15, S16, S25, S28 | API key | HTTP | Medium |
| 5 | Ghost | Publishing and newsletter editorial platform | S16, S19, S23 | API key | HTTP/SSE | Medium |
| 6 | Drupal | Enterprise CMS with content governance | S16, S19, S38 | OAuth2 | HTTP/SSE | Low |
| 7 | Google Search Console | Search performance, indexing, and sitemaps | S15, S17, S18 | OAuth2 | HTTP/SSE | Critical |
| 8 | SEMrush | Keyword research, rank tracking, competitive SEO | S15, S17, S18 | API key | HTTP/SSE | High |
| 9 | Ahrefs | Backlink and organic search intelligence | S16, S17, S18 | API key | HTTP/SSE | High |
| 10 | Screaming Frog | Technical SEO crawling and site audits | S02, S07, S17 | Token | HTTP | Medium |
| 11 | Yoast SEO | On-page SEO analysis and metadata governance | S02, S16, S17 | API key | HTTP | Medium |
| 12 | Algolia | Site search and content discovery | S02, S04, S16 | API key | HTTP/SSE | High |

## Notes

| # | Note |
|---|---|
| 1 | Google Search Console is the primary organic-search measurement source and a prerequisite for any SEO or content program. |
| 2 | Headless CMS platforms (Contentful, Sanity) are shared with engineering squads, so content-model changes require coordination with S02 and S04. |
| 3 | Marketing, social, and support squads share editorial tooling; standardize on one primary CMS per channel to avoid duplicated content. |
| 4 | Technical SEO crawlers should run read-only and rate-limited so audits never add load to production sites. |
