---
license: UNKNOWN
github_repo: drizzle-team/drizzle-orm
github_hash: 48e5406027103a9fca6eb66417187c4a8b5c6aa3
last_updated: 2026-04-25
source_type: derived
triggers: ["drizzle orm", "drizzle-orm"]
---
# drizzle-orm

> Drizzle ORM集成 - TypeScript原生的数据库ORM和迁移工具

## 来源项目

| 项目 | Stars | 核心能力 |
|------|-------|---------|
| [drizzle-team/drizzle-orm](https://github.com/drizzle-team/drizzle-orm) | 24k+ | TypeScript ORM + 轻量级 + 多数据库支持 |

## 核心价值

填补天龙引擎在**TypeScript原生ORM**和**自动化迁移**的关键空白，实现：
- 完整的TypeScript类型安全
- 20+数据库原生支持
- CLI自动化迁移
- 轻量级零依赖（~7.4kb）
- Serverless优化

## 技术架构

```
┌─────────────────────────────────────────────────────────────┐
│ Drizzle ORM Architecture                                    │
├─────────────────────────────────────────────────────────────┤
│  Schema Layer                                               │
│  ├── TypeScript Schema Definitions                          │
│  ├── Relations (belongsTo, hasMany)                        │
│  └── Indexes & Constraints                                  │
│                    ↓                                        │
│  Query Layer                                               │
│  ├── Type-Safe Query Builder                               │
│  ├── SQL-like API (select, insert, update, delete)         │
│  └── Raw SQL Support                                        │
│                    ↓                                        │
│  Migration Layer                                           │
│  ├── Drizzle Kit CLI (generate, migrate, push)           │
│  └── Versioned Migrations                                   │
└─────────────────────────────────────────────────────────────┘
```

## 多数据库支持

| 类型 | 数据库 |
|------|--------|
| **PostgreSQL** | PostgreSQL, Neon, Supabase, Vercel Postgres, PlanetScale, CockroachDB, AWS RDS |
| **MySQL** | MySQL, PlanetScale, TiDB, SingleStore |
| **SQLite** | SQLite, Bun SQL, Turso, Cloudflare D1, Expo SQLite |
| **其他** | PGLite, Gel, Cloudflare Durable Objects |

## 天龙岗位升级

| 岗位 | 版本 | 新增能力 | 提升 |
|------|------|---------|------|
| **03构建师** | V8.71 → V8.72 | Drizzle ORM + TypeScript schema | ⭐⭐⭐⭐⭐ |
| **19-01数据工程师** | V8.71 → V8.72 | Drizzle Kit迁移 + 多数据库支持 | ⭐⭐⭐⭐⭐ |

## 核心命令速查

```bash
# 安装
npm install drizzle-orm
npm install -D drizzle-kit

# 生成迁移
npx drizzle-kit generate

# 应用迁移
npx drizzle-kit migrate

# 推送schema（开发模式）
npx drizzle-kit push

# 启动可视化Studio
npx drizzle-kit studio
```

## Schema定义示例

### 用户表

```typescript
import { pgTable, serial, text, varchar, timestamp, boolean, uuid } from 'drizzle-orm/pg-core';

export const users = pgTable('users', {
  id: serial('id').primaryKey(),
  uuid: uuid('uuid').defaultRandom().notNull().unique(),
  name: varchar('name', { length: 255 }).notNull(),
  email: varchar('email', { length: 255 }).notNull().unique(),
  passwordHash: text('password_hash').notNull(),
  emailVerified: boolean('email_verified').default(false).notNull(),
  createdAt: timestamp('created_at').defaultNow().notNull(),
  updatedAt: timestamp('updated_at').defaultNow().notNull(),
});
```

### 文章表（带关系）

```typescript
import { pgTable, serial, text, varchar, timestamp, integer, boolean, foreignKey } from 'drizzle-orm/pg-core';
import { users } from './users';

export const posts = pgTable('posts', {
  id: serial('id').primaryKey(),
  title: varchar('title', { length: 255 }).notNull(),
  slug: varchar('slug', { length: 255 }).notNull().unique(),
  content: text('content').notNull(),
  excerpt: text('excerpt'),
  authorId: integer('author_id')
    .references(() => users.id)
    .notNull(),
  published: boolean('published').default(false).notNull(),
  publishedAt: timestamp('published_at'),
  createdAt: timestamp('created_at').defaultNow().notNull(),
  updatedAt: timestamp('updated_at').defaultNow().notNull(),
});
```

### 关系定义

```typescript
import { relations } from 'drizzle-orm';

export const usersRelations = relations(users, ({ many }) => ({
  posts: many(posts),
}));

export const postsRelations = relations(posts, ({ one }) => ({
  author: one(users, {
    fields: [posts.authorId],
    references: [users.id],
  }),
}));
```

## 查询示例

### Select查询

```typescript
import { db } from './db';
import { users, posts } from './schema';

// 查询所有用户
const allUsers = await db.select().from(users);

// 带条件查询
const activeUsers = await db
  .select()
  .from(users)
  .where(eq(users.emailVerified, true));

// 查询带关系
const usersWithPosts = await db.query.users.findMany({
  with: {
    posts: {
      where: eq(posts.published, true),
    },
  },
  orderBy: desc(users.createdAt),
});
```

### Insert操作

```typescript
// 单条插入
await db.insert(users).values({
  name: 'John Doe',
  email: 'john@example.com',
  passwordHash: await hash('password'),
});

// 批量插入
await db.insert(posts).values([
  { title: 'Post 1', slug: 'post-1', content: '...', authorId: 1 },
  { title: 'Post 2', slug: 'post-2', content: '...', authorId: 1 },
]);
```

### Update操作

```typescript
// 更新单条
await db
  .update(users)
  .set({ emailVerified: true, updatedAt: new Date() })
  .where(eq(users.id, 1));

// 带返回值的更新
const [updated] = await db
  .update(posts)
  .set({ published: true, publishedAt: new Date() })
  .where(eq(posts.slug, 'my-post'))
  .returning();
```

### Delete操作

```typescript
await db.delete(posts).where(eq(posts.id, 1));
```

## 天龙集成模式

### 模式1：工作流持久化

```typescript
// 天龙工作流状态持久化
import { pgTable, serial, text, jsonb, timestamp, varchar } from 'drizzle-orm/pg-core';

export const workflowRuns = pgTable('workflow_runs', {
  id: serial('id').primaryKey(),
  workflowId: varchar('workflow_id', { length: 255 }).notNull(),
  status: varchar('status', { length: 50 }).notNull(), // running, completed, failed
  input: jsonb('input').notNull(),
  output: jsonb('output'),
  error: text('error'),
  startedAt: timestamp('started_at').defaultNow().notNull(),
  completedAt: timestamp('completed_at'),
});

// 任务持久化
export const workflowTasks = pgTable('workflow_tasks', {
  id: serial('id').primaryKey(),
  runId: integer('run_id')
    .references(() => workflowRuns.id)
    .notNull(),
  taskId: varchar('task_id', { length: 255 }).notNull(),
  status: varchar('status', { length: 50 }).notNull(),
  result: jsonb('result'),
  createdAt: timestamp('created_at').defaultNow().notNull(),
});
```

### 模式2：Agent记忆存储

```typescript
// AI Agent记忆持久化
export const agentMemories = pgTable('agent_memories', {
  id: serial('id').primaryKey(),
  agentId: varchar('agent_id', { length: 255 }).notNull(),
  memoryType: varchar('memory_type', { length: 50 }).notNull(), // short, long, episodic
  content: text('content').notNull(),
  embedding: vector('embedding', { dimensions: 1536 }), // pgvector
  importance: integer('importance').default(5),
  metadata: jsonb('metadata'),
  createdAt: timestamp('created_at').defaultNow().notNull(),
  expiresAt: timestamp('expires_at'),
});
```

## 与现有天龙能力协同

| 天龙组件 | Drizzle ORM | 协同效果 |
|---------|------------|---------|
| **database-migrations** | expand-contract → Drizzle Kit | 手动→CLI自动化 |
| **simstudio-api** | 工作流持久化 | 状态存储 |
| **claude-mem** | 向量存储 | Agent记忆向量检索 |
| **paperclip-ticket** | 任务持久化 | 工单数据库 |

## Drizzle Kit配置

```typescript
// drizzle.config.ts
import { defineConfig } from 'drizzle-kit';

export default defineConfig({
  schema: './src/db/schema.ts',
  out: './drizzle',
  dialect: 'postgresql',
  dbCredentials: {
    url: process.env.DATABASE_URL!,
  },
  verbose: true,
  strict: true,
});
```

## 预期收益

| 指标 | V8.71 | V8.72 | 提升 |
|------|-------|-------|------|
| **Schema类型安全** | 手动SQL | 代码化+TypeScript | **质的飞跃** |
| **迁移效率** | 手动编写 | CLI自动生成 | **+200%** |
| **多数据库支持** | 有限 | 20+ | **+500%** |
| **Query构建** | 原始SQL | 链式API | **+150%** |
| **包大小** | ORM框架 | **~7.4kb** | **轻量级** |

## 技能文件

- [skills/drizzle-orm/SKILL.md](skills/drizzle-orm/SKILL.md)
- [skills/drizzle-orm/scripts/drizzle_client.ts](skills/drizzle-orm/scripts/drizzle_client.ts)
- [skills/drizzle-orm/templates/schema.ts](skills/drizzle-orm/templates/schema.ts)
