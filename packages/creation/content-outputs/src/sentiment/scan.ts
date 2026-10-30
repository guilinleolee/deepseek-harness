/**
 * The sentiment scan engine: one run fetches every enabled task's RSS feeds
 * through the shared gather fetcher, filters entries by the task's keyword
 * groups, classifies matches with a two-stage pipeline (local lexicon presale
 * → batched LLM refinement for the ambiguous), aggregates negative matches
 * into deduplicated alerts, and hands the batch back for persistence. The
 * weibo/bili sources run one LLM keyword-expansion pass per task per day
 * (the search terms real posters use, degrading to the raw subjects) and
 * drill one page of comments behind the hottest matched entries — the
 * comment layer is where the sentiment actually lives. The fetch happens
 * exclusively server-side; nothing here is a scraper — RSS feeds and the
 * public visitor endpoints are the phase-2 sources by design (see the
 * 2026-10-07 research).
 */

import type { Context } from '@deepseek-ai/cordis'
import { randomUUID } from 'node:crypto'
import type {
  SentimentAlert, SentimentAlertId, SentimentMention, SentimentMentionId, SentimentPolarity,
  SentimentScanResult, SentimentSettings, SentimentSource, SentimentTask,
} from './types.ts'
import { fetchFeedDocument } from '../gather/feed.ts'
import { htmlToText } from '../gather/sanitize.ts'
import { streamLlmText, type AiCallPolicy } from '../gather/ai.ts'
import {
  fetchBiliComments, fetchBiliVideos, fetchWeiboComments, fetchWeiboSearch, type SourceEntry,
} from './sources.ts'
import { expandTaskTerms, SENTIMENT_EXPAND_SEARCH_TERMS } from './expand.ts'

/** Timeout reason code carried by aborted sentiment LLM calls. */
export const SENTIMENT_AI_TIMEOUT_CODE = 'SENTIMENT_AI_TIMEOUT'

/** Prompt version of the sentiment refinement face. */
export const SENTIMENT_REFINE_PROMPT_VERSION = 'sentiment-refine@1'

/** Character cap of one mention's text handed to the model. */
const SENTIMENT_LLM_INPUT_CAP = 800

/** Entries read per feed per scan. */
const ENTRIES_PER_FEED_CAP = 30

/** At most this many mentions get LLM refinement per scan (cost bound). */
export const SENTIMENT_LLM_BATCH_CAP = 12

/** At most this many comment pages are drilled per task per source per round (cost bound). */
export const SENTIMENT_COMMENT_DRILLDOWN_CAP = 2

/** Alerts at this level or higher (more severe) trigger the depth round. */
export const SENTIMENT_DEPTH_ALERT_LEVEL = 2

/** Extra search terms consumed by the depth round per source. */
export const SENTIMENT_EXPAND_DEPTH_TERMS = 3

const REFINE_SYSTEM_PROMPT = [
  '你是企业舆情分析助手。对给定的内容条目判断情感倾向并给出依据。',
  '要求：',
  '- 只输出一个 JSON 对象，形如 {"polarity":"pos|neu|neg","confidence":0.85,"evidence":"不超过 60 字的依据摘录"}；',
  '- polarity 取值：pos（正面）、neu（中性）、neg（负面）；',
  '- evidence 必须是原文中支撑判断的短语，不要输出占位描述；',
  '- 不要输出其他任何文字。',
].join('\n')

/** The local lexicon: fast, free, and the first stage of the two-stage pipeline. */
const NEGATIVE_LEXICON: readonly string[] = ['投诉', '维权', '退款', '造假', '虚假', '欺诈', '差评', '吐槽', '翻车', '缺陷', '故障', '事故', '处罚', '罚款', '起诉', '诉讼', '曝光', '辟谣', '下架', '召回', '太慢', '推诿', '傲慢', '失望', '愤怒', '劣质', '假冒', '骗局', '亏损', '裁员', '欠薪']
const POSITIVE_LEXICON: readonly string[] = ['表扬', '好评', '点赞', '推荐', '值得', '优秀', '领先', '突破', '创新', '获奖', '冠军', '畅销', '回购', '认可', '信赖', '超越', '升级', '惊喜', '亮点', '标杆']

/** The structured verdict one classification stage produces. */
export interface LexiconVerdict {
  readonly polarity: SentimentPolarity
  readonly confidence: number
  readonly evidence: string | null
}

/**
 * Stage-1 lexicon classification: count lexicon hits in the text and return
 * the polarity with a confidence proportional to the hit margin.
 * @param text - the mention's combined title + summary text.
 * @returns the verdict; `neu` with 0.3 confidence when no lexicon term hits.
 */
export function classifyByLexicon(text: string): LexiconVerdict {
  let negHits = 0
  let posHits = 0
  let evidence: string | null = null
  for (const term of NEGATIVE_LEXICON) {
    if (text.includes(term)) {
      negHits += 1
      evidence ??= term
    }
  }
  for (const term of POSITIVE_LEXICON) {
    if (text.includes(term)) {
      posHits += 1
      if (evidence === null && negHits === 0) evidence = term
    }
  }
  if (negHits > posHits) return { polarity: 'neg', confidence: Math.min(0.95, 0.6 + negHits * 0.1), evidence }
  if (posHits > negHits) return { polarity: 'pos', confidence: Math.min(0.95, 0.6 + posHits * 0.1), evidence }
  if (negHits > 0) return { polarity: 'neu', confidence: 0.5, evidence }
  return { polarity: 'neu', confidence: 0.3, evidence: null }
}

/** Whether a lexicon verdict is confident enough to skip the LLM stage. */
export function needsRefinement(verdict: LexiconVerdict): boolean {
  return verdict.polarity === 'neu' || verdict.confidence < 0.7
}

/**
 * Parse the batched model answer into per-index verdicts. Model output is a
 * JSON boundary: an unusable body yields an empty map (the caller keeps the
 * lexicon verdicts for those indexes).
 * @param text - exact model text output.
 */
export function parseRefineBatchOutput(text: string): Map<number, LexiconVerdict> {
  const stripped = text.trim().replace(/^```(?:json)?\s*/u, '').replace(/\s*```$/u, '')
  const start = stripped.indexOf('{')
  const end = stripped.lastIndexOf('}')
  const result = new Map<number, LexiconVerdict>()
  if (start === -1 || end <= start) return result
  let parsed: unknown
  try {
    parsed = JSON.parse(stripped.slice(start, end + 1))
  } catch {
    return result
  }
  if (typeof parsed !== 'object' || parsed === null) return result
  for (const [key, value] of Object.entries(parsed as Record<string, unknown>)) {
    const index = Number.parseInt(key, 10)
    if (!Number.isInteger(index) || typeof value !== 'object' || value === null) continue
    const record = value as Record<string, unknown>
    const polarity = record.polarity
    if (typeof polarity !== 'string' || !['pos', 'neu', 'neg'].includes(polarity)) continue
    const confidence = typeof record.confidence === 'number' && Number.isFinite(record.confidence)
      ? Math.min(1, Math.max(0, record.confidence))
      : 0.5
    const evidence = typeof record.evidence === 'string' && record.evidence.trim().length > 0
      ? record.evidence.trim().slice(0, 200)
      : null
    result.set(index, { polarity: polarity as SentimentPolarity, confidence, evidence })
  }
  return result
}

/**
 * Match one entry against the task's keyword groups: a group matches when
 * every one of its terms appears in the text (AND within group, OR across
 * groups). The first matching polarized group biases the classification.
 */
export function matchesKeywordGroups(
  text: string,
  groups: readonly { readonly polarity: SentimentPolarity | 'any'; readonly terms: readonly string[] }[],
): { matched: boolean; hint: SentimentPolarity | null } {
  let hint: SentimentPolarity | null = null
  for (const group of groups) {
    if (group.terms.every(term => text.includes(term))) {
      if (group.polarity !== 'any') hint = group.polarity
      return { matched: true, hint }
    }
  }
  return { matched: false, hint: null }
}

export interface ScanEngineConfig {
  readonly provider: string
  readonly model: string
  readonly timeoutMs: number
  readonly maxOutputTokens: number
  /** `rules` skips the LLM refinement stage entirely; `llm-review` (default) refines the ambiguous. */
  readonly analyzer?: 'rules' | 'llm-review'
}

export interface ScanDeps {
  /** Fetch one feed document; defaults to the shared gather fetcher. */
  readonly fetchFeed?: typeof fetchFeedDocument
  readonly now?: () => Date
  readonly sleep?: (ms: number) => Promise<void>
  /** The batched LLM refinement; defaults to the shared llm call. */
  readonly refineBatch?: typeof refineBatchWithLlm
  readonly llmBatchCap?: number
  /** The weibo visitor search; injectable for tests. */
  readonly fetchWeibo?: typeof fetchWeiboSearch
  /** The weibo hot-comment read; injectable for tests. */
  readonly fetchWeiboComments?: typeof fetchWeiboComments
  /** The bilibili video search; injectable for tests. */
  readonly fetchBiliVideos?: typeof fetchBiliVideos
  /** The bilibili comment read; injectable for tests. */
  readonly fetchBiliComments?: typeof fetchBiliComments
  /** The keyword-expansion middleware; injectable for tests. */
  readonly expandTerms?: typeof expandTaskTerms
}

/** Build one mention row from a normalized source entry (keyword filter + classify upstream). */
function mentionOfEntry(
  entry: SourceEntry,
  taskId: SentimentTask['id'],
  source: SentimentSource,
  platform: string,
  polarity: SentimentPolarity,
  confidence: number,
  evidence: string | null,
  nowIso: string,
): SentimentMention {
  return {
    id: randomUUID() as SentimentMentionId,
    taskId,
    source,
    platform,
    url: entry.url,
    title: entry.title.slice(0, 500),
    summary: entry.summary.slice(0, 500),
    publishedAt: entry.publishedAt,
    capturedAt: nowIso,
    polarity,
    confidence,
    evidence,
    occurrences: 1,
    heatDelta: 0,
    heat: entry.heat,
    author: entry.author,
  }
}

/** One batched LLM refinement: numbered mentions in, per-index verdicts out. */
export async function refineBatchWithLlm(
  ctx: Context,
  policy: AiCallPolicy,
  items: ReadonlyArray<{ index: number; text: string }>,
): Promise<Map<number, LexiconVerdict>> {
  const framed = items.map(item => `${String(item.index)}. ${item.text.slice(0, SENTIMENT_LLM_INPUT_CAP)}`).join('\n')
  const system = `${REFINE_SYSTEM_PROMPT} 输入为按序号编号的多条内容，输出 JSON 对象的键为对应序号数字。`
  const output = await streamLlmText(ctx, policy, system, framed, SENTIMENT_AI_TIMEOUT_CODE)
  return parseRefineBatchOutput(output)
}

/**
 * Run one full scan across the enabled tasks and return the batch to persist.
 * @param ctx - context exposing the registered llm service.
 * @param tasks - the stored tasks (enabled ones with feeds are scanned).
 * @param settings - the stored settings (blacklists, thresholds).
 * @param ai - the resolved AI call policy for the refinement stage.
 * @returns the scan summary plus the new mentions and aggregated alerts.
 */
export async function runSentimentScan(
  ctx: Context,
  tasks: readonly SentimentTask[],
  settings: SentimentSettings,
  ai: ScanEngineConfig,
  deps: ScanDeps = {},
): Promise<{ result: SentimentScanResult; mentions: readonly SentimentMention[]; alerts: readonly SentimentAlert[] }> {
  const now = deps.now?.() ?? new Date()
  const nowIso = now.toISOString()
  const fetchFeed = deps.fetchFeed ?? fetchFeedDocument
  const fetchWeibo = deps.fetchWeibo ?? fetchWeiboSearch
  const fetchWeiboCommentsRead = deps.fetchWeiboComments ?? fetchWeiboComments
  const fetchBiliVideosRead = deps.fetchBiliVideos ?? fetchBiliVideos
  const fetchBiliCommentsRead = deps.fetchBiliComments ?? fetchBiliComments
  const expandTerms = deps.expandTerms ?? expandTaskTerms
  const mentions: SentimentMention[] = []
  const blacklistDomains = settings.domainBlacklist.map(domain => domain.toLowerCase())
  const blacklistAccounts = new Set(settings.accountBlacklist)
  const policy: AiCallPolicy = {
    provider: ai.provider,
    model: ai.model,
    timeoutMs: ai.timeoutMs,
    maxOutputTokens: ai.maxOutputTokens,
  }

  /** Shared keyword/blacklist/classify pipeline for one normalized entry page. */
  const ingestEntries = (
    entries: readonly SourceEntry[],
    task: SentimentTask,
    source: SentimentSource,
    platform: string,
    seenUrls: Set<string>,
    drilldown: Array<{ readonly source: SentimentSource; readonly refId: string; readonly comments: number }>,
  ): void => {
    for (const entry of entries) {
      if (seenUrls.has(entry.url)) continue
      seenUrls.add(entry.url)
      const text = `${entry.title}\n${entry.summary}`
      const match = matchesKeywordGroups(text, task.keywordGroups)
      if (!match.matched) continue
      if (blacklistDomains.some(domain => entry.url.toLowerCase().includes(domain))) continue
      if (entry.author !== null && blacklistAccounts.has(entry.author)) continue
      const lexicon = classifyByLexicon(text)
      mentions.push(mentionOfEntry(
        entry, task.id, source, platform,
        match.hint ?? lexicon.polarity, lexicon.confidence, lexicon.evidence, nowIso,
      ))
      if (typeof entry.refId === 'string' && entry.refId.length > 0) {
        drilldown.push({ source, refId: entry.refId, comments: entry.heat?.comments ?? 0 })
      }
    }
  }

  /** Drill one page of comments behind the hottest matched entries of one source. */
  const drillComments = async (
    task: SentimentTask,
    drilldown: ReadonlyArray<{ readonly source: SentimentSource; readonly refId: string; readonly comments: number }>,
    source: SentimentSource,
    platform: string,
    seenUrls: Set<string>,
    drilledRefs: Set<string>,
  ): Promise<void> => {
    const hottest = drilldown
      .filter(candidate => candidate.source === source && !drilledRefs.has(candidate.refId))
      .sort((left, right) => right.comments - left.comments)
      .slice(0, SENTIMENT_COMMENT_DRILLDOWN_CAP)
    for (const candidate of hottest) {
      drilledRefs.add(candidate.refId)
      const comments = source === 'weibo'
        ? await fetchWeiboCommentsRead(candidate.refId, {})
        : await fetchBiliCommentsRead(candidate.refId, {})
      ingestEntries(comments, task, source, platform, seenUrls, [])
    }
  }

  /** One search-plus-drill round for one source over the given terms. */
  const searchRound = async (
    task: SentimentTask,
    source: SentimentSource,
    terms: readonly string[],
    seenUrls: Set<string>,
    drilldown: Array<{ readonly source: SentimentSource; readonly refId: string; readonly comments: number }>,
    drilledRefs: Set<string>,
  ): Promise<void> => {
    if (source === 'weibo') {
      for (const term of terms) {
        const entries = await fetchWeibo(term, {})
        ingestEntries(entries, task, 'weibo', '微博', seenUrls, drilldown)
      }
      await drillComments(task, drilldown, 'weibo', '微博评论', seenUrls, drilledRefs)
    } else {
      for (const term of terms) {
        const entries = await fetchBiliVideosRead(term, {})
        ingestEntries(entries, task, 'bili', 'B站', seenUrls, drilldown)
      }
      await drillComments(task, drilldown, 'bili', 'B站评论', seenUrls, drilledRefs)
    }
  }

  for (const task of tasks.filter(candidate => candidate.enabled)) {
    const seenUrls = new Set<string>()
    const drilledRefs = new Set<string>()
    const drilldown: Array<{ readonly source: SentimentSource; readonly refId: string; readonly comments: number }> = []
    // RSS feeds: the phase-2 source, always the same fetcher and filters.
    for (const feedUrl of task.feedUrls) {
      let feed
      try {
        feed = await fetchFeed({ url: feedUrl }, {})
      } catch {
        // One unreachable feed is skipped; the scan continues with the rest.
        continue
      }
      if (feed.notModified) continue
      for (const item of feed.items.slice(0, ENTRIES_PER_FEED_CAP)) {
        const text = htmlToText(`${item.title ?? ''}\n${item.summary ?? ''}`)
        const match = matchesKeywordGroups(text, task.keywordGroups)
        if (!match.matched) continue
        if (seenUrls.has(item.url)) continue
        seenUrls.add(item.url)
        if (blacklistDomains.some(domain => item.url.toLowerCase().includes(domain))) continue
        const lexicon = classifyByLexicon(text)
        const polarity: SentimentPolarity = match.hint ?? lexicon.polarity
        mentions.push({
          id: randomUUID() as SentimentMentionId,
          taskId: task.id,
          source: 'rss',
          platform: hostnameOf(feedUrl),
          url: item.url,
          title: (item.title ?? text).slice(0, 500),
          summary: text.slice(0, 500),
          publishedAt: item.publishedAt,
          capturedAt: nowIso,
          polarity,
          confidence: lexicon.confidence,
          evidence: lexicon.evidence,
          occurrences: 1,
          heatDelta: 0,
          heat: null,
          author: null,
        })
      }
    }
    // Platform searches ride the keyword-expansion middleware: the task's
    // subjects widened into the terms real posters use, degrading to the
    // raw subjects; the breadth round searches the first few terms.
    const usesPlatformSearch = task.sources.includes('weibo') || task.sources.includes('bili')
    let expandedTerms: readonly string[] = []
    if (usesPlatformSearch) {
      try {
        expandedTerms = await expandTerms(ctx, policy, task)
      } catch {
        // The expansion middleware owns its degradation; an injected stub or
        // an unexpected throw falls back to the raw subjects, never fails
        // the scan.
        expandedTerms = task.subjects
      }
    }
    const breadthTerms = expandedTerms.slice(0, SENTIMENT_EXPAND_SEARCH_TERMS)
    // weibo visitor search: one page per term (subjects are company/brand
    // names; keyword-group terms would over-match). bilibili video search:
    // one page per term, then the comment layer of the hottest matched videos.
    if (task.sources.includes('weibo')) await searchRound(task, 'weibo', breadthTerms, seenUrls, drilldown, drilledRefs)
    if (task.sources.includes('bili')) await searchRound(task, 'bili', breadthTerms, seenUrls, drilldown, drilledRefs)
    // Depth round (the two-stage breadth→depth pass): when this task's
    // negative mentions already aggregate into a high-level alert, search
    // the next tier of expanded terms and drill deeper comments for the
    // same sources — more evidence for the events that matter.
    const negative = mentions.filter(mention => mention.taskId === task.id && mention.polarity === 'neg')
    if (negative.length > 0 && alertLevelOf(groupHeatOf(negative), settings) <= SENTIMENT_DEPTH_ALERT_LEVEL) {
      const depthTerms = expandedTerms.slice(SENTIMENT_EXPAND_SEARCH_TERMS, SENTIMENT_EXPAND_SEARCH_TERMS + SENTIMENT_EXPAND_DEPTH_TERMS)
      if (task.sources.includes('weibo')) await searchRound(task, 'weibo', depthTerms, seenUrls, drilldown, drilledRefs)
      if (task.sources.includes('bili')) await searchRound(task, 'bili', depthTerms, seenUrls, drilldown, drilledRefs)
    }
  }

  // Stage-2 LLM refinement: batch the ambiguous/low-confidence mentions.
  // The rules analyzer skips the stage; an LLM failure degrades to the
  // lexicon verdicts instead of failing the scan.
  const refinement: NonNullable<SentimentScanResult['refinement']> = ai.analyzer === 'rules' ? 'skipped' : 'ok'
  const ambiguous = refinement === 'skipped' ? [] : mentions
    .map((mention, index) => ({ index, mention }))
    .filter(({ mention }) => needsRefinement({ polarity: mention.polarity, confidence: mention.confidence, evidence: mention.evidence }))
    .slice(0, deps.llmBatchCap ?? SENTIMENT_LLM_BATCH_CAP)
  if (ambiguous.length > 0) {
    let verdicts: Map<number, LexiconVerdict>
    try {
      verdicts = await (deps.refineBatch ?? refineBatchWithLlm)(ctx, policy, ambiguous.map(({ index, mention }) => ({
        index,
        text: `${mention.title}\n${mention.summary}`,
      })))
    } catch {
      return {
        result: { captured: mentions.length, alerts: 0, at: nowIso, refinement: 'degraded' },
        mentions,
        alerts: aggregateAlerts(mentions, settings, nowIso),
      }
    }
    for (const { index, mention } of ambiguous) {
      const verdict = verdicts.get(index)
      if (verdict === undefined) continue
      mentions[index] = {
        ...mention,
        polarity: verdict.polarity,
        confidence: verdict.confidence,
        evidence: verdict.evidence ?? mention.evidence,
      }
    }
  }

  const newAlerts = aggregateAlerts(mentions, settings, nowIso)
  return {
    result: { captured: mentions.length, alerts: newAlerts.length, at: nowIso, refinement },
    mentions,
    alerts: newAlerts,
  }
}

function hostnameOf(feedUrl: string): string {
  try {
    return new URL(feedUrl).hostname
  } catch {
    return 'RSS'
  }
}

/**
 * Aggregate negative mentions into deduplicated alerts: one alert per
 * task+day event key, level from the aggregated heat against the
 * configured negative heat threshold.
 */
export function aggregateAlerts(
  mentions: readonly SentimentMention[],
  settings: SentimentSettings,
  nowIso: string,
): SentimentAlert[] {
  const negative = mentions.filter(mention => mention.polarity === 'neg')
  const byEvent = new Map<string, SentimentMention[]>()
  for (const mention of negative) {
    const key = `${mention.taskId}:${nowIso.slice(0, 10)}`
    byEvent.set(key, [...byEvent.get(key) ?? [], mention])
  }
  const alerts: SentimentAlert[] = []
  for (const [eventKey, group] of byEvent) {
    const lead = group[0]
    if (lead === undefined) continue
    const heat = groupHeatOf(group)
    const level = alertLevelOf(heat, settings)
    const reasonParts = [`负面提及 ${String(group.length)} 条`, `热度 ${String(heat)}`]
    const evidence = group.find(m => m.evidence !== null)?.evidence ?? null
    if (evidence !== null) reasonParts.push(`依据：${evidence}`)
    alerts.push({
      id: randomUUID() as SentimentAlertId,
      taskId: lead.taskId,
      eventKey,
      level,
      summary: group.length === 1
        ? lead.title
        : `${String(group.length)} 条负面提及聚集（含「${lead.title.slice(0, 40)}」等）`,
      reason: reasonParts.join('；'),
      mentionIds: group.map(m => m.id),
      handled: false,
      createdAt: nowIso,
      handledAt: null,
    })
  }
  return alerts
}

/** Summed engagement heat of one mention group (fallback: 100 per mention). */
export function groupHeatOf(group: readonly SentimentMention[]): number {
  const totalHeat = group.reduce((sum, m) => sum + (m.heat?.likes ?? 0) + (m.heat?.comments ?? 0) + (m.heat?.shares ?? 0), 0)
  return totalHeat > 0 ? totalHeat : group.length * 100
}

/** Map one aggregated heat against the configured threshold to an alert level. */
export function alertLevelOf(heat: number, settings: SentimentSettings): 1 | 2 | 3 | 4 {
  return heat >= settings.negativeHeatThreshold * 4 ? 1
    : heat >= settings.negativeHeatThreshold ? 2
      : heat >= settings.negativeHeatThreshold / 4 ? 3 : 4
}
