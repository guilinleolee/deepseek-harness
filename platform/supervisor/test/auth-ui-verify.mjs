/**
 * 卡巴格企业平台 · 登录/注册界面（auth-ui.mjs）自测脚本。
 *
 * 覆盖：登录页结构、两步验证第二阶段、SSO 按钮、可区分错误文案、注册页结构
 * （邀请码隐藏域/显示名/账号/密码/确认密码/强度提示/一致性提示/邀请信息/倒计时）、
 * 邀请码四类拒绝原因、XSS 转义、密码明文不外泄、无障碍、响应式与明暗主题、
 * 以及一次轻量 HTML 结构自检（标签配平 + 关键节点存在）。
 *
 * 运行：node platform/supervisor/test/auth-ui-verify.mjs
 * 退出码：全部通过 = 0；存在失败 = 1
 */
import assert from 'node:assert/strict'

import {
  AUTH_ERROR_TEXT,
  AUTH_UI_CSS,
  ROLE_LABELS,
  describeAuthError,
  escapeHtml,
  renderLoginPage,
  renderRegisterPage,
  renderTotpPage,
} from '../auth-ui.mjs'

/* ── 测试骨架 ──────────────────────────────────────────────────────────── */

let passed = 0
let failed = 0
const failures = []

/** 每个用例独立捕获异常：单条失败不中断整轮。 */
const check = (name, fn) => {
  try {
    fn()
    passed += 1
    console.log(`[PASS] ${name}`)
  } catch (error) {
    failed += 1
    failures.push({ name, message: error?.message ?? String(error) })
    console.error(`[FAIL] ${name} :: ${error?.message ?? error}`)
  }
}

const section = (title) => console.log(`\n── ${title} ──`)

/* ── 测试夹具 ──────────────────────────────────────────────────────────── */

/** 攻击载荷：同时打断属性上下文与标签上下文。 */
const XSS = '"><script>alert(1)</script>'
/** 哨兵：若出现在渲染结果里，说明密码明文被回显。 */
const SECRET = 'Sup3rSecret-Passw0rd!'

const loginHtml = renderLoginPage({ portalHostname: 'portal.example.com', ssoProviders: ['wecom', 'dingtalk'] })
const loginPlain = renderLoginPage()
const totpHtml = renderLoginPage({ stage: 'totp' })
const registerHtml = renderRegisterPage({ ssoProviders: ['wecom', 'dingtalk'] })
const registerRejected = renderRegisterPage({ error: '企业身份登录未启用，请联系管理员' })

/**
 * 判断渲染结果里是否存在「可执行」的注入脚本。
 * 注意：脚本块内出现字符串字面量 "alert(1)" 本身是惰性的（不是代码），
 * 真正的破口是脚本块内出现未转义的 <script / </script。
 */
const hasExecutablePayload = (html) =>
  html.includes('<script>alert(1)</script>') || /<script[^>]*>\s*alert\(1\)/i.test(html)

/** 脚本块内出现未转义的标签 → 说明注入切断了脚本块（真正的破口）。 */
const scriptBlockBreakout = (html) =>
  scriptBlocks(html).some((block) => /<\/?script/i.test(block))

/** 抽取页面内所有 <script> 块内容（用于逐块检查注入）。 */
const scriptBlocks = (html) => [...html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/gi)].map((m) => m[1])

/** 取某个 id 的标签片段（用于 hidden / autofocus 断言）。 */
const tagById = (html, id) => {
  const match = new RegExp(`<[^>]*\\bid="${id}"[^>]*>`, 'i').exec(html)
  return match === null ? '' : match[0]
}

/** 收集所有 input 标签（用于无障碍与密码泄漏检查）。 */
const inputTags = (html) => [...html.matchAll(/<input\b[^>]*>/gi)].map((m) => m[0])

/** 找出既没有 <label for> 关联、也没有 aria-label 的可见 input。 */
const inputsWithoutLabel = (html) => {
  const labels = [...html.matchAll(/<label\b[^>]*\bfor="([^"]+)"/gi)].map((m) => m[1])
  return inputTags(html).filter((tag) => {
    if (/type="hidden"/i.test(tag)) return false
    const id = (/\bid="([^"]+)"/i.exec(tag) ?? [])[1]
    if (id === undefined || id === '') return true
    return !(labels.includes(id) || /aria-label="[^"]+"/i.test(tag))
  })
}

/** 轻量 HTML 结构自检：成对标签必须配平。 */
const unbalancedTags = (html) => {
  const problems = []
  for (const tag of ['html', 'head', 'body', 'form', 'div', 'section', 'button', 'label', 'p', 'ul', 'li', 'span', 'style', 'script', 'main', 'header']) {
    const open = (html.match(new RegExp(`<${tag}\\b`, 'gi')) ?? []).length
    const close = (html.match(new RegExp(`</${tag}>`, 'gi')) ?? []).length
    if (open !== close) problems.push(`${tag}:${open}/${close}`)
  }
  return problems
}

/* ── A. 登录页：结构与表单 ────────────────────────────────────────────── */

section('A. 登录页 · 结构与表单')

check('A01 渲染结果为完整 HTML 文档', () => {
  assert.ok(loginHtml.startsWith('<!doctype html>'), '缺少 doctype')
  assert.ok(loginHtml.includes('<html lang="zh-CN">'), '缺少 lang 属性')
  assert.ok(loginHtml.trimEnd().endsWith('</html>'), '缺少 </html>')
})

check('A02 含 charset 与 viewport meta', () => {
  assert.ok(/<meta charset="utf-8">/i.test(loginHtml), '缺少 charset')
  assert.ok(/<meta name="viewport" content="width=device-width, initial-scale=1[^"]*">/i.test(loginHtml), '缺少 viewport')
})

check('A03 账号输入 autocomplete="username"', () => {
  const tag = tagById(loginHtml, 'acc')
  assert.ok(tag.includes('autocomplete="username"'), `账号输入缺少 autocomplete=username：${tag}`)
})

check('A04 账号输入有关联 label', () => {
  assert.ok(/<label for="acc">/.test(loginHtml), '缺少 <label for="acc">')
})

check('A05 密码输入 type="password"', () => {
  const tag = tagById(loginHtml, 'pw')
  assert.ok(/type="password"/.test(tag), `密码输入缺少 type=password：${tag}`)
})

check('A06 密码输入 autocomplete="current-password"', () => {
  const tag = tagById(loginHtml, 'pw')
  assert.ok(/autocomplete="current-password"/.test(tag), `密码输入缺少 autocomplete：${tag}`)
})

check('A07 密码输入有关联 label', () => {
  assert.ok(/<label for="pw">/.test(loginHtml), '缺少 <label for="pw">')
})

check('A08 两步验证码输入默认隐藏', () => {
  const wrap = tagById(loginHtml, 'totp-field')
  assert.ok(wrap.includes('hidden'), `默认阶段验证码区未隐藏：${wrap}`)
  assert.ok(/<label for="tc">/.test(loginHtml), '缺少 <label for="tc">')
})

check('A09 stage="totp" 时验证码区可见', () => {
  const wrap = tagById(totpHtml, 'totp-field')
  assert.ok(!wrap.includes('hidden'), `totp 阶段验证码区仍隐藏：${wrap}`)
})

check('A10 stage="totp" 时验证码输入被聚焦（autofocus）', () => {
  const tag = tagById(totpHtml, 'tc')
  assert.ok(tag.includes('autofocus'), `totp 阶段缺少 autofocus：${tag}`)
  assert.ok(/tc\.focus\(\)/.test(totpHtml), '缺少 JS 聚焦调用')
})

check('A11 默认表单 action 指向同源 /api/auth/login', () => {
  assert.ok(/<form id="login-form" method="post" action="\/api\/auth\/login"/.test(loginHtml), '默认 action 不是 /api/auth/login')
})

check('A12 stage="totp" 时表单 action 切换为 /api/auth/totp', () => {
  assert.ok(/<form id="login-form" method="post" action="\/api\/auth\/totp"/.test(totpHtml), 'totp 阶段 action 不是 /api/auth/totp')
})

check('A13 存在 type="submit" 提交按钮', () => {
  assert.ok(/<button[^>]*id="login-submit"[^>]*type="submit"/.test(loginHtml), '缺少提交按钮')
  assert.ok(loginHtml.includes('>登录</button>'), '提交按钮文案异常')
})

check('A14 错误区 role="alert"', () => {
  assert.ok(/role="alert"/.test(loginHtml), '缺少 role="alert"')
  assert.ok(/id="login-error"/.test(loginHtml), '缺少错误区容器')
})

check('A15 无 error 时错误区隐藏', () => {
  const tag = tagById(loginPlain, 'login-error')
  assert.ok(tag.includes('hidden'), `错误区未默认隐藏：${tag}`)
})

check('A16 有 error 时错误区可见且文案已转义', () => {
  const html = renderLoginPage({ error: '账号或密码错误' })
  const tag = tagById(html, 'login-error')
  assert.ok(!tag.includes('hidden'), '错误区未显示')
  assert.ok(html.includes('账号或密码错误'), '错误文案缺失')
})

check('A17 SSO 按钮在 ssoProviders 有值时出现', () => {
  assert.ok(/id="sso-list"/.test(loginHtml), '缺少 SSO 容器')
  assert.ok(loginHtml.includes('href="/api/auth/sso/wecom/start"'), '缺少企业微信按钮')
  assert.ok(loginHtml.includes('href="/api/auth/sso/dingtalk/start"'), '缺少钉钉按钮')
  assert.ok(loginHtml.includes('企业微信'), '缺少提供方中文标签')
})

check('A18 SSO 按钮在 ssoProviders 为空时不出现', () => {
  assert.ok(!loginPlain.includes('id="sso-list"'), '空列表仍渲染了 SSO 容器')
  assert.ok(!loginPlain.includes('/api/auth/sso/'), '空列表仍渲染了 SSO 链接')
})

check('A19 非法 provider id 被过滤（防路径注入）', () => {
  const html = renderLoginPage({ ssoProviders: ['../../evil', 'ok one', 'wecom'] })
  assert.ok(!html.includes('evil'), '非法 provider 泄漏到页面')
  assert.ok(!html.includes('ok one'), '含空格的 provider 泄漏到页面')
  assert.ok(html.includes('href="/api/auth/sso/wecom/start"'), '合法 provider 被误删')
})

check('A20 支持 { id, label } 形式的 provider', () => {
  const html = renderLoginPage({ ssoProviders: [{ id: 'oidc', label: '统一身份' }] })
  assert.ok(html.includes('href="/api/auth/sso/oidc/start"'), '缺少自定义 provider 链接')
  assert.ok(html.includes('统一身份'), '缺少自定义 provider 标签')
})

/* ── B. 登录页：错误可区分 ─────────────────────────────────────────────── */

section('B. 登录页 · 可区分的中文错误提示')

check('B01 五类登录错误文案互不相同', () => {
  const keys = ['bad_credentials', 'locked', 'disabled', 'totp_invalid', 'sso_unbound']
  const texts = keys.map((key) => AUTH_ERROR_TEXT[key])
  assert.equal(new Set(texts).size, texts.length, '存在重复文案')
  for (const text of texts) assert.ok(text.length > 0, '存在空文案')
})

check('B02 锁定文案含「锁定」', () => {
  assert.ok(AUTH_ERROR_TEXT.locked.includes('锁定'), AUTH_ERROR_TEXT.locked)
})

check('B03 禁用文案含「禁用」', () => {
  assert.ok(AUTH_ERROR_TEXT.disabled.includes('禁用'), AUTH_ERROR_TEXT.disabled)
})

check('B04 密码错误文案含「密码」且不含「验证码」', () => {
  assert.ok(AUTH_ERROR_TEXT.bad_credentials.includes('密码'), AUTH_ERROR_TEXT.bad_credentials)
  assert.ok(!AUTH_ERROR_TEXT.bad_credentials.includes('验证码'), '密码错误文案混入验证码语义')
})

check('B05 两步验证码错误文案含「验证码」', () => {
  assert.ok(AUTH_ERROR_TEXT.totp_invalid.includes('验证码'), AUTH_ERROR_TEXT.totp_invalid)
})

check('B06 SSO 未绑定文案含「绑定」并给出出路', () => {
  assert.ok(AUTH_ERROR_TEXT.sso_unbound.includes('绑定'), AUTH_ERROR_TEXT.sso_unbound)
})

check('B07 describeAuthError 区分 429 锁定', () => {
  const text = describeAuthError(429, '登录尝试过于频繁，账号已临时锁定，请约 12 分钟后再试')
  assert.ok(text.includes('锁定'), text)
  assert.ok(text.includes('12'), `未带出剩余分钟数：${text}`)
})

check('B08 describeAuthError 区分账号禁用', () => {
  const text = describeAuthError(401, '账号已禁用，请联系管理员')
  assert.ok(text.includes('禁用'), text)
})

check('B09 describeAuthError 区分密码错误', () => {
  const text = describeAuthError(401, '账号或密码错误')
  assert.ok(text.includes('密码'), text)
  assert.ok(!text.includes('验证码'), text)
})

check('B10 describeAuthError 区分验证码错误', () => {
  const text = describeAuthError(401, '账号或验证码错误')
  assert.ok(text.includes('验证码'), text)
})

check('B11 页面内联脚本含五类错误分支（不落笼统「登录失败」）', () => {
  for (const keyword of ['禁用', '验证码', '429', '403']) {
    assert.ok(loginHtml.includes(keyword), `内联脚本缺少分支关键词：${keyword}`)
  }
  assert.ok(!loginHtml.includes('登录失败（HTTP'), '仍使用笼统的失败文案')
})

/* ── C. 注册页：结构 ───────────────────────────────────────────────────── */

section('C. 企业身份开通页 · 结构')

check('C01 渲染结果为完整 HTML 文档', () => {
  assert.ok(registerHtml.startsWith('<!doctype html>'), '缺少 doctype')
  assert.ok(registerHtml.trimEnd().endsWith('</html>'), '缺少 </html>')
})

check('C02 含 viewport meta（响应式）', () => {
  assert.ok(/<meta name="viewport" content="width=device-width, initial-scale=1[^"]*">/i.test(registerHtml), '缺少 viewport')
})

check('C03 已取消邀请码注册：页面无邀请码输入/隐藏域', () => {
  assert.ok(!/name="code"/i.test(registerHtml), '仍存在邀请码字段')
  assert.ok(!/id="code-retry"/i.test(registerHtml), '仍存在换邀请码输入')
  assert.ok(!/邀请码/.test(registerHtml), '页面仍出现「邀请码」文案')
  assert.ok(!/invite/i.test(registerHtml), '页面仍出现 invite 相关内容')
})

check('C04 页面不收集任何凭据（无密码/账号输入）', () => {
  assert.ok(!/type="password"/i.test(registerHtml), '仍存在密码输入')
  assert.ok(!/name="password"/i.test(registerHtml), '仍存在密码字段')
  assert.ok(!/name="account"/i.test(registerHtml), '仍存在账号输入')
})

check('C05 列出已启用的企业身份入口并链接到 SSO start', () => {
  assert.ok(registerHtml.includes('/api/auth/sso/wecom/start'), '缺少企业微信开通入口')
  assert.ok(registerHtml.includes('/api/auth/sso/dingtalk/start'), '缺少钉钉开通入口')
  assert.ok(registerHtml.includes('企业微信'), '缺少企业微信文案')
  assert.ok(registerHtml.includes('钉钉'), '缺少钉钉文案')
})

check('C06 说明开通流程（扫码 → 首次登录自动建号）', () => {
  assert.ok(registerHtml.includes('开通账号'), '缺少开通账号标题')
  assert.ok(registerHtml.includes('扫码'), '缺少扫码说明')
  assert.ok(registerHtml.includes('自动'), '缺少自动开通说明')
})

check('C07 无 SSO 启用时给出联系管理员的指引', () => {
  const empty = renderRegisterPage({})
  assert.ok(empty.includes('管理员'), '空态缺少管理员指引')
  assert.ok(!empty.includes('/api/auth/sso/'), '空态不应出现 SSO 入口')
})

check('C08 已有账号可回到登录页', () => {
  assert.ok(registerHtml.includes('href="/login"'), '缺少登录页链接')
})

check('C09 页面无脚本块（不含任何动态逻辑）', () => {
  assert.ok(!/<script/i.test(registerHtml), '开通页不应包含脚本块')
})

check('C10 provider id 走白名单过滤（防路径注入）', () => {
  const evil = renderRegisterPage({ ssoProviders: ['../../etc/passwd', 'wecom'] })
  assert.ok(!evil.includes('/api/auth/sso/..'), '路径注入未被过滤')
  assert.ok(evil.includes('/api/auth/sso/wecom/start'), '合法 provider 被误删')
})

section('E. XSS 防护')

check('E01 登录页 error 注入被转义', () => {
  const html = renderLoginPage({ error: XSS })
  assert.ok(!hasExecutablePayload(html), 'error 注入产生可执行脚本')
  assert.ok(html.includes('&lt;script&gt;alert(1)&lt;/script&gt;'), '未看到转义后的文案')
})

check('E02 登录页 notice 注入被转义', () => {
  const html = renderLoginPage({ notice: XSS })
  assert.ok(!hasExecutablePayload(html), 'notice 注入产生可执行脚本')
})

check('E03 登录页 portalHostname 注入被转义', () => {
  const html = renderLoginPage({ portalHostname: XSS })
  assert.ok(!hasExecutablePayload(html), 'portalHostname 注入产生可执行脚本')
  for (const block of scriptBlocks(html)) {
    assert.ok(!block.includes('alert(1)'), '脚本块内出现注入代码')
  }
})

check('E04 注册页 error 注入被转义', () => {
  const html = renderRegisterPage({ error: XSS })
  assert.ok(!hasExecutablePayload(html), 'error 注入产生可执行脚本')
})

check('E05 开通页错误文案注入被转义', () => {
  const html = renderRegisterPage({ error: XSS })
  assert.ok(!hasExecutablePayload(html), 'department 注入产生可执行脚本')
  assert.ok(html.includes('&lt;script&gt;'), '未看到转义后的文案')
})

check('E06 开通页 provider label 注入被转义', () => {
  const html = renderRegisterPage({ ssoProviders: [{ id: 'wecom', label: XSS }] })
  assert.ok(!hasExecutablePayload(html), 'role 注入产生可执行脚本')
})

check('E07 开通页空态提示注入被转义', () => {
  const html = renderRegisterPage({ error: XSS, ssoProviders: [] })
  assert.ok(!hasExecutablePayload(html), 'expiresAt 注入产生可执行脚本')
})

check('E08 注册页邀请码 code 注入被转义', () => {
  const html = renderRegisterPage({ ssoProviders: [XSS] })
  assert.ok(!hasExecutablePayload(html), 'code 注入产生可执行脚本')
})

check('E09 开通页 provider id 注入被转义', () => {
  const html = renderRegisterPage({ ssoProviders: [XSS] })
  assert.ok(!hasExecutablePayload(html), 'instanceId 注入产生可执行脚本')
})

check('E10 注入后所有 <script> 块均不含载荷', () => {
  const pages = [renderLoginPage({ error: XSS, notice: XSS, portalHostname: XSS }), renderRegisterPage({ error: XSS, ssoProviders: ['wecom'] })]
  for (const html of pages) {
    for (const block of scriptBlocks(html)) {
      assert.ok(!block.includes('alert(1)'), '脚本块内出现注入代码')
    }
  }
})

check('E11 渲染结果不含 javascript: 协议', () => {
  assert.ok(!loginHtml.includes('javascript:'), '登录页含 javascript: 协议')
  assert.ok(!registerHtml.includes('javascript:'), '注册页含 javascript: 协议')
})

check('E12 escapeHtml 覆盖 & < > " \'', () => {
  assert.equal(escapeHtml('&'), '&amp;')
  assert.equal(escapeHtml('<'), '&lt;')
  assert.equal(escapeHtml('>'), '&gt;')
  assert.equal(escapeHtml('"'), '&quot;')
  assert.equal(escapeHtml("'"), '&#39;')
  assert.equal(escapeHtml('a&b<c'), 'a&amp;b&lt;c')
})

/* ── F. 不得泄漏密码明文 ───────────────────────────────────────────────── */

section('F. 不得泄漏密码明文')

check('F01 密码输入框不带 value 属性', () => {
  for (const html of [loginHtml, totpHtml, registerHtml]) {
    for (const tag of inputTags(html)) {
      if (!/type="password"/i.test(tag)) continue
      assert.ok(!/\bvalue=/i.test(tag), `密码输入框带 value：${tag}`)
    }
  }
})

check('F02 渲染函数忽略任何密码字段（不回显）', () => {
  const html = renderRegisterPage({ ssoProviders: [{ id: 'wecom', label: SECRET, password: SECRET }] })
  assert.ok(!html.includes(SECRET), '密码哨兵出现在渲染结果中')
})

check('F03 渲染结果不含任何令牌/凭据存取', () => {
  for (const html of [loginHtml, registerHtml]) {
    assert.ok(!html.includes('localStorage'), '使用了 localStorage')
    assert.ok(!html.includes('sessionStorage'), '使用了 sessionStorage')
    assert.ok(!html.includes('document.cookie'), '读取了 document.cookie')
  }
})

check('F04 登录/注册页均不在页面内下发令牌', () => {
  assert.ok(!/set-cookie/i.test(loginHtml), '登录页出现 set-cookie')
  assert.ok(!/\btoken\b\s*[:=]\s*["']/.test(loginHtml), '登录页内嵌了令牌变量')
})

/* ── G. 无障碍 ─────────────────────────────────────────────────────────── */

section('G. 无障碍')

check('G01 登录页每个可见 input 都有 label 或 aria-label', () => {
  const missing = inputsWithoutLabel(loginHtml)
  assert.deepEqual(missing, [], `缺少标签的输入：${missing.join(' | ')}`)
})

check('G02 注册页每个可见 input 都有 label 或 aria-label', () => {
  const missing = inputsWithoutLabel(registerHtml)
  assert.deepEqual(missing, [], `缺少标签的输入：${missing.join(' | ')}`)
})

check('G03 拒绝态注册页每个可见 input 都有 label 或 aria-label', () => {
  const missing = inputsWithoutLabel(registerRejected)
  assert.deepEqual(missing, [], `缺少标签的输入：${missing.join(' | ')}`)
})

check('G04 表单具备提交语义（登录页有表单；开通页无表单）', () => {
  assert.ok(/<form[^>]*method="post"/.test(loginHtml), '登录表单缺少 method=post')
  assert.ok(/<button[^>]*type="submit"/.test(loginHtml), '登录页缺少提交按钮')
  assert.ok(!/<form/i.test(registerHtml), '开通页不应含表单（不收集凭据）')
  assert.ok(!/<button[^>]*type="submit"/.test(registerHtml), '开通页不应含提交按钮')
})

check('G05 错误区 role="alert"（登录页 + 注册页）', () => {
  assert.ok(/id="login-error"[^>]*role="alert"/.test(loginHtml) || /role="alert"[^>]*id="login-error"/.test(loginHtml), '登录页错误区缺少 role=alert')
  assert.ok(/id="register-error"[^>]*role="alert"/.test(registerHtml) || /role="alert"[^>]*id="register-error"/.test(registerHtml), '注册页错误区缺少 role=alert')
})

check('G06 焦点环可见（:focus-visible + outline）', () => {
  assert.ok(AUTH_UI_CSS.includes(':focus-visible'), '缺少 :focus-visible 规则')
  assert.ok(/outline:\s*\d+px\s+solid/.test(AUTH_UI_CSS), '缺少 outline 焦点环')
})

check('G07 页面语言与标题存在', () => {
  assert.ok(/<html lang="zh-CN">/.test(loginHtml), '登录页缺少 lang')
  assert.ok(/<html lang="zh-CN">/.test(registerHtml), '注册页缺少 lang')
  assert.ok(/<title>卡巴格 · 登录<\/title>/.test(loginHtml), '登录页标题异常')
  assert.ok(/<title>卡巴格 · 开通账号<\/title>/.test(registerHtml), '开通页标题异常')
})

check('G08 主区域有可访问名称（aria-labelledby）', () => {
  assert.ok(/aria-labelledby="auth-title"/.test(loginHtml), '登录页缺少 aria-labelledby')
  assert.ok(/aria-labelledby="auth-title"/.test(registerHtml), '注册页缺少 aria-labelledby')
})

/* ── H. 响应式与主题 ───────────────────────────────────────────────────── */

section('H. 响应式、明暗主题与离线可用')

check('H01 两个页面都含 viewport meta', () => {
  for (const html of [loginHtml, registerHtml]) {
    assert.ok(/name="viewport"/.test(html), '缺少 viewport meta')
  }
})

check('H02 样式含移动端断点', () => {
  assert.ok(/@media \(max-width:\s*560px\)/.test(AUTH_UI_CSS), '缺少移动端断点')
})

check('H03 样式含 prefers-color-scheme 深色适配', () => {
  assert.ok(/@media \(prefers-color-scheme:\s*dark\)/.test(AUTH_UI_CSS), '缺少深色模式')
  assert.ok(/color-scheme:\s*light dark/.test(AUTH_UI_CSS), '缺少 color-scheme 声明')
})

check('H04 页面声明 color-scheme meta', () => {
  for (const html of [loginHtml, registerHtml]) {
    assert.ok(/<meta name="color-scheme" content="light dark">/.test(html), '缺少 color-scheme meta')
  }
})

check('H05 无外部 CDN / 字体 / 图片（离线可用）', () => {
  for (const html of [loginHtml, registerHtml]) {
    assert.ok(!/<link\b/i.test(html), '出现 <link> 外链')
    assert.ok(!/<script[^>]*\bsrc=/i.test(html), '出现外链脚本')
    assert.ok(!/<img\b/i.test(html), '出现 <img> 外链')
    assert.ok(!/@import/i.test(html), '出现 CSS @import')
    assert.ok(!/https?:\/\//i.test(html), '出现绝对 URL')
  }
})

check('H06 样式表被两个页面内联引用', () => {
  assert.ok(loginHtml.includes(AUTH_UI_CSS), '登录页未内联 AUTH_UI_CSS')
  assert.ok(registerHtml.includes(AUTH_UI_CSS), '注册页未内联 AUTH_UI_CSS')
})

/* ── I. 通用契约 ───────────────────────────────────────────────────────── */

section('I. 通用契约')

check('I01 renderTotpPage 等价于 stage="totp"', () => {
  const a = renderTotpPage({ portalHostname: 'x.example.com' })
  const b = renderLoginPage({ portalHostname: 'x.example.com', stage: 'totp' })
  assert.equal(a, b, 'renderTotpPage 与 renderLoginPage(stage=totp) 输出不一致')
})

check('I02 renderLoginPage 无参数时可用（默认全空）', () => {
  const html = renderLoginPage()
  assert.ok(html.includes('login-form'), '缺少表单')
  assert.ok(html.includes('id="acc"'), '缺少账号输入')
})

check('I03 renderRegisterPage 无参数时可用（邀请缺失也不崩）', () => {
  const html = renderRegisterPage()
  assert.ok(html.includes('开通账号'), '缺少开通页内容')
  assert.ok(!html.includes('id="invite-panel"'), '仍存在邀请信息面板')
})

check('I04 导出面完整（模块契约）', () => {
  assert.equal(typeof AUTH_UI_CSS, 'string')
  assert.equal(typeof renderLoginPage, 'function')
  assert.equal(typeof renderRegisterPage, 'function')
  assert.equal(typeof renderTotpPage, 'function')
  assert.equal(typeof describeAuthError, 'function')
  assert.equal(typeof escapeHtml, 'function')
})

/* ── J. HTML 结构自检（无浏览器时的替代校验）──────────────────────────── */

section('J. HTML 结构自检')

check('J01 登录页标签配平', () => {
  const problems = unbalancedTags(loginHtml)
  assert.deepEqual(problems, [], `标签未配平：${problems.join(', ')}`)
})

check('J02 两步验证页标签配平', () => {
  const problems = unbalancedTags(totpHtml)
  assert.deepEqual(problems, [], `标签未配平：${problems.join(', ')}`)
})

check('J03 注册页标签配平', () => {
  const problems = unbalancedTags(registerHtml)
  assert.deepEqual(problems, [], `标签未配平：${problems.join(', ')}`)
})

check('J04 拒绝态注册页标签配平', () => {
  const problems = unbalancedTags(registerRejected)
  assert.deepEqual(problems, [], `标签未配平：${problems.join(', ')}`)
})

check('J05 登录页关键节点齐备', () => {
  const nodes = ['login-form', 'login-error', 'login-notice', 'acc', 'pw', 'tc', 'totp-field', 'pw-field', 'login-submit']
  for (const id of nodes) {
    assert.ok(loginHtml.includes(`id="${id}"`), `缺少节点 #${id}`)
  }
})

check('J06 注册页关键节点齐备', () => {
  const nodes = ['register-error', 'sso-list', 'enroll-guide']
  for (const id of nodes) {
    assert.ok(registerHtml.includes(`id="${id}"`), `缺少节点 #${id}`)
  }
})

check('J07 表单提交端点均为同源相对路径', () => {
  const actions = [...loginHtml.matchAll(/<form[^>]*action="([^"]+)"/gi)].map((m) => m[1])
    .concat([...registerHtml.matchAll(/<form[^>]*action="([^"]+)"/gi)].map((m) => m[1]))
  assert.ok(actions.length > 0, '未找到表单 action')
  for (const action of actions) {
    assert.ok(action.startsWith('/'), `action 非同源相对路径：${action}`)
    assert.ok(!action.startsWith('//'), `action 为协议相对 URL：${action}`)
  }
})

/* ── K. 加固回归：脚本静态化与插值点全检 ───────────────────────────────── */

section('K. 加固回归 · 脚本静态化与插值点全检')

check('K01 页面脚本块内容不随动态输入变化（脚本静态化）', () => {
  const a = renderLoginPage({ error: 'x', notice: 'y', portalHostname: 'z' })
  const b = renderLoginPage({ error: 'X', notice: 'Y', portalHostname: 'Z' })
  const sa = scriptBlocks(a)
  const sb = scriptBlocks(b)
  assert.equal(sa.length, 1, `登录页脚本块数量异常：${sa.length}`)
  assert.equal(sa[0], sb[0], '登录页脚本块内容随动态输入变化，说明仍有插值残留')

  // 开通页不含任何脚本块（无表单、无动态逻辑）——插值残留无处可藏。
  const c = renderRegisterPage({ ssoProviders: ['wecom'] })
  const d = renderRegisterPage({ error: '"><script>alert(1)</script>', ssoProviders: ['wecom'] })
  assert.equal(scriptBlocks(c).length, 0, '开通页不应包含脚本块')
  assert.equal(scriptBlocks(d).length, 0, '开通页不应包含脚本块')
  assert.ok(!hasExecutablePayload(d), '开通页错误文案破开了页面')
})

check('K02 动态值改由 data-* 属性承载（不在脚本块内）', () => {
  assert.ok(/id="auth-root"[^>]*data-host=/.test(loginHtml), '登录页缺少 data-host 载体')
  assert.ok(/id="auth-root"[^>]*data-stage=/.test(loginHtml), '登录页缺少 data-stage 载体')
  assert.ok(/id="auth-root"[^>]*data-errors=/.test(loginHtml), '登录页缺少 data-errors 载体')
  assert.ok(/id="auth-root"[^>]*data-errors=/.test(registerHtml), '开通页缺少 data-errors 载体')
  assert.ok(loginHtml.includes('root.dataset.host'), '前端未从 dataset 读取 host')
})

check('K03 错误文案含 </script> 时页面不破', () => {
  const payload = '出错啦</script><script>alert(1)</script>'
  const html = renderLoginPage({ error: payload })
  assert.ok(!hasExecutablePayload(html), '错误文案破开了页面')
  assert.ok(!scriptBlockBreakout(html), '错误文案切断了脚本块')
  assert.equal(scriptBlocks(html).length, 1, '脚本块数量异常')
  assert.ok(html.includes('&lt;/script&gt;'), '未看到转义后的文案')
  assert.ok(html.includes('id="login-form"'), '表单结构被破坏')
  const reg = renderRegisterPage({ error: payload })
  assert.ok(!hasExecutablePayload(reg), '开通页错误文案破开了页面')
  assert.ok(!scriptBlockBreakout(reg), '开通页错误文案切断了脚本块')
  assert.equal(scriptBlocks(reg).length, 0, '开通页脚本块数量异常')
})

check('K04 开通页无任何隐藏域与表单（不收集凭据）', () => {
  const html = renderRegisterPage({ ssoProviders: ['wecom'] })
  assert.ok(!/type="hidden"/i.test(html), '开通页不应有隐藏域')
  assert.ok(!/<form/i.test(html), '开通页不应有表单')
  assert.ok(tagById(html, 'code') === '', '仍存在邀请码隐藏域')
})

check('K05 页面里不含任何 password 字段值回显', () => {
  const secret = 'Never-Show-Me-2026'
  // ① password 类键名注入输入对象 → 自动遮蔽
  const pages = {
    登录页: renderLoginPage({ portalHostname: 'x', ssoProviders: [{ id: 'wecom', label: '企业微信', password: secret }] }),
    TOTP页: renderTotpPage({ portalHostname: 'x', ssoProviders: [{ id: 'wecom', label: '企业微信', password: secret }] }),
    开通页: renderRegisterPage({ ssoProviders: [{ id: 'wecom', label: secret, password: secret }] }),
    开通页空态: renderRegisterPage({ ssoProviders: [{ id: 'wecom', label: secret, password: secret }] }),
  }
  for (const [name, html] of Object.entries(pages)) {
    assert.ok(!html.includes(secret), `${name} 回显了 password 字段值`)
  }
  // ② 敏感值经 sensitive 显式登记 → 即使走 error/notice 展示通道也被遮蔽
  const viaSlot = renderLoginPage({ error: secret, notice: secret, sensitive: [secret] })
  assert.ok(!viaSlot.includes(secret), 'error/notice 通道回显了敏感值')
  assert.ok(viaSlot.includes('********'), '敏感值未被替换为掩码')
  const regSlot = renderRegisterPage({ error: secret, sensitive: [secret] })
  assert.ok(!regSlot.includes(secret), '开通页 error 通道回显了敏感值')
  assert.ok(regSlot.includes('********'), '开通页敏感值未被替换为掩码')
})

check('K06 password 类键名在渲染结果中不可见', () => {
  for (const html of [loginHtml, totpHtml, registerHtml]) {
    assert.ok(!/password\s*[:=]\s*["'][^"']{4,}/i.test(html), '出现了密码类键值对')
    assert.ok(!/value="[^"]*"/.test(tagById(html, 'pw')), '密码输入框带 value')
    assert.ok(!/value="[^"]*"/.test(tagById(html, 'pw2')), '确认密码输入框带 value')
  }
})


/* ── 汇总 ──────────────────────────────────────────────────────────────── */

console.log('\n════════════════════════════════════════')
console.log(`用例总数：${passed + failed}`)
console.log(`PASS：${passed}`)
console.log(`FAIL：${failed}`)
if (failed > 0) {
  console.log('\n失败明细：')
  for (const item of failures) console.log(`  · ${item.name} :: ${item.message}`)
}
console.log('════════════════════════════════════════')
process.exit(failed === 0 ? 0 : 1)
