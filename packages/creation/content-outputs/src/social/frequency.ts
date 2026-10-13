/**
 * Daily capture-frequency gate for the social-capture faces: a local counter
 * file (0600, same directory as the sessions) limits one user to a handful
 * of captures per platform per day. The cap is a compliance posture first —
 * low frequency is what keeps logged-in reads off the platforms' risk
 * radar — and a风控 protection for the user's own account second.
 */

import { readFile } from 'node:fs/promises'
import { join } from 'node:path'
import { writeFileAtomic } from '@deepseek-ai/dsh-atomic-write'
import type { SocialPlatform } from '../persona/types.ts'

/** One day's counters; the date rollover invalidates the whole record. */
export interface CaptureCounters {
  readonly date: string
  readonly counts: Partial<Record<SocialPlatform, number>>
}

/** The counter file lives beside the sessions. */
export function countersPath(dir: string): string {
  return join(dir, 'capture-counts.json')
}

/** The local calendar day (YYYY-MM-DD), injected as `now` for tests. */
export function localDay(now: Date): string {
  const y = now.getFullYear()
  const m = String(now.getMonth() + 1).padStart(2, '0')
  const d = String(now.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

/** Read today's counters; a stale-date or unreadable file counts as empty. */
export async function readCounters(dir: string, now: Date): Promise<CaptureCounters> {
  let raw: string
  try {
    raw = await readFile(countersPath(dir), 'utf8')
  } catch {
    return { date: localDay(now), counts: {} }
  }
  try {
    const parsed = JSON.parse(raw) as CaptureCounters
    // Runtime JSON can carry null/odd shapes the static type cannot express.
    const counts = parsed.counts as Partial<Record<SocialPlatform, number>> | null | undefined
    if (parsed.date !== localDay(now) || typeof counts !== 'object' || counts === null) {
      return { date: localDay(now), counts: {} }
    }
    return { date: parsed.date, counts }
  } catch {
    return { date: localDay(now), counts: {} }
  }
}

/**
 * Consume one capture slot: throws when the platform's daily cap is reached,
 * otherwise persists the incremented counter.
 * @param dir - the social-states directory (counters live beside sessions).
 * @param platform - the platform being captured.
 * @param cap - the configured daily maximum (validated at config resolution).
 * @param now - the current instant (tests inject a fixed date).
 */
export async function consumeCapture(dir: string, platform: SocialPlatform, cap: number, now: Date): Promise<void> {
  const counters = await readCounters(dir, now)
  const used = counters.counts[platform] ?? 0
  if (used >= cap) {
    throw new Error(`该平台今天的读取次数已达上限（${String(cap)} 次/天）——低频读取是账号安全的保护线，明天再试`)
  }
  const next: CaptureCounters = { date: counters.date, counts: { ...counters.counts, [platform]: used + 1 } }
  await writeFileAtomic(countersPath(dir), JSON.stringify(next, null, 2), { mode: 0o600, dirMode: 0o700 })
}
