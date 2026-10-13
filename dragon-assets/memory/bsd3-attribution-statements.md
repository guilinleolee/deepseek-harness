---
name: bsd3-attribution-statements
description: BSD-3-Clause 协议合规模板（小红书 / 公众号 / H5 / 视频号 / 微博）· Stage 45.1 dsh-balance-meter (BSD-3-Clause)
metadata:
  node_type: memory
  type: reference
  originSessionId: stage-451-dsh-balance-meter
  modified: 2026-08-24T11:38:00.000Z
---

# BSD-3-Clause 版权声明模板 · Ghost011118/dsh-balance-meter 全平台

> **Why**：天龙阶段 45.1 dsh-balance-meter 是 **BSD-3-Clause ✅**（R1 评估 2026-08-24）。这是天龙**第 1 个 BSD-3-Clause 集成**（Stage 45.0 加入治理基线时定位"边界 GO"）。BSD-3 比 MIT 略严格（**明示**不得用作者名背书），与 AGPL 不同：BSD-3 不传染、商业可用、无网络服务条款触发。
>
> **How to apply**：用 BSD-3-Clause 项目时，可商用 + 修改 + 转授权；但必须在所有副本保留 3 项强条款（版权 / 免责声明 / 不得背书）。博客平台**可不挂版权声明**（BSD-3 不传染），但建议在内部文档标注。

---

## 一、原始声明（保留原文 · 1,519 B / 22 行标准 + 7 行注释）

```
BSD 3-Clause License

Copyright (c) 2026, Ghost011118
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
```

**完整 LICENSE**：https://github.com/Ghost011118/dsh-balance-meter/blob/master/LICENSE

---

## 二、BSD-3-Clause vs MIT 关键差异

| 条款 | MIT | **BSD-3-Clause** |
|---|---|---|
| 拷贝/分发自由 | ✅ | ✅ |
| 版权保留 | ✅ | ✅ |
| 免责声明 | ✅ | ✅ |
| **不得用作者名背书** | § 4 模糊 | § 3 **明示** |
| **不得用贡献者名背书** | ❌ | ✅ 新增 |
| **不得背书条款 source disclaimer** | ❌ | ✅ 新增 |
| 商用 | ✅ | ✅ |
| 网络服务条款触发 | ❌ | ❌ |

> BSD-3 比 MIT **严格 1 项**：**第 3 条明示不得用 copyright holder 或 contributors 的名字背书衍生作品**。这是 BSD-3 与 MIT 的核心区别。
> 
> BSD-3 不传染（vs AGPL-3.0 网络服务条款触发）。BSD-3 不强制 NOTICE（vs Apache-2.0）。

---

## 三、模板 1 · 小红书「个人简介」或置顶笔记（≤ 100 字）

```
💰 DSH 余额读取工具基于开源项目
   Ghost011118/dsh-balance-meter（BSD-3-Clause）
   github.com/Ghost011118/dsh-balance-meter
   本账号所有内容均为本人原创，使用工具部分已注明。
```

## 四、模板 2 · 公众号「关于 laoli_bro_2026」页（≤ 200 字）

```
关于本公众号使用的 DSH 余额读取能力

本公众号所有「DeepSeek 账户余额显示」「单 session cost 估算」
「peak/off-peak 分时定价」「per-model 价格自动切换」
类内容，使用的余额读取工具来自开源项目
DSH Balance Meter（GitHub: Ghost011118/dsh-balance-meter），
遵循 BSD 3-Clause 协议。

• 项目仓库：https://github.com/Ghost011118/dsh-balance-meter
• BSD-3-Clause 全文：https://opensource.org/licenses/BSD-3-Clause

文案 / 选题 / 配图 / 视频为本账号原创，
工具部分依据上述开源协议合规使用，特此致谢。
```

## 五、模板 3 · H5 footer（嵌入页底部）

```html
<footer class="bsd3-attribution">
  <small>
    本页 DSH 余额读取基于
    <a href="https://github.com/Ghost011118/dsh-balance-meter">Ghost011118/dsh-balance-meter</a>，
    遵循 <a href="https://opensource.org/licenses/BSD-3-Clause">BSD-3-Clause</a>。
    不得用上游作者名背书衍生作品（BSD §3）。
  </small>
</footer>
```

## 六、模板 4 · 视频号 / 抖音 / B 站简介（≤ 60 字）

```
DSH 余额读取：Ghost011118/dsh-balance-meter（BSD-3）
```

## 七、模板 5 · 微博置顶（≤80 字）

```
本微博所用 DSH 余额读取工具来自
Ghost011118/dsh-balance-meter，
BSD 3-Clause 开源协议（github.com/Ghost011118/dsh-balance-meter）。
```

## 八、红线 · 不要这样写

| ❌ 错误示例 | ⚠️ 问题 |
|-----------|--------|
| `余额读取 by Ghost011118，独家授权` | 🔴 **违反 BSD-3 § 3**（不得用作者名背书）|
| `DSH 余额 © Ghost011118` | 🔴 **混淆版权归属** |
| 完全不放版权声明 | 🟡 **不强制**（BSD-3 不传染），但建议保留 |
| `官方认证 / 官方授权` | 🔴 **背书违反**（措辞 A 边界）|

## 九、4 条硬约束（必须遵守）

1. **LICENSE verbatim 落盘**：`skills/dsh-balance-meter-integration/LICENSE`（1,548 B verbatim · 29 行）
2. **保留 3 项强条款**：版权段 + 免责声明 + 不得背书（第 3 条）
3. **不得用上游作者名做背书**（BSD-3 § 3）
4. **H5 嵌入附 Source 链接**（指向 dragon-engine fork 路径）

---

## 十、5 场景商用边界（BSD-3 比 MIT 严格 1 项）

| 场景 | 判断 | 依据 |
|------|------|------|
| C1 用 dsh-balance-meter 读取余额 | ✅ 可商用 + 注明 | BSD § 1 + § 2 |
| C2 接甲方商单（仅交付余额读取报告）| ✅ 可商用 | BSD § 1 + § 2 |
| C2' 把 dsh-balance-meter 包装为"Ghost011118 独家技术"卖甲方 | 🔴 **禁止**（违反 BSD § 3 不得背书）|
| C3 博主全息公众号封面 | ✅ 可商用 | BSD-3 不传染 |
| C4 用 dsh-balance-meter 做知识付费课程 | 🔴 **禁止商业化**（BSD § 3）|
| C5 整包闭源转售 | 🔴 **禁止**（BSD § 1 要求源 redistribution 时版权段保留；闭源 = 违反 § 2 binary 时"documentation 包含版权段"）|

---

## 十一、检查清单（每次发布含 dsh-balance-meter 输出时）

- [ ] 这篇是用 dsh-balance-meter 读取的吗？ → 是 → 触发版权声明
- [ ] 是个人 IP 自营内容（C1）吗？ → 是 → 在小红书置顶/简介挂模板 1
- [ ] 是公众号发布的（H5 或 PNG）？ → H5 → 加模板 3 footer；PNG → 模板 2 关于页已挂即可
- [ ] 是给甲方的商单（C2）吗？ → 仅交付 PNG → **不挂版权声明**（客户拿到的是图片不是源码，BSD-3 不传染）
- [ ] 是 H5 嵌入页吗？ → 在 footer 加模板 3 + Source 链接到 dragon-engine fork
- [ ] 是否用 Ghost011118 名字做推广？ → 禁止（BSD-3 § 3）

---

## 十二、相关链接

- [[stage-451-dsh-balance-meter]] — stage 45.1 主题文件（待写）
- [[dsh-ecosystem-license-policy]] — DSH 生态 NOASSERTION 治理基线 V1.0（含 BSD-3-Clause 接受）
- [[mit-attribution-statements §十七]] — stage 45 dsh-eval-bridge 借鉴档模板（与本节 BSD-3 模板对照）
- 上游 LICENSE：https://raw.githubusercontent.com/Ghost011118/dsh-balance-meter/master/LICENSE
- BSD-3-Clause 协议全文：https://opensource.org/licenses/BSD-3-Clause
- 上游仓库：https://github.com/Ghost011118/dsh-balance-meter
