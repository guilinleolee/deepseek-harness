#!/usr/bin/env node
/**
 * browser-automation — load a page, report what actually happened.
 *
 * Text-first by design: console errors and failed requests catch most breakage
 * and cost almost nothing, where a screenshot is expensive and usually only
 * settles layout questions.
 */
import { createRequire } from 'node:module'
import { readdirSync, existsSync } from 'node:fs'
import { homedir } from 'node:os'
import { join } from 'node:path'

/**
 * Never hardcode the extension version directory — it is rewritten on every
 * update, which is exactly how the CLI shim breaks when something pins it.
 * Glob and take the highest version present.
 */
function resolveChromium() {
  const roots = []
  for (const base of [
    join(homedir(), '.vscode-server/extensions'),
    join(homedir(), '.vscode/extensions'),
  ]) {
    if (!existsSync(base)) continue
    const dirs = readdirSync(base)
      .filter((d) => d.startsWith('danielsanmedium.dscodegpt-'))
      .sort((a, b) =>
        a.localeCompare(b, undefined, { numeric: true, sensitivity: 'base' }),
      )
    const newest = dirs[dirs.length - 1]
    if (newest) roots.push(join(base, newest, 'standalone') + '/')
  }
  roots.push('/home/mike/src/codegpt/codegpt-nextjs/', process.cwd() + '/')
  for (const root of roots) {
    try {
      const mod = createRequire(root)('patchright')
      const chromium = mod?.chromium ?? mod?.default?.chromium
      if (chromium) return { chromium, root }
    } catch {}
  }
  throw new Error(
    'Could not resolve patchright. Checked:\n  ' + roots.join('\n  '),
  )
}

const args = process.argv.slice(2)
const url = args.find((a) => !a.startsWith('--'))
const flag = (n) => {
  const i = args.indexOf(n)
  return i === -1 ? undefined : args[i + 1]
}
if (!url) {
  console.error(
    'usage: browser.mjs <url> [--snapshot [--full]] [--wait sel] [--eval js]' +
      ' [--script f] [--screenshot p] [--timeout ms]',
  )
  process.exit(2)
}
const timeout = Number(flag('--timeout') ?? 30000)

const { chromium, root } = resolveChromium()
const browser = await chromium.launch({
  headless: true,
  channel: 'chromium',
  args: ['--no-sandbox', '--disable-dev-shm-usage'],
})
const ctx = await browser.newContext({ locale: 'en-US' })
const page = await ctx.newPage()

const consoleMsgs = []
const failures = []
page.on('console', (m) => {
  if (m.type() === 'error' || m.type() === 'warning') {
    consoleMsgs.push(`[${m.type()}] ${m.text().slice(0, 300)}`)
  }
})
page.on('pageerror', (e) => consoleMsgs.push(`[uncaught] ${String(e).slice(0, 300)}`))
/**
 * Third-party analytics/ads are blocked in most environments and drown the
 * signal — a first run against the CodeGPT sidebar reported 8 "failures", 6 of
 * which were doubleclick and google-analytics beacons. Only same-origin and
 * unknown hosts are worth the reader's attention.
 */
const NOISE = /(^|\.)(google|googletagmanager|google-analytics|doubleclick|facebook|segment|sentry|posthog|mixpanel)\./
const noisy = (u) => { try { return NOISE.test(new URL(u).hostname) } catch { return false } }
page.on('requestfailed', (r) => {
  if (!noisy(r.url())) failures.push(`${r.failure()?.errorText ?? 'failed'} ${r.url().slice(0, 140)}`)
})
page.on('response', (r) => {
  if (r.status() >= 400 && !noisy(r.url())) failures.push(`HTTP ${r.status()} ${r.url().slice(0, 140)}`)
})

const t0 = Date.now()
let status = 0
let navError = null
try {
  const resp = await page.goto(url, { waitUntil: 'domcontentloaded', timeout })
  status = resp?.status() ?? 0
  const wait = flag('--wait')
  if (wait) await page.waitForSelector(wait, { timeout })
  /**
   * Wait for CONTENT, not for a fixed delay. A flat 1200ms sleep reported
   * bodyChars 0 on one run of the CodeGPT sidebar and 169 on the next — same
   * URL, same build. A client-rendered app that is merely slow is
   * indistinguishable from one that is broken unless you actually wait for it.
   */
  await page
    .waitForFunction(() => (document.body?.innerText || '').trim().length > 0, {
      timeout: Math.min(timeout, 15000),
    })
    .catch(() => {})
} catch (e) {
  navError = String(e).split('\n')[0]
}


/**
 * Accessibility snapshot with clickable refs.
 *
 * WHY REFS. Driving a page by CSS selector means AUTHORING a selector from a
 * DOM you cannot see, and a selector that matches nothing fails exactly like an
 * element that is absent — the single most expensive failure mode in practice.
 * A snapshot that hands back `@e7 button "Run"` removes the authoring step: you
 * click what the page says is there.
 *
 * Rolled by hand because patchright 1.61's ariaSnapshot() has no refs —
 * `{ref: true}` returns the identical string, and `_snapshotForAI` (what
 * Playwright's own MCP server uses) is not exposed. The structure ariaSnapshot
 * gives is still the best readable view of the page, so `full` returns that
 * instead; refs are for acting, the aria tree is for reading.
 *
 * The ref is stamped as a data attribute IN the page, so it dies on navigation
 * or a re-render. That is why re-snapshotting after anything that changes the
 * page is part of the contract rather than an optimisation.
 */
const REF_ATTR = 'data-ab-ref'
const MAX_SNAPSHOT_CHARS = 15000

const snapshotWithRefs = async (page, { full = false } = {}) => {
  if (full) {
    const aria = await page.locator('body').ariaSnapshot().catch(() => '')
    return aria.length > MAX_SNAPSHOT_CHARS
      ? aria.slice(0, MAX_SNAPSHOT_CHARS) + `\n… [truncated at ${MAX_SNAPSHOT_CHARS} chars]`
      : aria
  }

  return await page.evaluate(
    ({ attr, cap }) => {
      const INTERACTIVE =
        'button, a[href], input, select, textarea, summary, [contenteditable="true"],' +
        '[role=button], [role=link], [role=checkbox], [role=radio], [role=tab],' +
        '[role=menuitem], [role=option], [role=switch], [role=textbox], [role=combobox]'

      // Accessible name, in roughly the order the accname spec resolves it.
      // Deliberately not a full implementation — enough that a human-readable
      // label comes out for the things one actually clicks.
      const nameOf = (el) => {
        const byLabelled = el.getAttribute('aria-labelledby')
        if (byLabelled) {
          const t = byLabelled
            .split(/\s+/)
            .map((id) => document.getElementById(id)?.innerText || '')
            .join(' ')
            .trim()
          if (t) return t
        }
        const aria = el.getAttribute('aria-label')
        if (aria?.trim()) return aria.trim()
        if (el.id) {
          const lbl = document.querySelector(`label[for="${CSS.escape(el.id)}"]`)
          if (lbl?.innerText?.trim()) return lbl.innerText.trim()
        }
        const own = (el.innerText || '').replace(/\s+/g, ' ').trim()
        if (own) return own
        for (const a of ['placeholder', 'title', 'alt', 'value', 'name']) {
          const v = el.getAttribute(a)
          if (v?.trim()) return v.trim()
        }
        // Icon-only controls have no text and no label — and they are exactly
        // the ones a name-based locator cannot find, so anything that
        // distinguishes them is worth more here than elsewhere.
        const inner = el.querySelector('[aria-label], img[alt], svg[data-icon], [data-testid]')
        const hint =
          inner?.getAttribute('aria-label') ||
          inner?.getAttribute('alt') ||
          inner?.getAttribute('data-icon') ||
          inner?.getAttribute('data-testid')
        if (hint?.trim()) return hint.trim()
        return ''
      }

      const roleOf = (el) => {
        const explicit = el.getAttribute('role')
        if (explicit) return explicit
        const tag = el.tagName.toLowerCase()
        if (tag === 'a') return 'link'
        if (tag === 'input') return el.type === 'checkbox' || el.type === 'radio' ? el.type : 'textbox'
        if (tag === 'textarea') return 'textbox'
        return tag
      }

      // Clear stale refs so numbering restarts and a dead ref cannot resolve.
      for (const old of document.querySelectorAll(`[${attr}]`)) old.removeAttribute(attr)

      const lines = []
      let n = 0
      for (const el of document.querySelectorAll(INTERACTIVE)) {
        const r = el.getBoundingClientRect()
        // Zero-area or display:none elements are not clickable and would only
        // pad the list; an offscreen-but-scrollable one still counts.
        if (r.width === 0 || r.height === 0) continue
        const style = getComputedStyle(el)
        if (style.visibility === 'hidden' || style.display === 'none') continue

        const ref = `e${++n}`
        el.setAttribute(attr, ref)
        const name = nameOf(el).slice(0, 80)
        const state = [
          el.disabled ? 'disabled' : '',
          el.getAttribute('aria-checked') === 'true' || el.checked ? 'checked' : '',
          el.getAttribute('aria-expanded') === 'true' ? 'expanded' : '',
          // The tell that a nameless button opens something.
          el.getAttribute('aria-haspopup') ? `haspopup=${el.getAttribute('aria-haspopup')}` : '',
        ]
          .filter(Boolean)
          .join(' ')
        lines.push(`@${ref} ${roleOf(el)}${name ? ` "${name}"` : ''}${state ? ` [${state}]` : ''}`)
        if (lines.join('\n').length > cap) {
          lines.push(`… [truncated at ${cap} chars — pass full:true or narrow the page]`)
          break
        }
      }
      return lines.join('\n')
    },
    { attr: REF_ATTR, cap: MAX_SNAPSHOT_CHARS },
  )
}

/** Resolve a `@e3` (or bare `e3`) ref to a locator. */
const byRef = (page, ref) => page.locator(`[${REF_ATTR}="${String(ref).replace(/^@/, '')}"]`)

const info = await page
  .evaluate(() => ({
    title: document.title || '',
    bodyChars: (document.body?.innerText || '').trim().length,
    head: (document.body?.innerText || '').replace(/\s+/g, ' ').trim().slice(0, 200),
  }))
  .catch(() => ({ title: '', bodyChars: 0, head: '' }))

/**
 * Script mode. The useful QA actions are sequences — click, wait, assert — and a
 * fixed set of --click/--type flags would be a worse Playwright than Playwright.
 * The file default-exports async (page) => result; we own the browser, the
 * reporting and the teardown.
 */
let scriptResult
const scriptPath = flag('--script')
if (scriptPath) {
  try {
    const mod = await import(scriptPath.startsWith('/') ? scriptPath : `${process.cwd()}/${scriptPath}`)
    /**
     * Second argument: ref-based helpers. `page` stays first and unchanged, so
     * every script written before these existed keeps working.
     */
    const ui = {
      snapshot: (opts) => snapshotWithRefs(page, opts),
      ref: (r) => byRef(page, r),
      click: (r, opts) => byRef(page, r).click(opts),
      fill: (r, text, opts) => byRef(page, r).fill(text, opts),
      text: (r) => byRef(page, r).innerText(),
    }
    scriptResult = await (mod.default ?? mod.run)(page, ui)
  } catch (e) {
    scriptResult = `SCRIPT ERROR: ${String(e?.stack ?? e).split('\n').slice(0, 4).join(' | ')}`
  }
}

let evalResult
const expr = flag('--eval')
if (expr) {
  try {
    evalResult = await page.evaluate(`(() => (${expr}))()`)
  } catch (e) {
    evalResult = `EVAL ERROR: ${String(e).split('\n')[0]}`
  }
}
let snapshotOut
if (args.includes('--snapshot')) {
  snapshotOut = await snapshotWithRefs(page, { full: args.includes('--full') }).catch(
    (e) => `SNAPSHOT ERROR: ${String(e).split('\n')[0]}`,
  )
}

const shot = flag('--screenshot')
if (shot) await page.screenshot({ path: shot, fullPage: true }).catch(() => {})

console.log(`url        ${url}`)
console.log(`http       ${status}${navError ? `  NAV ERROR: ${navError}` : ''}`)
console.log(`load       ${Date.now() - t0}ms`)
console.log(`title      ${JSON.stringify(info.title)}`)
console.log(`bodyChars  ${info.bodyChars}`)
console.log(`patchright ${root}`)
if (info.head) console.log(`text       ${info.head}`)
if (expr) console.log(`eval       ${JSON.stringify(evalResult)}`)
if (scriptPath) console.log(`script     ${JSON.stringify(scriptResult, null, 1)}`)
if (shot) console.log(`screenshot ${shot}`)
if (snapshotOut !== undefined) console.log(`\nsnapshot:\n${snapshotOut}`)
console.log(`\nconsole errors/warnings (${consoleMsgs.length}):`)
for (const m of consoleMsgs.slice(0, 15)) console.log(`  ${m}`)
console.log(`\nrequests failed (${failures.length}):`)
for (const f of [...new Set(failures)].slice(0, 15)) console.log(`  ${f}`)

await browser.close()
process.exit(navError ? 1 : 0)
