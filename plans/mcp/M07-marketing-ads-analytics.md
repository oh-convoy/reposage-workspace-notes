# M07 — Marketing, Ads & Analytics

**Scope:** web/product analytics, ad platforms, email/CRM, attribution

## Servers

| # | MCP Server | Purpose | Used by squads | Auth | Transport | Criticality |
|---|---|---|---|---|---|---|
| 1 | Google Analytics | Web and product traffic analytics | S06, S10, S14, S21 | OAuth2 | HTTP/SSE | Critical |
| 2 | Google Ads | Paid search campaign management | S14, S21, S22 | OAuth2 | HTTP/SSE | High |
| 3 | Meta Ads | Social ad campaign management | S14, S21, S22 | OAuth2 | HTTP/SSE | High |
| 4 | LinkedIn Ads | B2B ad campaign management | S14, S21, S23 | OAuth2 | HTTP/SSE | Medium |
| 5 | HubSpot | CRM, contacts, and lifecycle marketing | S14, S19, S21 | API key | HTTP/SSE | Critical |
| 6 | Mailchimp | Email campaign and audience management | S14, S21 | API key | HTTP/SSE | Medium |
| 7 | Segment | Customer data pipeline and event routing | S04, S10, S14, S21 | API key | HTTP/SSE | Critical |
| 8 | Amplitude | Product analytics and behavioral cohorts | S06, S10, S14, S21 | API key | HTTP/SSE | High |
| 9 | Mixpanel | Product analytics and funnel analysis | S06, S10, S21 | API key | HTTP/SSE | Medium |
| 10 | Braze | Cross-channel customer engagement | S14, S19, S21 | API key | HTTP/SSE | Medium |
| 11 | AppsFlyer | Mobile attribution and marketing measurement | S10, S14, S21 | API key | HTTP/SSE | High |
| 12 | Salesforce Marketing Cloud | Enterprise campaign and journey orchestration | S14, S19, S21 | OAuth2 | HTTP/SSE | High |

## Notes

| # | Note |
|---|---|
| 1 | Segment is the shared customer data backbone; ad, CRM, and analytics servers depend on its event stream for consistent attribution. |
| 2 | Marketing and growth squads (S14, S21) are the primary consumers; analytics and data squads (S06, S10) supply the event and model layer. |
| 3 | Ad platform servers are read-heavy for reporting but carry spend-related write actions, so access should be scoped and audited. |
| 4 | CRM and email servers hold customer PII; onboarding requires privacy review before any squad gains write access. |
