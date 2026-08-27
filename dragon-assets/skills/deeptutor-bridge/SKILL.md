---
license: UNKNOWN
github_repo: HKUDS/DeepTutor
github_hash: e8a569a61856c74210d8fb7a406c5483b4a6d291
triggers: ["deeptutor bridge", "DeepTutor Bridge - DeepTutor AI学习后端桥接"]
---
# DeepTutor Bridge - DeepTutor AI学习后端桥接

## L0: 一句话 (≤15字)
调用DeepTutor后端实现深度学习辅导

## L1: 使用场景 (50-100字)

### 触发词
- 深度求解 / 详细解题
- 研究一下 / 深入研究
- 帮我做练习 / 生成测验
- 动画解释 / 可视化学习

### 适用场景
- 需要深度推理解题
- 生成个性化练习题
- 上传PDF/文档构建知识库
- 数学概念动画演示
- 多渠道学习（配合Telegram等）

### 不适用
- 简单快速问答（直接回答更快）
- 没有安装DeepTutor后端
- 需要实时交互的场景

## L2: 详细文档

### 前置条件

```bash
# 1. 安装DeepTutor后端
git clone https://github.com/HKUDS/DeepTutor.git
cd DeepTutor

# 2. 创建conda环境
conda create -n deeptutor python=3.11
conda activate deeptutor

# 3. 安装
pip install -e ".[server]"

# 4. 配置
cp .env.example .env
# 编辑.env设置LLM和Embedding

# 5. 启动后端（端口8001）
python -m deeptutor.api.run_server

# 6. 或仅安装CLI
pip install -e ".[cli]"
```

### 核心能力

```python
class DeepTutorBridge(dspy.Signature):
    """DeepTutor API桥接"""
    mode: str = dspy.InputField(
        desc="模式: chat/deep_solve/quiz/deep_research/math",
        prefix="模式"
    )
    query: str = dspy.InputField(desc="查询内容")
    kb_name: str = dspy.InputField(
        desc="知识库名称(chat模式)",
        default=""
    )
    config: dict = dspy.InputField(
        desc="额外配置",
        default={}
    )

    response: str = dspy.OutputField(desc="DeepTutor响应")
    sources: list = dspy.OutputField(desc="引用来源")
    session_id: str = dspy.OutputField(desc="会话ID")


class KnowledgeHubManager(dspy.Signature):
    """Knowledge Hub知识库管理"""
    action: str = dspy.InputField(
        desc="操作: create/list/add/search/delete",
        prefix="操作"
    )
    kb_name: str = dspy.InputField(desc="知识库名称")
    documents: list = dspy.InputField(
        desc="文档路径列表",
        default=[]
    )

    result: str = dspy.OutputField(desc="执行结果")
    kb_info: dict = dspy.OutputField(desc="知识库信息")


class TutorBotManager(dspy.Signature):
    """TutorBot导师管理"""
    action: str = dspy.InputField(
        desc="操作: create/list/switch/delete",
        prefix="操作"
    )
    bot_name: str = dspy.InputField(desc="Bot名称")
    persona: str = dspy.InputField(
        desc="人格描述",
        default=""
    )

    result: str = dspy.OutputField(desc="执行结果")
    bot_info: dict = dspy.OutputField(desc="Bot信息")
```

### DeepTutor五种模式

| 模式 | 命令 | 功能 | 学习师调用 |
|------|------|------|----------|
| **Chat** | `chat` | RAG问答式辅导 | 资料问答 |
| **Deep Solve** | `deep_solve` | 深度推理解题 | 难题讲解 |
| **Quiz Generation** | `quiz` | 生成练习测验 | 巩固练习 |
| **Deep Research** | `deep_research` | 主题深度研究 | 延伸学习 |
| **Math Animator** | `math` | 数学动画可视化 | 直观理解 |

### 使用示例

```bash
# ===== CLI命令（通过pip安装的deeptutor）=====

# Chat模式 - RAG知识库问答
deeptutor run chat "什么是注意力机制？" -t rag --kb my-kb

# Deep Solve - 深度解题
deeptutor run deep_solve "证明罗尔定理"

# Quiz - 生成练习
deeptutor run quiz "线性代数" --num 10 --difficulty medium

# Deep Research - 深度研究
deeptutor run deep_research "Transformer架构的演进"

# Math - 数学动画
deeptutor run math "泰勒展开" --animate

# ===== 知识库管理 =====
deeptutor kb create machine-learning
deeptutor kb add machine-learning --docs ./papers/
deeptutor kb list
deeptutor kb search machine-learning "梯度下降"
deeptutor kb delete old-kb

# ===== TutorBot管理 =====
deeptutor bot create math-tutor --persona "苏格拉底式数学导师"
deeptutor bot list
deeptutor bot switch math-tutor
deeptutor bot delete unused-bot

# ===== 会话管理 =====
deeptutor session list
deeptutor session open <session_id>
deeptutor session export <session_id> --format markdown
```

### Python API

```python
from deeptutor_bridge import DeepTutorBridge, KnowledgeHub, TutorBot

# 初始化桥接
bridge = DeepTutorBridge(base_url="http://localhost:8001")

# 1. Chat模式 - RAG问答
result = bridge.chat(
    query="解释反向传播算法的工作原理",
    kb_name="deep-learning"
)
print(f"回答: {result.response}")
print(f"来源: {result.sources}")

# 2. Deep Solve - 深度解题
result = bridge.deep_solve(
    query="用梯度下降法求解 y = x^4 - 3x^3 + 2 的最小值"
)
print(f"解题步骤: {result.response}")

# 3. Quiz - 生成测验
result = bridge.quiz(
    topic="微积分",
    num_questions=5,
    difficulty="medium",
    question_types=["multiple_choice", "short_answer"]
)
print(f"测验题: {result.response}")

# 4. Deep Research - 深度研究
result = bridge.deep_research(
    topic="大语言模型中的位置编码",
    depth="comprehensive"
)
print(f"研究报告: {result.response}")

# 5. Math Animation - 数学动画
result = bridge.math_animation(
    concept="傅里叶变换",
    animate=True
)
print(f"动画脚本: {result.response}")
```

### 与天龙引擎集成

```yaml
天龙引擎集成:
  学习师工作流:
    诊断阶段:
      - 检索DeepTutor知识库 → 了解用户已有知识
      - 会话历史 → 了解学习进度

    学习阶段:
      - Deep Solve → 深度推理解题
      - Math Animator → 数学可视化
      - Deep Research → 延伸学习

    巩固阶段:
      - Quiz Generation → 生成练习题
      - 记录到会话 → 持久化记忆

  Obsidian协同:
    - DeepTutor知识库 → Obsidian笔记
    - Obsidian笔记 → DeepTutor索引

  NotebookLM协同:
    - NotebookLM摘要 → DeepTutor
    - DeepTutor研究 → NotebookLM归档
```

### 配置选项

```yaml
# .env 配置示例
LLM_BINDING=openai
LLM_MODEL=gpt-4o-mini
LLM_API_KEY=sk-xxx
LLM_HOST=https://api.openai.com/v1

# 或使用免费MiniMax
LLM_BINDING=minimax
LLM_MODEL=MiniMax-M2
LLM_API_KEY=your-minimax-key
LLM_HOST=https://api.minimax.chat/v1

EMBEDDING_BINDING=openai
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSION=1536
```

### 服务端口

| 服务 | 默认端口 | 说明 |
|------|---------|------|
| Backend | 8001 | API服务 |
| Frontend | 3782 | Web界面（可选） |

### 故障排查

| 问题 | 解决方案 |
|------|---------|
| 连接失败 | 确认后端已启动: `python -m deeptutor.api.run_server` |
| API Key错误 | 检查.env配置 |
| 知识库为空 | 先添加文档: `deeptutor kb add` |
| 模型不支持 | 确认LLM_BINDING配置正确 |

### 质量标准

1. **响应完整性**: Deep Solve必须包含完整推导
2. **来源准确性**: Chat模式必须有引用标注
3. **测验有效性**: Quiz题目必须有唯一答案
4. **动画可运行**: Manim代码必须能执行

### 自检清单

- [ ] DeepTutor后端已启动
- [ ] API连接正常
- [ ] 知识库已创建
- [ ] TutorBot人格配置
- [ ] 与学习师工作流集成
