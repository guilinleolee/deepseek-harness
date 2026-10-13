---
license: UNKNOWN
name: database-migrations
description: Database migration best practices for schema changes, data migrations, rollbacks, and zero-downtime deployments across PostgreSQL, MySQL, and common ORMs (Prisma, Drizzle, Kysely, Django, golang-migrate).
github_repo: affaan-m/everything-claude-code
github_hash: 4e66b2882da9afb9747468b08a253ca2f09c85f3
last_updated: 2026-04-25
source_type: derived
origin: ECC (everything-claude-code)
triggers: ["database migrations", "Database Migration Patterns — 数据库迁移模式"]
---

# Database Migration Patterns — 数据库迁移模式

> 来源: [affaan-m/everything-claude-code/skills/database-migrations](https://github.com/affaan-m/everything-claude-code)

## 功能概述

安全、可逆的数据库模式变更规范，覆盖PostgreSQL/MySQL模式变更、数据迁移、回滚策略及零停机部署。适用于Prisma/Drizzle/Kysely/Django/golang-migrate等主流ORM工具。

## 何时使用

- 创建或修改数据库表结构
- 添加/删除列或索引
- 运行数据迁移（回填、转换）
- 规划零停机模式变更
- 为新项目配置迁移工具

## 核心原则

1. **每个变更都是迁移** — 绝不手动修改生产数据库
2. **迁移是不可变的** — 永远不要编辑已部署的迁移文件
3. **模式迁移与数据迁移分离** — DDL和DML绝不在同一迁移中混合
4. **在生产规模数据上测试迁移** — 处理100行的迁移在10M行时可能锁表
5. **Expand-Contract模式** — 零停机重命名/删除列

## 迁移安全检查表

| 检查项 | 说明 |
|--------|------|
| 迁移有UP和DOWN | 或明确标记为不可逆 |
| 大表无全表锁 | 使用并发操作 |
| 新列可空或有默认值 | 绝不添加NOT NULL而无默认值 |
| 索引使用CONCURRENTLY | 不在CREATE TABLE中内联创建 |
| 数据回填与模式变更分离 | 作为独立迁移 |
| 在生产数据副本上测试 | - |

## PostgreSQL模式

### 安全添加列

```sql
-- ✅ Good: 可空列，无锁
ALTER TABLE users ADD COLUMN avatar_url TEXT;

-- ✅ Good: 有默认值（PostgreSQL 11+即时执行，不重写）
ALTER TABLE users ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT true;

-- ❌ Bad: 无默认值的NOT NULL（锁表并重写所有行）
ALTER TABLE users ADD COLUMN role TEXT NOT NULL;
```

### 零停机重命名列（Expand-Contract）

```sql
-- Step 1: 添加新列 (迁移 001)
ALTER TABLE users ADD COLUMN display_name TEXT;

-- Step 2: 回填数据 (迁移 002)
UPDATE users SET display_name = username WHERE display_name IS NULL;

-- Step 3: 应用代码同时读写两列
-- Step 4: 停止写旧列，删除 (迁移 003)
ALTER TABLE users DROP COLUMN username;
```

### 并发创建索引

```sql
-- ❌ Bad: 阻塞大表写操作
CREATE INDEX idx_users_email ON users (email);

-- ✅ Good: 非阻塞，允许并发写
CREATE INDEX CONCURRENTLY idx_users_email ON users (email);
-- 注意: CONCURRENTLY不能在事务块内运行
```

### 批量数据迁移

```sql
-- ❌ Bad: 单事务更新所有行（锁表）
UPDATE users SET normalized_email = LOWER(email);

-- ✅ Good: 分批更新 + FOR UPDATE SKIP LOCKED
DO $$
DECLARE
  batch_size INT := 10000;
  rows_updated INT;
BEGIN
  LOOP
    UPDATE users
    SET normalized_email = LOWER(email)
    WHERE id IN (
      SELECT id FROM users
      WHERE normalized_email IS NULL
      LIMIT batch_size
      FOR UPDATE SKIP LOCKED
    );
    GET DIAGNOSTICS rows_updated = ROW_COUNT;
    RAISE NOTICE 'Updated % rows', rows_updated;
    EXIT WHEN rows_updated = 0;
    COMMIT;
  END LOOP;
END $$;
```

## ORM工具链

### Prisma (TypeScript/Node.js)

```bash
# 从模式变更创建迁移
npx prisma migrate dev --name add_user_avatar

# 在生产环境应用待处理迁移
npx prisma migrate deploy

# 重置数据库（仅开发）
npx prisma migrate reset
```

### Drizzle (TypeScript/Node.js)

```bash
# 从模式变更生成迁移
npx drizzle-kit generate

# 应用迁移
npx drizzle-kit migrate
```

### Django (Python)

```python
# 数据迁移
def backfill_display_names(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    batch_size = 5000
    users = User.objects.filter(display_name="")
    while users.exists():
        batch = list(users[:batch_size])
        for user in batch:
            user.display_name = user.username
        User.objects.bulk_update(batch, ["display_name"], batch_size=batch_size)

class Migration(migrations.Migration):
    dependencies = [("accounts", "0015_add_display_name")]
    operations = [
        migrations.RunPython(backfill_display_names),
    ]
```

### golang-migrate (Go)

```bash
# 创建迁移对
migrate create -ext sql -dir migrations -seq add_user_avatar

# 应用所有待处理迁移
migrate -path migrations -database "$DATABASE_URL" up

# 回滚最后迁移
migrate -path migrations -database "$DATABASE_URL" down 1
```

## 零停机迁移策略

```
Phase 1: EXPAND（扩展）
  - 添加新列/表（可空或带默认值）
  - 部署: 应用同时写入新旧列
  - 回填现有数据

Phase 2: MIGRATE（迁移）
  - 部署: 应用从新列读取，写入新旧列
  - 验证数据一致性

Phase 3: CONTRACT（收缩）
  - 部署: 应用仅使用新列
  - 在独立迁移中删除旧列/表
```

## 反模式

| 反模式 | 问题 | 正确做法 |
|--------|------|---------|
| 手动SQL在生产 | 无审计跟踪，不可重复 | 使用迁移文件 |
| 编辑已部署迁移 | 环境间漂移 | 创建新迁移 |
| NOT NULL无默认值 | 锁表，重写所有行 | 先添加可空，回填，加约束 |
| 大表内联索引 | 创建期间阻塞写操作 | CREATE INDEX CONCURRENTLY |
| 模式+数据同一迁移 | 回滚困难，长事务 | 分离迁移 |
| 删除代码前删除列 | 应用因缺失列报错 | 先删代码，再删列 |

## 天龙引擎集成

### 适用岗位

| 岗位 | 集成方式 | 增强能力 |
|------|---------|---------|
| **03构建师** | ORM迁移实现 | Prisma/Drizzle/Django/go-migrate |
| **04验证师** | 迁移测试 | 批量回填测试 + 并发索引验证 |
| **02架构师** | 零停机策略 | Expand-Contract模式设计 |
| **19-01数据工程师** | 数据管道迁移 | ETL模式变更 |

### 天龙引擎增强

```
┌─────────────────────────────────────────────────────────────┐
│ 天龙引擎 数据库迁移体系                                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   迁移流程:                                                  │
│   ├── 02架构师 → Expand-Contract模式设计                 │
│   ├── 03构建师 → 迁移实现 + ORM工具                     │
│   └── 04验证师 → 并发测试 + 回填验证                    │
│                                                             │
│   协同技能:                                                 │
│   ├── /python-patterns     → Django数据迁移              │
│   ├── /golang-patterns     → golang-migrate             │
│   └── /database-migrations → Prisma/Drizzle/Kysely      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 核心命令

```bash
# Prisma迁移
[@构建师] 使用Prisma实现这个数据库变更
[@构建师] 添加CONCURRENTLY索引

# Django迁移
[@构建师] 创建Django数据迁移回填display_name
[@构建师] 使用SeparateDatabaseAndState安全删除列

# 验证
[@验证师] 测试批量数据迁移（10000行批次）
[@验证师] 验证零停机重命名流程

# 架构设计
[@架构师] 设计这个重命名操作的Expand-Contract方案
```

---

**版本**: V1.0 | **兼容性**: 天龙引擎 V8.68+ | **来源**: ECC
