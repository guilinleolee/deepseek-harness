---
name: rollback
description: 回滚 - 代码或部署的回退操作
invokable: true
allowed-tools: Read, Glob, Bash, Write, TodoWrite
---
## Context

- Current state: !`git log --oneline -5`
- Last deployment: !`echo "请提供上次部署的版本或commit"`

## Your Task

执行回滚流程：

### 步骤 1: 确认回滚原因
- 记录需要回滚的问题
- 评估问题严重程度
- 确定回滚范围

### 步骤 2: 方案选择
```bash
# 查看最近的 commits
git log --oneline -10

# 查看部署历史
kubectl rollout history deployment/app

# 查看当前状态
kubectl get pods -o wide
```

### 步骤 3: 执行回滚

#### 代码回滚
```bash
# 回滚到上一个版本
git revert HEAD

# 回滚到指定版本
git revert <commit-hash>

# 重置到指定版本（谨慎使用）
git reset --hard <commit-hash>
```

#### 部署回滚
```bash
# Kubernetes 回滚
kubectl rollout undo deployment/app

# Docker Compose 回滚
docker-compose down && docker-compose -f docker-compose.backup.yml up

# 数据库迁移回滚
npm run migrate:down
```

### 步骤 4: 验证回滚
```bash
# 验证服务状态
kubectl get pods

# 运行健康检查
curl http://localhost:3000/health

# 运行冒烟测试
npm run test:smoke
```

### 步骤 5: 记录和通知
- 记录回滚原因和过程
- 通知相关人员
- 安排问题修复

## 回滚决策树

```
需要回滚？
├── 代码问题 → git revert
├── 部署问题 → kubectl rollout undo
├── 数据库问题 → migrate:down
└── 配置问题 → 恢复配置
```

## 注意事项

- 优先保留现场用于问题分析
- 确保回滚不会导致数据丢失
- 回滚后立即通知相关方
- 制定问题修复计划
