---
name: calendar-column-benchmark-repos
description: 内容日历栏目对标仓库 2026-09-27 GitHub API 核验事实（stars/license/活跃度），引用前需复查时效
metadata:
  node_type: memory
  type: reference
  originSessionId: sess_subagent_agent_3724ad1d-462a-4865-936b-8cb707e8d08a
---

内容日历栏目调研，2026-09-27 经 GitHub API / npm registry 逐一核验：

**任务 A 核验结论**
- fullcalendar/fullcalendar — 真实。20,654 stars，MIT，push 2026-09-05。
- inovector/mixpost — 真实。3,739 stars，MIT（此仓库为 Lite 版，README 明言"contains the Lite version of Mixpost Pro"），push 2026-03-16（已半年未更新，活跃度下降）。
- gitroomhq/postiz-app — 真实。36,360 stars，**AGPL-3.0**（不可抄代码），push 2026-09-26，极活跃。
- "workspace-mcp content-calendar" — **无法核验/疑似虚构**。GitHub 搜索 0 结果；"content-calendar mcp" 搜出的均为 0-9 star 无名小仓库，无可信对应。

**FullCalendar 许可划分（官网 pricing + npm 核验）**
- MIT 免费：@fullcalendar/core(7.1.0)、react、interaction（拖拽）、daygrid/timegrid（月/周/日）、list、multimonth、rrule、icalendar。
- 付费 Premium（$480 起，2-10 席位）：timeline、resource 系列视图、打印渲染；@fullcalendar/premium-common license 为 "SEE LICENSE IN LICENSE.md"（非 MIT）。

**备选组件关键差异**
- schedule-x/schedule-x — 2,585 stars，核心 MIT，但 **Drag-and-Drop/Resize/Sidebar/Drag-to-create/Resource/Gantt 全是付费功能**（€479/年）。拖拽改期需求下不可替代 FullCalendar。
- bigcalendar/react-big-calendar — 已从 jquense 迁移至 bigcalendar org。8,756 stars，MIT，push 2026-06-01。
- jkbrzt/rrule — 已从 jakubroztocil 迁移。3,744 stars，BSD-3-Clause（npm 确认），push 2024-06-27（稳定但低频维护）。
- calcom/cal.diy — 原 cal.com 已更名。48,662 stars，MIT，极活跃。数据模型：EventType(模板)/Booking(实例)/DestinationCalendar(外部镜像)/BookingDenormalized(查询投影)，schema 在 packages/prisma/schema.prisma。

**编辑日历/社媒排期参考**
- publishpress/publishpress-planner — GPLv2+，51 stars（GitHub），活跃（push 2026-09-25），基于 Automattic/edit-flow（366 stars，GPL-2.0，活跃）的 WordPress 编辑日历：custom status 驱动日历。
- socioboard/Socioboard-5.0 — 1,513 stars，license NOASSERTION（自定义）；socioboard/socioboard 6.0 仅 2 stars AGPL。
- brightbeanxyz/brightbean-studio — 2,376 stars，AGPL-3.0，活跃。
- Anil-matcha/Free-AI-Social-Media-Scheduler — 524 stars，MIT，活跃。
- inovector/MixpostApp — 132 stars，Mixpost Lite 预打包独立应用。

关联：[[content-studio-topic-library]] [[creation-column-benchmark-repos]]
