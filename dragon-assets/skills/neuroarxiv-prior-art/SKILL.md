# NeuroArxiv Prior Art Skill

> **来源**: [UditAkhourii/neuroarxiv](https://github.com/UditAkhourii/neuroarxiv)
> **版本**: V1.0
> **核心理念**: 在Claude设计新架构前，先检查arXiv真实论文Prior Art

---

## L0: 一句话描述 (≤15字)

**arXiv Prior Art检查 - 强制收敛推荐**

---

## L1: 使用场景 (50-100字)

**适用场景**：
- 架构设计前检查arXiv论文Prior Art
- 技术选型时了解已知失败案例
- 调研报告新增"风险告知"机制
- 收敛决策（强制推荐一个方案 + 已知风险）

**触发关键词**：`/prior-art`、`neuroarxiv`、`arXiv先验`、`先查论文`

---

## L2: 详细文档

### 核心能力矩阵

| 能力 | 说明 |
|------|------|
| arXiv专项搜索 | 按分类+关键词搜索真实论文 |
| 隔离阅读 | 每篇论文独立评估，不互相影响 |
| 聚类分析 | 按架构角度分组 |
| 收敛决策 | 强制推荐一个方案 + 已知风险 |
| Source-Skepticism | 标记论文局限性和已知失败 |

---

### 工作流程（Isolate-Then-Converge）

```
PROBLEM
  ↓
0. CATEGORIZE  — 映射到3-5个arXiv分类 + 关键词
  ↓
1. FETCH       — 真实HTTP请求获取论文摘要（确定性）
  ↓
2. DIVERGE     — 每篇论文隔离阅读（不互相影响）
  ↓
3. SCORE       — 评分：相关性/实用性/严谨性
   + CLUSTER   — 按架构角度分组
  ↓
4. CONVERGE    — 强制选择1个推荐 + 说明原因 + 已知风险
```

---

### 与普通调研的区别

| 对比维度 | 普通调研 | **NeuroArxiv** |
|----------|---------|----------------|
| 信息收集 | 收集所有信息 | 每条信息独立评估 |
| 决策方式 | "A/B/C方案，您选" | "我推荐A，因为..." |
| 风险告知 | 可选补充 | **强制包含** |
| 引用质量 | 可能有幻觉 | 真实arXiv论文ID |
| 已知失败 | 不提及 | **必须标记** |

---

### Source-Skepticism效果

| 对比维度 | 冷启动 | Web+arXiv搜索 | **NeuroArxiv** |
|----------|--------|--------------|----------------|
| 引用论文时标记风险 | 0/5 | 0/5 | **5/5** |
| 发现论文已撤回 | ❌ | ❌ | **✅** |
| 标记局限性 | ❌ | ❌ | **✅** |

---

### 使用命令

```bash
# 基础搜索
neuroarxiv "缓存一致性方案"
neuroarxiv "微服务架构选型" --papers 6

# Claude Code内使用
/neuroarxiv "分布式锁实现方案"
/prior-art "多Agent协作框架"
```

---

### 输出格式

```markdown
## NeuroArxiv Prior Art 分析

### 推荐方案：XXX架构

**置信度**：高（80%+）

**推荐理由**（来自arXiv论文验证）：
1. 论文[arXiv:xxxx.xxxx]证明：...
2. 论文[arXiv:xxxx.xxxx]指出：...

### ⚠️ 已知失败案例

| 论文 | 失败场景 | 原因 |
|------|---------|------|
| arXiv:xxxx | 高并发锁竞争 | 粗粒度锁瓶颈 |
| arXiv:yyyy | 分布式一致性问题 | 网络分区处理不当 |

### 📋 风险缓解建议

- 针对锁竞争：建议使用细粒度锁
- 针对一致性问题：建议使用最终一致性模型

### ⚠️ 用户可选择不采纳，但需要说明原因
```

---

## 安装方式

```bash
# 方式1: npx安装（推荐）
npx github:UditAkhourii/neuroarxiv install

# 方式2: 手动克隆
git clone https://github.com/UditAkhourii/neuroarxiv.git
cd neuroarxiv && npm install && npm run build

# 验证安装
neuroarxiv --help
```

---

## API调用示例

```javascript
// Node.js调用
const { neuroarxiv } = require('neuroarxiv');

// 搜索Prior Art
const result = await neuroarxiv.search({
  query: 'distributed cache consistency',
  papers: 6,
  categories: ['cs.DC', 'cs.NI']
});

console.log(result.recommendation);
console.log(result.known_failures);
```

---

## 注意事项

1. **速率限制**：arXiv API限制1秒1请求
2. **论文质量**：arXiv论文未经严格同行评审，需批判性使用
3. **收敛决策**：必须输出一个推荐，不可"给选项让用户选"
4. **风险告知**：必须包含已知失败案例

---

## 与天龙引擎协同

| 天龙组件 | 协同方式 |
|---------|---------|
| 01调研师 | Prior Art检查嵌入调研流程 |
| 02架构师 | 收敛决策模式增强Battle图 |
| 10-02 AI研究员 | arXiv论文质量评估 |
| deep-research | Prior Art作为L1资料源 |

---

**版本**: V1.0
**来源**: UditAkhourii/neuroarxiv
**集成日期**: 2026-08-18
