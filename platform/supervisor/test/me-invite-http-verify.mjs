/**
 * 个人中心 + 邀请注册（阶段 10）HTTP 集成验证：临时 data/ + 随机端口起真实
 * 网关（限流验收用独立第二网关隔离计数桶）。覆盖：
 * 1. /me 访问矩阵：employee 200 且只含本人数据（忽略查询参数）；admin/auditor
 *    同样可用（页顶「返回管理台」）；未认证 401 登录页；/login 直达与按角色跳转；
 * 2. 改密：错当前密码 400、弱新密码 400（策略文案）、两次不一致 400，全部
 *    member.self_password_change 留痕；成功后旧 JWT 401、新密码可登录；
 * 3. 用量三形态：点数（320/1000）、旧制（120/500 + 旧制标注）、不限额度；
 * 4. 下线所有设备：auth.revoke_all 留痕 + 旧 JWT 401；
 * 5. 邀请全流程：生成（审计不含明文 code）→ 注册页预设渲染 → 注册成功
 *    （角色/部门/实例正确 + tool-policy 下发 + member.register 留痕）→
 *    同 code 二次注册被拒（code_used）→ 撤销被拒 → 过期被拒 → 无效 code；
 * 6. 权限边界：employee 调 invite/create 403；
 * 7. 速率限制：独立网关上同 IP 连续无效注册达阈值即 429（有效邀请也 429）。
 *
 * 全程不占用 8460/9400/3181-3183；结束关闭全部服务并清理临时目录。
 * 运行：node test/me-invite-http-verify.mjs
 */
import { createHash } from 'node:crypto'
import { existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync, statSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'

import { auditQuery, initAudit } from '../audit.mjs'
import { createGatewayServer, hashPassword } from '../gateway.mjs'

const wait = (ms) => new Promise((r) => setTimeout(r, ms))
const JSON_HEAD = { 'content-type': 'application/json', connection: 'close' }

let passed = 0
let failed = 0
const check = (name, cond) => {
  if (cond === true) { passed += 1; console.log(`  ok  ${name}`) } else { failed += 1; console.error(`FAIL  ${name}`) }
}

const DATA = mkdtempSync(join(tmpdir(), 'lyz-me-invite-'))
const now = new Date().toISOString()
const month = `${new Date().getFullYear()}-${String(new Date().getMonth() + 1).padStart(2, '0')}`
const account = (id, acc, role, pw, extra = {}) => ({
  id, account: acc, displayName: id, role, department: '验证组', instanceId: 'e02',
  tokenEpoch: 0, createdAt: now, passwordHash: hashPassword(pw), ...extra,
})
const adminRec = { ...account('a1', 'admin@t', 'admin', 'AdminPass1'), instanceId: 'e01' }
writeFileSync(join(DATA, 'accounts.json'), `${JSON.stringify({ accounts: [
  adminRec,
  account('m1', 'member-a@t', 'employee', 'MemberPass1'),
  account('m2', 'member-b@t', 'auditor', 'AuditPass1'),
  account('p1', 'points@t', 'employee', 'PointsPass1', { monthlyPoints: 1000 }),
  account('l1', 'legacy@t', 'employee', 'LegacyPw12', { monthlyTokens: 500 }),
  account('n1', 'noquota@t', 'employee', 'NoquotaP1'),
] }, null, 2)}\n`)
writeFileSync(join(DATA, 'usage.json'), `${JSON.stringify({ months: { [month]: {
  'points@t': { tokensIn: 50, tokensOut: 10, requests: 7, points: 320 },
  'legacy@t': { tokensIn: 100, tokensOut: 20, requests: 2, points: 0 },
} } }, null, 2)}\n`)
// 邀请与注册按 IP 限速复用 security.json 参数（默认阈值即可，限流专项用独立网关）。
initAudit(DATA)

const manifest = {
  gatewayHost: 'localhost', portalPort: 0, relayPort: 0, repoRoot: '.',
  instances: [
    // e01 的 account 刻意携带恶意串：入口页插值必须转义（P2-7 断言）。
    { id: 'e01', account: 'x"><script>alert(1)</script>', uid: 1, port: 1 },
    { id: 'e02', account: 'member-a@t', uid: 2, port: 2 },
  ],
}
const gateway = createGatewayServer({ manifest, getState: () => ({ instances: {} }), dataDir: DATA })
await new Promise((r) => gateway.listen(0, '127.0.0.1', r))
const base = `http://127.0.0.1:${gateway.address().port}`
const post = async (path, body, cookie) =>
  fetch(`${base}${path}`, { method: 'POST', headers: cookie ? { ...JSON_HEAD, cookie } : JSON_HEAD, body: JSON.stringify(body ?? {}) })
const get = async (path, cookie) =>
  fetch(`${base}${path}`, { headers: cookie ? { cookie, connection: 'close' } : { connection: 'close' }, redirect: 'manual' })
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
const adminLogin = () => login('admin@t', 'AdminPass1')

try {
  /* ── 1. /me 访问矩阵与数据隔离 ────────────────────────────────────────── */
  console.log('# /me 访问矩阵')
  const admin = await adminLogin()
  check('admin 登录 200', admin.status === 200)
  const emp = await login('member-a@t', 'MemberPass1')
  check('employee 登录 200', emp.status === 200)
  const auditor = await login('member-b@t', 'AuditPass1')
  check('auditor 登录 200', auditor.status === 200)

  const meEmp = await get('/me', emp.cookie)
  const meEmpText = await meEmp.text()
  check('employee /me 200', meEmp.status === 200)
  check('只含本人数据（本人账号/部门/实例链接）', meEmpText.includes('member-a@t') && meEmpText.includes('e02.localhost') && meEmpText.includes('验证组'))
  check('不含他人账号与用量', !meEmpText.includes('admin@t') && !meEmpText.includes('member-b@t') && !meEmpText.includes('points@t'))
  check('含改密与设备区块', meEmpText.includes('修改密码') && meEmpText.includes('下线所有设备'))
  check('含最近登录（本人 IP）', meEmpText.includes('127.0.0.1'))
  const meEmpProbe = await get('/me?account=admin@t', emp.cookie)
  check('查询参数被忽略（仍只渲染本人）', meEmpProbe.status === 200 && !(await meEmpProbe.text()).includes('admin@t'))
  const meAdmin = await get('/me', admin.cookie)
  const meAdminText = await meAdmin.text()
  check('admin /me 同样可用（选择：不重定向）且含返回管理台', meAdmin.status === 200 && meAdminText.includes('返回管理台'))
  check('auditor /me 同样可用', (await get('/me', auditor.cookie)).status === 200)
  const meAnon = await get('/me')
  check('未认证 /me 401 + 登录页', meAnon.status === 401 && (await meAnon.text()).includes('登录'))
  const loginAnon = await get('/login')
  check('/login 未认证 200 表单', loginAnon.status === 200 && (await loginAnon.text()).includes('账号（邮箱）'))
  const loginEmp = await get('/login', emp.cookie)
  check('/login 已认证 employee 303 → /me', loginEmp.status === 303 && loginEmp.headers.get('location') === '/me')
  const loginAdmin = await get('/login', admin.cookie)
  check('/login 已认证 admin 303 → 入口页', loginAdmin.status === 303 && loginAdmin.headers.get('location') === '/')
  const loginPageHtml = await (await get('/login')).text()
  check('登录页含员工跳 /me 逻辑', loginPageHtml.includes("/me"))
  const portalHome = await get('/', admin.cookie)
  const portalText = await portalHome.text()
  check('入口页 account 插值转义（P2-7）', portalHome.status === 200 && portalText.includes('&lt;script&gt;') && !portalText.includes('<script>alert(1)'))

  /* ── 2. 改密全路径 ───────────────────────────────────────────────────── */
  console.log('# 改密')
  const wrongPw = await post('/api/me/password', { currentPassword: 'WrongPass9', newPassword: 'NewPass123', confirmPassword: 'NewPass123' }, emp.cookie)
  check('错当前密码 400 + 中文文案', wrongPw.status === 400 && String((await wrongPw.json()).error ?? '').includes('当前密码不正确'))
  check('wrong_password 留痕', await waitForAudit((e) => e.action === 'member.self_password_change' && e.result === 'fail' && e.detail?.reason === 'wrong_password') !== undefined)
  const weakPw = await post('/api/me/password', { currentPassword: 'MemberPass1', newPassword: 'weak', confirmPassword: 'weak' }, emp.cookie)
  check('弱新密码 400 + 策略文案', weakPw.status === 400 && String((await weakPw.json()).error ?? '').includes('密码'))
  const mismatch = await post('/api/me/password', { currentPassword: 'MemberPass1', newPassword: 'NewPass123', confirmPassword: 'NewPass999' }, emp.cookie)
  check('两次不一致 400', mismatch.status === 400 && String((await mismatch.json()).error ?? '').includes('不一致'))
  const pwOk = await post('/api/me/password', { currentPassword: 'MemberPass1', newPassword: 'NewPass123', confirmPassword: 'NewPass123' }, emp.cookie)
  const pwOkBody = await pwOk.json()
  check('改密成功 200 + 全端下线提示', pwOk.status === 200 && String(pwOkBody.message ?? '').includes('重新登录'))
  check('member.self_password_change ok 留痕', await waitForAudit((e) => e.action === 'member.self_password_change' && e.result === 'ok') !== undefined)
  check('旧 JWT 立即失效（/me 401）', (await get('/me', emp.cookie)).status === 401)
  const relogin = await login('member-a@t', 'NewPass123')
  check('新密码可登录', relogin.status === 200)
  check('旧密码不可登录', (await login('member-a@t', 'MemberPass1')).status === 401)

  /* ── 3. 用量三形态 ───────────────────────────────────────────────────── */
  console.log('# 本人用量三形态')
  const pts = await login('points@t', 'PointsPass1')
  const ptsText = await (await get('/me', pts.cookie)).text()
  check('点数形态 320/1000', ptsText.includes('320/1000') && ptsText.includes('点数'))
  const legacy = await login('legacy@t', 'LegacyPw12')
  const legacyText = await (await get('/me', legacy.cookie)).text()
  check('旧制形态 120/500 + 旧制标注', legacyText.includes('120/500') && legacyText.includes('旧制'))
  const noq = await login('noquota@t', 'NoquotaP1')
  const noqText = await (await get('/me', noq.cookie)).text()
  check('无记录且无额度 → 不限额度 0 点', noqText.includes('不限额度') && noqText.includes('0 点'))

  /* ── 4. 下线所有设备 ─────────────────────────────────────────────────── */
  console.log('# 下线所有设备')
  const rv = await post('/api/me/revoke-all', {}, auditor.cookie)
  check('revoke-all 200', rv.status === 200)
  check('auth.revoke_all 留痕（actor=本人）', await waitForAudit((e) => e.action === 'auth.revoke_all' && e.actor?.account === 'member-b@t') !== undefined)
  check('旧 JWT 401', (await get('/me', auditor.cookie)).status === 401)

  /* ── 5. 邀请全流程 ───────────────────────────────────────────────────── */
  console.log('# 邀请注册全流程')
  const inv = await post('/console/api/invite/create', { department: '设计部', role: 'employee', instanceId: 'e02', expiresInHours: 1 }, admin.cookie)
  const invBody = await inv.json()
  check('invite/create 200 + 一次性链接', inv.status === 200 && String(invBody.registerUrl ?? '').startsWith('/register?code=inv-'))
  check('invite.create 留痕且不含明文 code', await waitForAudit((e) => e.action === 'invite.create' && e.result === 'ok' && !JSON.stringify(e.detail ?? {}).includes('inv-')) !== undefined)
  const code = invBody.registerUrl.split('code=')[1]
  const regPage = await get(invBody.registerUrl)
  const regPageText = await regPage.text()
  check('注册页免登录 200 且渲染预设', regPage.status === 200 && regPageText.includes('设计部') && regPageText.includes('成员') && regPageText.includes('邀请有效'))
  const regOk = await post('/api/register', { code, account: 'newbie@t', displayName: '新员工', password: 'GoodPass123', confirmPassword: 'GoodPass123' })
  check('注册成功 200', regOk.status === 200)
  const regEvent = await waitForAudit((e) => e.action === 'member.register' && e.result === 'ok' && e.target === 'newbie@t')
  check('member.register ok 留痕（actor=本人）', regEvent !== undefined && regEvent.actor?.account === 'newbie@t')
  check('注册审计 detail 无密码字段', regEvent !== undefined && !JSON.stringify(regEvent.detail ?? {}).toLowerCase().includes('password'))
  const newbie = await login('newbie@t', 'GoodPass123')
  check('新账号可登录且实例绑定正确', newbie.status === 200 && newbie.body.instance === 'e02')
  const newbieMe = await (await get('/me', newbie.cookie)).text()
  check('新账号角色/部门来自邀请预设', newbieMe.includes('设计部') && newbieMe.includes('成员'))
  check('注册后该实例 tool-policy 已下发（阶段 9 复用）', existsSync(join(DATA, 'homes', 'e02', 'tool-policy.json')))
  const regAgain = await post('/api/register', { code, account: 'other@t', password: 'GoodPass123', confirmPassword: 'GoodPass123' })
  check('同 code 二次注册被拒（used）', regAgain.status === 400 && String((await regAgain.json()).error ?? '').includes('已被使用'))
  check('code_used fail 留痕', await waitForAudit((e) => e.action === 'member.register' && e.result === 'fail' && e.detail?.reason === 'code_used') !== undefined)

  const inv2 = await post('/console/api/invite/create', { department: '设计部', role: 'auditor', instanceId: 'e02' }, admin.cookie)
  const inv2Body = await inv2.json()
  const code2 = inv2Body.registerUrl.split('code=')[1]
  const rvk = await post('/console/api/invite/revoke', { id: inv2Body.id }, admin.cookie)
  check('invite/revoke 200 + 留痕', rvk.status === 200 && await waitForAudit((e) => e.action === 'invite.revoke' && e.result === 'ok') !== undefined)
  const regRevoked = await post('/api/register', { code: code2, account: 'other2@t', password: 'GoodPass123', confirmPassword: 'GoodPass123' })
  check('撤销后注册被拒', regRevoked.status === 400 && String((await regRevoked.json()).error ?? '').includes('撤销'))
  const dupRevoke = await post('/console/api/invite/revoke', { id: inv2Body.id }, admin.cookie)
  check('重复撤销 404', dupRevoke.status === 404)

  const expiredCode = 'inv-expired-code-test'
  const invitesStore = JSON.parse(readFileSync(join(DATA, 'invites.json'), 'utf8'))
  invitesStore.invites.push({
    id: 'inv-expired', codeHash: createHash('sha256').update(expiredCode, 'utf8').digest('hex'),
    department: '设计部', role: 'employee', instanceId: 'e02',
    expiresAt: new Date(Date.now() - 3_600_000).toISOString(), used: false, createdAt: now,
  })
  writeFileSync(join(DATA, 'invites.json'), `${JSON.stringify(invitesStore, null, 2)}\n`)
  const regExpired = await post('/api/register', { code: expiredCode, account: 'other3@t', password: 'GoodPass123', confirmPassword: 'GoodPass123' })
  check('过期 code 注册被拒', regExpired.status === 400 && String((await regExpired.json()).error ?? '').includes('已过期'))
  const regInvalid = await post('/api/register', { code: 'inv-not-a-real-code', account: 'other4@t', password: 'GoodPass123', confirmPassword: 'GoodPass123' })
  check('无效 code 注册被拒', regInvalid.status === 400 && String((await regInvalid.json()).error ?? '').includes('邀请链接无效'))
  // P2-2 纵深：手改存储造出的 admin 邀请一律无效（哈希正确也不放行）
  const adminInviteCode = 'inv-admin-role-code01'
  invitesStore.invites.push({
    id: 'inv-admin-role', codeHash: createHash('sha256').update(adminInviteCode, 'utf8').digest('hex'),
    department: '设计部', role: 'admin', instanceId: 'e02',
    expiresAt: new Date(Date.now() + 3_600_000).toISOString(), used: false, createdAt: now,
  })
  writeFileSync(join(DATA, 'invites.json'), `${JSON.stringify(invitesStore, null, 2)}\n`)
  const regAdminRole = await post('/api/register', { code: adminInviteCode, account: 'noadmin@t', password: 'GoodPass123', confirmPassword: 'GoodPass123' })
  check('手改存储的 admin 邀请被拒（纵深）', regAdminRole.status === 400 && String((await regAdminRole.json()).error ?? '').includes('邀请链接无效'))
  // P2-1 白名单：畸形 code 不经哈希比较直接按无效渲染，payload 不回流页面
  const xssRegPage = await get('/register?code=%22%3E%3Cscript%3Ealert(1)%3C%2Fscript%3E')
  const xssRegText = await xssRegPage.text()
  check('畸形 code 白名单拒绝且不回流页面', xssRegPage.status === 200 && xssRegText.includes('邀请链接无效') && !xssRegText.includes('<script>alert'))
  // P1-1 未预期抛错转 500（把 vkeys.json 换成目录 → issueVkey 落盘 rename 必抛，
  // readStore 的兜底不会吞这种错误），客户端不挂死
  const inv5 = await post('/console/api/invite/create', { department: '设计部', role: 'employee', instanceId: 'e02' }, admin.cookie)
  const code5 = (await inv5.json()).registerUrl.split('code=')[1]
  const vkeysPath = join(DATA, 'vkeys.json')
  const vkeysBackup = readFileSync(vkeysPath, 'utf8')
  rmSync(vkeysPath)
  mkdirSync(vkeysPath)
  const boom = await post('/api/register', { code: code5, account: 'boom@t', password: 'GoodPass123', confirmPassword: 'GoodPass123' })
  const boomBody = await boom.json().catch(() => ({}))
  check('注册内部抛错转 500 且有响应体（不挂死）', boom.status === 500 && typeof boomBody.error === 'string')
  check('internal fail 留痕', await waitForAudit((e) => e.action === 'member.register' && e.result === 'fail' && e.detail?.reason === 'internal') !== undefined)
  rmSync(vkeysPath, { recursive: true, force: true })
  writeFileSync(vkeysPath, vkeysBackup)
  const afterFix = await post('/api/register', { code: code5, account: 'boom2@t', password: 'GoodPass123', confirmPassword: 'GoodPass123' })
  check('抛错的注册未消耗邀请（修复后同 code 可注册）', afterFix.status === 200)
  const inv4 = await post('/console/api/invite/create', { department: '设计部', role: 'employee', instanceId: 'e02' }, admin.cookie)
  const code4 = (await inv4.json()).registerUrl.split('code=')[1]
  const weakReg = await post('/api/register', { code: code4, account: 'other5@t', password: 'weak', confirmPassword: 'weak' })
  check('弱密码注册被拒（策略文案）', weakReg.status === 400 && String((await weakReg.json()).error ?? '').includes('密码'))
  const regOk2 = await post('/api/register', { code: code4, account: 'other5@t', password: 'GoodPass123', confirmPassword: 'GoodPass123' })
  check('失败的注册不消耗邀请（同 code 可再注册）', regOk2.status === 200)

  /* ── 6. 权限边界 ─────────────────────────────────────────────────────── */
  console.log('# 权限边界')
  check('employee 调 invite/create 403', (await post('/console/api/invite/create', { role: 'employee', instanceId: 'e02' }, newbie.cookie)).status === 403)
  check('employee /me 不含他人用量行', !(await (await get('/me', newbie.cookie)).text()).includes('points@t'))

  /* ── 7. 速率限制（独立网关隔离计数桶）────────────────────────────────── */
  console.log('# 注册速率限制')
  const DATA2 = mkdtempSync(join(tmpdir(), 'lyz-me-invite-rate-'))
  writeFileSync(join(DATA2, 'accounts.json'), `${JSON.stringify({ accounts: [adminRec] }, null, 2)}\n`)
  writeFileSync(join(DATA2, 'security.json'), `${JSON.stringify({ loginWindowMinutes: 15, loginMaxFails: 3, lockoutMinutes: 15, passwordMinLength: 8, passwordMinClasses: 3 })}\n`)
  initAudit(DATA2)
  const gateway2 = createGatewayServer({ manifest, getState: () => ({ instances: {} }), dataDir: DATA2 })
  await new Promise((r) => gateway2.listen(0, '127.0.0.1', r))
  try {
    const base2 = `http://127.0.0.1:${gateway2.address().port}`
    const post2 = (path, body, cookie) => fetch(`${base2}${path}`, { method: 'POST', headers: cookie ? { ...JSON_HEAD, cookie } : JSON_HEAD, body: JSON.stringify(body ?? {}) })
    const admin2 = await (async () => {
      const res = await post2('/api/auth/login', { account: 'admin@t', password: 'AdminPass1' })
      return res.headers.getSetCookie()[0]?.split(';')[0]
    })()
    const inv3 = await post2('/console/api/invite/create', { department: '设计部', role: 'employee', instanceId: 'e02' }, admin2)
    const code3 = (await inv3.json()).registerUrl.split('code=')[1]
    for (let i = 0; i < 3; i++) {
      const bad = await post2('/api/register', { code: 'inv-wrong', account: `x${i}@t`, password: 'GoodPass123', confirmPassword: 'GoodPass123' })
      check(`无效注册 #${i + 1} 400`, bad.status === 400)
    }
    const locked = await post2('/api/register', { code: 'inv-wrong', account: 'x9@t', password: 'GoodPass123', confirmPassword: 'GoodPass123' })
    check('第 4 次无效注册 429 限流', locked.status === 429)
    check('rate_limited deny 留痕', await waitForAudit((e) => e.action === 'member.register' && e.result === 'deny' && e.detail?.reason === 'rate_limited') !== undefined)
    const validButLocked = await post2('/api/register', { code: code3, account: 'lucky@t', password: 'GoodPass123', confirmPassword: 'GoodPass123' })
    check('限流期间有效邀请也被拒（429 先于 code 校验）', validButLocked.status === 429)
    initAudit(DATA)
  } finally {
    gateway2.close()
    gateway2.closeAllConnections?.()
    rmSync(DATA2, { recursive: true, force: true })
  }
} finally {
  gateway.close()
  gateway.closeAllConnections?.()
  rmSync(DATA, { recursive: true, force: true })
}

console.log(`\n通过 ${passed}，失败 ${failed}`)
process.exit(failed > 0 ? 1 : 0)
