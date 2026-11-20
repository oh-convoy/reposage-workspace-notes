# M04 — Data & Databases

**Scope:** relational/NoSQL stores, warehouses, streaming, data catalogs

## Servers

| # | MCP Server | Purpose | Used by squads | Auth | Transport | Criticality |
|---|---|---|---|---|---|---|
| 1 | PostgreSQL MCP Server | Query and manage relational application data | S01, S04, S05, S12 | Service account | stdio | Critical |
| 2 | MySQL MCP Server | Access legacy and departmental relational stores | S01, S05, S35 | Service account | stdio | High |
| 3 | MongoDB MCP Server | Work with document-oriented operational data | S03, S04, S05 | Token | stdio | High |
| 4 | Redis MCP Server | Inspect caches, queues, and session state | S01, S06, S10 | Token | stdio | High |
| 5 | Snowflake MCP Server | Query the enterprise data warehouse | S05, S12, S18, S35 | Service account | HTTP | Critical |
| 6 | BigQuery MCP Server | Analyze large-scale analytics datasets | S05, S12, S18 | Service account | HTTP | High |
| 7 | Apache Kafka MCP Server | Publish, consume, and inspect event streams | S05, S06, S11, S13 | mTLS | HTTP/SSE | Critical |
| 8 | dbt MCP Server | Trigger and inspect data transformation models | S05, S12, S13 | Token | stdio | High |
| 9 | Elasticsearch MCP Server | Search and analyze indexed logs and documents | S06, S08, S17 | API key | HTTP | High |
| 10 | Great Expectations MCP Server | Validate data quality and pipeline expectations | S05, S07, S13 | Service account | stdio | Medium |
| 11 | Data Catalog (DataHub) MCP Server | Discover and govern dataset metadata and lineage | S05, S12, S14 | OAuth2 | HTTP | Medium |

## Notes

| # | Note |
|---|---|
| 1 | PostgreSQL, Snowflake, and Kafka are foundational; most data and AI squads depend on them directly or indirectly. |
| 2 | Warehouse and streaming access should go through governed service accounts with least-privilege grants, not personal credentials. |
| 3 | Catalog and data-quality servers are adoption-stage: standardize on them before broadening to more stores. |
| 4 | A small number of overlapping relational and NoSQL servers is intentional for legacy systems; consolidate during migration. |
