# kabage-tool-guard —— 实例内工具 RBAC 守卫（卡巴格平台阶段 9）

Cordis 插件：注册全局 `ctx.tools.guard()` 单调守卫，按平台下发的
`tool-policy.json` 在工具执行管线（`tools/pre-execute` 之后、dispatch 之前）
拒绝越权调用。被拒绝的调用以 `Error: <理由>` 返回给模型，同时把一条拒绝
事件追加到实例 home 的 `guard-events.jsonl` 桥文件，由平台 supervisor
daemon 周期转写成 `data/audit.jsonl`（`action=guard.deny`）后清空。

零 npm 依赖：只有 peer `@deepseek-ai/cordis`（不进插件包，经实例 profile
的 `$DSH_HOME/profiles/node_modules` 修复兜底目录解析，与安装共享同一
cordis 实例）。运行时只用 Node 内置 `node:fs`。

## 安装（平台侧一条命令）

```sh
cd platform/supervisor
node supervisor.mjs plugin-precheck --plugin ../plugins/kabage-tool-guard
# 隔离 home 真启动预检通过后投放全部实例并重启生效：
node supervisor.mjs plugin-push --plugin ../plugins/kabage-tool-guard --ids all
node supervisor.mjs plugin-activate --id e01   # 逐实例重启生效（或经管理台实例页）
```

本地路径安装走 pnpm（profile 目录 `nodeLinker: hoisted`、`autoInstallPeers:
false`），peer `@deepseek-ai/cordis` 不重复安装，由 `dsh web` 启动时的
`healProfilesModuleFallback` 建立的兜底目录按 Node 父目录解析补齐。

## 策略文件（由平台下发，勿手改）

路径：`<实例 home>/tool-policy.json`（即 `$DSH_HOME/tool-policy.json`），
由平台 `toolpolicy.mjs` 按实例归属账号的角色原子写入；管理台「部门与角色 →
实例内工具组策略」保存或成员角色变更后自动全量重写，实例侧 mtime 缓存
下一笔工具调用即生效，**无需重启实例**。

```json
{
  "role": "employee",
  "deny": ["command", "network"]
}
```

- `role`：下发时的角色名（仅用于拒绝文案与排查，不参与判定）。
- `deny`：禁用的工具组列表；元素只能是 `command` / `fs` / `network`。

语义：

- **文件不存在 = 全放行（fail-open）**。admin 实例可能从未下发过文件，
  隔离 precheck 的临时 home 也没有；缺文件不是错误。
- **文件存在但 JSON/结构非法 = fail-loud 抛错**。插件加载时抛错（实例启动
  失败），运行中热更新出的坏文件让当笔调用失败——坏配置必须可见。

## 工具组映射（真实注册名）

| 组 | 工具（DSH 注册名） |
|---|---|
| `command` 命令行 | `bash`、`pwsh`、`terminal_open`、`terminal_read`、`terminal_send`、`terminal_signal`、`terminal_list`、`terminal_close` |
| `fs` 文件 | `read`、`write`、`edit`、`read_image`、`str_replace_editor`、`glob`、`grep` |
| `network` 联网 | `web_search`、`web_fetch` |

映射外的内置工具（`todo_write`、`skill`、`subagent`、`session_*`、`job_*`、
`ask_user_question` 等）不属于受管组，一律放行。

## 配置（cordis.patch.yml，可覆盖）

| 键 | 缺省（`!!js` 求值） | 说明 |
|---|---|---|
| `policyPath` | `(process.env.DSH_HOME ?? ".") + "/tool-policy.json"` | 策略文件绝对路径 |
| `eventsPath` | `(process.env.DSH_HOME ?? ".") + "/guard-events.jsonl"` | 拒绝桥文件绝对路径 |

## 桥文件格式

一行一事件，字段对齐平台审计事件命名：

```json
{"ts":"2026-09-25T12:00:00.000Z","tool":"bash","group":"command","decision":"deny"}
```

平台转写（`toolpolicy.mjs` 的 `transcribeGuardEvents`）只取工具名/分组/
实例名标量，转写成功后清空桥文件——不含参数与任何内容正文（隐私红线）。

## 测试

```sh
node platform/plugins/kabage-tool-guard/test/guard-test.mjs
```

覆盖：分类映射逐工具名断言、策略读取（缺省/非法/危险结构）、mtime 热生效、
拒绝事件串行追加、guard allow/deny 行为（假 ctx.tools）。
