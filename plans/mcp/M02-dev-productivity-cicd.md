# M02 — Developer Productivity & CI/CD

**Scope:** delivery pipelines, issue trackers, terminals, scaffolding

## Servers

| # | MCP Server | Purpose | Used by squads | Auth | Transport | Criticality |
|---|---|---|---|---|---|---|
| 1 | GitHub Actions | Trigger and inspect delivery pipelines | S01, S02, S03, S04, S06, S07 | Token | HTTP/SSE | Critical |
| 2 | GitHub | Browse repositories, issues, and pull requests | S01, S02, S03, S04, S05, S06, S07, S08 | Token | HTTP/SSE | Critical |
| 3 | GitLab | Repository, pipeline, and merge request access | S04, S06, S07, S13 | Token | HTTP/SSE | High |
| 4 | Jenkins | Run and monitor legacy build jobs | S06, S07, S13 | API key | HTTP | High |
| 5 | CircleCI | Manage hosted CI pipelines and builds | S02, S03, S07 | API key | HTTP | Medium |
| 6 | Argo CD | Drive GitOps deployments and sync status | S01, S06, S13 | Service account | HTTP/SSE | Critical |
| 7 | Jira | Track work items, sprints, and backlogs | S01, S04, S06, S07, S08, S39 | OAuth2 | HTTP/SSE | Critical |
| 8 | Linear | Manage issues, cycles, and roadmaps | S02, S03, S10, S24, S39 | API key | HTTP/SSE | High |
| 9 | Shell / Terminal | Run local commands and build tooling | S01, S02, S03, S04, S05, S06, S08, S09, S10, S11, S13 | None | stdio | Critical |
| 10 | Filesystem | Read and write project scaffolding and files | S01, S02, S03, S04, S05, S06, S07, S10, S13 | None | stdio | Critical |
| 11 | Playwright | Automate end-to-end browser tests | S02, S07, S24, S25 | None | stdio | High |
| 12 | Test Runner (Vitest/JUnit) | Execute unit and integration test suites | S01, S02, S03, S07, S13 | None | stdio | High |
| 13 | Docker | Build images and run containers locally | S01, S05, S06, S07, S13 | None | stdio | High |
| 14 | Kubernetes | Inspect and manage cluster workloads | S01, S06, S13 | Service account | HTTP/SSE | High |
| 15 | Nx | Orchestrate monorepo tasks and generators | S01, S02, S03, S10 | None | stdio | Medium |
| 16 | Confluence | Publish engineering docs and runbooks | S01, S06, S08, S39 | OAuth2 | HTTP/SSE | Medium |

## Notes

| # | Note |
|---|---|
| 1 | GitHub Actions and GitHub are the shared backbone; most squads depend on them, so treat both as tier-zero services. |
| 2 | Terminal and filesystem servers are prerequisites for every agent-driven workflow and must be deployed on all squad runners. |
| 3 | Issue trackers are split by division: Jira for engineering and operations, Linear for product and AI teams; avoid dual ownership of the same backlog. |
| 4 | GitOps servers (Argo CD, Kubernetes) are gated behind service-account auth and security review before broader rollout. |
