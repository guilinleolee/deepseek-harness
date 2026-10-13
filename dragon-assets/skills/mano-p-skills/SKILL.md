---
license: UNKNOWN
---

# mano-p-skills

## L0: 一句话描述 (≤15字)
Computer Use Agent技能库

## L1: 使用场景 (50-100字)
基于Mano-P的Computer Use Agent Skills，用于构建更智能的CUA任务工作流。适合企业级GUI自动化、跨平台操作、长任务规划场景。

## L2: 详细文档

### 核心能力
1. **Mano-CUA Skills** - 第一阶段开源的Computer Use Agent Skills
2. **任务工作流构建** - 自定义Skills/Tools/Agent工作流
3. **多步任务执行** - 支持数十到数百步的企业级流程
4. **智能报告生成** - 自动生成数据分析报告、工作总结

### Skill模板

#### Skill 1: web_automation_skill
```yaml
name: web_automation_skill
description: 网页自动化任务
trigger_keywords: [浏览器, 网页, 登录, 填写表单]
steps:
  - think: 分析任务目标
  - act: 执行GUI操作
  - verify: 验证结果
```

#### Skill 2: cross_system_data_extract
```yaml
name: cross_system_data_extract
description: 跨系统数据提取
trigger_keywords: [提取数据, 导出, 跨系统, 无API]
steps:
  - identify: 识别源系统GUI
  - navigate: 导航到目标数据
  - extract: 提取数据
  - format: 格式化输出
```

#### Skill 3: enterprise_workflow_automation
```yaml
name: enterprise_workflow_automation
description: 企业级工作流自动化
trigger_keywords: [企业, 自动化, 流程, 长任务]
steps:
  - plan: 任务规划
  - execute: 分步执行
  - monitor: 进度监控
  - report: 生成报告
```

### 使用方法
```bash
# 列出所有可用Skills
python scripts/list_skills.py

# 执行自定义Skill
python scripts/execute_skill.py --skill web_automation_skill --task "登录GitHub并Star仓库"

# 构建新Skill
python scripts/build_skill.py --template enterprise_workflow_automation --name my_workflow
```

### 与mano-p-core协同
- mano-p-core: 提供底层GUI-VLA推理引擎
- mano-p-skills: 提供上层任务工作流封装
- 编排关系: Skills调用Engine，形成完整自动化链路

### 天龙引擎集成
- 所属岗位: 17-07 GUI-VLA集成工程师
- 协同技能: mano-p-core, turix-desktop-agent