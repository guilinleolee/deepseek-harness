---
license: UNKNOWN
---

# Design Token Automation System

## 触发词
`design-token`、`token-sync`、`design-sync`、`设计变量`、`design-system`

## 技能描述
Design Token全生命周期自动化系统，实现Figma设计变量到前端代码的自动化同步、版本控制和CI/CD流水线。

## 核心功能

### 1. Design Token同步
- Figma → Git自动同步
- 增量更新机制
- 冲突自动解决
- 版本历史管理

### 2. 代码生成
- CSS变量生成
- Tailwind配置生成
- SCSS变量生成
- TypeScript类型定义

### 3. CI/CD流水线
- 自动化测试
- 质量检查
- 自动发布
- 变更通知

### 4. 版本控制
- Git集成
- 变更追踪
- 回滚支持
- 分支管理

## 工作流程

```
Figma设计变更
    ↓
检测变更（Webhook）
    ↓
提取Design Token
    ↓
生成代码文件
    ↓
运行测试
    ↓
Git提交
    ↓
创建PR
    ↓
代码审查
    ↓
合并发布
    ↓
通知团队
```

## 配置文件

### design-token.config.js
```javascript
module.exports = {
  // Figma配置
  figma: {
    fileId: 'your-file-id',
    tokenSetId: 'your-token-set-id'
  },

  // 输出配置
  output: {
    css: './src/styles/tokens.css',
    tailwind: './tailwind.config.js',
    scss: './src/styles/tokens.scss',
    typescript: './src/types/tokens.ts'
  },

  // Git配置
  git: {
    branch: 'main',
    commitMessage: 'chore: update design tokens',
    prTitle: 'Design Tokens Update',
    prBody: 'Automated design token sync from Figma'
  },

  // 测试配置
  tests: {
    coverage: true,
    lint: true,
    typeCheck: true
  }
};
```

## 使用示例

### 手动同步
```bash
# 同步所有Design Token
npx design-token-system sync

# 同步特定变量集
npx design-token-system sync --set colors

# 预览变更（不提交）
npx design-token-system sync --dry-run
```

### 自动化CI/CD
```yaml
# .github/workflows/design-tokens.yml
name: Design Tokens Sync

on:
  schedule:
    - cron: '0 */4 * * *'  # 每4小时
  workflow_dispatch:

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Sync Design Tokens
        run: npx design-token-system sync
        env:
          FIGMA_ACCESS_TOKEN: ${{ secrets.FIGMA_TOKEN }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## 相关技能
- `vibma-design` - Figma设计操作
- `theme-factory` - 主题工厂
- `frontend-design` - 前端设计实现

## 版本
V1.0 - 初始版本，支持完整的Design Token CI/CD流水线
