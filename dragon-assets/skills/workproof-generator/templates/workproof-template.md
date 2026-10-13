# WorkProof - {{issue_id}}

## 基本信息

| 字段 | 值 |
|------|-----|
| **Issue ID** | {{issue_id}} |
| **标题** | {{issue_title}} |
| **PR链接** | {{pr_url}} |
| **生成时间** | {{generated_at}} |

## CI状态

{{ci_status_emoji}} **{{ci_status_upper}}**

{{#if ci_build_url}}
- 构建日志: {{ci_build_url}}
{{/if}}

## 代码变更统计

| 指标 | 数值 |
|------|------|
| 变更文件数 | {{files_changed}} |
| 新增行数 | +{{additions}} |
| 删除行数 | -{{deletions}} |
| 净增行数 | {{net_lines}} |

### 变更文件列表

{{#each changed_files}}
- `{{this}}`
{{/each}}

## 测试覆盖率

{{#if test_coverage}}
**{{test_coverage}}%**

{{#if coverage_badge}}
![Coverage]({{coverage_badge}})
{{/if}}
{{else}}
未报告
{{/if}}

## 复杂度评分

{{complexity_stars}} ({{complexity_score}}/10)

### 复杂度因素

| 因素 | 权重 | 得分 |
|------|------|------|
| 文件数量 | {{weights.file_count}} | {{file_score}} |
| 代码行数 | {{weights.lines_changed}} | {{line_score}} |
| 测试覆盖 | {{weights.test_presence}} | {{test_score}} |
| 依赖数量 | {{weights.dependency_count}} | {{dep_score}} |

## 演示视频

{{#if demo_video_url}}
[查看演示]({{demo_video_url}})
{{else}}
无
{{/if}}

## 验证备注

{{#each verification_notes}}
- {{this}}
{{/each}}

## 变更摘要

{{change_summary}}

---

*此工作证明由 WorkProof Generator 自动生成*
*生成时间: {{generated_at}}*
*验证状态: {{#if is_verified}}✅ 已验证{{else}}❌ 未通过{{/if}}*
