# M01 — Code & Version Control

**Scope:** repositories, code review, package registries, code search

## Servers

| # | MCP Server | Purpose | Used by squads | Auth | Transport | Criticality |
|---|---|---|---|---|---|---|
| 1 | GitHub MCP Server | Source hosting, pull requests, issues, code review | S01, S02, S03, S04, S06, S07, S08, S10 | OAuth2 | HTTP/SSE | Critical |
| 2 | GitLab MCP Server | Repository hosting, merge requests, CI pipelines | S01, S04, S06, S07, S13 | Token | HTTP | High |
| 3 | Bitbucket MCP Server | Repository hosting and pull-request review | S04, S07, S39 | OAuth2 | HTTP | Medium |
| 4 | Filesystem MCP Server | Local repository and workspace file access | S01, S02, S05, S06, S09, S10, S11 | None | stdio | Critical |
| 5 | ripgrep Code-Search MCP Server | Fast local code and pattern search across repos | S02, S05, S07, S08, S10 | None | stdio | High |
| 6 | Sourcegraph MCP Server | Cross-repository code search and navigation | S01, S02, S08, S09, S10 | Token | HTTP | Medium |
| 7 | npm Registry MCP Server | JavaScript package lookup and metadata | S02, S03, S10 | Token | HTTP | High |
| 8 | PyPI Registry MCP Server | Python package lookup and metadata | S09, S10, S11, S12, S13 | Token | HTTP | High |
| 9 | Docker Hub MCP Server | Container image registry browse and pull | S01, S05, S06, S13 | Service account | HTTP | High |
| 10 | Sonatype Nexus MCP Server | Internal artifact repository and dependency proxy | S01, S04, S06, S08, S13 | Service account | HTTP | High |

## Notes

| # | Note |
|---|---|
| 1 | GitHub is the primary source-control system and the default code-review path; most engineering squads depend on it daily. |
| 2 | Registry servers (npm, PyPI, Nexus) are the main software-supply-chain entry points and must be reached through the corporate proxy with dependency scanning enabled. |
| 3 | Repository hosts are converging on GitHub and GitLab; Bitbucket remains only where legacy integrations require it. |
| 4 | Read-only code search and filesystem servers are low-risk to adopt broadly and are prerequisites for agent-assisted engineering. |
