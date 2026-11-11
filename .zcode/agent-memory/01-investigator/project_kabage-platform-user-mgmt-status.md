---
name: kabage-platform-user-mgmt-status
description: 卡巴格企业平台用户管理代码的分支/合并/部署状态快照（2026-10-02 核实），platform/ 在当前分支是 untracked 部署副本
metadata:
  node_type: memory
  type: project
  originSessionId: sess_subagent_agent_c38aa329-73d3-47b4-8f68-884b6de07a65
---

卡巴格企业平台（原卡巴格）用户管理代码全部在 `feat/luoyunzong-console` 分支的 `platform/` 目录，**不在 `packages/`**（packages/identity 只是匿名遥测 id，与企业用户管理无关）。

2026-10-02 核实状态：
- PR #3 已于 2026-09-22 合并进 fork/master（内容截至 4912a002f4"console visual pass"）——早前"PR #3 未完成"的说法已过时。
- 未合并共 5 个提交：ea1af46111（stages 9-12，已推 fork 分支但无 PR）+ 400b58dcf9 / 6ddf9b64af / 7da4efb3a9（仅本地，7da4efb3a9 = 11b backlog 关闭：2FA 硬强制 enr=1、TOTP 重放防护、账号级限流桶、guard 审批组、tokens 页、角色矩阵编辑）。
- 磁盘 `platform/` 副本与本地分支 tip 7da4efb3a9 逐文件 diff 一致（部署副本已同步到最新代码）。
- 测试 11 套 615 项实测全绿（supervisor 9 套 501 + guard 72 + admin-tools 42），代码无 TODO/FIXME/stub。
- 挂起项全部是外部条件：真实 SMTP 凭证、真实企微/钉钉 SSO 凭证（钉钉需公网回调域名）、有余额上游（真实 LLM 工具拦截 + 真实模型对话）、跨月配额重置实测。
- 运行中 daemon（pid 记录于 data/daemon.pid，2026-10-01 22:44 启动）早于最后 3 个提交，新改动需 daemon 重启 + guard 插件重推才生效。

**Why:** platform/ 在 feat/dragon-bridge-integration 等分支上 untracked，`git status`/log 看不到这些信息；判定"开发完成"必须切到 console 分支核对。
**How to apply:** 下次评估平台完成度或部署时，先 `git rev-parse feat/luoyunzong-console fork/feat/luoyunzong-console` 对比本地/fork 差距，再 diff 磁盘 platform/ 与分支 tip，勿引用过时的"PR #3 未完成"结论。
