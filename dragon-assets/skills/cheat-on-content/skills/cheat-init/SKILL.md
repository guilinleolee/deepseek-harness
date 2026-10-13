# Cheat-Init — 项目初始化系统

## L0: 一句话描述
初始化内容校准项目，建立rubric和persona基线

## L1: 使用场景
新项目启动时定义评分标准、受众画像和评分锚点

## L2: 详细文档

### 触发词
- "初始化项目"
- "create project"
- "setup rubric"
- "初始化rubric"

### 初始化清单

```
1. [cheat-persona] 定义受众画像（锚定标准）
   └─ 要求: ≥5个校准样本
2. [cheat-score] 初始化7维rubric
   └─ 要求: 每维度定义1-5分标准
3. [cheat-predict] 建立盲预测基线
   └─ 要求: 首批≥3个样本
4. 创建buffer文件
   └─ 初始值: 5
5. 创建发布记录目录
   └─ 位置: publish-log/
```

### 初始化文件结构

```
project/
├── rubrics/
│   └── opinion-video.md     # 7维rubric
├── personas/
│   └── [target-audience].md # 受众画像
├── buffer.md                # Buffer状态
├── publish-log/             # 发布记录
│   ├── 2026-05-24-video-a.md
│   └── 2026-05-25-video-b.md
├── retro-log/               # 复盘记录
│   └── retro-2026-05-27.md
└── learned-rules/          # 判断进化规则
    └── rule-001.md
```

### 锚定验证

```
锚定完成标志:
- 8分以上内容: ≥5个样本，有播放数据验证
- 5分以下内容: ≥3个样本，验证"缺陷"
- 校准一致性: 人工评分 vs 系统评分误差<0.5
```

### 天龙引擎集成

- **天龙岗位**: 35-02社媒运营、30-01营销总监、50-01产品策划
- **协同**: cheat-persona（受众）、cheat-score（评分）、cheat-publish（发布）

### 快速初始化命令

```bash
# 一键初始化
cd project/
bash ~/.claude/skills/cheat-on-content/scripts/init-project.sh "项目名称"
```