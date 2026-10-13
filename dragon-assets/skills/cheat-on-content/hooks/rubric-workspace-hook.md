# rubric-workspace Hook

> **Rubric是工作台，不是博物馆** — 维护一个活的、可更新的评分标准。

## 核心原则

1. **Rubric必须反映当前数据**: 观察必须被数据验证
2. **被数据否定的观察必须删除**: 不能留着当"反面教材"
3. **新观察必须基于数据产生**: 不能基于直觉或假设
4. **更新需要全量重打分**: Bump阈值≥3次同一偏差才触发

## 触发时机

以下情况触发Rubric工作台检查:

| 触发场景 | 检查内容 |
|----------|----------|
| T+3d首次复盘完成 | 检查新数据是否否定现有观察 |
| T+7d最终复盘完成 | 检查是否需要新增观察 |
| 预测提交前 | 检查Rubric是否有与当前内容相关的观察 |
| Buffer接近耗尽 | 检查Rubric健康度 |

## 观察状态管理

### 观察生命周期

```
[新观察] → [待验证] → [已验证/已否定]
                            ↓
                      已否定 → 删除(不能留在Rubric里)
```

### 观察数据模型

```json
{
  "observation_id": "obs_001",
  "content": "职场内容ER普遍较高(≥7分)",
  "created_date": "2026-05-10",
  "created_based_on": ["2026-05-08-01", "2026-05-09-02"],
  "status": "verified|pending|rejected",
  "evidence": {
    "supporting_samples": 5,
    "contradicting_samples": 0,
    "match_rate": 1.0
  },
  "last_verified": "2026-05-20",
  "rejected_date": null,
  "rejected_reason": null,
  "updated_rubric_version": null
}
```

### 验证逻辑

每当有新的复盘数据时:

```python
def verify_observations(new_data: dict):
    """检查新数据是否影响现有观察"""
    for obs in rubric.observations:
        if obs.status == "verified":
            # 检查新数据是否与观察矛盾
            if contradicts(new_data, obs):
                obs.status = "pending_review"
                obs.contradicting_samples += 1

        if obs.status == "pending_review":
            if obs.contradicting_samples >= 3:
                # 自动标记为rejected
                obs.status = "rejected"
                obs.rejected_date = today()
                obs.rejected_reason = f"被{obs.contradicting_samples}条数据否定"
```

## 自动清理规则

### 已拒绝观察的处理

**已拒绝的观察不能删除后直接消失**，必须记录原因:

```json
{
  "observation_id": "obs_old_003",
  "content": "视频开头必须用数字才有冲击力",
  "status": "rejected",
  "rejected_date": "2026-05-20",
  "rejected_reason": "最近3条视频用反常识开头的HP更高",
  "replacement_observation": "obs_new_007"
}
```

### 已拒绝观察的反向生成

如果一个观察被大量否定，可以考虑生成**反向观察**:

```json
{
  "observation_id": "obs_new_007",
  "content": "反常识开头可能比数字开头更有冲击力(需要更多验证)",
  "status": "pending",
  "is_reverse_of": "obs_old_003",
  "evidence": {
    "supporting_samples": 3,
    "contradicting_samples": 0,
    "match_rate": 1.0
  }
}
```

## Rubric版本控制

### 版本历史

```json
{
  "rubric_versions": [
    {
      "version": "1.0",
      "date": "2026-05-01",
      "changes": "初始版本",
      "observations_count": 15
    },
    {
      "version": "1.1",
      "date": "2026-05-15",
      "changes": "删除obs_003，新增obs_007，更新obs_005",
      "observations_count": 14
    }
  ]
}
```

### 版本切换

如果需要回退到旧版本:

```bash
python3 skills/cheat-on-content/hooks/rubric-workspace.py revert --version 1.0
```

## 使用方式

```bash
# 查看Rubric健康度
python3 skills/cheat-on-content/hooks/rubric-workspace.py health

# 查看所有观察及其状态
python3 skills/cheat-on-content/hooks/rubric-workspace.py list --status pending

# 添加新观察
python3 skills/cheat-on-content/hooks/rubric-workspace.py add --content "新观察内容" --based-on "2026-05-24-01"

# 验证观察
python3 skills/cheat-on-content/hooks/rubric-workspace.py verify --obs-id obs_001 --result confirm

# 拒绝观察
python3 skills/cheat-on-content/hooks/rubric-workspace.py reject --obs-id obs_003 --reason "与最新数据矛盾"

# 触发Bump(全量重打分)
python3 skills/cheat-on-content/hooks/rubric-workspace.py bump --min-match-rate 0.8
```

## 配置

```json
{
  "rubric": {
    "workspace_mode": true,
    "auto_verify_on_retro": true,
    "auto_cleanup_on_reject": true,
    "bump_threshold": 3,
    "bump_min_match_rate": 0.8,
    "reverse_observation_threshold": 3
  }
}
```