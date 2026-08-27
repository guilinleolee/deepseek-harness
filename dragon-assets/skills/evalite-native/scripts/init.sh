#!/bin/bash
# Evalite Native 初始化脚本

set -e

echo "🚀 初始化 Evalite Native..."

# 检查 Node.js 版本
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
  echo "❌ Node.js 18+ required, current: $(node -v)"
  exit 1
fi

# 创建项目目录
PROJECT_DIR="${1:-./eval-project}"
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

# 初始化 package.json
if [ ! -f "package.json" ]; then
  echo "📦 创建 package.json..."
  cat > package.json << 'EOF'
{
  "name": "eval-project",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "eval": "evalite",
    "eval:watch": "evalite --watch"
  },
  "devDependencies": {
    "evalite": "latest",
    "@evalite/vitest": "latest",
    "vitest": "latest",
    "typescript": "latest",
    "tsx": "latest"
  }
}
EOF
fi

# 安装依赖
echo "📥 安装依赖..."
npm install

# 创建配置文件
if [ ! -f "evalite.config.ts" ]; then
  echo "⚙️ 创建 evalite.config.ts..."
  cat > evalite.config.ts << 'EOF'
import { defineConfig } from "evalite";
import { openai } from "ai";
import { anthropic } from "@ai-sdk/anthropic";

export default defineConfig({
  // 模型配置
  models: {
    gpt4: openai("gpt-4"),
    claude: anthropic("claude-3-sonnet-20240229"),
  },

  // 评分阈值 (0-1)
  threshold: 0.8,

  // 试验次数
  trials: 3,

  // 输出格式: table | json
  output: "table",
});
EOF
fi

# 创建评估目录
mkdir -p evals

# 创建示例评估
if [ ! -f "evals/example.test.ts" ]; then
  echo "📝 创建示例评估文件..."
  cat > evals/example.test.ts << 'EOF'
import { ev } from "evalite";
import { openai } from "ai";

const model = openai("gpt-4o");

ev("基础问答测试", async () => {
  const result = await model.chat.completions.create({
    messages: [
      { role: "user", content: "法国的首都是什么?" }
    ],
    model: "gpt-4o",
  });

  const answer = result.choices[0].message.content || "";

  return {
    // 简单 pass/fail
    pass: answer.includes("巴黎"),
    // 或使用评分 (0-1)
    score: answer.includes("巴黎") ? 1 : 0,
  };
});
EOF
fi

# 创建 vitest 配置
if [ ! -f "vitest.config.ts" ]; then
  echo "🔧 创建 vitest.config.ts..."
  cat > vitest.config.ts << 'EOF'
import { defineConfig } from "vitest/config";
import Evalite from "@evalite/vitest";

export default defineConfig({
  plugins: [Evalite()],
  test: {
    reporters: ["default", "evalite"],
  },
});
EOF
fi

# 创建 TypeScript 配置
if [ ! -f "tsconfig.json" ]; then
  echo "📄 创建 tsconfig.json..."
  cat > tsconfig.json << 'EOF'
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "types": ["vitest/globals"]
  },
  "include": ["**/*.ts"],
  "exclude": ["node_modules"]
}
EOF
fi

# 创建 README
cat > README.md << 'EOF'
# Evalite Native 评估项目

## 快速开始

```bash
# 运行评估
npm run eval

# 观看模式
npm run eval:watch
```

## 添加新评估

在 `evals/` 目录下创建新的 `.test.ts` 文件:

```typescript
import { ev } from "evalite";

ev("评估名称", async () => {
  // 你的测试逻辑
  return {
    pass: result === expected,
    score: similarity(result, expected),
  };
});
```
EOF

echo "✅ Evalite Native 初始化完成!"
echo ""
echo "📌 下一步:"
echo "   1. 编辑 evalite.config.ts 配置你的模型"
echo "   2. 在 evals/ 目录下添加评估用例"
echo "   3. 运行 npm run eval 执行评估"
