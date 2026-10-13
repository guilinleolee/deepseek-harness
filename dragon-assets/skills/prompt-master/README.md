# 提词师 (Prompt Master)

> 专业级提示词工程系统，让LLM输出质量提升10倍

## 🎯 一句话介绍

提供10+验证模板、智能路由和深度优化能力，基于顶级框架（CO-STAR, CREATE, APE）和质量标准，让每个人都能写出专业级提示词。

## ✨ 核心价值

- **开箱即用**: 10+验证模板，覆盖常见场景
- **质量保证**: 5维度评估体系，确保提示词质量
- **智能路由**: 自动匹配最相关模板
- **深度优化**: Subagent提供专业级优化
- **持续改进**: A/B测试和效果追踪

---

## 🏗️ 架构设计

### 混合架构
```
用户需求 → 提词师入口 → 智能路由
                                ↓
                    ┌───────────┴───────────┐
                    ↓                       ↓
              Skill（简单任务）      Subagent（复杂任务）
                    ↓                       ↓
              快速响应              深度分析优化
                    └───────────┬───────────┘
                                ↓
                          共享知识库
```

### 技术选型
- **Skill层**: Claude Code Skill + Markdown存储
- **Subagent层**: Claude Code Subagent + MCP工具
- **集成层**: SendMessage + JSON + Git

---

## 📅 进度追踪

| 阶段 | 负责人 | 状态 | 完成时间 |
|------|--------|------|----------|
| Phase 0 - 需求分析 | 00分析师 | ✅ 完成 | 2026-02-21 |
| **Phase 1 - 系统验证** | **03构建师** | **✅ 完成** | **2026-02-21** |
| Phase 2 - 深度调研 | 01调研师 | ⏳ 待启动 | - |
| Phase 3 - 功能增强 | 03构建师 | ⏳ 待启动 | - |
| Phase 4 - 生产部署 | 08发布师 | ⏳ 待启动 | - |

### Phase 1 完成情况（2026-02-21）

✅ **任务1**: 修复Windows编码问题
- 在 `render.py` 和 `evaluate.py` 中添加UTF-8编码支持
- 测试验证：中文显示正常，无乱码

✅ **任务2**: 测试所有模板
- 测试10个P0优先级模板
- 平均质量分：88.2/100
- 通过率：100%

✅ **任务3**: 实战验证
- 验证3个真实场景（00/02/06宗师）
- 平均质量分：88.3/100
- 系统状态：生产就绪 ✅

**关键成果**:
- 📦 交付5个核心脚本（render, evaluate, test, validate）
- 📊 生成3份详细报告（测试、验证、完成）
- 🚀 系统已达到生产就绪状态（8.6/10）
- ⚡ 渲染性能：平均0.052秒

**详细报告**:
- [TEST_REPORT.md](TEST_REPORT.md) - 模板测试报告
- [VALIDATION_REPORT.md](VALIDATION_REPORT.md) - 实战验证报告
- [COMPLETION_REPORT.md](COMPLETION_REPORT.md) - 任务完成报告

---

## 📁 文档索引

- **[ANALYSIS_REPORT.md](ANALYSIS_REPORT.md)** - 需求分析报告（00分析师）
- **[task_plan.md](task_plan.md)** - 任务计划与追踪
- **[findings.md](findings.md)** - 调研发现（01调研师更新中）

---

## 🎯 MVP范围

### v1.0 - 核心功能（Phase 1）
- ✅ 提示词模板库（15+场景）
- ✅ 提示词生成器（向导式）
- ✅ 基础优化建议
- ✅ 格式标准化
- ✅ 混合架构实现

### v1.1 - 增强功能（Phase 2）
- ✅ 新增5个高价值模板（API设计、测试用例、代码解释、错误诊断、文档生成）
- 🔍 深度优化
- 🔍 质量审计
- 🔍 案例调研
- 🔍 A/B测试建议

### v2.0 - 高级特性（Phase 3）
- 🚀 版本控制
- 🚀 效果追踪
- 🚀 团队协作
- 🚀 深度集成

---

## 🚀 快速开始

### 安装依赖

```bash
pip install pyyaml jinja2
```

### 使用提词师

**1. 查看所有模板**
```bash
cd C:\Users\li\.claude\skills\prompt-master
python scripts/render.py --list
```

**2. 渲染模板**
```bash
# 问题解构
python scripts/render.py -t problem-decomposition -v task_description="设计一个用户认证系统"

# 系统设计
python scripts/render.py -t system-design -v qps="10000" -v user_scale="百万级"

# 代码审查
python scripts/render.py -t code-review -v context_description="JWT认证模块"
```

**3. 评估提示词质量**
```bash
python scripts/evaluate.py --prompt my_prompt.txt
```

**4. 交互式模式**
```bash
python scripts/render.py --interactive
```

### 快速参考

- **[QUICK_GUIDE.md](QUICK_GUIDE.md)** - 5分钟快速上手指南
- **[TEST_REPORT.md](TEST_REPORT.md)** - 模板测试报告
- **[VALIDATION_REPORT.md](VALIDATION_REPORT.md)** - 实战验证报告
- **[COMPLETION_REPORT.md](COMPLETION_REPORT.md)** - 任务完成报告

---

## 🤝 与九部天龙集成

提词师可辅助所有九部天龙宗师：

- **00分析师**: 需求分析提示词
- **01调研师**: 调研计划提示词
- **02架构师**: 架构设计提示词
- **03构建师**: 代码生成提示词
- **04验证师**: 测试用例提示词
- **05安全师**: 安全审查提示词
- **06审查师**: 代码审查提示词
- **07记录师**: 文档编写提示词
- **08发布师**: 发布说明提示词

---

## 📊 成功指标

### 业务指标
- 提示词创建时间降低60%
- 质量评分提升30%
- 复用率>50%
- 满意度>4.0/5.0

### 技术指标
- Skill响应<1秒
- Subagent响应<30秒
- TOKEN消耗降低85%
- 可用性>99%

---

## 📌 下一步行动

**当前阶段**: Phase 1 - 深度调研
**负责人**: 01调研师

**优先任务**:
1. 🔴 调研GitHub开源工具（5+高星项目）
2. 🔴 分析商业工具特性（3+平台）
3. 🟡 整理最佳实践（提示词设计原则）
4. 🟢 更新findings.md

**成功标准**:
- 调研10+工具/项目
- 提取核心功能清单
- 形成最佳实践库
- 输出完整findings.md

---

**最后更新**: 2026-02-21
**维护者**: 九部天龙团队
