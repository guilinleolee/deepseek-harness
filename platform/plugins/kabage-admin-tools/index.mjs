/**
 * 卡巴格企业平台 · 管理类 DSH 工具（栏目规划 v2 阶段 12，实例侧）。
 *
 * 注册 9 个经 HTTP 调平台 console API 的管理工具（Node 22 全局 fetch）：
 * 只读 user_list / user_quota_query / audit_query；变更 user_create /
 * user_update / user_reset_password / user_set_disabled / user_set_quota /
 * user_reset_2fa。
 *
 * 鉴权：服务令牌（`kbsvc-…`）从插件 config 或实例 env（KABAGE_SERVICE_TOKEN）
 * 注入，随每个请求以 `Authorization: Bearer` 携带。**安全呈现决策**：
 * 不探测令牌角色——9 个工具始终注册；readonly 令牌调用变更工具时由平台侧
 * 403 转译为中文错误（保持注册逻辑与令牌角色解耦）。
 *
 * 一次性凭据：user_create 同时返回一次性密码与**虚拟钥匙 vkey**（平台侧
 * issueVkey 只在这一次响应里给明文，存储只有 SHA-256）。两者都原样回传并
 * 附醒目警示语；但 UI 卡片（presentCall）只渲染**脱敏后**的参数，明文凭据
 * 不进卡片/轨迹记录。
 *
 * 错误分层（稳定原因码，便于模型判断「重试 / 改参 / 找管理员」）：
 *   token_missing / insecure_transport / auth_failed / forbidden /
 *   not_found / rate_limited / platform_error / rejected / timeout /
 *   aborted / unreachable / response_too_large。
 *
 * 健壮性：单请求 10s 超时（自己造 AbortSignal，不依赖 exec.signal 一定存在）、
 * 5xx 短退避重试 1 次（默认只对只读 GET 自动重试——写操作幂等性未知，自动
 * 重试可能重复建号）、错误文案不泄露令牌与 URL 内嵌凭据。
 *
 * 零 npm 依赖（仅 peer @deepseek-ai/cordis），Node 22 全局 fetch。
 */

export const name = 'kabage-admin-tools'

/** 服务依赖声明：本插件全部能力挂在 ctx.tools 上（缺失即拒绝激活，fail-loud）。 */
export const inject = ['tools']

/** 列表类结果的最大条数（防工具结果超长）。 */
const LIST_LIMIT = 50

/** 单次平台请求超时（毫秒）。与平台侧抓取上限（10s）同量级：慢平台不拖死实例。 */
const REQUEST_TIMEOUT_MS = 10_000

/** 5xx 重试前的退避等待（毫秒）。短退避：5xx 多为瞬时故障，重试一次即可。 */
const RETRY_BACKOFF_MS = 250

/** 平台响应体上限（字节）。超过即报错，而不是把超大 JSON 灌进模型上下文。 */
const MAX_RESPONSE_BYTES = 5 * 1024 * 1024

/** 需要在 UI 卡片里打码的字段名（小写匹配）：明文凭据不进卡片/轨迹记录。 */
const SENSITIVE_KEYS = new Set([
  'password', 'passwd', 'pwd', 'pass', 'token', 'vkey', 'vkeys', 'secret',
  'apikey', 'api_key', 'authorization', 'bearer', 'credential', 'credentials',
  'cookie', 'session',
])

/** 工具允许写入的成员角色：admin 不开放给模型，避免提示注入式提权。 */
const ALLOWED_ROLES = new Set(['employee', 'auditor'])

/** 平台已有的全部角色（仅用于 user_list 的过滤值校验）。 */
const PLATFORM_ROLES = new Set(['admin', 'auditor', 'employee'])

/** user_list 可用的排序字段（白名单：不让任意字段名进排序器）。 */
const SORT_FIELDS = ['account', 'displayName', 'department', 'role', 'instance', 'pointsUsed', 'lastLogin']

/** 一次性的敏感结果警示语（密码 + 虚拟钥匙）。 */
const CREDENTIAL_WARNING = '⚠️ 敏感信息：下面的一次性密码与虚拟钥匙（vkey）只在本次结果里出现一次，平台只存哈希、无法找回。请立即经安全渠道转交本人并提醒尽快修改密码；vkey 等同密码，切勿贴入公开渠道或长期存储。'

/** 密码类结果的警示语（不含 vkey）。 */
const PWD_NOTICE = '一次性密码已在此结果与会话记录中可见，请引导成员尽快修改密码（也可在管理台成员页重置）。'

/** 回环主机判定：Bearer 令牌走明文 HTTP 时只有回环目标可接受。 */
const isLoopbackHost = (hostname) => {
  const h = String(hostname ?? '').toLowerCase().replace(/^\[|\]$/g, '')
  if (h === 'localhost' || h === '::1' || h === '0:0:0:0:0:0:0:1') return true
  if (h.startsWith('::ffff:')) return isLoopbackHost(h.slice('::ffff:'.length))
  return /^127\.\d{1,3}\.\d{1,3}\.\d{1,3}$/.test(h)
}

/** 深拷贝并给敏感字段打码（用于 UI 卡片；不修改原对象）。 */
const redactValue = (value) => {
  if (Array.isArray(value)) return value.map(redactValue)
  if (value !== null && typeof value === 'object') {
    const out = {}
    for (const [key, item] of Object.entries(value)) {
      out[key] = SENSITIVE_KEYS.has(key.toLowerCase()) ? '***（已脱敏）' : redactValue(item)
    }
    return out
  }
  return value
}

/** 抹掉文案里的令牌与 URL 内嵌凭据：服务端原文可能回显请求头内容。 */
const scrubSecret = (text, token) => {
  let out = String(text ?? '')
  if (token !== '') out = out.split(token).join('***')
  return out.replace(/([a-z][a-z0-9+.-]*:\/\/)[^/\s@]+@/gi, '$1***@')
}

/** 取正整数配置值，非法或缺省时回退到保守默认。 */
const positiveInt = (value, fallback) => (Number.isInteger(value) && value > 0 ? value : fallback)

/** 配置/env 统一取数：数字字符串可转数字，空值/非法值返回 undefined（走默认）。 */
const numFrom = (value) => {
  if (typeof value === 'number') return value
  if (typeof value === 'string' && value.trim() !== '') {
    const num = Number(value)
    return Number.isFinite(num) ? num : undefined
  }
  return undefined
}

/** 配置/env 统一取布尔：true / "1" / "true" 为真，其余为假。 */
const boolFrom = (value) => {
  if (typeof value === 'boolean') return value
  const text = String(value ?? '').trim().toLowerCase()
  return text === '1' || text === 'true'
}

/** 短退避等待。 */
const sleep = (ms) => new Promise((resolve) => { setTimeout(resolve, ms) })

/**
 * 合并「外部取消信号」与「本插件超时信号」。
 * exec.signal 可能不存在（工具直调/旧版宿主），所以超时必须自己兜底。
 */
const buildSignal = (external, timeoutMs) => {
  const timer = AbortSignal.timeout(timeoutMs)
  if (external === undefined || external === null) return { signal: timer, timedOut: () => timer.aborted }
  if (typeof AbortSignal.any === 'function') {
    return { signal: AbortSignal.any([external, timer]), timedOut: () => timer.aborted }
  }
  // 兜底（Node < 20.3 无 AbortSignal.any）：手工桥接两个信号。
  const controller = new AbortController()
  const abort = () => controller.abort()
  if (external.aborted === true) controller.abort()
  else external.addEventListener('abort', abort, { once: true })
  timer.addEventListener('abort', abort, { once: true })
  return { signal: controller.signal, timedOut: () => timer.aborted }
}

export function apply(ctx, config) {
  const baseUrl = String(config?.baseUrl ?? process.env.KABAGE_ADMIN_BASE_URL ?? 'http://127.0.0.1:8460').replace(/\/+$/, '')
  const defaultInstance = String(config?.defaultInstance ?? process.env.KABAGE_ADMIN_DEFAULT_INSTANCE ?? 'e01')
  const tokenOf = () => {
    const fromConfig = typeof config?.token === 'string' ? config.token : ''
    return fromConfig !== '' ? fromConfig : String(process.env.KABAGE_SERVICE_TOKEN ?? '')
  }
  // 可调参数（测试与部署调优用；缺省即安全/保守值）。config 优先，其次实例 env。
  const timeoutMs = positiveInt(numFrom(config?.timeoutMs ?? process.env.KABAGE_ADMIN_TIMEOUT_MS), REQUEST_TIMEOUT_MS)
  const retryBackoffMs = positiveInt(numFrom(config?.retryBackoffMs ?? process.env.KABAGE_ADMIN_RETRY_BACKOFF_MS), RETRY_BACKOFF_MS)
  const maxResponseBytes = positiveInt(numFrom(config?.maxResponseBytes ?? process.env.KABAGE_ADMIN_MAX_RESPONSE_BYTES), MAX_RESPONSE_BYTES)
  // 写操作默认不自动重试：member/create 等写端点幂等性未知，自动重试可能重复建号。
  const retryMutations = boolFrom(config?.retryMutations ?? process.env.KABAGE_ADMIN_RETRY_MUTATIONS)
  // 明文 HTTP + 非回环目标 = 服务令牌裸奔在网络上；默认拒绝，需显式 opt-in。
  const allowInsecureHttp = boolFrom(config?.allowInsecureHttp ?? process.env.KABAGE_ADMIN_ALLOW_INSECURE_HTTP)

  const parsedBase = (() => { try { return new URL(baseUrl) } catch { return null } })()
  const insecureTransport = parsedBase !== null && parsedBase.protocol === 'http:' && !isLoopbackHost(parsedBase.hostname)
  const insecureWarning = '安全告警：平台管理接口使用明文 HTTP 且目标不是回环地址，服务令牌（Bearer）会在网络上明文传输，请尽快改用 https 或回环地址。'

  /** 展示用的 baseUrl：抹掉 URL 内嵌的 user:pass，避免凭据进错误文案。 */
  const displayUrl = () => {
    try {
      const u = new URL(baseUrl)
      u.username = ''
      u.password = ''
      return u.toString().replace(/\/+$/, '')
    } catch {
      return baseUrl.replace(/\/\/[^@/]*@/, '//***@')
    }
  }

  /**
   * 调平台 console API 并把非 200 转译为带稳定原因码的中文工具错误
   * （execute 抛错 → 模型收到 `Error: <中文理由>`）。
   */
  async function callPlatform(method, path, body, exec) {
    const token = tokenOf()
    if (token === '') {
      throw new Error('平台管理工具未配置服务令牌：请管理员执行 add-service-token 生成后，将 KABAGE_SERVICE_TOKEN 注入本实例 env（原因码 token_missing）')
    }
    if (insecureTransport && !allowInsecureHttp) {
      throw new Error(`${insecureWarning}插件已拒绝向该地址发送服务令牌，请改用 https 或回环地址（原因码 insecure_transport）`)
    }
    // 只读 GET 自动重试；写操作默认不重试（可能重复建号），需显式开启。
    const maxAttempts = (method === 'GET' || retryMutations) ? 2 : 1
    for (let attempt = 1; attempt <= maxAttempts; attempt += 1) {
      const { signal, timedOut } = buildSignal(exec?.signal, timeoutMs)
      let res
      try {
        res = await fetch(`${baseUrl}${path}`, {
          method,
          headers: { 'content-type': 'application/json', authorization: `Bearer ${token}` },
          body: body === undefined ? undefined : JSON.stringify(body),
          signal,
        })
      } catch (error) {
        // 错误分层：外部取消 / 本插件超时 / 网络不可达，三者语义不同。
        if (exec?.signal?.aborted === true) {
          throw new Error('工具调用已被外部取消（原因码 aborted）')
        }
        if (timedOut()) {
          throw new Error(`平台管理接口响应超时（${timeoutMs}ms），可能是平台 daemon 卡住或网络拥塞（原因码 timeout）`)
        }
        throw new Error(`无法连接平台管理接口（${displayUrl()}），请确认平台 daemon 在运行（原因码 unreachable）: ${scrubSecret(error?.message ?? error, token)}`)
      }
      const raw = await readBody(res, token)
      const payload = parseJson(raw)
      if (res.status === 200) return payload
      // 5xx 视作瞬时故障：短退避后重试一次（只读 GET 或显式开启写重试时）。
      if (res.status >= 500 && attempt < maxAttempts) {
        await sleep(retryBackoffMs)
        continue
      }
      throw platformError(res.status, payload, token)
    }
    throw new Error('平台请求失败（原因码 platform_error）')
  }

  /** 读响应体并做体积闸门：平台 member/list 无分页，一次性返回全部成员。 */
  async function readBody(res, token) {
    let text = ''
    try {
      text = await res.text()
    } catch (error) {
      throw new Error(`读取平台响应失败（原因码 unreachable）：${scrubSecret(error?.message ?? error, token)}`)
    }
    const bytes = Buffer.byteLength(text, 'utf8')
    if (bytes > maxResponseBytes) {
      throw new Error(`平台响应体过大（${bytes} 字节 > ${maxResponseBytes} 字节上限），已中止解析以免撑爆模型上下文。平台 member/list 目前一次性返回全部成员、无分页能力，请联系平台侧加分页或减少成员规模（原因码 response_too_large）`)
    }
    return text
  }

  /** 非 JSON 响应按空对象处理（平台错误体统一是 JSON，这里只是兜底）。 */
  const parseJson = (raw) => {
    if (raw === '') return {}
    try { return JSON.parse(raw) } catch { return {} }
  }

  /** HTTP 状态 → 中文语义 + 稳定原因码。 */
  const platformError = (status, payload, token) => {
    const detail = typeof payload?.error === 'string' && payload.error !== '' ? scrubSecret(payload.error, token).slice(0, 300) : ''
    if (status === 401) return new Error('平台认证失败：服务令牌无效或已被撤销，请联系管理员重新签发（原因码 auth_failed）')
    if (status === 403) return new Error('权限不足：readonly 服务令牌不能执行变更操作，请联系管理员签发 admin 令牌（原因码 forbidden）')
    if (status === 404) return new Error(`账号不存在或目标不存在：平台返回「${detail === '' ? '未找到' : detail}」（原因码 not_found）`)
    if (status === 429) return new Error('平台限流：请求过于频繁，请稍后重试（原因码 rate_limited）')
    if (status >= 500) return new Error(`平台故障：平台内部错误（HTTP ${status}），可稍后重试（原因码 platform_error）`)
    return new Error(`平台拒绝该操作（${status}）：${detail === '' ? `HTTP ${status}` : detail}（原因码 rejected）`)
  }

  /** raw 注册（零依赖）：输入校验由本工具自带。 */
  const requireField = (args, name, description) => {
    const value = args?.[name]
    if (typeof value !== 'string' || value.trim() === '') {
      throw new Error(`参数 ${name} 必填（${description}）`)
    }
    return value.trim()
  }

  /** 角色取值校验：非法角色显式报错，绝不静默降级成 employee（避免悄悄改权）。 */
  const readRole = (value, action) => {
    if (value === undefined || value === null) return 'employee'
    const role = String(value).trim()
    if (!ALLOWED_ROLES.has(role)) {
      throw new Error(`参数 role 取值非法：${action}成员仅支持 employee（成员）或 auditor（审计员），收到「${role}」。admin（管理员）不可由本工具设置，以免模型误操作造成提权，请由管理员在管理台调整（原因码 invalid_role）`)
    }
    return role
  }

  /** 点数额度取值：留空 = 不限；其余必须是非负整数。 */
  const readPoints = (value) => {
    if (value === undefined || value === null) return null
    if (typeof value === 'string') {
      const text = value.trim()
      if (text === '') return null
      const num = Number(text)
      if (!Number.isInteger(num) || num < 0) throw new Error('参数 points 必须是非负整数（留空或省略 = 不限）（原因码 invalid_points）')
      return num
    }
    if (typeof value !== 'number' || !Number.isInteger(value) || value < 0) {
      throw new Error('参数 points 必须是非负整数（留空或省略 = 不限）（原因码 invalid_points）')
    }
    return value
  }

  const output = {
    // annotation-only unconstrained schema：结果为任意 JSON（registry 校验快照）。
    schema: {},
    render: (_args, value) => [{ type: 'text', text: JSON.stringify(value) }],
  }
  // UI render intent（仓库规则：设计期确定）：管理操作统一 generic 卡片。
  // 卡片内容做敏感字段脱敏：参数里可能带 password/vkey，明文不能进卡片与轨迹记录。
  const presentCall = (title) => (args) => ({ card: 'generic', title, kind: '管理操作', content: JSON.stringify(redactValue(args ?? {})) })

  /** 结果收尾：非回环明文 HTTP（已 opt-in）时把高危告警挂进结果，模型与人都看得见。 */
  const finalize = (result) => (insecureTransport ? { ...result, securityWarning: insecureWarning } : result)

  /* ── 只读三工具 ─────────────────────────────────────────────────────────── */

  ctx.tools.register({
    name: 'user_list',
    description: '查询卡巴格平台成员列表（账号/显示名/部门/角色/启用状态/实例/当月点数用量摘要）。支持 department/role/disabled/instance/q 过滤与排序，最多返回 50 条。',
    parameters: {
      type: 'object',
      properties: {
        q: { type: 'string', description: '关键词过滤：匹配账号/显示名/部门（可选）' },
        department: { type: 'string', description: '部门精确过滤（可选）' },
        role: { type: 'string', description: '角色过滤：admin / auditor / employee（可选）' },
        disabled: { type: 'boolean', description: '启用状态过滤：true=已禁用，false=正常（可选）' },
        instance: { type: 'string', description: '绑定实例 id 精确过滤（可选）' },
        sort: { type: 'string', description: `排序字段：${SORT_FIELDS.join(' / ')}（可选，默认 account）` },
        order: { type: 'string', description: '排序方向：asc / desc（可选，默认 asc）' },
        limit: { type: 'integer', description: '返回条数上限（可选，默认 50，最大 50）' },
      },
      additionalProperties: false,
    },
    output,
    presentCall: presentCall('平台成员列表'),
    async execute(args, exec) {
      const filters = readFilters(args)
      const sort = readSort(args?.sort)
      const order = readOrder(args?.order)
      const limit = readLimit(args?.limit)
      const data = await callPlatform('GET', '/console/api/member/list', undefined, exec)
      const all = Array.isArray(data.members) ? data.members : []
      const matched = all.filter((m) => matchMember(m, filters))
      const members = sortMembers(matched, sort, order).slice(0, limit)
      return finalize({
        month: data.month ?? null,
        total: all.length,
        matched: matched.length,
        shown: members.length,
        truncated: matched.length > members.length,
        filters,
        sort,
        order,
        hint: matched.length > members.length
          ? `还有 ${matched.length - members.length} 条未返回：请补充过滤条件（平台 member/list 无分页，一次返回全部成员）`
          : '已返回全部匹配成员',
        members,
      })
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
      return finalize(await callPlatform('GET', `/console/api/member/usage?account=${encodeURIComponent(account)}`, undefined, exec))
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
      // 多取 1 条用于判定「是否还有更多」：平台只回 events 数组、不给总数，
      // 返回条数恰好等于 limit 时无法区分「刚好用完」与「被截断」，
      // 多取一条才能精确判定 truncated（否则恰好 N 条时会误报截断）。
      params.set('limit', String(limit + 1))
      const data = await callPlatform('GET', `/console/api/audit?${params.toString()}`, undefined, exec)
      const raw = Array.isArray(data.events) ? data.events : []
      const events = raw.slice(0, limit)
      const hasMore = raw.length > limit
      return finalize({
        count: events.length,
        truncated: hasMore,
        hint: hasMore ? '还有更多条目，请缩小 action/actor 过滤后重试' : '已返回全部匹配条目',
        events,
      })
    },
  })

  /* ── 变更六工具（readonly 令牌调用时平台 403 → 中文错误）────────────────── */

  ctx.tools.register({
    name: 'user_create',
    description: `在平台创建成员账号（自动签发虚拟钥匙，返回一次性密码与 vkey）。role 仅 employee/auditor。${CREDENTIAL_WARNING}`,
    parameters: {
      type: 'object',
      properties: {
        account: { type: 'string', description: '新成员账号（邮箱形，如 name@company）' },
        displayName: { type: 'string', description: '显示名（可选，缺省取账号前缀）' },
        department: { type: 'string', description: '部门（可选，缺省「未分配」）' },
        role: { type: 'string', description: '角色：employee（缺省）或 auditor；admin 不可由本工具创建' },
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
      const role = readRole(args?.role, '创建')
      const body = {
        account,
        instance: typeof args.instance === 'string' && args.instance !== '' ? args.instance : defaultInstance,
        role,
      }
      const department = typeof args.department === 'string' ? args.department.trim() : ''
      if (typeof args.displayName === 'string' && args.displayName.trim() !== '') body.displayName = args.displayName.trim()
      if (department !== '') body.department = department
      if (typeof args.password === 'string' && args.password !== '') body.password = args.password
      const data = await callPlatform('POST', '/console/api/member/create', body, exec)
      const warnings = []
      // 平台 member/create 端点没有把 body.department 传给 addAccount
      // （console.mjs 只传 account/instance/role/displayName/password），
      // 建号时带的部门会被丢弃——这里补一次 update 落部门（幂等写；平台若
      // 将来修复则这一步是无副作用的重复写）。
      if (department !== '') {
        try {
          await callPlatform('POST', '/console/api/member/update', { account: data.account ?? account, department }, exec)
        } catch (error) {
          warnings.push(`部门未写入：平台建号端点忽略 department，补发 update 也失败（${error?.message ?? error}）`)
        }
      }
      if (typeof data.vkey !== 'string' || data.vkey === '') {
        warnings.push('平台未返回虚拟钥匙（vkey）：该成员实例暂时拿不到可用钥匙，请在管理台「令牌与配额」页签发一次')
      }
      return finalize({
        account: data.account ?? account,
        instance: data.instance ?? body.instance,
        password: typeof data.password === 'string' ? data.password : null,
        vkey: typeof data.vkey === 'string' ? data.vkey : null,
        sensitiveFields: ['password', 'vkey'],
        warnings,
        notice: CREDENTIAL_WARNING,
      })
    },
  })

  ctx.tools.register({
    name: 'user_update',
    description: '更新成员的部门 / 显示名 / 角色（role 仅 employee/auditor；至少提供一个字段）。',
    parameters: {
      type: 'object',
      properties: {
        account: { type: 'string', description: '成员账号' },
        displayName: { type: 'string', description: '新显示名（可选）' },
        department: { type: 'string', description: '新部门（可选）' },
        role: { type: 'string', description: '新角色：employee 或 auditor（可选；admin 不可由本工具设置）' },
      },
      required: ['account'],
      additionalProperties: false,
    },
    output,
    presentCall: presentCall('更新平台成员'),
    async execute(args, exec) {
      const account = requireField(args, 'account', '成员账号')
      const body = { account }
      let changed = false
      if (args.department !== undefined) { body.department = String(args.department); changed = true }
      if (args.displayName !== undefined) { body.displayName = String(args.displayName); changed = true }
      if (args.role !== undefined) { body.role = readRole(args.role, '更新'); changed = true }
      if (!changed) {
        throw new Error('至少提供 department / displayName / role 之一')
      }
      return finalize(await callPlatform('POST', '/console/api/member/update', body, exec))
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
      return finalize({
        account: data.account ?? account,
        password: typeof data.password === 'string' ? data.password : null,
        sensitiveFields: ['password'],
        notice: PWD_NOTICE,
      })
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
      return finalize(await callPlatform('POST', `/console/api/member/${args.disabled ? 'disable' : 'enable'}`, { account }, exec))
    },
  })

  ctx.tools.register({
    name: 'user_set_quota',
    description: '设置成员的月度点数额度（留空 = 不限）。平台按点数做硬停判定；需要 admin 令牌（readonly 令牌返回 forbidden）。',
    parameters: {
      type: 'object',
      properties: {
        account: { type: 'string', description: '成员账号' },
        points: { type: 'integer', description: '月度点数额度（非负整数）；留空或省略 = 不限' },
      },
      required: ['account'],
      additionalProperties: false,
    },
    output,
    presentCall: presentCall('设置成员额度'),
    async execute(args, exec) {
      const account = requireField(args, 'account', '成员账号')
      const points = readPoints(args?.points)
      const data = await callPlatform('POST', '/console/api/member/quota', { account, points }, exec)
      return finalize({
        account,
        quota: data.quota ?? points,
        unit: 'points',
        unlimited: points === null,
        notice: points === null
          ? '额度已设为不限（该成员本月不按点数硬停）。'
          : `额度已设为每月 ${points} 点数（本月用量达到该值即被平台硬停）。`,
      })
    },
  })

  ctx.tools.register({
    name: 'user_reset_2fa',
    description: '重置成员的 2FA（两步验证）绑定（成员丢失认证器时的救援操作）。解绑后该成员下次登录只需密码，请提醒其重新绑定认证器。',
    parameters: {
      type: 'object',
      properties: { account: { type: 'string', description: '成员账号' } },
      required: ['account'],
      additionalProperties: false,
    },
    output,
    presentCall: presentCall('重置成员两步验证'),
    async execute(args, exec) {
      const account = requireField(args, 'account', '成员账号')
      const data = await callPlatform('POST', '/console/api/member/2fa/reset', { account }, exec)
      return finalize({
        account: data.account ?? account,
        ok: data.ok === true,
        notice: '两步验证绑定已解除：该成员下次登录只需密码，请提醒其登录后重新绑定认证器。',
      })
    },
  })

  /* ── user_list 的过滤 / 排序参数解析 ─────────────────────────────────────── */

  function readFilters(args) {
    const filters = {}
    if (args?.q !== undefined) {
      if (typeof args.q !== 'string') throw new Error('参数 q 必须是字符串（原因码 invalid_parameter）')
      const q = args.q.trim()
      if (q !== '') filters.q = q
    }
    if (args?.department !== undefined) {
      if (typeof args.department !== 'string') throw new Error('参数 department 必须是字符串（原因码 invalid_parameter）')
      const dep = args.department.trim()
      if (dep !== '') filters.department = dep
    }
    if (args?.role !== undefined) {
      const role = String(args.role ?? '').trim()
      if (!PLATFORM_ROLES.has(role)) throw new Error(`参数 role 过滤值非法：仅支持 admin / auditor / employee，收到「${role}」（原因码 invalid_role）`)
      filters.role = role
    }
    if (args?.disabled !== undefined) {
      if (typeof args.disabled !== 'boolean') throw new Error('参数 disabled 必须是布尔值（原因码 invalid_parameter）')
      filters.disabled = args.disabled
    }
    if (args?.instance !== undefined) {
      if (typeof args.instance !== 'string') throw new Error('参数 instance 必须是字符串（原因码 invalid_parameter）')
      const instance = args.instance.trim()
      if (instance !== '') filters.instance = instance
    }
    return filters
  }

  function readSort(value) {
    if (value === undefined || value === null) return 'account'
    const key = String(value).trim()
    if (!SORT_FIELDS.includes(key)) throw new Error(`参数 sort 取值非法：仅支持 ${SORT_FIELDS.join(' / ')}，收到「${key}」（原因码 invalid_parameter）`)
    return key
  }

  function readOrder(value) {
    if (value === undefined || value === null) return 'asc'
    const order = String(value).trim().toLowerCase()
    if (order !== 'asc' && order !== 'desc') throw new Error(`参数 order 取值非法：仅支持 asc / desc，收到「${value}」（原因码 invalid_parameter）`)
    return order
  }

  function readLimit(value) {
    if (value === undefined || value === null) return LIST_LIMIT
    if (!Number.isInteger(value) || value <= 0) throw new Error('参数 limit 必须是正整数（原因码 invalid_parameter）')
    return Math.min(value, LIST_LIMIT)
  }

  /** 过滤：q 命中账号/显示名/部门，其余为精确匹配。 */
  function matchMember(member, filters) {
    if (filters.q !== undefined) {
      const needle = filters.q.toLowerCase()
      const hay = [member.account, member.displayName, member.department]
        .map((v) => String(v ?? '').toLowerCase())
        .join(' ')
      if (!hay.includes(needle)) return false
    }
    if (filters.department !== undefined && String(member.department ?? '未分配') !== filters.department) return false
    if (filters.role !== undefined && String(member.role ?? '') !== filters.role) return false
    if (filters.disabled !== undefined && Boolean(member.disabled) !== filters.disabled) return false
    if (filters.instance !== undefined && String(member.instanceId ?? '') !== filters.instance) return false
    return true
  }

  /** 排序：白名单字段；数值字段按数值比，字符串按中文 collation。 */
  function sortMembers(list, key, order) {
    const dir = order === 'desc' ? -1 : 1
    const value = (member) => {
      if (key === 'instance') return String(member.instanceId ?? '')
      if (key === 'pointsUsed') return Number(member.pointsUsed ?? 0)
      if (key === 'lastLogin') return String(member.lastLogin?.ts ?? '')
      return String(member[key] ?? '')
    }
    return [...list].sort((a, b) => {
      const va = value(a)
      const vb = value(b)
      if (typeof va === 'number' && typeof vb === 'number') return (va - vb) * dir
      return String(va).localeCompare(String(vb), 'zh-Hans-CN') * dir
    })
  }
}
