# 5 类天龙 Agent 协同接入点

> **Why**:天龙 28-04 / 35-02 / 35-05 / 28-10 / dsh-vision-toolkit 5 个 Agent / Skill 需要在 macOS 上做"原生 app 实操",通过 computer-use 注入对应触发词与触发段。

---

## 1. 28-04 内容策划师 V10.x

### 触发词注入

在 `agents/28-04-content-planner-v10-l0l1l2.md` `depends` 段加:

```yaml
depends:
  - dsh-computer-use V1.0
upstream:
  - dsh-computer-use 0.1.0 (Anionex · MIT ✅ · macOS native action layer)
```

### 用法

| 场景 | 工具链 |
|------|--------|
| 小红书 / 抖音 / 微信 app 实际呈现(绕 WAF) | `computer_observe`(screenshot)→ `dsh-vision-toolkit`(`vision_glance`) |
| 跨 app 调研(同一研究内多个 app 切换) | `computer_list_apps` → 多次 `computer_observe` + `targetHandle` 切窗 |
| 抓 app 内置数据(客户端 UI) | `computer_observe`(无 screenshot)+ `computer_set_value` 模拟搜索 |

### DON'T

- 不要在小红书 / 抖音 app 里**模拟发布** —— 这是 `computer_confirm` 高风险场景
- 不要把微信 app 截图存到公共目录 —— 包含用户私密数据

---

## 2. 35-02 社媒运营 V13.x

### 触发词注入

在 `agents/35-02-social-media.md` Step 5 实操段加:

```yaml
step_5_publish:
  preferred_tools:
    - dsh-computer-use V1.0 (macOS 上控制发布 app)
    - aihot V1.1 (实时 AI 资讯)
```

### 用法

| 场景 | 工具链 |
|------|--------|
| 视频号封面在 Mac 上裁剪 | `computer_observe`(截图)→ `computer_drag` 移动选区 → 导出 |
| macOS 上手动演示发图文(录制教学视频) | `computer_observe` → `computer_type_text` 写文 → `computer_perform_action` 点发布 |
| 多平台同步发布 | `computer_list_apps` → 多个 `computer_observe` 跨 app |

### DON'T

- 不要在小红书 app 里模拟评论 —— 这是 `computer_confirm` 高风险
- 视频号发视频时,先用 `computer_wait` 等到进度条 100% 再关 app,避免半成品

---

## 3. 35-05 短视频导演 V10.x

### 触发词注入

在 `agents/35-05-short-video-director.md` 镜头脚本实操段加:

```yaml
cutting_apps:
  - Final Cut Pro (macOS)
  - Adobe Premiere Pro (macOS)
  - CapCut for Mac
  control_via: dsh-computer-use V1.0
```

### 用法

| 场景 | 工具链 |
|------|--------|
| 把素材拖到 FCP 时间线 | `computer_observe` → `computer_drag`(timeline position) |
| 切片段 | `computer_observe` → `computer_press_key`(cmd+b) |
| 调整音量 | `computer_observe` → `computer_set_value`(slider) |
| 导出 | `computer_perform_action`("Export" button AXPress) |

### DON'T

- 导出视频是个长时间操作,务必 `computer_wait`(text:"Export Complete")而不是直接关 app
- 不要在导出过程中切到其他 app —— `targetHandle` 会失效

---

## 4. 28-10 财经数据底座师 V1.x

### 触发词注入

在 `agents/28-10-finance-data-base.md` 数据采集段加:

```yaml
data_sources:
  - a-stock-data V3.4.0 (API)
  - global-stock-data V1.0.1 (API)
  - 雪球 / 同花顺 Mac 客户端 (已登录态) — dsh-computer-use V1.0
```

### 用法

| 场景 | 工具链 |
|------|--------|
| 抓雪球 Mac 客户端自选股(API 不可达) | `computer_list_apps`(找 com.xueqiu.MacStock) → `computer_observe` → 提取自选股 |
| 同花顺 Mac F10(已登录态) | `computer_observe`(无 screenshot)+ 解析 AX tree |
| 雪球评论热榜(已绕过 WAF) | `computer_observe` → 解析 AX tree |

### DON'T

- 雪球 / 同花顺的 Mac 客户端 session 经常掉,务必先 `computer_observe` 确认登录态
- 不要抓**别人的**自选股 —— 这是 `computer_confirm` 高风险

---

## 5. dsh-vision-toolkit(跨 skill 协同)

### 协同模式

```
dsh-computer-use.computer_observe (screenshot=True)
   ↓ PNG 文件落盘到 artifactRoot
dsh-vision-toolkit.vision_glance(image=PATH)
   ↓ OCR + 视觉理解
dsh-vision-toolkit.vision_ground(image=PATH, query="找发送按钮")
   ↓ 返回坐标
dsh-computer-use.computer_click (coordinate)
```

### 用法

| 场景 | 工具链 |
|------|--------|
| OCR 截图识别 app 界面元素 | observe → vision_glance → 解析 |
| 找截图里"发送按钮"位置 | observe → vision_ground(query) → click |
| 批量截图分析 | observe × N → vision_long_screenshot_ocr → 综合 |

### DON'T

- 不要把 screenshot 落盘到公开目录 —— 包含敏感数据
- 不要把 secure text(密码、token)截到 screenshot,provider 会自动脱敏为 `[secure]`,但下游 OCR 不要尝试解析它

---

## 横切协同图

```
dsh-computer-use (native 动作层 · 0.1.0)
   ├─► 28-04 内容策划师 V10.x (绕 WAF 看 app 真实形态)
   ├─► 35-02 社媒运营 V13.x (macOS 端发图文实操)
   ├─► 35-05 短视频导演 V10.x (剪辑 app 实控)
   ├─► 28-10 财经底座师 V1.x (抓 mac 客户端 UI 数据)
   └─► dsh-vision-toolkit (截图 → OCR / 视觉理解)
```

**红线**(全协同段):
- 任意 `computer_confirm` 调用前必须先在 SKILL.md / agent.md 列出**为什么**这个动作需要确认(7 类高风险清单)
- 任意截图落盘前必须先有 `artifactRoot` 设置(默认 workspace-relative)
- 任意 sensitive 截图必须打 `[secure]` 标签(下游 vision-tools 不要解析)

## 相关链接

- [[../../SKILL.md]] · 主 SKILL.md(L6 节)
- [上游 Scope](https://github.com/Anionex/dsh-computer-use#scope)
- [上游 How it works](https://github.com/Anionex/dsh-computer-use#how-it-works)