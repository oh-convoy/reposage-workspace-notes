# M08 — Social Media & Community

**Scope:** publishing, engagement, community, listening

## Servers

| # | MCP Server | Purpose | Used by squads | Auth | Transport | Criticality |
|---|---|---|---|---|---|---|
| 1 | X (Twitter) API | Post, reply, and monitor brand mentions | S04, S06, S10 | OAuth2 | HTTP | High |
| 2 | LinkedIn Marketing | Publish company updates and lead campaigns | S02, S04, S09 | OAuth2 | HTTP | High |
| 3 | Instagram Graph / Threads | Schedule posts and track engagement metrics | S04, S10 | OAuth2 | HTTP | Medium |
| 4 | TikTok Business | Upload short-form video and pull performance data | S10, S11 | OAuth2 | HTTP | Medium |
| 5 | YouTube Data | Manage video uploads and comments | S05, S10 | OAuth2 | HTTP | High |
| 6 | Reddit API | Community posting and thread monitoring | S06, S12 | OAuth2 | HTTP | Medium |
| 7 | Discord Bot | Community server moderation and support triage | S06, S12 | Token | WebSocket | High |
| 8 | Pinterest API | Publish pins and catalogue engagement | S04, S11 | OAuth2 | HTTP | Low |
| 9 | Brandwatch | Social listening and sentiment analysis | S06, S09 | API key | HTTP | High |
| 10 | Slack Community Bridge | Route community signals into internal channels | S06, S12 | Token | HTTP/SSE | Medium |

## Notes

| # | Note |
|---|---|
| 1 | Social publishing servers share a common OAuth2 token lifecycle, so onboarding is best handled as one batch. |
| 2 | Listening (Brandwatch) is a cross-cutting dependency for S06 and S09; degradation directly affects sentiment reporting. |
| 3 | Platform API rate limits and policy changes are the primary adoption risk; each server needs an owner squad. |
| 4 | Discord and Slack bridges depend on community moderation workflows and should be piloted before broad rollout. |
