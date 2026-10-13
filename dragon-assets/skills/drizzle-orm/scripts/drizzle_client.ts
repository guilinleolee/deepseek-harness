#!/usr/bin/env python3
"""
Drizzle ORM Client - 天龙引擎数据库ORM集成
提供TypeScript Schema生成和迁移管理
"""

import json
import subprocess
from dataclasses import dataclass
from typing import Optional, List, Dict, Any


@dataclass
class DrizzleConfig:
    """Drizzle配置"""
    schema_path: str = "./src/db/schema.ts"
    output_path: str = "./drizzle"
    dialect: str = "postgresql"
    database_url: str = ""


class DrizzleClient:
    """Drizzle ORM客户端"""

    def __init__(self, config: Optional[DrizzleConfig] = None):
        self.config = config or DrizzleConfig()

    def generate(self) -> Dict[str, Any]:
        """生成迁移文件"""
        cmd = [
            "npx", "drizzle-kit", "generate",
            "--config", self.config.schema_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }

    def migrate(self) -> Dict[str, Any]:
        """应用迁移"""
        cmd = [
            "npx", "drizzle-kit", "migrate",
            "--config", self.config.schema_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }

    def push(self) -> Dict[str, Any]:
        """推送schema（开发模式）"""
        cmd = [
            "npx", "drizzle-kit", "push",
            "--config", self.config.schema_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }

    def studio(self) -> subprocess.Popen:
        """启动Drizzle Studio"""
        cmd = [
            "npx", "drizzle-kit", "studio",
            "--config", self.config.schema_path
        ]
        return subprocess.Popen(cmd)

    def check(self) -> Dict[str, Any]:
        """检查迁移状态"""
        cmd = [
            "npx", "drizzle-kit", "check",
            "--config", self.config.schema_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }


class SchemaGenerator:
    """Schema生成器"""

    @staticmethod
    def generate_users_table() -> str:
        """生成用户表Schema"""
        return '''
// 用户表
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
'''

    @staticmethod
    def generate_posts_table() -> str:
        """生成文章表Schema"""
        return '''
// 文章表
import { pgTable, serial, text, varchar, timestamp, integer, boolean } from 'drizzle-orm/pg-core';
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
'''

    @staticmethod
    def generate_workflow_runs_table() -> str:
        """生成工作流运行表（天龙引擎集成）"""
        return '''
// 工作流运行表
import { pgTable, serial, text, varchar, timestamp, jsonb } from 'drizzle-orm/pg-core';

export const workflowRuns = pgTable('workflow_runs', {
  id: serial('id').primaryKey(),
  workflowId: varchar('workflow_id', { length: 255 }).notNull(),
  status: varchar('status', { length: 50 }).notNull(), // running, completed, failed
  input: jsonb('input').notNull(),
  output: jsonb('output'),
  error: text('error'),
  startedAt: timestamp('started_at').defaultNow().notNull(),
  completedAt: timestamp('completed_at'),
  createdAt: timestamp('created_at').defaultNow().notNull(),
  updatedAt: timestamp('updated_at').defaultNow().notNull(),
});
'''

    @staticmethod
    def generate_agent_memories_table() -> str:
        """生成Agent记忆表（天龙引擎集成）"""
        return '''
// AI Agent记忆表
import { pgTable, serial, text, varchar, timestamp, jsonb, integer } from 'drizzle-orm/pg-core';

export const agentMemories = pgTable('agent_memories', {
  id: serial('id').primaryKey(),
  agentId: varchar('agent_id', { length: 255 }).notNull(),
  sessionId: varchar('session_id', { length: 255 }).notNull(),
  memoryType: varchar('memory_type', { length: 50 }).notNull(), // short, long, episodic
  content: text('content').notNull(),
  importance: integer('importance').default(5),
  metadata: jsonb('metadata'),
  createdAt: timestamp('created_at').defaultNow().notNull(),
  expiresAt: timestamp('expires_at'),
});
'''


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description="Drizzle ORM Client")
    parser.add_argument("action", choices=["generate", "migrate", "push", "check", "studio", "schema"], help="操作")
    parser.add_argument("--config", help="配置文件路径")
    parser.add_argument("--schema-type", choices=["users", "posts", "workflow", "memories"], help="Schema类型")

    args = parser.parse_args()
    client = DrizzleClient()

    if args.action == "generate":
        result = client.generate()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.action == "migrate":
        result = client.migrate()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.action == "push":
        result = client.push()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.action == "check":
        result = client.check()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.action == "studio":
        print("Starting Drizzle Studio...")
        client.studio()
    elif args.action == "schema":
        gen = SchemaGenerator()
        if args.schema_type == "users":
            print(gen.generate_users_table())
        elif args.schema_type == "posts":
            print(gen.generate_posts_table())
        elif args.schema_type == "workflow":
            print(gen.generate_workflow_runs_table())
        elif args.schema_type == "memories":
            print(gen.generate_agent_memories_table())


if __name__ == "__main__":
    main()
