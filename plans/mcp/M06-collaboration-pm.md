# M06 — Collaboration & Project Management

**Scope:** chat, docs, wikis, whiteboards, calendars

## Servers

| # | MCP Server | Purpose | Used by squads | Auth | Transport | Criticality |
|---|---|---|---|---|---|---|
| 1 | Slack | Team chat, channels, and notifications | S01, S02, S06, S07, S10, S39 | OAuth2 | HTTP/SSE | Critical |
| 2 | Microsoft Teams | Enterprise chat, meetings, and channels | S04, S06, S12, S14, S39 | OAuth2 | HTTP/SSE | High |
| 3 | Notion | Docs, wikis, and lightweight project tracking | S03, S05, S06, S10, S13 | Token | HTTP/SSE | High |
| 4 | Confluence | Enterprise wiki and knowledge base | S01, S04, S06, S08, S14 | API key | HTTP | High |
| 5 | Jira | Issue tracking and agile project management | S01, S02, S04, S06, S39 | OAuth2 | HTTP/SSE | Critical |
| 6 | Miro | Collaborative whiteboards and diagrams | S03, S06, S09, S15 | OAuth2 | HTTP/SSE | Medium |
| 7 | Google Workspace | Docs, Sheets, Drive, and shared files | S02, S03, S05, S06, S13 | OAuth2 | HTTP/SSE | High |
| 8 | Zoom | Video meetings and meeting recordings | S02, S06, S07, S39 | OAuth2 | HTTP/SSE | Medium |
| 9 | Atlassian | Unified access to Jira and Confluence data | S01, S04, S06, S14 | OAuth2 | HTTP/SSE | High |
| 10 | Microsoft 365 | Calendar, mail, and document collaboration | S04, S06, S11, S12 | OAuth2 | HTTP/SSE | High |
| 11 | Linear | Issue tracking and product planning | S03, S05, S06, S10 | API key | HTTP/SSE | Medium |
| 12 | GitHub Projects | Project boards and task tracking on code | S02, S06, S08, S09, S13 | Token | HTTP/SSE | Medium |

## Notes

| # | Note |
|---|---|
| 1 | Chat and issue tracking servers (Slack, Jira) are the company-wide baseline; nearly every squad depends on them, so onboarding is prioritised first. |
| 2 | Docs and wiki servers overlap heavily; squads should standardise on one primary knowledge platform to avoid duplicated and conflicting content. |
| 3 | All collaboration servers hold sensitive discussions and documents, so OAuth2 scopes and access reviews are required before rollout. |
| 4 | Whiteboard and meeting servers are lower criticality and can be adopted independently by product and design squads. |
