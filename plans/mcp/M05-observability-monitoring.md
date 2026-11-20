# M05 — Observability & Monitoring

**Scope:** logs, metrics, traces, errors, uptime

## Servers

| # | MCP Server | Purpose | Used by squads | Auth | Transport | Criticality |
|---|---|---|---|---|---|---|
| 1 | Sentry | Error tracking and release health | S02, S03, S06, S07, S10 | Token | HTTP/SSE | Critical |
| 2 | Grafana | Dashboards and alerting across data sources | S01, S05, S06, S13 | OAuth2 | HTTP/SSE | Critical |
| 3 | Prometheus | Metrics collection and querying | S01, S06, S13, S39 | Service account | HTTP | Critical |
| 4 | Datadog | Unified logs, metrics, and APM | S01, S04, S06, S13, S39 | API key | HTTP/SSE | High |
| 5 | New Relic | Application performance monitoring | S02, S04, S06, S13 | API key | HTTP/SSE | High |
| 6 | OpenTelemetry Collector | Vendor-neutral traces, metrics, and logs pipeline | S01, S05, S06, S10, S13 | None | HTTP | Critical |
| 7 | PagerDuty | Incident alerting and on-call escalation | S01, S06, S08, S39 | API key | HTTP/SSE | Critical |
| 8 | Elastic APM | Log search and application tracing | S04, S05, S06, S08 | API key | HTTP/SSE | High |
| 9 | Loki | Log aggregation and querying | S01, S05, S06, S13 | Service account | HTTP/SSE | High |
| 10 | Jaeger | Distributed tracing for microservices | S01, S04, S06, S10 | None | HTTP | Medium |
| 11 | Uptime Kuma | External uptime and endpoint monitoring | S06, S07, S39 | Token | HTTP | Medium |
| 12 | Better Stack | Uptime monitoring and status pages | S06, S19, S38, S39 | API key | HTTP/SSE | Medium |

## Notes

| # | Note |
|---|---|
| 1 | OpenTelemetry is the shared instrumentation standard; all squads emit telemetry through it to keep tooling swappable. |
| 2 | Sentry, Grafana, and PagerDuty form the baseline production trio and are adopted company-wide before other tools. |
| 3 | Observability MCP access should be read-mostly; write actions such as silences and escalations stay restricted to on-call roles. |
| 4 | AI squads (S10, S13) depend on trace and eval telemetry, so observability onboarding is a prerequisite for their pipelines. |
