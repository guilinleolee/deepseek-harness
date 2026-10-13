/**
 * Wire vocabulary of the sentiment face (企业舆情分析): monitoring tasks,
 * captured mentions, aggregated alerts, and the module settings, persisted
 * in the theme's `_sentiment.json` sidecar. Client-safe by construction —
 * no Node or filesystem imports.
 */

import type { Branded } from '@deepseek-ai/dsh-brand'
import type { SentimentReport } from './report.ts'

/** Stable identity of one monitor task. */
export type SentimentTaskId = Branded<'SentimentTaskId'>

/** Stable identity of one captured mention. */
export type SentimentMentionId = Branded<'SentimentMentionId'>

/** Stable identity of one aggregated alert. */
export type SentimentAlertId = Branded<'SentimentAlertId'>

/** Where a mention was captured from; phase 2 covers news RSS + weibo visitor + bilibili. */
export type SentimentSource = 'rss' | 'weibo' | 'bili'

/** Every supported source, frozen for wire validation. */
export const SENTIMENT_SOURCES: readonly SentimentSource[] = ['rss', 'weibo', 'bili']

/** Chinese label of one source. */
export const SENTIMENT_SOURCE_LABELS: Readonly<Record<SentimentSource, string>> = {
  rss: '新闻 RSS',
  weibo: '微博',
  bili: 'B 站',
}

/** Monitor task groups, in picker order; a custom group rides as free text. */
export const SENTIMENT_TASK_GROUPS = ['brand', 'complaint', 'competitor', 'policy'] as const

/** Chinese label of one task group. */
export const SENTIMENT_GROUP_LABELS: Readonly<Record<(typeof SENTIMENT_TASK_GROUPS)[number], string>> = {
  brand: '品牌舆情',
  complaint: '产品投诉',
  competitor: '竞品动态',
  policy: '行业政策',
}

/** Sentiment classification of one mention. */
export type SentimentPolarity = 'pos' | 'neu' | 'neg'

/** One monitor task: keywords, sources, schedule, and its notification roles. */
export interface SentimentTask {
  readonly id: SentimentTaskId
  readonly name: string
  readonly group: string
  readonly enabled: boolean
  /** Company/brand subjects, one per entry. */
  readonly subjects: readonly string[]
  /** Keyword OR-groups; a mention matches when any group's terms all hit its text. */
  readonly keywordGroups: readonly { readonly polarity: SentimentPolarity | 'any'; readonly terms: readonly string[] }[]
  readonly sources: readonly SentimentSource[]
  /** RSS feed URLs to scan (the phase-2 source; weibo/bili sources are task-level flags consumed by later phases). */
  readonly feedUrls: readonly string[]
  /** Minimum allowed schedule; the engine clamps below 30 minutes. */
  readonly intervalMinutes: number
  readonly createdAt: string
  readonly updatedAt: string
}

/** One captured and classified mention. */
export interface SentimentMention {
  readonly id: SentimentMentionId
  readonly taskId: SentimentTaskId
  readonly source: SentimentSource
  readonly platform: string
  readonly url: string
  readonly title: string
  readonly summary: string
  readonly publishedAt: string | null
  readonly capturedAt: string
  readonly polarity: SentimentPolarity
  /** 0–1 model/lexicon confidence. */
  readonly confidence: number
  /** The evidence line the classification grounded on (null for neutral-no-hit). */
  readonly evidence: string | null
  readonly heat: { readonly likes: number; readonly comments: number; readonly shares: number } | null
  readonly author: string | null
}

/** Re-export of the stored report document (defined in the report engine). */
export type { SentimentReport } from './report.ts'

/** One aggregated alert: multiple mentions collapse onto one event row. */
export interface SentimentAlert {
  readonly id: SentimentAlertId
  readonly taskId: SentimentTaskId
  /** The clustered event key (task + leading keyword group + day). */
  readonly eventKey: string
  readonly level: 1 | 2 | 3 | 4
  readonly summary: string
  readonly reason: string
  readonly mentionIds: readonly SentimentMentionId[]
  readonly handled: boolean
  readonly createdAt: string
  readonly handledAt: string | null
}

/** Module settings, persisted with the manifest. */
export interface SentimentSettings {
  readonly negativeHeatThreshold: number
  /** Percent surge day-over-day that raises an alert. */
  readonly negativeSurgePercent: number
  readonly domainBlacklist: readonly string[]
  readonly accountBlacklist: readonly string[]
  /** Mention retention window in days; older rows are pruned on scan. */
  readonly retentionDays: number
  /** Master switch of the webhook push; channels below fire only when this is on. */
  readonly notifyEnabled: boolean
  readonly dingtalkWebhook: string | null
  readonly wecomWebhook: string | null
  /** Alert-mail recipient; sends only when the SMTP transport is configured. */
  readonly email: string | null
  /** SMTP host of the alert-mail transport; null disables the email channel. */
  readonly smtpHost: string | null
  /** SMTP port (465 implicit TLS, 587 STARTTLS typical). */
  readonly smtpPort: number
  /** SMTP username; null with `smtpPasswordRef` unset means anonymous. */
  readonly smtpUser: string | null
  /** SMTP password; stored in the 0600 manifest like the webhooks. */
  readonly smtpPassword: string | null
  /** Alert-mail sender address shown to recipients. */
  readonly smtpFrom: string | null
}

/** The `_sentiment.json` manifest document; `formatVersion 0` has no compatibility promise. */
export interface SentimentManifest {
  readonly formatVersion: 0
  readonly tasks: readonly SentimentTask[]
  readonly mentions: readonly SentimentMention[]
  readonly alerts: readonly SentimentAlert[]
  readonly settings: SentimentSettings
  /** The last generated report; null before the first generation. */
  readonly report: SentimentReport | null
}

/** Result face of reading the manifest: valid rows plus every dropped one named. */
export interface SentimentSnapshot {
  readonly tasks: readonly SentimentTask[]
  readonly mentions: readonly SentimentMention[]
  readonly alerts: readonly SentimentAlert[]
  readonly settings: SentimentSettings
  readonly problems: readonly string[]
  /** Whether a scan is currently running (single-slot, UI disables the button). */
  readonly scanning: boolean
  /** The last scan's outcome summary; null before the first scan. */
  readonly lastScan: { readonly at: string; readonly captured: number; readonly alerts: number } | null
  /** The stored report; null before the first generation. */
  readonly report: SentimentReport | null
}

/** The upsert payload of `putSentimentTask` (gateway owns timestamps). */
export interface SentimentTaskInput {
  readonly id?: SentimentTaskId
  readonly name: string
  readonly group: string
  readonly enabled: boolean
  readonly subjects: readonly string[]
  readonly keywordGroups: readonly { readonly polarity: SentimentPolarity | 'any'; readonly terms: readonly string[] }[]
  readonly sources: readonly SentimentSource[]
  readonly feedUrls: readonly string[]
  readonly intervalMinutes: number
}

/** The dashboard/statistics projection the client renders. */
export interface SentimentStats {
  readonly total: number
  readonly positive: number
  readonly neutral: number
  readonly negative: number
  readonly highRisk: number
  readonly taskCount: number
  /** Mentions per local day for the trend chart (last 14 days, oldest first). */
  readonly trend: ReadonlyArray<{ readonly day: string; readonly pos: number; readonly neu: number; readonly neg: number }>
  /** Mentions per platform, high first, capped at 8. */
  readonly platforms: ReadonlyArray<{ readonly platform: string; readonly count: number }>
}

/** Result face of one scan run. */
export interface SentimentScanResult {
  readonly captured: number
  readonly alerts: number
  readonly at: string
}
