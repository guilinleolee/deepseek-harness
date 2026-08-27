# 个人账号记忆与复盘

只在用户明确开启后使用。本模块让 Skill 参考同一位创作者自己确认过的经验；它不是云端数据库，也不收集其他用户信息。

## 隐私与边界

- 默认目录：`$CODEX_HOME/data/media-publish-check/`；`CODEX_HOME` 未设置时为 `~/.codex/data/media-publish-check/`。
- 脚本不包含网络请求、登录、上传、遥测或共享功能。每个本地账号目录相互独立；只读取本次用户指定的账号代号。
- 资料目录在 Skill 文件夹和 Git 仓库之外，不随安装包、提交或发布上传。不要把该目录复制进公开项目。
- 默认只保存最小化复盘数据：平台、内容形式、风险标签、审核结论、结果状态和脱敏摘要。不要保存原片、完整正文、账号密码、电话、订单、地址、二维码或他人未授权内容。
- 用户可用 `forget` 删除任一案例；不确定结果一律记录为 `unknown`。低播放、主观感受和单次猜测不能当作平台处罚证据。

## 自然语言入口

| 用户表达 | 执行动作 |
|---|---|
| `开启个人账号记忆，账号叫小水` | 创建本地空档案；只确认账号代号和常用平台。 |
| `保存这次审核到我的经验库` | 记录这次审核的最小化案例；先让用户确认简短摘要。 |
| `这条后来被提示站外导流，帮我复盘` | 记录用户确认的结果和已脱敏通知摘要。 |
| `按我的经验库审核这条抖音视频` | 只取最多 3 条相关、已启用的个人提醒，再完成正常审核。 |
| `查看/关闭/删除我的账号记忆` | 展示本地状态、停止读取，或删除指定案例。 |

不要一次发长问卷。只有在用户选择保存或复盘时，使用这张复盘卡：

```text
账号代号：...
这条是否发布：已发布 / 未发布 / 未知
实际结果：正常 / 收到平台通知 / 驳回 / 未知
平台通知摘要（可选，已脱敏）：...
```

## 本地命令

以下命令仅操作用户本机。`<账号代号>` 使用英文、数字、短横线或下划线，例如 `xiaoshui`。

```bash
# 首次开启
python3 scripts/account_memory.py init --account <账号代号> --platforms douyin,xiaohongshu

# 保存一次审核（不保存原素材）
python3 scripts/account_memory.py save-review --account <账号代号> --platform douyin \
  --content-type video --risk-tags ai-label,platform-mention --predicted-risk R2 \
  --summary "已检查封面与口播，待补成片画面"

# 复盘实际结果；case-id 由 save-review 输出
python3 scripts/account_memory.py feedback --account <账号代号> --case-id <案例ID> \
  --outcome platform-notice --notice-summary "平台提示已脱敏"

# 根据真实反馈生成候选提醒；不会自动启用
python3 scripts/account_memory.py rebuild-candidates --account <账号代号>
python3 scripts/account_memory.py activate --account <账号代号> --candidate-id <候选ID>
python3 scripts/account_memory.py deactivate --account <账号代号> --candidate-id <候选ID>
python3 scripts/account_memory.py disable --account <账号代号>

# 下次审核前取相关经验；最多返回 3 条
python3 scripts/account_memory.py context --account <账号代号> --platform douyin \
  --risk-tags ai-label,platform-mention
```

## 迭代规则

1. **官方规则**：仅能以官方链接、条款和核验日期更新；个人案例永不改写公开规则。
2. **个人案例**：收到明确平台通知后，可生成“候选账号提醒”；一次案例也只代表该账号的一次观察。
3. **生效规则**：必须由账号主人明确启用。三条以上同类、已确认反馈会提高候选强度，但仍不自动生效。
4. **正常发布**：只用于校准误报倾向，不抵消法律、平台官方规则、AI 标识、授权或事实待证要求。
5. **过期与撤回**：候选提醒默认 90 天后需要复核；用户可删除案例或停用规则。

输出个人经验时标明：`账号经验，不等于平台官方规则`。不要用它承诺“必过审”或“绝不会限流”。
