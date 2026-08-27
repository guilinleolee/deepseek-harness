---
license: UNKNOWN
github_repo: code-yeongyu/oh-my-openagent
github_hash: 48b0cfeaf54b19beca3c29d501c58c05d5515d2d
last_updated: 2026-04-25
source_type: derived
triggers: ["hash anchored edit", "Hash-Anchored Edit - 基于哈希的稳定编辑"]
---
# Hash-Anchored Edit - 基于哈希的稳定编辑

> 基于内容哈希的稳定编辑系统，防止上下文不匹配导致的编辑错误，编辑稳定性+10%

## 触发词

`/hash-read`, `/hash-edit`, `/hash-verify`, `/hash-diff`, `哈希编辑`, `锚点编辑`

## 功能

### 1. 读取文件并显示锚点
```
/hash-read src/app.ts
```
输出格式：`LINE#HASH| content`

### 2. 使用锚点编辑
```
/hash-edit src/app.ts "8#H4" "  res.json({ message: 'Hello' });"
```
验证哈希匹配后才执行编辑

### 3. 验证文件锚点
```
/hash-verify src/app.ts
```

### 4. 对比文件变更
```
/hash-diff src/app.ts
```

## 核心机制

```
1. 读取文件时为每行添加哈希锚点 (LINE#HASH)
2. 编辑时验证哈希是否匹配
3. 不匹配则拒绝编辑，防止代码损坏
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

## 来源

> [oh-my-openagent](https://github.com/code-yeongyu/oh-my-openagent) - Hash-Anchored Edit