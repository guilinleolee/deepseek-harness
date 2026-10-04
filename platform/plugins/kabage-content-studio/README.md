# kabage-content-studio · 内容创作工作台（受管投放）

卡巴格企业平台的内容创作能力包：把 DSH web 应用内建的内容创作四件套收编为
平台可治理的插件，按实例白名单下发。

## 投放内容

| 条目 | 包 | 作用 |
|---|---|---|
| `content-outputs` | @deepseek-ai/dsh-content-outputs | 产出库 Remote（唯一授权写路径，写 `<DSH_HOME>/outputs`） |
| `content-schedule` | @deepseek-ai/dsh-content-schedule | 发布日历 Remote |
| `content-topics` | @deepseek-ai/dsh-content-topics | 选题库 Remote |
| `ui-content-studio` | @deepseek-ai/dsh-client-ui-content-studio | 侧栏入口与工作台界面（纯 UI） |

## 与内建行的差异

- content-outputs 的内容 AI 配置从 `minimax-0801`（实例未注册，调用必失败）
  修正为 `zai` + `glm-5.3-flash`——统一走平台 Relay，按点数计量。
- 生命周期全部走管理台：precheck 真启动拦截 → 暂存 → 重启生效 → drift 对齐，
  开关动作落 `plugin.push` 等审计事件。

## 开通 / 停用某员工

1. 管理台 → 插件页 → kabage-content-studio → 勾选目标实例 → 投放（暂存）。
2. 重启该实例生效（或 plugin-activate）。
3. 停用 = plugin-remove + 重启；员工实例的 profile patch（cordis.patch.yml）
   中的 disabled 段与本体行可并存（禁用优先）。

## gather 出网白名单（订阅抓取）

订阅抓取（gather）在实例进程内直接出网取源，不经过工具守卫。放行范围两级控制：

- **Config 字段（主通道）**：投放后编辑实例 home 里本插件副本的
  `cordis.patch.yml`，给 `content-outputs` 行加 `config.allowedFeedHosts`
  （域名数组，条目含子域；空数组 = 全拒）→ 重启实例生效。
- **env 回退（独立部署用）**：实例环境变量 `GATHER_ALLOWED_FEED_HOSTS`
  （instances.json 按实例注入）：未设置 = 不限制；空串 = 全部拒绝；
  逗号/空格分隔域名 = 白名单。Config 有值时 env 被忽略。

机制实现见 content-outputs 的 `src/gather/feed.ts`
（`resolveAllowedFeedHosts` / `isFeedHostAllowed` / `GatherFetchDeps`）。

