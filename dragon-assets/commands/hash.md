---
name: hash
description: hash - 天龙Hash-Anchored Edit命令
invokable: true
---
# /hash - 天龙Hash-Anchored Edit命令

基于内容哈希的稳定编辑系统，防止上下文不匹配导致的编辑错误。

## 使用方式

```bash
/hash-read <file>                    # 读取文件并显示Hash锚点
/hash-edit <file> <anchor> <content> # 使用锚点编辑
/hash-verify <file>                  # 验证文件锚点
/hash-diff <file>                    # 对比当前文件与锚点
```

## 功能说明

### 1. 读取文件并显示锚点

```bash
/hash-read src/app.ts
```

**输出示例**:
```
📄 src/app.ts (Hash-Anchored View)
==================================================

 1#A3| import express from 'express';
 2#B7| import { config } from './config';
 3#C2|
 4#D9| const app = express();
 5#E1| const PORT = process.env.PORT || 3000;
 6#F5|
 7#G8| app.get('/', (req, res) => {
 8#H4|   res.send('Hello World');
 9#I6| });
10#J2|
11#K7| app.listen(PORT, () => {
12#L3|   console.log(`Server running on port ${PORT}`);
13#M9| });

==================================================
Anchors: 13 lines, Hash algorithm: FNV-1a (2-char)
```

### 2. 使用锚点编辑

```bash
/hash-edit src/app.ts "8#H4" "  res.json({ message: 'Hello World' });"
```

**工作流程**:
```
1. 解析锚点: line=8, expected_hash=H4
2. 读取当前第8行内容
3. 计算实际哈希
4. 对比: H4 == H4 ✅
5. 执行编辑
```

**哈希不匹配时**:
```
❌ Hash mismatch for anchor "8#H4"
   Expected: H4
   Actual: X9
   The file may have changed since last read.
   Please run /hash-read to get updated anchors.
```

### 3. 验证文件锚点

```bash
/hash-verify src/app.ts
```

**输出示例**:
```
✅ src/app.ts - All anchors valid
   13 lines verified, 0 mismatches
```

### 4. 对比文件变更

```bash
/hash-diff src/app.ts
```

**输出示例**:
```
📊 src/app.ts - Change Detection
==================================================

Changed lines:
  5#E1 → 5#X7  (content changed)
    - const PORT = process.env.PORT || 3000;
    + const PORT = config.port || 3000;

Added lines:
  14#N2 (new line)

Removed lines:
  (none)

==================================================
Summary: 1 changed, 1 added, 0 removed
```

## Hash锚点格式

```
LINE#HASH

LINE:  行号（1-based）
HASH:  内容哈希（2-3字符，FNV-1a算法）

示例:
  11#VK    → 第11行，哈希VK
  42#A3B   → 第42行，哈希A3B
```

## 哈希算法

```typescript
// FNV-1a 简化版（2字符输出）
function computeHash(content: string): string {
  const trimmed = content.trim();
  let hash = 2166136261; // FNV offset basis

  for (let i = 0; i < trimmed.length && i < 50; i++) {
    hash ^= trimmed.charCodeAt(i);
    hash = (hash * 16777619) >>> 0; // FNV prime
  }

  // 转换为36进制（0-9, A-Z），取前2-3字符
  return (hash % 46656).toString(36).toUpperCase().padStart(2, '0');
}
```

## 为什么需要Hash-Anchored Edit？

### 问题：传统行号编辑

```
场景: Agent读取文件，计划编辑第8行

问题:
1. 其他Agent同时编辑了第5行（插入新代码）
2. 原第8行变成第9行
3. Agent编辑错误的位置！

结果: 代码损坏，需要人工修复
```

### 解决：Hash-Anchored Edit

```
场景: Agent读取文件，计划编辑锚点 "8#H4"

过程:
1. 其他Agent编辑了第5行（文件变化）
2. Agent尝试编辑 "8#H4"
3. 系统计算第8行当前哈希: X9
4. H4 ≠ X9 → 编辑被拒绝
5. Agent收到错误，重新读取文件

结果: 编辑安全，无代码损坏
```

## 效果对比

| 模型 | 无Hash-Anchored | 有Hash-Anchored | 提升 |
|------|----------------|-----------------|------|
| Grok Code Fast 1 | 6.7% | 68.3% | **+61.6%** |
| Claude Sonnet | ~85% | ~95% | **+10%** |

## 天龙岗位映射

| 岗位 | 用途 |
|------|------|
| **03构建师** | 精确代码编辑 |
| **06审查师** | 安全代码修改 |
| **04验证师** | 编辑验证 |

## 与Agent Booster协同

```
Agent Booster: 速度优化 (352x加速)
Hash-Anchored: 准确性优化 (编辑成功率+10%)

协同效果:
  快速 + 准确 = 高效可靠的代码编辑

工作流:
1. /hash-read 获取锚点
2. /booster edit 使用锚点编辑（内部调用hash验证）
3. /hash-verify 确认编辑正确
```

## 配置选项

```json
// .claude/hash-config.json
{
  "hashAlgorithm": "fnv1a",
  "hashLength": 2,
  "maxLineLength": 50,
  "enableAutoVerification": true
}
```

## 来源

> [oh-my-openagent](https://github.com/code-yeongyu/oh-my-openagent) - Hash-Anchored Edit
> [oh-my-pi](https://github.com/can1357/oh-my-pi) - 原始灵感
> 集成方案: [analysis/OH-MY-OPENAGENT-P1-INTEGRATION-PLAN.md](analysis/OH-MY-OPENAGENT-P1-INTEGRATION-PLAN.md)