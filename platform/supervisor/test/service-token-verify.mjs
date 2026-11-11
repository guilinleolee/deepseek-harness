/**
 * 服务令牌 + 管理类 DSH 工具的平台侧验证（阶段 12）：临时 data/ + 随机端口
 * 起真实网关。覆盖：token 生成（哈希落盘）→ Bearer 认证命中 → admin token
 * 全通（列表/用量/变更，审计 actor=svc:名称）→ readonly 只读白名单（白名单
 * 外 GET 403、变更 POST 403 deny 留痕）→ 页面路由一律 401 → 撤销后 401（
 * mtime 下一请求生效）→ 坏 token 401。工具结果数据源端点（member/list、
 * member/usage）断言结构。
 *
 * 运行：node test/service-token-verify.mjs
 */
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'

import { auditAppend, auditQuery, initAudit } from '../audit.mjs'
import { createGatewayServer, hashPassword } from '../gateway.mjs'
import { authenticateServiceToken, createServiceToken, revokeServiceToken } from '../service-tokens.mjs'

const wait = (ms) => new Promise((r) => setTimeout(r, ms))
const JSON_HEAD = { 'content-type': 'application/json', connection: 'close' }

let passed = 0
let failed = 0
const check = (name, cond) => {
  if (cond === true) { passed += 1; console.log(`  ok  ${name}`) } else { failed += 1; console.error(`FAIL  ${name}`) }
}

// P2-7：模块级缓存按 dataDir 键控——第二个目录在 import 早期即参与断言。
const DATA_B = mkdtempSync(join(tmpdir(), 'lyz-svc-token-b-'))

const DATA = mkdtempSync(join(tmpdir(), 'lyz-svc-token-'))
const now = new Date().toISOString()
const mkAccount = (id, acc, role, pw, extra = {}) => ({
  id, account: acc, displayName: id, role, department: '验证组', instanceId: 'e02',
  tokenEpoch: 0, createdAt: now, passwordHash: hashPassword(pw), ...extra,
})
writeFileSync(join(DATA, 'accounts.json'), `${JSON.stringify({ accounts: [
  mkAccount('a1', 'admin@t', 'admin', 'AdminPass1', { instanceId: 'e01' }),
  mkAccount('m1', 'member@t', 'employee', 'MemberPass1', { monthlyPoints: 1000 }),
] }, null, 2)}\n`)
writeFileSync(join(DATA, 'usage.json'), `${JSON.stringify({ months: { [`${new Date().getFullYear()}-${String(new Date().getMonth() + 1).padStart(2, '0')}`]: {
  'member@t': { tokensIn: 50, tokensOut: 10, requests: 3, points: 320 },
} } }, null, 2)}\n`)
initAudit(DATA)

const manifest = {
  gatewayHost: 'localhost', portalPort: 0, relayPort: 0, repoRoot: '.',
  instances: [
    { id: 'e01', account: 'admin@t', uid: 1, port: 1 },
    { id: 'e02', account: 'member@t', uid: 2, port: 2 },
  ],
}
const gateway = createGatewayServer({ manifest, getState: () => ({ instances: {} }), dataDir: DATA })
await new Promise((r) => gateway.listen(0, '127.0.0.1', r))
const base = `http://127.0.0.1:${gateway.address().port}`
const get = (path, token) => fetch(`${base}${path}`, { headers: token ? { authorization: `Bearer ${token}`, connection: 'close' } : { connection: 'close' }, redirect: 'manual' })
const post = (path, body, token) => fetch(`${base}${path}`, { method: 'POST', headers: { ...JSON_HEAD, ...(token ? { authorization: `Bearer ${token}` } : {}) }, body: JSON.stringify(body ?? {}) })
const waitForAudit = async (pred, timeoutMs = 4000) => {
  const deadline = Date.now() + timeoutMs
  while (Date.now() < deadline) {
    const e = auditQuery({ limit: 10000 }).find(pred)
    if (e !== undefined) return e
    await wait(40)
  }
  return undefined
}

try {
  /* ── 1. 令牌生成（哈希落盘、明文只此一次）────────────────────────────── */
  console.log('# 令牌生成')
  const adminTok = createServiceToken(DATA, 'e01-admin', 'admin')
  const readonlyTok = createServiceToken(DATA, 'report-readonly', 'readonly')
  check('明文 token 形态 kbsvc-<base64url>', adminTok.token.startsWith('kbsvc-') && adminTok.token.length > 40)
  check('存储只落哈希', !readFileSync(join(DATA, 'service-tokens.json'), 'utf8').includes(adminTok.token) && readFileSync(join(DATA, 'service-tokens.json'), 'utf8').includes('"tokenHash"'))
  let threw = false
  try { createServiceToken(DATA, 'e01-admin', 'admin') } catch { threw = true }
  check('重复名称被拒', threw)
  check('authenticate 命中（timingSafeEqual 路径）', authenticateServiceToken(DATA, adminTok.token)?.id === 'e01-admin')
  // P2-7：缓存按 dataDir 隔离——A 目录的令牌在 B 目录不可认证；B 目录自建令牌互不影响。
  check('cache 键控：A 目录令牌在 B 目录不可认证', authenticateServiceToken(DATA_B, adminTok.token) === null)
  const tokB = createServiceToken(DATA_B, 'b-only', 'admin')
  check('cache 键控：B 目录令牌仅在 B 目录可认证', authenticateServiceToken(DATA_B, tokB.token)?.id === 'b-only' && authenticateServiceToken(DATA, tokB.token) === null)
  check('cache 键控：A 目录原令牌不受 B 目录影响', authenticateServiceToken(DATA, adminTok.token)?.id === 'e01-admin')
  check('authenticate 非 kbsvc 串直接 null', authenticateServiceToken(DATA, 'other-secret') === null)

  /* ── 2. admin token 全通 ─────────────────────────────────────────────── */
  console.log('# admin 服务令牌')
  const list = await get('/console/api/member/list', adminTok.token)
  const listBody = await list.json()
  check('member/list 200（工具数据源结构）', list.status === 200 && Array.isArray(listBody.members) && listBody.members.length === 2 && listBody.members[0].pointsUsed !== undefined)
  const usage = await get('/console/api/member/usage?account=member@t', adminTok.token)
  const usageBody = await usage.json()
  check('member/usage 200（点数/额度/余量）', usage.status === 200 && usageBody.points === 320 && usageBody.monthlyPoints === 1000 && usageBody.remainingPoints === 680)
  check('member/usage 未知账号 404', (await get('/console/api/member/usage?account=ghost@t', adminTok.token)).status === 404)
  const upd = await post('/console/api/member/update', { account: 'member@t', department: '工程部' }, adminTok.token)
  check('admin token 变更 200', upd.status === 200)
  const updEvent = await waitForAudit((e) => e.action === 'member.update' && e.actor?.account === 'svc:e01-admin')
  check('审计 actor=svc:名称（可区分于人）', updEvent !== undefined && updEvent.actor?.role === 'admin')
  check('admin token 页面路由 401（仅 /console/api/*）', (await get('/console', adminTok.token)).status === 401 && (await get('/console/members', adminTok.token)).status === 401)

  /* ── 3. readonly 只读白名单 ───────────────────────────────────────────── */
  console.log('# readonly 服务令牌')
  check('readonly 白名单内 member/list 200', (await get('/console/api/member/list', readonlyTok.token)).status === 200)
  check('readonly 白名单内 audit 200', (await get('/console/api/audit?limit=5', readonlyTok.token)).status === 200)
  check('readonly 白名单内 toolpolicy 200', (await get('/console/api/toolpolicy', readonlyTok.token)).status === 200)
  check('readonly 白名单外 export 403', (await get('/console/api/audit/export', readonlyTok.token)).status === 403)
  check('readonly 白名单外 plugin/jobs 403', (await get('/console/api/plugin/jobs', readonlyTok.token)).status === 403)
  // P2-8：白名单外 GET 拒绝留 deny 审计（actor=svc: 身份）。
  const deniedEvent = await waitForAudit((e) => e.action === 'security.service_token_denied' && e.result === 'deny' && e.actor?.account === 'svc:report-readonly' && e.target === '/console/api/audit/export')
  check('readonly GET 白名单外 403 留 deny 痕（P2-8）', deniedEvent !== undefined)
  const roUpd = await post('/console/api/member/update', { account: 'member@t', department: '设计部' }, readonlyTok.token)
  check('readonly 变更 POST 403', roUpd.status === 403)
  const roEvent = await waitForAudit((e) => e.action === 'member.update' && e.result === 'deny' && e.actor?.account === 'svc:report-readonly')
  check('readonly 403 deny 留痕（actor=svc:）', roEvent !== undefined)

  /* ── 4. 撤销与坏 token ───────────────────────────────────────────────── */
  console.log('# 撤销与坏 token')
  check('坏 token 401', (await get('/console/api/member/list', 'kbsvc-not-a-real-token')).status === 401)
  check('无 token 无 cookie 401（登录页）', (await get('/console/api/member/list')).status === 401)
  check('revoke 返回 true 且撤销下一请求生效', revokeServiceToken(DATA, 'e01-admin') === true && (await get('/console/api/member/list', adminTok.token)).status === 401)
  // CLI 的 create 审计（security.service_token_create）由手动 CLI 验证覆盖
  // （supervisor CLI 使用固定 data/ 目录，不在本测试可达范围）。
  check('revoke 未知名称 false', revokeServiceToken(DATA, 'e01-admin') === false)
} finally {
  gateway.close()
  gateway.closeAllConnections?.()
  rmSync(DATA, { recursive: true, force: true })
  rmSync(DATA_B, { recursive: true, force: true })
}

console.log(`\n通过 ${passed}，失败 ${failed}`)
process.exit(failed > 0 ? 1 : 0)
