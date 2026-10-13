---
license: UNKNOWN
github_repo: camel-ai/oasis
github_hash: e88662fd3928f0dd7cc6fe919eea4c6b484aa6d3
last_updated: 2026-04-25
source_type: derived
triggers: ["swarm intelligence", "Swarm Intelligence Skill"]
---
# Swarm Intelligence Skill

> 群体智能推演引擎 - 基于 MiroFish + OASIS

## 核心价值

填补天龙引擎在**群体智能推演**和**预测引擎**两大核心能力的空白。

| 能力 | 说明 | 应用场景 |
|------|------|---------|
| **多Agent仿真** | 100万级Agent并行仿真 | 社交媒体模拟、舆情推演 |
| **平行推演** | 种子信息驱动 + 变量注入 | 市场预测、事件发展推演 |
| **GraphRAG** | 实体关系抽取 + 人设生成 | 知识图谱构建、角色建模 |
| **ReportAgent** | 深度交互 + 时序记忆 | 报告生成、趋势分析 |

## 技术来源

- **MiroFish** (18k Stars): https://github.com/666ghj/MiroFish
- **OASIS** (CAMEL-AI): https://github.com/camel-ai/oasis

## 依赖要求

```yaml
Python: 3.11-3.12
Node.js: 18+
LLM API: OpenAI SDK格式（推荐阿里百炼qwen-plus）
记忆管理: Zep Cloud（可选）
部署: Docker Compose
```

## 安装方式

### 方式1: Docker部署（推荐）

```bash
# 克隆项目
git clone https://github.com/666ghj/MiroFish.git
cd MiroFish

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入 API Keys

# 启动服务
docker-compose up -d

# 访问前端
open http://localhost:8080
```

### 方式2: 源码部署

```bash
# 后端
cd backend
pip install -r requirements.txt
python main.py

# 前端
cd frontend
npm install
npm run dev
```

## 核心命令

### 舆情推演

```bash
# 推演舆情事件发展
/swarm-predict --type sentiment --seed "武汉大学事件" --steps 10

# 输出：事件发展路径、关键节点、影响范围
```

### 市场预测

```bash
# 预测市场趋势
/swarm-predict --type market --seed "AI芯片市场" --variables "政策,技术,竞争"

# 输出：市场走向、关键因素、风险点
```

### 社交媒体仿真

```bash
# 仿真社交平台传播
/swarm-simulate --platform twitter --agents 10000 --seed "产品发布"

# 输出：传播路径、关键KOL、舆情分布
```

### 知识图谱构建

```bash
# 从文本构建图谱
/swarm-graph --input article.md --output graph.json

# 输出：实体关系图、人设卡片、事件时间线
```

## API接口

### Python调用

```python
from swarm_intelligence import SwarmEngine

# 初始化引擎
engine = SwarmEngine(
    llm_api="your_api_key",
    model="qwen-plus"
)

# 创建仿真环境
env = engine.create_environment(
    name="市场预测",
    agents=1000,
    platform="twitter"
)

# 注入种子信息
env.inject_seed("新产品发布消息")

# 运行推演
result = env.run(steps=10)

# 获取报告
report = engine.generate_report(result)
```

### REST API

```bash
# 创建推演任务
curl -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "type": "sentiment",
    "seed": "武汉大学事件",
    "steps": 10,
    "variables": ["媒体", "公众", "官方"]
  }'

# 获取推演结果
curl http://localhost:8000/api/predict/{task_id}/result
```

## 四大核心模块

### 1. GraphRAG图谱构建

```yaml
功能:
  - 实体关系抽取
  - 人设自动生成
  - 知识图谱可视化

输入: 文本/URL/文档
输出: 实体关系图 + 人设卡片
```

### 2. 多智能体仿真

```yaml
功能:
  - 100万Agent并行
  - 23种行为动作（点赞/评论/关注/搜索等）
  - 动态环境适应

参数:
  - agents: Agent数量
  - platform: 平台类型（twitter/reddit/weibo）
  - duration: 仿真时长
```

### 3. 平行推演预测

```yaml
功能:
  - 种子信息驱动
  - 上帝视角变量注入
  - 多路径推演

参数:
  - seed: 种子信息
  - variables: 变量列表
  - steps: 推演步数
```

### 4. ReportAgent报告

```yaml
功能:
  - 深度交互分析
  - 时序记忆更新
  - 可视化报告生成

输出:
  - 趋势分析
  - 关键节点
  - 风险预警
```

## 应用场景

### 舆情监控

```
输入: 热点事件
处理: 多Agent仿真传播
输出: 舆情发展预测 + 应对建议
```

### 市场研究

```
输入: 行业/产品
处理: 平行推演
输出: 市场趋势预测 + 竞争分析
```

### 内容创作

```
输入: 故事大纲
处理: 角色仿真
输出: 情节发展预测 + 结局推演
```

### 金融预测

```
输入: 市场/政策
处理: 多因素推演
输出: 走势预测 + 风险评估
```

## 与天龙引擎协同

| 天龙岗位 | 协同方式 | 收益 |
|----------|---------|------|
| **32-01 市场研究** | 舆情推演 + 市场预测 | 预测能力质的飞跃 |
| **35-02 社媒运营** | 社交媒体仿真 | 运营策略优化 |
| **62-02 行业研究员** | 行业趋势推演 | 研究深度提升 |
| **00 分析师** | 群体智能分析 | 分析维度扩展 |
| **02 架构师** | 多Agent架构设计 | 系统设计能力提升 |

## 配置文件

### swarm-config.yaml

```yaml
# LLM配置
llm:
  provider: openai  # openai/azure/alibaba
  model: qwen-plus
  api_key: ${OPENAI_API_KEY}

# 仿真配置
simulation:
  max_agents: 1000000
  default_platform: twitter
  steps_per_run: 10

# 记忆配置
memory:
  provider: zep  # zep/local
  zep_api_key: ${ZEP_API_KEY}

# 推演配置
prediction:
  parallel_paths: 3
  confidence_threshold: 0.7
```

## 预期收益

| 指标 | 集成前 | 集成后 | 提升 |
|------|--------|--------|------|
| **预测推演能力** | 无 | 完整 | 质的飞跃 |
| **群体智能仿真** | 无 | 100万Agent | 质的飞跃 |
| **舆情分析深度** | 评论分析 | 推演预测 | +300% |
| **市场研究精度** | 数据驱动 | 推演驱动 | +200% |

## 版本历史

| 版本 | 日期 | 更新 |
|------|------|------|
| V1.0 | 2026-03-13 | 初始版本，集成MiroFish核心能力 |

## 参考资料

- [MiroFish GitHub](https://github.com/666ghj/MiroFish)
- [OASIS Paper](https://arxiv.org/abs/2408.07513)
- [CAMEL-AI](https://github.com/camel-ai/camel)