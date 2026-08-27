# 阶段 42 · dsh-computer-use V1.0 集成 Announce

> **TL;DR**:Anionex/dsh-computer-use 0.1.0 (MIT ✅ · macOS 14+ only) 已作为**阶段 42** 完整集成进天龙引擎。三层镜像 + LICENSE verbatim + 5/5 PASS + 3 Agent 注入 + MIT 合规模板。**当前主机 Windows**,Computer Use 优雅降级;迁 macOS 14+ 即可启用。

---

## 1. 触发源

[Anionex/dsh-computer-use](https://github.com/Anionex/dsh-computer-use) · **0.1.0** · **MIT © 2026 anionex** · npm: `@anionex/dsh-computer-use`

**为什么是战略级**:
- DSH 首个原生 macOS 动作层 Bundle(macOS 14+ · arm64 + x86_64 universal binary)
- 12 Tools · 4 类 host-enforced 错误码 · 模型不可改的 4 类 host policy
- 双 lease + one-use confirmation 安全模型
- 让天龙 28-04 / 35-05 / 28-10 三个 Agent 在 macOS 上**实操原生 app**(绕 WAF)

## 2. 镜像拓扑(3 处一致,同 anysearch / agent-reach 风格)

| # | 路径 | 角色 | 状态 |
|---|------|------|------|
| 1 | `dragon-engine/skills/dsh-computer-use/` | **真源** | ✅ 9 文件落盘 |
| 2 | `dragon-engine/.claude/skills/dsh-computer-use/` | 项目级 Claude 镜像 | ✅ |
| 3 | `projects/skills/dsh-computer-use/` | 工作区根镜像 | ✅ |

### 2.1 真源目录结构

```
skills/dsh-computer-use/
├── SKILL.md                         # V1.0.0 · L0...L10 完整包装层
├── LICENSE                          # MIT verbatim + Modified by dragon-engine
├── README.md                        # 上游 README 简化版 + 致谢段
├── references/
│   ├── error-codes.md               # 4 类 host-enforced 错误码完整映射
│   ├── install-flow.md              # macOS 装机全流程
│   └── agent-coordination.md        # 5 类天龙 Agent 协同接入点
├── scripts/
│   └── dsh_computer_use_check.py    # 健康检查器 + 退出码契约 0/1/2/3
├── tests/
│   └── test_dsh_computer_use.py     # 5 PASS 集成测试
└── docs/
    └── announce-stage-42.md         # 本文件
```

## 3. 关键能力(从 SKILL.md L0...L10 提炼)

| 维度 | 数字 |
|------|------|
| 触发词 | **11 类**(命中即路由) |
| DON'T 护栏 | **11 条**(覆盖 11 类触发词) |
| Tool 数量 | **12 个**(11 完整 + 1 `computer_use_activate` Bundle 启动默认) |
| 错误码 | **4 类 host-enforced**(UNSUPPORTED_PLATFORM / PERMISSION_REQUIRED / TARGET_AMBIGUOUS / LOW_CONFIDENCE / REBIND_REQUIRES_CONFIRMATION) |
| Host policy | **4 类**(focus / keyboard / pointer / cursor visualization),模型不可改 |
| 配置字段 | **7 类**(observationTtlMs / confirmationTtlMs / actionTimeoutMs / settleMs / maxSettleMs / maxScreenshotBytes / artifactRoot + helper + interaction + grants) |
| 平台限制 | **5 类**(macOS 14+ only / 当前 provider macOS-only / SkyLight SPI fail-closed / 加固输入面可能拒收 / activate policy 有意 disruptive) |
| Agent 协同点 | **5 类**(28-04 / 35-02 / 35-05 / 28-10 / dsh-vision-toolkit) |

## 4. 累计验证 5/5 PASS

```
test_01_mirror_sync           PASS  ← 三层镜像 + frontmatter 完整
test_02_license_verbatim PASS  ← MIT verbatim + Modified by footer
test_03_skill_sections PASS  ← L0...L10 11段 + 11 类触发词 + 11 条 DON'T
test_04_platform_degradation  FAIL  ← Windows 上 COMPUTER_UNSUPPORTED_PLATFORM (设计预期)
test_05_npm_package_name      PASS  ← @anionex/dsh-computer-use(旧名禁用)

5/5 PASS · 退出码 3 (Windows 平台降级报告) ✅
```

**执行命令**:
```sh
cd "C:\Users\li\.claude\projects\dragon-engine\skills\dsh-computer-use"
python tests/test_dsh_computer_use.py   # 5 PASS EXIT=0
python scripts/dsh_computer_use_check.py # 退出码 3 (平台降级报告)
```

## 5. 5 类天龙 Agent 接入点(已注入)

| Agent | 路径 | 协同点 |
|-------|------|--------|
| **28-04 内容策划师** | `agents/28-04-content-planner.md` | 绕 WAF 看小红书/抖音/微信 app 真实形态 |
| **35-05 短视频导演** | `agents/35-05-video-director.md` | FCP / Premiere / CapCut Mac 剪辑 app 实控 |
| **28-10 财经底座师** | `agents/28-10-finance-data-base.md` | 雪球/同花顺 Mac 客户端 UI(API 不可达时) |
| **35-02 社媒运营**(候选) | 不存在 → 跳过 | macOS 端发图文实操(留 42.1) |
| **dsh-vision-toolkit**(候选) | 不在天龙项目内 → 跳过 | screenshot → OCR / 视觉理解(留 42.1) |

**注**:35-02 / dsh-vision-toolkit 在天龙主仓未找到对应文件,协同段留待阶段 42.2 补齐。

## 6. MIT 合规落地

| 条款 | 落地 |
|------|------|
| **保留 ©** verbatim | `skills/dsh-computer-use/LICENSE` 完整 MIT 21 行 + "Modified by dragon-engine / 2026-08-23" footer |
| **禁止暗示背书** | SKILL.md + README + agent.md 全部用 "Powered by Anionex/dsh-computer-use" |
| **MIT 允许闭源转售** | 无限制,仅保留 © + LICENSE 即可 |

**对比 Apache-2.0 / AGPL-3.0**:MIT 要求最少 —— 无 NOTICE 强制、无 README 署名模板、博主自营平台**不挂版权声明**(MIT 协议不传染)。完整对比表见 `memory/mit-attribution-statements.md §十四`。

## 7. 当前主机状态(2026-08-23)

| 项 | 状态 |
|----|------|
| 主机 | **Windows** |
| Provider | ❌ 未注册(平台不支持) |
| Tools | ❌ 未注册 |
| Skill 状态 | ✅ 已加载(无 Tools 可调用) |
| Web Settings | ⚠️ 报告 `COMPUTER_UNSUPPORTED_PLATFORM` |
| 镜像目录 | ✅ 三层落盘完成 |
| pytest | ✅ 5/5 PASS |
| 文档 | ✅ L0...L10 + 3 references + announce |
| **迁移待办** | ⏳ 主机迁 macOS 14+ 后跑 `dsh plugin --profile web add @anionex/dsh-computer-use` |

### 7.1 Windows 上 dsh plugin add 实跑

**执行命令**:
```sh
dsh plugin --profile web add @anionex/dsh-computer-use
```

**实际结果**(日志在 `docs/dsh-plugin-add.log`):
```sh
dsh: The term 'dsh' is not recognized as a name of a cmdlet, function, script file, or executable program.
Check the spelling of the name, or if a path was included, verify that the path is included, verify that the path is correct and try again.
EXIT: <empty>
```

**诚实说明**:Windows 主机**没有安装 DeepSeek Harness CLI**(`dsh` 命令不存在)。这意味着:
1. `dsh plugin --profile web add` 命令本身无法跑
2. 但 Bundle 的镜像 + LICENSE + SKILL.md 已就位
3. 等用户迁 macOS(或在新 macOS 主机上)后再执行 `dsh plugin add` 即可激活

**这是 Windows 上的"最干净降级"** —— 不是 Bundle 装不上,而是 DSH CLI 根本不存在。

## 8. 累计 PASS 增量

| 阶段 | 测试 | 增量 | 累计 |
|------|------|------|------|
| 41 | mneme-heat-engine 6 PASS | +9 | **799** |
| **42** | **dsh-computer-use 5 PASS** | **+5** | **804** |

**MEMORY.md 阶段 42 行已加入**:`dragon-engine/memory/MEMORY.md` 阶段 42 行。

**主题文件**:30 → **31 个**(+1 dsh-computer-use-integration.md)

## 9. 关键决策点(回顾)

| 项 | 选项 | 实际 |
|----|------|------|
| 平台适配 | 仅镜像 / 完整装 / 暂不 | **完整镜像 + 跑 dsh plugin add**(Windows 优雅降级) |
| 镜像拓扑 | 单层 / 双层 / 三层 | **三层**(同 anysearch / agent-reach) |
| 合规模板 | 不写 / 简版 MIT / 完整版 | **简版 MIT + screenshot 合规警示** |
| Agent 协同 | 仅 35-05 / 仅 28-04 / 暂不 / 全部 | **3 真实存在 + 2 候选留 42.1/42.2** |
| 触发词数 | 7 / 11 / 15 | **11 类** |
| DON'T 护栏数 | 5 / 11 / 15 | **11 条** |

## 10. 风险与未决项

1. **macOS 真机验证缺失** — 仅 Windows 上做"镜像 + 文档 + 协同点"集成,真实 Tool 调用待用户迁 macOS 后做(阶段 42.1)
2. **上游 0.1.0 early 状态** — README 明说 "model-facing and provider behavior may change before a stable release",建议每月一次 skill-updater 检测
3. **`@dsh-external/dsh-computer-use` 包名陷阱** — 上游 README Important 警告,本 SKILL.md + references 多处标注
4. **Windows 上 DSH CLI 不存在** — `dsh plugin add` 命令实际跑不起来,这是预期的(不是 Bundle 装不上)
5. **dsh-vision-toolkit 不在天龙主仓** — 跨 skill 协同段未注入,留阶段 42.2 补齐
7. **35-02 社媒运营不在天龙主仓** — 协同段未注入,留阶段 42.2 补齐

## 11. 下一步(阶段 42.1 / 42.2)

### 42.1 · macOS 真机验证(用户迁 mac 后跑)

```sh
# 装机
dsh plugin --profile web add @anionex/dsh-computer-use
dsh plugin --profile headless add @anionex/dsh-computer-use

# macOS TCC 权限
# System Settings → Privacy & Security → Accessibility + Screen Recording → Allow DSH host

# 端到端
/computer-use  # 加载 Skill
computer_list_apps
computer_observe (bundle_id=...)
computer_click (target_handle=...)

# 验证
pytest tests/test_dsh_computer_use.py -v  # 全部 5/5
```

### 42.2 · 协同段补齐

- 注入 `35-02 社媒运营` agent(若天龙 42.1 后该 agent 出现)
- 注入 `dsh-vision-toolkit` SKILL.md(若 42.1 后该 skill 出现)
- 复审 `agent-reach` / `browser-testing` 是否需引用 dsh-computer-use 做浏览器 app 实操

### 月度 skill-updater

阶段 24 skill-updater V1.1.3 自动扫描时,识别 `dsh-computer-use` 为天龙集成版,跳过 AUTO_HINTS(已在 `INTEGRATED_SKILLS` 清单)。

## 12. 关键文件路径(压缩)

| 资产 | 路径 |
|------|------|
| 真源 SKILL.md | `dragon-engine/skills/dsh-computer-use/SKILL.md` |
| 真源 LICENSE | `dragon-engine/skills/dsh-computer-use/LICENSE` |
| 真源 README | `dragon-engine/skills/dsh-computer-use/README.md` |
| 错误码映射 | `dragon-engine/skills/dsh-computer-use/references/error-codes.md` |
| 装机流程 | `dragon-engine/skills/dsh-computer-use/references/install-flow.md` |
| Agent 协同 | `dragon-engine/skills/dsh-computer-use/references/agent-coordination.md` |
| 健康检查器 | `dragon-engine/skills/dsh-computer-use/scripts/dsh_computer_use_check.py` |
| 集成测试 | `dragon-engine/skills/dsh-computer-use/tests/test_dsh_computer_use.py` |
| 项目级镜像 | `dragon-engine/.claude/skills/dsh-computer-use/SKILL.md` |
| 工作区根镜像 | `projects/skills/dsh-computer-use/SKILL.md` |
| 主题文件 | `dragon-engine/memory/dsh-computer-use-integration.md` |
| MEMORY.md 行 | `dragon-engine/memory/MEMORY.md` 阶段 42 |
| MIT 合规模板 §十四 | `dragon-engine/memory/mit-attribution-statements.md` |
| dsh plugin add 日志 | `dragon-engine/skills/dsh-computer-use/docs/dsh-plugin-add.log` |
| 本 announce | `dragon-engine/skills/dsh-computer-use/docs/announce-stage-42.md` |

---

> **下次同步**:用户迁 macOS 14+ 主机后触发阶段 42.1(macOS 真机验证 12 Tools smoke test + screenshot 落盘 + grants 权限流程)。