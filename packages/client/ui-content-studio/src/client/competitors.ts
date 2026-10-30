/**
 * Browser-side configuration and pure logic for the competitors view: the
 * benchmark-account registry (localStorage), dedup/upsert semantics, the
 * account-relative heat ranking, report digests, and the catch-up check.
 * No React, no IO beyond the one localStorage namespace — everything here is
 * unit-testable, and the manifest itself lives on disk behind the gateway.
 */

import type { TopicItemInput } from '@deepseek-ai/dsh-content-topics/types'
import type {
  CompetitorHeatLevel, CompetitorManifest, CompetitorMetricSnapshot, CompetitorPlatform, CompetitorWork,
  CompetitorWorkId,
} from '@deepseek-ai/dsh-content-outputs/types'

/** localStorage namespace owned by the competitors view. */
export const COMPETITORS_STORAGE_KEY = 'dsh-content-studio.competitors.accounts'

/** Pre-alignment namespace; still read on load so existing browsers migrate. */
const COMPETITORS_LEGACY_STORAGE_KEY = 'content-studio.competitors.accounts'

/** Browser-side benchmark account. Never written to disk by this phase. */
export interface CompetitorAccount {
  /** Stable id (`acc-` prefixed). */
  id: string
  name: string
  platform: CompetitorPlatform
  /** Account homepage URL, when known. */
  homepageUrl: string
  /** Niche tags (赛道标签). */
  topics: readonly string[]
  priority: 'high' | 'medium' | 'low'
  note: string
  /** Account positioning (定位). */
  positioning: string
  /** Follower tier (粉丝量级) as free text. */
  followerTier: string
  /** Monetization path (变现方式) as free text. */
  monetization: string
  /** Collection cadence in days; a hint for the catch-up check, not a scheduler. */
  intervalDays: 1 | 3 | 7
  /** Disabled accounts drop out of the catch-up banner. */
  enabled: boolean
  /** Creation instant (ISO 8601). */
  createdAt: string
}

/** Heat verdict for one work inside its account's distribution. */
export interface CompetitorHeat {
  readonly level: CompetitorHeatLevel
  readonly score: number
}

/** Platforms the phase-one manual import supports. */
export const COMPETITOR_PLATFORMS: readonly CompetitorPlatform[] = ['xhs', 'douyin', 'wechat', 'bili', 'zhihu', 'toutiao']

/** Works ranked per heat computation window (the account's most recent ones). */
const HEAT_WINDOW = 30

/** Minimum works before a distribution can rank hot vs normal. */
const HEAT_MIN_SAMPLE = 4

/**
 * Build a stable prefixed id. `crypto.randomUUID` when available, else a
 * best-effort fallback (the id only needs uniqueness within one browser).
 * @param prefix - id prefix (`acc-`, `cw-`, `cr-`, `idea-`).
 * @returns the new id.
 */
export function newId(prefix: string): string {
  const random = typeof crypto !== 'undefined' && 'randomUUID' in crypto
    ? crypto.randomUUID()
    : `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}`
  return `${prefix}-${random}`
}

/**
 * Load the account registry from localStorage.
 * @returns the valid accounts plus whether the save surface is degraded
 *   (private mode / quota), which the UI surfaces as a warning.
 */
export function loadAccounts(): { accounts: readonly CompetitorAccount[]; degraded: boolean } {
  let raw: string | null = null
  try {
    raw = localStorage.getItem(COMPETITORS_STORAGE_KEY)
    if (raw === null) raw = localStorage.getItem(COMPETITORS_LEGACY_STORAGE_KEY)
  } catch {
    return { accounts: [], degraded: true }
  }
  if (raw === null) return { accounts: [], degraded: false }
  return { accounts: parseAccounts(raw), degraded: false }
}

/**
 * Persist the account registry.
 * @param accounts - the complete next registry.
 * @returns whether the write succeeded; a failure degrades to memory-only.
 */
export function saveAccounts(accounts: readonly CompetitorAccount[]): boolean {
  try {
    localStorage.setItem(COMPETITORS_STORAGE_KEY, JSON.stringify(accounts, null, 2))
    localStorage.removeItem(COMPETITORS_LEGACY_STORAGE_KEY)
    return true
  } catch {
    return false
  }
}

/** Structural validation for one stored or imported account. */
function isAccount(value: unknown): value is CompetitorAccount {
  if (typeof value !== 'object' || value === null) return false
  const record = value as Record<string, unknown>
  return typeof record.id === 'string' && record.id.length > 0
    && typeof record.name === 'string' && record.name.length > 0
    && COMPETITOR_PLATFORMS.includes(record.platform as CompetitorPlatform)
    && (record.homepageUrl === undefined || typeof record.homepageUrl === 'string')
    && (record.topics === undefined || (Array.isArray(record.topics) && record.topics.every(tag => typeof tag === 'string')))
    && (record.priority === undefined || record.priority === 'high' || record.priority === 'medium' || record.priority === 'low')
    && typeof record.intervalDays === 'number' && (record.intervalDays === 1 || record.intervalDays === 3 || record.intervalDays === 7)
    && typeof record.enabled === 'boolean'
    && typeof record.createdAt === 'string'
}

/** Parse stored JSON into valid accounts, dropping anything malformed. */
function parseAccounts(raw: string): readonly CompetitorAccount[] {
  let parsed: unknown
  try {
    parsed = JSON.parse(raw)
  } catch {
    return []
  }
  if (!Array.isArray(parsed)) return []
  return parsed.filter(isAccount)
}

/**
 * Import an account JSON payload (the export file's content), skipping
 * entries that duplicate an existing or in-batch name+platform pair.
 * @param json - the imported file content.
 * @param existing - the current registry.
 * @returns the merged registry plus the added and skipped counts.
 */
export function importAccounts(json: string, existing: readonly CompetitorAccount[]): {
  accounts: readonly CompetitorAccount[]
  added: number
  skipped: number
} {
  let parsed: unknown
  try {
    parsed = JSON.parse(json)
  } catch {
    return { accounts: existing, added: 0, skipped: 0 }
  }
  const candidates = Array.isArray(parsed) ? parsed.filter(isAccount) : []
  const accounts = [...existing]
  const seen = new Set(existing.map(account => duplicateKey(account)))
  let added = 0
  let skipped = 0
  for (const candidate of candidates) {
    const key = duplicateKey(candidate)
    if (seen.has(key)) {
      skipped += 1
      continue
    }
    seen.add(key)
    accounts.push({ ...candidate, id: newId('acc'), createdAt: new Date().toISOString() })
    added += 1
  }
  return { accounts, added, skipped }
}

/** Name+platform identity an import dedupes on. */
function duplicateKey(account: CompetitorAccount): string {
  return `${account.platform}::${account.name.trim()}`
}

/**
 * Export the registry as the import/export JSON payload.
 * @param accounts - the accounts to serialize.
 * @returns the pretty-printed JSON payload with a trailing newline, the exact format `importAccounts` accepts.
 */
export function exportAccounts(accounts: readonly CompetitorAccount[]): string {
  return `${JSON.stringify(accounts, null, 2)}\n`
}

/**
 * One work's interaction score: likes + 2×comments + 3×shares, with views
 * counted at 1/100 as a reach tiebreaker. Weights favor conversation over
 * applause, per the competitor-plan scoring rule.
 * @param metrics - the work's snapshots, oldest first.
 * @returns the score of the newest snapshot, or 0 without snapshots.
 */
export function interactionScore(metrics: readonly CompetitorMetricSnapshot[]): number {
  const latest = metrics.at(-1)
  if (latest === undefined) return 0
  const reach = latest.views === undefined ? 0 : Math.round(latest.views / 100)
  return latest.likes + 2 * latest.comments + 3 * latest.shares + reach
}

/**
 * Rank one account's works by account-relative heat: the interaction score
 * of the newest snapshot, compared against the account's own recent
 * distribution (≥P90 hot, ≥P50 normal, else cold). Fewer than four works
 * cannot rank, so they all read normal — cross-account absolute values are
 * never compared.
 * @param works - the account's works (any order).
 * @returns heat per work id for the ranked window; works outside the window
 *   read cold once the account has enough sample.
 */
export function heatByWork(works: readonly CompetitorWork[]): ReadonlyMap<string, CompetitorHeat> {
  const heat = new Map<string, CompetitorHeat>()
  const ranked = [...works]
    .sort((a, b) => recencyKey(b) - recencyKey(a))
    .slice(0, HEAT_WINDOW)
  const scores = ranked.map(work => interactionScore(work.metrics))
  if (ranked.length < HEAT_MIN_SAMPLE) {
    for (const work of ranked) heat.set(work.id, { level: 'normal', score: interactionScore(work.metrics) })
    return heat
  }
  const sorted = [...scores].sort((a, b) => a - b)
  const percentile = (fraction: number): number => at(sorted, Math.ceil(fraction * (sorted.length - 1)))
  const p90 = percentile(0.9)
  const p50 = percentile(0.5)
  ranked.forEach((work, index) => {
    const score = at(scores, index)
    const level: CompetitorHeatLevel = score >= p90 && score > 0 ? 'hot' : score >= p50 ? 'normal' : 'cold'
    heat.set(work.id, { level, score })
  })
  return heat
}

/** Newest-first sort key: publication instant when known, else import instant. */
function recencyKey(work: CompetitorWork): number {
  return Date.parse(work.publishedAt ?? work.importedAt)
}

/** Sort orders the works library offers. */
export type WorkSort = 'newest' | 'score' | 'collects'

/**
 * Sort the works library. `newest` is publication-first; `score` is the
 * interaction score; `collects` ranks by the saves/shares count — tutorial
 * accounts collect far more than they like, so like-only rankings hide their
 * real top works.
 * @param works - the works to sort (not mutated).
 * @param sort - the chosen order.
 * @returns the sorted copy, best first.
 */
export function sortWorks(works: readonly CompetitorWork[], sort: WorkSort): readonly CompetitorWork[] {
  const copy = [...works]
  if (sort === 'newest') return copy.sort((a, b) => recencyKey(b) - recencyKey(a))
  if (sort === 'score') return copy.sort((a, b) => interactionScore(b.metrics) - interactionScore(a.metrics))
  return copy.sort((a, b) => (b.metrics.at(-1)?.shares ?? 0) - (a.metrics.at(-1)?.shares ?? 0))
}

/** One work entry of the browser-sync export payload (see `importSyncPayload`). */
export interface SyncWorkPayload {
  readonly platformWorkId?: string
  readonly title: string
  readonly url?: string
  readonly publishedAt?: string
  readonly likes?: number
  readonly comments?: number
  readonly shares?: number
  readonly views?: number
  readonly body?: string
  /** Top comment texts harvested from the work's detail page, best-effort order. */
  readonly hotComments?: readonly string[]
}

/** The browser-sync export payload the ego-browser collector writes. */
export interface SyncPayload {
  readonly version: 1
  readonly platform: CompetitorPlatform
  readonly account: {
    readonly name: string
    readonly homepageUrl?: string
    readonly bio?: string
    readonly followers?: string
  }
  readonly works: readonly SyncWorkPayload[]
}

/** Result of applying one sync payload: manifest counts plus the matched account patch. */
export interface SyncImportResult {
  readonly manifest: CompetitorManifest
  readonly added: number
  readonly updated: number
  /** Body assets to write for synced works carrying body text or hot comments. */
  readonly assets: ReadonlyArray<{ file: string; content: string }>
  /** Registry fields the payload refreshes, keyed by the matched account id; absent when no account matched. */
  readonly accountPatch?: { accountId: string; followerTier?: string; positioning?: string }
}

/**
 * Apply one browser-sync export payload: every work entry upserts through the
 * same dedup path as manual import (title fallback included), and the account
 * named by the payload refreshes its follower tier (and positioning, only
 * when the stored one is empty). The payload is a convenience export, not a
 * trusted wire: malformed entries are skipped, not fatal.
 * @param json - the collector's JSON file content.
 * @param manifest - the current theme manifest.
 * @param accounts - the current account registry, for the name+platform match.
 * @returns the next manifest, the added/updated counts, and the account patch.
 */
export function importSyncPayload(
  json: string,
  manifest: CompetitorManifest,
  accounts: readonly CompetitorAccount[],
): SyncImportResult {
  let parsed: unknown
  try { parsed = JSON.parse(json) } catch { return { manifest, added: 0, updated: 0, assets: [] } }
  const record = parsed as Record<string, unknown>
  if (record.version !== 1 || !Array.isArray(record.works)) return { manifest, added: 0, updated: 0, assets: [] }
  const platform = COMPETITOR_PLATFORMS.includes(record.platform as CompetitorPlatform)
    ? record.platform as CompetitorPlatform
    : undefined
  const accountName = typeof record.account === 'object' && record.account !== null
    && typeof (record.account as Record<string, unknown>).name === 'string'
    ? (record.account as { name: string }).name.trim()
    : ''
  if (platform === undefined || accountName.length === 0) return { manifest, added: 0, updated: 0, assets: [] }
  const account = accounts.find(candidate => candidate.platform === platform && candidate.name.trim() === accountName)
  const payload = record as unknown as SyncPayload
  const assets: Array<{ file: string; content: string }> = []
  let next = manifest
  let added = 0
  let updated = 0
  for (const entry of payload.works) {
    if (typeof entry !== 'object' || entry === null || typeof entry.title !== 'string' || entry.title.trim().length === 0) continue
    // Works with body or comments land a body asset so the AI teardown reads
    // them; the file name is stable per platform id, so re-syncs overlay the
    // same file while a stored textFile is never downgraded.
    const hasBodyContent = (entry.body !== undefined && entry.body.trim().length > 0)
      || (entry.hotComments !== undefined && entry.hotComments.some(comment => typeof comment === 'string' && comment.trim().length > 0))
    const textFile = hasBodyContent && entry.platformWorkId !== undefined && entry.platformWorkId.trim().length > 0
      ? `sync-${entry.platformWorkId.trim()}.md`
      : undefined
    if (textFile !== undefined) {
      assets.push({ file: textFile, content: buildSyncAssetMarkdown(entry) })
    }
    const upsert = upsertWork(next, {
      accountId: account?.id ?? 'unassigned',
      accountName,
      platform,
      platformWorkId: entry.platformWorkId ?? '',
      title: entry.title.trim(),
      ...(entry.url !== undefined && entry.url.length > 0 ? { url: entry.url } : {}),
      ...(entry.publishedAt !== undefined && entry.publishedAt.length > 0 ? { publishedAt: entry.publishedAt } : {}),
      ...(textFile !== undefined ? { textFile } : {}),
      metrics: {
        t: new Date().toISOString(),
        likes: Math.max(entry.likes ?? 0, 0),
        comments: Math.max(entry.comments ?? 0, 0),
        shares: Math.max(entry.shares ?? 0, 0),
        ...(entry.views !== undefined && entry.views > 0 ? { views: Math.round(entry.views) } : {}),
      },
    })
    next = upsert.manifest
    if (upsert.updated) updated += 1
    else added += 1
  }
  const followers = typeof payload.account.followers === 'string' ? payload.account.followers.trim() : ''
  const bio = typeof payload.account.bio === 'string' ? payload.account.bio.trim() : ''
  const accountPatch = account === undefined ? undefined : {
    accountId: account.id,
    ...(followers.length > 0 ? { followerTier: followers } : {}),
    ...(account.positioning.length === 0 && bio.length > 0 ? { positioning: bio.slice(0, 120) } : {}),
  }
  const base = { manifest: next, added, updated, assets }
  return accountPatch === undefined ? base : { ...base, accountPatch }
}

/**
 * Render one synced work's body asset: the work body when the collector
 * captured it, then the harvested hot comments as a list — both are teardown
 * inputs, and the comment section doubles as the audience-insight source.
 * @param entry - the payload work entry.
 * @returns the markdown file content.
 */
export function buildSyncAssetMarkdown(entry: SyncWorkPayload): string {
  const lines = [`# ${entry.title.trim()}`, '']
  if (entry.body !== undefined && entry.body.trim().length > 0) lines.push(entry.body.trim(), '')
  const comments = (entry.hotComments ?? []).map(comment => typeof comment === 'string' ? comment.trim() : '').filter(comment => comment.length > 0)
  if (comments.length > 0) {
    lines.push('## 热门评论', '')
    for (const comment of comments) lines.push(`- ${comment}`)
    lines.push('')
  }
  return `${lines.join('\n')}\n`
}

/**
 * Upsert one manually imported work into the manifest. The dedup key is
 * `platform + accountId + platformWorkId`; an existing work keeps its id,
 * markers, analysis, and text file, and gains the new metrics snapshot.
 * A missing platform id falls back to the normalized title so re-importing
 * the same piece still dedupes.
 * @param manifest - the current manifest.
 * @param draft - the imported work's fields (id-less); omitted optional
 *   fields keep the stored values on update.
 * @returns the next manifest and whether this was an update of an existing work.
 */
export function upsertWork(
  manifest: CompetitorManifest,
  draft: Omit<CompetitorWork, 'id' | 'importedAt' | 'metrics' | 'hot' | 'favorite' | 'via' | 'analysis'> & {
    metrics: CompetitorMetricSnapshot
  },
): { manifest: CompetitorManifest; updated: boolean } {
  const titleKey = `title:${draft.title.trim()}`
  const platformWorkId = draft.platformWorkId.trim().length > 0 ? draft.platformWorkId.trim() : titleKey
  // Match the exact key first, then the title key — a re-import that learned
  // the real platform id still finds the work it originally imported by title.
  const candidateKeys = new Set([platformWorkId, titleKey])
  const existing = manifest.works.find(work =>
    work.platform === draft.platform
    && work.accountId === draft.accountId
    && candidateKeys.has(work.platformWorkId),
  )
  if (existing === undefined) {
    const work: CompetitorWork = {
      accountId: draft.accountId,
      accountName: draft.accountName,
      platform: draft.platform,
      platformWorkId,
      title: draft.title,
      ...(draft.url !== undefined ? { url: draft.url } : {}),
      ...(draft.publishedAt !== undefined ? { publishedAt: draft.publishedAt } : {}),
      ...(draft.textFile !== undefined ? { textFile: draft.textFile } : {}),
      id: newId('cw') as CompetitorWorkId,
      importedAt: new Date().toISOString(),
      metrics: [draft.metrics],
      hot: false,
      favorite: false,
      via: 'manual',
      analysis: { status: 'none' },
    }
    return { manifest: { ...manifest, works: [...manifest.works, work] }, updated: false }
  }
  // A re-import refreshes display facts but never the identity, markers,
  // analysis, or snapshots already recorded.
  const updated: CompetitorWork = {
    ...overlay(existing, {
      title: draft.title,
      accountName: draft.accountName,
      ...(draft.url !== undefined ? { url: draft.url } : {}),
      ...(draft.publishedAt !== undefined ? { publishedAt: draft.publishedAt } : {}),
      ...((existing.textFile ?? draft.textFile) !== undefined ? { textFile: existing.textFile ?? draft.textFile } : {}),
    }),
    metrics: appendSnapshot(existing.metrics, draft.metrics),
  }
  return {
    manifest: { ...manifest, works: manifest.works.map(work => (work.id === existing.id ? updated : work)) },
    updated: true,
  }
}

/**
 * Overlay optional fields onto a base object: `undefined` patch values keep
 * the stored value, present values overwrite. Keeps optional-property types
 * honest without explicit `undefined` assignments.
 * @param base - the stored object.
 * @param patch - the candidate replacement fields.
 * @returns the base with every present patch field applied.
 */
function overlay<T extends object>(base: T, patch: Partial<T>): T {
  const result = { ...base }
  for (const [key, value] of Object.entries(patch)) {
    if (value !== undefined) (result as Record<string, unknown>)[key] = value
  }
  return result
}

/** Append a snapshot only when its values differ from the newest one. */
function appendSnapshot(
  metrics: readonly CompetitorMetricSnapshot[],
  snapshot: CompetitorMetricSnapshot,
): readonly CompetitorMetricSnapshot[] {
  const latest = metrics.at(-1)
  if (latest !== undefined && latest.likes === snapshot.likes && latest.comments === snapshot.comments
    && latest.shares === snapshot.shares && latest.views === snapshot.views) return metrics
  return [...metrics, snapshot]
}

/**
 * Whether one account is due for collection: enabled, and its interval has
 * elapsed since the last recorded collection (or it never recorded one).
 * @param account - the account to check.
 * @param manifest - the theme manifest carrying `syncedAt`.
 * @param now - reference instant.
 * @returns true when the catch-up banner should name this account.
 */
export function isAccountStale(account: CompetitorAccount, manifest: CompetitorManifest, now: Date): boolean {
  if (!account.enabled) return false
  const last = manifest.syncedAt[account.id]
  if (last === undefined) return true
  const elapsed = now.getTime() - Date.parse(last)
  return !(Number.isFinite(elapsed)) || elapsed >= account.intervalDays * 24 * 60 * 60 * 1000
}

/**
 * Aggregate one account's works into the report digest: structured facts
 * only, capped so a report prompt stays inside the token budget. Raw work
 * text never enters a digest.
 * @param accountName - display name of the account.
 * @param platform - platform id.
 * @param works - the account's works.
 * @returns the digest text (≤1000 characters).
 */
export function aggregateAccountDigest(accountName: string, platform: CompetitorPlatform, works: readonly CompetitorWork[]): string {
  const analyzed = works.filter(work => work.analysis.status === 'done' && work.analysis.result !== undefined)
  const topicCounts = countTop(analyzed.flatMap(work => work.analysis.result?.topics ?? []))
  const hookCounts = countTop(analyzed.map(work => (work.analysis.result?.hookType ?? '').split(/[（(]/u)[0]?.trim() ?? ''))
  const withPublished = works.filter(work => work.publishedAt !== undefined)
  const earliest = withPublished.length > 0
    ? withPublished.map(work => work.publishedAt).filter(date => date !== undefined).sort()[0]?.slice(0, 10)
    : undefined
  const span = works.length > 1 ? spanWeeks(works) : 0
  const perWeek = span > 0 ? (works.length / span).toFixed(1) : String(works.length)
  const hotCount = works.filter(work => work.hot).length
  const lines = [
    `账号：${accountName}（平台：${platform}）`,
    `作品数：${works.length}${earliest === undefined ? '' : `，最早发布 ${earliest}`}`,
    `更新频率：约 ${perWeek} 条/周（按导入作品估算）`,
    `用户标记爆款：${hotCount} 条；拆解完成：${analyzed.length} 条`,
    `选题分布：${formatCounts(topicCounts, analyzed.length)}`,
    `钩子类型频次：${formatCounts(hookCounts, analyzed.length)}`,
    `互动量级：中位数互动分 ${median(works.map(work => interactionScore(work.metrics)))}`,
  ]
  return lines.join('\n').slice(0, 1000)
}

/**
 * Aggregate one account into the audit digest for the eight-dimension health
 * check: registry facts (follower tier, positioning, monetization) plus the
 * works-side distribution facts the audit dimensions score against — recency,
 * medians (never averages), heat ranks, save counts. Capped like the report
 * digest so the audit prompt stays inside the token budget.
 * @param account - the account under audit.
 * @param works - the account's works from the theme manifest.
 * @returns the digest text (≤1000 characters).
 */
export function aggregateAuditDigest(account: CompetitorAccount, works: readonly CompetitorWork[]): string {
  const latest = (work: CompetitorWork) => work.metrics.at(-1)
  const med = (values: readonly number[]): number => median(values)
  const heatCounts = { hot: 0, normal: 0, cold: 0 }
  for (const heat of heatByWork(works).values()) heatCounts[heat.level] += 1
  const newest = [...works].sort((a, b) => recencyKey(b) - recencyKey(a))[0]
  const daysSinceNewest = newest === undefined ? undefined
    : Math.round((Date.now() - recencyKey(newest)) / (24 * 60 * 60 * 1000))
  const lines = [
    `账号：${account.name}（平台：${account.platform}）`,
    `档案：粉丝量级 ${account.followerTier || '未填'}；定位 ${account.positioning || '未填'}；变现方式 ${account.monetization || '未填'}`,
    `作品数：${works.length}（导入估算）`,
    `互动中位数：赞 ${med(works.map(work => latest(work)?.likes ?? 0))} / 藏 ${med(works.map(work => latest(work)?.shares ?? 0))} / 评 ${med(works.map(work => latest(work)?.comments ?? 0))}`,
    `互动率代理：点赞中位数 ÷ 粉丝数（粉丝量级为文本，未折算）`,
    `账号内热度分布：爆款 ${heatCounts.hot} / 正常 ${heatCounts.normal} / 冷门 ${heatCounts.cold}（P90/P50 相对分位）`,
    `用户标记爆款：${works.filter(work => work.hot).length} 条；已拆解：${works.filter(work => work.analysis.status === 'done').length} 条`,
    `最新作品距今：${daysSinceNewest === undefined || !Number.isFinite(daysSinceNewest) ? '未知' : `${daysSinceNewest} 天`}；发布节奏：约 ${works.length > 1 ? (works.length / Math.max(spanWeeks(works), 0.1)).toFixed(1) : String(works.length)} 条/周（导入估算）`,
    `钩子类型频次：${formatCounts(countTop(works.map(work => (work.analysis.result?.hookType ?? '').split(/[（(]/u)[0]?.trim() ?? '').filter(value => value.length > 0)), works.filter(work => work.analysis.status === 'done').length)}`,
    `收藏最高：${[...works].sort((a, b) => (latest(b)?.shares ?? 0) - (latest(a)?.shares ?? 0))[0]?.title ?? '无'}`,
  ]
  return lines.join('\n').slice(0, 1000)
}

/** Count occurrences, descending, keeping at most the top eight. */
function countTop(values: readonly string[]): ReadonlyArray<readonly [string, number]> {  const counts = new Map<string, number>()
  for (const value of values) {
    const key = value.trim()
    if (key.length === 0) continue
    counts.set(key, (counts.get(key) ?? 0) + 1)
  }
  return [...counts.entries()].sort((a, b) => b[1] - a[1]).slice(0, 8)
}

/** Weeks between the newest and oldest recency keys, minimum 0.1. */
function spanWeeks(works: readonly CompetitorWork[]): number {
  const keys = works.map(recencyKey).filter(key => Number.isFinite(key))
  if (keys.length < 2) return 0
  const spanMs = Math.max(...keys) - Math.min(...keys)
  return Math.max(spanMs / (7 * 24 * 60 * 60 * 1000), 0.1)
}

/** Format a count map, stating the unanalyzed remainder when present. */
function formatCounts(counts: ReadonlyArray<readonly [string, number]>, analyzed: number): string {
  const parts = counts.map(([value, count]) => `${value} ${count}`)
  const total = counts.reduce((sum, [, count]) => sum + count, 0)
  if (analyzed > total) parts.push(`未拆解 ${analyzed - total}`)
  return parts.length > 0 ? parts.join('、') : '无数据'
}

/** Index a list with the caller's proven-range guarantee; throws on programmer error. */
function at<T>(list: readonly T[], index: number): T {
  const value = list[index]
  if (value === undefined) throw new Error(`competitors: index ${index} out of range (${list.length} entries)`)
  return value
}

/** Median of a numeric sample, rounded. */
function median(values: readonly number[]): number {
  if (values.length === 0) return 0
  const sorted = [...values].sort((a, b) => a - b)
  const middle = Math.floor(sorted.length / 2)
  const value = sorted.length % 2 === 1 ? at(sorted, middle) : (at(sorted, middle - 1) + at(sorted, middle)) / 2
  return Math.round(value)
}

/**
 * Render the topic-idea asset file for the 收录为选题 action: structured
 * YAML header (title, source, platform, description, differentiation,
 * source reference) so a later information-gathering index can pick it up.
 * @param work - the work the idea derives from.
 * @param idea - the AI-suggested differentiated topic text, when analyzed.
 * @returns the markdown file content.
 */

/**
 * Build the topic-bank upsert for one benchmark work: a `benchmark`-source
 * idea whose `refId` anchors the work id and whose snapshot keeps the title
 * and the first differentiated topic suggestion readable if the work or its
 * teardown later goes away. Idempotency lives with the caller, which checks
 * the bank for the same `refId` before putting.
 * @param work - the benchmark work being collected.
 * @param capturedAt - the capture instant, ISO 8601.
 * @returns the upsert input for the contentTopics Remote.
 */
export function competitorWorkToTopicInput(work: CompetitorWork, capturedAt: string): TopicItemInput {
  const suggestion = work.analysis.result?.migrationTopics[0] ?? null
  return {
    title: suggestion ?? work.title,
    oneLiner: suggestion,
    status: 'idea',
    source: {
      type: 'benchmark',
      refId: work.id,
      url: work.url ?? null,
      snapshot: { title: work.title, summary: suggestion, capturedAt },
    },
    tags: ['对标'],
    description: null,
    score: null,
    planDate: null,
    scheduleItemId: null,
    topicDir: null,
  }
}

/**
 * Build the topic-idea markdown file the competitor view saves for one work.
 * @param work - the source competitor work the idea came from.
 * @param idea - the differentiated-angle suggestion; falls back to the work title when absent.
 * @returns the markdown document with a `kind: topic-idea` front matter and source-attribution footer.
 */
export function buildIdeaMarkdown(work: CompetitorWork, idea: string | undefined): string {
  const lines = [
    '---',
    'kind: topic-idea',
    `title: ${JSON.stringify(idea ?? work.title)}`,
    `sourceAccount: ${JSON.stringify(work.accountName)}`,
    `platform: ${work.platform}`,
    `sourceWork: ${JSON.stringify(work.title)}`,
    `sourceWorkId: ${work.id}`,
    `createdAt: ${new Date().toISOString()}`,
    '---',
    '',
    `# 选题：${idea ?? work.title}`,
    '',
    `- 来源账号：${work.accountName}（${work.platform}）`,
    work.url === undefined ? '' : `- 原文：${work.url}`,
    '- 差异化建议：' + (idea ?? '（该作品尚未拆解，暂无 AI 差异化建议）'),
    '',
    '> 由对标账号视图收录，仅供选题参考。',
  ]
  return `${lines.join('\n')}\n`
}
