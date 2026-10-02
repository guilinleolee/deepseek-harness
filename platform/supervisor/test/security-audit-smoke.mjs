/**
 * 安全与审计冒烟测试（零测试框架，node 直接运行）。
 *
 * 在系统临时目录验证：密码策略正反例、登录速率限制全路径
 * （连败→锁定→解锁恢复→成功清零）、限流计数桶文件持久化（重建 guard =
 * 模拟 daemon 重启）、auditAppend→auditQuery 各过滤条件、审计按大小轮转
 * （归档/保留/跨档查询）、security.json 缺省生成与改写（含审计轮转参数）、
 * addAccount/setPassword 存储函数内强制密码策略。不触碰生产 data/ 与
 * 8460/9400 端口。
 *
 * 运行：node test/security-audit-smoke.mjs
 */
import { existsSync, mkdtempSync, readdirSync, readFileSync, rmSync, statSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'

import { auditAppend, auditQuery, initAudit } from '../audit.mjs'
import { addAccount, loadAccounts, setPassword, verifyPassword } from '../gateway.mjs'
import { checkPasswordPolicy, createLoginRateGuard, generatePassword, loadSecurityConfig, saveSecurityConfig } from '../security.mjs'

const sleep = (ms) => new Promise((r) => setTimeout(r, ms))
const throws = (fn) => {
  try {
    fn()
    return false
  } catch {
    return true
  }
}

const DATA = mkdtempSync(join(tmpdir(), 'lyz-audit-smoke-'))
let passed = 0
let failed = 0
const check = (name, cond) => {
  if (cond === true) { passed += 1; console.log(`  ok  ${name}`) } else { failed += 1; console.error(`FAIL  ${name}`) }
}

initAudit(DATA)

/* ── 1. 密码策略 ─────────────────────────────────────────────────────────── */
console.log('# 密码策略')
check('正例：8 位三类字符 Abcdef12', checkPasswordPolicy('Abcdef12', 'u@x').ok === true)
check('正例：更长且含符号 Passw0rd!', checkPasswordPolicy('Passw0rd!', 'u@x').ok === true)
check('正例：11 位三类字符 LongEnough1', checkPasswordPolicy('LongEnough1', 'u@x').ok === true)
check('正例：调低参数后 6 位两类通过', checkPasswordPolicy('abcd12', 'u@x', { passwordMinLength: 6, passwordMinClasses: 2 }).ok === true)
check('反例：过短 Ab1', checkPasswordPolicy('Ab1', 'u@x').ok === false)
check('反例：缺数字 abcdefgh', checkPasswordPolicy('abcdefgh', 'u@x').ok === false)
check('反例：只有两类 Abcdefgh', checkPasswordPolicy('Abcdefgh', 'u@x').ok === false)
check('反例：与账号名相同（大小写不敏感）', checkPasswordPolicy('Abcd1234', 'abcd1234').ok === false)
check('反例：空密码', checkPasswordPolicy('', 'u@x').ok === false)
check('反例文案为中文', String(checkPasswordPolicy('Ab1', 'u@x').message).includes('密码'))
const genOk = Array.from({ length: 20 }, () => checkPasswordPolicy(generatePassword(), 'u@x').ok).every(Boolean)
check('generatePassword 连续 20 个全部满足策略', genOk)

/* ── 2. 登录速率限制：连败→锁定→解锁恢复→成功清零 ────────────────────────── */
console.log('# 登录速率限制')
const guard = createLoginRateGuard(() => ({ windowMs: 400, maxFails: 3, lockoutMs: 600 }))
guard.fail('a@x', '1.2.3.4')
guard.fail('a@x', '1.2.3.4')
check('未达阈值仍放行', guard.check('a@x', '1.2.3.4').allowed === true)
guard.fail('a@x', '1.2.3.4')
const locked = guard.check('a@x', '1.2.3.4')
check('达阈值锁定', locked.allowed === false)
check('retryAfterMinutes ≥ 1', Number.isInteger(locked.retryAfterMinutes) && locked.retryAfterMinutes >= 1)
check('同账号不同 IP 不受影响', guard.check('a@x', '5.6.7.8').allowed === true)
check('同 IP 不同账号不受影响', guard.check('b@x', '1.2.3.4').allowed === true)
guard.fail('a@x', '1.2.3.4')
check('锁定中不续期（仍返回允许倒计时）', guard.check('a@x', '1.2.3.4').allowed === false)
await sleep(700)
check('锁定期满恢复放行', guard.check('a@x', '1.2.3.4').allowed === true)
guard.fail('a@x', '1.2.3.4')
check('解锁后重新计数（1 次失败仍放行）', guard.check('a@x', '1.2.3.4').allowed === true)
const guard2 = createLoginRateGuard(() => ({ windowMs: 60_000, maxFails: 3, lockoutMs: 60_000 }))
guard2.fail('c@x', '9.9.9.9')
guard2.fail('c@x', '9.9.9.9')
guard2.success('c@x', '9.9.9.9')
check('成功登录清零（再 2 次失败仍放行）', guard2.check('c@x', '9.9.9.9').allowed === true)

/* ── 3. 审计追加与查询 ───────────────────────────────────────────────────── */
console.log('# 审计追加与查询')
await auditAppend({ actor: { account: 'admin@x', role: 'admin', ip: '1.1.1.1' }, action: 'auth.login_success', target: 'admin@x', result: 'ok' })
await auditAppend({ actor: { account: 'a@x', role: 'employee', ip: '2.2.2.2' }, action: 'auth.login_fail', result: 'fail', detail: { reason: 'bad_credentials' } })
await auditAppend({ actor: { account: 'A@X', role: 'employee', ip: '2.2.2.2' }, action: 'auth.login_rate_limited', result: 'deny', detail: { retryAfterMinutes: 15 } })
await auditAppend({ actor: { account: 'boss@x', role: 'admin', ip: '3.3.3.3' }, action: 'member.create', target: 'a@x', result: 'ok', detail: { role: 'employee' } })
await auditAppend({ actor: { account: 'boss@x', role: 'admin', ip: '3.3.3.3' }, action: 'security.config_change', result: 'ok', detail: { old: { x: 1 }, new: { x: 2 } } })
const all = auditQuery({})
check('默认读出全部 5 条', all.length === 5)
check('倒序（最新在前）', all[0].action === 'security.config_change' && all[4].action === 'auth.login_success')
check('事件带可解析 ts', typeof all[0].ts === 'string' && !Number.isNaN(Date.parse(all[0].ts)))
check('actionPrefix=auth 命中 3 条', auditQuery({ actionPrefix: 'auth' }).length === 3)
check('actionPrefix=auth.login_f 精确前缀命中 1 条', auditQuery({ actionPrefix: 'auth.login_f' }).length === 1)
check('actor 关键词大小写不敏感命中 2 条', auditQuery({ actor: 'a@x' }).length === 2)
check('result=deny 命中 1 条', auditQuery({ result: 'deny' }).length === 1)
check('组合过滤（前缀+账号+结果）命中 1 条', auditQuery({ actionPrefix: 'auth', actor: 'a@x', result: 'fail' }).length === 1)
check('limit 截断保留最新 2 条', auditQuery({ limit: 2 }).map((e) => e.action).join(',') === 'security.config_change,member.create')
const lines = readFileSync(join(DATA, 'audit.jsonl'), 'utf8').trimEnd().split('\n')
check('JSONL 逐行可解析', lines.every((l) => { try { JSON.parse(l); return true } catch { return false } }))
check('事件字段齐全（ts/actor/action/result）', lines.map((l) => JSON.parse(l)).every((e) => typeof e.ts === 'string' && 'actor' in e && typeof e.action === 'string' && typeof e.result === 'string'))
check('文件恰好一个换行结尾', readFileSync(join(DATA, 'audit.jsonl'), 'utf8').endsWith('}\n') && !readFileSync(join(DATA, 'audit.jsonl'), 'utf8').endsWith('\n\n'))

/* ── 3b. actor 全等匹配（exact，P1-2：子串账号不混入他人记录）───────────── */
console.log('# actor exact 精确匹配')
await auditAppend({ actor: { account: 'zz@x', role: 'employee', ip: '2.2.2.2' }, action: 'auth.login_success', target: 'zz@x', result: 'ok' })
await auditAppend({ actor: { account: 'zzz@x', role: 'employee', ip: '2.2.2.2' }, action: 'auth.login_success', target: 'zzz@x', result: 'ok' })
check('子串匹配：zz@x 命中 2 条（含 zzz@x）', auditQuery({ actor: 'zz@x' }).length === 2)
const exactZz = auditQuery({ actor: 'zz@x', exact: true })
check('exact 全等：zz@x 只命中 1 条且账号全等', exactZz.length === 1 && exactZz[0].actor.account === 'zz@x')
check('exact 大小写不敏感全等', auditQuery({ actor: 'ZZ@X', exact: true }).length === 1)
check('exact 不误伤长账号自身查询', auditQuery({ actor: 'zzz@x', exact: true }).every((e) => e.actor.account === 'zzz@x') && auditQuery({ actor: 'zzz@x', exact: true }).length === 1)

/* ── 4. security.json 缺省生成与改写 ─────────────────────────────────────── */
console.log('# 安全配置')
const def = loadSecurityConfig(DATA)
check('缺省文件自动生成', existsSync(join(DATA, 'security.json')))
check('缺省参数值（15/10/15/8/3）',
  def.loginWindowMinutes === 15 && def.loginMaxFails === 10 && def.lockoutMinutes === 15
  && def.passwordMinLength === 8 && def.passwordMinClasses === 3)
check('缺省审计轮转参数（16MB/4 份）', def.auditRotateBytes === 16_777_216 && def.auditKeepArchives === 4)
saveSecurityConfig(DATA, { loginMaxFails: 4, passwordMinLength: 10 })
const changed = loadSecurityConfig(DATA)
check('部分键改写生效且未动其他键', changed.loginMaxFails === 4 && changed.passwordMinLength === 10 && changed.loginWindowMinutes === 15)
let threw = false
try { saveSecurityConfig(DATA, { loginMaxFails: 0 }) } catch { threw = true }
check('越界参数被拒', threw)
check('被拒参数不落盘', loadSecurityConfig(DATA).loginMaxFails === 4)
threw = false
try { saveSecurityConfig(DATA, { nonsense: 1 }) } catch { threw = true }
check('未知参数被拒', threw)
const DATA2 = mkdtempSync(join(tmpdir(), 'lyz-audit-smoke2-'))
let freshOk = false
try {
  freshOk = loadSecurityConfig(DATA2).lockoutMinutes === 15 && existsSync(join(DATA2, 'security.json'))
} finally {
  rmSync(DATA2, { recursive: true, force: true })
}
check('全新目录缺省生成', freshOk)

/* ── 5. 限流计数桶持久化（重建 guard = 模拟 daemon 重启）─────────────────── */
console.log('# 限流持久化')
const DATA3 = mkdtempSync(join(tmpdir(), 'lyz-audit-smoke3-'))
const limits = () => ({ windowMs: 60_000, maxFails: 3, lockoutMs: 60_000 })
const guardP = createLoginRateGuard(limits, { dataDir: DATA3, file: 'rate-limits.json' })
guardP.fail('p@x', '3.3.3.3')
guardP.fail('p@x', '3.3.3.3')
check('失败即落盘 rate-limits.json', existsSync(join(DATA3, 'rate-limits.json')))
const guardReborn = createLoginRateGuard(limits, { dataDir: DATA3, file: 'rate-limits.json' })
check('重建后失败计数存活（2 次仍放行）', guardReborn.check('p@x', '3.3.3.3').allowed === true)
guardReborn.fail('p@x', '3.3.3.3')
check('重建后第 3 次失败触发锁定', guardReborn.check('p@x', '3.3.3.3').allowed === false)
const guardReborn2 = createLoginRateGuard(limits, { dataDir: DATA3, file: 'rate-limits.json' })
check('锁定期内重建仍锁定（重启绕不过锁定）', guardReborn2.check('p@x', '3.3.3.3').allowed === false)
check('锁定只影响该账号+IP', guardReborn2.check('q@x', '3.3.3.3').allowed === true)
guardReborn2.success('p@x', '3.3.3.3')
const guardReborn3 = createLoginRateGuard(limits, { dataDir: DATA3, file: 'rate-limits.json' })
check('成功清零持久化（重建后放行）', guardReborn3.check('p@x', '3.3.3.3').allowed === true)
const persisted = JSON.parse(readFileSync(join(DATA3, 'rate-limits.json'), 'utf8'))
check('清零后文件不残留死条目', Object.keys(persisted.buckets ?? {}).length === 0)
rmSync(DATA3, { recursive: true, force: true })

/* ── 5b. 账号级全局桶（跨 IP 分布式撞库封口）────────────────────────────── */
console.log('# 账号级限流桶')
const DATA5 = mkdtempSync(join(tmpdir(), 'lyz-audit-smoke5-'))
const limitsG = () => ({ windowMs: 60_000, maxFails: 3, accountMaxFails: 5, lockoutMs: 60_000 })
const guardG = createLoginRateGuard(limitsG, { dataDir: DATA5, file: 'rl-g.json' })
for (let i = 1; i <= 4; i++) guardG.fail('g@x', `10.0.0.${i}`)
check('4 个 IP 各失败 1 次：各 IP 桶均放行', [1, 2, 3, 4].every((i) => guardG.check('g@x', `10.0.0.${i}`).allowed === true))
guardG.fail('g@x', '10.0.0.5')
check('跨 IP 累计达 accountMaxFails 即全局锁定', guardG.check('g@x', '10.0.0.1').allowed === false)
check('全局锁定不影响其他账号', guardG.check('h@x', '10.0.0.1').allowed === true)
const guardG2 = createLoginRateGuard(limitsG, { dataDir: DATA5, file: 'rl-g.json' })
check('账号级锁定持久化（重建后全新 IP 也拒）', guardG2.check('g@x', '10.0.0.9').allowed === false)
guardG2.success('g@x', '10.0.0.1')
check('成功清零含全局桶（重建后放行）', guardG2.check('g@x', '10.0.0.1').allowed === true)
guardG2.fail('', '10.0.0.1')
check('空账号桶（注册限流）不设全局桶', guardG2.check('', '10.0.0.1').allowed === true)
rmSync(DATA5, { recursive: true, force: true })

/* ── 6. 审计按大小轮转（归档 + 保留 + 跨档查询）──────────────────────────── */
console.log('# 审计轮转')
const DATA_ROT = mkdtempSync(join(tmpdir(), 'lyz-audit-rotate-'))
writeFileSync(join(DATA_ROT, 'security.json'), `${JSON.stringify({
  loginWindowMinutes: 15, loginMaxFails: 10, lockoutMinutes: 15,
  passwordMinLength: 8, passwordMinClasses: 3,
  auditRotateBytes: 1024, auditKeepArchives: 2, require2faRoles: [],
}, null, 2)}\n`)
initAudit(DATA_ROT)
for (let i = 0; i < 40; i++) {
  await auditAppend({ actor: { account: `u${String(i).padStart(2, '0')}@x`, role: 'employee', ip: '1.1.1.1' }, action: `t.ev${String(i).padStart(2, '0')}`, result: 'ok' })
}
const rotateFiles = readdirSync(DATA_ROT).filter((n) => /^audit-\d{8}-\d{6}-\d{3}\.jsonl$/.test(n)).sort()
check('按阈值轮转且只保留 auditKeepArchives 份归档', rotateFiles.length === 2)
check('active 文件重新从小计数', statSync(join(DATA_ROT, 'audit.jsonl')).size < 1100)
const total = auditQuery({ limit: 10_000 })
check('查询跨 active+归档且被清理档不再可见（<40）', total.length < 40 && total.length >= 3)
check('跨文件倒序（最新事件在最前）', total[0]?.action === 't.ev39')
check('最旧归档已清理（ev00 查不到）', auditQuery({ actor: 'u00@x', exact: true }).length === 0)
check('归档内事件按 actor 精确命中', auditQuery({ actor: 'u39@x', exact: true }).length === 1)
check('跨档组合过滤（前缀+limit 截断保最新）', auditQuery({ actionPrefix: 't.ev', limit: 2 }).map((e) => e.action).join(',') === 't.ev39,t.ev38')
rmSync(DATA_ROT, { recursive: true, force: true })
initAudit(DATA)

/* ── 7. 存储函数内强制密码策略（CLI 无绕过面）────────────────────────────── */
console.log('# 建号/改密策略收口')
const DATA4 = mkdtempSync(join(tmpdir(), 'lyz-audit-smoke4-'))
check('addAccount 弱密码被拒', throws(() => addAccount(DATA4, { account: 'weak@x', instanceId: 'e01', role: 'employee', password: 'weak' })))
check('被拒建号不落盘', loadAccounts(DATA4).accounts.length === 0)
const created = addAccount(DATA4, { account: 'ok@x', instanceId: 'e01', role: 'employee', password: 'GoodPass123' })
check('addAccount 合规密码创建成功', created.account === 'ok@x')
const policyThrows = throws(() => setPassword(DATA4, 'ok@x', 'weak'))
const keepOk = verifyPassword(loadAccounts(DATA4).accounts.find((a) => a.account === 'ok@x'), 'GoodPass123')
check('setPassword 弱密码被拒且旧密码保留', policyThrows && keepOk)
setPassword(DATA4, 'ok@x', 'NewPass1234')
const rec = loadAccounts(DATA4).accounts.find((a) => a.account === 'ok@x')
check('setPassword 合规密码生效且旧密失效', verifyPassword(rec, 'NewPass1234') && !verifyPassword(rec, 'GoodPass123'))
rmSync(DATA4, { recursive: true, force: true })

rmSync(DATA, { recursive: true, force: true })
console.log(`\n通过 ${passed}，失败 ${failed}`)
if (failed > 0) process.exit(1)
