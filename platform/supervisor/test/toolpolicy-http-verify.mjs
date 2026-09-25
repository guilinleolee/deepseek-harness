/**
 * 工具 RBAC（阶段 9）HTTP 集成验证：临时 data/ + 随机端口起真实网关
 * （参照 auth-audit-http-verify.mjs 的受控环境），覆盖：
 * 1. GET /console/api/toolpolicy（admin/auditor 只读）与缺省策略自动生成；
 * 2. admin POST 改策略 → 200 + toolpolicy.change 审计（旧值→新值）+
 *    三实例 home 的 tool-policy.json 全量下发且内容按角色正确；
 * 3. 非法策略（未知组名）400 + fail 审计 + 存量文件零波及；
 * 4. auditor 变更 403（只读角色）+ deny 审计；employee 拒入管理台；
 * 5. 成员角色变更（member/update）→ 所在实例策略文件立即重写；
 * 6. guard 拒绝桥文件 → transcribeGuardEvents 转写成 audit.jsonl
 *    （guard.deny，actor=实例归属账号，detail 只含标量）+ 桥文件清空 +
 *    幂等（空桥文件不产生事件）。
 *
 * 全程不占用 8460/9400/3181-3183；结束关闭服务并清理临时目录。
 * 运行：node test/toolpolicy-http-verify.mjs
 */
import { existsSync, mkdtempSync, readFileSync, rmSync, statSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'

import { auditAppend, auditQuery, initAudit } from '../audit.mjs'
import { createGatewayServer, hashPassword } from '../gateway.mjs'
import { transcribeGuardEvents, truncateIfUnchanged } from '../toolpolicy.mjs'

const wait = (ms) => new Promise((r) => setTimeout(r, ms))
const JSON_HEAD = { 'content-type': 'application/json', connection: 'close' }

let passed = 0
let failed = 0
const check = (name, cond) => {
  if (cond === true) { passed += 1; console.log(`  ok  ${name}`) } else { failed += 1; console.error(`FAIL  ${name}`) }
}

const DATA = mkdtempSync(join(tmpdir(), 'lyz-toolpolicy-http-'))
const now = new Date().toISOString()
const homeOf = (id) => join(DATA, 'homes', id)
const homePolicyOf = (id) => JSON.parse(readFileSync(join(homeOf(id), 'tool-policy.json'), 'utf8'))
const account = (id, acc, role, pw) => ({
  id, account: acc, displayName: id, role, department: '验证组', instanceId: '',
  tokenEpoch: 0, createdAt: now, passwordHash: hashPassword(pw),
})
const adminRec = account('acc-admin', 'admin@t', 'admin', 'AdminPass1')
const memberRec = account('acc-member', 'member-a@t', 'employee', 'MemberPass1')
const auditorRec = account('acc-auditor', 'member-b@t', 'auditor', 'AuditPass1')
adminRec.instanceId = 'e01'
memberRec.instanceId = 'e02'
auditorRec.instanceId = 'e03'
writeFileSync(join(DATA, 'accounts.json'), `${JSON.stringify({ accounts: [adminRec, memberRec, auditorRec] }, null, 2)}\n`)
initAudit(DATA)

const manifest = {
  gatewayHost: 'localhost', portalPort: 0, relayPort: 0, repoRoot: '.',
  instances: [
    { id: 'e01', account: 'admin@t', uid: 1, port: 1 },
    { id: 'e02', account: 'member-a@t', uid: 2, port: 2 },
    { id: 'e03', account: 'member-b@t', uid: 3, port: 3 },
  ],
}
const gateway = createGatewayServer({ manifest, getState: () => ({ instances: {} }), dataDir: DATA })
await new Promise((r) => gateway.listen(0, '127.0.0.1', r))
const base = `http://127.0.0.1:${gateway.address().port}`
const post = async (path, body, cookie) =>
  fetch(`${base}${path}`, { method: 'POST', headers: cookie ? { ...JSON_HEAD, cookie } : JSON_HEAD, body: JSON.stringify(body ?? {}) })
const get = async (path, cookie) =>
  fetch(`${base}${path}`, { headers: cookie ? { cookie, connection: 'close' } : { connection: 'close' } })
const login = async (acc, pw) => {
  const res = await post('/api/auth/login', { account: acc, password: pw })
  return { status: res.status, cookie: res.headers.getSetCookie()[0]?.split(';')[0], body: await res.json().catch(() => ({})) }
}
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
  /* ── 1. 缺省策略自动生成 + 只读 GET ───────────────────────────────────── */
  console.log('# 缺省策略与只读 GET')
  const admin = await login('admin@t', 'AdminPass1')
  check('admin 登录 200', admin.status === 200 && admin.cookie !== undefined)
  const got = await get('/console/api/toolpolicy', admin.cookie)
  const gotBody = await got.json()
  check('GET toolpolicy 200', got.status === 200)
  check('缺省策略文件自动生成', existsSync(join(DATA, 'toolpolicy.json')))
  check('缺省策略：auditor/employee 禁 command+network，admin 全开',
    JSON.stringify(gotBody.policy.roles.auditor.deny) === JSON.stringify(['command', 'network'])
    && JSON.stringify(gotBody.policy.roles.employee.deny) === JSON.stringify(['command', 'network'])
    && gotBody.policy.roles.admin.deny.length === 0)
  const auditor = await login('member-b@t', 'AuditPass1')
  check('auditor 登录 200 且可只读 GET', auditor.status === 200 && (await get('/console/api/toolpolicy', auditor.cookie)).status === 200)

  /* ── 2. admin 改策略 → 下发三实例 + 审计旧值→新值 ─────────────────────── */
  console.log('# admin 改策略与全量下发')
  const changed = await post('/console/api/toolpolicy', {
    roles: {
      auditor: { deny: ['command', 'network', 'fs'] },
      employee: { deny: ['command'] },
    },
  }, admin.cookie)
  check('POST toolpolicy 200', changed.status === 200)
  const ev = await waitForAudit((e) => e.action === 'toolpolicy.change' && e.result === 'ok')
  check('toolpolicy.change 落盘 ok', ev !== undefined)
  check('审计 detail 含旧值→新值',
    JSON.stringify(ev?.detail?.old?.roles?.auditor?.deny) === JSON.stringify(['command', 'network'])
    && JSON.stringify(ev?.detail?.new?.roles?.auditor?.deny) === JSON.stringify(['command', 'fs', 'network']))
  check('审计 target=tool-policy', ev?.target === 'tool-policy')
  check('e01（admin）下发全开', JSON.stringify(homePolicyOf('e01').deny) === '[]' && homePolicyOf('e01').role === 'admin')
  check('e02（employee）只禁 command', JSON.stringify(homePolicyOf('e02').deny) === JSON.stringify(['command']) && homePolicyOf('e02').role === 'employee')
  check('e03（auditor）三组全禁（deny 归一化为组规范顺序）', JSON.stringify(homePolicyOf('e03').deny) === JSON.stringify(['command', 'fs', 'network']) && homePolicyOf('e03').role === 'auditor')
  const rolesHtml = await (await get('/console/roles', admin.cookie)).text()
  check('部门与角色页含可编辑工具组面板', rolesHtml.includes('实例内工具组策略') && rolesHtml.includes('employee-command') && rolesHtml.includes('saveToolPolicy'))

  /* ── 3. 非法策略 400 + fail 审计 + 存量零波及 ─────────────────────────── */
  console.log('# 非法策略拒绝')
  const before = readFileSync(join(homeOf('e02'), 'tool-policy.json'), 'utf8')
  const bad = await post('/console/api/toolpolicy', { roles: { employee: { deny: ['shell'] } } }, admin.cookie)
  check('未知组名 400 + 中文文案', bad.status === 400 && String((await bad.json()).error ?? '').includes('deny'))
  const badEv = await waitForAudit((e) => e.action === 'toolpolicy.change' && e.result === 'fail')
  check('非法策略 fail 留痕', badEv !== undefined)
  check('存量 home 策略零波及', readFileSync(join(homeOf('e02'), 'tool-policy.json'), 'utf8') === before)

  /* ── 4. auditor 变更 403、employee 拒入 ───────────────────────────────── */
  console.log('# 角色门禁')
  const aPost = await post('/console/api/toolpolicy', { roles: { employee: { deny: [] } } }, auditor.cookie)
  check('auditor 改策略 403 只读文案', aPost.status === 403 && (await aPost.json()).error === '审计员为只读角色')
  check('auditor 403 deny 留痕', await waitForAudit((e) => e.action === 'toolpolicy.change' && e.result === 'deny') !== undefined)
  const employee = await login('member-a@t', 'MemberPass1')
  check('employee 登录 200', employee.status === 200)
  check('employee GET 管理台 403', (await get('/console/api/toolpolicy', employee.cookie)).status === 403)

  /* ── 5. 成员角色变更 → 所在实例策略重写 ───────────────────────────────── */
  console.log('# 角色变更联动下发')
  const roleChange = await post('/console/api/member/update', { account: 'member-a@t', role: 'auditor' }, admin.cookie)
  check('改角色 200', roleChange.status === 200)
  check('e02 策略立即按 auditor 新角色重写（三组全禁）',
    JSON.stringify(homePolicyOf('e02').deny) === JSON.stringify(['command', 'fs', 'network']) && homePolicyOf('e02').role === 'auditor')

  /* ── 6. guard 桥文件 → 转写审计 + 清空 + 幂等 ─────────────────────────── */
  console.log('# guard 事件转写')
  writeFileSync(join(homeOf('e02'), 'guard-events.jsonl'),
    `${JSON.stringify({ ts: now, tool: 'bash', group: 'command', decision: 'deny' })}\n`
    + `${JSON.stringify({ ts: now, tool: 'web_search', group: 'network', decision: 'deny' })}\n`
    + '这行是半行损坏\n')
  writeFileSync(join(homeOf('e03'), 'guard-events.jsonl'),
    `${JSON.stringify({ ts: now, tool: 'grep', group: 'fs', decision: 'deny' })}\n`)
  const t = await transcribeGuardEvents(DATA, manifest, auditAppend)
  check('转写 3 条（坏行跳过）', t.transcribed === 3 && t.instances.length === 2)
  const denyEvents = auditQuery({ actionPrefix: 'guard.deny', limit: 100 })
  check('audit.jsonl 出现 3 条 guard.deny', denyEvents.length === 3)
  const bashEvent = denyEvents.find((e) => e.target === 'bash')
  check('actor=实例归属账号', bashEvent?.actor?.account === 'member-a@t')
  check('detail 只含工具/分组/实例标量', bashEvent?.detail?.tool === 'bash' && bashEvent?.detail?.group === 'command' && bashEvent?.detail?.instance === 'e02')
  check('e03 事件归属正确（fs/grep/member-b）', denyEvents.some((e) => e.target === 'grep' && e.detail?.instance === 'e03' && e.actor?.account === 'member-b@t'))
  check('桥文件转写后清空', readFileSync(join(homeOf('e02'), 'guard-events.jsonl'), 'utf8') === '' && readFileSync(join(homeOf('e03'), 'guard-events.jsonl'), 'utf8') === '')
  const t2 = await transcribeGuardEvents(DATA, manifest, auditAppend)
  check('空桥文件幂等（0 条）', t2.transcribed === 0 && auditQuery({ actionPrefix: 'guard.deny', limit: 100 }).length === 3)

  /* ── 7. 截断前重读比对（P1-3：并发追加不被截断销毁）──────────────────── */
  console.log('# 截断前指纹比对')
  const bridge1 = join(homeOf('e02'), 'guard-events.jsonl')
  const line1 = `${JSON.stringify({ ts: now, tool: 'bash', group: 'command', decision: 'deny' })}\n`
  const line2 = `${JSON.stringify({ ts: now, tool: 'grep', group: 'fs', decision: 'deny' })}\n`
  writeFileSync(bridge1, line1)
  const snap = { mtimeMs: statSync(bridge1).mtimeMs, size: statSync(bridge1).size }
  writeFileSync(bridge1, line1 + line2) // 模拟 guard 在快照之后又追加了一条
  check('指纹变化 → 不截断、文件保留两条', truncateIfUnchanged(bridge1, snap) === false
    && readFileSync(bridge1, 'utf8').trimEnd().split('\n').length === 2)
  const fresh = { mtimeMs: statSync(bridge1).mtimeMs, size: statSync(bridge1).size }
  check('指纹一致 → 截断清空', truncateIfUnchanged(bridge1, fresh) === true && readFileSync(bridge1, 'utf8') === '')
  check('文件消失 → 返回 false 不抛错', truncateIfUnchanged(join(homeOf('e02'), 'no-such-file.jsonl'), { mtimeMs: 1, size: 1 }) === false)
} finally {
  gateway.close()
  gateway.closeAllConnections?.()
  rmSync(DATA, { recursive: true, force: true })
}

console.log(`\n通过 ${passed}，失败 ${failed}`)
process.exit(failed > 0 ? 1 : 0)
