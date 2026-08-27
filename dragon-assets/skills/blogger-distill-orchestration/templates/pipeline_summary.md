# Pipeline 执行摘要 — {{ blogger_name }}

**Blogger ID**: {{ blogger_id }}
**模式**: {{ mode }}
**步骤范围**: {{ step_range }}
**执行时间**: {{ elapsed_seconds }}s
**完成时间**: {{ completed_at }}

---

## 步骤结果

| 步骤 | 状态 | 耗时 | 关键指标 |
|------|------|------|---------|
| 1. 采集 | {{ "✅ 完成" if 1 in completed_steps else ("❌ 失败" if 1 in failed_steps else "⏭️ 跳过") }} | {{ step_timings.get(1, "—") }}s | {{ step_metrics.get(1, "") }} |
| 2. 验证 | {{ "✅ 完成" if 2 in completed_steps else ("❌ 失败" if 2 in failed_steps else "⏭️ 跳过") }} | {{ step_timings.get(2, "—") }}s | {{ step_metrics.get(2, "") }} |
| 3. 补全 | {{ "✅ 完成" if 3 in completed_steps else ("❌ 失败" if 3 in failed_steps else "⏭️ 跳过") }} | {{ step_timings.get(3, "—") }}s | {{ step_metrics.get(3, "") }} |
| 4. 分析 | {{ "✅ 完成" if 4 in completed_steps else ("❌ 失败" if 4 in failed_steps else "⏭️ 跳过") }} | {{ step_timings.get(4, "—") }}s | {{ step_metrics.get(4, "") }} |
| 5. 蒸馏 | {{ "✅ 完成" if 5 in completed_steps else ("❌ 失败" if 5 in failed_steps else "⏭️ 跳过") }} | {{ step_timings.get(5, "—") }}s | {{ step_metrics.get(5, "") }} |
| 6. 归档 | {{ "✅ 完成" if 6 in completed_steps else ("❌ 失败" if 6 in failed_steps else "⏭️ 跳过") }} | {{ step_timings.get(6, "—") }}s | {{ step_metrics.get(6, "") }} |

---

## 质量门控

- **V1 阻断**: {{ "是" if 1 in failed_steps else "否" }}
- **V6 阻断**: {{ "是" if 6 in failed_steps else "否" }}
- **DLQ 待处理**: {{ dlq_pending }}

---

## 输出文件

{{ range(output_files) | map("file_row") | join("\n") }}

---

{{ "# 错误详情" if failed_steps else "" }}

{{ failed_errors }}
