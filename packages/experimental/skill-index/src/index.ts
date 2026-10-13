/**
 * Dragon Engine asset index reader.
 *
 * This package exposes the `dragon-assets/index/*.jsonl` files (mirrored from
 * `dragon-engine V2.5`'s `scripts/build-index.py` output) as a Cordis Service
 * consumers can read at runtime. It is read-only — the index is regenerated
 * upstream by the dragon-engine toolchain, not by DSH.
 *
 * The service gives DSH three affordances:
 *
 * 1. `loadAll()` — read every jsonl file into one snapshot.
 * 2. `search(query)` — substring + facet filter over the snapshot.
 * 3. `get(id, kind?)` — exact-id lookup, optional kind disambiguation.
 *
 * @module @deepseek-ai/dsh-experimental-skill-index
 */

import { existsSync, promises as fs } from 'node:fs'
import { dirname, join } from 'node:path'
import { Service } from '@deepseek-ai/cordis'
import type { AssetIndexEntry, AssetKind, Config, IndexSnapshot, SearchQuery } from './types'

const DEFAULT_RELATIVE_ROOT = 'dragon-assets'
const INDEX_DIRECTORY = 'index'
const INDEX_FILES: Readonly<Record<AssetKind, string>> = {
  skill: 'SKILLS.jsonl',
  agent: 'AGENTS.jsonl',
  hook: 'HOOKS.jsonl',
  command: 'COMMANDS.jsonl',
  plugin: 'PLUGINS.jsonl',
}

declare module '@deepseek-ai/cordis' {
  interface Context {
    /** The Dragon Engine asset index registry, populated from `dragon-assets/index/`. */
    dragonIndex: DragonAssetIndex
  }
}

/**
 * Read-only registry over the `dragon-assets/index/*.jsonl` snapshots.
 *
 * One service instance owns one snapshot. Callers can refresh the snapshot by
 * calling `loadAll()` again; the registry exposes the current snapshot via
 * the `snapshot` accessor.
 */
export class DragonAssetIndex extends Service {
  private readonly root: string
  private current: IndexSnapshot = EMPTY_SNAPSHOT

  constructor(ctx: import('@deepseek-ai/cordis').Context, config: Partial<Config> = {}) {
    super(ctx, 'dragonIndex')
    this.root = resolveRoot(config.dragonAssetsRoot)
  }

  /** The resolved `dragon-assets/` root this registry reads from. */
  get rootPath(): string {
    return this.root
  }

  /** The currently cached snapshot, or an empty placeholder before `loadAll()`. */
  get snapshot(): IndexSnapshot {
    return this.current
  }

  /**
   * Read every jsonl file into one snapshot and cache it.
   * @returns the loaded snapshot.
   */
  async loadAll(): Promise<IndexSnapshot> {
    const [skills, agents, hooks, commands, plugins] = await Promise.all([
      this.readJsonl('skill'),
      this.readJsonl('agent'),
      this.readJsonl('hook'),
      this.readJsonl('command'),
      this.readJsonl('plugin'),
    ])
    this.current = Object.freeze({
      skills,
      agents,
      hooks,
      commands,
      plugins,
      all: Object.freeze([...skills, ...agents, ...hooks, ...commands, ...plugins]),
    })
    return this.current
  }

  /**
   * Filter the cached snapshot.
   * @param query - filter criteria; missing fields do not restrict.
   * @returns matching entries, ordered as the source jsonl declared them.
   */
  search(query: SearchQuery = {}): readonly AssetIndexEntry[] {
    const source = this.entriesByKind(query.kind)
    const needle = query.text?.toLowerCase()
    const matched = source.filter(entry => matchesQuery(entry, needle, query.license))
    return typeof query.limit === 'number' ? matched.slice(0, query.limit) : matched
  }

  /**
   * Exact-id lookup against the cached snapshot.
   * @param id - the asset identifier to resolve.
   * @param kind - optional kind disambiguator; omitted matches the first entry of any kind.
   * @returns the matching entry, or `undefined` if none.
   */
  get(id: string, kind?: AssetKind): AssetIndexEntry | undefined {
    const idLower = id.toLowerCase()
    if (kind !== undefined) {
      return this.entriesByKind(kind).find(entry => entry.id.toLowerCase() === idLower)
    }
    return this.current.all.find(entry => entry.id.toLowerCase() === idLower)
  }

  private entriesByKind(kind: AssetKind | undefined): readonly AssetIndexEntry[] {
    if (kind === undefined) return this.current.all
    switch (kind) {
      case 'skill': return this.current.skills
      case 'agent': return this.current.agents
      case 'hook': return this.current.hooks
      case 'command': return this.current.commands
      case 'plugin': return this.current.plugins
    }
  }

  private async readJsonl(kind: AssetKind): Promise<readonly AssetIndexEntry[]> {
    const file = join(this.root, INDEX_DIRECTORY, INDEX_FILES[kind])
    let raw: string
    try {
      raw = await fs.readFile(file, 'utf8')
    } catch (error) {
      const code = (error as NodeJS.ErrnoException).code
      if (code === 'ENOENT') return Object.freeze([])
      /* v8 ignore next -- NodeJS fs rejections are always Error instances; the String branch is type-safe defensiveness only. */
      const reason = error instanceof Error ? error.message : String(error)
      throw new Error(`dragonIndex: failed to read ${file}: ${reason}`)
    }
    return parseJsonl(raw)
  }
}

const EMPTY_SNAPSHOT: IndexSnapshot = Object.freeze({
  skills: Object.freeze([]),
  agents: Object.freeze([]),
  hooks: Object.freeze([]),
  commands: Object.freeze([]),
  plugins: Object.freeze([]),
  all: Object.freeze([]),
})

/** Resolve the configured root with an explicit value winning over env over workspace default. */
function resolveRoot(explicit: string | undefined): string {
  if (explicit !== undefined) return explicit
  const fromEnv = process.env.DRAGON_ASSETS_ROOT
  if (typeof fromEnv === 'string' && fromEnv !== '') return fromEnv
  return join(resolveWorkspaceRoot(process.cwd()), DEFAULT_RELATIVE_ROOT)
}

/**
 * Find the nearest ancestor of `start` whose directory contains a `package.json`,
 * then return its parent (the conventional workspace root).
 *
 * Walks at most 8 levels; if no `package.json` is found in that window the search
 * gives up and returns the deepest-reached ancestor, which is `start` when the
 * filesystem root was hit before any matching package was located.
 */
function resolveWorkspaceRoot(start: string): string {
  let current = start
  for (let depth = 0; depth < 8; depth += 1) {
    if (existsSync(join(current, 'package.json'))) return dirname(current)
    current = dirname(current)
  }
  /* v8 ignore next -- The loop always advances and `existsSync` always resolves;
   * this fallback is type-safe defensiveness against a hypothetical walk exhaust. */
  return current
}

function parseJsonl(raw: string): readonly AssetIndexEntry[] {
  const lines = raw.split(/\r?\n/)
  const entries: AssetIndexEntry[] = []
  for (let i = 0; i < lines.length; i += 1) {
    const line = lines[i]?.trim()
    /* v8 ignore else -- Array#split always yields a string at index < length;
     * the optional chain guards against noUncheckedIndexedAccess narrowing. */
    if (line === undefined || line === '') continue
    let parsed: unknown
    try {
      parsed = JSON.parse(line)
    } catch (error) {
      /* v8 ignore next -- JSON.parse rejections are always SyntaxError instances; the String branch is type-safe defensiveness only. */
      const reason = error instanceof Error ? error.message : String(error)
      throw new Error(`dragonIndex: malformed jsonl line ${i + 1}: ${reason}`)
    }
    if (!isAssetIndexEntry(parsed)) {
      throw new Error(`dragonIndex: jsonl line ${i + 1} is missing required id/kind/path fields`)
    }
    entries.push(parsed)
  }
  return Object.freeze(entries)
}

function isAssetIndexEntry(value: unknown): value is AssetIndexEntry {
  if (value === null || typeof value !== 'object') return false
  const obj = value as Record<string, unknown>
  if (typeof obj.id !== 'string' || obj.id === '') return false
  if (typeof obj.kind !== 'string') return false
  if (typeof obj.path !== 'string' || obj.path === '') return false
  return true
}

function matchesQuery(entry: AssetIndexEntry, needle: string | undefined, license: AssetIndexEntry['license']): boolean {
  if (license !== undefined && entry.license !== license) return false
  if (needle === undefined) return true
  if (entry.id.toLowerCase().includes(needle)) return true
  if (typeof entry.description === 'string' && entry.description.toLowerCase().includes(needle)) return true
  if (Array.isArray(entry.triggers) && entry.triggers.some(t => typeof t === 'string' && t.toLowerCase().includes(needle))) return true
  if (Array.isArray(entry.tags) && entry.tags.some(t => typeof t === 'string' && t.toLowerCase().includes(needle))) return true
  if (typeof entry.upstream === 'string' && entry.upstream.toLowerCase().includes(needle)) return true
  return false
}

export default DragonAssetIndex
export type { AssetIndexEntry, AssetKind, Config, IndexSnapshot, LicenseTier, SearchQuery } from './types'
