---
license: UNKNOWN
triggers: ["vimax video pipeline", "vimax-video-pipeline"]
---
# vimax-video-pipeline

## L0: 一句话描述 (≤15字)
ViMax多Agent视频生成流水线技能包

## L1: 使用场景 (50-100字)
适用场景：需要从剧本/小说/创意生成专业视频内容时调用。触发条件：用户说"用ViMax生成视频"、"小说转视频"、"剧本转视频"、"AI生成短视频"时自动调度。支持Idea2Video/Novel2Video/Script2Video/AutoCameo四种工作流。

## L2: 详细文档

### 来源项目

| 项目 | Stars | 核心能力 |
|------|-------|---------|
| [HKUDS/ViMax](https://github.com/HKUDS/ViMax) | 4.9k | 多Agent视频生成、RAG角色追踪、双重参考图过滤 |

### 核心价值
填补天龙引擎在**多Agent视频生成流水线**领域的关键空白，实现剧本/小说/创意到专业视频的端到端自动化。

### 新增能力

| 能力 | 功能 | 核心Agent |
|------|------|----------|
| **角色一致性追踪** | RAG跨Scene/Event/Novel层级角色记忆 | CharacterExtractor, CharacterPortraitsGenerator |
| **双重参考图过滤** | Text过滤(≥8张) → Multimodal过滤(VLM选择) | ReferenceImageSelector, BestImageSelector |
| **多机位模拟** | 镜头树架构+父子依赖关系 | CameraImageGenerator, SceneExtractor |
| **事件提取与压缩** | 长视频事件切分+Novel压缩 | EventExtractor, NovelCompressor |
| **全局信息规划** | 多场景协同+整体叙事连贯 | GlobalInformationPlanner, ScriptPlanner |

### 十大专业Agent

```
Screenwriter                    - 剧本编写Agent
CharacterExtractor             - 角色提取Agent
CharacterPortraitsGenerator    - 角色肖像生成Agent
ScriptPlanner                 - 脚本规划Agent
ReferenceImageSelector          - 参考图筛选Agent
BestImageSelector             - 最优图像选择Agent
CameraImageGenerator          - 机位图像生成Agent
SceneExtractor                - 场景提取Agent
EventExtractor                - 事件提取Agent
NovelCompressor               - 小说压缩Agent
GlobalInformationPlanner       - 全局信息规划Agent
```

### 四种工作流

| 工作流 | 输入 | 输出 | Pipeline |
|--------|------|------|----------|
| **Idea2Video** | 一句话创意 | 完整视频 | 创意→剧本→角色→场景→视频 |
| **Novel2Video** | 小说/故事文本 | 视频集 | 小说→事件→场景→角色→视频 |
| **Script2Video** | 剧本/脚本 | 视频 | 脚本→镜头→机位→图像→视频 |
| **AutoCameo** | 文本/音频 | 虚拟形象视频 | 音频→唇同步→虚拟形象 |

### RAG角色追踪架构

```
┌─────────────────────────────────────────────────────────────┐
│                    RAG 三层角色追踪                          │
├─────────────────────────────────────────────────────────────┤
│  Scene层: 角色出现次数、关系网络、场景分布                   │
│      ↓                                                    │
│  Event层: 角色动作、情绪变化、对话场景                     │
│      ↓                                                    │
│  Novel层: 角色成长弧线、性格演变、跨事件一致性              │
│                                                             │
│  CharacterExtractor → CharacterPortraitsGenerator → RAG存储  │
└─────────────────────────────────────────────────────────────┘
```

### 双重参考图过滤

```
┌─────────────────────────────────────────────────────────────┐
│  Text-Only Filtering (≥8张)                               │
│  ├── CLIP相似度排序                                       │
│  ├── 美学评分过滤                                        │
│  └── 主题相关性验证                                      │
│                    ↓                                       │
│  Multimodal Filtering (VLM选择)                           │
│  ├── GPT-4V/Gemini-Pro视觉理解                          │
│  ├── 角色一致性验证                                      │
│  └── 空间布局合理性                                      │
│                    ↓                                       │
│  BestImageSelector → 最终参考图输出                       │
└─────────────────────────────────────────────────────────────┘
```

### 机位树架构

```
┌─────────────────────────────────────────────────────────────┐
│                    Camera Tree Architecture                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                    [全景 Wide Shot]                        │
│                    /      |      \                          │
│               [中景]  [特写]  [侧面]                        │
│                 |       |       |                         │
│            [正面]  [侧面]  [背面]                          │
│                                                             │
│  父子依赖: 子节点继承父节点相机关系                         │
│  空间一致性: 保持同一场景内机位逻辑连贯                     │
└─────────────────────────────────────────────────────────────┘
```

### 天龙岗位升级

| 岗位 | 版本 | 新增能力 |
|------|------|---------|
| **35-05 短视频编导** | V6.0 → V7.0 | ViMax多Agent流水线 + 4种工作流 + RAG角色追踪 |
| **17-01 数据分析师** | V1.5 → V1.6 | EventExtractor事件分析 + NovelCompressor内容压缩 |
| **09-02 编排协调师** | V9.4 → V9.5 | ViMax流水线编排 + 多Agent状态协调 |

### 核心命令速查

```bash
# Idea2Video工作流
[@35-05] 使用ViMax Idea2Video生成"一个人穿越到古代"主题视频

# Novel2Video工作流
[@35-05] 使用ViMax Novel2Video将小说片段转换为视频

# Script2Video工作流
[@35-05] 使用ViMax Script2Video将剧本转换为视频

# AutoCameo工作流
[@35-05] 使用ViMax AutoCameo生成虚拟形象演讲视频

# 角色追踪检查
[@17-01] 检查视频生成过程中的角色一致性

# 机位规划
[@35-05] 规划一场对话场景的多机位布局
```

### 与现有视频引擎对比

| 维度 | Pixelle-Video | Remotion | ViMax | 选择建议 |
|------|--------------|----------|-------|---------|
| **输入** | 主题 | React代码 | 剧本/小说/创意 | 文本→ViMax, 代码→Remotion |
| **角色一致性** | 无 | 无 | **完整RAG追踪** | 角色视频→ViMax |
| **多机位** | 无 | 无 | **Camera Tree** | 专业分镜→ViMax |
| **工作流** | 全自动 | 代码驱动 | **4种专业** | 多场景→ViMax |

### 协同链路

```
天龙引擎视频生成全家桶:
├── ViMax (V11.15) ⭐NEW - 多Agent流水线、角色追踪、专业分镜
├── Pixelle-Video (V8.98) - 端到端自动、数字人口播
├── Remotion (V8.28) - 代码驱动、精确控制
├── MagiHuman (V8.76) - 人像视频极速生成
└── daVinci-MagiHuman (V8.76) - 15B参数人像视频

引擎选择矩阵:
- 剧本/小说/故事 → ViMax (RAG角色追踪)
- 数字人口播 → Pixelle-Video
- 数据可视化视频 → Remotion
- 快速人像 → MagiHuman/daVinci-MagiHuman
```

### 流水线编排命令

```bash
# 启动流水线
python3 ~/.claude/skills/vimax-video-pipeline/scripts/pipeline_orchestrator.py \
  --workflow idea2video \
  --input "AI在未来世界的冒险故事" \
  --output ./vimax_output

# 检查点管理
python3 ~/.claude/skills/vimax-video-pipeline/scripts/checkpoint_manager.py \
  --save --phase scene_extraction

python3 ~/.claude/skills/vimax-video-pipeline/scripts/checkpoint_manager.py \
  --load --phase scene_extraction

# Agent状态查询
python3 ~/.claude/skills/vimax-video-pipeline/scripts/agent_communicator.py \
  --status --agent screenwriter

# RAG角色查询
python3 ~/.claude/skills/vimax-video-pipeline/scripts/rag_tracker.py \
  --query "主角外貌特征"
```

### 配置文件

```yaml
# configs/vimax_config.yaml
vimax:
  model:
    llm: gpt-4o
    vlm: gpt-4o
    image: dalle-3

  pipeline:
    max_parallel_agents: 3
    checkpoint_enabled: true
    checkpoint_dir: ./checkpoints

  rag:
    vector_store: chromadb
    embedding_model: text-embedding-3-small

  character_consistency:
    enabled: true
    min_portraits: 3
    max_portraits: 9

  camera:
    tree_depth: 3
    default_fov: 60

  workflows:
    idea2video:
      scenes: 5-10
      duration_per_scene: 10-20
    novel2video:
      events_per_chapter: 3-5
      compression_ratio: 0.3
    script2video:
      shots_per_scene: 4-8
      camera_angles: ["wide", "medium", "closeup"]
```

### 技能文件

- [SKILL.md](SKILL.md) - 本文件
- [scripts/pipeline_orchestrator.py](scripts/pipeline_orchestrator.py) - 流水线编排器
- [scripts/checkpoint_manager.py](scripts/checkpoint_manager.py) - 检查点管理器
- [scripts/agent_communicator.py](scripts/agent_communicator.py) - Agent通信器
- [scripts/rag_tracker.py](scripts/rag_tracker.py) - RAG角色追踪器
- [workflows/idea2video.json](workflows/idea2video.json) - Idea2Video工作流
- [workflows/novel2video.json](workflows/novel2video.json) - Novel2Video工作流
- [workflows/script2video.json](workflows/script2video.json) - Script2Video工作流
- [workflows/autocameo.json](workflows/autocameo.json) - AutoCameo工作流
- [configs/vimax_config.yaml](configs/vimax_config.yaml) - ViMax配置

### 预期收益

| 指标 | V11.14 | V11.15 | 提升 |
|------|---------|---------|------|
| **角色一致性** | 无追踪 | RAG三层追踪 | **质的飞跃** |
| **视频生成质量** | 自动生成 | 专业分镜 | **质的飞跃** |
| **多Agent编排** | 手动 | 自动流水线 | **+400%** |
| **工作流覆盖** | 1种 | 4种 | **+300%** |
| **角色视频能力** | 无 | 完整 | **新增能力** |

### 注意事项

1. **模型依赖**: 需要GPT-4V/Gemini-Pro进行视觉理解
2. **RAG存储**: 建议使用ChromaDB进行向量存储
3. **检查点**: 长视频建议开启检查点避免重复计算
4. **角色数量**: 建议单视频角色≤5个以保证一致性
