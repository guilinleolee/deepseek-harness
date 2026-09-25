/**
 * 安全与审计冒烟测试（零测试框架，node 直接运行）。
 *
 * 在系统临时目录验证：密码策略正反例、登录速率限制全路径
 * （连败→锁定→解锁恢复→成功清零）、auditAppend→auditQuery 各过滤条件、
 * security.json 缺省生成与改写。不触碰生产 data/ 与 8460/9400 端口。
 *
 * 运行：node test/security-audit-smoke.mjs
 */
import { existsSync, mkdtempSync, readFileSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'

import { auditAppend, auditQuery, initAudit } from '../audit.mjs'
import { checkPasswordPolicy, createLoginRateGuard, generatePassword, loadSecurityConfig, saveSecurityConfig } from '../security.mjs'

const sleep = (ms) => new Promise((r) => setTimeout(r, ms))

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

rmSync(DATA, { recursive: true, force: true })
console.log(`\n通过 ${passed}，失败 ${failed}`)
if (failed > 0) process.exit(1)
