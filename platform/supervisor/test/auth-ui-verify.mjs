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
  INVITE_REJECT_REASON,
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

const invite = {
  department: '研发中心',
  role: 'employee',
  instanceId: 'e01',
  expiresAt: '2099-12-31T23:59:59.000Z',
}

const loginHtml = renderLoginPage({ portalHostname: 'portal.example.com', ssoProviders: ['wecom', 'dingtalk'] })
const loginPlain = renderLoginPage()
const totpHtml = renderLoginPage({ stage: 'totp' })
const registerHtml = renderRegisterPage({ code: 'inv-demo-code', invite })
const registerRejected = renderRegisterPage({ code: 'inv-demo-code', reason: 'code_expired' })

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

section('C. 注册页 · 结构')

check('C01 渲染结果为完整 HTML 文档', () => {
  assert.ok(registerHtml.startsWith('<!doctype html>'), '缺少 doctype')
  assert.ok(registerHtml.trimEnd().endsWith('</html>'), '缺少 </html>')
})

check('C02 含 viewport meta（响应式）', () => {
  assert.ok(/<meta name="viewport" content="width=device-width, initial-scale=1[^"]*">/i.test(registerHtml), '缺少 viewport')
})

check('C03 邀请码隐藏域存在（type="hidden" name="code"）', () => {
  const tag = tagById(registerHtml, 'code')
  assert.ok(/type="hidden"/.test(tag), `邀请码域不是隐藏域：${tag}`)
  assert.ok(/name="code"/.test(tag), `邀请码域缺少 name=code：${tag}`)
  assert.ok(tag.includes('inv-demo-code'), '邀请码未写入隐藏域')
})

check('C04 显示名输入存在', () => {
  const tag = tagById(registerHtml, 'dn')
  assert.ok(tag.includes('name="displayName"'), tag)
  assert.ok(/<label for="dn">/.test(registerHtml), '缺少显示名 label')
})

check('C05 账号输入存在且 autocomplete=username', () => {
  const tag = tagById(registerHtml, 'acc')
  assert.ok(tag.includes('name="account"'), tag)
  assert.ok(tag.includes('autocomplete="username"'), tag)
})

check('C06 密码输入 type=password 且 autocomplete=new-password', () => {
  const tag = tagById(registerHtml, 'pw')
  assert.ok(/type="password"/.test(tag), tag)
  assert.ok(/autocomplete="new-password"/.test(tag), tag)
})

check('C07 确认密码输入存在', () => {
  const tag = tagById(registerHtml, 'pw2')
  assert.ok(/type="password"/.test(tag), tag)
  assert.ok(tag.includes('name="confirmPassword"'), tag)
})

check('C08 密码强度实时提示区存在', () => {
  assert.ok(/id="pw-rules"/.test(registerHtml), '缺少强度规则区')
  assert.ok(/id="pw-hint"/.test(registerHtml), '缺少强度提示文案')
  assert.ok(/aria-live="polite"/.test(registerHtml), '强度提示缺少 aria-live')
})

check('C09 强度规则覆盖「最少 8 位」与三类字符', () => {
  assert.ok(registerHtml.includes('至少 8 位'), '缺少长度规则')
  assert.ok(registerHtml.includes('小写字母'), '缺少小写规则')
  assert.ok(registerHtml.includes('大写字母'), '缺少大写规则')
  assert.ok(registerHtml.includes('数字'), '缺少数字规则')
  assert.ok(registerHtml.includes('三类字符'), '缺少三类字符口径说明')
})

check('C10 强度校验逻辑与后端口径一致（长度≥8 且 3 类）', () => {
  assert.ok(/value\.length >= 8/.test(registerHtml), '缺少长度判定')
  assert.ok(/\/\[a-z\]\//.test(registerHtml), '缺少小写判定')
  assert.ok(/\/\[A-Z\]\//.test(registerHtml), '缺少大写判定')
  assert.ok(/\/\[0-9\]\//.test(registerHtml), '缺少数字判定')
  assert.ok(/classes >= 3/.test(registerHtml), '缺少三类字符判定')
})

check('C11 确认密码一致性提示存在', () => {
  assert.ok(/id="pw2-hint"/.test(registerHtml), '缺少一致性提示')
  assert.ok(registerHtml.includes('两次输入的密码一致'), '缺少一致性文案')
})

check('C12 邀请信息展示：部门 / 角色 / 实例 / 有效期', () => {
  assert.ok(registerHtml.includes('研发中心'), '缺少部门')
  assert.ok(registerHtml.includes('成员'), '缺少角色中文标签')
  assert.ok(registerHtml.includes('e01'), '缺少实例')
  assert.ok(registerHtml.includes('2099-12-31'), '缺少有效期')
})

check('C13 角色标签映射正确（admin/auditor/employee）', () => {
  assert.equal(ROLE_LABELS.admin, '管理员')
  assert.equal(ROLE_LABELS.auditor, '审计员')
  assert.equal(ROLE_LABELS.employee, '成员')
  const html = renderRegisterPage({ invite: { ...invite, role: 'admin' } })
  assert.ok(html.includes('管理员'), 'admin 未映射为管理员')
})

check('C14 有效期倒计时元素存在', () => {
  assert.ok(/id="countdown"/.test(registerHtml), '缺少倒计时元素')
  assert.ok(/setInterval\(tick, 1000\)/.test(registerHtml), '缺少倒计时定时器')
})

check('C15 错误区 role="alert"', () => {
  assert.ok(/role="alert"/.test(registerHtml), '缺少 role="alert"')
  assert.ok(/id="register-error"/.test(registerHtml), '缺少错误区容器')
})

check('C16 表单 POST 到同源 /api/register', () => {
  assert.ok(/<form id="register-form" method="post" action="\/api\/register"/.test(registerHtml), '表单 action 不是 /api/register')
})

check('C17 存在 type="submit" 提交按钮', () => {
  assert.ok(/<button[^>]*id="register-submit"[^>]*type="submit"/.test(registerHtml), '缺少提交按钮')
})

check('C18 提交中按钮禁用逻辑存在', () => {
  assert.ok(/submit\.disabled = true/.test(registerHtml), '缺少提交时禁用按钮')
  assert.ok(/submit\.textContent = '提交中…'/.test(registerHtml), '缺少提交中文案')
})

/* ── D. 注册页：邀请码拒绝原因与出路 ──────────────────────────────────── */

section('D. 注册页 · 邀请码四类原因')

check('D01 邀请码无效 → 提示「无效」并给出出路', () => {
  const html = renderRegisterPage({ reason: 'invalid_code' })
  assert.ok(html.includes('无效'), '缺少无效提示')
  assert.ok(html.includes('联系'), '缺少联系管理员出路')
  assert.ok(html.includes('换一个邀请码'), '缺少换邀请码出路')
  assert.ok(html.includes('href="/login"'), '缺少直接登录出路')
})

check('D02 邀请码过期 → 提示「过期」并给出出路', () => {
  const html = renderRegisterPage({ reason: 'code_expired' })
  assert.ok(html.includes('过期'), '缺少过期提示')
  assert.ok(html.includes('重新生成'), '缺少重新生成出路')
  assert.ok(html.includes('直接登录'), '缺少直接登录出路')
})

check('D03 邀请码已使用 → 提示「已被使用」并给出出路', () => {
  const html = renderRegisterPage({ reason: 'code_used' })
  assert.ok(html.includes('已被使用') || html.includes('已使用'), '缺少已使用提示')
  assert.ok(html.includes('只能注册一次'), '缺少一次性说明')
  assert.ok(html.includes('直接登录'), '缺少直接登录出路')
})

check('D04 邀请码已撤销 → 提示「撤销」并给出出路', () => {
  const html = renderRegisterPage({ reason: 'code_revoked' })
  assert.ok(html.includes('撤销'), '缺少撤销提示')
  assert.ok(html.includes('联系'), '缺少联系出路')
})

check('D05 四类原因文案互不相同', () => {
  const reasons = Object.keys(INVITE_REJECT_REASON)
  const details = reasons.map((key) => INVITE_REJECT_REASON[key].detail)
  assert.equal(new Set(details).size, details.length, '存在重复文案')
  for (const key of reasons) {
    const item = INVITE_REJECT_REASON[key]
    assert.ok(item.title.length > 0 && item.detail.length > 0 && item.remedy.length > 0, `${key} 文案不完整`)
  }
})

check('D06 拒绝面板提供「换一个邀请码」输入框', () => {
  assert.ok(/id="code-retry"/.test(registerRejected), '缺少换码输入框')
  assert.ok(/<label for="code-retry">/.test(registerRejected), '换码输入框缺少 label')
  assert.ok(/id="code-retry-apply"/.test(registerRejected), '缺少使用该邀请码按钮')
})

check('D07 未知 reason 安全降级（不抛异常、不误报）', () => {
  const html = renderRegisterPage({ reason: 'weird_reason' })
  assert.ok(!html.includes('weird_reason'), '未知原因码被原样渲染')
  assert.ok(html.includes('register-form'), '页面结构被破坏')
})

/* ── E. XSS 防护 ───────────────────────────────────────────────────────── */

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

check('E05 注册页 invite.department 注入被转义', () => {
  const html = renderRegisterPage({ invite: { ...invite, department: XSS } })
  assert.ok(!hasExecutablePayload(html), 'department 注入产生可执行脚本')
  assert.ok(html.includes('&lt;script&gt;'), '未看到转义后的文案')
})

check('E06 注册页 invite.role 注入被转义', () => {
  const html = renderRegisterPage({ invite: { ...invite, role: XSS } })
  assert.ok(!hasExecutablePayload(html), 'role 注入产生可执行脚本')
})

check('E07 注册页 invite.expiresAt 注入被转义', () => {
  const html = renderRegisterPage({ invite: { ...invite, expiresAt: XSS } })
  assert.ok(!hasExecutablePayload(html), 'expiresAt 注入产生可执行脚本')
})

check('E08 注册页邀请码 code 注入被转义', () => {
  const html = renderRegisterPage({ code: XSS, invite })
  assert.ok(!hasExecutablePayload(html), 'code 注入产生可执行脚本')
})

check('E09 注册页 invite.instanceId 注入被转义', () => {
  const html = renderRegisterPage({ invite: { ...invite, instanceId: XSS } })
  assert.ok(!hasExecutablePayload(html), 'instanceId 注入产生可执行脚本')
})

check('E10 注入后所有 <script> 块均不含载荷', () => {
  const pages = [renderLoginPage({ error: XSS, notice: XSS, portalHostname: XSS }), renderRegisterPage({ error: XSS, invite: { ...invite, department: XSS, role: XSS, instanceId: XSS, expiresAt: XSS }, code: XSS })]
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
  const html = renderRegisterPage({ invite: { ...invite, password: SECRET }, error: SECRET })
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

check('G04 表单具备提交语义', () => {
  assert.ok(/<form[^>]*method="post"/.test(loginHtml), '登录表单缺少 method=post')
  assert.ok(/<form[^>]*method="post"/.test(registerHtml), '注册表单缺少 method=post')
  assert.ok(/<button[^>]*type="submit"/.test(loginHtml), '登录页缺少提交按钮')
  assert.ok(/<button[^>]*type="submit"/.test(registerHtml), '注册页缺少提交按钮')
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
  assert.ok(/<title>卡巴格 · 邀请注册<\/title>/.test(registerHtml), '注册页标题异常')
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
  assert.ok(html.includes('register-form'), '缺少表单')
  assert.ok(html.includes('id="invite-panel"'), '缺少邀请信息面板')
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
  const nodes = ['register-form', 'register-error', 'code', 'dn', 'acc', 'pw', 'pw2', 'pw-rules', 'pw-hint', 'pw2-hint', 'invite-panel', 'countdown', 'register-submit']
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

check('K01 脚本块完全静态：不同动态输入下脚本内容逐字一致', () => {
  const a = renderLoginPage({ portalHostname: 'a.example.com', error: '甲', notice: '乙', ssoProviders: ['wecom'] })
  const b = renderLoginPage({ portalHostname: '"><script>alert(1)</script>', error: '丙', notice: '丁', ssoProviders: [] })
  const sa = scriptBlocks(a)
  const sb = scriptBlocks(b)
  assert.equal(sa.length, 1, `登录页脚本块数量异常：${sa.length}`)
  assert.equal(sb.length, 1, `登录页脚本块数量异常：${sb.length}`)
  assert.equal(sa[0], sb[0], '脚本块内容随动态输入变化，说明仍有插值残留')

  const c = renderRegisterPage({ code: 'inv-a', invite })
  const d = renderRegisterPage({ code: '"><script>alert(1)</script>', invite: { ...invite, department: '<img src=x onerror=alert(1)>' } })
  const sc = scriptBlocks(c)
  const sd = scriptBlocks(d)
  assert.equal(sc.length, 1, `注册页脚本块数量异常：${sc.length}`)
  assert.equal(sc[0], sd[0], '注册页脚本块内容随动态输入变化，说明仍有插值残留')
})

check('K02 动态值改由 data-* 属性承载（不在脚本块内）', () => {
  assert.ok(/id="auth-root"[^>]*data-host=/.test(loginHtml), '登录页缺少 data-host 载体')
  assert.ok(/id="auth-root"[^>]*data-stage=/.test(loginHtml), '登录页缺少 data-stage 载体')
  assert.ok(/id="auth-root"[^>]*data-errors=/.test(loginHtml), '登录页缺少 data-errors 载体')
  assert.ok(/id="auth-root"[^>]*data-expires=/.test(registerHtml), '注册页缺少 data-expires 载体')
  assert.ok(/id="auth-root"[^>]*data-errors=/.test(registerHtml), '注册页缺少 data-errors 载体')
  assert.ok(loginHtml.includes('root.dataset.host'), '前端未从 dataset 读取 host')
  assert.ok(registerHtml.includes('root.dataset.expires'), '前端未从 dataset 读取 expires')
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
  assert.ok(!hasExecutablePayload(reg), '注册页错误文案破开了页面')
  assert.ok(!scriptBlockBreakout(reg), '注册页错误文案切断了脚本块')
  assert.equal(scriptBlocks(reg).length, 1, '注册页脚本块数量异常')
})

check('K04 邀请码含单引号与双引号时不破', () => {
  const code = `inv-'"><script>alert(1)</script>&key='`
  const html = renderRegisterPage({ code, invite })
  assert.ok(!hasExecutablePayload(html), '邀请码破开了页面')
  assert.ok(!scriptBlockBreakout(html), '邀请码切断了脚本块')
  assert.equal(scriptBlocks(html).length, 1, '脚本块数量异常')
  const tag = tagById(html, 'code')
  assert.ok(/&quot;/.test(tag), `双引号未转义：${tag}`)
  assert.ok(/&#39;/.test(tag), `单引号未转义：${tag}`)
  // 隐藏域属性闭合完好：value="..." 之后紧跟 aria-label
  assert.ok(/value="[^"]*"\s+aria-label="邀请码"/.test(tag), `隐藏域属性结构异常：${tag}`)
})

check('K05 页面里不含任何 password 字段值回显', () => {
  const secret = 'Never-Show-Me-2026'
  // ① password 类键名注入输入对象 → 自动遮蔽
  const pages = {
    登录页: renderLoginPage({ portalHostname: 'x', ssoProviders: [{ id: 'wecom', label: '企业微信', password: secret }] }),
    TOTP页: renderTotpPage({ portalHostname: 'x', ssoProviders: [{ id: 'wecom', label: '企业微信', password: secret }] }),
    注册页: renderRegisterPage({ code: 'inv-1', invite: { ...invite, password: secret, confirmPassword: secret, newPassword: secret, oldPassword: secret, passwordHash: secret } }),
    拒绝态注册页: renderRegisterPage({ code: 'inv-1', reason: 'code_expired', invite: { ...invite, password: secret } }),
  }
  for (const [name, html] of Object.entries(pages)) {
    assert.ok(!html.includes(secret), `${name} 回显了 password 字段值`)
  }
  // ② 敏感值经 sensitive 显式登记 → 即使走 error/notice 展示通道也被遮蔽
  const viaSlot = renderLoginPage({ error: secret, notice: secret, sensitive: [secret] })
  assert.ok(!viaSlot.includes(secret), 'error/notice 通道回显了敏感值')
  assert.ok(viaSlot.includes('********'), '敏感值未被替换为掩码')
  const regSlot = renderRegisterPage({ error: secret, sensitive: [secret] })
  assert.ok(!regSlot.includes(secret), '注册页 error 通道回显了敏感值')
  assert.ok(regSlot.includes('********'), '注册页敏感值未被替换为掩码')
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
