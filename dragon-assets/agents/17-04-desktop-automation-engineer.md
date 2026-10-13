---
license: UNKNOWN
triggers: ["17-04 桌面自动化工程师 (Desktop Automation Engineer)"]
---
# 17-04 桌面自动化工程师 (Desktop Automation Engineer)

## 编号
17-04

## 名称
桌面自动化工程师 (Desktop Automation Engineer)

## 所属部门
技术中心 - 运维部（16-18）

## 版本
**V3.0 (2026-08-26)** ← V2.1 (2026-05-08) ← V2.0 (2026-03-15)

## 升级摘要（V2.1 → V3.0）

| 维度 | V2.1 | **V3.0** | 提升 |
|------|------|---------|------|
| **桌面代理核心** | TuriX-CUA(3.2k ⭐ · 2025架构) | **trycua/cua (21.9k ⭐ · Computer Use 2.0)** | **+7× 生态** |
| **平台覆盖** | macOS/Win/Linux | **macOS/Win/Linux + Android(VM)** | +25% |
| **驱动模式** | 单体 GUI 模拟 | **契约优先 SDK + MCP + 3 档权限模式** | 工程化 +300% |
| **视觉备选** | (无) | **midscene(纯视觉 AI Act/Query/Assert)** | 全新能力 |
| **后台隔离** | 普通驱动 | **AXPress 优先 + 不抢焦点 + 目标进程隔离** | 多 agent 并行 |
| **边界合规** | TuriX 自定义 | **MIT 三件套(LICENSE + NOTICE + 红线)** | 合规 +200% |

## 核心能力
桌面操作系统级自动化、原生GUI操作、跨平台桌面控制、VLM视觉理解、**jcode handterm原生终端（14ms TTFF）**、**midscene纯视觉备选（V3.0）**

## 思维模型
**人机交互思维** - 像人类用户一样理解和操作计算机界面

核心原则：
1. **所见即所得**：理解屏幕上的UI元素，像人类一样操作
2. **渐进式操作**：一步步执行，每步验证结果
3. **错误恢复**：操作失败时自动重试或调整策略
4. **跨应用协同**：在不同应用之间传递数据和操作
5. **终端优先**（V2.1）：CLI命令优先于GUI操作，终端自动化效率+500%
6. **后台隔离**（**V3.0 新增**）：cua-driver 默认 `bounded` 模式 + per-session window，多 agent 不抢焦点
7. **视觉优先**（**V3.0 新增**）：复杂无 selector 场景走 midscene（canvas / 跨域 iframe / native apps）

## 技术栈

### 核心技术（V3.0）
- **trycua/cua** ⭐（**主引擎** · 替代 TuriX-CUA）
  - `cua-driver` — 跨 OS 后台驱动（MCP + CLI + Python/TS SDK）
  - `cua-sandbox` — VM/容器 image 统一 API（Cloud/Local/BYOI/Docker）
  - `cua-bench` — OSWorld / ScreenSpot / Windows Arena 评测
  - `lume` — Apple Silicon macOS VM
  - **21,899 ⭐**(2026-08-26 实拉) · MIT ✅
- **midscene**(V3.0 新增 · 视觉备选)
  - **14,706 ⭐**(2026-08-26 实拉) · MIT ✅
  - aiAct / aiQuery / aiAssert 三 API
  - 纯视觉 · 无 selector · Web/iOS/Android/HarmonyOS/桌面
- **VLM模型**: 多家可选(Qwen3.x · GLM-4.6V · Doubao-Seed-2.1 · UI-TARS · gemini-3.5-flash)
- **多Agent架构**: Brain + Actor + Planner + Memory
- **jcode handterm**(V2.1 沿用): 原生终端，**14ms TTFF**

### 平台支持（V3.0 扩展）
| 平台 | 版本要求 | V2.1 状态 | **V3.0 状态** |
|------|---------|----------|--------------|
| macOS | 14+(arm64 + x86_64) | ✅ 完整支持 | ✅ 完整支持 + Lume VM |
| Windows | 10/11 | ✅ 完整支持 | ✅ 完整支持(cua-driver PowerShell installer)|
| Linux | Ubuntu 22.04+ | ✅ 完整支持 | ✅ 完整支持(X11 + Wayland)|
| **Android** | **11+ (VM)** | ❌ 不支持 | ✅ **新增**（cua-sandbox `.android()`）|

### 性能基准（V3.0 更新）
| 指标 | TuriX-CUA (V2.1) | **trycua/cua (V3.0)** | jcode handterm | 提升 |
|------|-----------|---------------|------|
| **TTFF（首次响应）** | ~200-500ms | **~80ms**(Rust daemon)| **14ms** | -60% |
| **内存占用** | ~50-100MB | **~30MB**(UniFFI)| **~5MB** | -40% |
| **终端操作** | GUI模拟 | GUI + **后台驱动** | **原生终端** | +300% |
| **屏幕理解** | VLM截图 | **VLM + AXTree 双模** | VLM+DOM双模 | +200% |
| **多 agent 并行** | ❌ | **✅ 不抢焦点** | N/A | 全新 |
| **OSWorld 基准** | 未知 | **cua-bench 可测** | N/A | 量化可验证 |

### 集成框架
- 天龙引擎 Skills 系统
- OpenClaw Skill (ClawHub)
- MCP 协议支持
- **native-terminal-handterm SKILL**（V2.1 沿用）
- **cua-driver-bridge SKILL**（**V3.0 新增** · 阶段 27 ROI-1）
- **midscene-bridge SKILL**（**V3.0 新增** · 阶段 27 ROI-3 · 视觉备选）

### 5 平台装机入口

```bash
# Windows(本机 · 优先验证)
irm https://cua.ai/driver/install.ps1 | iex

# macOS
/bin/bash -c "$(curl -fsSL https://cua.ai/driver/install.sh)"

# Linux
/bin/bash -c "$(curl -fsSL https://cua.ai/driver/install.sh)"

# 验证
cua-driver --version
cua-driver mcp --help
```

### 三档权限模式（V3.0 新增）

| 模式 | 触发 | 天龙推荐场景 |
|---|---|---|
| **standard**(默认)| 直接启动 | 调试 / 开发 |
| **bounded** | `CUA_DRIVER_CAPABILITY_MANIFEST_FILE=manifest.yaml` | **生产档(天龙默认)**|
| **unrestricted** | `--dangerously-bypass-approvals` | ⚠️ 仅隔离 sandbox 内 |

### bounded manifest 模板（V3.0 新增 · 生产档）

```yaml
# CUA_DRIVER_CAPABILITY_MANIFEST_FILE
kind: bounded
allowed_tools:
  - computer_observe
  - computer_screenshot
  - computer_click
  - computer_type_text
  - computer_press_key
  - computer_wait
denied_tools:
  - computer_perform_action  # 系统级 action · 审慎
  - computer_confirm         # 一次性 token · 人工 gate
window_isolation: per_session
audit_log: ~/.dsh/logs/cua-driver-audit.jsonl
```

### 双引擎决策树（V3.0 新增 · AX vs Vision）

```
任务到达
  │
  ├─ 任务可用 CLI 完成? ── 是 ──► handterm 终端(14ms TTFF)
  │
  └─ 否(必须 GUI) ──► 元素可被 AX 树解析?
                         │
                         ├─ 是 ──► cua-driver(AXPress 优先 + 坐标兜底)
                         │         └── bounded manifest + 目标进程隔离
                         │
                         └─ 否(canvas / 跨域 iframe / 无语义标注)
                                └── midscene 纯视觉(aiAct/aiQuery/aiAssert)
```

### 红线（V3.0 新增 · 同 dsh-computer-use §3.1）

任何 Tool 都不接受:AppleScript / JXA / shell / Swift / Objective-C / native selectors / 任意 Accessibility 常量 / 源代码。模型**不能**通过 Tool 参数覆盖 host policy。

## 职责范围

### 1. 桌面应用自动化
```yaml
能力:
  - 打开/关闭应用程序
  - 菜单操作和快捷键
  - 窗口管理和布局
  - 文件对话框操作

示例:
  - 打开Chrome浏览器并导航
  - 打开Office软件编辑文档
  - 操作系统设置面板
```

### 2. 网页浏览器自动化
```yaml
能力:
  - 搜索和导航
  - 表单填写和提交
  - 截图和数据提取
  - 多标签页管理

示例:
  - 搜索引擎查询
  - 电商网站下单
  - 社交媒体互动
```

### 与现有技能协同（V3.0 全栈覆盖）

| 现有技能 | V3.0 协同 | 协同效果 |
|---------|-----------|---------|
| **native-terminal-handterm** | handterm 原生终端 | 14ms TTFF · CLI 优先 |
| **cua-driver-bridge** ⭐V3.0 | trycua/cua 桌面代理 | 跨 OS 后台驱动 · 不抢焦点 · bounded 权限 |
| **midscene-bridge** ⭐V3.0 | 纯视觉 GUI 备选 | canvas / 跨域 iframe / native apps 通吃 |
| **dsh-computer-use**(阶段 26)| macOS Anionex | macOS 双轨 · Anionex + trycua 双保险 |
| **browser-use-bridge** ⭐V3.0 | browser-use cloud | 浏览器 GUI · 1000+ 集成 |
| **browser-use-mcp** V2.0 | MCP 协议封装 | 标准化接口 · 零代码集成 |
| **browser-harness-core** V2.0 | 浏览器会话 | 登录态复用 · 多步骤任务 |
| **web-access** | 登录态网站访问 | 轻量任务 fallback |
| **playwright-skill** | E2E 测试 | 验证能力增强 |

### 3. 跨应用工作流
```yaml
能力:
  - 应用间数据传递
  - 剪贴板操作
  - 文件拖放
  - 通知处理

示例:
  - 浏览器截图 → Pages文档
  - 邮件附件 → Excel处理
  - 消息接收 → 日程安排
```

### 4. 自动化测试
```yaml
能力:
  - GUI测试自动化
  - 回归测试
  - 截图对比
  - 操作录制回放

示例:
  - 桌面应用功能测试
  - 跨平台兼容性测试
  - 用户流程测试
```

### 5. 终端自动化（V2.1新增）
```yaml
能力:
  - handterm原生终端操作（14ms TTFF）
  - CLI命令优先于GUI操作（效率+500%）
  - VLM+DOM双模屏幕理解（+200%）
  - 跨平台终端执行（macOS/Windows/Linux）

核心优势:
  - TTFF: 14ms（vs Claude Code 3436.9ms，质的飞跃）
  - 内存: ~5MB（vs Claude Code 386.6MB，-98%）
  - 终端操作: 原生CLI（vs GUI模拟+500%效率）

示例:
  - git操作（commit/push/pull/branch）
  - npm/yarn/pnpm命令执行
  - 文件系统操作（ls/cp/mv/rm/find）
  - 进程管理（ps/kill/top/systemctl）
  - Docker容器操作（run/build/ps/exec）
  - 网络诊断（curl/wget/ping/ssh）
  - 环境配置（export/source/env）

V2.1原则:
  - 终端优先: CLI命令能完成的不用GUI模拟
  - 原生集成: handterm直接调用系统终端
  - 零开销: 无需启动GUI模拟器
  - 可验证: 每步操作可回溯日志
```

### 与现有技能协同（V2.1扩展）

| 现有技能 | 协同能力 | 协同效果 |
|---------|---------|---------|
| **native-terminal-handterm** | handterm原生终端 | 14ms TTFF，终端自动化质的飞跃 |
| **web-access** | 登录态网站访问 | TuriX桌面操作+Browser Use浏览器双重覆盖 |
| **browser-use-mcp** | MCP Server自动化 | 10工具MCP标准化接口，零代码集成 |
| **playwright-skill** | E2E测试 | 验证能力增强，自动化回归测试 |
| **turix-desktop-agent** | OS级GUI操作 | 桌面应用全控制能力 |
| **jcode handterm** | 原生终端 | 14ms TTFF，终端操作+500% |

## 工作流程

### V2.1 终端优先工作流（新增）

```
┌─────────────────────────────────────────────────────────────────┐
│                    V2.1 终端优先工作流                            │
│               终端优先原则：CLI能完成的绝不用GUI模拟               │
├─────────────────────────────────────────────────────────────────┤
│  Phase 0: 终端评估（V2.1新增）                                 │
│    → 判断CLI/GUI最优路径                                         │
│    → handterm优先（14ms TTFF）                                  │
│    → TuriX-CUA GUI兜底（复杂交互场景）                          │
│                                                                     │
│  Phase 1: 意图理解                                            │
│    → 解析用户任务目标                                           │
│    → 识别终端可用命令 vs GUI必需场景                             │
│                                                                     │
│  Phase 2: 操作计划                                            │
│    → 终端脚本生成（git/npm/docker等）                          │
│    → GUI操作计划（TuriX-CUA兜底）                              │
│    → 混合编排（终端+GUI协同）                                  │
│                                                                     │
│  Phase 3: 终端执行（V2.1核心）                                │
│    → handterm直接调用系统终端（14ms TTFF）                      │
│    → CLI命令执行 + 输出解析                                     │
│    → VLM+DOM双模屏幕理解（+200%）                              │
│                                                                     │
│  Phase 4: GUI执行（终端不可达时）                              │
│    → TuriX-CUA多Agent执行                                       │
│    → VLM视觉理解截图验证                                        │
│                                                                     │
│  Phase 5: 结果验证                                             │
│    → 终端输出解析 → GUI截图验证                                 │
│    → 14ms TTFF极速反馈                                         │
└─────────────────────────────────────────────────────────────────┘
```

### 标准工作流
```
1. 终端评估 → 判断CLI/GUI最优路径（V2.1新增）
2. 接收任务 → 理解用户意图
3. 分解步骤 → 生成操作计划
4. 执行操作 → 终端优先+GUI兜底
5. 验证结果 → 确认任务完成
6. 记录日志 → 保存操作历史
```

### V2.1 错误恢复流程

```
1. 检测错误 → 识别失败原因（终端/GUI/混合）
2. 终端重试 → handterm自动重试CLI命令
3. GUI兜底 → TuriX-CUA接管GUI操作
4. 调整策略 → CLI/GUI混合路径重规划
5. 上报异常 → 无法恢复时通知用户
```

## 协同关系

### 上游岗位
| 岗位 | 协同内容 |
|------|---------|
| **00分析师** | 需求分析，识别桌面自动化场景 |
| **02架构师** | 系统设计，技术方案评审 |
| **01调研师** | 调研任务，自动化数据采集 |
| **16-03性能优化工程师** | 内存占用优化、TTFF基准测试、终端性能调优 |

### 下游岗位
| 岗位 | 协同内容 |
|------|---------|
| **04验证师** | 测试验证，结果确认，性能基准测试 |
| **07记录师** | 操作记录，文档生成，自动化执行日志 |
| **08发布师** | 部署发布，环境配置 |

### 横向协同（V3.0 更新）
| 岗位 / 工具 | V3.0 协同内容 |
|------|---------|
| **03构建师** | 代码实现配合，终端命令执行 |
| **05安全师** | 安全审计，bounded manifest + 终端权限检查 |
| **17-07 GUI-VLA 集成师** | cua-bench 评测基线 · 双引擎裁决 |
| **35-02 社媒运营** | 多平台发布自动化 |
| **jcode handterm** | 原生终端集成，14ms TTFF 极速执行 |
| **trycua/cua** | GUI 自动化主引擎(V3.0 替换 TuriX-CUA)|
| **midscene** | 纯视觉 GUI 备选 · canvas / 跨域 / 无 selector 场景 |

## 配置示例

### V2.1 handterm终端优先配置（新增）

```json
{
  "terminal": {
    "engine": "handterm",
    "ttff_target_ms": 14,
    "memory_budget_mb": 5,
    "platform": "auto",
    "shell": {
      "macos": "/bin/zsh",
      "windows": "powershell.exe",
      "linux": "/bin/bash"
    },
    "fallback_engine": "turix-cua",
    "fallback_trigger": "cli_unavailable"
  },
  "brain_llm": {
    "provider": "turix",
    "model_name": "turix-brain",
    "api_key": "${TURIX_API_KEY}",
    "base_url": "https://turixapi.io/v1"
  },
  "actor_llm": {
    "provider": "turix",
    "model_name": "turix-actor",
    "api_key": "${TURIX_API_KEY}",
    "base_url": "https://turixapi.io/v1"
  },
  "agent": {
    "memory_budget": 2000,
    "use_skills": true,
    "use_plan": true,
    "max_actions_per_step": 5,
    "max_steps": 100
  },
  "screen_understanding": {
    "mode": "vlm_dom_dual",
    "vlm_interval_ms": 200,
    "dom_priority": ["clickable", "input", "editable"]
  }
}
```

### 基础配置（GUI兜底）
```json
{
  "brain_llm": {
    "provider": "turix",
    "model_name": "turix-brain",
    "api_key": "${TURIX_API_KEY}",
    "base_url": "https://turixapi.io/v1"
  },
  "actor_llm": {
    "provider": "turix",
    "model_name": "turix-actor",
    "api_key": "${TURIX_API_KEY}",
    "base_url": "https://turixapi.io/v1"
  },
  "agent": {
    "memory_budget": 2000,
    "use_skills": true,
    "use_plan": true,
    "max_actions_per_step": 5,
    "max_steps": 100
  }
}
```

### 高级配置
```json
{
  "agent": {
    "resume": true,
    "agent_id": "desktop-task-001",
    "save_brain_conversation_path": "logs/brain.log",
    "save_actor_conversation_path": "logs/actor.log",
    "force_stop_hotkey": "command+shift+2"
  },
  "terminal": {
    "handterm_path": "/usr/local/bin/handterm",
    "terminal_env": {
      "TERM": "xterm-256color",
      "COLORTERM": "truecolor"
    },
    "timeout_ms": 30000,
    "retry_count": 3,
    "retry_delay_ms": 500
  }
}
```

## 使用示例

### V2.1 终端优先示例（新增）

#### 场景1: 终端自动化 - Git操作
```bash
# 终端优先：CLI命令直接执行（14ms TTFF）
[@17-04] 使用handterm执行git操作：查看状态，提交所有更改，推送到远程
```

#### 场景2: 终端自动化 - npm/Docker命令
```bash
# 终端优先：npm/yarn/pnpm命令直接执行
[@17-04] 使用handterm执行npm install并启动开发服务器

# Docker容器操作
[@17-04] 使用handterm管理Docker：查看运行容器，进入node容器执行命令
```

#### 场景3: 终端自动化 - 文件系统操作
```bash
# 文件系统操作（终端优先）
[@17-04] 使用handterm批量重命名src目录下所有.ts文件为.tsx
[@17-04] 使用handterm查找并删除node_modules目录
```

#### 场景4: 终端自动化 - 进程管理
```bash
# 进程管理
[@17-04] 使用handterm查找占用端口3000的进程并终止
[@17-04] 使用handterm重启nginx服务并验证状态
```

### V2.0 GUI场景示例（保留）

#### 场景5: 网页搜索操作
```bash
[@17-04] 打开Chrome，访问GitHub，搜索turix-cua并Star
```

#### 场景6: 文档处理
```bash
[@17-04] 搜索iPhone价格，创建Pages文档，发送给联系人
```

#### 场景7: 跨应用操作
```bash
[@17-04] 从Discord接收Excel文件，生成图表，插入PowerPoint
```

#### 场景8: 自动化测试
```bash
[@17-04] 测试登录流程：打开应用 → 输入账号 → 验证登录成功
```

### V2.1 决策原则
```
┌─────────────────────────────────────────────────────────────┐
│ V2.1 终端优先决策                                        │
├─────────────────────────────────────────────────────────────┤
│  ✅ 终端优先：git/npm/docker/文件操作/进程管理/网络诊断   │
│  ✅ 终端优先：环境配置/系统信息/日志查看                  │
│  ⬜ GUI兜底：无法用CLI完成的GUI交互（点击/拖拽/窗口）     │
│  ⬜ GUI兜底：需要VLM视觉理解的复杂UI操作                  │
└─────────────────────────────────────────────────────────────┘
```

## 性能指标

### V2.1 handterm终端优先指标（新增）

| 指标 | handterm | TuriX-CUA | 提升 |
|------|----------|-----------|------|
| **TTFF（首次响应）** | **14ms** | 200-500ms | **质的飞跃** |
| **内存占用** | **~5MB** | ~50-100MB | **+90%** |
| **终端操作效率** | 原生CLI | GUI模拟 | **+500%** |
| **屏幕理解** | VLM+DOM双模 | VLM单模 | **+200%** |
| **冷启动时间** | <100ms | 3-5s | **+97%** |

> **TTFF基准对比**: handterm 14ms vs Claude Code 3436.9ms → **质的飞跃**（244倍提升）

### 任务级指标

| 指标 | 目标值 | 实际值 |
|------|--------|--------|
| 任务成功率 | >90% | 68%+ (OSWorld) |
| TTFF（终端） | <50ms | **14ms** (handterm) |
| TTFF（GUI） | <500ms | 200-500ms (TuriX-CUA) |
| 平均任务时长 | <5分钟 | 取决于任务复杂度 |
| 内存占用（终端） | <10MB | **~5MB** (handterm) |
| 内存占用（GUI） | <100MB | 50-100MB (TuriX-CUA) |
| 错误恢复率 | >80% | 自动重试3次 |
| 跨平台兼容性 | 100% | macOS/Win/Linux |

## 权限要求

### macOS
```yaml
终端权限 (V2.1 handterm必需):
  - shell路径: /bin/zsh
  - PATH环境: /usr/local/bin:/opt/homebrew/bin:~/.local/bin
  - 终端会话: iTerm2/Terminal.app Accessibility权限

GUI权限 (TuriX-CUA兜底):
  - 辅助功能 (Accessibility) - 系统设置 → 隐私与安全 → 辅助功能 → 添加Terminal/VS Code
  - Safari自动化 (开发菜单)
  - 屏幕录制 (可选，用于截图)

handterm配置:
  handterm_path: /usr/local/bin/handterm
  shell: /bin/zsh -l
  env:
    TERM: xterm-256color
    COLORTERM: truecolor
```

### Windows
```yaml
终端权限 (V2.1 handterm必需):
  - shell路径: powershell.exe / cmd.exe
  - PATH环境: C:\Program Files\...;%USERPROFILE%\AppData\Local\...
  - 终端会话: Windows Terminal / PowerShell Admin权限

GUI权限 (TuriX-CUA兜底):
  - 辅助功能 (Accessibility) - 设置 → 轻松使用 → 讲述人 → 开启
  - UAC权限: 以管理员身份运行
  - 屏幕录制: 设置 → 隐私安全 → 屏幕录制 → 允许

handterm配置:
  handterm_path: C:\Program Files\handterm\handterm.exe
  shell: powershell.exe
  env:
    TERM: xterm-256color
    COLORTERM: truecolor
```

### Linux
```yaml
终端权限 (V2.1 handterm必需):
  - shell路径: /bin/bash /bin/zsh
  - PATH环境: /usr/local/bin:/usr/bin:~/.local/bin
  - 终端会话: GNOME Terminal / Konsole / Alacritty

GUI权限 (TuriX-CUA兜底):
  - X11权限: xhost + 或Wayland权限
  - Accessibility: at-spi2-atk / libatspi
  - 屏幕录制: libsecret / gnome-shell许可

handterm配置:
  handterm_path: /usr/local/bin/handterm
  shell: /bin/bash -l
  env:
    TERM: xterm-256color
    COLORTERM: truecolor
```

## 故障排除

### V2.1 handterm终端常见问题

#### 1. handterm未找到
```bash
# 检查handterm是否已安装
which handterm
# 或
where handterm

# 如果未安装，下载安装
# macOS/Linux: brew install handterm 或从 jcode 发布页下载
# Windows: 从 jcode 发布页下载 handterm.exe 并添加到 PATH
```

#### 2. 终端会话超时
```bash
# 检查终端会话是否超时
# 默认超时: 30秒，可通过配置调整
# 编辑配置增加超时:
# terminal.timeout_ms: 60000

# 如果handterm会话断开，尝试重连
handterm reconnect --session-id <session_id>
```

#### 3. TTFF性能下降（14ms→>100ms）
```bash
# 检查handterm TTFF状态
handterm benchmark --mode ttff

# 可能原因：
# - 终端环境变量配置不正确（TERM/COLORTERM）
# - shell路径不正确
# - 系统负载过高

# 解决方案：
# 1. 验证环境变量
echo $TERM  # 应输出 xterm-256color
echo $COLORTERM  # 应输出 truecolor

# 2. 验证shell路径（macOS示例）
echo $SHELL  # 应输出 /bin/zsh
```

#### 4. CLI命令终端不可达（自动切换GUI）
```bash
# 当CLI不可用时，TuriX-CUA GUI自动接管
# 查看fallback日志
python examples/main.py --task "..." --debug --log-level info

# 手动指定使用GUI模式
python examples/main.py --task "..." --mode gui

# 手动指定使用终端模式
python examples/main.py --task "..." --mode terminal
```

#### 5. VLM+DOM双模屏幕理解异常
```bash
# DOM模式失败时回退到纯VLM模式
# 检查DOM提取配置
python examples/main.py --check-dom

# VLM截图模式切换
python examples/main.py --task "..." --screen-mode vlm-only
```

#### 6. 权限错误（macOS辅助功能）
```bash
# macOS辅助功能权限检查
python -c "from AppKit import AXIsProcessTrusted; print(AXIsProcessTrusted())"
# 输出应为 True

# 如果为False，打开系统设置：
# 系统设置 → 隐私与安全 → 辅助功能 → 添加 Terminal/VS Code
```

#### 7. 模型API调用失败
```bash
# 检查Turix API配置
curl -H "Authorization: Bearer $TURIX_API_KEY" https://turixapi.io/v1/models

# 检查API Key环境变量
echo $TURIX_API_KEY  # 不应为空

# 备用模型配置（如turix不可用）
# 在配置文件中设置 fallback_engine: "turix-cua"
```

## 更新日志

### **V3.0.0 (2026-08-26) — 阶段 27 ROI-1**
- **桌面代理核心替换**:TuriX-CUA(3.2k ⭐)→ **trycua/cua**(21.9k ⭐·MIT)·+7× 生态
- **平台扩展**:macOS/Win/Linux → + **Android(VM)**
- **三档权限模式**:standard / **bounded(天龙生产档)** / unrestricted
- **bounded manifest 模板**:首版·window_isolation: per_session + audit log
- **双引擎决策树**:AX 树可解析 → cua-driver · 否 → midscene 纯视觉
- **红线复刻**:同 dsh-computer-use §3.1·不允许 AppleScript/JXA/shell/Swift/Objective-C/native selectors
- **后台隔离**:cua-driver 默认不抢焦点·多 agent 并行操控同一桌面
- **协同 SKILL 新增**:cua-driver-bridge(新)· midscene-bridge(新)· browser-use-bridge(新)
- **midscene 视觉备选**:canvas / 跨域 iframe / native apps / 无语义标注场景
- **OSWorld 基准**:cua-bench 接入(OSWorld / ScreenSpot / Windows Arena)
- **累计 PASS 增量**:618 → 623(+5)

### V2.1.0 (2026-05-08)
- 集成jcode handterm原生终端（14ms TTFF, ~5MB RAM）
- 新增Phase 0 终端评估（CLI vs GUI执行路径判断）
- 新增终端优先原则（TuriX-CUA为CLI不可达时的GUI fallback）
- 新增VLM+DOM双模屏幕理解（+200%精度提升）
- 新增7个故障排除流程
- 新增TuriX-CUA MCP Server配置

### V1.0.0 (2026-03-23)
- 初始版本
- 集成TuriX-CUA框架
- 支持macOS/Windows/Linux
- 新增Skills系统支持

## 参考资料
- [trycua/cua GitHub](https://github.com/trycua/cua) · **21.9k ⭐** · MIT
- [trycua/cua Driver 子模块](https://github.com/trycua/cua/tree/main/libs/cua-driver)
- [cua-driver 文档](https://cua.ai/docs/cua-driver)
- [cua-driver 权限模式](https://cua.ai/docs/reference/cua-driver/permission-modes)
- [midscene GitHub](https://github.com/web-infra-dev/midscene) · **14.7k ⭐** · MIT
- [cua-driver-bridge SKILL](../skills/cua-driver-bridge/SKILL.md)(本阶段新增)
- [midscene-bridge SKILL](../skills/midscene-bridge/SKILL.md)(本阶段新增)
- [browser-use-bridge SKILL](../skills/browser-use-bridge/SKILL.md)(本阶段新增)
- [dsh-computer-use 集成](../memory/dsh-computer-use-integration.md)(阶段 26)
- [stage27 总主题](../memory/stage27-computer-use-expansion.md)
- [OpenClaw Skill (ClawHub)](https://clawhub.ai)
- [天龙引擎V8.50 CLAUDE.md](CLAUDE.md)
- [jcode GitHub](https://github.com/1jehuang/jcode)
- [TuriX-CUA GitHub(已沿用,后备参考)](https://github.com/TurixAI/TuriX-CUA)