/**
 * 卡巴格企业平台 · 管理类 DSH 工具（栏目规划 v2 阶段 12，实例侧）。
 *
 * 注册 7 个经 HTTP 调平台 console API 的管理工具（Node 22 全局 fetch）：
 * 只读 user_list / user_quota_query / audit_query；变更 user_create /
 * user_update / user_reset_password / user_set_disabled。
 *
 * 鉴权：服务令牌（`kbsvc-…`）从插件 config 或实例 env（KABAGE_SERVICE_TOKEN）
 * 注入，随每个请求以 `Authorization: Bearer` 携带。**安全呈现决策**：
 * 不探测令牌角色——7 个工具始终注册；readonly 令牌调用变更工具时由平台侧
 * 403 转译为中文错误结果（保持注册逻辑与令牌角色解耦）。
 * 一次性密码（user_create / user_reset_password）会留在管理员实例的会话
 * 记录中——结果附带提示引导尽快改密（详见 README「会话记录含敏感结果」节）。
 *
 * 平台 401/403/4xx/网络错 → execute 抛错 → 模型收到 `Error: <中文理由>`；
 * 列表结果截断（≤50 条）防超长。零 npm 依赖（仅 peer @deepseek-ai/cordis）。
 */

export const name = 'kabage-admin-tools'

/** 服务依赖声明：本插件全部能力挂在 ctx.tools 上（缺失即拒绝激活，fail-loud）。 */
export const inject = ['tools']

/** 列表类结果的最大条数（防工具结果超长）。 */
const LIST_LIMIT = 50

export function apply(ctx, config) {
  const baseUrl = String(config?.baseUrl ?? process.env.KABAGE_ADMIN_BASE_URL ?? 'http://127.0.0.1:8460').replace(/\/+$/, '')
  const defaultInstance = String(config?.defaultInstance ?? process.env.KABAGE_ADMIN_DEFAULT_INSTANCE ?? 'e01')
  const tokenOf = () => {
    const fromConfig = typeof config?.token === 'string' ? config.token : ''
    return fromConfig !== '' ? fromConfig : String(process.env.KABAGE_SERVICE_TOKEN ?? '')
  }

  /**
   * 调平台 console API 并把非 200 转译为中文工具错误（execute 抛错 → 模型
   * 收到 isError 结果）。401/403 带稳定原因码，便于模型/管理员定位。
   */
  async function callPlatform(method, path, body, exec) {
    const token = tokenOf()
    if (token === '') {
      throw new Error('平台管理工具未配置服务令牌：请管理员执行 add-service-token 生成后，将 KABAGE_SERVICE_TOKEN 注入本实例 env（原因码 token_missing）')
    }
    let res
    try {
      res = await fetch(`${baseUrl}${path}`, {
        method,
        headers: { 'content-type': 'application/json', authorization: `Bearer ${token}` },
        body: body === undefined ? undefined : JSON.stringify(body),
        signal: exec.signal,
      })
    } catch (error) {
      throw new Error(`无法连接平台管理接口（${baseUrl}），请确认平台 daemon 在运行（原因码 unreachable）: ${error?.message ?? error}`)
    }
    let payload = {}
    try { payload = await res.json() } catch { /* 非 JSON 响应按空处理 */ }
    if (res.status === 200) return payload
    if (res.status === 401) throw new Error('平台认证失败：服务令牌无效或已被撤销，请联系管理员重新签发（原因码 auth_failed）')
    if (res.status === 403) throw new Error('权限不足：readonly 服务令牌不能执行变更操作，请联系管理员签发 admin 令牌（原因码 forbidden）')
    const detail = typeof payload?.error === 'string' && payload.error !== '' ? payload.error : `HTTP ${res.status}`
    throw new Error(`平台拒绝该操作（${res.status}）: ${detail}`)
  }

  /** raw 注册（零依赖）：输入校验由本工具自带。 */
  const requireField = (args, name, description) => {
    const value = args?.[name]
    if (typeof value !== 'string' || value.trim() === '') {
      throw new Error(`参数 ${name} 必填（${description}）`)
    }
    return value.trim()
  }

  const output = {
    // annotation-only unconstrained schema：结果为任意 JSON（registry 校验快照）。
    schema: {},
    render: (_args, value) => [{ type: 'text', text: JSON.stringify(value) }],
  }
  // UI render intent（仓库规则：设计期确定）：管理操作统一 generic 卡片。
  const presentCall = (title) => (args) => ({ card: 'generic', title, kind: '管理操作', content: JSON.stringify(args ?? {}) })

  const PWD_NOTICE = '一次性密码已在此结果与会话记录中可见，请引导成员尽快修改密码（也可在管理台成员页重置）。'

  /* ── 只读三工具 ─────────────────────────────────────────────────────────── */

  ctx.tools.register({
    name: 'user_list',
    description: '查询卡巴格平台成员列表（账号/部门/角色/启用状态/实例/当月点数用量摘要）。最多返回 50 条。',
    parameters: { type: 'object', properties: {} },
    output,
    presentCall: presentCall('平台成员列表'),
    async execute(_args, exec) {
      const data = await callPlatform('GET', '/console/api/member/list', undefined, exec)
      const members = Array.isArray(data.members) ? data.members.slice(0, LIST_LIMIT) : []
      return {
        month: data.month ?? null,
        total: Array.isArray(data.members) ? data.members.length : 0,
        shown: members.length,
        truncated: Array.isArray(data.members) && data.members.length > LIST_LIMIT,
        members,
      }
    },
  })

  ctx.tools.register({
    name: 'user_quota_query',
    description: '查询某成员当月用量与额度（点数/额度/余量；旧制 tokens 账号按旧口径标注）。',
    parameters: {
      type: 'object',
      properties: { account: { type: 'string', description: '成员账号（邮箱）' } },
      required: ['account'],
      additionalProperties: false,
    },
    output,
    presentCall: presentCall('查询成员用量'),
    async execute(args, exec) {
      const account = requireField(args, 'account', '成员账号（邮箱）')
      return callPlatform('GET', `/console/api/member/usage?account=${encodeURIComponent(account)}`, undefined, exec)
    },
  })

  ctx.tools.register({
    name: 'audit_query',
    description: '查询平台审计日志（谁/何时/对谁/动作/结果，最新在前）。limit 上限 50；action 为前缀（如 auth、member、guard.deny）。',
    parameters: {
      type: 'object',
      properties: {
        action: { type: 'string', description: 'action 前缀过滤（可选，如 auth / member.create / guard.deny）' },
        actor: { type: 'string', description: '账号关键词过滤（可选）' },
        limit: { type: 'integer', description: '返回条数上限（可选，默认 20，最大 50）' },
      },
      additionalProperties: false,
    },
    output,
    presentCall: presentCall('平台审计查询'),
    async execute(args, exec) {
      const params = new URLSearchParams()
      if (typeof args?.action === 'string' && args.action !== '') params.set('action', args.action)
      if (typeof args?.actor === 'string' && args.actor !== '') params.set('actor', args.actor)
      const requested = Number.isInteger(args?.limit) ? args.limit : 20
      const limit = Math.max(1, Math.min(requested, LIST_LIMIT))
      params.set('limit', String(limit))
      const data = await callPlatform('GET', `/console/api/audit?${params.toString()}`, undefined, exec)
      const events = Array.isArray(data.events) ? data.events.slice(0, LIST_LIMIT) : []
      return {
        count: events.length,
        truncated: events.length >= LIST_LIMIT,
        hint: '需要更多条目请缩小 action/actor 过滤后重试',
        events,
      }
    },
  })

  /* ── 变更四工具（readonly 令牌调用时平台 403 → 中文错误）────────────────── */

  ctx.tools.register({
    name: 'user_create',
    description: `在平台创建成员账号（自动签发虚拟钥匙）。role 仅 employee/auditor。${PWD_NOTICE}`,
    parameters: {
      type: 'object',
      properties: {
        account: { type: 'string', description: '新成员账号（邮箱形，如 name@company）' },
        department: { type: 'string', description: '部门（可选，缺省「未分配」）' },
        role: { type: 'string', description: '角色：employee（缺省）或 auditor；创建 admin 需管理员在管理台操作' },
        password: { type: 'string', description: '初始密码（可选；缺省由平台自动生成并在结果中一次性返回）' },
        instance: { type: 'string', description: `绑定实例 id（可选，缺省 ${defaultInstance}）` },
      },
      required: ['account'],
      additionalProperties: false,
    },
    output,
    presentCall: presentCall('创建平台成员'),
    async execute(args, exec) {
      const account = requireField(args, 'account', '新成员账号（邮箱形）')
      const body = {
        account,
        instance: typeof args.instance === 'string' && args.instance !== '' ? args.instance : defaultInstance,
        role: args.role === 'auditor' ? 'auditor' : 'employee',
      }
      if (typeof args.department === 'string' && args.department !== '') body.department = args.department
      if (typeof args.password === 'string' && args.password !== '') body.password = args.password
      const data = await callPlatform('POST', '/console/api/member/create', body, exec)
      return { account: data.account, instance: data.instance, password: data.password, notice: PWD_NOTICE }
    },
  })

  ctx.tools.register({
    name: 'user_update',
    description: '更新成员的部门或角色（role 仅 employee/auditor；至少提供一个字段）。',
    parameters: {
      type: 'object',
      properties: {
        account: { type: 'string', description: '成员账号' },
        department: { type: 'string', description: '新部门（可选）' },
        role: { type: 'string', description: '新角色：employee 或 auditor（可选）' },
      },
      required: ['account'],
      additionalProperties: false,
    },
    output,
    presentCall: presentCall('更新平台成员'),
    async execute(args, exec) {
      const account = requireField(args, 'account', '成员账号')
      const body = { account }
      if (args.department !== undefined) body.department = String(args.department)
      if (args.role !== undefined) body.role = args.role === 'auditor' ? 'auditor' : 'employee'
      if (body.department === undefined && body.role === undefined) {
        throw new Error('至少提供 department 或 role 之一')
      }
      return callPlatform('POST', '/console/api/member/update', body, exec)
    },
  })

  ctx.tools.register({
    name: 'user_reset_password',
    description: `重置成员密码：平台生成新密码一次性返回，该成员全部会话立即下线。${PWD_NOTICE}`,
    parameters: {
      type: 'object',
      properties: { account: { type: 'string', description: '成员账号' } },
      required: ['account'],
      additionalProperties: false,
    },
    output,
    presentCall: presentCall('重置成员密码'),
    async execute(args, exec) {
      const account = requireField(args, 'account', '成员账号')
      const data = await callPlatform('POST', '/console/api/member/reset-password', { account }, exec)
      return { account: data.account ?? account, password: data.password, notice: PWD_NOTICE }
    },
  })

  ctx.tools.register({
    name: 'user_set_disabled',
    description: '启用或禁用成员账号（禁用 = 立即下线 + 吊销虚拟钥匙；启用 = 按历史白名单重签）。',
    parameters: {
      type: 'object',
      properties: {
        account: { type: 'string', description: '成员账号' },
        disabled: { type: 'boolean', description: 'true=禁用，false=启用' },
      },
      required: ['account', 'disabled'],
      additionalProperties: false,
    },
    output,
    presentCall: presentCall('启用/禁用平台成员'),
    async execute(args, exec) {
      const account = requireField(args, 'account', '成员账号')
      if (typeof args.disabled !== 'boolean') throw new Error('参数 disabled 必填且必须是布尔值（true=禁用，false=启用）')
      return callPlatform('POST', `/console/api/member/${args.disabled ? 'disable' : 'enable'}`, { account }, exec)
    },
  })
}
