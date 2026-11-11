/** Topic-bank Remote for the content-creation library. */

import type { Context } from '@deepseek-ai/cordis'
import z from '@deepseek-ai/schemastery'
import type Schema from '@deepseek-ai/schemastery'
import { resolveDshHome } from '@deepseek-ai/dsh-home-paths'
import { join } from 'node:path'
import { TypertRemoteService, Remote } from '@deepseek-ai/dsh-typert-protocol'
// Typert-generated ./typert and ./remote artifacts import Zod at runtime.
import type {} from 'zod'
import type {
  ContentTopicsSnapshot, TopicCategoriesSnapshot, TopicCategory, TopicCategoryInput, TopicItem, TopicItemInput,
} from './types.ts'
import { TOPICS_FILENAME, mutateTopics, normalizeInput, readTopics } from './store.ts'
import {
  TOPIC_CATEGORIES_FILENAME, TOPIC_CATEGORIES_MAX, mutateTopicCategories, normalizeCategoryInput, readTopicCategories,
} from './categories.ts'

export type * from './types.ts'
export { TOPICS_FILENAME, normalizeInput, readTopics, mutateTopics } from './store.ts'
export {
  TOPIC_CATEGORIES_FILENAME, TOPIC_CATEGORIES_MAX, mutateTopicCategories, normalizeCategoryInput, readTopicCategories,
} from './categories.ts'

/** Content-topics Remote configuration. */
export interface Config {
  /** Outputs library root. Defaults to `<dsh home>/outputs`. */
  root?: string
}

export const Config: Schema<Config> = z.object({
  root: z.string(),
})

/**
 * Remote topic-bank service over `_topics.json` at the library root. Every
 * method reads or commits the file directly — the bank is small, and the
 * file stays the single truth the agent can also read.
 */
export class ContentTopicsGateway extends TypertRemoteService {
  static inject = []

  static Config: Schema<Config> = Config

  /** Absolute topic bank file path. */
  private readonly file: string

  /** Absolute topic categories file path. */
  private readonly categoriesFile: string

  constructor(ctx: Context, config: Config) {
    super(ctx, 'contentTopics')
    const root = join(resolveDshHome(config.root), 'outputs')
    this.file = join(root, TOPICS_FILENAME)
    this.categoriesFile = join(root, TOPIC_CATEGORIES_FILENAME)
  }

  /**
   * Read the whole topic bank.
   * @returns items sorted by `updatedAt` (newest first), with every bad
   * stored record named.
   */
  @Remote('list')
  async list(): Promise<ContentTopicsSnapshot> {
    return readTopics(this.file)
  }

  /**
   * Upsert one topic: an absent `id` (or an unknown one) creates; a known one
   * replaces in place, keeping the stored `createdAt` and restamping
   * `updatedAt`. Identity is decided by id alone.
   * @param input - the upsert payload.
   * @returns the post-write topic bank snapshot.
   */
  @Remote('put')
  async put(input: TopicItemInput): Promise<ContentTopicsSnapshot> {
    const { item, detail } = normalizeInput(input)
    if (item === undefined) throw new Error(`invalid topic item: ${detail}`)
    return mutateTopics(this.file, (items) => {
      const previous = items.find(candidate => candidate.id === item.id)
      if (previous === undefined) return [...items, item]
      return items.map(candidate => candidate.id === item.id ? { ...item, createdAt: previous.createdAt } : candidate)
    })
  }

  /**
   * Delete one topic by id; deleting an unknown id is a no-op, not an error.
   * Only the topic record is removed — the linked schedule entry and the
   * outputs project, if any, stay untouched.
   * @param id - the topic's stable identity.
   * @returns the post-write topic bank snapshot.
   */
  @Remote('delete')
  async delete(id: TopicItem['id']): Promise<ContentTopicsSnapshot> {
    return mutateTopics(this.file, items => items.filter(candidate => candidate.id !== id))
  }

  /**
   * Read the whole topic-category list.
   * @returns items sorted by `updatedAt` (newest first), with every bad
   * stored record named.
   */
  @Remote('listCategories')
  async listCategories(): Promise<TopicCategoriesSnapshot> {
    return readTopicCategories(this.categoriesFile)
  }

  /**
   * Upsert one topic category: an absent `id` (or an unknown one) creates; a
   * known one replaces in place, keeping the stored `createdAt` and
   * restamping `updatedAt`. A create is rejected once the store holds the
   * category cap.
   * @param input - the upsert payload.
   * @returns the post-write category snapshot.
   */
  @Remote('putCategory')
  async putCategory(input: TopicCategoryInput): Promise<TopicCategoriesSnapshot> {
    const { item, detail } = normalizeCategoryInput(input)
    if (item === undefined) throw new Error(`invalid topic category: ${detail}`)
    return mutateTopicCategories(this.categoriesFile, (items) => {
      const previous = items.find(candidate => candidate.id === item.id)
      if (previous === undefined) {
        if (items.length >= TOPIC_CATEGORIES_MAX) throw new Error(`invalid topic category: at most ${TOPIC_CATEGORIES_MAX} categories are stored`)
        return [...items, item]
      }
      return items.map(candidate => candidate.id === item.id ? { ...item, createdAt: previous.createdAt } : candidate)
    })
  }

  /**
   * Delete one topic category by id; deleting an unknown id is a no-op, not
   * an error. Only the category record is removed — topics produced under it
   * stay in the bank.
   * @param id - the category's stable identity.
   * @returns the post-write category snapshot.
   */
  @Remote('deleteCategory')
  async deleteCategory(id: TopicCategory['id']): Promise<TopicCategoriesSnapshot> {
    return mutateTopicCategories(this.categoriesFile, items => items.filter(candidate => candidate.id !== id))
  }
}

export default ContentTopicsGateway
