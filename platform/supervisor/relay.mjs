/**
 * 落云宗企业平台 · Relay 密钥代理（任务书阶段 3 + 计量配额阶段 4）。
 *
 * 职责：持有真实上游 Key（真实 Key 唯一容身处）；对实例暴露 OpenAI 兼容的
 * `POST /v1/chat/completions`；用虚拟钥匙（vk-…，只存 SHA-256）认证调用方，
 * per-request 校验模型授权与月度 Token 配额，然后把 Authorization 换成真实
 * Key 转发上游，并从响应抽取 token 用量入账。实例侧零改动——provider 路由
 * 的 baseURL 指向 Relay、apiKeyEnv 指向虚拟钥匙。
 *
 * 安全语义（任务书决定 2/5/6 + 安全设计原则）：
 * - 服务端强制：认证、模型授权、配额在本进程 per-request 校验，不信任实例
 *   自律；用量与额度只存在服务端，实例内没有任何可篡改的配额状态；
 * - 硬停：本月用量 ≥ 额度即拒新请求（可读 429），已转发的 in-flight 请求
 *   放行至完成；额度不设（undefined）= 不限（如管理员账号）；
 * - 月键取部署服务器本地时区（决定 6），无 per-tenant 时区；
 * - 虚拟钥匙吊销即时生效（每次请求按 mtime 缓存重读 vkeys.json）；
 * - 日志只记元数据（谁/何时/哪个模型/哪个上游/状态/耗时/token 数），
 *   绝不落 prompt、completion 或任何消息正文。
 */
import { createServer, request as httpRequest } from 'node:http'
import { request as httpsRequest } from 'node:https'
import { createHash, randomBytes, timingSafeEqual } from 'node:crypto'
import { appendFileSync, mkdirSync, readFileSync, renameSync, statSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'

const UPSTREAMS_FILE = 'upstreams.json'
const VKEYS_FILE = 'vkeys.json'
const ACCOUNTS_FILE = 'accounts.json'
const USAGE_FILE = 'usage.json'
const BODY_LIMIT_BYTES = 32 * 1024 * 1024
const UPSTREAM_TIMEOUT_MS = 300_000
/** 从响应抽取 usage 的缓冲上限：超过即放弃抽取（只影响计量精度，不影响转发）。 */
const TAP_LIMIT_BYTES = 8 * 1024 * 1024

const hashToken = (token) => createHash('sha256').update(token).digest('hex')

/** 月键：部署服务器本地时区的 `YYYY-MM`（任务书决定 6，无 per-tenant 时区）。 */
export function monthKey(date = new Date()) {
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`
}

/** mtime 缓存的 JSON 读取：文件没变就不重读，变了立刻生效（吊销 ≤ 下一次请求）。 */
function cachedJson(file, cache) {
  let mtime
  try {
    mtime = statSync(file).mtimeMs
  } catch {
    return null
  }
  if (cache.file === file && cache.mtime === mtime && cache.value !== undefined) return cache.value
  try {
    cache.file = file
    cache.mtime = mtime
    cache.value = JSON.parse(readFileSync(file, 'utf8'))
  } catch {
    cache.value = null
  }
  return cache.value
}

const openAiError = (res, status, message, code) => {
  res.writeHead(status, { 'content-type': 'application/json' })
  const type = status === 401 ? 'authentication_error' : status === 429 ? 'insufficient_quota' : 'invalid_request_error'
  res.end(JSON.stringify({ error: { message, type, code } }))
}

/**
 * 创建 Relay 服务器。
 * @param manifest - instances.json 内容（读 relayPort 之外的实例映射仅用于日志归属）
 * @param dataDir  - data/ 目录（upstreams.json、vkeys.json、logs/relay.log）
 */
export function createRelayServer({ dataDir }) {
  const upstreamsCache = {}
  const vkeysCache = {}
  const accountsCache = {}
  const logFile = join(dataDir, 'logs', 'relay.log')

  const logMeta = (entry) => {
    try {
      mkdirSync(join(dataDir, 'logs'), { recursive: true })
      appendFileSync(logFile, `${JSON.stringify(entry)}\n`)
    } catch { /* 日志失败不影响转发 */ }
  }

  /* ── 计量存储（usage.json）：单进程内串行读改写，原子落盘 ─────────────────── */
  let usageQueue = Promise.resolve()
  const withUsageLock = (fn) => {
    const next = usageQueue.then(fn, fn)
    usageQueue = next.catch(() => {})
    return next
  }
  const readUsage = () => {
    try {
      return JSON.parse(readFileSync(join(dataDir, USAGE_FILE), 'utf8'))
    } catch {
      return { months: {} }
    }
  }
  const writeUsage = (store) => {
    const path = join(dataDir, USAGE_FILE)
    const tmp = `${path}.tmp`
    writeFileSync(tmp, `${JSON.stringify(store, null, 2)}\n`)
    renameSync(tmp, path)
  }
  const recordUsage = (account, tokensIn, tokensOut) => withUsageLock(() => {
    if (!Number.isFinite(tokensIn) && !Number.isFinite(tokensOut)) return
    const store = readUsage()
    const month = monthKey()
    store.months[month] ??= {}
    const entry = store.months[month][account] ??= { tokensIn: 0, tokensOut: 0, requests: 0 }
    entry.tokensIn += Number.isFinite(tokensIn) ? tokensIn : 0
    entry.tokensOut += Number.isFinite(tokensOut) ? tokensOut : 0
    entry.requests += 1
    writeUsage(store)
  })
  const usedTokensThisMonth = (account) => {
    const entry = readUsage().months[monthKey()]?.[account]
    return entry ? entry.tokensIn + entry.tokensOut : 0
  }

  return createServer((req, res) => {
    const incoming = req.url
    if (req.method !== 'POST' || !(incoming === '/v1/chat/completions' || incoming === '/v1/completions' || incoming === '/v1/messages')) {
      openAiError(res, 404, `unknown relay route ${req.method} ${req.url}`, 'not_found')
      return
    }

    const auth = req.headers.authorization ?? ''
    const token = auth.startsWith('Bearer ') ? auth.slice(7) : ''
    if (!token.startsWith('vk-')) {
      openAiError(res, 401, 'missing or malformed virtual key (expected "Authorization: Bearer vk-…")', 'invalid_api_key')
      return
    }
    const presented = Buffer.from(hashToken(token), 'hex')
    const vkeys = cachedJson(join(dataDir, VKEYS_FILE), vkeysCache)?.vkeys ?? []
    const vkey = vkeys.find((v) => {
      const stored = Buffer.from(v.tokenHash, 'hex')
      return stored.length === presented.length && timingSafeEqual(stored, presented)
    })
    if (vkey === undefined || vkey.revoked) {
      openAiError(res, 401, 'virtual key is invalid or revoked; ask your administrator for a new one', 'invalid_api_key')
      return
    }

    let raw = ''
    let oversized = false
    req.on('data', (chunk) => {
      raw += chunk
      if (raw.length > BODY_LIMIT_BYTES) { oversized = true; req.destroy() }
    })
    req.on('end', () => {
      if (oversized) return
      let body
      try {
        body = JSON.parse(raw || '{}')
      } catch {
        openAiError(res, 400, 'request body is not valid JSON', 'invalid_body')
        return
      }
      const model = typeof body.model === 'string' ? body.model : ''
      if (vkey.models !== '*' && !vkey.models.includes(model)) {
        openAiError(res, 403, `model "${model}" is not authorized for this virtual key`, 'model_not_authorized')
        return
      }
      // 配额硬停（阶段 4）：账号设了 monthlyTokens 且本月用量已到线，拒新请求。
      // 用量只存在服务端 usage.json，实例内没有任何可篡改的配额状态。
      const accountRecord = cachedJson(join(dataDir, ACCOUNTS_FILE), accountsCache)?.accounts
        ?.find((a) => a.account === vkey.account)
      if (accountRecord?.disabled) {
        openAiError(res, 401, '账号已禁用，请联系管理员', 'account_disabled')
        return
      }
      const quota = accountRecord?.monthlyTokens
      const used = usedTokensThisMonth(vkey.account)
      if (Number.isFinite(quota) && used >= quota) {
        openAiError(res, 429, `本月 Token 额度已用完（${used}/${quota}）。请联系管理员调整额度。`, 'insufficient_quota')
        return
      }
      const upstreams = cachedJson(join(dataDir, UPSTREAMS_FILE), upstreamsCache)?.upstreams ?? []
      const upstream = upstreams.find((u) => !u.revoked && u.models.includes(model))
      if (upstream === undefined) {
        openAiError(res, 403, `model "${model}" has no upstream configured on the relay`, 'no_upstream')
        return
      }
      // 按供应商 API 格式映射转发路径：openai 格式走 /chat/completions，anthropic 原生走 /v1/messages
      const upstreamPath = (upstream.apiFormat === 'anthropic')
        ? '/v1/messages'
            : incoming.replace('/v1', '')
      if (!['/v1/messages', '/chat/completions', '/completions'].includes(upstreamPath)) {
        openAiError(res, 400, `unsupported path for upstream "${upstream.name}": ${upstreamPath}`, 'bad_path')
        return
      }

      // 流式请求补 stream_options.include_usage：上游会在末块带 usage，供计量抽取。
      if (body.stream === true && (typeof body.stream_options !== 'object' || body.stream_options === null)) {
        body.stream_options = { include_usage: true }
        raw = JSON.stringify(body)
      }

      // 真实 Key 只在此处出现：从上游表注入 Authorization，原请求头不带出去。
      const started = Date.now()
      const sendUpstream = upstream.baseURL.startsWith('https:') ? httpsRequest : httpRequest
      let upstreamReq
      try {
        upstreamReq = sendUpstream(
          `${upstream.baseURL.replace(/\/$/, '')}${req.url.replace(/^\/v1/, '')}`,
          {
            method: 'POST',
            headers: {
              'content-type': req.headers['content-type'] ?? 'application/json',
              'content-length': Buffer.byteLength(raw),
              authorization: `Bearer ${upstream.apiKey}`,
              accept: req.headers.accept ?? 'application/json',
            },
            timeout: UPSTREAM_TIMEOUT_MS,
          },
          (upstreamRes) => {
            res.writeHead(upstreamRes.statusCode ?? 502, upstreamRes.headers)
            // 计量抽取（tee，不阻塞转发）：SSE 逐行扫末块 usage；JSON 解析整体。
            const contentType = String(upstreamRes.headers['content-type'] ?? '')
            let usage = null
            if (contentType.includes('text/event-stream')) {
              let lineBuf = ''
              upstreamRes.on('data', (chunk) => {
                lineBuf += chunk.toString('utf8')
                let idx
                while ((idx = lineBuf.indexOf('\n')) >= 0) {
                  const line = lineBuf.slice(0, idx).trim()
                  lineBuf = lineBuf.slice(idx + 1)
                  if (!line.startsWith('data:')) continue
                  const payload = line.slice(5).trim()
                  if (payload === '' || payload === '[DONE]') continue
                  try {
                    const parsed = JSON.parse(payload)
                    if (parsed.usage && typeof parsed.usage === 'object') usage = parsed.usage
                  } catch { /* 非 JSON 行（注释等）跳过 */ }
                }
              })
            } else if (contentType.includes('application/json')) {
              const chunks = []
              let size = 0
              upstreamRes.on('data', (chunk) => {
                size += chunk.length
                if (size <= TAP_LIMIT_BYTES) chunks.push(chunk)
              })
              upstreamRes.on('end', () => {
                try {
                  const parsed = JSON.parse(Buffer.concat(chunks).toString('utf8'))
                  if (parsed.usage && typeof parsed.usage === 'object') usage = parsed.usage
                } catch { /* 抽取失败不影响转发与计量降级 */ }
              })
            }
            upstreamRes.pipe(res)
            upstreamRes.on('end', () => {
              const tokensIn = Number(usage?.prompt_tokens)
              const tokensOut = Number(usage?.completion_tokens)
              if (Number.isFinite(tokensIn) || Number.isFinite(tokensOut)) {
                void recordUsage(vkey.account, tokensIn, tokensOut)
              }
              logMeta({
                at: new Date().toISOString(), account: vkey.account, instance: vkey.instanceId,
                vkeyId: vkey.id, model, upstream: upstream.name,
                status: upstreamRes.statusCode ?? 0, ms: Date.now() - started,
                tokensIn: Number.isFinite(tokensIn) ? tokensIn : undefined,
                tokensOut: Number.isFinite(tokensOut) ? tokensOut : undefined,
              })
            })
            upstreamRes.on('error', () => res.destroy())
          },
        )
      } catch (error) {
        // 坏上游配置（URL 非法等）只影响这一笔请求，不拖垮整个控制进程。
        logMeta({
          at: new Date().toISOString(), account: vkey.account, instance: vkey.instanceId,
          vkeyId: vkey.id, model, upstream: upstream.name, status: 502, ms: Date.now() - started,
          error: error.message,
        })
        openAiError(res, 502, `upstream "${upstream.name}" misconfigured`, 'upstream_error')
        return
      }
      upstreamReq.on('timeout', () => upstreamReq.destroy(new Error('upstream timeout')))
      upstreamReq.on('error', (error) => {
        logMeta({
          at: new Date().toISOString(), account: vkey.account, instance: vkey.instanceId,
          vkeyId: vkey.id, model, upstream: upstream.name, status: 502, ms: Date.now() - started,
          error: error.message,
        })
        if (!res.headersSent) openAiError(res, 502, `upstream "${upstream.name}" unreachable`, 'upstream_error')
        else res.end()
      })
      upstreamReq.end(raw)
    })
  })
}

/* ── 存储与 CLI 支撑（被 supervisor.mjs 的命令复用）──────────────────────── */

function readStore(dataDir, file, fallback) {
  try {
    return JSON.parse(readFileSync(join(dataDir, file), 'utf8'))
  } catch {
    return fallback
  }
}

function writeStore(dataDir, file, value) {
  const path = join(dataDir, file)
  const tmp = `${path}.tmp`
  writeFileSync(tmp, `${JSON.stringify(value, null, 2)}\n`)
  renameSync(tmp, path)
}

/** 上游增加模型：写入 models 列表与展示元数据（modelMeta）。已存在则报错。 */
export function addModel(dataDir, { upstream, model, meta }) {
  const store = readStore(dataDir, UPSTREAMS_FILE, { upstreams: [] })
  const u = store.upstreams.find((x) => x.name === upstream)
  if (u === undefined) throw new Error(`上游不存在: ${upstream}`)
  if (u.models.includes(model)) throw new Error(`模型已存在: ${model}`)
  u.models.push(model)
  if (meta && typeof meta === 'object') {
    u.modelMeta ??= {}
    u.modelMeta[model] = meta
  }
  writeStore(dataDir, UPSTREAMS_FILE, store)
}

/** 上游删除模型：从 models 列表与展示元数据中移除。 */
export function removeModel(dataDir, { upstream, model }) {
  const store = readStore(dataDir, UPSTREAMS_FILE, { upstreams: [] })
  const u = store.upstreams.find((x) => x.name === upstream)
  if (u === undefined) throw new Error(`上游不存在: ${upstream}`)
  if (!u.models.includes(model)) throw new Error(`模型不存在: ${model}`)
  u.models = u.models.filter((m) => m !== model)
  if (u.modelMeta !== undefined) delete u.modelMeta[model]
  writeStore(dataDir, UPSTREAMS_FILE, store)
}

/** 删除整个上游供应商（含其模型与展示元数据）。 */
export function removeUpstream(dataDir, { name }) {
  const store = readStore(dataDir, UPSTREAMS_FILE, { upstreams: [] })
  const before = store.upstreams.length
  store.upstreams = store.upstreams.filter((x) => x.name !== name)
  if (store.upstreams.length === before) throw new Error(`上游不存在: ${name}`)
  writeStore(dataDir, UPSTREAMS_FILE, store)
}

export function setUpstream(dataDir, { name, baseURL, models, apiKey, note, website, apiFormat, authEnv, modelMapping, fallbackModel, configJSON, fullUrl }) {
  const store = readStore(dataDir, UPSTREAMS_FILE, { upstreams: [] })
  const existing = store.upstreams.find((u) => u.name === name)
  if (existing) {
    existing.baseURL = baseURL
    existing.models = models
    if (apiKey !== undefined) existing.apiKey = apiKey
    if (note !== undefined) existing.note = note
    if (website !== undefined) existing.website = website
    if (apiFormat !== undefined) existing.apiFormat = apiFormat
    if (authEnv !== undefined) existing.authEnv = authEnv
    if (modelMapping !== undefined) existing.modelMapping = modelMapping
    if (fallbackModel !== undefined) existing.fallbackModel = fallbackModel
    if (configJSON !== undefined) existing.configJSON = configJSON
    if (fullUrl !== undefined) existing.fullUrl = fullUrl
  } else {
    if (apiKey === undefined) throw new Error(`上游 ${name} 不存在，首次创建必须提供 --key`)
    store.upstreams.push({ name, baseURL, models, apiKey, revoked: false, note, website, apiFormat: apiFormat ?? 'openai', authEnv, modelMapping, fallbackModel, configJSON, fullUrl, createdAt: new Date().toISOString() })
  }
  writeStore(dataDir, UPSTREAMS_FILE, store)
}

export function listUpstreams(dataDir) {
  return readStore(dataDir, UPSTREAMS_FILE, { upstreams: [] }).upstreams.map((u) => ({
    name: u.name,
    baseURL: u.baseURL,
    models: u.models,
    revoked: u.revoked === true,
    // 只回显指纹，绝不回显真实 Key。
    keyFingerprint: u.apiKey === undefined ? '—' : `${u.apiKey.slice(0, 4)}…${u.apiKey.slice(-4)}（${u.apiKey.length} 字符）`,
    modelMeta: u.modelMeta ?? {},
    note: u.note ?? '',
    website: u.website ?? '',
    apiFormat: u.apiFormat ?? 'openai',
    authEnv: u.authEnv ?? '',
    modelMapping: u.modelMapping ?? [],
    fallbackModel: u.fallbackModel ?? '',
    configJSON: u.configJSON ?? '',
    fullUrl: u.fullUrl === true,
  }))
}

/** 签发虚拟钥匙：token 只在此返回一次，存储里只有 SHA-256。同账号旧钥匙自动吊销。 */
export function issueVkey(dataDir, { account, instanceId, models }) {
  const store = readStore(dataDir, VKEYS_FILE, { vkeys: [] })
  for (const v of store.vkeys) {
    if (v.account === account && !v.revoked) v.revoked = true
  }
  const token = `vk-${randomBytes(24).toString('base64url')}`
  const record = {
    id: `vkid-${randomBytes(4).toString('hex')}`,
    tokenHash: hashToken(token),
    account,
    instanceId,
    models,
    revoked: false,
    createdAt: new Date().toISOString(),
  }
  store.vkeys.push(record)
  writeStore(dataDir, VKEYS_FILE, store)
  return { token, record }
}

export function revokeVkey(dataDir, { account }) {
  const store = readStore(dataDir, VKEYS_FILE, { vkeys: [] })
  let n = 0
  for (const v of store.vkeys) {
    if (v.account === account && !v.revoked) { v.revoked = true; n += 1 }
  }
  if (n === 0) throw new Error(`账号 ${account} 没有有效的虚拟钥匙`)
  writeStore(dataDir, VKEYS_FILE, store)
  return n
}

/** 更新账号活跃虚拟钥匙的模型白名单（控制台矩阵编辑）。 */
export function setVkeyModels(dataDir, { account, models }) {
  const store = readStore(dataDir, VKEYS_FILE, { vkeys: [] })
  const active = store.vkeys.filter((v) => v.account === account && !v.revoked)
  if (active.length === 0) throw new Error(`账号 ${account} 没有有效的虚拟钥匙`)
  for (const v of active) v.models = models
  writeStore(dataDir, VKEYS_FILE, store)
  return models
}

export function listVkeys(dataDir) {
  return readStore(dataDir, VKEYS_FILE, { vkeys: [] }).vkeys.map((v) => ({
    id: v.id, account: v.account, instanceId: v.instanceId,
    models: v.models, revoked: v.revoked, createdAt: v.createdAt,
  }))
}

/** 设置月度 Token 额度：null = 不限（管理员）；数字 = 硬停线（0 = 立即停）。 */
export function setQuota(dataDir, { account, monthlyTokens }) {
  const store = readStore(dataDir, ACCOUNTS_FILE, { accounts: [] })
  const record = store.accounts.find((a) => a.account === account)
  if (record === undefined) throw new Error(`账号不存在: ${account}`)
  if (monthlyTokens === null) delete record.monthlyTokens
  else record.monthlyTokens = monthlyTokens
  writeStore(dataDir, ACCOUNTS_FILE, store)
  return record
}

/** 当月用量对照额度（读侧：直接读文件，与 Relay 的写入经原子替换保持一致）。 */
export function listUsage(dataDir, month = monthKey()) {
  const accounts = readStore(dataDir, ACCOUNTS_FILE, { accounts: [] }).accounts
  const months = readStore(dataDir, USAGE_FILE, { months: {} }).months
  const usage = months[month] ?? {}
  return accounts.map((a) => {
    const entry = usage[a.account] ?? { tokensIn: 0, tokensOut: 0, requests: 0 }
    const used = entry.tokensIn + entry.tokensOut
    return {
      account: a.account,
      instanceId: a.instanceId,
      month,
      tokensIn: entry.tokensIn,
      tokensOut: entry.tokensOut,
      requests: entry.requests,
      monthlyTokens: a.monthlyTokens ?? null,
      used,
      remaining: Number.isFinite(a.monthlyTokens) ? Math.max(0, a.monthlyTokens - used) : null,
    }
  })
}
