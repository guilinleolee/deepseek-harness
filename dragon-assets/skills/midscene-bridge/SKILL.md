---
name: midscene-bridge
license: MIT
description: web-infra-dev/midscene 桥接 — 纯视觉 GUI agent · 多平台(网页/iOS/Android/HarmonyOS/桌面)统一抽象 · 阶段 27 ROI-3
metadata:
  version: "1.0"
  author: "dragon-engine"
  upstream: web-infra-dev/midscene · 14.7k ⭐ · MIT
  upstream_repo: https://github.com/web-infra-dev/midscene
  modified: 2026-08-26
  triggers: ["midscene", "midscene-bridge", "视觉 GUI", "pure vision GUI agent"]
---

# midscene-bridge Skill

## L0 · 一句话描述

**纯视觉** GUI agent 桥接 — 无 selector / 无 DOM 依赖 / 多平台统一抽象(Web/iOS/Android/HarmonyOS/桌面)。

## L1 · 使用场景

- 17-07 GUI-VLA 集成工程师 V1.1:**纯视觉** GUI agent 备选(mano-p-core 之外)
- 17-04 桌面自动化工程师 V3.0:canvas / 跨域 iframe / 无语义标注场景兜底
- 04 验证师:UI 视觉验证(颜色/布局/状态)
- 03 构建师:E2E 测试 + Playwright 套件
- 22-创意策划师 / 13-设计师:UI 断言工具

## L2 · 详细文档

### 来源与协议

- **上游**:`web-infra-dev/midscene` · **14,706 ⭐**(2026-08-26 实拉)
- **协议**:MIT ✅(LICENSE verbatim 已落盘 + Modified by 标注)
- **官网**:https://midscenejs.com
- **API 参考**:https://midscenejs.com/reference/

### 核心定位

> **Less maintenance** — no selectors to chase when the UI changes.
> **Reach every element and surface** — if a human can see it, Midscene can target it, even with no semantic annotations, on `<canvas>`, native apps, and cross-origin iframes.
> **Assert what users actually see** — verify colors, highlights, layout, and rendered state, not just whether a DOM node exists.

### 与其他 GUI agent 的对比

| 维度 | cua-driver(AX 优先)| **midscene(纯视觉)** | 传统 DOM-based |
|------|---------------------|----------------------|----------------|
| **依赖** | Accessibility API | **截图 + VLM** | DOM 结构 + selector |
| **脆弱性** | 中(AX 树变化)| **低(只看截图)** | 高(每次重构崩)|
| **canvas / iframe** | ❌ 不可 | **✅ 通吃** | ❌ 不可达 |
| **native apps** | ⚠️ 部分 | **✅ 通吃** | ❌ 不可达 |
| **速度** | **~80ms** | **~1-3s**(VLM)| <100ms |
| **模型要求** | 无 | **强 UI 定位 VLM** | 无 |
| **多平台统一 API** | ❌ 桌面 only | **✅ 5 平台** | ❌ Web only |

### 4 大平台 + 5 模型策略

| 平台 | 集成 | SDK |
|---|---|---|
| **Web** | ✅ | `@midscene/web` · Playwright/Puppeteer |
| **iOS** | ✅ | `midscene-ios` · scrcpy / yume-chan / appium-webdriveragent |
| **Android** | ✅ | `@midscene/android` · appium-adb / scrcpy / YADB |
| **HarmonyOS** | ✅ | `@midscene/harmonyos` |
| **Desktop** | ✅ | `@midscene/desktop` · libnut-core |

**模型策略**(纯视觉 UI 定位):
- **Qwen3.x**(自托管 · **天龙推荐**)
- Doubao-Seed-2.1-Pro
- GLM-4.6V
- gemini-3.5-flash
- UI-TARS(开源 · ByteDance)

### 3 大 API

| API | 用途 | 备注 |
|---|---|---|
| `aiAct` | 自然语言操作 | "Click the login button" |
| `aiQuery` | 屏幕数据提取 | 返回结构化 JSON |
| `aiAssert` | UI 验证 | 颜色/布局/状态 |

### JS SDK 示例

```javascript
import { PageAgent } from '@midscene/web';
import { chromium } from 'playwright';

const browser = await chromium.launch();
const page = await browser.newPage();
await page.goto('https://example.com');

const agent = new PageAgent(page, {
  model: { provider: 'qwen', name: 'qwen3.5-plus' },
});

// 自然语言操作
await agent.aiAct('Click the login button');
await agent.aiAct('Type "hello" in the search box');

// 数据提取
const result = await agent.aiQuery('{title: string, price: number}[]');
console.log(result);

// UI 验证
await agent.aiAssert('The login button is visible');
```

### 与 Playwright/Vitest 集成

```javascript
// 加到 Playwright 测试套件
import { test, expect } from '@playwright/test';
import { midscene } from '@midscene/web';

test('login flow', async ({ page }) => {
  await page.goto('https://example.com/login');
  await midscene(page).aiAct('Type "user@example.com" in email field');
  await midscene(page).aiAct('Type "password123" in password field');
  await midscene(page).aiAct('Click login button');
  await midscene(page).aiAssert('Welcome message is visible');
});
```

### YAML 配置(hand-off 给 AI agent)

```yaml
# tasks/login.yaml
name: 登录流程
platform: web
model: qwen3.5-plus
steps:
  - aiAct: Navigate to https://example.com/login
  - aiAct: Type "user@example.com" in email field
  - aiAct: Type "password123" in password field
  - aiAct: Click login button
  - aiAssert: Welcome message is visible
```

### 与既有 skill 协同

| 既有 skill | 协同点 |
|---|---|
| `skills/cua-driver-bridge/`(ROI-1)| AX 树可解析 → cua · 否则 → midscene |
| `skills/browser-use-bridge/`(ROI-2)| 浏览器 GUI 优先 browser-use · canvas/iframe 兜底 midscene |
| `skills/browser-use-mcp/` V2.0 | MCP 协议互通 |
| `skills/browser-harness-core/` V2.0 | 多步骤任务编排 |
| `skills/agent-browser/` (Vercel Labs) | 确定性 ref · 性能关键场景 |
| `skills/dsh-computer-use/`(阶段 26)| macOS 桌面代理 · 不抢焦点 |

### Agent 接入点

- **17-04-desktop-automation-engineer** V3.0:**双引擎裁决** · AX 可达 → cua · 否 → midscene
- **17-07-gui-vla-engineer** V1.1(本阶段升级):mano-p-core + **midscene** 双轨
- **04-validator**:UI 视觉断言
- **13-designer**:UI/UX 验证
- **22-creative-planner**:跨平台 UI 验收

### 验证(midscene_check.py)

```bash
python scripts/midscene_check.py
# 退出码契约 0/1/2/3
# 0 = 全部健康
# 1 = 工具不可用
# 2 = 限流 / 模型未配
# 3 = schema 不匹配
```

### 风险与边界

| 风险 | 处置 |
|---|---|
| 纯视觉模型未配 | 配 Qwen3.x 或 GLM-4.6V(天龙已栈)|
| 截图慢(~1-3s)| 批量任务并行 · cache 复用 |
| VLM 误定位 | 加 aiAssert 二次校验 |
| 多平台 SDK 部分测试不全 | 优先 Web + Android · iOS/HarmonyOS/Desktop 验证后置 |
| 上游快速迭代(7 天 1 commit)| 月度 skill-updater 检测 |

---

## 累计验证 · 4 PASS

```
test_01_skill_md_exists       PASS
test_02_license_verbatim      PASS
test_03_3_api_wrappers        PASS
test_04_midscene_check_4_code PASS

---EXIT: 0---
```

---

## 来源链接

- 上游 README:https://github.com/web-infra-dev/midscene
- 上游 Midscene Skills:https://github.com/web-infra-dev/midscene-skills
- 官方文档:https://midscenejs.com
- API 参考:https://midscenejs.com/reference/
- Showcases:https://midscenejs.com/showcases
- Model Strategy:https://midscenejs.com/model-strategy
- 本地路径:`C:\Users\li\.claude\projects\dragon-engine\skills\midscene-bridge\`
- 主主题文件:`memory/stage27-computer-use-expansion.md`(本阶段)

---

## 版本信息

- **V1.0**(2026-08-26):阶段 27 ROI-3 · 3 API 封装 + 4 PASS 验证
- **下次同步点**:17-07 V1.1 升级后