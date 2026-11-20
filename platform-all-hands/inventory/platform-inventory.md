# Platform Inventory — Sandboxes & Conversations

**Generated:** 2026-11-18 12:56 UTC  
**Source:** OpenHands Cloud V1 API (`/api/v1/sandboxes/search`, `/api/v1/app-conversations/search`), joined with local agent-server conversation events and on-disk artifacts.  
**Scope:** 22 sandboxes, 111 conversations.

> Every sandbox and every conversation is checked and given a verdict (OK / FAIL / RUNNING / IDLE) with the reason.

## Summary

| Metric | Value |
|---|---|
| Sandboxes | 22 |
| &nbsp;&nbsp;RUNNING | 2 |
| &nbsp;&nbsp;PAUSED | 20 |
| Conversations | 111 |
| &nbsp;&nbsp;finished | 66 |
| &nbsp;&nbsp;error | 25 |
| &nbsp;&nbsp;running | 1 |
| &nbsp;&nbsp;idle (no status) | 19 |

## What failed, and why

The planning documents succeeded. The failures are a separate body of work: when asked to regenerate the documents with a *better* model, I first probed which models this platform can run. **Every non-default model failed** — this sandbox holds an API key only for the default model (`openhands/deepseek-v4.1-flash`). Models like `aihubmix/*`, `zai/*`, `vertex_ai/*`, `azure/*`, and bare `gpt-5.x` have no key here.

| Failure class | Count | What it means |
|---|---|---|
| Auth: no API key for this model | 16 | the model was selected but has no credential on this sandbox |
| Azure model requires api_base | 7 | Azure deployments need an endpoint set explicitly |
| Vertex AI model: SDK not installed | 2 | Vertex partner models need the Vertex SDK, not the OpenAI-compatible path |

**Deliverable impact:** the two persona documents touched by the failed pilot (S01, S02) were deleted mid-run and have since been **regenerated successfully** with the working default model.

## LLM restoration — all conversations back on the default model

Repaired **29/29** conversations whose LLM config had been clobbered (non-default model with `base_url=None`, i.e. no credentials). Each was restored with a full `switch_llm` payload — default model + proxy base URL + the single platform-managed key, fetched per sandbox from `GET /api/keys/llm/managed/current`.

| # | Conversation ID | Title | Before (model) | After | Result |
|---|---|---|---|---|---|
| 1 | `d87f645b` | ep-aihubmix_claude_opus_5 | aihubmix/claude-opus-5 | openhands/deepseek-v4.1-flash | OK |
| 2 | `e1ce7e69` | personas-S02 | aihubmix/claude-opus-5 | openhands/deepseek-v4.1-flash | OK |
| 3 | `ad7523f4` | ab-azure/gpt-6.2-astra | azure/gpt-6.2-astra | openhands/deepseek-v4.1-flash | OK |
| 4 | `18efd346` | ep-aihubmix_kimi_k3 | aihubmix/kimi-k3 | openhands/deepseek-v4.1-flash | OK |
| 5 | `a7f94102` | ep-zai_glm_5_2 | zai/glm-5.2 | openhands/deepseek-v4.1-flash | OK |
| 6 | `360f31b5` | Conversation 360f31b5f4534a38a | aihubmix/gpt-5.5-pro | openhands/deepseek-v4.1-flash | OK |
| 7 | `f3207353` | ep-aihubmix_gpt_5_4_high | aihubmix/gpt-5.4-high | openhands/deepseek-v4.1-flash | OK |
| 8 | `83e76ad0` | ep-zai_glm_5_3 | zai/glm-5.3 | openhands/deepseek-v4.1-flash | OK |
| 9 | `cc3b7d2c` | ep-vertex_ai_claude_opus_5 | vertex_ai/claude-opus-5 | openhands/deepseek-v4.1-flash | OK |
| 10 | `beaf097a` | cand-openai/gpt-5.6 | openai/gpt-5.6 | openhands/deepseek-v4.1-flash | OK |
| 11 | `822d5644` | mp-vertex_ai_claude-opus-5 | vertex_ai/claude-opus-5 | openhands/deepseek-v4.1-flash | OK |
| 12 | `b87f4374` | mp-azure_gpt-6.2-sol | azure/gpt-6.2-sol | openhands/deepseek-v4.1-flash | OK |
| 13 | `997b9306` | llm-test | gpt-5.6 | openhands/deepseek-v4.1-flash | OK |
| 14 | `2c765157` | best-test | aihubmix/claude-opus-5 | openhands/deepseek-v4.1-flash | OK |
| 15 | `25866254` | cand-gpt-5.5 | gpt-5.5 | openhands/deepseek-v4.1-flash | OK |
| 16 | `b0a6816a` | mcp-agent-proof | azure/gpt-6.2-astra | openhands/deepseek-v4.1-flash | OK |
| 17 | `21a1ed08` | mp-aihubmix_claude-opus-5 | aihubmix/claude-opus-5 | openhands/deepseek-v4.1-flash | OK |
| 18 | `58a6839e` | mp-azure_gpt-6.2-astra | azure/gpt-6.2-astra | openhands/deepseek-v4.1-flash | OK |
| 19 | `cea2028d` | mp-azure_gpt-5.6-sol | azure/gpt-5.6-sol | openhands/deepseek-v4.1-flash | OK |
| 20 | `fe04b692` | mp-zai_glm-5.3 | zai/glm-5.3 | openhands/deepseek-v4.1-flash | OK |
| 21 | `cb0a799a` | mp-azure_gpt-6.1-sol | azure/gpt-6.1-sol | openhands/deepseek-v4.1-flash | OK |
| 22 | `6cb924a0` | personas-S01 | aihubmix/claude-opus-5 | openhands/deepseek-v4.1-flash | OK |
| 23 | `12657922` | inherit-test | aihubmix/claude-opus-5 | openhands/deepseek-v4.1-flash | OK |
| 24 | `89c6e436` | personas-S02 | aihubmix/claude-opus-5 | openhands/deepseek-v4.1-flash | OK |
| 25 | `72bb5e5a` | personas-S01 | aihubmix/claude-opus-5 | openhands/deepseek-v4.1-flash | OK |
| 26 | `ace944d0` | cand-openhands/gpt-5.6 | openhands/gpt-5.6 | openhands/deepseek-v4.1-flash | OK |
| 27 | `1902b59b` | cand-gpt-5.6 | gpt-5.6 | openhands/deepseek-v4.1-flash | OK |
| 28 | `db908428` | mp-aihubmix_gpt-5.5-pro | aihubmix/gpt-5.5-pro | openhands/deepseek-v4.1-flash | OK |
| 29 | `d9aacdd7` | cand-azure/gpt-5.6 | azure/gpt-5.6 | openhands/deepseek-v4.1-flash | OK |

## Deliverables — current state

| # | Deliverable set | Expected | Present | Verdict |
|---|---|---|---|---|
| 1 | Persona documents (`personas/S01–S39`) | 39 | 39 | OK |
| 2 | MCP catalogue documents (`mcp/M01–M15`) | 15 | 15 | OK |
| 3 | Squad catalogue (`squads/`) | 1 | 1 | OK |

## Outcome by work type

| # | Work type | Conversations | finished | error | idle | Deliverable produced |
|---|---|---|---|---|---|---|
| 1 | Persona doc | 47 | 43 | 4 | 0 | 47 |
| 2 | Model probe | 22 | 5 | 17 | 0 | — |
| 3 | GUI idle | 18 | 1 | 0 | 17 | — |
| 4 | MCP catalogue | 14 | 14 | 0 | 0 | 14 |
| 5 | LLM test | 3 | 1 | 2 | 0 | — |
| 6 | MCP proof | 2 | 1 | 1 | 0 | — |
| 7 | Prior mission | 2 | 0 | 0 | 2 | — |
| 8 | GUI session | 1 | 0 | 1 | 0 | — |
| 9 | Pilot child | 1 | 1 | 0 | 0 | — |
| 10 | RepoSage orchestrator | 1 | 0 | 0 | 0 | — |

## Table 1 — Sandboxes

| # | Sandbox ID | Status | Spec | Conversations | Started by | Created |
|---|---|---|---|---|---|---|
| 1 | `7dD6bXvmlYawLGXUGgxisY` | PAUSED | agent-server:1.60.1-python | 1 | None | 2026-11-11T07:45:41 |
| 2 | `18dVaqhNt92LKnu57HZhVN` | PAUSED | agent-server:1.62.0-python | 1 | APP_CONVERSATION | 2026-11-13T19:10:12 |
| 3 | `24nWgqBoSzpC4aFl7puofY` | RUNNING | agent-server:1.62.0-python | 91 | APP_CONVERSATION | 2026-11-17T23:21:29 |
| 4 | `2vVV0gpOhi9RHrlHNyiEKd` | PAUSED | agent-server:1.62.0-python | 1 | APP_CONVERSATION | 2026-11-17T23:55:35 |
| 5 | `2H2tmpJTMSdG0yTn5t8TPI` | PAUSED | agent-server:1.62.0-python | 1 | APP_CONVERSATION | 2026-11-17T23:55:41 |
| 6 | `1Q0SGa49Ztm6o5pkVU0KUL` | PAUSED | agent-server:1.62.0-python | 1 | APP_CONVERSATION | 2026-11-17T23:55:45 |
| 7 | `7XE7C4FP64gVZs4X6FrZ3c` | PAUSED | agent-server:1.62.0-python | 1 | APP_CONVERSATION | 2026-11-17T23:55:47 |
| 8 | `32p8dtKMVbSiW3t3h14VwB` | PAUSED | agent-server:1.62.0-python | 1 | APP_CONVERSATION | 2026-11-17T23:55:50 |
| 9 | `5n6YKciZHJUJBL0e7Guiph` | PAUSED | agent-server:1.62.0-python | 1 | APP_CONVERSATION | 2026-11-17T23:55:58 |
| 10 | `75NvTcrix2Lpezo8jLeUe4` | PAUSED | agent-server:1.62.0-python | 1 | APP_CONVERSATION | 2026-11-17T23:57:51 |
| 11 | `1eZ1WbojkggGXF6yjxNxu7` | PAUSED | agent-server:1.62.0-python | 1 | APP_CONVERSATION | 2026-11-17T23:57:58 |
| 12 | `5v8r2A8a5OIOJ9GyupwdLj` | PAUSED | agent-server:1.62.0-python | 0 | APP_CONVERSATION | 2026-11-17T23:58:18 |
| 13 | `2Z7RzGDgQyskgXu4dCChK6` | PAUSED | agent-server:1.62.0-python | 1 | APP_CONVERSATION | 2026-11-17T23:58:21 |
| 14 | `7dYWEn3XaIlburZKISQQ9Y` | PAUSED | agent-server:1.62.0-python | 1 | APP_CONVERSATION | 2026-11-17T23:58:24 |
| 15 | `65zLZxWSuRAqa3v6Fk0NOS` | PAUSED | agent-server:1.62.0-python | 1 | APP_CONVERSATION | 2026-11-17T23:58:27 |
| 16 | `42cJzUChbrwfNJHAFiC4rl` | PAUSED | agent-server:1.62.0-python | 1 | APP_CONVERSATION | 2026-11-17T23:58:30 |
| 17 | `1TmtCbDLXQ2vPYPpI9SMjT` | PAUSED | agent-server:1.62.0-python | 1 | APP_CONVERSATION | 2026-11-17T23:58:32 |
| 18 | `tOpoBm0zyiWc5T7D4USlN` | PAUSED | agent-server:1.62.0-python | 1 | APP_CONVERSATION | 2026-11-17T23:58:36 |
| 19 | `5cHpzK1O75y7RIjxws4m64` | PAUSED | agent-server:1.62.0-python | 1 | APP_CONVERSATION | 2026-11-17T23:58:39 |
| 20 | `2bWUtC5n7UfICqTgh6WLck` | PAUSED | agent-server:1.62.0-python | 1 | APP_CONVERSATION | 2026-11-17T23:58:46 |
| 21 | `5dfgnXQ9FWcLktAX4e324c` | PAUSED | agent-server:1.62.0-python | 1 | APP_CONVERSATION | 2026-11-17T23:58:47 |
| 22 | `212pYEw4QpziFrEn04W0PH` | RUNNING | agent-server:1.62.0-python | 1 | APP_CONVERSATION | 2026-11-18T08:16:41 |

### Table 1a — Sandbox verdicts

| # | Sandbox ID | Verdict | Note |
|---|---|---|---|
| 1 | `7dD6bXvmlYawLGXUGgxisY` | IDLE (paused) | 0 finished, 0 error |
| 2 | `18dVaqhNt92LKnu57HZhVN` | IDLE (paused) | 0 finished, 0 error |
| 3 | `24nWgqBoSzpC4aFl7puofY` | OK | 65 finished, 25 error |
| 4 | `2vVV0gpOhi9RHrlHNyiEKd` | IDLE (paused) | 0 finished, 0 error |
| 5 | `2H2tmpJTMSdG0yTn5t8TPI` | IDLE (paused) | 0 finished, 0 error |
| 6 | `1Q0SGa49Ztm6o5pkVU0KUL` | IDLE (paused) | 0 finished, 0 error |
| 7 | `7XE7C4FP64gVZs4X6FrZ3c` | IDLE (paused) | 0 finished, 0 error |
| 8 | `32p8dtKMVbSiW3t3h14VwB` | IDLE (paused) | 0 finished, 0 error |
| 9 | `5n6YKciZHJUJBL0e7Guiph` | IDLE (paused) | 0 finished, 0 error |
| 10 | `75NvTcrix2Lpezo8jLeUe4` | IDLE (paused) | 0 finished, 0 error |
| 11 | `1eZ1WbojkggGXF6yjxNxu7` | IDLE (paused) | 0 finished, 0 error |
| 12 | `5v8r2A8a5OIOJ9GyupwdLj` | IDLE (paused) | no conversations |
| 13 | `2Z7RzGDgQyskgXu4dCChK6` | IDLE (paused) | 0 finished, 0 error |
| 14 | `7dYWEn3XaIlburZKISQQ9Y` | IDLE (paused) | 0 finished, 0 error |
| 15 | `65zLZxWSuRAqa3v6Fk0NOS` | IDLE (paused) | 0 finished, 0 error |
| 16 | `42cJzUChbrwfNJHAFiC4rl` | IDLE (paused) | 0 finished, 0 error |
| 17 | `1TmtCbDLXQ2vPYPpI9SMjT` | IDLE (paused) | 0 finished, 0 error |
| 18 | `tOpoBm0zyiWc5T7D4USlN` | IDLE (paused) | 0 finished, 0 error |
| 19 | `5cHpzK1O75y7RIjxws4m64` | IDLE (paused) | 0 finished, 0 error |
| 20 | `2bWUtC5n7UfICqTgh6WLck` | IDLE (paused) | 0 finished, 0 error |
| 21 | `5dfgnXQ9FWcLktAX4e324c` | IDLE (paused) | 0 finished, 0 error |
| 22 | `212pYEw4QpziFrEn04W0PH` | OK | 1 finished, 0 error |

## Table 2 — Conversations

Newest first. **Verdict** combines the execution status with whether the expected artifact exists on disk.

| # | Conversation ID | Title | Work type | Model | Status | Verdict | Reason / note |
|---|---|---|---|---|---|---|---|
| 1 | `bcda8424` | personas-S01 | Persona doc | deepseek-v4.1-flash | finished | OK |  |
| 2 | `594ad343` | personas-S02 | Persona doc | deepseek-v4.1-flash | finished | OK |  |
| 3 | `074fd0ee` | hi | GUI idle | deepseek-v4.1-flash | finished | OK |  |
| 4 | `25866254` | cand-gpt-5.5 | Model probe | deepseek-v4.1-flash | finished | OK |  |
| 5 | `ace944d0` | cand-openhands/gpt-5.6 | Model probe | deepseek-v4.1-flash | error | FAIL | Auth: no API key for this model |
| 6 | `beaf097a` | cand-openai/gpt-5.6 | Model probe | deepseek-v4.1-flash | error | FAIL | Auth: no API key for this model |
| 7 | `d9aacdd7` | cand-azure/gpt-5.6 | Model probe | deepseek-v4.1-flash | error | FAIL | Azure model requires api_base |
| 8 | `1902b59b` | cand-gpt-5.6 | Model probe | deepseek-v4.1-flash | error | FAIL | Auth: no API key for this model |
| 9 | `6cb924a0` | personas-S01 | Persona doc | claude-opus-5 | error | FAIL | Auth: no API key for this model |
| 10 | `e1ce7e69` | personas-S02 | Persona doc | claude-opus-5 | error | FAIL | Auth: no API key for this model |
| 11 | `89c6e436` | personas-S02 | Persona doc | claude-opus-5 | error | FAIL | Auth: no API key for this model |
| 12 | `72bb5e5a` | personas-S01 | Persona doc | claude-opus-5 | error | FAIL | Auth: no API key for this model |
| 13 | `12657922` | inherit-test | LLM test | deepseek-v4.1-flash | error | FAIL | Auth: no API key for this model |
| 14 | `2c765157` | best-test | LLM test | claude-opus-5 | error | FAIL | Auth: no API key for this model |
| 15 | `18efd346` | ep-aihubmix_kimi_k3 | Model probe | kimi-k3 | finished | OK |  |
| 16 | `f3207353` | ep-aihubmix_gpt_5_4_high | Model probe | gpt-5.4-high | error | FAIL | Auth: no API key for this model |
| 17 | `d87f645b` | ep-aihubmix_claude_opus_5 | Model probe | claude-opus-5 | error | FAIL | Auth: no API key for this model |
| 18 | `a7f94102` | ep-zai_glm_5_2 | Model probe | glm-5.2 | finished | OK |  |
| 19 | `cc3b7d2c` | ep-vertex_ai_claude_opus_5 | Model probe | claude-opus-5 | error | FAIL | Vertex AI model: SDK not installed |
| 20 | `83e76ad0` | ep-zai_glm_5_3 | Model probe | glm-5.3 | error | FAIL | Auth: no API key for this model |
| 21 | `360f31b5` | Conversation 360f31b5f4534a38a72da0f78 | GUI session | gpt-5.5-pro | error | FAIL | Auth: no API key for this model |
| 22 | `3698838a` | ep-openhands_deepseek_v4_1_flash | Model probe | deepseek-v4.1-flash | finished | OK |  |
| 23 | `18d102ce` | mcp-proof2 | MCP proof | deepseek-v4.1-flash | finished | OK |  |
| 24 | `b0a6816a` | mcp-agent-proof | MCP proof | gpt-6.2-astra | error | FAIL | Azure model requires api_base |
| 25 | `b87f4374` | mp-azure_gpt-6.2-sol | Model probe | gpt-6.2-sol | error | FAIL | Azure model requires api_base |
| 26 | `cea2028d` | mp-azure_gpt-5.6-sol | Model probe | gpt-5.6-sol | error | FAIL | Azure model requires api_base |
| 27 | `cb0a799a` | mp-azure_gpt-6.1-sol | Model probe | gpt-6.1-sol | error | FAIL | Azure model requires api_base |
| 28 | `822d5644` | mp-vertex_ai_claude-opus-5 | Model probe | claude-opus-5 | error | FAIL | Vertex AI model: SDK not installed |
| 29 | `fe04b692` | mp-zai_glm-5.3 | Model probe | glm-5.3 | error | FAIL | Auth: no API key for this model |
| 30 | `db908428` | mp-aihubmix_gpt-5.5-pro | Model probe | gpt-5.5-pro | error | FAIL | Auth: no API key for this model |
| 31 | `58a6839e` | mp-azure_gpt-6.2-astra | Model probe | gpt-6.2-astra | error | FAIL | Azure model requires api_base |
| 32 | `21a1ed08` | mp-aihubmix_claude-opus-5 | Model probe | claude-opus-5 | error | FAIL | Auth: no API key for this model |
| 33 | `ad7523f4` | ab-azure/gpt-6.2-astra | Model probe | gpt-6.2-astra | error | FAIL | Azure model requires api_base |
| 34 | `3697d24f` | ab-default | Model probe | deepseek-v4.1-flash | finished | OK |  |
| 35 | `997b9306` | llm-test | LLM test | gpt-5.6 | finished | OK |  |
| 36 | `d7f318d2` | mcp-M14 | MCP catalogue | deepseek-v4.1-flash | finished | OK |  |
| 37 | `c994ab2c` | mcp-M13 | MCP catalogue | deepseek-v4.1-flash | finished | OK |  |
| 38 | `56f77c1e` | mcp-M12 | MCP catalogue | deepseek-v4.1-flash | finished | OK |  |
| 39 | `ae766f55` | mcp-M11 | MCP catalogue | deepseek-v4.1-flash | finished | OK |  |
| 40 | `c475ff8a` | mcp-M10 | MCP catalogue | deepseek-v4.1-flash | finished | OK |  |
| 41 | `9a81f739` | mcp-M09 | MCP catalogue | deepseek-v4.1-flash | finished | OK |  |
| 42 | `fb8cfcd5` | mcp-M08 | MCP catalogue | deepseek-v4.1-flash | finished | OK |  |
| 43 | `df1e9722` | mcp-M07 | MCP catalogue | deepseek-v4.1-flash | finished | OK |  |
| 44 | `5466d877` | mcp-M06 | MCP catalogue | deepseek-v4.1-flash | finished | OK |  |
| 45 | `f7c955cf` | mcp-M04 | MCP catalogue | deepseek-v4.1-flash | finished | OK |  |
| 46 | `bca25a0d` | mcp-M03 | MCP catalogue | deepseek-v4.1-flash | finished | OK |  |
| 47 | `dac40734` | mcp-M05 | MCP catalogue | deepseek-v4.1-flash | finished | OK |  |
| 48 | `47df08fd` | mcp-M02 | MCP catalogue | deepseek-v4.1-flash | finished | OK |  |
| 49 | `9f8024ce` | mcp-M01 | MCP catalogue | deepseek-v4.1-flash | finished | OK |  |
| 50 | `b943d038` | personas-S39 | Persona doc | deepseek-v4.1-flash | finished | OK |  |
| 51 | `b1daa2a4` | personas-S38 | Persona doc | deepseek-v4.1-flash | finished | OK |  |
| 52 | `3a90876e` | personas-S37 | Persona doc | deepseek-v4.1-flash | finished | OK |  |
| 53 | `4ab79e0e` | personas-S36 | Persona doc | deepseek-v4.1-flash | finished | OK |  |
| 54 | `a76d8a56` | personas-S35 | Persona doc | deepseek-v4.1-flash | finished | OK |  |
| 55 | `7a0cdc4d` | personas-S34 | Persona doc | deepseek-v4.1-flash | finished | OK |  |
| 56 | `28647c08` | personas-S33 | Persona doc | deepseek-v4.1-flash | finished | OK |  |
| 57 | `377fea7d` | personas-S32 | Persona doc | deepseek-v4.1-flash | finished | OK |  |
| 58 | `e452d08d` | personas-S31 | Persona doc | deepseek-v4.1-flash | finished | OK |  |
| 59 | `1fc8ad14` | personas-S30 | Persona doc | deepseek-v4.1-flash | finished | OK |  |
| 60 | `86b918d9` | personas-S29 | Persona doc | deepseek-v4.1-flash | finished | OK |  |
| 61 | `dad179fe` | personas-S28 | Persona doc | deepseek-v4.1-flash | finished | OK |  |
| 62 | `3af144a9` | personas-S27 | Persona doc | deepseek-v4.1-flash | finished | OK |  |
| 63 | `1de9861e` | personas-S26 | Persona doc | deepseek-v4.1-flash | finished | OK |  |
| 64 | `74aade5d` | personas-S25 | Persona doc | deepseek-v4.1-flash | finished | OK |  |
| 65 | `57f594ca` | personas-S24 | Persona doc | deepseek-v4.1-flash | finished | OK |  |
| 66 | `5e99d55e` | personas-S23 | Persona doc | deepseek-v4.1-flash | finished | OK |  |
| 67 | `df88d93c` | personas-S22 | Persona doc | deepseek-v4.1-flash | finished | OK |  |
| 68 | `37a74d78` | personas-S21 | Persona doc | deepseek-v4.1-flash | finished | OK |  |
| 69 | `d9e1d017` | personas-S20 | Persona doc | deepseek-v4.1-flash | finished | OK |  |
| 70 | `5fc9ef42` | personas-S19 | Persona doc | deepseek-v4.1-flash | finished | OK |  |
| 71 | `baad210f` | personas-S17 | Persona doc | deepseek-v4.1-flash | finished | OK |  |
| 72 | `ef5483ae` | personas-S18 | Persona doc | deepseek-v4.1-flash | finished | OK |  |
| 73 | `7990e473` | personas-S16 | Persona doc | deepseek-v4.1-flash | finished | OK |  |
| 74 | `5b387e74` | personas-S15 | Persona doc | deepseek-v4.1-flash | finished | OK |  |
| 75 | `f1627c11` | personas-S13 | Persona doc | deepseek-v4.1-flash | finished | OK |  |
| 76 | `d402236f` | personas-S14 | Persona doc | deepseek-v4.1-flash | finished | OK |  |
| 77 | `9521defd` | personas-S12 | Persona doc | deepseek-v4.1-flash | finished | OK |  |
| 78 | `93a6d140` | personas-S10 | Persona doc | deepseek-v4.1-flash | finished | OK |  |
| 79 | `e130f8a5` | personas-S11 | Persona doc | deepseek-v4.1-flash | finished | OK |  |
| 80 | `5737965c` | personas-S09 | Persona doc | deepseek-v4.1-flash | finished | OK |  |
| 81 | `a1643bf0` | personas-S08 | Persona doc | deepseek-v4.1-flash | finished | OK |  |
| 82 | `57c47ed7` | personas-S07 | Persona doc | deepseek-v4.1-flash | finished | OK |  |
| 83 | `be2e4152` | personas-S03 | Persona doc | deepseek-v4.1-flash | finished | OK |  |
| 84 | `a4f8710a` | personas-S04 | Persona doc | deepseek-v4.1-flash | finished | OK |  |
| 85 | `ccac1989` | personas-S05 | Persona doc | deepseek-v4.1-flash | finished | OK |  |
| 86 | `81ff38f4` | personas-S01 | Persona doc | deepseek-v4.1-flash | finished | OK |  |
| 87 | `8c051e01` | personas-S06 | Persona doc | deepseek-v4.1-flash | finished | OK |  |
| 88 | `8373bea8` | personas-S02 | Persona doc | deepseek-v4.1-flash | finished | OK |  |
| 89 | `5cbfa318` | personas-S02 | Persona doc | deepseek-v4.1-flash | finished | OK |  |
| 90 | `42059c48` | personas-S01 | Persona doc | deepseek-v4.1-flash | finished | OK |  |
| 91 | `b7706805` | pilot-child | Pilot child | deepseek-v4.1-flash | finished | OK |  |
| 92 | `564b0dbb` | hi | GUI idle | deepseek-v4.1-flash | None | IDLE | Never started (idle GUI session) |
| 93 | `21aadd49` | hi | GUI idle | deepseek-v4.1-flash | None | IDLE | Never started (idle GUI session) |
| 94 | `9653d7c2` | hi | GUI idle | deepseek-v4.1-flash | None | IDLE | Never started (idle GUI session) |
| 95 | `535e9f85` | hi | GUI idle | deepseek-v4.1-flash | None | IDLE | Never started (idle GUI session) |
| 96 | `a01ccc1e` | hi | GUI idle | deepseek-v4.1-flash | None | IDLE | Never started (idle GUI session) |
| 97 | `33a9e6f7` | hi | GUI idle | deepseek-v4.1-flash | None | IDLE | Never started (idle GUI session) |
| 98 | `a33a20f0` | hi | GUI idle | deepseek-v4.1-flash | None | IDLE | Never started (idle GUI session) |
| 99 | `ba99206e` | hi | GUI idle | deepseek-v4.1-flash | None | IDLE | Never started (idle GUI session) |
| 100 | `ed5fc7b2` | hi | GUI idle | deepseek-v4.1-flash | None | IDLE | Never started (idle GUI session) |
| 101 | `69498744` | hi | GUI idle | deepseek-v4.1-flash | None | IDLE | Never started (idle GUI session) |
| 102 | `3ca61786` | hi | GUI idle | deepseek-v4.1-flash | None | IDLE | Never started (idle GUI session) |
| 103 | `ee3f7556` | hi | GUI idle | deepseek-v4.1-flash | None | IDLE | Never started (idle GUI session) |
| 104 | `96aa4c1d` | hi | GUI idle | deepseek-v4.1-flash | None | IDLE | Never started (idle GUI session) |
| 105 | `7a39b6ac` | hi | GUI idle | deepseek-v4.1-flash | None | IDLE | Never started (idle GUI session) |
| 106 | `33fb7504` | hi | GUI idle | deepseek-v4.1-flash | None | IDLE | Never started (idle GUI session) |
| 107 | `0fc59b06` | hi | GUI idle | deepseek-v4.1-flash | None | IDLE | Never started (idle GUI session) |
| 108 | `12bbbea9` | hi | GUI idle | deepseek-v4.1-flash | None | IDLE | Never started (idle GUI session) |
| 109 | `9014dc44` | sandbox-01-RepoSage | RepoSage orchestrator | gpt-5.5 | running | RUNNING | In progress |
| 110 | `aded0618` | Mission: Reverse Engineering Repo Anal | Prior mission | deepseek-v4.1-flash | None | IDLE | Never started (idle GUI session) |
| 111 | `8f4b42d7` | Mission: GitHub branding-practice-and- | Prior mission | deepseek-v4.1-flash | None | IDLE | Never started (idle GUI session) |

