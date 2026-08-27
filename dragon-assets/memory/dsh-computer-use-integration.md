---
name: dsh-computer-use-integration
description: Anionex/dsh-computer-use 0.1.0 集成档案 — MIT · macOS 14+ native action layer · 12 Tools · 4 类 host-enforced 错误码 · 阶段 26
metadata:
  type: project
  node_type: memory
  originSessionId: dsh-computer-use-integration-20260823
  modified: 2026-08-23T22:30:00.000Z
heat: 0.7
last_ref_date: 2026-08-24
mneme_schema: v12.0
---


# dsh-computer-use 集成档案 V1.0(阶段 26)

> **TL;DR**:[Anionex/dsh-computer-use](https://github.com/Anionex/dsh-computer-use) 是 DeepSeek Harness 的 **原生 macOS 动作层**(0.1.0 · MIT ✅ · 由 [anionex](https://anionex.me/) 维护 · npm: `@anionex/dsh-computer-use`)。它给 DSH Agent 提供 **Accessibility 优先、目标进程隔离、不抢焦点、可观测可回滚** 的电脑控制能力。**当前主机是 Windows,功能不可用**(provider 仅 macOS);天龙集成的是**包装层 + 三层镜像 + Agent 协同点 + 合规模板**,等用户迁 macOS 即可启用。

---

## 一、实跑元数据(2026-08-23)

### 1.1 上游仓库 GitHub REST 实拉

| 字段 | 值 |
|------|----|
| **license.spdx_id** | **MIT** 🟢 |
| **default_branch** | main |
| **npm_package** | `@anionex/dsh-computer-use` ✅ |
| **deprecated_package** | `@dsh-external/dsh-computer-use` ❌ 从未发布到 npm |
| **stars** | 新仓库,Star 计数待后续追踪 |
| **lastest_release** | 0.1.0(早期版,model-facing API 可能变化) |
| **platform** | macOS 14+(arm64 + x86_64 universal binary) |

### 1.2 LICENSE verbatim 已实拉确认

```
MIT License
Copyright (c) 2026 anionex
... (标准 MIT 21 行)
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND...
---
Modified by dragon-engine / 2026-08-23
Source: https://github.com/Anionex/dsh-computer-use
```

已落盘:`C:\Users\li\.claude\projects\dragon-engine\skills\dsh-computer-use\LICENSE`

### 1.3 NOTICE 文件不存在(MIT 协议不需要)

`https://raw.githubusercontent.com/Anionex/dsh-computer-use/main/NOTICE` 返回 **404 Not Found** ✅ 符合预期(MIT 协议不强制 NOTICE,Apache-2.0 才强制)。

---

## 二、镜像拓扑(3 处一致,同 anysearch / agent-reach 风格)

| # | 路径 | 角色 | 状态 |
|---|------|------|------|
| 1 | `C:\Users\li\.claude\projects\dragon-engine\skills\dsh-computer-use\` | **真源**(SKILL.md + LICENSE + README + scripts + tests + references) | ✅ 已落盘 |
| 2 | `C:\Users\li\.claude\projects\dragon-engine\.claude\skills\dsh-computer-use\` | 项目级 Claude 配置镜像 | ✅ 已落盘 |
| 3 | `C:\Users\li\.claude\projects\skills\dsh-computer-use\` | 工作区根级镜像 | ✅ 已落盘 |

**不入全局**:`~/.claude/skills/dsh-computer-use/` 不存在(用户决策"靠项目级路径工作")。

### 2.1 真源目录结构

```
skills/dsh-computer-use/
├── SKILL.md                    # V1.0.0 · L0...L10 完整包装层
├── LICENSE                     # MIT verbatim + Modified by
├── README.md                   # 上游 README 简化版 + Modified by 标注
├── references/
│   ├── error-codes.md          # 4 类 host-enforced 错误码完整映射
│   ├── install-flow.md         # macOS 装机全流程
│   └── agent-coordination.md   # 5 类天龙 Agent 协同接入点
├── scripts/
│   └── dsh_computer_use_check.py  # 健康检查器 + 退出码契约 0/1/2/3
└── tests/
    └── test_dsh_computer_use.py   # 5 PASS 集成测试
```

---

## 三、12 个 Tool + 4 类 host-enforced 错误码

### 3.1 Tool 完整词汇表

| Tool | 用途 | 默认输入路径 |
|------|------|--------------|
| `computer_list_apps` | 列出有界用户态 app | — |
| `computer_observe` | 返回 fresh full/diff Accessibility 观测 + 可选截图 | Semantic |
| `computer_click` | 优先 AXPress · index/targetHandle + allowCoordinateFallback | Semantic → 目标进程坐标 |
| `computer_set_value` | 设/清空可编辑值(不用剪贴板)| Semantic |
| `computer_type_text` | Accessibility Unicode → 目标进程 keyboard fallback | Semantic → 键盘 |
| `computer_press_key` | 有限词汇一键到目标进程 + modifiers | 键盘 |
| `computer_scroll` | 目标进程 + window 内定向滚动 | 指针 |
| `computer_drag` | 观测内两点拖动 | 指针 |
| `computer_perform_action` | 执行 Accessibility action | Semantic |
| `computer_wait` | 轮询有界 text/role/title 条件 | 纯观测 |
| `computer_confirm` | 获取一次性 token 绑死敏感动作 | — |
| `computer_use_activate` | Bundle 启动时唯一直接暴露的 Tool | — |

**红线**:任何 Tool **不接受** AppleScript / JXA / shell / Swift / Objective-C / native selectors / 任意 Accessibility 常量 / 源代码。

### 3.2 4 类 host-enforced 错误码

| 错误码 | 触发 | 处置 |
|--------|------|------|
| `COMPUTER_UNSUPPORTED_PLATFORM` | Windows / Linux | DSH profile 正常启动 · Tools 不注册 · Web Settings 提示 |
| `COMPUTER_PERMISSION_REQUIRED` | app 不在 grants + policy 是 `never` | Settings 加 bundle id 或换 `ask` preset |
| `COMPUTER_TARGET_AMBIGUOUS` / `COMPUTER_TARGET_LOW_CONFIDENCE` | `targetHandle` 解析失败 | resolver **fail-closed** · 不猜 |
| `COMPUTER_TARGET_REBIND_REQUIRES_CONFIRMATION` | 高风险 rebind | one-use token 作废 · 重观测 + 重确认 |

**关键设计**:模型**不能**通过 Tool 参数覆盖这些 host policy。

---

## 四、合规边界(MIT 红线)

> 复用 [mit-attribution-statements](mit-attribution-statements.md) §一 的 3 条强制条款:

| 条款 | dsh-computer-use 应用 | 落地 |
|------|----------------------|------|
| **保留 ©** 版权声明 | 落 `skills/dsh-computer-use/LICENSE` 完整 verbatim | ✅ 已落盘 |
| **禁止暗示背书** | agent.md / SKILL.md 不得用 "dsh-computer-use 官方" / "官方授权" 字样,仅 "Powered by Anionex/dsh-computer-use" | ✅ 已落盘 |
| **MIT 允许闭源转售 / 修改** | 天龙可直接集成 + 包装 + 改写,但必须保留 © + LICENSE | ✅ 已落盘 |

**额外建议**(非强制,但符合 best practice):
- screenshot 录制合规警告:截图可能包含其他 app 可见数据,应被视为敏感
- macOS TCC 权限自助清单:Accessibility + Screen Recording + Input Monitoring

---

## 五、5 类 Agent 协同点(天龙注入)

| Agent | 注入位置 | 用途 |
|-------|---------|------|
| `28-04 内容策划师 V10.x` | depends / upstream 段 | 绕 WAF 看 app 真实形态(小红书 / 抖音 / 微信 app) |
| `35-02 社媒运营 V13.x` | Step 5 实操段 | macOS 端发图文实操 · 视频号封面裁剪 |
| `35-05 短视频导演 V10.x` | 镜头脚本实操段 | FCP / Premiere / CapCut Mac 真实剪辑 |
| `28-10 财经底座师 V1.x` | 数据采集段 | 雪球 / 同花顺 Mac 客户端 UI(已登录态) |
| `dsh-vision-toolkit` | 跨 skill 协同 | screenshot → OCR / 视觉理解 |

详细协同段:[`skills/dsh-computer-use/references/agent-coordination.md`](../skills/dsh-computer-use/references/agent-coordination.md)

---

## 六、5 类平台限制(Windows 用户必读)

| # | 限制 | 天龙对策 |
|---|------|---------|
| 1 | **仅 macOS 14+**(arm64 + x86_64) | Windows / Linux → 优雅降级 + 文档化迁移待办 |
| 2 | 当前 provider 是 **macOS-only**(Windows UI Automation / Linux providers 未实现) | 等上游迭代,或自行 fork |
| 3 | SkyLight SPI 失败 → 指针 fallback fail-closed | 接受 fail-closed,改用 Semantic |
| 4 | 自定义画布 / 游戏 / 加固输入面可能拒绝目标进程输入 | 永远优先 Semantic Accessibility |
| 5 | `focusPolicy: activate` / `keyboardPolicy: activate` 有意 disruptive | 默认 `preserve` / `activate` |

**当前主机(2026-08-23)**:
- 主机: **Windows**
- Provider: ❌ 未注册(平台不支持)
- Tools: ❌ 未注册
- Skill 状态: ✅ 已加载(无 Tools 可调用)
- Web Settings: ⚠️ 报告 `COMPUTER_UNSUPPORTED_PLATFORM`
- 迁移待办: ⏳ 主机迁 macOS 14+ 后跑 `dsh plugin --profile web add @anionex/dsh-computer-use`

---

## 七、累计 PASS 增量

| 阶段 | 测试 | 增量 | 累计 |
|------|------|------|------|
| 25.2 | TradingAgents-astock 4 PASS | +4 | **618** |
| **26** | **dsh-computer-use 5 PASS** | **+5** | **623** |

### 7.1 5 个 PASS 用例

1. **test_01_mirror_sync**:三层镜像存在 + frontmatter 完整(name/version/license/platform)
2. **test_02_license_verbatim**:LICENSE 是上游 MIT verbatim + Modified by dragon-engine footer
3. **test_03_skill_sections**:SKILL.md 包含 L0...L10 11 个段 + 11 类触发词 + 11 条 DON'T 护栏
4. **test_04_platform_degradation**:Windows / Linux 上报告平台降级(macOS 通过)
5. **test_05_npm_package_name**:包名是 `@anionex/dsh-computer-use`;`@dsh-external/...` 不能作 install 命令

---

## 八、风险与未决项

1. **macOS 真机验证缺失** —— 阶段 26 仅在 Windows 上做"镜像 + 文档 + 协同点"集成,真实 Tool 调用待用户迁 macOS 后做(预计阶段 26.1)
2. **上游 0.1.0 early 状态** —— README 明确说 "model-facing and provider behavior may change before a stable release",建议每月一次 skill-updater 检测
3. **AppleScript / JXA / shell 红线** —— 任何 Tool 都不接;若用户后续要求"用 AppleScript 触发 macOS 操作",需明确告知"出 Computer Use 范围"
4. **`@dsh-external/dsh-computer-use` 包名陷阱** —— 上游 README 用 Important 警告,本 SKILL.md 也在 frontmatter 与 references/error-codes.md / install-flow.md 多处标注

---

## 九、来源链接

- 上游仓库: https://github.com/Anionex/dsh-computer-use
- 上游 LICENSE: https://raw.githubusercontent.com/Anionex/dsh-computer-use/main/LICENSE (MIT verbatim, 2026-08-23 实拉)
- 上游 README: https://raw.githubusercontent.com/Anionex/dsh-computer-use/main/README.md
- npm: `@anionex/dsh-computer-use`
- 作者主页: https://anionex.me/
- 作者 X: https://x.com/anion_ex

---

## 十、阶段 26 实施总结

> **总目标**:把 Anionex/dsh-computer-use 0.1.0 集成进天龙引擎,作为**原生 macOS 动作层**,支撑 5 个下游 Agent(app 实操场景)。当前 Windows 上做镜像 + 文档 + 协同点埋设,累计 PASS **618 → 623**。

### 实际交付物

| 项 | 路径 | 状态 |
|----|------|------|
| 三层镜像(SKILL.md) | `skills/dsh-computer-use/SKILL.md` + `.claude/skills/dsh-computer-use/SKILL.md` + `skills/dsh-computer-use/SKILL.md` | ✅ |
| LICENSE verbatim | `skills/dsh-computer-use/LICENSE` | ✅ |
| 上游 README 简化版 | `skills/dsh-computer-use/README.md` | ✅ |
| 3 个 references | `references/{error-codes,install-flow,agent-coordination}.md` | ✅ |
| 健康检查器 | `scripts/dsh_computer_use_check.py` | ✅ |
| 集成测试 | `tests/test_dsh_computer_use.py` | ✅ |
| 主题文件 | `memory/dsh-computer-use-integration.md` (本文) | ✅ |
| MIT 合规模板 | `memory/mit-attribution-statements.md` | ✅ |
| 5 个 Agent 注入点 | `agents/{28-04,35-02,35-05,28-10}*.md` + `dsh-vision-toolkit` | ✅ |
| MEMORY.md 行 | `memory/MEMORY.md` 阶段 26 行 + 累计 623 | ✅ |

### 关键决策点

| 项 | 选项 | 实际选择 |
|----|------|---------|
| 平台适配 | 仅镜像 / 完整装 / 暂不 | **完整镜像 + 跑 dsh plugin add**(Windows 优雅降级) |
| 镜像拓扑 | 单层 / 双层 / 三层 | **三层**(同 anysearch / agent-reach) |
| 合规模板 | 不写 / 简版 MIT / 完整版 | **简版 MIT + screenshot 合规警示** |
| Agent 协同 | 仅 35-05 / 仅 28-04 / 暂不 / 全部 | **全部注入** |
| 触发词数 | 7 / 11 / 15 | **11 类**(覆盖 12 Tools + 1 显式加载) |
| DON'T 护栏数 | 5 / 11 / 15 | **11 条**(对齐 11 类触发词) |

### 验收门槛(本阶段已 PASS)

- [x] 累计 PASS **623**
- [x] 三层镜像 + LICENSE verbatim + 3 references + 2 scripts/tests
- [x] MIT 红线检查表 3/3 PASS
- [x] 5 个 Agent 接入点埋设
- [x] MEMORY.md / dsh-computer-use-integration / mit-attribution-statements 三件套
- [x] 主题文件 +4 = **31 个**(原 30)
- [x] GitHub ⭐ 计数留待 26.1 端到端后追踪

---

> **下次同步点**:用户迁 macOS 14+ 主机后跑一次端到端,触发阶段 26.1(macOS 真机验证 · 12 Tools smoke test + screenshot 落盘 + grants 权限流程)。