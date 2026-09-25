/**
 * TOTP 两步验证（阶段 11A）验证：RFC 6238 附录 B 标准向量 + HTTP 全流程。
 *
 * 向量部分：secret = ASCII "12345678901234567890"（20 字节），SHA1/8 位
 * 逐时间片对照 RFC 6238 附录 B；另覆盖 base32 往返、容错与非法输入、
 * AES-GCM 加解密往返与坏密文拒绝。
 * HTTP 部分（随机端口 + 临时 data/，不占 8460/9400/3181-3183）：
 * 绑定（setup→错码拒→对码 confirm）→ 登录 totp_required（无 cookie）→
 * 错 code 401 且 auth.totp_fail 留痕 → 对 code 登录成功（login_success
 * detail totp:true）→ disable 恢复单因子 → admin reset 救援 → 软强制
 * needs_2fa_enrollment → 限流同桶（错 3 次后对码也 429）。
 *
 * 运行：node test/twofa-http-verify.mjs
 */
import { createHash } from 'node:crypto'
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'

import { auditAppend, auditQuery, initAudit } from '../audit.mjs'
import { createGatewayServer, getOrCreateSecret, hashPassword } from '../gateway.mjs'
import { saveSecurityConfig } from '../security.mjs'
import { base32Decode, base32Encode, decryptText, deriveKey, encryptText, generateTotpSecret, otpauthUrl, totp, verifyTotp } from '../totp.mjs'

const wait = (ms) => new Promise((r) => setTimeout(r, ms))
const JSON_HEAD = { 'content-type': 'application/json', connection: 'close' }

let passed = 0
let failed = 0
const check = (name, cond) => {
  if (cond === true) { passed += 1; console.log(`  ok  ${name}`) } else { failed += 1; console.error(`FAIL  ${name}`) }
}
const codeAt = (base32Secret, time, digits = 6) => totp(base32Decode(base32Secret), { time, digits })

/* ── 1. RFC 6238 附录 B 标准向量（SHA1、8 位）────────────────────────────── */
console.log('# RFC 6238 附录 B 向量')
const RFC_SECRET = Buffer.from('12345678901234567890', 'ascii')
const RFC_VECTORS = [
  [59, '94287082'],
  [1_111_111_109, '07081804'],
  [1_111_111_111, '14050471'],
  [1_234_567_890, '89005924'],
  [2_000_000_000, '69279037'],
  [20_000_000_000, '65353130'],
]
for (const [seconds, expected] of RFC_VECTORS) {
  const got = totp(RFC_SECRET, { time: seconds * 1000, digits: 8 })
  check(`T=${seconds} → ${expected}`, got === expected)
}
check('6 位 = 8 位值后 6 位（T=59 → 287082）', totp(RFC_SECRET, { time: 59_000, digits: 6 }) === '287082')
check('±1 窗口放行（T=59 的码在 T=89 仍过）', verifyTotp(RFC_SECRET, '287082', { time: 89_000, window: 1 }))
check('±1 窗口外拒绝（T=149）', verifyTotp(RFC_SECRET, '287082', { time: 149_000, window: 1 }) === false)
check('非数字/位数不符直接拒绝', verifyTotp(RFC_SECRET, '28708', { time: 59_000 }) === false && verifyTotp(RFC_SECRET, '28708a', { time: 59_000 }) === false)

/* ── 2. base32 与 AES-GCM ───────────────────────────────────────────────── */
console.log('# base32 与 AES-GCM')
const roundtrip = generateTotpSecret()
check('base32 往返一致', base32Encode(base32Decode(roundtrip)) === roundtrip)
check('base32 字符集合法（RFC 4648）', /^[A-Z2-7]+$/.test(roundtrip))
check('base32 容忍小写与空格', Buffer.compare(base32Decode(roundtrip.toLowerCase()), base32Decode(roundtrip)) === 0)
let threw = false
try { base32Decode('abc1!') } catch { threw = true }
check('非法字符抛错（含 0/1/8/9 与符号）', threw)
const key = deriveKey('unit-test-secret')
const enc = encryptText(key, 'JBSWY3DPEHPK3PXP')
check('密文带 enc:v1 前缀且不含明文', enc.startsWith('enc:v1:') && !enc.includes('JBSWY3DP'))
check('解密往返一致', decryptText(key, enc) === 'JBSWY3DPEHPK3PXP')
check('密文随机化（同明文两次密文不同）', encryptText(key, 'x') !== encryptText(key, 'x'))
threw = false
try { decryptText(key, 'plaintext-not-enc') } catch { threw = true }
check('非 enc 前缀密文拒绝解密', threw)
const wrongKey = deriveKey('other-secret')
threw = false
try { decryptText(wrongKey, enc) } catch { threw = true }
check('错误密钥 GCM 认证失败拒绝', threw)

/* ── 3. HTTP 全流程 ─────────────────────────────────────────────────────── */
console.log('# HTTP 全流程')
const DATA = mkdtempSync(join(tmpdir(), 'lyz-twofa-http-'))
const now = new Date().toISOString()
const mkAccount = (id, acc, role, pw) => ({
  id, account: acc, displayName: id, role, department: '验证组', instanceId: 'e02',
  tokenEpoch: 0, createdAt: now, passwordHash: hashPassword(pw),
})
writeFileSync(join(DATA, 'accounts.json'), `${JSON.stringify({ accounts: [
  mkAccount('a1', 'admin@t', 'admin', 'AdminPass1'),
  mkAccount('m1', 'member@t', 'employee', 'MemberPass1'),
] }, null, 2)}\n`)
initAudit(DATA)
// 限流阈值 3：TOTP 猜测与密码猜测同桶（见流程 D）。
writeFileSync(join(DATA, 'security.json'), `${JSON.stringify({
  loginWindowMinutes: 15, loginMaxFails: 3, lockoutMinutes: 15, passwordMinLength: 8, passwordMinClasses: 3, require2faRoles: [],
})}\n`)

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

try {
  const admin = await login('admin@t', 'AdminPass1')
  check('admin 登录 200（无 2FA 时正常签发）', admin.status === 200 && admin.cookie !== undefined && admin.body.totp_required === undefined)
  const twofaKey = deriveKey(getOrCreateSecret(DATA))

  /* 3a. 绑定流程 */
  const emp = await login('member@t', 'MemberPass1')
  check('employee 登录 200', emp.status === 200)
  const setup = await post('/api/me/2fa/setup', {}, emp.cookie)
  const setupBody = await setup.json()
  check('setup 200 返回 base32 与 otpauth 链接', setup.status === 200 && /^[A-Z2-7]+$/.test(setupBody.secret ?? '') && String(setupBody.otpauth ?? '').startsWith('otpauth://totp/Kabage:member'))
  check('otpauth 链接含 issuer 与密钥', setupBody.otpauth.includes('issuer=Kabage') && setupBody.otpauth.includes(`secret=${setupBody.secret}`))
  const badConfirm = await post('/api/me/2fa/confirm', { code: '000000' }, emp.cookie)
  check('confirm 错码 400', badConfirm.status === 400 && String((await badConfirm.json()).error ?? '').includes('验证码错误'))
  const goodCode = codeAt(setupBody.secret, Date.now())
  const confirm = await post('/api/me/2fa/confirm', { code: goodCode }, emp.cookie)
  check('confirm 对码 200', confirm.status === 200)
  check('security.2fa_enabled 留痕', await waitForAudit((e) => e.action === 'security.2fa_enabled' && e.result === 'ok' && e.target === 'member@t') !== undefined)
  const setupAgain = await post('/api/me/2fa/setup', {}, emp.cookie)
  check('已启用再 setup 400', setupAgain.status === 400 && String((await setupAgain.json()).error ?? '').includes('已启用'))
  const meText = await (await get('/me', emp.cookie)).text()
  check('/me 显示已启用状态', meText.includes('已启用') && meText.includes('关闭两步验证'))

  /* 3b. 登录 totp_required 与验证码换 JWT */
  const login1 = await login('member@t', 'MemberPass1')
  check('已启用后登录返回 totp_required 且不发 cookie', login1.status === 200 && login1.body.totp_required === true && login1.cookie === undefined)
  const totpBad = await post('/api/auth/totp', { account: 'member@t', code: '000000' })
  check('错 code 401', totpBad.status === 401)
  check('auth.totp_fail 留痕', await waitForAudit((e) => e.action === 'auth.totp_fail' && e.detail?.reason === 'bad_code') !== undefined)
  const totpOk = await post('/api/auth/totp', { account: 'member@t', code: codeAt(setupBody.secret, Date.now()) })
  check('对 code 登录成功 + cookie', totpOk.status === 200 && totpOk.headers.getSetCookie()[0] !== undefined)
  check('login_success detail 带 totp:true', await waitForAudit((e) => e.action === 'auth.login_success' && e.detail?.totp === true && e.target === 'member@t') !== undefined)
  check('未启用账号走 totp 端点被拒', (await post('/api/auth/totp', { account: 'admin@t', code: '123456' })).status === 401)

  /* 3c. disable 恢复单因子 */
  const badDisable = await post('/api/me/2fa/disable', { password: 'WrongPass1' }, totpOk.headers.getSetCookie()[0]?.split(';')[0])
  check('disable 错密码 400', badDisable.status === 400 && String((await badDisable.json()).error ?? '').includes('当前密码不正确'))
  const okDisable = await post('/api/me/2fa/disable', { password: 'MemberPass1' }, totpOk.headers.getSetCookie()[0]?.split(';')[0])
  check('disable 对密码 200', okDisable.status === 200)
  check('security.2fa_disabled 留痕', await waitForAudit((e) => e.action === 'security.2fa_disabled' && e.result === 'ok') !== undefined)
  const login2 = await login('member@t', 'MemberPass1')
  check('关闭后登录恢复单因子（直接发 cookie）', login2.status === 200 && login2.cookie !== undefined && login2.body.totp_required === undefined)

  /* 3d. admin reset 救援 */
  const setup2 = await post('/api/me/2fa/setup', {}, login2.cookie)
  const secret2 = (await setup2.json()).secret
  await post('/api/me/2fa/confirm', { code: codeAt(secret2, Date.now()) }, login2.cookie)
  const membersHtml = await (await get('/console/members', admin.cookie)).text()
  check('成员页含重置2FA按钮（启用中的账号）', membersHtml.includes('resetTwofa') && membersHtml.includes('重置2FA'))
  const resetByOther = await post('/console/api/member/2fa/reset', { account: 'ghost@t' }, admin.cookie)
  check('reset 未知账号 404', resetByOther.status === 404)
  const resetOk = await post('/console/api/member/2fa/reset', { account: 'member@t' }, admin.cookie)
  check('admin reset 200', resetOk.status === 200)
  check('security.2fa_reset 留痕', await waitForAudit((e) => e.action === 'security.2fa_reset' && e.target === 'member@t') !== undefined)
  const login3 = await login('member@t', 'MemberPass1')
  check('reset 后登录恢复单因子（救援成立）', login3.status === 200 && login3.cookie !== undefined && login3.body.totp_required === undefined)

  /* 3e. 软强制 needs_2fa_enrollment */
  saveSecurityConfig(DATA, { require2faRoles: ['employee'] })
  const login4 = await login('member@t', 'MemberPass1')
  check('软强制角色未绑定：登录成功但响应附 needs_2fa_enrollment', login4.status === 200 && login4.cookie !== undefined && login4.body.needs_2fa_enrollment === true)
  const meBanner = await (await get('/me', login4.cookie)).text()
  check('/me 顶部出现绑定提醒横幅', meBanner.includes('管理员已要求') && meBanner.includes('两步验证'))
  const adminLogin2 = await login('admin@t', 'AdminPass1')
  check('非清单角色（admin）不带 enrollment 标记', adminLogin2.body.needs_2fa_enrollment === undefined)
  saveSecurityConfig(DATA, { require2faRoles: [] })

  /* 3f. 限流同桶（错 3 次后对码也 429；放最后，锁定不影响其他断言）+ P1-1 损坏探针 */
  console.log('# 限流同桶与损坏密文 fail-closed')
  const setup3 = await post('/api/me/2fa/setup', {}, login4.cookie)
  const secret3 = (await setup3.json()).secret
  await post('/api/me/2fa/confirm', { code: codeAt(secret3, Date.now()) }, login4.cookie)
  // P1-1：损坏 encSecret → 正确密码登录 fail-closed（500 + security.twofa_broken，不发 cookie）
  const twofaPath = join(DATA, 'twofa.json')
  const twofaBackup = readFileSync(twofaPath, 'utf8')
  const twofaStore = JSON.parse(twofaBackup)
  twofaStore['member@t'].encSecret = 'enc:v1:broken:broken:broken'
  writeFileSync(twofaPath, `${JSON.stringify(twofaStore, null, 2)}\n`)
  const brokenConfirm = await post('/api/me/2fa/confirm', { code: '123456' }, login4.cookie)
  check('confirm 对损坏记录：中文救援文案', brokenConfirm.status === 400 && String((await brokenConfirm.json()).error ?? '').includes('请联系管理员重置'))
  const brokenLogin = await login('member@t', 'MemberPass1')
  check('损坏密文：正确密码登录被拒 500（fail-closed）', brokenLogin.status === 500 && String(brokenLogin.body.error ?? '').includes('两步验证配置损坏'))
  check('损坏密文：不签发 cookie', brokenLogin.cookie === undefined)
  check('security.twofa_broken 留痕（actor=尝试登录的账号）', await waitForAudit((e) => e.action === 'security.twofa_broken' && e.result === 'fail' && e.target === 'member@t') !== undefined)
  writeFileSync(twofaPath, twofaBackup)
  for (let i = 0; i < 3; i++) {
    const bad = await post('/api/auth/totp', { account: 'member@t', code: '000000' })
    check(`TOTP 错码 #${i + 1} 401`, bad.status === 401)
  }
  const locked = await post('/api/auth/totp', { account: 'member@t', code: codeAt(secret3, Date.now()) })
  check('第 4 次即使对码也 429（同桶限流）', locked.status === 429)
  check('login_rate_limited 留痕（totp 路径）', await waitForAudit((e) => e.action === 'auth.login_rate_limited' && e.actor?.account === 'member@t') !== undefined)
} finally {
  gateway.close()
  gateway.closeAllConnections?.()
  rmSync(DATA, { recursive: true, force: true })
}

console.log(`\n通过 ${passed}，失败 ${failed}`)
process.exit(failed > 0 ? 1 : 0)
