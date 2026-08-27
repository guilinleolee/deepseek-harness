# AGENTS.md - dsh-customer-service

DSH Web GUI customer service workbench plugin. AI-first (C-end) with human fallback.

## 形态

- Independent cordis bundle package, follows all constraints in ../AGENTS.md
- host half (src/index.ts) mounts API proxy routes + systemPrompt hook (default off)
- client half (src/client/index.tsx) mounts sidebar entry + settings section + i18n
- Pure logic (router, type constants) in src/core/, shared by both halves

## 架构边界

- This plugin does NOT directly connect to PostgreSQL / FastGPT / MinIO / Whisper
- Those are served by independently deployed cs-backend (deepseek-harness/dragon-engine/customer-service-deploy/)
- DSH host reverse-proxies /cs-api/* to cs-backend; browser only talks to DSH host

## 系统提示公告 (issue #839)

- announceToAgent default false (keep agent system prompt clean)
- Users opt in via settings panel
- Announcement text only states capabilities, constraints, triggers; no long paragraphs

## 文件归属

- host protocol / API proxy / systemPrompt hooks in src/
- browser transport and UI in src/client/
- pure router logic and types in src/core/

## 测试纪律

- Changes to router strategy, threshold constants, or API protocol require tests/ unit tests
- No fixture depending on DSH source checkout

## 提交前检查

Run from repo root:

    pnpm --filter @linxin666/dsh-client-ui-customer-service typecheck
    pnpm --filter @linxin666/dsh-client-ui-customer-service test
    pnpm --filter @linxin666/dsh-client-ui-customer-service build
    pnpm docs:check
