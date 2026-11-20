# M14 — Customer Support & CRM

**Scope:** ticketing, chat support, CRM, knowledge base, feedback

## Servers

| # | MCP Server | Purpose | Used by squads | Auth | Transport | Criticality |
|---|---|---|---|---|---|---|
| 1 | Zendesk | Support ticketing and help center | S01, S04, S38, S39 | OAuth2 | HTTP/SSE | Critical |
| 2 | Intercom | Live chat and customer messaging | S02, S15, S38 | OAuth2 | HTTP/SSE | High |
| 3 | Salesforce | Enterprise CRM and sales pipeline | S12, S37, S38 | OAuth2 | HTTP/SSE | Critical |
| 4 | HubSpot CRM | Marketing, sales, and service CRM | S15, S16, S37, S38 | OAuth2 | HTTP/SSE | High |
| 5 | Freshdesk | Ticketing and multi-channel support | S38, S39 | API key | HTTP | Medium |
| 6 | Pylon | B2B support inbox and account context | S37, S38 | API key | HTTP/SSE | Medium |
| 7 | Canny | Feature requests and product feedback | S24, S38, S39 | API key | HTTP | Medium |
| 8 | Gainsight | Customer success and health scoring | S12, S37, S38 | OAuth2 | HTTP/SSE | High |
| 9 | Zoho Desk | Ticketing and customer service workflows | S38, S39 | OAuth2 | HTTP | Low |
| 10 | ServiceNow | Enterprise service management and ITSM | S01, S06, S38, S39 | OAuth2 | HTTP/SSE | High |
| 11 | Confluence KB | Knowledge base articles for support agents | S01, S04, S38 | API key | HTTP | High |
| 12 | Front | Shared inbox and team email support | S37, S38 | API key | HTTP/SSE | Medium |

## Notes

| # | Note |
|---|---|
| 1 | Ticketing and CRM servers (Zendesk, Salesforce) are the support baseline and are shared with sales and operations, so they are onboarded first and treated as critical dependencies. |
| 2 | Knowledge base content overlaps with the collaboration category; support squads should source articles from a single authoritative wiki to avoid stale answers. |
| 3 | CRM and customer-success servers hold personal and contract data, so OAuth2 scopes and access reviews are required before rollout. |
| 4 | Feedback and low-volume desk servers are lower criticality and can be adopted independently by product and success squads. |
