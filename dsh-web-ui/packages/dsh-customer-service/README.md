# @linxin666/dsh-client-ui-customer-service

Customer service workbench plugin for the DSH Web GUI. AI-first C-end support with FastGPT RAG, faster-whisper ASR, edge-tts voice replies, ticket center, and channel management. Host-authoritative; backed by an independently deployed PostgreSQL stack.

## Features (V0.1 MVP)

- AI auto-reply with confidence threshold routing (auto-reply, suggest-reply, transfer-to-human)
- Real-time conversation workbench (WebSocket)
- Ticket center (multi-conversation merge / split)
- Knowledge base management (FastGPT dataset sync)
- Bot configuration (system prompt + fallback message + test sandbox)
- Channel gateway (WebSocket / WeChat / HTTP webhook - admin-configurable)
- Voice input (faster-whisper) + voice output (edge-tts, zero cost)
- Multi-language UI (zh / en)

## Architecture

The plugin is a thin Cordis bundle that mounts UI affordances into the DSH Web GUI. All heavy lifting (PostgreSQL, FastGPT, MinIO, faster-whisper) lives in a separate Docker Compose stack at `D:\\deepseek-harness\\dragon-engine\\customer-service-deploy\\`. The DSH host reverse-proxies `/cs-api/*` to the cs-backend service so the browser only talks to the DSH host.

```
DSH Browser
   |
DSH Host (this plugin)
   | /cs-api/*
cs-backend (Fastify + LLM/ASR/TTS adapters)
   |
PostgreSQL + FastGPT + MinIO + faster-whisper
```

## Install

```sh
# from dsh-web-ui repo root
pnpm install
pnpm --filter @linxin666/dsh-client-ui-customer-service build

# activate via profile (do NOT kill running dsh service)
dsh plugin --profile <your-profile> add link:./packages/dsh-customer-service
```

Restart the DSH service (do it yourself, not the agent) after plugin add.

## Configuration

The plugin accepts these settings (default in `Schema`):

| key | type | default | description |
|-----|------|---------|-------------|
| `announceToAgent` | bool | false | Inject plugin announcement into agent system prompt (issue #839; default off) |
| `backendUrl` | string | `http://localhost:8080` | cs-backend service address |
| `autoReplyThreshold` | number 0-1 | 0.75 | Confidence threshold for AI auto-reply |
| `transferHumanThreshold` | number 0-1 | 0.40 | Confidence threshold below which transfer to human |

## Tests

```sh
pnpm --filter @linxin666/dsh-client-ui-customer-service typecheck
pnpm --filter @linxin666/dsh-client-ui-customer-service test
```

Current coverage: router strategy + nav items invariant.

## License

MIT. Companion stack components keep their own licenses:

- FastGPT: MIT
- MinIO: AGPL-3.0 (self-host only; not network-distributed)
- faster-whisper: MIT
- edge-tts: MIT (uses public Microsoft Edge TTS endpoint)
- PostgreSQL: PostgreSQL License

## Repository rules

This package follows `packages/AGENTS.md` (host/client split, semantic attrs, i18n contract, no emoji in code or docs).
