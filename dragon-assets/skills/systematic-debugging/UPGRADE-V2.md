# Systematic Debugging V2.0 升级报告

## 升级来源

整合自以下三个来源：
1. **GSD-2 debug-like-expert** - 方法论调查 + 证据收集
2. **omnidebug-autopilot** - 自动堆栈检测 + 浏览器复现
3. **天龙引擎原有** - 四阶段调试框架

## 新增功能

### 1. Decision Gate 集成
每个阶段完成后触发决策门控，确保用户对调试流程有控制权。

### 2. 六阶段扩展（原四阶段）
- Phase 0: Triage（新增）- 堆栈检测 + 错误分类
- Phase 1-4: 原有流程
- Phase 5: Verification（新增）- 自动验证门控

### 3. 堆栈自动检测
```yaml
# 自动检测技术栈
Stack Detection:
  Node.js/TypeScript:
    signals: [package.json, tsconfig.json]
    verify: [pnpm test, pnpm lint, pnpm build]

  Python:
    signals: [pyproject.toml, requirements.txt]
    verify: [pytest -q, ruff check .]

  Go:
    signals: [go.mod]
    verify: [go test ./..., go vet ./...]

  Rust:
    signals: [Cargo.toml]
    verify: [cargo test, cargo clippy]
```

### 4. 浏览器复现模块
```bash
# 浏览器Bug复现流程
python scripts/repro_browser_issue.py \
  --project-root . \
  --repro-cmd "playwright test tests/bug.spec.ts" \
  --expect fail \
  --runs 2

# 捕获调试工件
python scripts/capture_browser_artifacts.py \
  --project-root . \
  --output-dir .debug/browser-artifacts
```

### 5. 自动修复启发式
优先级排序：
1. Incorrect logic or branching
2. Null and undefined handling
3. Async and concurrency ordering
4. Contract and schema mismatch
5. Config and environment mismatch
6. Dependency incompatibility
7. Resource, path, or permission issues

## 与 GSD-2 对比

| 维度 | GSD-2 debug-like-expert | Systematic Debugging V2.0 |
|------|------------------------|--------------------------|
| 阶段数 | 未明确 | **6阶段** |
| Decision Gate | ✅ 有 | ✅ 已集成 |
| 堆栈检测 | ✅ 自动 | ✅ 已集成 |
| 浏览器复现 | ✅ Playwright | ✅ 已集成 |
| 自动修复 | ✅ 有 | ✅ 已集成 |
| 与天龙岗位集成 | ❌ 无 | ✅ 完整 |

## 文件变更

| 文件 | 变更类型 | 说明 |
|------|---------|------|
| `SKILL.md` | 升级 | V1.0 → V2.0 |
| `UPGRADE-V2.md` | 新增 | 本文档 |

## 后续工作

1. [ ] 创建 `scripts/repro_browser_issue.py`
2. [ ] 创建 `scripts/capture_browser_artifacts.py`
3. [ ] 集成到 hooks.json
4. [ ] 更新 SKILLS_INDEX.md

---
**升级日期**: 2026-03-25
**升级者**: 天龙引擎团队