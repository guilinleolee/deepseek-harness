/**
 * The sentiment alert push: when a scan lands new unhandled alerts, the
 * gateway posts one text message per configured webhook channel (Dingtalk
 * group robot, WeCom group robot — both public plain-JSON protocols) and,
 * when the SMTP transport is configured, one digest email. Push is
 * best-effort by design: the alerts are already persisted, so a channel
 * failure degrades to a console note and never fails the scan.
 */

import type { SentimentAlert, SentimentAlertChannelDelivery, SentimentAlertDelivery, SentimentPushChannelOutcome, SentimentPushRoundResult, SentimentSettings, SentimentTask } from './types.ts'
import type SMTPTransport from 'nodemailer/lib/smtp-transport'

/** Wire aliases: the push vocabulary is declared on the public type subpath. */
export type PushChannelOutcome = SentimentPushChannelOutcome
export type PushRoundResult = SentimentPushRoundResult

/** Deadline of one webhook POST; a slow IM endpoint must not pin the scan. */
export const SENTIMENT_PUSH_TIMEOUT_MS = 10_000

/** Alerts pushed per scan, most severe first (cost and noise bound). */
export const SENTIMENT_PUSH_ALERT_CAP = 5

/** Attempts per channel before a delivery is terminal `failed`. */
export const SENTIMENT_PUSH_MAX_ATTEMPTS = 5

/** Minimum gap between two delivery attempts of one channel (retry cooldown). */
export const SENTIMENT_PUSH_RETRY_COOLDOWN_MS = 10 * 60_000

/** Injection face for tests: the fetch implementation defaults to the global one. */
export interface PushDeps {
  readonly fetchImpl?: typeof fetch
  readonly now?: () => Date
  /** The mail transport factory; defaults to nodemailer's createTransport. */
  readonly createTransport?: (options: unknown) => { sendMail: (mail: unknown) => Promise<unknown> }
}

/** Level 1 is the most severe; sort ascending so the worst alerts push first. */
function compareByLevel(a: SentimentAlert, b: SentimentAlert): number {
  return a.level - b.level || (a.createdAt < b.createdAt ? -1 : 1)
}

/**
 * Format the push message for one scan's new alerts: one line per alert,
 * severity first, with the task name and the alert summary.
 * @param alerts - the scan's new alerts (any order).
 * @param tasks - the stored tasks (id → name lookup).
 * @param at - the scan instant.
 * @returns the plain-text message body.
 */
export function formatAlertMessage(alerts: readonly SentimentAlert[], tasks: readonly SentimentTask[], at: string): string {
  const taskName = (id: string): string => tasks.find(task => task.id === id)?.name ?? id
  const lines = [
    `【企业舆情告警】${at.slice(0, 16).replace('T', ' ')} 新增 ${String(alerts.length)} 条：`,
    ...[...alerts].sort(compareByLevel).slice(0, SENTIMENT_PUSH_ALERT_CAP)
      .map(alert => `L${String(alert.level)} ${taskName(alert.taskId)}：${alert.summary}`),
  ]
  if (alerts.length > SENTIMENT_PUSH_ALERT_CAP) lines.push(`（其余 ${String(alerts.length - SENTIMENT_PUSH_ALERT_CAP)} 条见工作台告警中心）`)
  return lines.join('\n')
}

/**
 * POST one text message to a Dingtalk group robot webhook.
 * @returns null on success, else the failure message.
 */
export async function pushDingtalk(url: string, message: string, deps: PushDeps = {}): Promise<string | null> {
  return postText(url, { msgtype: 'text', text: { content: message } }, deps)
}

/**
 * POST one text message to a WeCom group robot webhook.
 * @returns null on success, else the failure message.
 */
export async function pushWecom(url: string, message: string, deps: PushDeps = {}): Promise<string | null> {
  return postText(url, { msgtype: 'text', text: { content: message } }, deps)
}

/** Shared webhook POST: timeout, non-2xx rejection, error stringification. */
async function postText(url: string, body: unknown, deps: PushDeps): Promise<string | null> {
  try {
    const response = await (deps.fetchImpl ?? fetch)(url, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(SENTIMENT_PUSH_TIMEOUT_MS),
    })
    if (!response.ok) return `HTTP ${String(response.status)}`
    return null
  } catch (error) {
    return error instanceof Error ? error.message : String(error)
  }
}

/**
 * Send one digest email through the configured SMTP transport. Implicit TLS
 * on port 465, STARTTLS otherwise; a missing host/recipient/password means
 * the channel is not configured and sends nothing.
 * @returns null on success, else the failure message.
 */
export async function pushEmail(
  settings: SentimentSettings,
  message: string,
  deps: PushDeps = {},
): Promise<string | null> {
  if (settings.smtpHost === null || settings.email === null || settings.smtpPassword === null) return null
  try {
    const nodemailer = await import('nodemailer')
    const options: SMTPTransport.Options = {
      host: settings.smtpHost,
      port: settings.smtpPort,
      secure: settings.smtpPort === 465,
      ...(settings.smtpUser === null ? {} : { auth: { user: settings.smtpUser, pass: settings.smtpPassword } }),
    }
    const transport = deps.createTransport === undefined
      ? nodemailer.createTransport(options)
      : deps.createTransport(options)
    await transport.sendMail({
      from: settings.smtpFrom ?? settings.email,
      to: settings.email,
      subject: '企业舆情告警',
      text: message,
    })
    return null
  } catch (error) {
    return error instanceof Error ? error.message : String(error)
  }
}

/**
 * Run one push round over the configured channels. Every configured channel
 * fires exactly once per scan regardless of alert count (one digest message),
 * and `notifyEnabled` gates the whole round.
 * @param settings - the module settings (switch + webhook URLs + SMTP).
 * @param alerts - the scan's new alerts; empty means no message at all.
 * @param tasks - the stored tasks.
 * @param at - the scan instant.
 * @returns per-channel outcomes (`attempted: false` = disabled, unconfigured, or nothing to send).
 */
export async function pushAlertRound(
  settings: SentimentSettings,
  alerts: readonly SentimentAlert[],
  tasks: readonly SentimentTask[],
  at: string,
  deps: PushDeps = {},
): Promise<PushRoundResult> {
  const skipped: PushChannelOutcome = { attempted: false, error: null }
  if (!settings.notifyEnabled || alerts.length === 0) return { dingtalk: skipped, wecom: skipped, email: skipped }
  const message = formatAlertMessage(alerts, tasks, at)
  const [dingtalk, wecom, email] = await Promise.all([
    settings.dingtalkWebhook !== null ? pushDingtalk(settings.dingtalkWebhook, message, deps) : Promise.resolve(null),
    settings.wecomWebhook !== null ? pushWecom(settings.wecomWebhook, message, deps) : Promise.resolve(null),
    pushEmail(settings, message, deps),
  ])
  return {
    dingtalk: settings.dingtalkWebhook === null ? skipped : { attempted: true, error: dingtalk },
    wecom: settings.wecomWebhook === null ? skipped : { attempted: true, error: wecom },
    // The email channel is configured only with host + recipient + password all present.
    email: settings.smtpHost === null || settings.email === null || settings.smtpPassword === null
      ? skipped
      : { attempted: true, error: email },
  }
}

/** The initial delivery record of a channel: not yet attempted. */
export function freshChannelDelivery(): SentimentAlertChannelDelivery {
  return { status: 'pending', attempts: 0, lastAt: null, lastError: null }
}

/** The initial per-channel delivery record set of a fresh alert. */
export function freshAlertDelivery(): SentimentAlertDelivery {
  return { dingtalk: freshChannelDelivery(), wecom: freshChannelDelivery(), email: freshChannelDelivery() }
}

/**
 * Advance one channel's delivery record with one round outcome: an
 * unattempted channel keeps its record, a success turns `delivered`, and a
 * failure counts the attempt and stays `pending` until the cap makes it
 * terminal `failed`.
 */
export function advanceChannelDelivery(
  current: SentimentAlertChannelDelivery,
  outcome: PushChannelOutcome,
  nowIso: string,
): SentimentAlertChannelDelivery {
  if (!outcome.attempted) return current
  // Terminal `failed` stays put; the cap is only reset by a new scan event.
  if (current.status === 'failed') return current
  if (outcome.error === null) return { status: 'delivered', attempts: current.attempts + 1, lastAt: nowIso, lastError: null }
  const attempts = current.attempts + 1
  return attempts >= SENTIMENT_PUSH_MAX_ATTEMPTS
    ? { status: 'failed', attempts, lastAt: nowIso, lastError: outcome.error }
    : { status: 'pending', attempts, lastAt: nowIso, lastError: outcome.error }
}

/**
 * Whether one channel is due for a retry: not delivered or terminally
 * failed, under the attempt cap, and past the cooldown since the last try
 * (a never-attempted channel is always due).
 */
export function isChannelRetryDue(current: SentimentAlertChannelDelivery, now: Date): boolean {
  if (current.status !== 'pending' || current.attempts >= SENTIMENT_PUSH_MAX_ATTEMPTS) return false
  if (current.lastAt === null) return true
  return now.getTime() - Date.parse(current.lastAt) >= SENTIMENT_PUSH_RETRY_COOLDOWN_MS
}

/**
 * Whether one alert should join the next retry round: every stored channel
 * is due. Alerts without a delivery record predate tracking and never retry.
 */
export function isAlertRetryDue(alert: SentimentAlert, now: Date): boolean {
  if (alert.handled || alert.delivery === undefined || alert.delivery === null) return false
  return isChannelRetryDue(alert.delivery.dingtalk, now)
    || isChannelRetryDue(alert.delivery.wecom, now)
    || isChannelRetryDue(alert.delivery.email, now)
}

/**
 * Advance one alert's delivery record with one round's outcomes, starting
 * from the fresh record when the alert carries none.
 */
export function advanceAlertDelivery(
  alert: SentimentAlert,
  round: PushRoundResult,
  nowIso: string,
): SentimentAlertDelivery {
  const base = alert.delivery ?? freshAlertDelivery()
  return {
    dingtalk: advanceChannelDelivery(base.dingtalk, round.dingtalk, nowIso),
    wecom: advanceChannelDelivery(base.wecom, round.wecom, nowIso),
    email: advanceChannelDelivery(base.email, round.email, nowIso),
  }
}

/**
 * Send one test message through every configured channel, regardless of the
 * `notifyEnabled` switch (the point is to verify the configuration).
 * @returns per-channel outcomes; unconfigured channels are `attempted: false`.
 */
export async function pushTestRound(settings: SentimentSettings, deps: PushDeps = {}): Promise<PushRoundResult> {
  const message = '【企业舆情告警】这是一条测试推送。收到即表示该渠道配置可用。'
  const [dingtalk, wecom, email] = await Promise.all([
    settings.dingtalkWebhook !== null ? pushDingtalk(settings.dingtalkWebhook, message, deps) : Promise.resolve(null),
    settings.wecomWebhook !== null ? pushWecom(settings.wecomWebhook, message, deps) : Promise.resolve(null),
    pushEmail(settings, message, deps),
  ])
  const skipped: PushChannelOutcome = { attempted: false, error: null }
  return {
    dingtalk: settings.dingtalkWebhook === null ? skipped : { attempted: true, error: dingtalk },
    wecom: settings.wecomWebhook === null ? skipped : { attempted: true, error: wecom },
    email: settings.smtpHost === null || settings.email === null || settings.smtpPassword === null
      ? skipped
      : { attempted: true, error: email },
  }
}
