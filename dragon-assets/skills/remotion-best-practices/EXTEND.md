# Remotion Best Practices EXTEND.md

## 默认Remotion最佳实践配置

---

## 自定义组件结构

### flat-structure
- organization: single_folder
- composition: linear_sequence
- reusability: limited

### component-library
- organization: separate_compositions_ui
- composition: atomic_building_blocks
- reusability: high

---

## 自定义时间控制

### frame-based
- unit: exact_frames
- precision: pixel_perfect

### duration-based
- unit: time_seconds
- precision: time_based_interpolation

---

## 自定义渲染策略

### local-rendering
- location: developer_machine
- speed: hardware_limited

### lambda-rendering
- location: aws_lambda
- speed: horizontally_scaled

---

## 配置优先级

CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置

---

## 使用示例

### 简单动画
- structure: flat-structure
- timing: frame-based
- rendering: local-rendering

### 参数化视频
- structure: component-library
- timing: duration-based
- rendering: lambda-rendering
