# creation/ — the content-creation outputs domain

English | [中文](README.zh.md)

The creation family owns the durable surface the agent writes finished content into: one directory per creation under the outputs library root, with finished files at the project root, intermediate material under `assets/`, and `.dsh-output.json` as the only metadata. The web Content Studio ([`dsh-client-ui-content-studio`](../client/ui-content-studio)) reads it through the Remotes below; writing stays the agent's job through its own tools.

| Package | Role | ctx key |
|---|---|---|
| `content-outputs/` | Read-only `contentOutputs/list` Remote projecting the outputs library from disk per call | — (Remote-only gateway) |
| `content-schedule/` | `contentSchedule/list`, `put`, `delete` Remote over the library's `_schedule.json` publication calendar | — (Remote-only gateway) |
| `content-topics/` | `contentTopics/list`, `put`, `delete` Remote over the library's `_topics.json` topic bank | — (Remote-only gateway) |

The on-disk formats are `formatVersion 0` with no compatibility promise, per the repository's pre-release stance.
