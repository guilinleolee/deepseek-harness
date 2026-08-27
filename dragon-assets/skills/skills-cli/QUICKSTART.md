# Vercel Skills CLI - 快速参考

## 已安装 ✓

技能已成功安装到 `C:\Users\li\.claude\skills\skills-cli\`

## 立即使用

### 查找技能
```bash
# 交互式搜索
npx skills find

# 关键词搜索
npx skills find typescript
npx skills find frontend
npx skills find testing
```

### 列出已安装技能
```bash
# 列出所有已安装技能
npx skills list

# 仅全局技能
npx skills list -g
```

### 安装技能
```bash
# 安装到 Claude Code（全局）
npx skills add vercel-labs/agent-skills -a claude-code -g

# 列出仓库中的可用技能
npx skills add vercel-labs/agent-skills --list

# 安装特定技能
npx skills add owner/repo --skill frontend-design -a claude-code -g

# 批量安装多个技能
npx skills add owner/repo --skill frontend-design --skill web-design-guidelines -a claude-code -g
```

### 更新技能
```bash
# 检查更新
npx skills check

# 更新所有技能
npx skills update
```

### 移除技能
```bash
# 交互式移除
npx skills remove

# 移除特定技能（全局）
npx skills remove skill-name --global
```

## 常用技能仓库

- **Vercel Agent Skills**: `vercel-labs/agent-skills`
  - 包含前端设计、React 模式、测试模式等核心技能

## 更多信息

- 完整文档：[SKILL.md](./SKILL.md)
- 官方网站：https://skills.sh
- GitHub：https://github.com/vercel-labs/skills
