# Agent Note：落云宗 Relay 以 OpenAI 兼容上游接缝实现真实 Key 零下发

Status: implemented

[English](2026-09-21-luoyunzong-relay-virtual-key.md) | 中文

## 问题

任务书阶段 3（`落云宗企业平台任务书.md`）：真实上游 Key 只存在于 Relay 进程；实例只持可吊销的虚拟钥匙；验收 = 实例内（环境变量、配置 dump、磁盘）任何地方无真实 Key，吊销后新请求立即被拒，换上游供应商实例零改动。DSH 的 LLM 路径本来就每请求经 credentials capability 解析凭证、以 `Authorization: Bearer` 发往 provider 配置的 `baseURL`——问题是这个接缝够不够，还是必须按任务书默认落点新增 `credentials-broker` Provider seam。

## 决策

`platform/supervisor/relay.mjs` —— 绑定 `127.0.0.1:9400` 的 Relay 进程，暴露 OpenAI 兼容的 `POST /v1/chat/completions`。虚拟钥匙（`vk-…`，随机 24 字节，存储只有 SHA-256）认证调用方；请求体的 `model` 对照钥匙的模型白名单（`*` 或显式列表）；模型在 `data/upstreams.json`（name、真实 baseURL、真实 key、服务的 models）中解析出唯一上游，把 Authorization 换成真实 Key，转发 `POST <上游 baseURL>/chat/completions`，流式与非流式响应原样透传。实例 home 只改 provider 路由：`baseURL: http://127.0.0.1:9400/v1`、`apiKeyEnv: LYZ_VIRTUAL_KEY`、`.credentials.yaml` 只含虚拟钥匙——此前过渡态拷入的真实凭证已删除。吊销经 mtime 缓存重读 `vkeys.json`，被吊销的钥匙在最下一个请求即被拒；已转发的 in-flight 请求不中断。`relay.log` 只记元数据（账号、实例、钥匙 id、模型、上游、状态、耗时），绝不落正文（任务书决定 5）。

两个关键细节。其一，pi-ai 的 openai-completions 适配器按 `model.provider` 与 `model.baseUrl` 自动检测线上兼容档（`open.bigmodel.cn` 命中 zai 档：不发 `store`、不发 `developer` 角色、不发 `reasoning_effort`、zai thinking 格式）；实例指到 `127.0.0.1` 会静默丢掉这套档，所以实例的 provider 路由改名为 `zai`（`providers` 字典的键就是自由命名的路由名），检测按名字命中，线上格式穿过 Relay 前后完全一致。其二，上游可能是 https：转发按协议选 `node:https` / `node:http`，构造包在 try/catch 里，一个配坏的上游只会 502 这一笔请求，不拖垮控制进程。

## 已否决的替代方案

**在 harness 内做 credentials-broker Provider seam。** 否决：provider 配置的 `baseURL` 接缝本来就存在且接受任何 OpenAI 兼容端点，让 Relay 扮演上游即可达成全部验收且 harness 零改动——任务书自己的规则（「仅当扩展点不够时才进仓库」）适用。broker Provider 同样需要客户端侧的信任凭证（换个名字的虚拟钥匙），零件更多而一个都没省。

**改造 credentials capability 让解析走 RPC 代理。** 同样的反对理由且面更大：为省一行配置改动 harness 拥有的解析语义。

## 后果

阶段 3 全部验收在无余额条件下成立（手头上游都没有余额）：实例 home 真实 Key 出现次数为零（用真实值 grep）；缺失/伪造/已吊销钥匙 401；授权模型转发上游后拿到的 429「余额不足」本身就是真实 Key 注入成功的证据（上游先认证后查余额——注入失败会是 401）；两次 `set-upstream` 把 `glm-5.3-flash` 从上游 zhipu 迁到 zhipu-backup，同一把虚拟钥匙照常打通（relay.log 显示上游已切换），实例零改动；e01 实例端到端 headless 调用走完 实例 → Relay → 上游，元数据全记录（7 条，含 agent 的重试连发——正是阶段 4 配额要管住的行为）。吊销已实测：同一 token 之前 400（已转发；空 messages 被上游参数校验拒绝）、`revoke-vkey` 之后立即 401。

代价与遗留：Relay 只信回环——远程部署与网关同置一个主机边界内；上游真实 Key 在明文 JSON 里（展示只给指纹），等阶段 3+ 控制面数据库替换；模型白名单 per-key 且静态，等控制台接管；流式 usage 的 token 数尚未抽取进计量存储——随阶段 4 落地，per-request 配额强制将并入现有 per-request 模型检查。压测中还暴露一个阶段 1 的潜伏缺陷：磁盘占用采样每 60 秒同步遍历 pnpm 重度的 home，一次饿死事件循环数十秒（请求只能在遍历间隙被服务）；遍历已改异步（`fs/promises` 线程池 I/O），间隔 120 秒，条目上限不变。
