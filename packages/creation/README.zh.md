# creation/ — 内容创作产物域

[English](README.md) | 中文

creation 族拥有 agent 写入成品的持久化磁盘面：产物库根目录下一次创作一个目录——成品文件放项目根，中间素材放 `assets/`，`.dsh-output.json` 是唯一元数据。Web 端内容创作工作台（[`dsh-client-ui-content-studio`](../client/ui-content-studio)）通过下面的 Remote 读取；写入始终是 agent 通过自身工具完成的职责。

| 包 | 职责 | ctx key |
|---|---|---|
| `content-outputs/` | 只读 `contentOutputs/list` Remote，每次调用从磁盘投影产物库 | —（仅 Remote 网关） |
| `content-schedule/` | `contentSchedule/list`、`put`、`delete` Remote，读写库根的 `_schedule.json` 发布日历 | —（仅 Remote 网关） |
| `content-topics/` | `contentTopics/list`、`put`、`delete` Remote，读写库根的 `_topics.json` 选题库 | —（仅 Remote 网关） |

磁盘格式为 `formatVersion 0`，无兼容性承诺，遵循仓库的预发布立场。
