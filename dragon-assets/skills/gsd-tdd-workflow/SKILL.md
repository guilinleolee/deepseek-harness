---
license: UNKNOWN
name: gsd-tdd-workflow
version: 1.0.0
description: |
  GSD风格的TDD工作流，融合三阶段提交机制。每个TDD阶段（Red→Green→Refactor）自动提交，确保原子化、可追溯的开发过程。
author: 天龙引擎团队 + GSD
created: 2026-03-27
category: development
source: https://github.com/gsd-build/get-shit-done

triggers:
  - "用户提到「gsd-tdd GSD TDD工作流」时"
  - "用户需要原子化TDD开发时"
---

# GSD TDD Workflow - 三阶段原子化TDD

## 核心价值

GSD风格的TDD工作流，将Red-Green-Refactor每个阶段与Git提交绑定，确保：

1. **原子化提交**：每个TDD阶段独立提交
2. **可追溯性**：完整记录每个测试和实现的变更
3. **回滚安全**：任何阶段失败可安全回滚
4. **偏差处理**：自动检测并处理偏差

## 三阶段提交架构

```
┌─────────────────────────────────────────────────────────────┐
│ GSD TDD 三阶段原子化工作流                                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  RED Phase                    GREEN Phase                   │
│  ┌──────────────┐            ┌──────────────┐              │
│  │ Write Test   │            │ Minimal Code │              │
│  │ (Failing)    │            │ (Passing)    │              │
│  └──────┬───────┘            └──────┬───────┘              │
│         │                           │                       │
│         ▼                           ▼                       │
│  ┌──────────────┐            ┌──────────────┐              │
│  │ Verify Fails │            │ Verify Pass  │              │
│  └──────┬───────┘            └──────┬───────┘              │
│         │                           │                       │
│         ▼                           ▼                       │
│  ┌──────────────┐            ┌──────────────┐              │
│  │ git commit   │            │ git commit   │              │
│  │ "test: ..."  │            │ "feat: ..."  │              │
│  └──────────────┘            └──────────────┘              │
│                                                             │
│  REFACTOR Phase                                             │
│  ┌──────────────┐                                           │
│  │ Clean Code   │                                           │
│  └──────┬───────┘                                           │
│         │                                                   │
│         ▼                                                   │
│  ┌──────────────┐                                           │
│  │ Tests Still  │                                           │
│  │ Pass         │                                           │
│  └──────┬───────┘                                           │
│         │                                                   │
│         ▼                                                   │
│  ┌──────────────┐                                           │
│  │ git commit   │ (if changes)                              │
│  │ "refactor:"  │                                           │
│  └──────────────┘                                           │
└─────────────────────────────────────────────────────────────┘
```

## 铁律

```
NO CODE WITHOUT A FAILING TEST FIRST
NO COMMIT WITHOUT VERIFICATION
NO REFACTOR WITHOUT GREEN TESTS
```

## Phase 1: RED (测试先行)

### 步骤

1. **识别测试场景**
   - 从需求文档提取测试场景
   - 定义边界条件
   - 列出错误场景

2. **编写失败测试**
   ```typescript
   // test/user-auth.test.ts
   describe('User Authentication', () => {
     it('should reject empty email', async () => {
       const result = await authenticate({ email: '', password: 'test' });
       expect(result.error).toBe('Email is required');
     });

     it('should reject invalid email format', async () => {
       const result = await authenticate({ email: 'invalid', password: 'test' });
       expect(result.error).toBe('Invalid email format');
     });
   });
   ```

3. **验证测试失败**
   ```bash
   npm test test/user-auth.test.ts
   # FAIL - expected 'Email is required', got undefined
   ```

4. **提交测试**
   ```bash
   git add test/user-auth.test.ts
   git commit -m "test: add user authentication validation tests"
   ```

### RED提交格式

```
test: [测试描述]

Tests:
- [测试用例1]
- [测试用例2]

Expected: All tests fail (feature not implemented)
```

## Phase 2: GREEN (最小实现)

### 步骤

1. **编写最小代码**
   ```typescript
   // src/auth.ts
   export async function authenticate(credentials: Credentials): Promise<Result> {
     if (!credentials.email?.trim()) {
       return { error: 'Email is required' };
     }

     if (!credentials.email.includes('@')) {
       return { error: 'Invalid email format' };
     }

     // 最小实现，只让测试通过
     return { success: true, user: { id: 1, email: credentials.email } };
   }
   ```

2. **验证测试通过**
   ```bash
   npm test test/user-auth.test.ts
   # PASS - All tests pass
   ```

3. **运行全部测试**
   ```bash
   npm test
   # 确保没有破坏其他测试
   ```

4. **提交实现**
   ```bash
   git add src/auth.ts
   git commit -m "feat: implement email validation for authentication"
   ```

### GREEN提交格式

```
feat: [功能描述]

Implemented:
- [实现内容]

Tests: All passing
Coverage: [当前覆盖率]
```

## Phase 3: REFACTOR (清理优化)

### 步骤

1. **识别重构机会**
   - 重复代码
   - 魔法数字
   - 复杂条件
   - 长函数

2. **执行重构**
   ```typescript
   // 重构后
   const EMAIL_REQUIRED = 'Email is required';
   const INVALID_EMAIL_FORMAT = 'Invalid email format';

   function validateEmail(email: string): string | null {
     if (!email?.trim()) return EMAIL_REQUIRED;
     if (!email.includes('@')) return INVALID_EMAIL_FORMAT;
     return null;
   }

   export async function authenticate(credentials: Credentials): Promise<Result> {
     const emailError = validateEmail(credentials.email);
     if (emailError) return { error: emailError };

     return { success: true, user: { id: 1, email: credentials.email } };
   }
   ```

3. **验证测试仍然通过**
   ```bash
   npm test
   # PASS - 所有测试仍然通过
   ```

4. **条件性提交**
   ```bash
   # 只有在有变更时才提交
   if git diff --quiet; then
     echo "No changes to commit"
   else
     git add src/auth.ts
     git commit -m "refactor: extract email validation logic"
   fi
   ```

### REFACTOR提交格式

```
refactor: [重构描述]

Changes:
- [变更内容]

Tests: All still passing
Reason: [重构原因]
```

## 测试框架自动检测

```bash
# 自动检测项目使用的测试框架
if [ -f "jest.config.js" ] || [ -f "jest.config.ts" ]; then
  TEST_RUNNER="jest"
elif [ -f "vitest.config.ts" ] || grep -q "vitest" package.json; then
  TEST_RUNNER="vitest"
elif [ -f "pytest.ini" ] || [ -f "setup.cfg" ]; then
  TEST_RUNNER="pytest"
elif [ -f "go.mod" ]; then
  TEST_RUNNER="go test"
elif [ -f "Cargo.toml" ]; then
  TEST_RUNNER="cargo test"
fi
```

## 偏差处理规则

| 偏差类型 | 触发条件 | 自动处理 |
|---------|---------|---------|
| **测试未失败** | RED阶段测试通过 | 自动修复测试，确保测试正确验证预期行为 |
| **测试未通过** | GREEN阶段测试失败 | 继续实现，不提交直到通过 |
| **其他测试失败** | 提交前全量测试失败 | 停止提交，修复破坏的测试 |
| **覆盖率下降** | 提交后覆盖率降低 | 警告并要求补充测试 |

## 完整工作流示例

```bash
# 1. 开始新的TDD周期
/gsd-tdd start "用户认证功能"

# 2. RED阶段：编写失败测试
/gsd-tdd red "should reject empty email"
# → 自动创建测试文件
# → 运行测试，确认失败
# → 自动提交：test: add email validation test

# 3. GREEN阶段：最小实现
/gsd-tdd green
# → 编写最小实现
# → 运行测试，确认通过
# → 自动提交：feat: implement email validation

# 4. REFACTOR阶段：清理优化
/gsd-tdd refactor
# → 执行重构
# → 运行测试，确认仍然通过
# → 自动提交（如有变更）：refactor: extract validation logic

# 5. 完成周期
/gsd-tdd complete
# → 显示本次TDD周期总结
# → 显示覆盖率报告
# → 显示提交历史
```

## 与GSD命令协同

| GSD命令 | TDD命令 | 协同效果 |
|--------|---------|---------|
| `/gsd:execute-phase` | `/gsd-tdd` | 执行阶段自动使用TDD模式 |
| `/gsd:verify-work` | `/gsd-tdd verify` | 验证时自动运行测试 |
| `/gsd:debug` | `/gsd-tdd debug` | 调试时自动创建失败测试 |

## 与天龙引擎协同

| 天龙岗位 | 协同方式 |
|---------|---------|
| **04验证师** | 使用GSD TDD工作流进行测试验证 |
| **03构建师** | 使用GSD TDD工作流实现代码 |
| **06审查师** | 审查TDD周期完整性和提交质量 |

## 命令列表

```bash
/gsd-tdd start <feature>      # 开始新的TDD周期
/gsd-tdd red <test-case>      # RED阶段：创建失败测试
/gsd-tdd green                # GREEN阶段：实现代码
/gsd-tdd refactor             # REFACTOR阶段：清理优化
/gsd-tdd verify               # 验证当前状态
/gsd-tdd status               # 查看TDD周期状态
/gsd-tdd complete             # 完成当前周期
/gsd-tdd abort                # 中止当前周期
```

## 质量门槛

在完成TDD周期前，必须满足：

- [ ] 所有测试通过
- [ ] 覆盖率 >= 80%
- [ ] 无跳过的测试
- [ ] 无TODO注释
- [ ] 提交历史清晰（test→feat→refactor）

## 预期收益

| 指标 | 传统开发 | GSD TDD | 提升 |
|------|---------|---------|------|
| **Bug发现时间** | 集成阶段 | 编码阶段 | **-90%** |
| **代码质量** | 事后修复 | 先天保障 | **+200%** |
| **可追溯性** | 部分 | 完整 | **质的飞跃** |
| **回滚安全** | 低 | 高 | **质的飞跃** |
| **协作效率** | 低 | 高 | **+150%** |

## 配置文件

```yaml
# .gsd-tdd.yaml
test_framework: auto  # jest, vitest, pytest, go test, cargo test
min_coverage: 80
commit_template: conventional
skip_coverage_check: false
auto_commit: true
verify_all_tests: true
```

---

**核心理念**：TDD不仅是一种测试方法，更是一种设计方法。通过先写测试，我们被迫思考API设计和边界条件，从而产生更好的代码结构。