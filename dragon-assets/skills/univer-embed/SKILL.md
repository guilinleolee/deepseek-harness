---
name: univer-embed
description: Embed one Univer Unit inside another through DSH tools and the Lite Interface. Use proactively when a Sheet, Doc, Slide, Base, Board, dashboard, report, presentation, database, or canvas should display or interact with content from another Unit in the same .univer file.
metadata:
  source: dream-num/dsh-univer-office v0.2.9 (Apache-2.0)
  mirrored: 2026-08-26
  version_upstream: 0.2.9
---

> **Apache-2.0 镜像说明**：本文件是上游 `dream-num/dsh-univer-office` 仓库 `skills/univer-embed/SKILL.md` 的镜像。
> **完整上游文件**：<https://raw.githubusercontent.com/dream-num/dsh-univer-office/main/skills/univer-embed/SKILL.md>

---

# Embed Units（镜像摘要）

**先加载 `univer` + 宿主/子 Unit 的 skill。** 两个 Unit 在**同一 `.univer` 文件 + 同一 draft worktree**，各用精确 `unitId` 寻址。

Viewer 只支持**一层 Embed**。宿主可含多个 sibling Embed，但**不要**嵌入一个本身已含 Embed 的 Unit（用 sibling 或 link）。

未知 API 先 `univer_api`（`FUniver.createEmbed` / `FEmbed` / `FEmbedHostSurface` / `ICreateEmbedParams` / `IEmbedDescriptor`）。

**先创建并验证子 Unit**。用其精确 `unitId` + 真实 Unit 类型在 ResourceRef 里。

- `SheetFloating` 宿主要显式 drawing 放置
- 绝对画布 bounds：`{ kind: univerAPI.Enum.SheetDrawingAnchorType.None, bounds: { left, top, width, height } }`

例：把 Doc 作为 Sheet tab 嵌入（`univer_execute` 针对宿主 Sheet Unit）：

```js
const hostUnitId = "<host-unit-id>";
const childUnitId = "<child-unit-id>";
const sourceRef = "#unit=" + childUnitId + "&type=doc";
const embed = univerAPI.createEmbed({
  embedId: "<embed-id>",
  host: {
    unitId: hostUnitId,
    surface: univerAPI.Enum.FEmbedHostSurface.SheetTab,
  },
  content: {
    unitType: univerAPI.Enum.UniverInstanceType.UNIVER_DOC,
    ref: sourceRef,
  },
  interaction: "interactive",
});
const child = await embed.loadAsync();
if (!child || child.getId() !== childUnitId) {
  throw new Error("Embedded child mismatch");
}
const descriptor = embed.getDescriptor();
if (descriptor.source?.ref !== sourceRef) {
  throw new Error("Embedded ResourceRef mismatch");
}
return { childUnitId: child.getId(), descriptor };
```

改子类型时，`unitType` 与 ResourceRef 的 `type` **必须同步**改成相同的真实类型。

## 验证（每次 mutation 后）

1. 新 `univer_execute` 重读返回的 child Facade + descriptor
2. 验精确 child Unit ID/type、ResourceRef、host surface、interaction 模式、宿主 anchor/放置
3. 必要时用 `univer_inspect` 同时检视宿主 + 子 Unit
4. 按宿主 Unit Skill 的 `univer_screenshot` 流程检视 PNG（确认子内容在宿主内渲染）
   - **结构 ResourceRef 读回仍然必需** —— 截图本身不能证明子 ID/type 绑定
5. 按 `univer` ready/status 流程交付

## 上游原文指针

- 完整 SKILL.md：<https://raw.githubusercontent.com/dream-num/dsh-univer-office/main/skills/univer-embed/SKILL.md>
