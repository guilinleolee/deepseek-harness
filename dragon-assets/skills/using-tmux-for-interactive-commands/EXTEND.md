# Using Tmux for Interactive Commands EXTEND.md

## 默认Tmux配置

---

## 自定义会话管理

### single-session
- sessions: one_only
- switching: not_needed
- persistence: manual
- complexity: minimal

### multi-session
- sessions: named_sessions
- switching: session_list
- persistence: detach_attach
- complexity: moderate

### project-sessions
- sessions: per_project
- switching: context_aware
- persistence: automatic_restore
- complexity: high

---

## 自定义窗口布局

### single-pane
- layout: one_window_only
- splits: none
- navigation: simple
- use_case: single_task

### split-vertical
- layout: side_by_side
- splits: vertical_only
- navigation: pane_selection
- use_case: comparison_monitoring

### split-grid
- layout: 2x2_or_more
- splits: both_directions
- navigation: directional
- use_case: multitasking_dashboard

### tiled-layout
- layout: auto_tiled
- splits: evenly_distributed
- navigation: systematic
- use_case: equal_importance

---

## 自定义环境持久化

### no-persistence
- save: never
- restore: fresh_start
- state: volatile
- use_case: ephemeral_tasks

### session-persistence
- save: on_detach
- restore: on_attach
- state: directory_based
- use_case: daily_work

### continuous-persistence
- save: real_time
- restore: crash_recovery
- state: fully_snapshot
- use_case: critical_workflows

---

## 自定义命令自动化

### manual-start
- startup: empty_session
- commands: user_entered
- scripting: none
- efficiency: manual

### profile-based
- startup: named_profile
- commands: preconfigured
- scripting: shell_scripting
- efficiency: automated

### programmatic
- startup: tmux_scripting
- commands: dynamically_generated
- scripting: full_api
- efficiency: highly_automated

---

## 自定义同步操作

### no-sync
- typing: independent_panes
- broadcasting: none
- collaboration: sequential
- use_case: independent_tasks

### sync-panes
- typing: mirrored_input
- broadcasting: all_panes
- collaboration: simultaneous
- use_case: parallel_operations

### selective-sync
- typing: group_based
- broadcasting: targeted_groups
- collaboration: flexible
- use_case: mixed_workflow

---

## 自定义状态监控

### basic-status
- indicators: session_list_only
- details: minimal
- updates: manual_refresh
- awareness: low

### enhanced-status
- indicators: session_window_pane
- details: process_info
- updates: automatic_refresh
- awareness: medium

### rich-status
- indicators: comprehensive_info
- details: cpu_memory_network
- updates: real_time_monitoring
- awareness: high

---

## 配置优先级

CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置

---

## 使用示例

### 快速任务
- session: single-session
- layout: single-pane
- persistence: no-persistence
- automation: manual-start
- sync: no-sync
- monitoring: basic-status

### 开发环境
- session: project-sessions
- layout: split-grid
- persistence: session-persistence
- automation: profile-based
- sync: selective-sync
- monitoring: enhanced-status

### 运维仪表板
- session: multi-session
- layout: tiled-layout
- persistence: continuous-persistence
- automation: programmatic
- sync: sync-panes
- monitoring: rich-status
