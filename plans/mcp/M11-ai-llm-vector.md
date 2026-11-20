# M11 — AI, LLM & Vector

**Scope:** model providers, agent runtimes, embeddings, vector stores, evaluation

## Servers

| # | MCP Server | Purpose | Used by squads | Auth | Transport | Criticality |
|---|---|---|---|---|---|---|
| 1 | OpenAI MCP Server | Access frontier chat, reasoning, and embedding models | S09, S10, S11, S12, S13, S14 | API key | HTTP/SSE | Critical |
| 2 | Anthropic Claude MCP Server | Access Claude models for agentic and long-context workloads | S10, S09, S14, S16 | API key | HTTP/SSE | Critical |
| 3 | Google Gemini MCP Server | Access multimodal generation and reasoning models | S09, S10, S12, S24, S26 | API key | HTTP/SSE | High |
| 4 | Hugging Face MCP Server | Discover, download, and serve open models and datasets | S09, S11, S13 | Token | HTTP | High |
| 5 | OpenHands Agent-Server MCP | Run and orchestrate autonomous coding and task agents | S01, S06, S07, S10 | Token | HTTP/SSE | High |
| 6 | Pinecone MCP Server | Store and query managed vector embeddings | S10, S11, S12, S17 | API key | HTTP | High |
| 7 | Weaviate MCP Server | Run semantic and hybrid search over vectorized content | S10, S16, S17, S21 | API key | HTTP | Medium |
| 8 | Qdrant MCP Server | Serve self-hosted vector search for retrieval pipelines | S10, S11, S13 | API key | HTTP | High |
| 9 | pgvector MCP Server | Add vector similarity search to PostgreSQL data | S05, S10, S12 | Service account | stdio | High |
| 10 | LangSmith MCP Server | Trace, evaluate, and monitor LLM applications | S09, S10, S14 | API key | HTTP | High |
| 11 | Weights & Biases MCP Server | Track experiments, metrics, and model artifacts | S09, S11, S13 | API key | HTTP | High |
| 12 | MLflow MCP Server | Register, version, and serve models across the lifecycle | S11, S13 | Service account | HTTP | Medium |

## Notes

| # | Note |
|---|---|
| 1 | Model-provider servers (OpenAI, Anthropic, Gemini) are foundational; most AI squads depend on at least one directly or through shared gateways. |
| 2 | Vector stores overlap by design: managed (Pinecone) for product retrieval, self-hosted (Qdrant) and pgvector for cost-sensitive and co-located workloads. |
| 3 | Evaluation and tracking servers are adoption-stage; standardize on LangSmith and W&B before broadening to more experiment tooling. |
| 4 | Provider access should route through governed API keys and shared gateways with spend and safety controls, not per-engineer credentials. |
