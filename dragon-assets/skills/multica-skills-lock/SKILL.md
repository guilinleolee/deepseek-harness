---
license: UNKNOWN
github_repo: multica-ai/multica
github_hash: 5eab1dbbe1826616ec57bee57cf939a64b341125
last_updated: 2026-04-25
source_type: derived
triggers: ["multica skills lock", "multica-skills-lock"]
---
# multica-skills-lock

> Multica Skills Lock 机制 — 技能版本锁定与依赖管理

## L0: 一句话描述
技能版本锁定文件：`skills-lock.json` 约束技能依赖，确保 Agent 执行一致性

## L1: 使用场景

- 需要锁定技能版本避免自动更新破坏功能
- 需要管理技能依赖链（技能A依赖技能B）
- 需要在 Workspace 级别共享技能配置
- 需要确保不同 Agent 运行相同版本技能

## L2: 详细文档

### Skills Lock 核心架构

```
┌─────────────────────────────────────────────────────────────┐
│           Multica Skills Lock 架构                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  skills-lock.json                                          │
│  ├── version: "1.0.0"                                      │
│  ├── skills[]                                              │
│  │   ├── name: "react-dev"                                │
│  │   ├── version: "2.1.0"                                │
│  │   ├── source: "npm" | "github" | "local"              │
│  │   └── dependencies: ["typescript", "vite"]              │
│  └── workspaces[]                                          │
│      └── workspace_id → skill references                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 锁定策略

| 策略 | 说明 | 适用场景 |
|------|------|---------|
| `exact` | 精确版本 `"2.1.0"` | 生产环境，必须锁定 |
| `range` | 版本范围 `"^2.1.0"` | 开发环境，允许补丁更新 |
| `latest` | 始终最新 | 测试/预览环境 |
| `workspace` | Workspace 级别覆盖 | 多租户场景 |

### CLI 命令

```bash
# 安装技能（自动生成 skills-lock.json）
multica skills install react-dev@2.1.0

# 锁定所有技能版本
multica skills lock

# 验证锁定状态
multica skills verify

# 更新技能（更新锁文件）
multica skills update react-dev@2.2.0

# 解锁技能
multica skills unlock react-dev

# 查看依赖树
multica skills tree
```

### 依赖解析规则

```json
{
  "skills-lock.json": {
    "version": "1.0.0",
    "resolve_strategy": "topological_sort",
    "conflict_resolution": "workspace_precedence",
    "skills": [
      {
        "name": "code-review",
        "version": "1.5.0",
        "hash": "sha256:abc123...",
        "source": "github",
        "dependencies": [
          { "name": "eslint", "version": "8.50.0" },
          { "name": "prettier", "version": "3.0.0" }
        ]
      }
    ]
  }
}
```

### Workspace 级别覆盖

```bash
# 为特定 Workspace 覆盖技能版本
multica skills override --workspace ws-001 --skill react-dev@3.0.0

# 列出 Workspace 覆盖
multica skills overrides --workspace ws-001

# 清除 Workspace 覆盖
multica skills override --workspace ws-001 --skill react-dev --clear
```

### 天龙岗位集成

#### 08 发布师 (V8.91)

```yaml
发布流程集成:
  1. pre-deploy: multica skills verify --strict
  2. 确保 skills-lock.json 提交到 Git
  3. 部署后验证技能版本一致性
  4. 异常时自动回滚技能版本
```

#### 09-02 编排协调师 (V8.91)

```yaml
多Agent技能管理:
  1. 为每个 Workspace 生成 skills-lock.json
  2. 验证所有 Agent 技能版本一致性
  3. 检测技能依赖冲突
  4. Workspace 间技能同步
```

### 与天龙现有技能协同

| 天龙组件 | 协同方式 | 效果 |
|---------|---------|------|
| claude-mem | 技能记忆缓存 + 版本锁定 | 一致性+50% |
| paperclip-ticket | 工单记录技能变更历史 | 可追溯性+200% |
| blueprint | 计划锁定 + 技能版本绑定 | 执行稳定性+100% |
| ai-router | 技能优先级 + 版本偏好 | 路由精确度+30% |

### 最佳实践

1. **生产环境必须锁定**：使用 `exact` 策略
2. **CI/CD 验证**：每次部署前运行 `multica skills verify`
3. **Workspace 隔离**：多租户场景使用 Workspace 级别覆盖
4. **依赖审查**：新增技能前检查依赖树

---

*来源: [multica-ai/multica](https://github.com/multica-ai/multica) - Skills Lock机制*
