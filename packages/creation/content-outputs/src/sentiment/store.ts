/**
 * Sentiment file store: reads and writes the `_sentiment.json` sidecar
 * (tasks, mentions, alerts, settings) on every call, following the persona
 * manifest's rules — one malformed record never hides the rest, and every
 * write refuses to touch a file whose current state dropped records.
 */

import { mkdir, readFile } from 'node:fs/promises'
import { dirname } from 'node:path'
import { createHash, randomUUID } from 'node:crypto'
import { withFileLock, writeFileAtomic } from '@deepseek-ai/dsh-atomic-write'
import type {
  SentimentAlert, SentimentAlertAdjudication, SentimentAlertDelivery, SentimentAlertId, SentimentMention, SentimentPolarity, SentimentReport, SentimentSettings, SentimentSource, SentimentTask,
  SentimentTaskId, SentimentTaskInput, SentimentManifest, SentimentSnapshot,
} from './types.ts'
import { SENTIMENT_SOURCES } from './types.ts'

/** System file name of the sentiment manifest at the library root. */
export const SENTIMENT_FILENAME = '_sentiment.json'

/** Stored-shape caps enforced at the wire boundary. */
export const SENTIMENT_MAX_NAME = 100
/** Character cap of one subject / keyword term. */
export const SENTIMENT_MAX_TERM = 100
/** Cap of keyword groups per task. */
export const SENTIMENT_MAX_KEYWORD_GROUPS = 20
/** Cap of terms per keyword group. */
export const SENTIMENT_MAX_TERMS = 20
/** Cap of feed URLs per task. */
export const SENTIMENT_MAX_FEEDS = 20
/** Character cap of one feed URL. */
export const SENTIMENT_MAX_URL = 2_000
/** Character cap of a mention title/summary/author/evidence field. */
export const SENTIMENT_MAX_TEXT = 2_000
/** Cap of stored mentions (the retention pruner keeps this as a hard ceiling too). */
export const SENTIMENT_MAX_MENTIONS = 5_000
/** Cap of stored alerts. */
export const SENTIMENT_MAX_ALERTS = 500
/** Cap of stored tasks. */
export const SENTIMENT_MAX_TASKS = 50
/** Minimum schedule interval (matches the gather face's floor). */
export const SENTIMENT_MIN_INTERVAL_MINUTES = 30

const trimTerm = (term: string): string => term.trim()

/** Query parameters stripped before URL dedup (tracking and rotation noise). */
const DEDUP_STRIPPED_PARAMS = /^(utm_|spm|from|share_|scene|chksm|issp|nsukey|ref|fbclid|igshid)/iu

/**
 * Normalize one URL for dedup: drop the fragment, lowercase the host, and
 * strip tracking parameters. Unparseable strings pass through unchanged.
 */
export function normalizeSentimentUrl(url: string): string {
  try {
    const parsed = new URL(url)
    parsed.hash = ''
    parsed.hostname = parsed.hostname.toLowerCase()
    const kept = [...parsed.searchParams.entries()].filter(([key]) => !DEDUP_STRIPPED_PARAMS.test(key))
    parsed.search = ''
    for (const [key, value] of kept) parsed.searchParams.append(key, value)
    return parsed.toString()
  } catch {
    // Not a parseable URL: dedup falls back to the raw string.
    return url
  }
}

/** First dedup key of one mention: the normalized URL, scoped to its task. */
function sentimentUrlKey(taskId: string, url: string): string {
  return `${taskId}:url:${normalizeSentimentUrl(url)}`
}

/** Second dedup key: the content hash of title + summary, scoped to its task. */
function sentimentContentKey(taskId: string, title: string, summary: string | null): string {
  const text = `${title.trim()}\n${summary?.trim() ?? ''}`.slice(0, SENTIMENT_MAX_TEXT * 2)
  return `${taskId}:content:${createHash('sha256').update(text).digest('hex')}`
}

const POLARITIES: readonly SentimentPolarity[] = ['pos', 'neu', 'neg']

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null
}

function isText(value: unknown, max: number): value is string {
  return typeof value === 'string' && value.length > 0 && value.length <= max
}

function isNullableText(value: unknown, max: number): value is string | null {
  return value === null || isText(value, max)
}

function isTimestamp(value: unknown): value is string {
  return isText(value, 40)
}

function isTask(value: unknown): value is SentimentTask {
  if (!isRecord(value)) return false
  if (!isText(value.id, 64) || !isText(value.name, SENTIMENT_MAX_NAME)) return false
  if (!isText(value.group, SENTIMENT_MAX_NAME) || typeof value.enabled !== 'boolean') return false
  if (!Array.isArray(value.subjects) || value.subjects.length > 20) return false
  if (!value.subjects.every(subject => isText(subject, SENTIMENT_MAX_TERM))) return false
  if (!Array.isArray(value.keywordGroups) || value.keywordGroups.length > SENTIMENT_MAX_KEYWORD_GROUPS) return false
  for (const group of value.keywordGroups) {
    if (!isRecord(group)) return false
    if (group.polarity !== 'any' && !POLARITIES.includes(group.polarity as SentimentPolarity)) return false
    if (!Array.isArray(group.terms) || group.terms.length === 0 || group.terms.length > SENTIMENT_MAX_TERMS) return false
    if (!group.terms.every(term => isText(term, SENTIMENT_MAX_TERM))) return false
  }
  if (!Array.isArray(value.sources) || value.sources.length === 0) return false
  if (!value.sources.every(source => SENTIMENT_SOURCES.includes(source as never))) return false
  if (!Array.isArray(value.feedUrls) || value.feedUrls.length > SENTIMENT_MAX_FEEDS) return false
  if (!value.feedUrls.every(url => isText(url, SENTIMENT_MAX_URL))) return false
  if (typeof value.intervalMinutes !== 'number' || !Number.isInteger(value.intervalMinutes)) return false
  if (value.intervalMinutes < SENTIMENT_MIN_INTERVAL_MINUTES) return false
  return isTimestamp(value.createdAt) && isTimestamp(value.updatedAt)
}

function isMention(value: unknown): value is SentimentMention {
  if (!isRecord(value)) return false
  if (!isText(value.id, 64) || !isText(value.taskId, 64)) return false
  if (!SENTIMENT_SOURCES.includes(value.source as never) || !isText(value.platform, 40)) return false
  if (!isText(value.url, SENTIMENT_MAX_URL) || !isText(value.title, SENTIMENT_MAX_TEXT)) return false
  if (!isNullableText(value.summary, SENTIMENT_MAX_TEXT)) return false
  if (!(value.publishedAt === null || isTimestamp(value.publishedAt))) return false
  if (!isTimestamp(value.capturedAt) || !POLARITIES.includes(value.polarity as SentimentPolarity)) return false
  if (typeof value.confidence !== 'number' || !Number.isFinite(value.confidence) || value.confidence < 0 || value.confidence > 1) return false
  if (!isNullableText(value.evidence, SENTIMENT_MAX_TEXT) || !isNullableText(value.author, 200)) return false
  if (value.occurrences !== undefined && (typeof value.occurrences !== 'number' || !Number.isInteger(value.occurrences) || value.occurrences < 1)) return false
  if (value.heatDelta !== undefined && (typeof value.heatDelta !== 'number' || !Number.isInteger(value.heatDelta))) return false
  return value.heat === null || isRecord(value.heat)
}

function isAlert(value: unknown): value is SentimentAlert {
  if (!isRecord(value)) return false
  if (!isText(value.id, 64) || !isText(value.taskId, 64) || !isText(value.eventKey, 200)) return false
  const level = value.level
  if (level !== 1 && level !== 2 && level !== 3 && level !== 4) return false
  if (!isText(value.summary, SENTIMENT_MAX_TEXT) || !isText(value.reason, SENTIMENT_MAX_TEXT)) return false
  if (!Array.isArray(value.mentionIds) || value.mentionIds.length === 0 || value.mentionIds.length > 100) return false
  if (!value.mentionIds.every(id => isText(id, 64))) return false
  if (typeof value.handled !== 'boolean') return false
  if (!(isTimestamp(value.createdAt) && (value.handledAt === null || isTimestamp(value.handledAt)))) return false
  if (value.delivery !== undefined && value.delivery !== null && !isAlertDelivery(value.delivery)) return false
  if (value.adjudication === undefined || value.adjudication === null) return true
  if (!isRecord(value.adjudication)) return false
  const adjudication = value.adjudication
  return isText(adjudication.optimistic, SENTIMENT_MAX_TEXT)
    && isText(adjudication.cautious, SENTIMENT_MAX_TEXT)
    && isText(adjudication.conclusion, SENTIMENT_MAX_TEXT)
    && isTimestamp(adjudication.at)
}

/** Validate one stored per-channel delivery record. */
function isChannelDelivery(value: unknown): boolean {
  if (!isRecord(value)) return false
  if (value.status !== 'pending' && value.status !== 'delivered' && value.status !== 'failed') return false
  if (typeof value.attempts !== 'number' || !Number.isInteger(value.attempts) || value.attempts < 0) return false
  if (!(value.lastAt === null || isTimestamp(value.lastAt))) return false
  return value.lastError === null || isNullableText(value.lastError, SENTIMENT_MAX_TEXT)
}

function isAlertDelivery(value: unknown): value is SentimentAlertDelivery {
  return isRecord(value)
    && isChannelDelivery(value.dingtalk) && isChannelDelivery(value.wecom) && isChannelDelivery(value.email)
}

export const DEFAULT_SENTIMENT_SETTINGS: SentimentSettings = {
  negativeHeatThreshold: 500,
  negativeSurgePercent: 200,
  domainBlacklist: [],
  accountBlacklist: [],
  retentionDays: 90,
  notifyEnabled: true,
  dingtalkWebhook: null,
  wecomWebhook: null,
  email: null,
  smtpHost: null,
  smtpPort: 465,
  smtpUser: null,
  smtpPassword: null,
  smtpFrom: null,
}

function isSettings(value: unknown): value is SentimentSettings {
  if (!isRecord(value)) return false
  if (typeof value.negativeHeatThreshold !== 'number' || value.negativeHeatThreshold < 0 || value.negativeHeatThreshold > 100_000) return false
  if (typeof value.negativeSurgePercent !== 'number' || value.negativeSurgePercent < 0 || value.negativeSurgePercent > 10_000) return false
  if (!Array.isArray(value.domainBlacklist) || !value.domainBlacklist.every(d => isText(d, 200))) return false
  if (!Array.isArray(value.accountBlacklist) || !value.accountBlacklist.every(a => isText(a, 200))) return false
  if (typeof value.retentionDays !== 'number' || !Number.isInteger(value.retentionDays) || value.retentionDays < 1 || value.retentionDays > 365) return false
  if (typeof value.notifyEnabled !== 'boolean') return false
  if (value.smtpHost !== null && !isNullableText(value.smtpHost, 200)) return false
  if (typeof value.smtpPort !== 'number' || !Number.isInteger(value.smtpPort) || value.smtpPort < 1 || value.smtpPort > 65_535) return false
  if (!isNullableText(value.smtpUser, 200) || !isNullableText(value.smtpPassword, 500)) return false
  if (!isNullableText(value.smtpFrom, 200)) return false
  return isNullableText(value.dingtalkWebhook, 500) && isNullableText(value.wecomWebhook, 500) && isNullableText(value.email, 200)
}

function isReport(value: unknown): value is SentimentReport {
  if (!isRecord(value)) return false
  if (!isText(value.markdown, 100_000)) return false
  if (typeof value.degraded !== 'boolean') return false
  if (!isTimestamp(value.generatedAt)) return false
  if (!isText(value.promptVersion, 100)) return false
  const mentionCount: unknown = value.mentionCount
  const alertCount: unknown = value.alertCount
  if (!(typeof mentionCount === 'number' && Number.isInteger(mentionCount) && mentionCount >= 0
    && typeof alertCount === 'number' && Number.isInteger(alertCount) && alertCount >= 0)) return false
  if (value.ir === undefined) return true
  if (!isRecord(value.ir)) return false
  const ir = value.ir
  if (!isText(ir.template, 40)) return false
  if (!Array.isArray(ir.sections) || ir.sections.length === 0 || ir.sections.length > 12) return false
  return ir.sections.every(section => isRecord(section)
    && isText(section.key, 100) && isText(section.title, 200) && isText(section.body, 40_000))
}

/** Newest mention first; the id breaks ties so the order is total and stable. */
function compareMentions(a: SentimentMention, b: SentimentMention): number {
  if (a.capturedAt !== b.capturedAt) return a.capturedAt > b.capturedAt ? -1 : 1
  return a.id < b.id ? -1 : 1
}

/** Newest task/alert first by updatedAt/createdAt. */
function compareTasks(a: SentimentTask, b: SentimentTask): number {
  if (a.updatedAt !== b.updatedAt) return a.updatedAt > b.updatedAt ? -1 : 1
  return a.id < b.id ? -1 : 1
}

function compareAlerts(a: SentimentAlert, b: SentimentAlert): number {
  if (a.createdAt !== b.createdAt) return a.createdAt > b.createdAt ? -1 : 1
  return a.id < b.id ? -1 : 1
}

/** One stored manifest parse: `empty`, `invalid` (refuse-write), or `ok`. */
export type SentimentParse =
  | { readonly kind: 'empty' }
  | { readonly kind: 'invalid'; readonly problem: string }
  | {
    readonly kind: 'ok'
    readonly tasks: readonly SentimentTask[]
    readonly mentions: readonly SentimentMention[]
    readonly alerts: readonly SentimentAlert[]
    readonly settings: SentimentSettings
    readonly report: SentimentReport | null
    readonly problems: readonly string[]
  }

/**
 * Parse one stored manifest body. Future formats never load as current
 * records; invalid JSON is its own refuse-write state.
 */
export function parseSentimentManifest(raw: string): SentimentParse {
  if (raw.length === 0) return { kind: 'empty' }
  let parsed: unknown
  try {
    parsed = JSON.parse(raw)
  } catch {
    return { kind: 'invalid', problem: 'sentiment file is not valid JSON' }
  }
  const root = parsed as Record<string, unknown>
  if (root.formatVersion !== 0) return { kind: 'invalid', problem: `unsupported sentiment formatVersion ${String(root.formatVersion)}` }
  const problems: string[] = []
  const tasks: SentimentTask[] = []
  if (Array.isArray(root.tasks)) {
    for (const task of root.tasks) {
      if (isTask(task)) tasks.push(task)
      else problems.push(`dropped one invalid sentiment task: ${JSON.stringify(task).slice(0, 120)}`)
    }
  }
  const mentions: SentimentMention[] = []
  if (Array.isArray(root.mentions)) {
    for (const mention of root.mentions) {
      if (!isMention(mention)) {
        problems.push(`dropped one invalid sentiment mention: ${JSON.stringify(mention).slice(0, 120)}`)
        continue
      }
      // Same-version safe read: rows stored before occurrence counting read
      // as single-capture with no heat change.
      const normalized = {
        ...mention,
        ...(mention.occurrences === undefined ? { occurrences: 1 as const } : {}),
        ...(mention.heatDelta === undefined ? { heatDelta: 0 as const } : {}),
      }
      mentions.push(normalized)
    }
  }
  const alerts: SentimentAlert[] = []
  if (Array.isArray(root.alerts)) {
    for (const alert of root.alerts) {
      if (isAlert(alert)) alerts.push(alert)
      else problems.push(`dropped one invalid sentiment alert: ${JSON.stringify(alert).slice(0, 120)}`)
    }
  }
  const settings = isSettings(root.settings) ? root.settings : DEFAULT_SENTIMENT_SETTINGS
  const report = isReport(root.report) ? root.report : null
  if (root.report !== undefined && root.report !== null && report === null) {
    problems.push('dropped one invalid sentiment report')
  }
  tasks.sort(compareTasks)
  mentions.sort(compareMentions)
  alerts.sort(compareAlerts)
  return { kind: 'ok', tasks, mentions, alerts, settings, report, problems }
}

/** The empty projection every unreadable state falls back to. */
function emptySnapshot(): SentimentSnapshot {
  return {
    tasks: [], mentions: [], alerts: [], settings: DEFAULT_SENTIMENT_SETTINGS,
    problems: [], scanning: false, lastScan: null, report: null,
  }
}

/**
 * Read the manifest for the projection.
 * @param file - absolute `_sentiment.json` path; a missing file is empty.
 */
export async function readSentimentFile(file: string): Promise<SentimentSnapshot> {
  let raw: string
  try {
    raw = await readFile(file, 'utf8')
  } catch {
    return emptySnapshot()
  }
  const parsed = parseSentimentManifest(raw)
  if (parsed.kind === 'empty') return emptySnapshot()
  if (parsed.kind === 'invalid') return { ...emptySnapshot(), problems: [parsed.problem] }
  return {
    tasks: parsed.tasks,
    mentions: parsed.mentions,
    alerts: parsed.alerts,
    settings: parsed.settings,
    problems: parsed.problems,
    scanning: false,
    lastScan: null,
    report: parsed.report,
  }
}

/** Read the raw manifest inside a lock and refuse states a write would corrupt. */
async function readForWrite(file: string): Promise<Exclude<SentimentParse, { kind: 'empty' | 'invalid' }>> {
  await mkdir(dirname(file), { recursive: true, mode: 0o700 })
  let raw = ''
  try {
    raw = await readFile(file, 'utf8')
  } catch {
    // Missing file: an empty manifest is the legitimate first-write state.
  }
  const parsed = parseSentimentManifest(raw)
  if (parsed.kind === 'empty') return { kind: 'ok', tasks: [], mentions: [], alerts: [], settings: DEFAULT_SENTIMENT_SETTINGS, report: null, problems: [] }
  if (parsed.kind === 'invalid') throw new Error(`refusing to write ${SENTIMENT_FILENAME}: ${parsed.problem}`)
  if (parsed.problems.length > 0) throw new Error(`refusing to write ${SENTIMENT_FILENAME}: resolve the stored invalid entries first (${String(parsed.problems.length)} dropped)`)
  return parsed
}

async function writeManifest(
  file: string,
  tasks: readonly SentimentTask[],
  mentions: readonly SentimentMention[],
  alerts: readonly SentimentAlert[],
  settings: SentimentSettings,
  report: SentimentReport | null,
): Promise<void> {
  const manifest: SentimentManifest = { formatVersion: 0, tasks, mentions, alerts, settings, report }
  const body = `${JSON.stringify(manifest, null, 2)}\n`
  await writeFileAtomic(file, body, { mode: 0o600, dirMode: 0o700 })
}

/** Validate one upsert input into its stored shape. */
export function normalizeSentimentTaskInput(
  input: SentimentTaskInput,
  existing: SentimentTask | undefined,
  now: string,
): { task?: SentimentTask; detail?: string } {
  if (typeof input.name !== 'string' || input.name.trim().length === 0) return { detail: 'name must be a non-empty string' }
  if (input.name.length > SENTIMENT_MAX_NAME) return { detail: 'name exceeds the length cap' }
  if (typeof input.group !== 'string' || input.group.trim().length === 0 || input.group.length > SENTIMENT_MAX_NAME) return { detail: 'group must be a non-empty string within the cap' }
  if (typeof input.enabled !== 'boolean') return { detail: 'enabled must be a boolean' }
  if (!Array.isArray(input.subjects) || input.subjects.length === 0 || input.subjects.length > 20) return { detail: 'subjects must be 1-20 strings' }
  if (!input.subjects.every(s => typeof s === 'string' && s.trim().length > 0 && s.trim().length <= SENTIMENT_MAX_TERM)) return { detail: 'subjects must be non-empty strings within the term cap' }
  if (!Array.isArray(input.keywordGroups) || input.keywordGroups.length === 0 || input.keywordGroups.length > SENTIMENT_MAX_KEYWORD_GROUPS) return { detail: 'keywordGroups must be 1-20 groups' }
  for (const group of input.keywordGroups) {
    if (!isRecord(group)) return { detail: 'keywordGroups entries must be objects' }
    if (group.polarity !== 'any' && !POLARITIES.includes(group.polarity as SentimentPolarity)) return { detail: 'unknown keyword group polarity' }
    if (!Array.isArray(group.terms) || group.terms.length === 0 || group.terms.length > SENTIMENT_MAX_TERMS) return { detail: 'keyword group terms must be 1-20 strings' }
    if (!group.terms.every((term: unknown) => typeof term === 'string' && term.trim().length > 0 && term.trim().length <= SENTIMENT_MAX_TERM)) return { detail: 'keyword terms must be non-empty within the cap' }
  }
  if (!Array.isArray(input.sources) || input.sources.length === 0 || !input.sources.every(s => SENTIMENT_SOURCES.includes(s as never))) return { detail: 'unknown sentiment source' }
  if (new Set(input.sources).size !== input.sources.length) return { detail: 'sources must not repeat' }
  if (!Array.isArray(input.feedUrls) || input.feedUrls.length > SENTIMENT_MAX_FEEDS) return { detail: 'feedUrls exceed the cap' }
  if (!input.feedUrls.every(u => typeof u === 'string' && u.trim().length > 0 && u.trim().length <= SENTIMENT_MAX_URL)) return { detail: 'feedUrls must be non-empty within the cap' }
  if (typeof input.intervalMinutes !== 'number' || !Number.isInteger(input.intervalMinutes) || input.intervalMinutes < SENTIMENT_MIN_INTERVAL_MINUTES) {
    return { detail: `intervalMinutes must be an integer >= ${String(SENTIMENT_MIN_INTERVAL_MINUTES)}` }
  }

  const id = existing?.id ?? (input.id ?? (randomUUID() as SentimentTaskId))
  const keywordGroups = input.keywordGroups.map((group: SentimentTaskInput['keywordGroups'][number]) => ({
    polarity: group.polarity,
    terms: group.terms.map(trimTerm),
  }))
  const subjects = input.subjects.map((subject: string) => subject.trim())
  const task: SentimentTask = {
    id,
    name: input.name.trim(),
    group: input.group.trim(),
    enabled: input.enabled,
    subjects,
    keywordGroups,
    sources: input.sources.filter((source: SentimentSource) => SENTIMENT_SOURCES.includes(source)),
    feedUrls: input.feedUrls.map((url: string) => url.trim()),
    intervalMinutes: input.intervalMinutes,
    createdAt: existing?.createdAt ?? now,
    updatedAt: now,
  }
  return { task }
}

/** Write one full snapshot (sorted upstream). */
async function writeSnapshot(
  file: string,
  tasks: readonly SentimentTask[],
  mentions: readonly SentimentMention[],
  alerts: readonly SentimentAlert[],
  settings: SentimentSettings,
  report: SentimentReport | null,
): Promise<void> {
  const sorted = {
    tasks: [...tasks].sort(compareTasks),
    mentions: [...mentions].sort(compareMentions),
    alerts: [...alerts].sort(compareAlerts),
  }
  await writeManifest(file, sorted.tasks, sorted.mentions, sorted.alerts, settings, report)
}

/**
 * Upsert one task under a file lock; unknown-id updates reject.
 * @returns the stored task.
 */
export async function putSentimentTaskFile(
  file: string, input: SentimentTaskInput, now: string = new Date().toISOString(),
): Promise<SentimentTask> {
  return withFileLock(file, async () => {
    const state = await readForWrite(file)
    const existing = input.id === undefined ? undefined : state.tasks.find(task => task.id === input.id)
    if (input.id !== undefined && existing === undefined) throw new Error(`unknown sentiment task: ${input.id}`)
    const normalized = normalizeSentimentTaskInput(input, existing, now)
    if (normalized.task === undefined) throw new Error(`invalid sentiment task input: ${normalized.detail}`)
    const task = normalized.task
    const keptTasks = [task, ...state.tasks.filter(candidate => candidate.id !== task.id)]
    await writeSnapshot(file, keptTasks, state.mentions, state.alerts, state.settings, state.report)
    return task
  })
}

/** Remove one task and its mentions/alerts; removing an unknown id is a no-op. */
export async function deleteSentimentTaskFile(file: string, id: string): Promise<void> {
  await withFileLock(file, async () => {
    const state = await readForWrite(file)
    const nextTasks = state.tasks.filter(task => task.id !== id)
    if (nextTasks.length === state.tasks.length) return
    const keptMentions = state.mentions.filter(m => m.taskId !== id)
    const keptAlerts = state.alerts.filter(a => a.taskId !== id)
    await writeSnapshot(file, nextTasks, keptMentions, keptAlerts, state.settings, state.report)
  })
}

/** Flip one task's enabled flag; unknown ids reject. */
export async function setSentimentTaskEnabledFile(
  file: string, id: string, enabled: boolean, now: string = new Date().toISOString(),
): Promise<SentimentTask> {
  return withFileLock(file, async () => {
    const state = await readForWrite(file)
    const existing = state.tasks.find(task => task.id === id)
    if (existing === undefined) throw new Error(`unknown sentiment task: ${id}`)
    const task: SentimentTask = { ...existing, enabled, updatedAt: now }
    const keptTasks = [task, ...state.tasks.filter(candidate => candidate.id !== task.id)]
    await writeSnapshot(file, keptTasks, state.mentions, state.alerts, state.settings, state.report)
    return task
  })
}

/** Replace the settings block. */
export async function putSentimentSettingsFile(file: string, settings: SentimentSettings): Promise<void> {
  await withFileLock(file, async () => {
    const state = await readForWrite(file)
    if (!isSettings(settings)) throw new Error('invalid sentiment settings')
    await writeSnapshot(file, state.tasks, state.mentions, state.alerts, settings, state.report)
  })
}

/**
 * Append one scan batch under a file lock: dedupes mentions by normalized
 * URL and content hash within the task (a duplicate bumps the original's
 * `occurrences` instead of adding a row), prunes past the retention window
 * and hard caps, merges new alerts, and returns the post-write snapshot
 * counts.
 * @returns how many new mention rows and alerts were written.
 */
export async function appendSentimentScanFile(
  file: string,
  newMentions: readonly SentimentMention[],
  newAlerts: readonly SentimentAlert[],
): Promise<{ captured: number; alerts: number }> {
  return withFileLock(file, async () => {
    const state = await readForWrite(file)
    // Mention identity: both dedup keys map onto the row object that first
    // carried them; a duplicate bumps its `occurrences` count.
    const rows: SentimentMention[] = [...state.mentions]
    const keyOwner = new Map<string, SentimentMention>()
    for (const row of rows) {
      keyOwner.set(sentimentUrlKey(row.taskId, row.url), row)
      keyOwner.set(sentimentContentKey(row.taskId, row.title, row.summary), row)
    }
    const extra = new Map<SentimentMention, { count: number; latest: SentimentMention }>()
    for (const mention of newMentions) {
      const owner = keyOwner.get(sentimentUrlKey(mention.taskId, mention.url))
        ?? keyOwner.get(sentimentContentKey(mention.taskId, mention.title, mention.summary))
      if (owner === undefined) {
        keyOwner.set(sentimentUrlKey(mention.taskId, mention.url), mention)
        keyOwner.set(sentimentContentKey(mention.taskId, mention.title, mention.summary), mention)
        rows.push(mention)
        continue
      }
      const previous = extra.get(owner)
      extra.set(owner, { count: (previous?.count ?? 0) + 1, latest: mention })
    }
    const heatTotal = (heat: SentimentMention['heat']): number => heat === null ? 0 : heat.likes + heat.comments + heat.shares
    const counted = rows.map(row => {
      const bump = extra.get(row)
      if (bump === undefined) return row
      // A duplicate refreshes engagement: adopt the newest heat readings and
      // record the delta against the stored row (0 when either side is heat-less).
      const latestHeat = bump.latest.heat
      const heatDelta = latestHeat === null ? row.heatDelta : heatTotal(latestHeat) - heatTotal(row.heat)
      return {
        ...row,
        occurrences: row.occurrences + bump.count,
        heat: latestHeat === null ? row.heat : latestHeat,
        heatDelta,
      }
    })
    const keptMentions = counted
      .filter(m => Date.parse(m.capturedAt) >= Date.now() - (state.settings.retentionDays * 24 * 60 * 60 * 1000))
      .sort(compareMentions)
      .slice(0, SENTIMENT_MAX_MENTIONS)
    const keptAlerts = [...newAlerts, ...state.alerts]
      .sort(compareAlerts)
      .slice(0, SENTIMENT_MAX_ALERTS)
    await writeSnapshot(file, state.tasks, keptMentions, keptAlerts, state.settings, state.report)
    return { captured: newMentions.length - [...extra.values()].reduce((sum, entry) => sum + entry.count, 0), alerts: newAlerts.length }
  })
}

/**
 * Persist one batch of alert push-delivery records under a file lock.
 * Unknown ids are skipped (the alert may have been pruned mid-push);
 * updates with no matching alert write nothing.
 */
export async function putSentimentAlertDeliveriesFile(
  file: string,
  updates: readonly { readonly id: SentimentAlertId; readonly delivery: SentimentAlertDelivery }[],
): Promise<void> {
  if (updates.length === 0) return
  await withFileLock(file, async () => {
    const state = await readForWrite(file)
    const byId = new Map(updates.map(update => [update.id, update.delivery]))
    const nextAlerts = state.alerts.map(alert => {
      const delivery = byId.get(alert.id)
      return delivery === undefined ? alert : { ...alert, delivery }
    })
    if (nextAlerts.every((alert, index) => alert === state.alerts[index])) return
    await writeSnapshot(file, state.tasks, state.mentions, nextAlerts, state.settings, state.report)
  })
}

/** Mark one alert handled. Unknown ids reject. */
export async function handleSentimentAlertFile(file: string, id: string, now: string = new Date().toISOString()): Promise<void> {  await withFileLock(file, async () => {
    const state = await readForWrite(file)
    const alert = state.alerts.find(a => a.id === id)
    if (alert === undefined) throw new Error(`unknown sentiment alert: ${id}`)
    const next: SentimentAlert = { ...alert, handled: true, handledAt: now }
    await writeSnapshot(file, state.tasks, state.mentions, [next, ...state.alerts.filter(a => a.id !== id)], state.settings, state.report)
  })
}

/**
 * Attach one dual-perspective adjudication to one alert under a file lock;
 * unknown ids reject and a later run replaces the earlier verdict.
 * @returns the updated alert.
 */
export async function putSentimentAlertAdjudicationFile(
  file: string, id: string, adjudication: SentimentAlertAdjudication,
): Promise<SentimentAlert> {
  return withFileLock(file, async () => {
    const state = await readForWrite(file)
    const alert = state.alerts.find(a => a.id === id)
    if (alert === undefined) throw new Error(`unknown sentiment alert: ${id}`)
    if (!isText(adjudication.optimistic, SENTIMENT_MAX_TEXT)
      || !isText(adjudication.cautious, SENTIMENT_MAX_TEXT)
      || !isText(adjudication.conclusion, SENTIMENT_MAX_TEXT)
      || !isTimestamp(adjudication.at)) throw new Error('invalid sentiment alert adjudication')
    const next: SentimentAlert = { ...alert, adjudication }
    await writeSnapshot(file, state.tasks, state.mentions, [next, ...state.alerts.filter(a => a.id !== id)], state.settings, state.report)
    return next
  })
}

/**
 * Store one generated report under a file lock, replacing any previous one
 * (the manifest keeps the newest report only, like the scan summary).
 * @returns the stored report.
 */
export async function putSentimentReportFile(file: string, report: SentimentReport): Promise<SentimentReport> {
  await withFileLock(file, async () => {
    const state = await readForWrite(file)
    await writeSnapshot(file, state.tasks, state.mentions, state.alerts, state.settings, report)
  })
  return report
}
