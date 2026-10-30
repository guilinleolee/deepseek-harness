/**
 * 卡巴格企业平台 · 登录 / 注册界面渲染模块（独立、零依赖 ESM）。
 *
 * 设计意图
 * --------
 * 1) 纯函数渲染：本模块只做「给定状态 → 输出完整 HTML 字符串」，不碰网络、
 *    不读文件、不依赖 gateway/portal/sso 等任何既有模块。因此可以被
 *    gateway.mjs（登录页）与 portal.mjs（邀请注册页）同时引用，也可以被
 *    单元测试独立加载。
 * 2) 零外部资源：样式内联、字体走系统栈、无 CDN/图片/图标外链 —— 离线可用，
 *    内网环境不会因为第三方请求失败而白屏。
 * 3) 明暗双主题：CSS 变量 + prefers-color-scheme，深色下不刺眼；焦点环用
 *    :focus-visible，键盘可达。
 * 4) 无障碍底线：每个可交互控件都有 <label for>，错误区 role="alert"，
 *    提示区 role="status"，表单有真实提交语义（<form method="post"> +
 *    <button type="submit">）。
 * 5) XSS 防线（三层）：
 *    a. 白名单渲染 —— 邀请只渲染 department/role/instanceId/expiresAt 四个已知字段；
 *    b. HTML 上下文一律 escapeHtml（& < > " ' 全转义，属性无法提前闭合）；
 *    c. **脚本块完全静态** —— 任何动态值（portalHostname / 过期时间 / 错误文案表）
 *       都不再插进 <script>，而是经 escapeHtml 后放进根元素的 data-* 属性，
 *       由前端用 dataset 读取。这样 payload 在物理上无法进入脚本上下文，
 *       既不能闭合标签，也不能形成可执行代码。
 * 6) 不回显密码类字段：渲染函数只认白名单字段，且最终对「输入对象里所有
 *    password/secret/token 类字段的值」做一次全页遮蔽（见 redactSecrets），
 *    即使调用方误把请求体塞进 invite 或 error，密码也不会出现在 HTML 里。
 *
 * 对外导出
 * --------
 * - AUTH_UI_CSS          共享样式表字符串（登录页/注册页复用）
 * - renderLoginPage()    登录页（含 stage='totp' 第二阶段）
 * - renderTotpPage()     两步验证阶段（renderLoginPage 的便捷包装）
 * - renderRegisterPage() 邀请注册页
 * - AUTH_ERROR_TEXT      错误文案表（前端 JS 与服务端提示共用同一份）
 * - describeAuthError()  把 (HTTP 状态码, 后端 error 文本) 归一为可区分文案
 * - escapeHtml()         HTML 转义工具（接线时若需自行拼装可复用）
 */

/** 角色码 → 中文标签（与 portal.mjs 的 ROLE_LABELS 保持一致）。 */
export const ROLE_LABELS = { admin: '管理员', auditor: '审计员', employee: '成员' }

/**
 * 第三方登录提供方标签。本模块不 import sso.mjs（避免循环依赖与耦合），
 * 只维护一份展示用的标签表；未知 provider 会被过滤掉，不生成按钮。
 */
export const SSO_PROVIDER_LABELS = { wecom: '企业微信', dingtalk: '钉钉' }

/* ── 转义与脱敏工具 ────────────────────────────────────────────────────── */

/**
 * HTML 文本/属性转义。顺序敏感：& 必须最先处理，否则会把已生成的实体
 * 二次转义（例如 &lt; → &amp;lt;）。
 */
export function escapeHtml (value) {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
}

/**
 * data-* 属性值序列化：与 escapeHtml 同口径，但额外保证结果可以安全地
 * 放进双引号属性里（引号已转义为 &quot;）。浏览器读取 dataset 时会自动
 * 反转义，JS 侧拿到的就是原始字符串。
 */
const dataAttr = (value) => escapeHtml(value)

/** 放进 data-* 属性的 JSON：先 JSON.stringify 再整体转义，dataset 读取后可直接 parse。 */
const dataJson = (value) => escapeHtml(JSON.stringify(value ?? null))

/** 只允许安全字符出现在 URL 路径段里（provider id 等），其余丢弃。 */
const safeSegment = (value) => (/^[A-Za-z0-9_-]{1,32}$/.test(String(value ?? '')) ? String(value) : '')

/** 敏感字段名匹配：password / secret / token / 密钥类，命中即视为不可回显。 */
const SENSITIVE_KEY_RE = /pass|pwd|secret|credential|token|api_?key|private_?key/i

/**
 * 收集输入对象里所有「敏感字段」的值（递归，含嵌套对象）。
 * 用于最终的全页遮蔽：即便调用方把请求体塞进 invite / error，密码值
 * 也不会出现在 HTML 里。
 */
function collectSensitiveValues (input, depth = 0, seen = new Set()) {
  if (input === null || input === undefined || depth > 4) return []
  if (typeof input === 'string' || typeof input === 'number' || typeof input === 'boolean') return []
  if (typeof input !== 'object') return []
  if (seen.has(input)) return []
  seen.add(input)
  const found = []
  for (const [key, value] of Object.entries(input)) {
    if (SENSITIVE_KEY_RE.test(key)) {
      if (typeof value === 'string' && value.length >= 4) found.push(value)
      continue
    }
    found.push(...collectSensitiveValues(value, depth + 1, seen))
  }
  return found
}

/**
 * 全页遮蔽：把敏感值在最终 HTML 里一律替换为掩码。
 * 双重保险——白名单渲染是第一道，这里是最后一道，确保页面里绝不出现
 * password 类字段的明文值。
 */
function redactSecrets (html, values) {
  let out = html
  for (const value of values) {
    if (typeof value !== 'string' || value.length < 4) continue
    out = out.split(value).join('********')
  }
  return out
}

/**
 * 汇总「需要遮蔽的值」：① 输入对象里所有 password/secret/token 类键的值；
 * ② 调用方通过 sensitive 显式登记的值（例如上游请求体里回传的密码）。
 */
function secretValuesOf (options, sensitive) {
  const list = [...collectSensitiveValues(options)]
  if (Array.isArray(sensitive)) {
    for (const value of sensitive) {
      if (typeof value === 'string' && value.length >= 4) list.push(value)
    }
  }
  return list
}

/* ── 错误文案表（前端 JS 与服务端提示共用同一份）───────────────────────── */

/**
 * 可区分的错误文案。刻意不使用笼统的「登录失败」：用户要能据此判断
 * 「重试」「等锁定期」「找管理员」「重新绑定」。
 */
export const AUTH_ERROR_TEXT = {
  bad_credentials: '账号或密码错误，请核对后重试。',
  locked: '登录尝试过于频繁，账号已被临时锁定，请约 {minutes} 分钟后再试。',
  disabled: '该账号已被禁用，请联系管理员恢复后登录。',
  totp_invalid: '两步验证码错误或已过期，请重新输入认证器中的 6 位动态码。',
  sso_unbound: '该企业账号尚未绑定卡巴格账号，请先完成一次性绑定（需输入账号与密码）。',
  sso_failed: '第三方登录失败，请重试或改用账号密码登录。',
  twofa_broken: '两步验证配置损坏，请联系管理员在管理台重置 2FA。',
  enrollment_required: '管理员已要求该角色绑定两步验证，请到个人中心完成绑定后重新登录。',
  cross_origin: '请求来源校验失败，请返回本页面重新登录。',
  network: '网络异常，请检查连接后重试。',
  unknown: '操作失败，请稍后重试。',
}

/**
 * 把后端的 (HTTP 状态码, error 文本) 归一为一条可区分的中文提示。
 * 后端 error 文本本身已是中文（如「账号已禁用，请联系管理员」），
 * 这里按语义归类，保证同一类故障给同一句话。
 *
 * @param {number} status HTTP 状态码
 * @param {string} rawError 后端返回的 error 字段
 * @returns {string} 可直接展示的中文提示
 */
export function describeAuthError (status, rawError) {
  const raw = String(rawError ?? '')
  if (status === 429) {
    const minutes = /约\s*(\d+)\s*分钟/.exec(raw)
    return AUTH_ERROR_TEXT.locked.replace('{minutes}', minutes ? minutes[1] : '若干')
  }
  if (status === 403) return AUTH_ERROR_TEXT.cross_origin
  if (status === 500) {
    if (raw.includes('两步验证')) return AUTH_ERROR_TEXT.twofa_broken
    return raw || AUTH_ERROR_TEXT.unknown
  }
  if (status === 401) {
    if (raw.includes('禁用')) return AUTH_ERROR_TEXT.disabled
    if (raw.includes('验证码')) return AUTH_ERROR_TEXT.totp_invalid
    return AUTH_ERROR_TEXT.bad_credentials
  }
  if (status === 404) return AUTH_ERROR_TEXT.network
  return raw || AUTH_ERROR_TEXT.unknown
}

/* ── 共享样式 ──────────────────────────────────────────────────────────── */

/**
 * 登录 / 注册页共用样式。企业风格：克制的蓝灰底色 + 白色卡片 + 单一强调色，
 * 圆角与阴影轻量，避免「炫技」导致的可信度下降。
 */
export const AUTH_UI_CSS = `
:root{
  color-scheme: light dark;
  --bg:#f4f6fa;
  --bg-grad:radial-gradient(1100px 520px at 50% -12%,#e6ecfb 0%,rgba(244,246,250,0) 62%);
  --card:#ffffff;
  --card-border:#e5e7eb;
  --text:#111827;
  --muted:#6b7280;
  --field-border:#d1d5db;
  --accent:#2563eb;
  --accent-strong:#1d4ed8;
  --on-accent:#ffffff;
  --danger:#b91c1c;--danger-bg:#fef2f2;--danger-border:#fecaca;
  --warn:#b45309;--warn-bg:#fffbeb;--warn-border:#fde68a;
  --ok:#047857;--ok-bg:#ecfdf5;--ok-border:#a7f3d0;
  --info:#1d4ed8;--info-bg:#eff6ff;--info-border:#bfdbfe;
  --radius:14px;
  --shadow:0 16px 40px rgba(15,23,42,.10);
}
@media (prefers-color-scheme:dark){
  :root{
    --bg:#0b1120;
    --bg-grad:radial-gradient(1100px 520px at 50% -12%,#152242 0%,rgba(11,17,32,0) 62%);
    --card:#111a2e;
    --card-border:#26324a;
    --text:#e6ebf5;
    --muted:#9aa7bd;
    --field-border:#33415c;
    --accent:#3b82f6;
    --accent-strong:#60a5fa;
    --on-accent:#06101f;
    --danger:#fca5a5;--danger-bg:#2a1418;--danger-border:#7f1d1d;
    --warn:#fcd34d;--warn-bg:#2a2110;--warn-border:#78551b;
    --ok:#6ee7b7;--ok-bg:#0d2a20;--ok-border:#14603f;
    --info:#93c5fd;--info-bg:#10233f;--info-border:#1e4a7a;
    --shadow:0 16px 40px rgba(0,0,0,.45);
  }
}
*{box-sizing:border-box}
html,body{height:100%}
body{
  margin:0;background:var(--bg);background-image:var(--bg-grad);background-repeat:no-repeat;
  color:var(--text);line-height:1.6;
  font-family:system-ui,-apple-system,"Segoe UI","PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;
  -webkit-font-smoothing:antialiased;
}
/* 键盘可达：鼠标点击不显示焦点环，Tab 聚焦必须清晰可见 */
:focus{outline:none}
:focus-visible{outline:3px solid var(--accent);outline-offset:2px;border-radius:8px}
.auth-shell{min-height:100%;display:flex;align-items:center;justify-content:center;padding:2rem 1rem}
.auth-card{
  width:100%;max-width:420px;background:var(--card);border:1px solid var(--card-border);
  border-radius:var(--radius);box-shadow:var(--shadow);padding:1.9rem 1.8rem;
}
.auth-head{margin-bottom:1.2rem}
.brand{margin:0;font-size:.78rem;letter-spacing:.16em;color:var(--muted);text-transform:uppercase}
.auth-head h1{margin:.25rem 0 .3rem;font-size:1.45rem;line-height:1.3}
.auth-sub{margin:0;color:var(--muted);font-size:.9rem}
.field{margin-bottom:.85rem}
.field label{display:block;font-size:.82rem;color:var(--muted);margin-bottom:.3rem}
.field input,.field select{
  width:100%;padding:.62rem .7rem;border-radius:9px;border:1px solid var(--field-border);
  background:var(--bg);color:var(--text);font-family:inherit;font-size:.95rem;
}
.field input:focus{border-color:var(--accent);box-shadow:0 0 0 3px rgba(37,99,235,.16)}
.hint{margin:.35rem 0 0;font-size:.79rem;color:var(--muted)}
.hint[data-state="ok"]{color:var(--ok)}
.hint[data-state="warn"]{color:var(--warn)}
.hint[data-state="error"]{color:var(--danger)}
.rules{list-style:none;margin:.45rem 0 0;padding:0;font-size:.79rem;color:var(--muted)}
.rules li{display:flex;gap:.4rem;align-items:baseline}
.rules li::before{content:"○";width:1em;flex:none;color:var(--muted)}
.rules li[data-ok="true"]{color:var(--ok)}
.rules li[data-ok="true"]::before{content:"✓"}
.btn{
  width:100%;margin-top:1rem;padding:.72rem 1rem;border:none;border-radius:9px;
  background:var(--accent);color:var(--on-accent);font-family:inherit;font-size:.95rem;
  font-weight:600;cursor:pointer;
}
.btn:hover{background:var(--accent-strong)}
.btn:disabled{opacity:.62;cursor:progress}
.btn-secondary{background:transparent;color:var(--text);border:1px solid var(--field-border);font-weight:500}
.btn-secondary:hover{background:rgba(127,127,127,.08)}
.alert{
  border-radius:10px;border:1px solid var(--card-border);padding:.62rem .8rem;
  font-size:.86rem;margin-bottom:.9rem;
}
.alert[hidden]{display:none!important}
.alert-error{background:var(--danger-bg);border-color:var(--danger-border);color:var(--danger)}
.alert-notice{background:var(--info-bg);border-color:var(--info-border);color:var(--info)}
.alert-warn{background:var(--warn-bg);border-color:var(--warn-border);color:var(--warn)}
.alert-ok{background:var(--ok-bg);border-color:var(--ok-border);color:var(--ok)}
.divider{display:flex;align-items:center;gap:.7rem;margin:1.1rem 0 .8rem;color:var(--muted);font-size:.78rem}
.divider::before,.divider::after{content:"";flex:1;height:1px;background:var(--card-border)}
.sso-list{display:grid;gap:.5rem}
.sso-btn{
  display:block;padding:.62rem .8rem;border-radius:9px;border:1px solid var(--card-border);
  background:var(--bg);color:var(--text);text-align:center;text-decoration:none;font-size:.9rem;
}
.sso-btn:hover{border-color:var(--accent);color:var(--accent)}
.auth-foot{margin-top:1.1rem;font-size:.85rem;color:var(--muted);text-align:center}
.auth-foot a{color:var(--accent)}
.info-panel{
  background:var(--info-bg);border:1px solid var(--info-border);border-radius:10px;
  padding:.85rem .95rem;margin-bottom:1rem;font-size:.86rem;color:var(--text);
}
@media (max-width:560px){
  .auth-shell{padding:1.1rem .8rem;align-items:flex-start}
  .auth-card{max-width:none;padding:1.35rem 1.1rem;border-radius:12px}
  .auth-head h1{font-size:1.28rem}
}
@media (prefers-reduced-motion:reduce){
  *{transition:none!important;animation:none!important}
}
`

/* ── 小工具（片段拼装）──────────────────────────────────────────────────── */

/** 提示框：role=alert 用于错误（会被读屏立即播报），role=status 用于中性提示。 */
const alertBox = ({ id, tone = 'error', role = 'alert', text = '', extra = '' }) => {
  const hidden = text === '' ? ' hidden' : ''
  return `<div class="alert alert-${tone}" role="${role}" id="${id}"${hidden}${extra}><span class="alert-text">${escapeHtml(text)}</span></div>`
}

/** 带 label 的输入行（无障碍：每个 input 都有 <label for>）。 */
const field = ({ id, label, type = 'text', name = '', autocomplete = '', required = false, attrs = '' }) => {
  const attrsAll = [
    `id="${id}"`,
    `name="${escapeHtml(name)}"`,
    type ? `type="${type}"` : '',
    autocomplete ? `autocomplete="${escapeHtml(autocomplete)}"` : '',
    required ? 'required' : '',
    attrs,
  ].filter(Boolean).join(' ')
  return `<div class="field">
<label for="${id}">${escapeHtml(label)}</label>
<input ${attrsAll}>
</div>`
}

/** 第三方登录按钮：provider id 经白名单过滤，避免路径注入。 */
const ssoButtons = (ssoProviders) => {
  const list = Array.isArray(ssoProviders) ? ssoProviders : []
  const items = []
  for (const raw of list) {
    const id = safeSegment(typeof raw === 'string' ? raw : raw?.id)
    if (id === '') continue
    const text = typeof raw === 'string'
      ? escapeHtml(SSO_PROVIDER_LABELS[id] ?? id)
      : escapeHtml(raw?.label ?? SSO_PROVIDER_LABELS[id] ?? id)
    items.push(`<a class="sso-btn" href="/api/auth/sso/${id}/start" rel="noopener">使用${text}账号登录</a>`)
  }
  if (items.length === 0) return ''
  return `<div class="divider">或使用企业身份登录</div>
<div class="sso-list" id="sso-list">
${items.join('\n')}
</div>`
}

/* ── 登录页 ────────────────────────────────────────────────────────────── */

/**
 * 渲染登录页。
 *
 * 脚本块是完全静态的：portalHostname / stage / 错误文案表全部经 escapeHtml
 * 放进根元素的 data-* 属性，由前端 dataset 读取。payload 因此无法进入
 * 脚本上下文（既不能闭合标签，也不能形成可执行代码）。
 *
 * @param {object} [options]
 * @param {string} [options.error=''] 服务端已知的错误文案（已转义输出）
 * @param {string} [options.portalHostname=''] portal 主机名：员工在 portal
 *        主机登录后跳个人中心 /me，实例子域登录则原地刷新进入工作区。
 * @param {Array} [options.ssoProviders=[]] 已启用的第三方登录 provider 列表
 *        （元素可以是 'wecom' 这样的字符串，或 { id, label } 对象）
 * @param {'password'|'totp'} [options.stage='password'] 'totp' 进入两步验证
 *        第二阶段：隐藏密码框、显示并聚焦验证码框、表单改为 POST /api/auth/totp
 * @param {string} [options.notice=''] 中性提示（如 SSO 未绑定的引导语）
 * @param {string[]} [options.sensitive=[]] 需要在页面上遮蔽的敏感值
 *        （例如上游请求体里回传的密码）；这些值一律以 ******** 呈现
 * @returns {string} 完整 HTML 字符串
 */
export function renderLoginPage (options = {}) {
  const { error = '', portalHostname = '', ssoProviders = [], stage = 'password', notice = '', sensitive = [] } = options
  const totpStage = stage === 'totp'
  const action = totpStage ? '/api/auth/totp' : '/api/auth/login'
  const submitText = totpStage ? '验证并登录' : '登录'
  const portalHint = portalHostname === ''
    ? ''
    : `<p class="hint">当前登录域名：${escapeHtml(portalHostname)}</p>`

  const html = `<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="color-scheme" content="light dark">
<meta name="referrer" content="same-origin">
<title>卡巴格 · 登录</title>
<style>${AUTH_UI_CSS}</style>
</head>
<body>
<main class="auth-shell" id="auth-root" data-stage="${escapeHtml(totpStage ? 'totp' : 'password')}" data-host="${dataAttr(portalHostname)}" data-errors="${dataJson(AUTH_ERROR_TEXT)}">
<section class="auth-card" aria-labelledby="auth-title">
<header class="auth-head">
<p class="brand">卡巴格企业平台</p>
<h1 id="auth-title">登录</h1>
<p class="auth-sub">使用企业账号登录卡巴格工作区</p>
</header>
${alertBox({ id: 'login-error', tone: 'error', role: 'alert', text: error })}
${alertBox({ id: 'login-notice', tone: 'notice', role: 'status', text: notice })}
<form id="login-form" method="post" action="${action}" novalidate>
${field({ id: 'acc', label: '账号（企业邮箱）', type: 'email', name: 'account', autocomplete: 'username', required: true })}
<div class="field" id="pw-field"${totpStage ? ' hidden' : ''}>
<label for="pw">密码</label>
<input id="pw" name="password" type="password" autocomplete="current-password">
</div>
<div class="field" id="totp-field"${totpStage ? '' : ' hidden'}>
<label for="tc">两步验证码</label>
<input id="tc" name="code" type="text" inputmode="numeric" autocomplete="one-time-code" maxlength="6" placeholder="6 位动态码"${totpStage ? ' autofocus' : ''}>
<p class="hint" id="tc-hint">请输入认证器 App 中的 6 位动态验证码。</p>
</div>
<button class="btn" id="login-submit" type="submit">${submitText}</button>
${portalHint}
</form>
${ssoButtons(ssoProviders)}
<p class="auth-foot">还没有账号？<a href="/register">用企业身份开通</a></p>
</section>
</main>
<script>
(function () {
  /* 动态值一律从 data-* 读取：脚本块内没有任何插值，payload 无法进入脚本上下文 */
  var root = document.getElementById('auth-root')
  var ERRORS = JSON.parse(root.dataset.errors)
  var STAGE = root.dataset.stage || 'password'
  var HOST = root.dataset.host || ''
  var form = document.getElementById('login-form')
  var errBox = document.getElementById('login-error')
  var errText = errBox.querySelector('.alert-text')
  var noteBox = document.getElementById('login-notice')
  var noteText = noteBox.querySelector('.alert-text')
  var submit = document.getElementById('login-submit')
  var acc = document.getElementById('acc')
  var pw = document.getElementById('pw')
  var pwField = document.getElementById('pw-field')
  var tc = document.getElementById('tc')
  var totpField = document.getElementById('totp-field')

  function showError (msg) { errText.textContent = msg; errBox.hidden = false }
  function clearError () { errText.textContent = ''; errBox.hidden = true }
  function showNotice (msg) { noteText.textContent = msg; noteBox.hidden = false }
  function busy (on) { submit.disabled = on; submit.textContent = on ? '处理中…' : (STAGE === 'totp' ? '验证并登录' : '登录') }

  /* 归类后端错误：密码错 / 锁定 / 禁用 / 验证码错 各给不同提示与出路 */
  function describe (status, payload) {
    var raw = (payload && payload.error) ? String(payload.error) : ''
    if (status === 429) {
      var m = /(\\d+)\\s*分钟/.exec(raw)
      return ERRORS.locked.replace('{minutes}', m ? m[1] : '若干')
    }
    if (status === 403) return ERRORS.cross_origin
    if (status === 500) return raw.indexOf('两步验证') >= 0 ? ERRORS.twofa_broken : (raw || ERRORS.unknown)
    if (status === 401) {
      if (raw.indexOf('禁用') >= 0) return ERRORS.disabled
      if (raw.indexOf('验证码') >= 0) return ERRORS.totp_invalid
      return ERRORS.bad_credentials
    }
    if (status === 404) return ERRORS.network
    return raw || ERRORS.unknown
  }

  function enterTotpStage () {
    STAGE = 'totp'
    form.setAttribute('action', '/api/auth/totp')
    pwField.hidden = true
    totpField.hidden = false
    busy(false)
    submit.textContent = '验证并登录'
    tc.focus()
  }

  function finish (payload) {
    if (payload && payload.role === 'employee' && HOST !== '' && location.hostname === HOST) { location.href = '/me'; return }
    location.reload()
  }

  /* SSO 回跳提示：?sso=unbound|failed|bound 由网关在跳转时带上 */
  try {
    var q = new URLSearchParams(location.search).get('sso')
    if (q === 'unbound') showNotice(ERRORS.sso_unbound)
    else if (q === 'failed') showError(ERRORS.sso_failed)
    else if (q === 'bound') showNotice('绑定成功，正在进入工作区…')
  } catch (e) { /* URLSearchParams 不可用时静默降级 */ }

  if (STAGE === 'totp') { try { tc.focus() } catch (e) { /* 忽略 */ } }

  form.addEventListener('submit', function (ev) {
    ev.preventDefault()
    clearError()
    busy(true)
    var url = STAGE === 'totp' ? '/api/auth/totp' : '/api/auth/login'
    var body = STAGE === 'totp'
      ? { account: acc.value, code: tc.value }
      : { account: acc.value, password: pw.value }
    fetch(url, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify(body)
    }).then(function (r) {
      return r.json().catch(function () { return {} }).then(function (j) { return { status: r.status, body: j } })
    }).then(function (res) {
      if (res.status === 200 && res.body && res.body.totp_required) {
        showNotice('密码已通过验证，请输入认证器中的 6 位动态码。')
        enterTotpStage()
        return
      }
      if (res.status === 200) {
        if (res.body && res.body.needs_2fa_enrollment) {
          showNotice(ERRORS.enrollment_required)
          busy(true)
          submit.textContent = '正在跳转…'
          setTimeout(function () { finish(res.body) }, 2500)
          return
        }
        finish(res.body)
        return
      }
      busy(false)
      showError(describe(res.status, res.body))
      if (STAGE === 'totp') { tc.value = ''; tc.focus() } else { pw.value = ''; pw.focus() }
    }).catch(function () {
      busy(false)
      showError(ERRORS.network)
    })
  })
})();
</script>
</body>
</html>
`
  return redactSecrets(html, secretValuesOf(options, sensitive))
}

/**
 * 两步验证阶段页面。等价于 renderLoginPage({ stage: 'totp' })，
 * 单独导出便于网关在「登录已过密码因子、需要动态码」时直接调用。
 */
export function renderTotpPage (options = {}) {
  return renderLoginPage({ ...options, stage: 'totp' })
}

/* ── 企业身份开通页（免邀请码注册）────────────────────────────────────── */

/**
 * 渲染「企业身份开通账号」页。
 *
 * 取消邀请码注册后，自助开通账号的唯一凭据是企业身份（企业微信/钉钉 SSO）：
 * 员工点按钮 → 跳供应商扫码 → 回调首次登录自动建号 → 直接进工作区。
 * 页面本身不收集任何凭据（无密码、无邀请码），因此没有表单提交逻辑。
 *
 * @param {object} [options]
 * @param {Array} [options.ssoProviders=[]] 已启用的第三方登录 provider 列表
 * @param {string} [options.error=''] 服务端错误文案
 * @param {string[]} [options.sensitive=[]] 需要在页面上遮蔽的敏感值
 * @returns {string} 完整 HTML 字符串
 */
export function renderRegisterPage (options = {}) {
  const { error = '', ssoProviders = [], sensitive = [] } = options
  const list = Array.isArray(ssoProviders) ? ssoProviders : []
  const items = []
  for (const raw of list) {
    const id = safeSegment(typeof raw === 'string' ? raw : raw?.id)
    if (id === '') continue
    const text = typeof raw === 'string'
      ? escapeHtml(SSO_PROVIDER_LABELS[id] ?? id)
      : escapeHtml(raw?.label ?? SSO_PROVIDER_LABELS[id] ?? id)
    items.push(`<a class="sso-btn" href="/api/auth/sso/${id}/start" rel="noopener">使用${text}账号开通</a>`)
  }
  const enrollList = items.length === 0
    ? ''
    : `<div class="sso-list" id="sso-list">
${items.join('\n')}
</div>`
  const emptyNotice = items.length === 0
    ? `<div class="info-panel" id="sso-empty" role="status">
<p style="margin:0">管理员尚未配置企业身份登录，暂时无法自助开通账号。</p>
<p style="margin:.45rem 0 0">请联系企业管理员在管理台「安全与审计 → 企业身份登录」中启用企业微信或钉钉后，再回到本页。</p>
</div>`
    : ''

  const html = `<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="color-scheme" content="light dark">
<meta name="referrer" content="same-origin">
<title>卡巴格 · 开通账号</title>
<style>${AUTH_UI_CSS}</style>
</head>
<body>
<main class="auth-shell" id="auth-root" data-expires="" data-errors="${dataJson(AUTH_ERROR_TEXT)}">
<section class="auth-card" aria-labelledby="auth-title">
<header class="auth-head">
<p class="brand">卡巴格企业平台</p>
<h1 id="auth-title">开通账号</h1>
<p class="auth-sub">使用企业身份扫码，首次登录即自动开通你的工作区账号</p>
</header>
${alertBox({ id: 'register-error', tone: 'error', role: 'alert', text: error })}
<div class="info-panel" id="enroll-guide">
<p style="margin:0">开通流程：</p>
<ul style="margin:.45rem 0 0;padding-left:1.1rem">
<li>点击下方按钮，跳转到企业微信或钉钉的扫码页面。</li>
<li>用企业身份完成扫码与授权，平台据此确认你属于本企业。</li>
<li>首次登录会自动创建你的账号与工作区，之后直接扫码进入，无需密码。</li>
</ul>
</div>
${emptyNotice}
${enrollList}
<p class="auth-foot">已有账号？<a href="/login">直接登录</a></p>
</section>
</main>
</body>
</html>
`
  return redactSecrets(html, secretValuesOf(options, sensitive))
}
