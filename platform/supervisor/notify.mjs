/**
 * 卡巴格企业平台 · 邮件通知（栏目规划 v2 阶段 11B）。
 *
 * 配置 data/notify.json：{"mode":"off"|"file"|"smtp", smtp:{host,port,secure,
 * auth:{user,passEnc},from}, adminNotify:[...]}，缺省 mode=off（零打扰）。
 * SMTP 密码经 AES-256-GCM 加密落盘（totp.mjs 的 encryptText，密钥派生自
 * auth-secret.key），配置读取与保存由调用方传入派生 key。
 *
 * sendMail({to, subject, text})：模块级串行队列异步发送；失败只 console.error
 * 并向调用方 resolve false——通知系统任何故障都不阻断主业务流程。
 * - file 模式：渲染完整 MIME（UTF-8 base64 头）写 data/outbox/<ts>-<n>.eml；
 * - smtp 模式：零依赖最小 SMTP 客户端（node:net + node:tls STARTTLS，
 *   EHLO/AUTH LOGIN/MAIL/RCPT/DATA/QUIT，多行应答，10 秒超时）。
 *
 * 真实外网 SMTP 未验证（无凭证）；本地 mock SMTP 由测试覆盖命令流。
 */
import { mkdirSync, readFileSync, renameSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'
import net from 'node:net'
import tls from 'node:tls'

import { decryptText, deriveKey, encryptText } from './totp.mjs'

const NOTIFY_FILE = 'notify.json'
const SMTP_TIMEOUT_MS = 10_000

const DEFAULT_NOTIFY = () => ({
  mode: 'off',
  smtp: { host: '', port: 587, secure: true, auth: { user: '', passEnc: '' }, from: '' },
  adminNotify: [],
})

let notifyDir = null
let notifyKey = null
let mailQueue = Promise.resolve()
let outboxSeq = 0

/** 配置通知数据目录与加密根（建服时调用一次；authSecret 缺省 = 通知禁用）。 */
export function initNotify(dataDir, authSecret) {
  notifyDir = dataDir
  notifyKey = authSecret === undefined ? null : deriveKey(authSecret)
}

function loadNotifyRaw(dataDir) {
  try {
    const parsed = JSON.parse(readFileSync(join(dataDir, NOTIFY_FILE), 'utf8'))
    return parsed !== null && typeof parsed === 'object' && !Array.isArray(parsed) ? parsed : {}
  } catch {
    return {}
  }
}

function saveNotifyRaw(dataDir, config) {
  mkdirSync(dataDir, { recursive: true })
  const path = join(dataDir, NOTIFY_FILE)
  const tmp = `${path}.tmp`
  writeFileSync(tmp, `${JSON.stringify(config, null, 2)}\n`)
  renameSync(tmp, path)
}

/** 读取生效配置（缺省自动生成 off）；passEnc 不解密（需要明文时走 getSmtpPassword）。 */
export function loadNotifyConfig(dataDir = notifyDir) {
  const merged = { ...DEFAULT_NOTIFY(), ...loadNotifyRaw(dataDir) }
  merged.smtp = { ...DEFAULT_NOTIFY().smtp, ...(merged.smtp ?? {}) }
  merged.smtp.auth = { ...DEFAULT_NOTIFY().smtp.auth, ...(merged.smtp?.auth ?? {}) }
  if (!Array.isArray(merged.adminNotify)) merged.adminNotify = []
  if (!['off', 'file', 'smtp'].includes(merged.mode)) merged.mode = 'off'
  return merged
}

/** 头部注入防线：地址/发件人等进 MIME 头的值一律禁止 CR/LF。 */
const hasCrlf = (value) => /[\r\n]/.test(String(value ?? ''))

/**
 * 合并保存通知配置（管理台通知设置区）。patch.pass 提供明文则加密落盘；
 * 未提供则保留既有 passEnc（页面回显打码）。from/user/adminNotify 含 CR/LF
 * 抛错（CRLF 头注入防线）；校验失败抛错（调用方转 400 并留审计）。
 */
export function saveNotifyConfig(dataDir, patch, key = notifyKey) {
  const config = loadNotifyConfig(dataDir)
  if (patch.mode !== undefined) {
    if (!['off', 'file', 'smtp'].includes(patch.mode)) throw new Error('mode 只支持 off/file/smtp')
    config.mode = patch.mode
  }
  if (patch.smtp !== undefined && typeof patch.smtp === 'object' && patch.smtp !== null) {
    const smtp = patch.smtp
    if (smtp.host !== undefined) {
      if (typeof smtp.host !== 'string') throw new Error('smtp.host 必须是字符串')
      config.smtp.host = smtp.host.trim()
    }
    if (smtp.port !== undefined) {
      const port = Number(smtp.port)
      if (!Number.isInteger(port) || port < 1 || port > 65535) throw new Error('smtp.port 必须是 1–65535 的整数')
      config.smtp.port = port
    }
    if (smtp.secure !== undefined) config.smtp.secure = smtp.secure === true
    if (smtp.from !== undefined) {
      if (typeof smtp.from !== 'string') throw new Error('smtp.from 必须是字符串')
      if (hasCrlf(smtp.from)) throw new Error('发件人地址不能包含换行符')
      config.smtp.from = smtp.from.trim()
    }
    if (smtp.user !== undefined) {
      if (typeof smtp.user !== 'string') throw new Error('smtp.auth.user 必须是字符串')
      if (hasCrlf(smtp.user)) throw new Error('SMTP 用户名不能包含换行符')
      config.smtp.auth.user = smtp.user.trim()
    }
    // 明文密码只在内存出现一次；未提供则保留既有密文（页面回显打码）。
    if (typeof smtp.pass === 'string' && smtp.pass !== '') {
      if (key === null) throw new Error('通知加密根未初始化（缺 auth-secret）')
      config.smtp.auth.passEnc = encryptText(key, smtp.pass)
    }
  }
  if (patch.adminNotify !== undefined) {
    if (!Array.isArray(patch.adminNotify) || patch.adminNotify.some((a) => typeof a !== 'string')) {
      throw new Error('adminNotify 必须是字符串数组')
    }
    if (patch.adminNotify.some(hasCrlf)) throw new Error('抄送地址不能包含换行符')
    config.adminNotify = patch.adminNotify.map((a) => a.trim()).filter(Boolean)
  }
  saveNotifyRaw(dataDir, config)
  return loadNotifyConfig(dataDir)
}

/** SMTP 密码明文（发信时用）；未配置返回 ''。 */
export function getSmtpPassword(dataDir = notifyDir, key = notifyKey) {
  const passEnc = loadNotifyConfig(dataDir).smtp.auth.passEnc
  if (typeof passEnc !== 'string' || passEnc === '') return ''
  if (key === null) throw new Error('通知加密根未初始化（缺 auth-secret）')
  return decryptText(key, passEnc)
}

/* ── MIME 渲染（file 模式直接落盘；smtp 模式作为 DATA 载荷）──────────────── */

const b64Utf8 = (text) => Buffer.from(String(text), 'utf8').toString('base64')

/** RFC 5322 Date 头（本地时区即可，邮件服务器不解析它做任何决策）。 */
const rfcDate = (date = new Date()) => date.toUTCString()

/**
 * 渲染完整 MIME 消息。to 支持 string 或数组（一封信多收件人，To 头逗号分隔）。
 * Subject 按 RFC 2047 UTF-8 base64 词编码；正文 base64 并按 76 字符折行。
 */
export function buildMime({ from, to, subject, text, date = new Date() }) {
  const toList = Array.isArray(to) ? to : [to]
  const body = Buffer.from(String(text ?? ''), 'utf8').toString('base64').replace(/(.{76})/g, '$1\r\n')
  return [
    `From: ${from}`,
    `To: ${toList.join(', ')}`,
    `Subject: =?UTF-8?B?${b64Utf8(subject)}?=`,
    `Date: ${rfcDate(date)}`,
    'MIME-Version: 1.0',
    'Content-Type: text/plain; charset=UTF-8',
    'Content-Transfer-Encoding: base64',
    '',
    body.endsWith('\r\n') ? body : `${body}\r\n`,
  ].join('\r\n')
}

/* ── 最小 SMTP 客户端（smtp 模式）────────────────────────────────────────── */

/**
 * 发送一封（底层：单收件人数组循环在外层 smtpSendMail）。命令序列：
 * 连接 → 220 → EHLO → [STARTTLS] → [AUTH LOGIN] → MAIL → RCPT(s) → DATA → QUIT。
 * 多行应答按 `250-`（继续）/`250 `（结束）解析；单命令 10 秒超时。
 */
export function smtpSendMail({ host, port, secure, user, pass, from, to, subject, text }) {
  return new Promise((resolveSend, rejectSend) => {
    const toList = Array.isArray(to) ? to : [to]
    let socket = secure
      ? tls.connect({ host, port, servername: host })
      : net.connect({ host, port })
    socket.setTimeout(SMTP_TIMEOUT_MS)
    let lineBuffer = ''
    let wait = null // { code, resolve, reject, timer }
    const transcript = []
    socket.on('timeout', () => {
      fail(new Error(`SMTP 超时（${SMTP_TIMEOUT_MS}ms）`))
      socket.destroy()
    })
    const fail = (error) => {
      if (wait) { wait.reject(error); wait = null }
      else rejectSend(error)
      // 失败即断开：伪造/挂死的对端不再消耗本进程资源。
      try { socket.destroy() } catch { /* 已销毁 */ }
    }
    const consume = (chunk) => {
      lineBuffer += chunk.toString('utf8')
      for (;;) {
        const idx = lineBuffer.indexOf('\r\n')
        if (idx === -1) return
        const line = lineBuffer.slice(0, idx)
        lineBuffer = lineBuffer.slice(idx + 2)
        if (wait === null) continue
        transcript.push(line)
        // 多行应答：`250-` 继续读；`250 `（空格）结束。
        // 应答码白名单判定（P2-5）：1xx–3xx 视为通过；NaN/非数字首行/4xx/5xx
        // 一律拒绝——伪造或损坏的应答绝不能被当成成功。
        if (!/^\d{3}(?:$|-)/.test(line) || /^\d{3} /.test(line) || /^\d{3}$/.test(line)) {
          const code = Number(line.slice(0, 3))
          const { resolve: resolveWait, reject: rejectWait } = wait
          clearTimeout(wait.timer)
          wait = null
          if (!Number.isInteger(code) || code < 100 || code >= 400) {
            rejectWait(new Error(`SMTP 非法或失败应答: ${line}`))
          } else {
            resolveWait({ code, transcript: transcript.join('\n') })
          }
        }
      }
    }
    const expect = (codes) => new Promise((resolveWait, rejectWait) => {
      const timer = setTimeout(() => fail(new Error(`SMTP 应答超时（${SMTP_TIMEOUT_MS}ms）`)), SMTP_TIMEOUT_MS)
      wait = { resolve: resolveWait, reject: rejectWait, timer }
      void codes
    })
    socket.on('data', consume)
    socket.on('error', fail)
    socket.on('close', () => { if (wait !== null) fail(new Error('SMTP 连接被关闭')) })
    const send = (line) => new Promise((r) => socket.write(`${line}\r\n`, () => r()))
    ;(async () => {
      await expect([220])
      await send('EHLO kabage.local')
      const ehlo = await expect([250])
      // STARTTLS 只在服务器明文端口宣告支持时升级（EHLO 应答含关键字）。
      if (!secure && /STARTTLS/i.test(ehlo.transcript)) {
        await send('STARTTLS')
        await expect([220])
        await new Promise((r) => {
          socket.removeAllListeners('data')
          socket.removeAllListeners('error')
          socket = tls.connect({ socket, servername: host }, () => r())
          socket.on('data', consume)
          socket.on('error', fail)
          socket.setTimeout(SMTP_TIMEOUT_MS, () => fail(new Error('SMTP 超时')))
        })
        await send('EHLO kabage.local')
        await expect([250])
      }
      if (user !== '') {
        await send('AUTH LOGIN')
        await expect([334])
        await send(Buffer.from(user, 'utf8').toString('base64'))
        await expect([334])
        await send(Buffer.from(pass, 'utf8').toString('base64'))
        await expect([235])
      }
      await send(`MAIL FROM:<${from}>`)
      await expect([250])
      for (const recipient of toList) {
        await send(`RCPT TO:<${recipient}>`)
        await expect([250, 251])
      }
      await send('DATA')
      await expect([354])
      // 点透明：行首 . → ..；CRLF 行尾；终止符 <CRLF>.<CRLF>。
      const dotStuffed = buildMime({ from, to: toList, subject, text })
        .split('\r\n').map((l) => (l.startsWith('.') ? `.${l}` : l)).join('\r\n')
      socket.write(`${dotStuffed}\r\n.\r\n`)
      await expect([250])
      await send('QUIT')
      await expect([221])
      socket.end()
      resolveSend({ transcript: transcript.join('\n') })
    })().catch(fail)
  })
}

/* ── 对外入口：串行发送队列 ─────────────────────────────────────────────── */

/**
 * 发送一封通知邮件。mode=off 直接跳过；notify 未初始化（缺 authSecret）跳过。
 * 返回 {sent, via, paths?}；file 模式 paths 为落盘的 .eml 路径。
 */
export function sendMail({ to, subject, text }) {
  if (notifyDir === null || notifyKey === null) return Promise.resolve({ sent: false, via: 'disabled' })
  const config = loadNotifyConfig(notifyDir)
  if (config.mode === 'off') return Promise.resolve({ sent: false, via: 'off' })
  const toList = (Array.isArray(to) ? to : [to]).map(String).filter(Boolean)
  if (toList.length === 0) return Promise.resolve({ sent: false, via: 'no-recipient' })
  const from = config.smtp.from || 'kabage@localhost'
  // 失败只 console.error 并 resolve 失败结果（绝不 reject——调用方多为 void
  // 触发点，rejection 会变 unhandled；队列链继续不断）。
  const job = mailQueue.then(async () => {
    if (config.mode === 'file') {
      const dir = join(notifyDir, 'outbox')
      mkdirSync(dir, { recursive: true })
      const stamp = new Date().toISOString().replace(/[:.]/g, '-')
      const paths = []
      // 每收件人一封（真实投递语义；To 头只含本人，便于测试断言归属）。
      for (const recipient of toList) {
        outboxSeq += 1
        const path = join(dir, `${stamp}-${outboxSeq}.eml`)
        const tmp = `${path}.tmp`
        writeFileSync(tmp, buildMime({ from, to: recipient, subject, text }))
        renameSync(tmp, path)
        paths.push(path)
      }
      return { sent: true, via: 'file', paths }
    }
    const pass = getSmtpPassword(notifyDir, notifyKey)
    await smtpSendMail({
      host: config.smtp.host, port: config.smtp.port, secure: config.smtp.secure,
      user: config.smtp.auth.user, pass, from,
      to: toList, subject, text,
    })
    return { sent: true, via: 'smtp' }
  }).catch((error) => {
    console.error(`[notify] 邮件发送失败（mode=${config.mode}）: ${error?.message ?? error}`)
    return { sent: false, via: 'failed', error: String(error?.message ?? error) }
  })
  mailQueue = job.then(() => {})
  return job
}

/** 供触发点使用的便捷包装：本人 + adminNotify 合并发送（审计由调用方负责）。 */
export function notifyAccountAndAdmins(account, subject, text) {
  // 未初始化（调用方未传 authSecret / initNotify 未调）时早退不抛（P2-6）：
  // 触发点在业务主流程内，通知缺失只降级不炸主流程。
  if (notifyDir === null || notifyKey === null) {
    console.error('[notify] 通知未初始化（缺数据目录或 auth-secret），跳过发送')
    return Promise.resolve({ sent: false, via: 'disabled' })
  }
  const config = loadNotifyConfig(notifyDir)
  const recipients = [account, ...config.adminNotify]
  return sendMail({ to: recipients, subject, text })
}

/** 主题前缀（触发点共用，便于 outbox 过滤）。 */
export const NOTIFY_SUBJECT_PREFIX = '[卡巴格]'
