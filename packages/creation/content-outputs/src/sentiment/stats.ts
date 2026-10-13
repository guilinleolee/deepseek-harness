/**
 * The dashboard statistics projection computed from the stored mentions:
 * counts, the 14-day local-day trend, and the per-platform top list.
 */

import type { SentimentMention, SentimentStats, SentimentTask } from './types.ts'

/** The trend window the dashboard renders. */
export const SENTIMENT_TREND_DAYS = 14

/** Local calendar day (YYYY-MM-DD) of one timestamp. */
export function localDayOf(iso: string): string {
  const date = new Date(iso)
  if (Number.isNaN(date.getTime())) return ''
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

/**
 * Compute the dashboard statistics from the stored mentions.
 * @param mentions - the stored mentions (any order).
 * @param tasks - the stored tasks (for the task count).
 * @param now - the current instant anchoring the trend window.
 */
export function computeSentimentStats(
  mentions: readonly SentimentMention[],
  tasks: readonly SentimentTask[],
  now: Date,
): SentimentStats {
  const positive = mentions.filter(m => m.polarity === 'pos').length
  const negative = mentions.filter(m => m.polarity === 'neg').length
  const neutral = mentions.length - positive - negative

  const trend: Array<{ day: string; pos: number; neu: number; neg: number }> = []
  const byDay = new Map<string, { pos: number; neu: number; neg: number }>()
  for (const mention of mentions) {
    const day = localDayOf(mention.capturedAt)
    if (day.length === 0) continue
    const bucket = byDay.get(day) ?? { pos: 0, neu: 0, neg: 0 }
    if (mention.polarity === 'pos') bucket.pos += 1
    else if (mention.polarity === 'neg') bucket.neg += 1
    else bucket.neu += 1
    byDay.set(day, bucket)
  }
  for (let offset = SENTIMENT_TREND_DAYS - 1; offset >= 0; offset -= 1) {
    const day = localDayOf(new Date(now.getFullYear(), now.getMonth(), now.getDate() - offset).toISOString())
    const bucket = byDay.get(day) ?? { pos: 0, neu: 0, neg: 0 }
    trend.push({ day, ...bucket })
  }

  const byPlatform = new Map<string, number>()
  for (const mention of mentions) {
    byPlatform.set(mention.platform, (byPlatform.get(mention.platform) ?? 0) + 1)
  }
  const platforms = [...byPlatform.entries()]
    .map(([platform, count]) => ({ platform, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 8)

  return {
    total: mentions.length,
    positive,
    neutral,
    negative,
    highRisk: negative,
    taskCount: tasks.length,
    trend,
    platforms,
  }
}
