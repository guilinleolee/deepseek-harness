# @linxin666/dsh-client-ui-customer-service

DSH Web GUI 的客服工作台插件。AI 优先（C 端）+ 人工兜底，集成 FastGPT RAG、faster-whisper ASR、edge-tts 语音回复、工单中心与渠道管理。Host 权威，业务数据落在独立 PostgreSQL 栈。

## 功能（V0.1 MVP）

- AI 自动回复 + 置信度阈值路由（自动回复 / 建议回复 / 转人工）
- 实时会话工作台（WebSocket）
- 工单中心（多会话合并 / 拆分）
- 知识库管理（与 FastGPT 数据集同步）
- 智能客服配置（提示词 + 兜底话术 + 测试沙盒）
- 渠道接入（WebSocket / 微信公众号 / HTTP Webhook，管理员自配置）
- 语音输入（faster-whisper）+ 语音输出（edge-tts，零费用）
- 多语言 UI（中 / 英）

## 架构

本插件是一个轻量 Cordis bundle，仅在 DSH Web GUI 中挂载 UI 入口。重型依赖（PostgreSQL、FastGPT、MinIO、faster-whisper）由独立的 Docker Compose 栈承载，路径在 `D:\\deepseek-harness\\dragon-engine\\customer-service-deploy\\`。DSH host 通过 `/cs-api/*` 反向代理到 cs-backend，浏览器只与 DSH host 通信。

```
DSH Browser
   |
DSH Host (本插件)
   | /cs-api/*
cs-backend (Fastify + LLM/ASR/TTS 适配层)
   |
PostgreSQL + FastGPT + MinIO + faster-whisper
```

## 安装

```sh
# 在 dsh-web-ui 仓根目录
pnpm install
pnpm --filter @linxin666/dsh-client-ui-customer-service build

# 通过 profile 激活（不要 kill 运行中的 dsh 服务）
dsh plugin --profile <your-profile> add link:./packages/dsh-customer-service
```

`dsh plugin add` 后请你自己重启 DSH 服务（agent 不替你重启）。

## 配置项

插件接受以下设置（默认值见 `Schema`）：

| key | 类型 | 默认值 | 说明 |
|-----|------|--------|------|
| `announceToAgent` | bool | false | 向 agent 系统提示注入插件公告（issue #839，默认关闭） |
| `backendUrl` | string | `http://localhost:8080` | cs-backend 服务地址 |
| `autoReplyThreshold` | number 0-1 | 0.75 | AI 自动回复的置信度阈值 |
| `transferHumanThreshold` | number 0-1 | 0.40 | 转人工的置信度下限 |

## 测试

```sh
pnpm --filter @linxin666/dsh-client-ui-customer-service typecheck
pnpm --filter @linxin666/dsh-client-ui-customer-service test
```

当前覆盖：路由策略 + 导航项常量。

## 协议

MIT。配套组件各自保留协议：

- FastGPT: MIT
- MinIO: AGPL-3.0（仅自托管，不做网络分发）
- faster-whisper: MIT
- edge-tts: MIT（调用 Microsoft Edge TTS 公开端点）
- PostgreSQL: PostgreSQL License

## 仓内约束

本包遵循 `packages/AGENTS.md`（host/client 半区分层、语义属性、i18n 契约、代码与文档不加 emoji）。
