/**
 * Topic-category file store: reads and writes the categories JSON directly
 * on every call. The file lives at the library root next to `_topics.json`
 * under the `_` prefix so the outputs scanner treats it as a system entry.
 * Keeping categories in their own sidecar means the topics bank format and
 * its read-modify-write cycle never see category writes.
 *
 * Validation follows the topic-bank rule: one malformed record is named in
 * `problems` and skipped, and a file whose `formatVersion` is not the
 * current one never loads as current records.
 */

import { mkdir, readFile } from 'node:fs/promises'
import { dirname } from 'node:path'
import { randomUUID } from 'node:crypto'
import { withFileLock, writeFileAtomic } from '@deepseek-ai/dsh-atomic-write'
import type { TopicCategoriesSnapshot, TopicCategory, TopicCategoryInput } from './types.ts'

/** System file name of the topic categories at the library root. */
export const TOPIC_CATEGORIES_FILENAME = '_topic-categories.json'

/** Current on-disk format version of the categories file. */
const FORMAT_VERSION = 0

/** Cap of stored categories. */
export const TOPIC_CATEGORIES_MAX = 30

/** Character cap of one category name. */
export const TOPIC_CATEGORY_NAME_MAX = 40

/** Cap of keywords per category. */
export const TOPIC_CATEGORY_KEYWORDS_MAX = 20

/** Character cap of one keyword term. */
export const TOPIC_CATEGORY_TERM_MAX = 40

/** Cap of RSS feed URLs per category. */
export const TOPIC_CATEGORY_FEEDS_MAX = 10

const ISO_PATTERN = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$/

function isIsoTimestamp(value: unknown): value is string {
  return typeof value === 'string' && ISO_PATTERN.test(value) && !Number.isNaN(Date.parse(value))
}

function isFeedUrls(value: unknown): value is string[] {
  return Array.isArray(value) && value.length <= TOPIC_CATEGORY_FEEDS_MAX
    && value.every(url => typeof url === 'string' && url.length > 0 && url.length <= 500)
}

function isCategory(value: unknown): value is TopicCategory {
  if (typeof value !== 'object' || value === null) return false
  const record = value as Record<string, unknown>
  return typeof record.id === 'string' && record.id.length > 0
    && typeof record.name === 'string' && record.name.length > 0 && record.name.length <= TOPIC_CATEGORY_NAME_MAX
    && Array.isArray(record.keywords) && record.keywords.length > 0
    && record.keywords.length <= TOPIC_CATEGORY_KEYWORDS_MAX
    && record.keywords.every(keyword => typeof keyword === 'string' && keyword.length > 0 && keyword.length <= TOPIC_CATEGORY_TERM_MAX)
    && (record.feedUrls === undefined || isFeedUrls(record.feedUrls))
    && isIsoTimestamp(record.createdAt)
    && isIsoTimestamp(record.updatedAt)
}

/** Sort key: `updatedAt` descending (newest first), then id for stability. */
function compareCategories(a: TopicCategory, b: TopicCategory): number {
  if (a.updatedAt !== b.updatedAt) return a.updatedAt > b.updatedAt ? -1 : 1
  return a.id < b.id ? -1 : 1
}

/**
 * Validate one upsert input into its stored shape: `id` is generated as a
 * UUID when absent, timestamps are stamped here, and keywords are trimmed
 * with blanks dropped. Duplicate keywords collapse to their first occurrence.
 * @param input - the upsert payload.
 * @returns the stored category, or the reason the input is invalid.
 */
export function normalizeCategoryInput(input: TopicCategoryInput): { item?: TopicCategory; detail?: string } {
  if (typeof input.name !== 'string' || input.name.trim().length === 0 || input.name.trim().length > TOPIC_CATEGORY_NAME_MAX) {
    return { detail: `name must be a non-empty string of at most ${TOPIC_CATEGORY_NAME_MAX} characters` }
  }
  if (!Array.isArray(input.keywords) || input.keywords.length === 0 || input.keywords.length > TOPIC_CATEGORY_KEYWORDS_MAX) {
    return { detail: `keywords must be 1-${TOPIC_CATEGORY_KEYWORDS_MAX} strings` }
  }
  const keywords: string[] = []
  for (const keyword of input.keywords) {
    if (typeof keyword !== 'string') return { detail: 'keywords must be strings' }
    const term = keyword.trim()
    if (term.length === 0) continue
    if (term.length > TOPIC_CATEGORY_TERM_MAX) return { detail: `keyword terms must be at most ${TOPIC_CATEGORY_TERM_MAX} characters` }
    if (!keywords.includes(term)) keywords.push(term)
  }
  if (keywords.length === 0) return { detail: 'keywords must contain at least one non-empty term' }
  let feedUrls: string[] = []
  if (input.feedUrls !== undefined) {
    if (!Array.isArray(input.feedUrls) || input.feedUrls.length > TOPIC_CATEGORY_FEEDS_MAX) {
      return { detail: `feedUrls must be at most ${TOPIC_CATEGORY_FEEDS_MAX} strings` }
    }
    feedUrls = []
    for (const url of input.feedUrls) {
      if (typeof url !== 'string') return { detail: 'feedUrls must be strings' }
      const trimmed = url.trim()
      if (trimmed.length === 0) continue
      if (trimmed.length > 500) return { detail: 'feed URLs must be at most 500 characters' }
      if (!feedUrls.includes(trimmed)) feedUrls.push(trimmed)
    }
  }
  const now = new Date().toISOString()
  return {
    item: {
      id: input.id ?? (randomUUID() as TopicCategory['id']),
      name: input.name.trim(),
      keywords,
      feedUrls,
      createdAt: now,
      updatedAt: now,
    },
  }
}

function parseJsonOrNull(raw: string): unknown {
  try {
    return JSON.parse(raw)
  } catch {
    return null
  }
}

/**
 * Read the topic categories file.
 * @param file - absolute `_topic-categories.json` path; a missing file is empty.
 * @returns the snapshot with items sorted and every bad record named.
 */
export async function readTopicCategories(file: string): Promise<TopicCategoriesSnapshot> {
  const raw = await readFile(file, 'utf8').catch(() => null)
  if (raw === null) return { file, items: [], problems: [] }
  const parsed = parseJsonOrNull(raw)
  if (parsed === null) return { file, items: [], problems: ['topic categories file is not valid JSON'] }
  const root = parsed as Record<string, unknown>
  if (root.formatVersion !== FORMAT_VERSION) {
    return { file, items: [], problems: [`unsupported topic categories formatVersion ${String(root.formatVersion)}`] }
  }
  if (!Array.isArray(root.items)) return { file, items: [], problems: ['topic categories file has no items array'] }

  const items: TopicCategory[] = []
  const problems: string[] = []
  for (const entry of root.items) {
    if (isCategory(entry)) items.push(entry)
    else problems.push(`dropped one invalid category record: ${JSON.stringify(entry).slice(0, 120)}`)
  }
  items.sort(compareCategories)
  return { file, items, problems }
}

/**
 * Apply one mutation to the topic categories under a file lock, atomically.
 * @param file - absolute `_topic-categories.json` path; parent directories
 * are created before the lock so a fresh install's very first write succeeds.
 * @param mutate - pure transform over the current category list.
 * @returns the mutation's write snapshot (post-write state).
 */
export async function mutateTopicCategories(
  file: string,
  mutate: (items: readonly TopicCategory[]) => Promise<readonly TopicCategory[]> | readonly TopicCategory[],
): Promise<TopicCategoriesSnapshot> {
  await mkdir(dirname(file), { recursive: true, mode: 0o700 })
  return withFileLock(file, async () => {
    const before = await readTopicCategories(file)
    const items = await mutate(before.items)
    const body = `${JSON.stringify({ formatVersion: FORMAT_VERSION, items }, null, 2)}\n`
    await writeFileAtomic(file, body, { mode: 0o600, dirMode: 0o700 })
    const after = await readTopicCategories(file)
    return { ...after, problems: [...before.problems, ...after.problems] }
  })
}
