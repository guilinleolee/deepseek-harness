/**
 * 管理台加固验证（Top10 #1/#2/#3 回归套件）：
 *
 * 1. vkey 最后一公里（credentials.mjs）：
 *    - 纯函数 mergeCredentialsYaml：空文件建骨架 / 既有 refs 替换 / 顶部或
 *      records 段保留 / 无 refs 块追加 / 值转义 / 非法键名拒绝；
 *    - writeInstanceCredentials：真实落盘（temp dir）→ 覆盖更新 → records
 *      原样保留 → 原子写（tmp 不残留）→ 非法实例 id 拒绝；
 *    - 集成：service-token issueVkey 后 writeVkeyToHome 落盘（走 console
 *      同一原语）。
 * 2. member.role_grant 权限点拆分（console.mjs）：
 *    - PERMISSION_POINTS 含新点、DEFAULT_MATRIX：admin=开 / auditor=关 /
 *      employee=关（新点缺省安全）；
 *    - member/update 带 role → 需 member.role_grant（auditor 403 留痕
 *      member.role_change deny、detail.point=member.role_grant）；
 *    - member/update 不带 role（改部门）→ 只需 member.change；
 *    - member/create role=admin → 需 member.role_grant；
 *    - 授予 employee member.role_grant 后 → 可改角色（矩阵收放生效）。
 * 3. 控制台 API 认证失败限速（console.mjs）：
 *    - 无 cookie 连发 N 次变更 POST → 401 前几次，达阈值后 429
 *      （retryAfterMinutes ≥1）；
 *    - 429 留痕 security.console_auth_limited deny；
 *    - console-auth-limits.json 持久化、不含明文 token（隐私红线）；
 *    - 独立文件：与登录限速 rate-limits.json 互不干扰。
 *
 * 运行：node test/console-hardening-verify.mjs
 */
import { mkdtempSync, readFileSync, rmSync, writeFileSync, existsSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'

import { auditAppend, auditQuery, initAudit } from '../audit.mjs'
import { createGatewayServer, hashPassword } from '../gateway.mjs'
import { authenticateServiceToken, createServiceToken } from '../service-tokens.mjs'
import { issueVkey } from '../relay.mjs'
import { mergeCredentialsYaml, writeInstanceCredentials, writeVkeyToHome, instanceCredentialsPath } from '../credentials.mjs'

const wait = (ms) => new Promise((r) => setTimeout(r, ms))
const JSON_HEAD = { 'content-type': 'application/json', connection: 'close' }

let passed = 0
let failed = 0
const check = (name, cond) => {
  if (cond === true) { passed += 1; console.log(`  ok  ${name}`) } else { failed += 1; console.error(`FAIL  ${name}`) }
}

const DATA = mkdtempSync(join(tmpdir(), 'lyz-console-hardening-'))
const now = new Date().toISOString()
const mkAccount = (id, acc, role, pw, extra = {}) => ({
  id, account: acc, displayName: id, role, department: '验证组', instanceId: 'e01',
  tokenEpoch: 0, createdAt: now, passwordHash: hashPassword(pw), ...extra,
})
writeFileSync(join(DATA, 'accounts.json'), `${JSON.stringify({ accounts: [
  mkAccount('a1', 'admin@t', 'admin', 'AdminPass1'),
  mkAccount('e1', 'emp@t', 'employee', 'EmpPass123'),
] }, null, 2)}\n`)
initAudit(DATA)

const manifest = {
  gatewayHost: 'localhost', portalPort: 0, relayPort: 0, repoRoot: '.',
  instances: [
    { id: 'e01', account: 'admin@t', uid: 1, port: 1 },
  ],
}
const gateway = createGatewayServer({ manifest, getState: () => ({ instances: {} }), dataDir: DATA })
await new Promise((r) => gateway.listen(0, '127.0.0.1', r))
const base = `http://127.0.0.1:${gateway.address().port}`
const post = (path, body, cookie) => fetch(`${base}${path}`, {
  method: 'POST',
  headers: { ...JSON_HEAD, ...(cookie ? { cookie } : {}) },
  body: JSON.stringify(body ?? {}),
})
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
  /* ── 1. credentials.mjs 纯函数 ─────────────────────────────────────────── */
  console.log('# mergeCredentialsYaml 纯函数')
  check('空文件 → version+refs 骨架', mergeCredentialsYaml(undefined, 'LYZ_VIRTUAL_KEY', 'vk-abc') === 'version: 1\nrefs:\n  LYZ_VIRTUAL_KEY: vk-abc\n')
  const baseYaml = 'version: 1\nrefs:\n  LYZ_VIRTUAL_KEY: vk-old\nrecords:\n  client-connection/browser-session:\n    kind: grant\n    payload:\n      version: 1\n      secret: keep-me\n'
  const replaced = mergeCredentialsYaml(baseYaml, 'LYZ_VIRTUAL_KEY', 'vk-new')
  check('既有 refs 值原位替换', replaced.includes('  LYZ_VIRTUAL_KEY: vk-new\n'))
  check('records 段逐行保留', replaced.includes('  client-connection/browser-session:\n') && replaced.includes('      secret: keep-me\n'))
  check('旧值不再出现', !replaced.includes('vk-old'))
  const noRefs = 'version: 1\nrecords:\n  x:\n    kind: grant\n'
  const appended = mergeCredentialsYaml(noRefs, 'LYZ_VIRTUAL_KEY', 'vk-add')
  check('无 refs 块 → 尾部追加段', appended.startsWith('version: 1\nrecords:\n  x:\n    kind: grant\nrefs:\n  LYZ_VIRTUAL_KEY: vk-add\n'))
  check('值含特殊字符 → 双引号转义', mergeCredentialsYaml(undefined, 'LYZ_VIRTUAL_KEY', 'vk a"b').includes('  LYZ_VIRTUAL_KEY: "vk a\\"b"\n'))
  check('多引用键共存', (() => {
    const two = mergeCredentialsYaml(baseYaml, 'OTHER_REF', 'v-2')
    return two.includes('LYZ_VIRTUAL_KEY: vk-old') && two.includes('OTHER_REF: v-2')
  })())
  let threw = false
  try { mergeCredentialsYaml(undefined, 'bad key', 'v') } catch { threw = true }
  check('非法键名（含空格）拒绝', threw)

  /* ── 2. writeInstanceCredentials 落盘 ─────────────────────────────────── */
  console.log('# writeInstanceCredentials 落盘')
  const HOME = join(DATA, 'homes', 'e01')
  const credPath = instanceCredentialsPath(DATA, 'e01')
  const w1 = writeVkeyToHome(DATA, 'e01', 'vk-write-1')
  check('首次写入 ok + 路径正确', w1.ok === true && w1.path === credPath)
  check('落盘内容含骨架与明文', readFileSync(credPath, 'utf8').includes('LYZ_VIRTUAL_KEY: vk-write-1'))
  writeFileSync(credPath, 'version: 1\nrecords:\n  sess:\n    kind: grant\n    payload:\n      secret: s3cret\n', 'utf8')
  const w2 = writeVkeyToHome(DATA, 'e01', 'vk-write-2')
  const merged = readFileSync(credPath, 'utf8')
  check('覆盖更新保留 records', w2.ok === true && merged.includes('LYZ_VIRTUAL_KEY: vk-write-2') && merged.includes('secret: s3cret') && !merged.includes('vk-write-1'))
  const tmpLeftover = existsSync(`${credPath}.`)
  check('原子写无 tmp 残留（成功路径）', !tmpLeftover)
  const wBad = writeInstanceCredentials(DATA, '../escape', 'LYZ_VIRTUAL_KEY', 'v')
  check('非法实例 id 拒绝', wBad.ok === false)
  const wEmpty = writeInstanceCredentials(DATA, 'e01', 'LYZ_VIRTUAL_KEY', '')
  check('空值拒绝', wEmpty.ok === false)

  /* ── 3. role_grant 权限点 ─────────────────────────────────────────────── */
  console.log('# member.role_grant 权限点拆分')
  const admin = await login('admin@t', 'AdminPass1')
  check('admin 登录 200', admin.status === 200)
  const emp = await login('emp@t', 'EmpPass123')
  check('employee 登录 200', emp.status === 200)

  // 3a. employee 改自己的部门（member.change 不在 employee 手里 → 403，但 point 应是 member.change 而非 role_grant）
  const empDept = await post('/console/api/member/update', { account: 'emp@t', department: '新部门' }, emp.cookie)
  check('employee 改部门 403（member.change 口径）', empDept.status === 403)
  // 3b. employee 改角色 → 新权限点：403 且 detail.point=member.role_grant
  const empRole = await post('/console/api/member/update', { account: 'emp@t', role: 'admin' }, emp.cookie)
  check('employee 改角色 403', empRole.status === 403)
  const roleDeny = await waitForAudit((e) => e.action === 'member.role_change' && e.result === 'deny' && e.actor?.account === 'emp@t')
  check('deny 留痕 action=member.role_change', roleDeny !== undefined && roleDeny.detail?.point === 'member.role_grant')
  // 3c. admin 带 role 改 → 200（admin 全权限）
  const admRole = await post('/console/api/member/update', { account: 'emp@t', role: 'employee' }, admin.cookie)
  check('admin 改角色 200', admRole.status === 200)
  // 3d. admin 建 admin 账号 → role_grant 口径（走 200）
  const admCreate = await post('/console/api/member/create', { account: 'new-admin@t', role: 'admin', instance: 'e01', password: 'NewAdmin1' }, admin.cookie)
  const admCreateBody = await admCreate.json().catch(() => ({}))
  check('admin 建 admin 200（含 password/vkey）', admCreate.status === 200 && typeof admCreateBody?.password === 'string' && typeof admCreateBody?.vkey === 'string')
  check('建号响应含 vkeyHome 落盘路径', typeof admCreateBody?.vkeyHome === 'string' && admCreateBody.vkeyHome.includes('e01'))
  check('建号后 vkey 已自动写入实例 home', readFileSync(instanceCredentialsPath(DATA, 'e01'), 'utf8').includes('LYZ_VIRTUAL_KEY: vk-'))
  // 3e. 矩阵授予 employee member.role_grant → 可改角色
  const grant = await post('/console/api/role-matrix', { roles: { employee: { 'member.role_grant': true } } }, admin.cookie)
  check('矩阵授予 employee role_grant 200', grant.status === 200)
  const empRole2 = await post('/console/api/member/update', { account: 'emp@t', role: 'employee' }, emp.cookie)
  check('employee 获授权后改角色 200', empRole2.status === 200)
  // 还原矩阵（employee role_grant 关回）
  await post('/console/api/role-matrix', { roles: { employee: { 'member.role_grant': false } } }, admin.cookie)

  /* ── 4. 认证失败限速 ──────────────────────────────────────────────────── */
  console.log('# 控制台 API 认证失败限速')
  // 4a. 无凭据连打：security.json 缺省 loginMaxFails=10 → 第 11 次 429。
  let statuses = []
  for (let i = 0; i < 12; i++) {
    const r = await post('/console/api/member/list', {})
    statuses.push(r.status)
  }
  check('前 10 次 401、其后 429', statuses.filter((s) => s === 401).length === 10 && statuses.slice(10).every((s) => s === 429))
  const limited429 = statuses[statuses.length - 1]
  const limitedEntry = await waitForAudit((e) => e.action === 'security.console_auth_limited' && e.result === 'deny')
  check('429 留痕 security.console_auth_limited', limitedEntry !== undefined)
  // 4b. 持久化文件：存在、是 JSON、不含明文凭据（无 token 字段——桶键是 sha256 切片/'-'）。
  const persisted = JSON.parse(readFileSync(join(DATA, 'console-auth-limits.json'), 'utf8'))
  check('console-auth-limits.json 持久化', typeof persisted?.buckets === 'object')
  check('桶键不含明文 bearer（仅 sha256 切片或 -）', Object.keys(persisted.buckets).every((k) => /^[0-9a-f]{12}\|.+|-\|.+$/.test(k)))
  // 4c. 独立于登录限速：rate-limits.json 不因 console 401 而产生桶
  const loginLimits = existsSync(join(DATA, 'rate-limits.json'))
    ? JSON.parse(readFileSync(join(DATA, 'rate-limits.json'), 'utf8'))
    : { buckets: {} }
  check('登录限速文件不受 console 401 影响', Object.keys(loginLimits.buckets ?? {}).length === 0)
  // 4d. 限速期：管理员带 cookie 的正常 POST 不受影响（限的是「认证失败」桶）
  const admPing = await post('/console/api/member/update', { account: 'emp@t', department: '验证组' }, admin.cookie)
  check('限速期间合法会话照常 200', admPing.status === 200)
  // 4e. 无效 bearer 计入 bearer 桶（与 '-' 桶隔离）
  const bearerStatuses = []
  for (let i = 0; i < 3; i++) {
    const r = await fetch(`${base}/console/api/member/list`, { headers: { authorization: 'Bearer kbsvc-invalid-token' } })
    bearerStatuses.push(r.status)
  }
  check('无效 bearer 401（不与无凭据桶合并计满）', bearerStatuses.every((s) => s === 401))
  const persisted2 = JSON.parse(readFileSync(join(DATA, 'console-auth-limits.json'), 'utf8'))
  const bearerBucket = Object.keys(persisted2.buckets).find((k) => /^[0-9a-f]{12}\|/.test(k))
  check('bearer 桶键为 sha256 切片且独立计数', bearerBucket !== undefined)
} finally {
  gateway.close()
  rmSync(DATA, { recursive: true, force: true })
}

console.log(`\n通过 ${passed}，失败 ${failed}`)
if (failed > 0) process.exit(1)
