/**
 * 邮件通知（阶段 11B）验证：file 模式 .eml 断言 + mock SMTP 命令流 + 触发点。
 *
 * 1. buildMime 纯函数：头齐全、Subject RFC 2047 编码、正文 UTF-8 base64 折行；
 * 2. file 模式：sendMail 落盘 data/outbox/*.eml（每收件人一封，解码断言）；
 * 3. relay 80% 告警：mock 上游打点跨线 → 告警 .eml 恰好一封（alerted 标记
 *    每月一次）+ usage.alerted + notify.quota_warn 审计；
 * 4. smtp 模式：本地 mock SMTP（假应答 220/250/334/354/221）断言命令流
 *    （EHLO 多行应答解析、AUTH LOGIN base64、MAIL/RCPT/DATA/QUIT）与消息体；
 * 5. 账号变更：建号/禁用/重置密码三类通知，重置邮件绝不含新密码原文。
 *
 * 随机端口 + 临时目录；真实外网 SMTP 标注待凭证后真机验证。
 * 运行：node test/notify-verify.mjs
 */
import { spawn } from 'node:child_process'
import { createServer } from 'node:net'
import { existsSync, mkdirSync, mkdtempSync, readFileSync, readdirSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { fileURLToPath } from 'node:url'

import { auditAppend, auditQuery, initAudit } from '../audit.mjs'
import { createGatewayServer, getOrCreateSecret, hashPassword } from '../gateway.mjs'
import { createRelayServer, issueVkey, monthKey } from '../relay.mjs'
import { buildMime, getSmtpPassword, initNotify, loadNotifyConfig, notifyAccountAndAdmins, saveNotifyConfig, sendMail } from '../notify.mjs'

const wait = (ms) => new Promise((r) => setTimeout(r, ms))
const JSON_HEAD = { 'content-type': 'application/json', connection: 'close' }

let passed = 0
let failed = 0
const check = (name, cond) => {
  if (cond === true) { passed += 1; console.log(`  ok  ${name}`) } else { failed += 1; console.error(`FAIL  ${name}`) }
}

// P2-6：未初始化（initNotify 之前）时 notifyAccountAndAdmins 早退不抛。
const early = await notifyAccountAndAdmins('a@x', 's', 't')
check('未初始化时早退不抛（P2-6）', early.sent === false && early.via === 'disabled')

const DATA = mkdtempSync(join(tmpdir(), 'lyz-notify-'))
const now = new Date().toISOString()
initAudit(DATA)
initNotify(DATA, 'notify-test-secret')

/* ── 1. buildMime 纯函数 ─────────────────────────────────────────────────── */
console.log('# buildMime')
const mime = buildMime({ from: 'noreply@kabage.local', to: 'a@x', subject: '配额提醒', text: '正文第一行\n正文第二行', date: new Date(0) })
check('含 From/To/MIME-Version 头', mime.includes('From: noreply@kabage.local') && mime.includes('To: a@x') && mime.includes('MIME-Version: 1.0'))
check('Subject RFC 2047 UTF-8 base64 词编码', mime.includes('Subject: =?UTF-8?B?') === true && /Subject: =\?UTF-8\?B\?[A-Za-z0-9+/=]+\?=/.test(mime))
check('正文 base64 且 76 字符折行', mime.split('\r\n').every((l) => l.length <= 80))
check('CRLF 行尾（无裸 LF）', /(^|[^\r])\n/.test(mime) === false)
check('多收件人 To 逗号分隔', buildMime({ from: 'f@x', to: ['a@x', 'b@x'], subject: 's', text: 't' }).includes('To: a@x, b@x'))
check('正文可解码还原', Buffer.from(mime.split('Content-Transfer-Encoding: base64\r\n\r\n')[1].replace(/\r\n/g, ''), 'base64').toString('utf8') === '正文第一行\n正文第二行')

/* ── 2. 配置保存与 file 模式 ─────────────────────────────────────────────── */
console.log('# 配置与 file 模式')
check('缺省 mode=off', loadNotifyConfig(DATA).mode === 'off')
const saved = saveNotifyConfig(DATA, { mode: 'file', smtp: { host: 'smtp.x', port: 465, secure: true, user: 'u@x', pass: 'Secret1', from: 'noreply@kabage.local' }, adminNotify: ['boss@x'] })
check('保存后 mode=file', saved.mode === 'file')
check('pass 加密落盘（文件不含明文）', !readFileSync(join(DATA, 'notify.json'), 'utf8').includes('Secret1') && saved.smtp.auth.passEnc.startsWith('enc:v1:'))
check('getSmtpPassword 解密还原', getSmtpPassword(DATA) === 'Secret1')
check('未提供 pass 时保留既有密文', saveNotifyConfig(DATA, { mode: 'file' }).smtp.auth.passEnc !== '')
// P2-4 CRLF 头注入防线：from/user/adminNotify 含换行一律拒绝且不落盘
const crlfThrows = (patch) => { try { saveNotifyConfig(DATA, patch); return false } catch { return true } }
check('from 含 CRLF 被拒', crlfThrows({ smtp: { from: 'a@x\r\nBCC: victim@x' } }))
check('smtp.user 含 LF 被拒', crlfThrows({ smtp: { user: 'u@x\nX-INJ: 1' } }))
check('adminNotify 含 CRLF 被拒', crlfThrows({ adminNotify: ['a@x\r\nb@x'] }))
check('CRLF 拒绝后配置未被污染', loadNotifyConfig(DATA).smtp.from === 'noreply@kabage.local' && !readFileSync(join(DATA, 'notify.json'), 'utf8').includes('BCC'))
const r1 = await sendMail({ to: 'member@x', subject: '第一封', text: '你好，通知正文。' })
check('file 模式 sent via file', r1.sent === true && r1.via === 'file')
const r2 = await sendMail({ to: ['member@x', 'boss@x'], subject: '多收件人', text: '两封' })
check('多收件人各落一封', r2.paths.length === 2)
const outbox = join(DATA, 'outbox')
const emls = readdirSync(outbox).filter((f) => f.endsWith('.eml')).sort()
check('outbox 共 3 封 .eml', emls.length === 3)
const first = readFileSync(join(outbox, emls[0]), 'utf8')
check('.eml 结构：To/Subject 编码/正文可解码', first.includes('To: member@x')
  && /Subject: =\?UTF-8\?B\?/.test(first)
  && Buffer.from(first.split('Content-Transfer-Encoding: base64\r\n\r\n')[1].replace(/\r\n/g, ''), 'base64').toString('utf8').includes('通知正文'))
check('.eml 文件名时间戳序号命名', emls.every((f) => /^\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}-\d{3}Z-\d+\.eml$/.test(f)))

/* ── 3. 账号变更通知（建号/禁用/重置密码，网关真实端点）───────────────────── */
console.log('# 账号变更通知')
const mkAccount = (id, acc, role, pw, extra = {}) => ({
  id, account: acc, displayName: id, role, department: '验证组', instanceId: 'e02',
  tokenEpoch: 0, createdAt: now, passwordHash: hashPassword(pw), ...extra,
})
writeFileSync(join(DATA, 'accounts.json'), `${JSON.stringify({ accounts: [
  mkAccount('a1', 'admin@t', 'admin', 'AdminPass1'),
  mkAccount('m1', 'member@t', 'employee', 'MemberPass1', { monthlyPoints: 180 }),
] }, null, 2)}\n`)
const manifest = {
  gatewayHost: 'localhost', portalPort: 0, relayPort: 0, repoRoot: '.',
  instances: [{ id: 'e01', account: 'admin@t', uid: 1, port: 1 }, { id: 'e02', account: 'member@t', uid: 2, port: 2 }],
}
const gateway = createGatewayServer({ manifest, getState: () => ({ instances: {} }), dataDir: DATA })
await new Promise((r) => gateway.listen(0, '127.0.0.1', r))
const base = `http://127.0.0.1:${gateway.address().port}`
const post = async (path, body, cookie) =>
  fetch(`${base}${path}`, { method: 'POST', headers: cookie ? { ...JSON_HEAD, cookie } : JSON_HEAD, body: JSON.stringify(body ?? {}) })
const admin = await post('/api/auth/login', { account: 'admin@t', password: 'AdminPass1' })
const adminCookie = admin.headers.getSetCookie()[0]?.split(';')[0]
const countEmls = (subjectPart) => readdirSync(outbox).filter((f) => {
  try { return Buffer.from(readFileSync(join(outbox, f), 'utf8').match(/Subject: =\?UTF-8\?B\?(.+?)\?=/)?.[1] ?? '', 'base64').toString('utf8').includes(subjectPart) } catch { return false }
}).length
const created = await post('/console/api/member/create', { account: 'newbie@t', instance: 'e02', role: 'employee', password: 'NewbiePass1' }, adminCookie)
check('建号 200', created.status === 200)
await wait(80)
check('建号通知落盘（不含密码原文）', (() => {
  const files = readdirSync(outbox).filter((f) => { const c = readFileSync(join(outbox, f), 'utf8'); return c.includes(`To: newbie@t`) })
  const body = Buffer.from(files.at(-1) !== undefined ? readFileSync(join(outbox, files.at(-1)), 'utf8').split('Content-Transfer-Encoding: base64\r\n\r\n')[1].replace(/\r\n/g, '') : '', 'base64').toString('utf8')
  return files.length === 1 && body.includes('已创建') && !body.includes('NewbiePass1')
})())
const disabled = await post('/console/api/member/disable', { account: 'newbie@t' }, adminCookie)
check('禁用 200', disabled.status === 200)
await wait(80)
check('禁用通知落盘', countEmls('已被禁用') === 1)
const reset = await post('/console/api/member/reset-password', { account: 'newbie@t' }, adminCookie)
const resetBody = await reset.json()
check('重置密码 200', reset.status === 200 && typeof resetBody.password === 'string')
await wait(80)
check('重置通知落盘且绝不含新密码原文', countEmls('密码已被重置') === 1 && !readFileSync(join(outbox, readdirSync(outbox).at(-1)), 'utf8').includes(resetBody.password) && !(() => {
  const raw = readFileSync(join(outbox, readdirSync(outbox).at(-1)), 'utf8')
  return Buffer.from(raw.split('Content-Transfer-Encoding: base64\r\n\r\n')[1].replace(/\r\n/g, ''), 'base64').toString('utf8').includes(resetBody.password)
})())

/* ── 4. relay 80% 配额告警（每账号每月一次）──────────────────────────────── */
console.log('# relay 80% 配额告警')
const mock = spawn(process.execPath, [fileURLToPath(new URL('./mock-upstream.mjs', import.meta.url))], { stdio: 'ignore' })
try {
  let mockUp = false
  for (let i = 0; i < 50 && !mockUp; i++) {
    mockUp = await new Promise((resolveProbe) => {
      fetch('http://127.0.0.1:9410/v1/chat/completions', { method: 'POST', headers: JSON_HEAD, body: '{}' })
        .then((res) => { res.arrayBuffer().catch(() => {}); resolveProbe(res.status === 200) })
        .catch(() => resolveProbe(false))
    })
    if (!mockUp) await wait(100)
  }
  check('mock 上游就绪', mockUp)
  writeFileSync(join(DATA, 'upstreams.json'), `${JSON.stringify({ upstreams: [
    { name: 'mock', baseURL: 'http://127.0.0.1:9410', models: ['test-model'], apiKey: 'sk-x', revoked: false, apiFormat: 'openai', createdAt: now },
  ] }, null, 2)}\n`)
  const relay = createRelayServer({ dataDir: DATA, authSecret: getOrCreateSecret(DATA) })
  await new Promise((r) => relay.listen(0, '127.0.0.1', r))
  const relayPort = relay.address().port
  // member@t monthlyPoints=180；一次请求实结 160 点 ≥ 144（80%）。
  const vkey = issueVkey(DATA, { account: 'member@t', instanceId: 'e02', models: ['test-model'] }).token
  const chat = (tokens) => fetch(`http://127.0.0.1:${relayPort}/v1/chat/completions`, {
    method: 'POST', headers: { ...JSON_HEAD, authorization: `Bearer ${vkey}` },
    body: JSON.stringify({ model: 'test-model', messages: [{ role: 'user', content: 'hi' }], max_tokens: tokens }),
  })
  const beforeWarn = countEmls('配额即将用尽')
  const res1 = await chat(500)
  check('relay 请求 200（160 点，跨 80% 线）', res1.status === 200)
  await res1.arrayBuffer()
  await wait(120)
  // notifyAdmin=['boss@x']：告警 = 本人一封 + 抄送一封，共 2 封。
  const warnCount1 = countEmls('配额即将用尽') - beforeWarn
  check('跨线触发告警恰 2 封（本人 + adminNotify 抄送）', warnCount1 === 2)
  const warnFileByTo = (recipient) => readdirSync(outbox).some((f) => {
    const raw = readFileSync(join(outbox, f), 'utf8')
    const subject = Buffer.from(raw.match(/Subject: =\?UTF-8\?B\?(.+?)\?=/)?.[1] ?? '', 'base64').toString('utf8')
    return subject.includes('配额即将用尽') && raw.includes(`To: ${recipient}`)
  })
  check('收件人=本人与抄送管理员各一封', warnFileByTo('member@t') && warnFileByTo('boss@x'))
  const usageEntry = JSON.parse(readFileSync(join(DATA, 'usage.json'), 'utf8')).months[monthKey()]['member@t']
  check('usage 记录 alerted 标记', usageEntry.alerted === true)
  check('notify.quota_warn 审计留痕', await (async () => {
    const deadline = Date.now() + 4000
    while (Date.now() < deadline) {
      const e = auditQuery({ actionPrefix: 'notify.quota_warn', limit: 100 }).find((x) => x.target === 'member@t')
      if (e !== undefined) return e.detail?.used === 160 && e.detail?.limit === 180 && e.detail?.unit === '点数'
      await wait(40)
    }
    return false
  })())
  const beforeWarn2 = countEmls('配额即将用尽')
  const res2 = await chat(500)
  check('第二笔请求 200', res2.status === 200)
  await res2.arrayBuffer()
  await wait(120)
  check('同月不再重复告警（每账号每月一次）', countEmls('配额即将用尽') - beforeWarn2 === 0)
  relay.close()
  relay.closeAllConnections?.()
} finally {
  mock.kill()
}

/* ── 5. smtp 模式（本地 mock SMTP，命令流断言）───────────────────────────── */
console.log('# smtp 模式（mock SMTP）')
const commands = []
const rcptTo = []
const dataBuf = []
let authUser = ''
let authPass = ''
let dataPayload = ''
let authStage = 0
let inData = false
let lineBuf = ''
const smtpMock = createServer((socket) => {
  socket.write('220 mock.local ESMTP\r\n')
  socket.on('data', (chunk) => {
    lineBuf += chunk.toString('utf8')
    for (;;) {
      const idx = lineBuf.indexOf('\r\n')
      if (idx === -1) return
      const line = lineBuf.slice(0, idx)
      lineBuf = lineBuf.slice(idx + 2)
      if (inData) {
        if (line === '.') { inData = false; dataPayload = dataBuf.join('\r\n'); socket.write('250 queued\r\n') } else dataBuf.push(line)
        continue
      }
      commands.push(line)
      if (/^EHLO/i.test(line)) { socket.write('250-mock.local greets\r\n250-SIZE 10485760\r\n250 AUTH LOGIN\r\n') } else if (/^AUTH LOGIN/i.test(line)) { authStage = 1; socket.write('334 VXNlcm5hbWU6\r\n') } else if (authStage === 1) { authUser = Buffer.from(line, 'base64').toString('utf8'); authStage = 2; socket.write('334 UGFzc3dvcmQ6\r\n') } else if (authStage === 2) { authPass = Buffer.from(line, 'base64').toString('utf8'); authStage = 0; socket.write('235 authenticated\r\n') } else if (/^MAIL FROM/i.test(line)) { socket.write('250 OK\r\n') } else if (/^RCPT TO/i.test(line)) { rcptTo.push(line); socket.write('250 OK\r\n') } else if (/^DATA/i.test(line)) { inData = true; socket.write('354 end with <CRLF>.<CRLF>\r\n') } else if (/^QUIT/i.test(line)) { socket.write('221 bye\r\n'); socket.end() } else { socket.write('250 OK\r\n') }
    }
  })
})
await new Promise((r) => smtpMock.listen(0, '127.0.0.1', r))
const smtpPort = smtpMock.address().port
saveNotifyConfig(DATA, { mode: 'smtp', smtp: { host: '127.0.0.1', port: smtpPort, secure: false, user: 'mailer@x', pass: 'PlainPass9', from: 'kabage@x' } })
const smtpResult = await sendMail({ to: 'member@x', subject: 'SMTP 通道测试', text: '经 mock SMTP 投递。' })
check('smtp 模式 sent via smtp', smtpResult.sent === true && smtpResult.via === 'smtp')
await wait(100)
check('命令流：EHLO→AUTH→MAIL→RCPT→DATA→QUIT', (() => {
  const seq = commands.map((c) => c.split(' ')[0].toUpperCase())
  return seq.includes('EHLO') && seq.includes('AUTH') && seq.includes('MAIL') && seq.includes('RCPT') && seq.includes('DATA') && seq.includes('QUIT')
    && seq.indexOf('EHLO') < seq.indexOf('AUTH') && seq.indexOf('AUTH') < seq.indexOf('MAIL') && seq.indexOf('MAIL') < seq.indexOf('RCPT') && seq.indexOf('RCPT') < seq.indexOf('DATA') && seq.indexOf('DATA') < seq.indexOf('QUIT')
})())
check('AUTH LOGIN 凭据 base64 正确', authUser === 'mailer@x' && authPass === 'PlainPass9')
check('RCPT 收件人正确', rcptTo.some((r) => r.toUpperCase().includes('MEMBER@X')))
check('DATA 消息体为完整 MIME（Subject 编码 + 正文可解码）', /Subject: =\?UTF-8\?B\?/.test(dataPayload)
  && Buffer.from(dataPayload.split('Content-Transfer-Encoding: base64\r\n\r\n')[1]?.replace(/\r\n/g, '') ?? '', 'base64').toString('utf8').includes('经 mock SMTP 投递'))
check('SMTP 密码明文不出现在 DATA/命令流', !dataPayload.includes('PlainPass9') && !commands.some((c) => c.includes('PlainPass9')))
smtpMock.close()

// P2-5：应答码白名单——非数字首行应答（伪造/损坏服务器）必须被拒绝而非误判成功。
const garbageMock = createServer((socket) => {
  socket.on('error', () => {})
  socket.write('HELO this is not an SMTP reply\r\n')
  socket.on('data', () => { try { socket.write('still garbage\r\n') } catch { /* 客户端已断开 */ } })
})
await new Promise((r) => garbageMock.listen(0, '127.0.0.1', r))
saveNotifyConfig(DATA, { mode: 'smtp', smtp: { host: '127.0.0.1', port: garbageMock.address().port, secure: false, user: '', from: 'kabage@x' } })
const garbageResult = await sendMail({ to: 'member@x', subject: 's', text: 't' })
check('SMTP 非法（非数字）首行应答被拒（P2-5）', garbageResult.sent === false)
const code4xxMock = createServer((socket) => {
  socket.on('error', () => {})
  socket.write('450 busy\r\n')
  socket.on('data', () => { try { socket.write('450 busy\r\n') } catch { /* 客户端已断开 */ } })
})
await new Promise((r) => code4xxMock.listen(0, '127.0.0.1', r))
saveNotifyConfig(DATA, { mode: 'smtp', smtp: { host: '127.0.0.1', port: code4xxMock.address().port, secure: false, user: '', from: 'kabage@x' } })
const code4xxResult = await sendMail({ to: 'member@x', subject: 's', text: 't' })
check('4xx 应答被拒', code4xxResult.sent === false)
garbageMock.close()
code4xxMock.close()
saveNotifyConfig(DATA, { mode: 'file' })

/* ── 6. 管理台通知设置端点（admin-only + 审计）───────────────────────────── */
console.log('# 通知设置端点')
const notifySave = await post('/console/api/notify/config', { mode: 'file', smtp: { host: 'smtp2.x', port: 587, secure: false, user: 'u2@x', pass: 'NewPass8', from: 'n@x' }, adminNotify: ['boss@x'] }, adminCookie)
check('admin 保存通知配置 200', notifySave.status === 200)
check('security.notify_change 留痕（不含密码）', await (async () => {
  const deadline = Date.now() + 4000
  while (Date.now() < deadline) {
    const e = auditQuery({ actionPrefix: 'security.notify_change', limit: 100 })[0]
    if (e !== undefined) return e.result === 'ok' && !JSON.stringify(e).includes('NewPass8')
    await wait(40)
  }
  return false
})())
const badNotify = await post('/console/api/notify/config', { mode: 'carrier-pigeon' }, adminCookie)
check('非法 mode 400', badNotify.status === 400)
check('notify.json 不含 SMTP 明文密码', !readFileSync(join(DATA, 'notify.json'), 'utf8').includes('NewPass8'))

gateway.close()
gateway.closeAllConnections?.()
rmSync(DATA, { recursive: true, force: true })
console.log(`\n通过 ${passed}，失败 ${failed}`)
process.exit(failed > 0 ? 1 : 0)
