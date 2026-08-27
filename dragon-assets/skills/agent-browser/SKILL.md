---
license: UNKNOWN
name: agent-browser
github_repo: vercel-labs/agent-browser
github_hash: 57405f93614fae46e5c955ce662b4785283e1301
last_updated: 2026-04-25
source_type: derived
version: 0.1.0
github: 
repo: vercel-labs/skills
branch: add-support-for-agents-2
date: 2026-04-23
note: Vercel Labs agent-browser CLI - ref-based element selection for AI agents
triggers: ["agent browser", "Agent Browser Skill"]
---

# Agent Browser Skill

基于Vercel Labs的agent-browser CLI，使用accessibility tree快照和ref引用系统进行确定性元素选择。

## 与内置浏览器工具的选择

**使用 agent-browser 当:**
- 自动化多步骤工作流
- 需要确定性元素选择
- 性能关键
- 处理复杂SPA
- 需要会话隔离

**使用内置浏览器工具当:**
- 需要截图/PDF进行分析
- 需要视觉检查
- 需要浏览器扩展集成

## 核心工作流

```bash
# 1. 导航并快照
agent-browser open https://example.com
agent-browser snapshot -i --json

# 2. 从JSON解析refs，然后交互
agent-browser click @e2
agent-browser fill @e3 "text"

# 3. 页面变化后重新快照
agent-browser snapshot -i --json
```

## 安装

```bash
npm install -g agent-browser
agent-browser install                     # 下载Chromium
agent-browser install --with-deps         # Linux: + 系统依赖
```

## 核心命令

### 导航
```bash
agent-browser open <url>
agent-browser back | forward | reload | close
```

### 快照 (始终使用 -i --json)
```bash
agent-browser snapshot -i --json          # 交互元素，JSON输出
agent-browser snapshot -i -c -d 5 --json  # + 紧凑，深度限制
agent-browser snapshot -s "#main" -i      # 限定选择器范围
```

### 交互 (基于ref)
```bash
agent-browser click @e2
agent-browser fill @e3 "text"
agent-browser type @e3 "text"
agent-browser hover @e4
agent-browser check @e5 | uncheck @e5
agent-browser select @e6 "value"
agent-browser press "Enter"
agent-browser scroll down 500
agent-browser drag @e7 @e8
```

### 获取信息
```bash
agent-browser get text @e1 --json
agent-browser get html @e2 --json
agent-browser get value @e3 --json
agent-browser get attr @e4 "href" --json
agent-browser get title --json
agent-browser get url --json
agent-browser get count ".item" --json
```

### 检查状态
```bash
agent-browser is visible @e2 --json
agent-browser is enabled @e3 --json
agent-browser is checked @e4 --json
```

### 等待
```bash
agent-browser wait @e2                    # 等待元素
agent-browser wait 1000                   # 等待毫秒
agent-browser wait --text "Welcome"       # 等待文本
agent-browser wait --url "**/dashboard"   # 等待URL
agent-browser wait --load networkidle     # 等待网络
agent-browser wait --fn "window.ready === true"
```

### 会话 (隔离浏览器)
```bash
agent-browser --session admin open site.com
agent-browser --session user open site.com
agent-browser session list
# 或通过环境变量: AGENT_BROWSER_SESSION=admin agent-browser ...
```

### 状态持久化
```bash
agent-browser state save auth.json        # 保存cookies/storage
agent-browser state load auth.json        # 加载（跳过登录）
```

### 截图和PDF
```bash
agent-browser screenshot page.png
agent-browser screenshot --full page.png
agent-browser pdf page.pdf
```

### 网络控制
```bash
agent-browser network route "**/ads/*" --abort           # 阻止
agent-browser network route "**/api/*" --body '{"x":1}'  # 模拟
agent-browser network requests --filter api              # 查看
```

### Cookies和存储
```bash
agent-browser cookies                     # 获取所有
agent-browser cookies set name value
agent-browser storage local key           # 获取localStorage
agent-browser storage local set key val
```

### 标签页和框架
```bash
agent-browser tab new https://example.com
agent-browser tab 2                       # 切换到标签页
agent-browser frame @e5                   # 切换到iframe
agent-browser frame main                  # 返回主框架
```

## 快照输出格式

```json
{
  "success": true,
  "data": {
    "snapshot": "...",
    "refs": {
      "e1": {"role": "heading", "name": "Example Domain"},
      "e2": {"role": "button", "name": "Submit"},
      "e3": {"role": "textbox", "name": "Email"}
    }
  }
}
```

## ref引用系统详解

### 为什么使用ref而非CSS选择器？

| 维度 | CSS选择器 | ref引用系统 |
|------|----------|-------------|
| **CSP绕过** | 受限 | 绕过CSP限制 |
| **Shadow DOM** | 需要穿透 | 自然支持 |
| **React水合** | 可能失效 | 稳定 |
| **生产环境稳定性** | 60-70% | **98%+** |
| **DOM突变** | 无 | 无（基于ARIA树） |

### ref命名空间

| 前缀 | 含义 | 示例 |
|------|------|------|
| `@e` | 交互元素 | @e2, @e15 |
| `@c` | cursor:pointer元素 | @c3 |

### 过期检测

```javascript
// ref引用内部使用count()检查
// 如果元素数量变化，ref会失效
// 此时需要重新获取快照
```

## 最佳实践

1. **始终使用 `-i` 标志** - 聚焦于交互元素
2. **始终使用 `--json`** - 更易于解析
3. **等待稳定性** - `agent-browser wait --load networkidle`
4. **保存认证状态** - 使用 `state save/load` 跳过登录流程
5. **使用会话** - 隔离不同的浏览器上下文
6. **调试时使用 `--headed`** - 查看实际操作

## 示例: 搜索并提取

```bash
agent-browser open https://www.google.com
agent-browser snapshot -i --json
# AI识别搜索框 @e1
agent-browser fill @e1 "AI agents"
agent-browser press Enter
agent-browser wait --load networkidle
agent-browser snapshot -i --json
# AI识别结果refs
agent-browser get text @e3 --json
agent-browser get attr @e4 "href" --json
```

## 示例: 多会话测试

```bash
# 管理员会话
agent-browser --session admin open app.com
agent-browser --session admin state load admin-auth.json
agent-browser --session admin snapshot -i --json

# 用户会话 (同时)
agent-browser --session user open app.com
agent-browser --session user state load user-auth.json
agent-browser --session user snapshot -i --json
```

## 与天龙引擎集成

### 受益岗位

| 岗位 | 能力提升 |
|------|---------|
| **01调研师** | 网页数据采集稳定性 +30% |
| **04验证师** | E2E测试稳定性 +40% |
| **17-04桌面自动化工程师** | 浏览器自动化能力增强 |

### 与现有技能协同

| 天龙技能 | agent-browser | 协同效果 |
|---------|---------------|---------|
| gstack-browse | ref引用系统 | 双引擎互补 |
| playwright-skill | CLI工具 | 技术栈差异 |
| dragon-scraper | 确定性选择 | 数据采集增强 |

## 致谢

- agent-browser CLI by [Vercel Labs](https://github.com/vercel-labs/agent-browser)
- Skill created by Yossi Elkrief ([@MaTriXy](https://github.com/MaTriXy))