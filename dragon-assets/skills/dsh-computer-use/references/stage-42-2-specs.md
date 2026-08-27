# 阶段 42.2 接入点规约 · 35-02 社媒运营 + dsh-vision-toolkit

> **TL;DR**:dsh-computer-use V1.0 集成时承诺的 5 类 Agent 协同点中,**35-02 社媒运营 agent** 和 **dsh-vision-toolkit skill** 当前**不在天龙主仓内**。本文件是阶段 42.2 的**接入点规约**(documentation-only),等这两个资产在天龙主仓出现时**直接套用本规约**即可完成协同段注入。

---

## 1. 35-02 社媒运营 · 接入点规约

### 1.1 触发条件与工具链

| 场景 | 工具链 |
|------|--------|
| 视频号封面在 Mac 上裁剪 | `computer_observe`(截图)→ `computer_drag` 移动选区 → 导出 |
| macOS 上手动演示发图文(录制教学视频)| `computer_observe` → `computer_type_text` 写文 → `computer_perform_action` 点发布 |
| 多平台同步发布 | `computer_list_apps` → 多个 `computer_observe` 跨 app |

### 1.2 平台 → app 映射

| 内容运营目标 | 平台 app | dsh-computer-use 适用? |
|--------------|---------|---------------------|
| 公众号 | 微信公众号(微信内置)| ✅ `computer_observe` + `computer_click` |
| 小红书 | 小红书 Mac 客户端 | ✅ `computer_observe` + `computer_type_text` |
| 抖音 | 抖音 Mac 客户端 | ✅ 同上 |
| 视频号 | 视频号(微信内置)| ✅ 同上 |
| 掘金 / 知乎 | 浏览器 web 版 | ⚠️ 优先 `agent-browser` / browser automation |

### 1.3 DON'T

- 不要在小红书 / 抖音 app 里**模拟评论** —— 这是 `computer_confirm` 高风险场景
- 视频号发视频时,务必先 `computer_wait`(text:"进度条 100%")再关 app
- 不要把微信 app 截图存到公共目录 —— 包含用户私密数据

### 1.4 期望注入位置

```yaml
# agents/35-02-social-media.md(若该 agent 后续出现)
## 🔗 阶段 42 协同 · dsh-computer-use V1.0

[本节内容按本规约 §1.1 - §1.4 完整复制]
```

### 1.5 触发词建议

- "在 macOS 上发小红书图文"
- "mac 上演示视频号发布"
- "用 Mac 客户端发公众号"
- "/computer-use" 加载本 Skill 后整套调用

---

## 2. dsh-vision-toolkit · 接入点规约

### 2.1 跨 skill 协同模式

```
dsh-computer-use.computer_observe (screenshot=True)
   ↓ PNG 文件落盘到 artifactRoot
dsh-vision-toolkit.vision_glance(image=PATH)
   ↓ OCR + 视觉理解
dsh-vision-toolkit.vision_ground(image=PATH, query="找发送按钮")
   ↓ 返回坐标
dsh-computer-use.computer_click (coordinate)
```

### 2.2 用法场景

| 场景 | 工具链 |
|------|--------|
| OCR 截图识别 app 界面元素 | observe → vision_glance → 解析 |
| 找截图里"发送按钮"位置 | observe → vision_ground(query) → click |
| 批量截图分析 | observe × N → vision_long_screenshot_ocr → 综合 |
| PII 检测(给截图过隐私合规)| observe → vision_detect(pII=True) → 决定能否公开发布 |

### 2.3 DON'T

- 不要把 screenshot 落盘到公开目录 —— 包含敏感数据
- 不要把 secure text(密码、token)截到 screenshot,provider 会自动脱敏为 `[secure]`
- 下游 vision-tools 不要尝试解析 `[secure]` 标记

### 2.4 期望注入位置

```yaml
# skills/dsh-vision-toolkit/SKILL.md(若该 skill 后续出现)
## 🔗 阶段 42 协同 · dsh-computer-use V1.0

### 跨 skill 协同模式
[本节 §2.1 完整复制]

### 用法场景
[本节 §2.2 完整复制]

### DON'T
[本节 §2.3 完整复制]

### 当前主机状态
- 主机: **Windows**(2026-08-23)→ `COMPUTER_UNSUPPORTED_PLATFORM`
- 等迁 macOS 14+ 后即可使用

### 相关链接
- [[../dsh-computer-use/SKILL.md]] · dsh-computer-use 主 SKILL.md
- [[../dsh-computer-use/references/agent-coordination.md]] · 5 类天龙 Agent 协同接入点
- [[../../memory/dsh-computer-use-integration.md]] · 阶段 42 主题文件
```

### 2.5 触发词建议

- "OCR 一下这张图"
- "找截图里的 XX 元素位置"
- "检测这张截图里的 PII"

---

## 3. 验证清单(42.2 真正完成时)

- [ ] 天龙主仓出现 `agents/35-02-social-media.md` → 套用 §1 规约注入协同段
- [ ] 天龙主仓出现 `skills/dsh-vision-toolkit/SKILL.md` → 套用 §2 规约注入协同段
- [ ] 跑 `pytest skills/dsh-computer-use/tests/test_dsh_computer_use.py` 5/5 PASS
- [ ] 跑 `pytest skills/skill-updater/tests/test_skill_updater.py` 55/55 PASS
- [ ] 更新 `memory/dsh-computer-use-integration.md` §五 Agent 协同矩阵:5 类 → 5 类(完整)
- [ ] 更新 `memory/MEMORY.md` 阶段 42 行(从 "35-02 / dsh-vision-toolkit 不在主仓留 42.2" → "已完成")

---

## 4. 当前阶段 42.2 状态(2026-08-23)

| 项 | 状态 |
|----|------|
| 35-02 社媒运营 agent | ❌ 不在天龙主仓(全仓 grep 无结果) |
| dsh-vision-toolkit skill | ❌ 不在天龙主仓(全仓 grep 无结果) |
| 接入点规约文档 | ✅ 本文件 `references/stage-42-2-specs.md` |
| 等待触发 | ⏳ 天龙主仓出现对应文件时套用 |

**预期收益**:等未来天龙主仓出现 35-02 / dsh-vision-toolkit,只需复制本规约 §1 / §2 即可完成注入,**无需重新设计**(5 分钟工作量 → 30 秒工作量)。

## 5. 相关链接

- [[../SKILL.md]] · dsh-computer-use 主 SKILL.md(L6 节)
- [[agent-coordination.md]] · 已注入的 4 类 Agent 协同段参考
- [[../../memory/dsh-computer-use-integration.md]] · 阶段 42 主题文件
- [[../../memory/MEMORY.md]] 阶段 42 行