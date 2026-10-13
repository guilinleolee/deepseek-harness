/**
 * Dragon Engine agent role registry.
 *
 * This package scans every `.md` file under `dragon-assets/agents/` and produces
 * a typed roster keyed by the upstream 00-99 numeric id. The roster is a
 * snapshot, refreshed on demand via `loadAll()`. Consumers may select roles by
 * family, free-text search, or exact id.
 *
 * Each source markdown is parsed for:
 *   - leading `# ROLE_NAME` heading (display name)
 *   - first non-heading paragraph (description)
 *   - frontmatter `license:` if present
 *   - capabilities harvested from the `## 能力` / `## Capabilities` section
 *
 * The service is read-only and never writes back to the mirror.
 *
 * @module @deepseek-ai/dsh-experimental-agent-roster
 */

import { existsSync, promises as fs } from 'node:fs'
import { join } from 'node:path'
import { Service } from '@deepseek-ai/cordis'
import type { AgentFamily, AgentId, AgentRole, Config, RoleSearchQuery } from './types'

const DEFAULT_RELATIVE_ROOT = 'dragon-assets'
const AGENTS_DIRECTORY = 'agents'
const DEFAULT_EXCLUDES = ['.gitnexus', 'shibazi', 'zcf']

/** Loaded configuration for {@link AgentRoster}. */
interface AgentRosterConfig extends Config {
  /** Directory names under `dragon-assets/agents/` to ignore. */
  excludeSubdirs?: readonly string[]
}

declare module '@deepseek-ai/cordis' {
  interface Context {
    /** The Dragon Engine agent role registry, populated from `dragon-assets/agents/`. */
    agentRoster: AgentRoster
  }
}

/**
 * Read-only registry over the `dragon-assets/agents/` source markdowns.
 *
 * One service instance owns one snapshot; call `loadAll()` after upstream
 * mirror changes to refresh.
 */
export class AgentRoster extends Service {
  private readonly root: string
  private readonly exclude: ReadonlySet<string>
  private current: readonly AgentRole[] = []

  constructor(ctx: import('@deepseek-ai/cordis').Context, config: Partial<AgentRosterConfig> = {}) {
    super(ctx, 'agentRoster')
    this.root = resolveRoot(config.dragonAssetsRoot)
    this.exclude = new Set([...DEFAULT_EXCLUDES, ...(config.excludeSubdirs ?? [])])
  }

  /** The resolved `dragon-assets/` root this registry reads from. */
  get rootPath(): string {
    return this.root
  }

  /** The currently cached roster, or an empty placeholder before `loadAll()`. */
  get roles(): readonly AgentRole[] {
    return this.current
  }

  /**
   * Walk the `agents/` mirror and parse every markdown file into a role.
   * @returns the loaded roster, sorted by numeric prefix then id.
   */
  async loadAll(): Promise<readonly AgentRole[]> {
    const agentsDir = join(this.root, AGENTS_DIRECTORY)
    if (!existsSync(agentsDir)) {
      this.current = Object.freeze([])
      return this.current
    }
    const files = await collectMarkdownFiles(agentsDir, this.exclude)
    const roles: AgentRole[] = []
    for (const file of files) {
      const role = await parseRoleFile(this.root, file)
      if (role !== undefined) roles.push(role)
    }
    roles.sort(compareRoles)
    this.current = Object.freeze(roles)
    return this.current
  }

  /**
   * Filter the cached roster.
   * @param query - filter criteria; missing fields do not restrict.
   * @returns matching roles, sorted as the source roster declared them.
   */
  search(query: RoleSearchQuery = {}): readonly AgentRole[] {
    const needle = query.text?.toLowerCase()
    const matched = this.current.filter((role) => {
      if (query.family !== undefined && role.family !== query.family) return false
      if (query.license !== undefined && role.license !== query.license) return false
      if (needle !== undefined && !matchesNeedle(role, needle)) return false
      return true
    })
    return typeof query.limit === 'number' ? matched.slice(0, query.limit) : matched
  }

  /**
   * Exact-id lookup against the cached roster.
   * @param id - the role identifier (without `.md`).
   * @returns the matching role, or `undefined` if none.
   */
  get(id: AgentId): AgentRole | undefined {
    return this.current.find(role => role.id === id)
  }

  /** Return every role belonging to one family bucket. */
  byFamily(family: AgentFamily): readonly AgentRole[] {
    return this.current.filter(role => role.family === family)
  }
}

function resolveRoot(explicit: string | undefined): string {
  if (explicit !== undefined) return explicit
  const fromEnv = process.env.DRAGON_ASSETS_ROOT
  /* v8 ignore else -- DRAGON_ASSETS_ROOT is either set (path 1) or absent / empty
   * (path 2). When empty the env is treated as absent to avoid joining into "". */
  if (typeof fromEnv === 'string' && fromEnv !== '') return fromEnv
  return join(process.cwd(), DEFAULT_RELATIVE_ROOT)
}

async function collectMarkdownFiles(dir: string, exclude: ReadonlySet<string>): Promise<string[]> {
  const out: string[] = []
  await walkMarkdown(dir, exclude, out)
  return out
}

async function walkMarkdown(dir: string, exclude: ReadonlySet<string>, out: string[]): Promise<void> {
  const entries: import('node:fs').Dirent[] = await fs.readdir(dir, { withFileTypes: true })
  for (const entry of entries) {
    const full = join(dir, entry.name)
    if (entry.isDirectory()) {
      if (exclude.has(entry.name)) continue
      await walkMarkdown(full, exclude, out)
    } else if (entry.isFile() && entry.name.endsWith('.md')) {
      out.push(full)
    }
  }
}

async function parseRoleFile(root: string, file: string): Promise<AgentRole | undefined> {
  const raw: string = await fs.readFile(file, 'utf8')
  const relPath = file.slice(root.length + 1)
  // walkMarkdown only yields `.md` files, so the basename always ends in `.md`.
  const segments = relPath.split(/[\\/]/)
  const lastSegment = segments[segments.length - 1] ?? relPath
  const id = lastSegment.replace(/\.md$/, '')
  const parsed = parseMarkdown(raw)
  if (parsed.displayName === '' && parsed.description === '') return undefined
  const family = familyOf(id, parsed.numericPrefix)
  return Object.freeze({
    id,
    family,
    numericPrefix: parsed.numericPrefix,
    displayName: parsed.displayName,
    ...parsed.displayNameZh !== undefined ? { displayNameZh: parsed.displayNameZh } : {},
    description: parsed.description,
    capabilities: Object.freeze(parsed.capabilities),
    ...parsed.license !== undefined ? { license: parsed.license } : {},
    path: `agents/${relPath.split(/[\\/]/).join('/')}`,
  })
}

interface ParsedMarkdown {
  displayName: string
  displayNameZh?: string
  description: string
  capabilities: string[]
  license?: string
  numericPrefix: string
}

function parseMarkdown(raw: string): ParsedMarkdown {
  const lines = raw.split(/\r?\n/)
  let displayName = ''
  let displayNameZh: string | undefined
  let description = ''
  const capabilities: string[] = []
  let license: string | undefined
  let numericPrefix = ''
  let inCapabilities = false
  let inFrontmatter = false
  let frontmatterClosed = false
  let sawFirstHeading = false

  for (const line of lines) {
    if (!frontmatterClosed) {
      if (line.trim() === '---') {
        if (!inFrontmatter) {
          inFrontmatter = true
          continue
        }
        frontmatterClosed = true
        inFrontmatter = false
        continue
      }
      if (inFrontmatter) {
        const fm = line.match(/^([A-Za-z_-]+):\s*(.*)$/)
        if (fm !== null && fm[1] === 'license' && typeof fm[2] === 'string') license = fm[2].trim()
        continue
      }
    }

    if (!sawFirstHeading) {
      const heading = line.match(/^#\s+(.+?)\s*$/)
      if (heading !== null && typeof heading[1] === 'string') {
        sawFirstHeading = true
        const text: string = heading[1]
        const zh = text.match(/[\u4e00-\u9fff]/)
        if (zh !== null) {
          displayNameZh = text
          displayName = text
        } else {
          displayName = text
        }
        numericPrefix = extractNumericPrefix(displayName)
        continue
      }
    }

    if (line.match(/^##\s+(能力|Capabilities)/) !== null) {
      inCapabilities = true
      continue
    }
    if (line.match(/^##\s+/) !== null) {
      inCapabilities = false
      continue
    }
    if (inCapabilities) {
      const bullet = line.match(/^\s*[-*]\s+(.+?)\s*$/)
      if (bullet !== null && typeof bullet[1] === 'string') capabilities.push(bullet[1])
      continue
    }

    if (description === '' && sawFirstHeading && line.trim() !== '' && !line.match(/^#/)) {
      description = line.trim()
    }
  }

  const out: ParsedMarkdown = { displayName, description, capabilities, numericPrefix }
  if (displayNameZh !== undefined) out.displayNameZh = displayNameZh
  if (license !== undefined) out.license = license
  return out
}

function extractNumericPrefix(displayName: string): string {
  const m = displayName.match(/^(\d{2})(?:-(\d{2}))?/)
  if (m === null || m[1] === undefined) return ''
  if (m[2] === undefined) return m[1]
  return `${m[1]}-${m[2]}`
}

function familyOf(id: string, prefix: string): AgentFamily {
  /* v8 ignore next -- String#split always yields at least one element;
   * the nullish coalesce is type-safe defensiveness for noUncheckedIndexedAccess. */
  const head = prefix.split('-')[0] ?? ''
  const headNum = Number.parseInt(head, 10)
  if (Number.isNaN(headNum)) {
    if (id.includes('finance')) return 'finance'
    if (id.includes('hr')) return 'hr'
    return 'unknown'
  }
  if (headNum <= 9) return 'core'
  if (headNum <= 15) return 'platform'
  if (headNum <= 19) return 'data'
  if (headNum <= 25) return 'business'
  if (headNum <= 29) return 'finance'
  if (headNum <= 35) return 'social'
  if (headNum <= 40) return 'sales'
  if (headNum <= 47) return 'commerce'
  if (headNum <= 89) return 'finance-2'
  /* v8 ignore else -- headNum > 99 falls through to unknown; dragon-engine's 00-99 numbering never produces this branch in practice. */
  if (headNum <= 99) return 'hr'
  /* v8 ignore next -- headNum is a parsed integer; values above 99 are extremely unlikely from dragon-engine's 00-99 numbering. */
  return 'unknown'
}

function compareRoles(a: AgentRole, b: AgentRole): number {
  if (a.numericPrefix !== b.numericPrefix) {
    if (a.numericPrefix === '') return 1
    if (b.numericPrefix === '') return -1
    return a.numericPrefix < b.numericPrefix ? -1 : 1
  }
  /* v8 ignore next -- Roster ids are unique; the equality branch is type-safe defensiveness only. */
  return a.id < b.id ? -1 : a.id > b.id ? 1 : 0
}

function matchesNeedle(role: AgentRole, needle: string): boolean {
  if (role.id.toLowerCase().includes(needle)) return true
  if (role.displayName.toLowerCase().includes(needle)) return true
  if (role.description.toLowerCase().includes(needle)) return true
  if (role.capabilities.some(c => c.toLowerCase().includes(needle))) return true
  if (typeof role.license === 'string' && role.license.toLowerCase().includes(needle)) return true
  return false
}

export default AgentRoster
export type { AgentFamily, AgentId, AgentRole, Config, RoleSearchQuery } from './types'
export type { AgentRosterConfig }
