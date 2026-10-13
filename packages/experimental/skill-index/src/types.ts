/**
 * Dragon Engine asset index entry schema.
 *
 * Each line of `dragon-assets/index/{SKILLS,AGENTS,HOOKS,COMMANDS,PLUGINS}.jsonl`
 * represents one asset entry. The schema mirrors the dragon-index/1.0 format
 * declared by the upstream `dragon-engine` project's `INDEX_MASTER.json`.
 *
 * @module @deepseek-ai/dsh-experimental-skill-index
 */

/** Asset kind discriminator matching `INDEX_MASTER.json` counts. */
export type AssetKind = 'skill' | 'agent' | 'hook' | 'command' | 'plugin'

/** License tier classification derived from upstream LICENSE markers. */
export type LicenseTier = 'mit' | 'apache-2.0' | 'bsd-3-clause' | 'agpl-3.0' | 'noassertion' | 'unknown'

/** Discovery status flag for downstream consumers. */
export type AssetStatus = 'active' | 'deprecated' | 'experimental' | 'archived' | 'unknown'

/**
 * One asset index entry decoded from a jsonl line.
 *
 * The schema is intentionally permissive on unknown fields: dragon-engine
 * updates its schema over time and we read whatever fields the file carries,
 * typed access goes through the documented accessors.
 */
export interface AssetIndexEntry {
  /** Required: stable identifier matching the asset directory or filename basename. */
  id: string
  /** Required: discriminator used to pick the right jsonl file. */
  kind: AssetKind
  /** Optional semantic version. */
  version?: string
  /** Optional discovery status flag. */
  status?: AssetStatus
  /** Optional license tier (normalized). */
  license?: LicenseTier
  /** Optional upstream source label, e.g. `SamurAIGPT/Generative-Media-Skills`. */
  upstream?: string
  /** Required: workspace-relative path inside `dragon-assets/`. */
  path: string
  /** Optional frontmatter or frontmatter-derived description. */
  description?: string
  /** Optional trigger phrases for hot-path routing. */
  triggers?: string[]
  /** Optional general tags. */
  tags?: string[]
  /** Optional mtime in ISO format. */
  mtime?: string
  /** Optional SHA-256 hash. */
  hash?: string
  /** Optional extra fields preserved by the reader. */
  [extra: string]: unknown
}

/** Loaded configuration for {@link DragonAssetIndex}. */
export interface Config {
  /**
   * Absolute filesystem path to the `dragon-assets/` mirror root.
   * Default: `<workspace>/dragon-assets`.
   */
  dragonAssetsRoot: string
}

/** Index snapshot returned by {@link DragonAssetIndex.loadAll}. */
export interface IndexSnapshot {
  /** Skill entries from `dragon-assets/index/SKILLS.jsonl`. */
  readonly skills: readonly AssetIndexEntry[]
  /** Agent entries from `dragon-assets/index/AGENTS.jsonl`. */
  readonly agents: readonly AssetIndexEntry[]
  /** Hook entries from `dragon-assets/index/HOOKS.jsonl`. */
  readonly hooks: readonly AssetIndexEntry[]
  /** Command entries from `dragon-assets/index/COMMANDS.jsonl`. */
  readonly commands: readonly AssetIndexEntry[]
  /** Plugin entries from `dragon-assets/index/PLUGINS.jsonl`. */
  readonly plugins: readonly AssetIndexEntry[]
  /** Combined entry list, useful for cross-kind queries. */
  readonly all: readonly AssetIndexEntry[]
}

/** Filter criteria for {@link DragonAssetIndex.search}. */
export interface SearchQuery {
  /** Restrict to one kind; omitted matches every kind. */
  kind?: AssetKind
  /** Substring match against `id`, `description`, `triggers`, `tags`, `upstream`. */
  text?: string
  /** Restrict to one license tier. */
  license?: LicenseTier
  /** Cap the result count; omitted returns every match. */
  limit?: number
}
