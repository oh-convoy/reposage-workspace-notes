# M12 — Security, Identity & Compliance

**Scope:** SAST/DAST, secrets, identity, vulnerability and compliance scanning

## Servers

| # | MCP Server | Purpose | Used by squads | Auth | Transport | Criticality |
|---|---|---|---|---|---|---|
| 1 | Snyk | Dependency and container vulnerability scanning | S01, S02, S04, S06, S07, S13 | Token | HTTP/SSE | Critical |
| 2 | Semgrep | Static analysis for custom code patterns | S01, S02, S03, S07, S10 | Token | HTTP/SSE | High |
| 3 | Trivy | Scan images, filesystems, and IaC for flaws | S01, S05, S06, S13 | None | stdio | Critical |
| 4 | Grype | Vulnerability scanning of container artifacts | S01, S05, S06, S13 | None | stdio | High |
| 5 | HashiCorp Vault | Dynamic secrets and credential brokering | S01, S05, S06, S07, S13 | Token | HTTP/SSE | Critical |
| 6 | 1Password | Manage developer secrets and service credentials | S02, S03, S06, S08, S10 | Service account | HTTP/SSE | High |
| 7 | Okta | Workforce identity, SSO, and access policies | S01, S06, S08, S39 | OAuth2 | HTTP/SSE | Critical |
| 8 | Auth0 | Customer authentication and authorization | S02, S03, S04, S07 | OAuth2 | HTTP/SSE | High |
| 9 | Snyk IaC | Detect misconfigurations in infrastructure code | S01, S05, S06, S13 | Token | HTTP/SSE | High |
| 10 | OWASP ZAP | Dynamic application security testing | S02, S03, S07, S24 | API key | HTTP/SSE | Medium |
| 11 | Vanta | Continuous compliance and control monitoring | S01, S06, S08, S39 | OAuth2 | HTTP/SSE | High |
| 12 | HashiCorp Boundary | Identity-based access to privileged targets | S01, S05, S06, S13 | mTLS | HTTP | Medium |

## Notes

| # | Note |
|---|---|
| 1 | Snyk, Trivy, and Semgrep form the baseline scanning trio and should be wired into every squad's pipeline before release gating. |
| 2 | Vault and Okta are shared platform dependencies; changes to either require security review and staged rollout across all squads. |
| 3 | Scanning servers should run read-only against source and artifacts; remediation actions stay with squad owners through pull requests. |
| 4 | Compliance tooling (Vanta) depends on evidence feeds from the scanning and identity servers, so adopt those first. |
