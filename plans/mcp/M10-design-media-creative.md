# M10 — Design, Media & Creative

**Scope:** design tools, asset management, video/audio pipelines, generative media

## Servers

| # | MCP Server | Purpose | Used by squads | Auth | Transport | Criticality |
|---|---|---|---|---|---|---|
| 1 | Figma | Read and generate design files and components | S03, S06, S09, S15, S21 | OAuth2 | HTTP/SSE | High |
| 2 | Canva | Create and manage branded marketing assets | S06, S10, S15, S22 | OAuth2 | HTTP/SSE | Medium |
| 3 | Adobe Firefly | Generate and edit imagery and design assets | S09, S15, S21, S22 | API key | HTTP | Medium |
| 4 | Miro | Collaborative whiteboards and visual planning | S03, S06, S09, S15 | OAuth2 | HTTP/SSE | Medium |
| 5 | Cloudinary | Store, transform, and deliver media assets | S09, S11, S15, S21, S24 | API key | HTTP | High |
| 6 | Mux | Ingest, transcode, and stream video | S09, S11, S15, S24 | Token | HTTP | High |
| 7 | Vimeo | Host, manage, and share video content | S06, S15, S22 | OAuth2 | HTTP/SSE | Medium |
| 8 | YouTube Studio | Manage video uploads, metadata, and analytics | S10, S15, S22 | OAuth2 | HTTP/SSE | Medium |
| 9 | ElevenLabs | Generate synthetic speech and voice audio | S10, S15, S21, S24 | API key | HTTP | High |
| 10 | OpenAI Whisper | Transcribe and translate audio to text | S09, S10, S11, S24 | API key | HTTP | High |
| 11 | OpenAI TTS | Convert text to natural speech audio | S10, S15, S21 | API key | HTTP | Medium |
| 12 | Descript | Edit audio and video via transcript workflows | S15, S22, S24 | OAuth2 | HTTP/SSE | Low |
| 13 | Shutterstock | Source licensed stock imagery and footage | S15, S21, S22 | API key | HTTP | Low |
| 14 | Google Drive | Store and share creative source files | S03, S06, S09, S15 | OAuth2 | HTTP/SSE | High |

## Notes

| # | Note |
|---|---|
| 1 | Asset storage and delivery servers (Cloudinary, Google Drive) are the shared media backbone; creative and product squads depend on them before any design or media workflow can run. |
| 2 | Generative media servers (Firefly, ElevenLabs, Whisper, TTS) raise licensing, rights, and data-residency questions and need legal and security review before broad rollout. |
| 3 | Design tooling overlaps across Figma, Canva, and Miro; squads should agree on a primary design platform to avoid duplicated and divergent source files. |
| 4 | Video and audio pipeline servers carry the highest bandwidth and cost, so usage should be metered and budgeted per squad. |
