# Context Doctor Integration (天龙引擎集成包装层)

> **上游**：[Zhenyu98/dsh-context-doctor](https://github.com/Zhenyu98/dsh-context-doctor) · **v0.6.1** · **19 ⭐** · **BSD-3-Clause** ✅ · TypeScript + Node.js ≥ 22.19
> **作者**：dsh-external（同 DSH 插件注册组织，DSH 官方 bundle 插件路径）
> **集成阶段**：天龙引擎 阶段 26（2026-08-23）
> **核心价值**：DSH 上下文注入审计插件 —— 让模型/用户**看清每个请求背着多少上下文**，自动检测 AGENTS.md 重复段落、catalog 冗余 skill、rank shadow 冲突、MCP 工具面膨胀

---

## 一、本目录角色

| 文件 | 角色 |
|------|------|
| `README.md`（本文件）| 集成层说明文档 · 与天龙协同矩阵 · 安装指南 |
| `LICENSE` | 上游 BSD-3-Clause 原文（10 段 31 行，**必须保留**）|
| `NOTICE` | 上游版权 + **Modified by dragon-engine / 2026-08-23** 标注（BSD 第 2 条要求）|
| `INTEGRATION_CHECKLIST.md` | 11 项上线 checklist（plugins/agents 联动验证）|
| `scripts/install-context-doctor.sh` | 一键安装脚本（老李 DSH 宿主页执行）|
| `scripts/audit-template.md` | context_audit 调用模板（DSH 模型提示词）|

> **不入主仓的部分**：上游 `src/` 源码（audit.ts/scan.ts/analyze.ts/tokens.ts/routes.ts）**不镜像到本仓**——它通过 DSH cordis bundle 插件机制动态加载，本仓只保留合规文件 + 集成文档。

---

## 二、安装步骤（DSH 宿主页一行命令）

```bash
# 1. 安装插件到 dsh web profile
dsh plugin --profile web add "github:Zhenyu98/dsh-context-doctor#main"

# 2. 验证合成树
dsh --profile web --dump-config | grep context-doctor

# 预期成功信号：
# - insert:
#     - id: context-doctor
#       name: 'dsh-context-doctor'

# 3. 重启 dsh web
# Ctrl+C 关掉当前 dsh web 进程，再重新 dsh web

# 4. 验证（在新会话里调工具）
context_audit
# 或更详细的：
context_audit detail=developer includeSkillBodies=true maxSkillBodies=20
```

**失败排查**：
| 现象 | 原因 | 解决 |
|------|------|------|
| `dsh plugin` 报 unknown subcommand | DSH 版本 < 0.1.0-rc.6 | 升级 DSH |
| `dump-config` 找不到 context-doctor | 插件没成功 install | 重新跑步骤 1，看 stderr |
| Web UI 没圆环 | 没重启 / 没进已有会话 | 重启 dsh web + 进已有会话（new session 无 sessionId 时不显示）|
| 工具调不动 | headless 模式无 webServer | 工具仍可用，圆环不显示是预期 |

---

## 三、上游协议合规（BSD-3-Clause 红线）

| BSD-3-Clause 条款 | 应用 | 落地 |
|-------------------|------|------|
| **第 1 条** 再分发源代码必须保留版权声明 | `LICENSE` 文件包含 `Copyright (c) 2026, dsh-external` | ✅ `LICENSE` 已实拉确认 |
| **第 2 条** 再分发 binary 必须在文档/材料中复制版权 + 免责声明 | `NOTICE` 文件 | ✅ `NOTICE` 已落盘 |
| **第 3 条** 未经书面许可，**不得**用版权人或贡献者名字背书衍生作品 | 天龙不得说"dsh-context-doctor 官方推荐 / 官方认证" | ✅ 集成文档统一用 "Powered by Zhenyu98/dsh-context-doctor" |

**NOTE**：上游未提供 NOTICE 文件（BSD-3-Clause 不强制 NOTICE，但要求 modified 标注）—— 本仓自建 `NOTICE` 含 Modified 标注。

---

## 四、与天龙引擎协同矩阵

### 4.1 痛点命中（天龙当下）

| 天龙实情 | context-doctor 对策 |
|---|---|
| 🟥 用户级 `~/.dsh/AGENTS.md` 已被沙箱从 **571,153 → 65,128 字节**（截 506KB / 88%）| `context_audit` 量化"指令链总 token"，定位重复段落 |
| 🟥 skills **803 个**——`<available_skills>` catalog 每请求常驻 | catalog 描述 token 阈值告警（>3k → medium）|
| 🟥 agents **177 个**——多版本并存（V10.3/V10.4/V11/V12/V13.3）| 命中"同名 skill shadow"检测 |
| 🟥 30+ 第三方集成（agent-reach/aihot/anysearch/baoyu/guizang/cangjie...）| catalog 描述 token 实时监控 |
| 🟥 MCP 工具面无审计 | 按 server 分组统计 |

### 4.2 与已有 SKILL 协同

| SKILL | 协同方式 |
|---|---|
| **a-stock-data-bridge** (Apache-2.0) | 阶段 25 新增 + 5 Agent 升级前/后 audit 对比 |
| **anysearch** (Apache-2.0) | 3 垂直封装 catalog 描述去重 |
| **agent-reach** (MIT) | 15 渠道 catalog 描述审计 |
| **aihot** (MIT) | V1.1 描述与其他热点 SKILL 撞车检测 |
| **neat-freak** | memory 治理互补（neat-freak 治"内容重复"，context-doctor 治"catalog 重复"）|
| **advanced-memory-sync** | 同属"减负"三角，各治一域 |
| **session-distiller** | 蒸馏产 skill → catalog → 监控 |

### 4.3 与已有 Agent 协同（天龙阶段 26 改造）

| Agent | 改造 |
|---|---|
| **🆕 40-01 上下文治理师 V1.0** | 专责 daily/weekly context_audit + 裁剪建议 + 回归验证 |
| **07-scribe V12.1 → V12.2** | daily brief 加"context health index"章节 |
| **09-06-skills-administrator V1.0 → V1.1** | 上线前 audit 门禁 + catalog 阈值告警 + shadow 检测 |
| **09-03-meta-reviewer** | 评审流程加"context_audit 必跑"环节 |
| **09-04-chief-of-staff** | 周报加"上下文治理 KPI"章节 |

---

## 五、阶段 26 实施边界

| 验收项 | 数量 | 备注 |
|-------|------|------|
| 安装合规文件落盘 | 4 文件 | README/LICENSE/NOTICE/CHECKLIST |
| Agent 新增 | 1 | 40-01 上下文治理师 V1.0 |
| Agent 升级 | 2 | 07-scribe V12.2 + 09-06-skills-administrator V1.1 |
| 主题文件 | 1 | memory/context-doctor-integration.md |
| pytest PASS 增量 | 暂不强制（DSH 插件无需跑天龙 pytest）| 通过 dsh plugin 自身的 29 用例（上游已 PASS）|

---

## 六、来源链接

- 仓库：<https://github.com/Zhenyu98/dsh-context-doctor>
- v0.6.1 package.json：<https://raw.githubusercontent.com/Zhenyu98/dsh-context-doctor/main/package.json>
- LICENSE（BSD-3-Clause 31 行）：<https://raw.githubusercontent.com/Zhenyu98/dsh-context-doctor/main/LICENSE>
- README：<https://raw.githubusercontent.com/Zhenyu98/dsh-context-doctor/main/README.md>
- 核心源码：`src/index.ts` + `src/audit.ts` + `src/scan.ts` + `src/analyze.ts` + `src/tokens.ts`（17KB+8KB+5KB+1KB，不镜像）
- DSH 官方插件机制：<https://github.com/dsh-external/plugin-registry>

---

## 版本信息

- **v0.6.1**（2026-08-22 上游最后 commit，仍在活跃迭代）
- **集成版本 V1.0**（2026-08-23 · 天龙阶段 26 · 老李拍板）
- **协议风险**：🟢 零（BSD-3-Clause，仅保留版权 + 禁背书）
- **适配成本**：🟢 极低（DSH 官方插件，peer 依赖已在天龙仓）
