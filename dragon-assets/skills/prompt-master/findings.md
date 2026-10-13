# 调研发现：提示词工具生态系统

## 调研时间
2026-02-21

## 调研目标
为"提词师"系统提供技术参考和设计灵感

---

## 1. 开源工具分析

### 1.1 dair-ai/Prompt-Engineering-Guide ⭐ 50k+
- **仓库**: https://github.com/dair-ai/Prompt-Engineering-Guide
- **Stars**: ~50,000+
- **核心特性**:
  - 全面的提示词工程指南，涵盖30+种技术
  - 支持多语言（13种语言）
  - 300万+学习者（截至2024年1月）
  - 提供在线课程（DAIR.AI Academy）
- **架构亮点**:
  - 结构化文档系统：Introduction → Techniques → Applications → Prompts → Models → Risks
  - 每个技术都有详细示例和最佳实践
  - 集成Notebook教程和代码示例
- **可借鉴点**:
  - ✅ **分类体系**: 按技术类型（Zero-Shot, Few-Shot, CoT, ReAct）和应用场景（分类、生成、推理）分类
  - ✅ **Web版部署**: 使用Next.js + Nextra构建文档网站（https://www.promptingguide.ai/）
  - ✅ **社区驱动**: 支持PR贡献，Discord社区，多语言翻译
  - ✅ **商业模式**: 提供付费课程和企业服务

### 1.2 microsoft/prompt-engineering ⭐ 企业级
- **仓库**: https://github.com/microsoft/prompt-engineering
- **核心特性**:
  - 专注于Codex模型用于代码生成和操作
  - 提供实际应用案例（Codex-Babylon, Codex-CLI, MinecraftCodex）
  - 企业级开源流程（CLA, Code of Conduct）
- **架构亮点**:
  - **实战导向**: 每个仓库都是完整的应用示例
  - **模块化设计**: 独立的工具仓库，便于复用
  - **法律合规**: 完整的开源许可管理
- **可借鉴点**:
  - ✅ **实战案例**: 提供可运行的完整项目
  - ✅ **文档驱动**: 每个项目都有详细的README和示例
  - ✅ **企业流程**: CLA自动化，贡献者管理

### 1.3 promptslab/Promptify ⭐ NLP专注
- **仓库**: https://github.com/promptslab/Promptify
- **Stars**: 2,000+
- **核心特性**:
  - 专注于NLP任务的提示词工程
  - 提供Pipeline API，2行代码完成NLP任务
  - 支持10+种NLP任务（NER, 分类, QA, 摘要等）
  - 输出结构化（Python对象）
- **架构亮点**:
  - **Pipeline API**: `Prompter` + `Model` + `Pipeline` 三层架构
  - **模板系统**: 使用Jinja2模板管理提示词
  - **模型无关**: 支持OpenAI, HuggingFace, Azure等
  - **Few-Shot支持**: 轻松添加示例
- **可借鉴点**:
  - ✅ **结构化输出**: 解决LLM输出解析难题
  - ✅ **模板系统**: Jinja2模板便于版本管理和复用
  - ✅ **快速开发**: 2行代码完成复杂NLP任务
  - ✅ **成本优化**: 提示词优化降低OpenAI Token成本

### 1.4 langfuse/langfuse ⭐ 22k (LLMOps平台)
- **仓库**: https://github.com/langfuse/langfuse
- **Stars**: 22,126
- **核心特性**:
  - 开源LLM工程平台
  - LLM可观测性、指标、评估、提示词管理、Playground、数据集
  - 集成OpenTelemetry, Langchain, OpenAI SDK等
- **架构亮点**:
  - **全生命周期管理**: 从开发到部署到监控
  - **可观测性优先**: 跟踪每次LLM调用
  - **版本控制**: 提示词版本管理和A/B测试
- **可借鉴点**:
  - ✅ **可观测性**: 跟踪和调试LLM应用
  - ✅ **提示词版本管理**: Git风格的版本控制
  - ✅ **评估框架**: 自动化评估LLM输出质量
  - ✅ **数据集管理**: 管理测试数据和Golden Set

### 1.5 Agenta-AI/agenta ⭐ 3.8k (LLMOps平台)
- **仓库**: https://github.com/Agenta-AI/agenta
- **Stars**: 3,859
- **核心特性**:
  - 开源LLMOps平台
  - 提示词Playground、管理、评估、可观测性一体化
- **可借鉴点**:
  - ✅ **一体化**: 开发、测试、部署、监控统一平台
  - ✅ **评估工具**: 内置多种评估指标
  - ✅ **协作功能**: 团队协作和版本管理

### 1.6 pezzolabs/pezzo ⭐ 3.1k (开发者优先)
- **仓库**: https://github.com/pezzolabs/pezzo
- **Stars**: 3,187
- **核心特性**:
  - 开源、开发者优先的LLMOps平台
  - 提示词设计、版本管理、即时交付、协作、故障排查、可观测性
- **可借鉴点**:
  - ✅ **开发者体验**: CLI工具和IDE集成
  - ✅ **版本管理**: Git风格的提示词版本控制
  - ✅ **即时部署**: 一键部署到生产环境


---

## 2. 商业平台分析

### 2.1 AIPRM (Chrome扩展)
- **网站**: https://www.aiprm.com
- **核心特性**:
  - Chrome扩展，集成到ChatGPT界面
  - 社区驱动的提示词库
  - 一键应用预设提示词模板
  - 提示词收藏和自定义
- **商业模式**: 免费版 + 付费订阅
- **可借鉴点**:
  - ✅ **浏览器集成**: 直接在ChatGPT界面使用
  - ✅ **社区生态**: 用户贡献和分享提示词
  - ✅ **分类标签**: 按用途、行业、难度分类
  - ✅ **一键应用**: 降低使用门槛

### 2.2 PromptBase (提示词市场)
- **网站**: https://promptbase.com
- **核心特性**:
  - 提示词交易市场
  - 用户可以买卖高质量提示词
  - 支持多种模型（DALL-E, GPT-3, Midjourney等）
  - 提示词质量评级和评论
- **商业模式**: 交易佣金（提示词售价的20%）
- **可借鉴点**:
  - ✅ **市场机制**: 激励用户贡献高质量提示词
  - ✅ **质量评级**: 星级评价和使用统计
  - ✅ **预览功能**: 展示提示词效果示例
  - ✅ **多模型支持**: 覆盖主流生成式AI

### 2.3 FlowGPT (社区驱动)
- **网站**: https://flowgpt.com
- **核心特性**:
  - 完全免费的提示词社区
  - 提示词分享和发现
  - 用户可以fork和优化他人提示词
  - 提示词挑战和竞赛
- **可借鉴点**:
  - ✅ **开源理念**: 完全免费，知识共享
  - ✅ **社交功能**: 关注、点赞、评论
  - ✅ **Fork机制**: 鼓励迭代优化
  - ✅ **社区活动**: 定期举办提示词竞赛

### 2.4 SnackPrompt (教育导向)
- **网站**: https://snackprompt.com
- **核心特性**:
  - 专注于提示词教育和学习
  - 提供提示词构建教程
  - 示例库和最佳实践
- **可借鉴点**:
  - ✅ **教育导向**: 降低学习曲线
  - ✅ **逐步指导**: 从零开始教学
  - ✅ **案例丰富**: 大量实际应用案例


---

## 3. 最佳实践汇总

### 3.1 提示词设计原则

#### CO-STAR框架（新加坡政府科技局）
- **C**ontext（背景）：提供足够的背景信息
- **O**bjective（目标）：明确期望的输出
- **S**tyle（风格）：指定输出的风格和语调
- **T**one（语气）：控制输出的情感色彩
- **A**udience（受众）：说明目标受众
- **R**esponse（响应）：定义输出格式

#### CREATE框架
- **C**ontext（上下文）：设定任务背景
- **R**ole（角色）：为AI分配角色
- **E**xplicit（明确）：提供明确指令
- **A**ctions（行动）：指定执行步骤
- **T**one（语调）：设定输出语调
- **E**xample（示例）：提供参考示例

#### 结构化提示词设计原则（来自dair-ai）
1. **明确性**: 使用清晰、具体的语言
2. **示例驱动**: 使用Few-Shot示例引导模型
3. **思维链**: 让模型展示推理过程（CoT）
4. **分步骤**: 复杂任务分解为多个步骤
5. **格式约束**: 明确指定输出格式（JSON、Markdown等）
6. **约束条件**: 明确说明限制和要求
7. **迭代优化**: 通过多次尝试优化提示词

### 3.2 质量评估框架

#### 评估维度（来自Promptify和Langfuse）
1. **准确性**: 输出是否正确完成预期任务
2. **一致性**: 多次运行结果是否一致
3. **完整性**: 是否包含所有必需信息
4. **相关性**: 输出是否与问题相关
5. **格式正确性**: 输出格式是否符合要求
6. **Token效率**: 提示词长度是否优化

#### 评估方法
- **自动化评估**: 使用Golden Set对比
- **人工评估**: 专家打分
- **A/B测试**: 对比不同提示词版本
- **用户反馈**: 收集实际使用反馈

### 3.3 提示词模式库（来自dair-ai）

#### 基础模式
1. **Zero-Shot**: 直接指令，无示例
2. **Few-Shot**: 提供1-5个示例
3. **CoT（Chain-of-Thought）**: 让模型展示思考过程
4. **Self-Consistency**: 多次采样取最一致答案

#### 高级模式
1. **ReAct**: 推理 + 行动循环
2. **ToT（Tree-of-Thoughts）**: 探索多个推理路径
3. **RAG（检索增强生成）**: 结合外部知识库
4. **Prompt Chaining**: 多步骤提示词链
5. **ART（自动推理工具）**: 自动选择工具
6. **DSP（方向刺激提示）**: 引导模型特定方向

### 3.4 提示词模板系统（来自Promptify）

#### 模板管理
- 使用Jinja2模板引擎
- 支持变量插值和条件逻辑
- 版本控制和复用

#### 示例模板结构
```jinja
You are a {{ role }} expert.
Your task is to {{ task }}.

Context: {{ context }}

Examples:
{% for example in examples %}
Q: {{ example.question }}
A: {{ example.answer }}
{% endfor %}

Now, answer: {{ input }}
```


---

## 4. 技术方案建议

### 4.1 架构推荐

基于调研结果，推荐"提词师"系统采用以下架构：

#### 核心架构（三层设计）

```
┌─────────────────────────────────────────────────────────────┐
│                    提词师系统架构                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📝 模板层 (Template Layer)                                  │
│     ├── Jinja2模板引擎                                       │
│     ├── 版本控制系统（Git-like）                              │
│     ├── 模板分类体系                                         │
│     └── 变量管理                                            │
│                                                             │
│  🔧 执行层 (Execution Layer)                                 │
│     ├── Pipeline API（参考Promptify）                        │
│     ├── 提示词构建器                                         │
│     ├── Few-Shot示例管理                                     │
│     └── 输出解析器（结构化输出）                               │
│                                                             │
│  📊 评估层 (Evaluation Layer)                                │
│     ├── 自动化评估框架                                       │
│     ├── A/B测试支持                                         │
│     ├── 可观测性跟踪                                        │
│     └── 用户反馈收集                                        │
│                                                             │
│  🔌 集成层 (Integration Layer)                               │
│     ├── Claude Code集成                                      │
│     ├── 多模型支持（Claude, GPT-4, 本地模型）                    │
│     ├── 知识库集成（RAG）                                    │
│     └── Web Dashboard                                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 MVP功能清单（优先级排序）

#### P0 - 核心功能（必须有）
1. **提示词模板管理**
   - 创建、编辑、删除提示词模板
   - 分类和标签系统
   - 搜索和过滤
   - 版本历史

2. **提示词构建器**
   - 可视化构建界面
   - 支持CO-STAR/CREATE框架
   - 实时预览
   - 变量插值

3. **基础执行**
   - 集成Claude API
   - 一键运行提示词
   - 输出展示
   - 简单历史记录

#### P1 - 重要功能（应该有）
4. **Few-Shot示例管理**
   - 示例库
   - 拖拽添加示例
   - 示例版本控制

5. **结构化输出**
   - 输出解析器（JSON、Markdown等）
   - Schema验证
   - 格式化展示

6. **评估系统**
   - Golden Set对比
   - 基础评估指标
   - 手动评分

7. **协作功能**
   - 团队共享
   - 权限管理
   - 评论和反馈

#### P2 - 增强功能（可以有）
8. **高级模式**
   - Chain-of-Thought模板
   - Prompt Chaining工作流
   - RAG集成

9. **可观测性**
   - Token使用统计
   - 成本追踪
   - 性能监控

10. **社区功能**
    - 公共模板库
    - 模板分享
    - 评分和评论

### 4.3 技术栈推荐

#### 后端
- **语言**: Python 3.10+
- **框架**: FastAPI（快速开发）或 Flask（轻量级）
- **数据库**: PostgreSQL（元数据） + Redis（缓存）
- **模板引擎**: Jinja2
- **版本控制**: Git（后端） + 自研版本管理系统

#### 前端
- **框架**: React 18 + TypeScript
- **UI库**: shadcn/ui（美观）或 Ant Design（企业级）
- **编辑器**: Monaco Editor（代码提示）或 CodeMirror
- **状态管理**: Zustand（轻量）或 Redux Toolkit

#### 集成
- **Claude API**: Anthropic官方SDK
- **存储**: 本地文件系统 / S3兼容存储
- **搜索**: Meilisearch（轻量全文搜索）

### 4.4 数据模型设计

#### 核心实体

```typescript
// 提示词模板
interface PromptTemplate {
  id: string;
  name: string;
  description: string;
  content: string; // Jinja2模板
  category: string;
  tags: string[];
  variables: Variable[];
  examples: Example[];
  version: number;
  author: string;
  createdAt: Date;
  updatedAt: Date;
}

// 变量定义
interface Variable {
  name: string;
  type: 'text' | 'number' | 'select' | 'multiline';
  description: string;
  required: boolean;
  defaultValue?: any;
  options?: string[]; // for select type
}

// Few-Shot示例
interface Example {
  id: string;
  input: string;
  output: string;
  explanation?: string;
}

// 执行记录
interface Execution {
  id: string;
  templateId: string;
  templateVersion: number;
  inputValues: Record<string, any>;
  output: any;
  metrics: {
    tokens: number;
    cost: number;
    latency: number;
  };
  status: 'success' | 'error';
  createdAt: Date;
}

// 评估结果
interface Evaluation {
  id: string;
  templateId: string;
  goldenSetId: string;
  scores: {
    accuracy: number;
    consistency: number;
    completeness: number;
  };
  executedAt: Date;
}
```

### 4.5 关键技术实现

#### 1. 模板系统（参考Promptify）
```python
from jinja2 import Template, Environment

class PromptBuilder:
    def __init__(self):
        self.env = Environment()
    
    def build(self, template: str, variables: dict, examples: list = None):
        """构建提示词"""
        tmpl = self.env.from_string(template)
        
        # 添加Few-Shot示例
        if examples:
            variables['examples'] = examples
        
        return tmpl.render(**variables)
```

#### 2. 版本控制（Git风格）
```python
import hashlib

class PromptVersion:
    def save_version(self, template_id: str, content: str):
        """保存新版本"""
        version_hash = hashlib.sha256(content.encode()).hexdigest()
        # 存储到数据库
        return version_hash
    
    def get_version(self, template_id: str, version: int):
        """获取指定版本"""
        # 从数据库检索
        pass
```

#### 3. 输出解析器（参考Promptify）
```python
import json
import re

class OutputParser:
    def parse_json(self, output: str) -> dict:
        """解析JSON输出"""
        try:
            return json.loads(output)
        except:
            # 尝试提取JSON片段
            match = re.search(r'\{.*\}', output, re.DOTALL)
            if match:
                return json.loads(match.group())
            raise ValueError("无法解析JSON输出")
```

### 4.6 实施路线图

#### 阶段1：MVP（4-6周）
- Week 1-2: 模板管理 + 基础UI
- Week 3-4: 提示词构建器 + Claude集成
- Week 5-6: 执行系统 + 基础评估

#### 阶段2：增强（4-6周）
- Week 7-8: Few-Shot示例管理
- Week 9-10: 结构化输出
- Week 11-12: 协作功能

#### 阶段3：高级（6-8周）
- Week 13-14: 高级模式（CoT, Chaining）
- Week 15-16: 可观测性
- Week 17-18: 社区功能

### 4.7 成功指标

#### 用户指标
- DAU/MAU（日活/月活）
- 提示词创建数量
- 提示词使用次数
- 用户留存率

#### 质量指标
- 提示词成功率（输出符合预期）
- 平均Token使用量
- 平均响应时间
- 用户满意度评分

#### 业务指标
- 提示词分享率
- 协作次数
- 评估完成率
- 成本节省（相比直接使用Claude）

---

## 5. 总结与建议

### 核心洞察
1. **开源工具已成熟**: Langfuse、Promptify等工具提供了成熟的提示词管理和评估方案
2. **社区驱动是关键**: dair-ai/Prompt-Engineering-Guide通过社区贡献达到50k+ stars
3. **模板化是趋势**: Promptify的Jinja2模板系统证明了模板化的价值
4. **评估必不可少**: Langfuse的可观测性功能对生产环境至关重要

### 给"提词师"系统的建议
1. **借鉴Promptify的Pipeline API**: 简化用户操作，2行代码完成任务
2. **学习dair-ai的分类体系**: 按技术和应用场景双重分类
3. **采用Langfuse的版本管理**: Git风格的版本控制
4. **集成CO-STAR/CREATE框架**: 降低用户学习曲线
5. **构建社区生态**: 鼓励用户分享和贡献模板

### 下一步行动
1. ✅ 完成技术调研（本文档）
2. ⏭️ 与02架构师讨论技术方案
3. ⏭️ 确定MVP功能范围
4. ⏭️ 开始原型开发

---

**调研完成时间**: 2026-02-21  
**调研工具**: GitHub API, Web Scraping  
**数据来源**: 6个开源仓库 + 4个商业平台 + 最佳实践文档
