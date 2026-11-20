# M03 — Cloud & Infrastructure

**Scope:** cloud providers, containers, orchestration, infrastructure as code

## Servers

| # | MCP Server | Purpose | Used by squads | Auth | Transport | Criticality |
|---|---|---|---|---|---|---|
| 1 | AWS MCP Server | Provision and manage AWS cloud resources | S06, S10, S14 | API key | stdio | Critical |
| 2 | Google Cloud MCP Server | Manage GCP services and projects | S06, S11, S14 | Service account | stdio | High |
| 3 | Azure MCP Server | Operate Azure resources and subscriptions | S06, S12, S14 | OAuth2 | stdio | High |
| 4 | Kubernetes MCP Server | Inspect and manage cluster workloads | S06, S08, S10, S13 | Token | stdio | Critical |
| 5 | Docker MCP Server | Build and run container images | S06, S08, S09, S13 | None | stdio | High |
| 6 | Terraform MCP Server | Plan and apply infrastructure as code | S06, S10, S14 | Token | stdio | Critical |
| 7 | Helm MCP Server | Manage Kubernetes application releases | S06, S10, S13 | Token | stdio | High |
| 8 | Cloudflare MCP Server | Manage DNS, CDN and edge services | S07, S11, S15 | API key | HTTP/SSE | Medium |
| 9 | Vercel MCP Server | Deploy and manage frontend hosting | S03, S07, S15 | Token | HTTP | Medium |
| 10 | Pulumi MCP Server | Provision cloud infrastructure as code | S06, S10, S14 | API key | stdio | Medium |

## Notes

| # | Note |
|---|---|
| 1 | Cloud provider servers are shared foundations; a change in one affects every squad that deploys to that platform. |
| 2 | Kubernetes, Docker and Terraform are the highest-dependency servers and should be prioritised for onboarding. |
| 3 | Infrastructure as code servers depend on cloud provider credentials; access review is required before rollout. |
| 4 | Edge and hosting servers are lower risk and can be adopted independently by product squads. |
