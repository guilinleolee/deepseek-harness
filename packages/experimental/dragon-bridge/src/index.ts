/**
 * Dragon Bridge facade.
 *
 * Unifies `skill-index`, `agent-roster`, and `license-policy` behind a single
 * service so DSH consumers can query the dragon-assets mirror with one
 * `dragonBridge.search()` call and trust that AGPL / NOASSERTION entries
 * have already been filtered or flagged per the license policy.
 *
 * Lifecycle: requires the three upstream packages to be registered first.
 * The bridge loads the skill index and agent roster on first use, then
 * resolves each entry through the policy. Results are cached until the
 * next `loadAll()`.
 *
 * @module @deepseek-ai/dsh-experimental-dragon-bridge
 */

import { Service } from '@deepseek-ai/cordis'
import type {
  AssetIndexEntry,
  AssetKind as IndexKind,
} from '@deepseek-ai/dsh-experimental-skill-index'
import type { AgentRole } from '@deepseek-ai/dsh-experimental-agent-roster'
import type { BridgeSearchQuery, Config, DragonAsset } from './types'

const SKILL_INDEX_KINDS: ReadonlyArray<IndexKind> = ['skill', 'agent', 'hook', 'command', 'plugin']
const AGENT_ROLE_KIND = 'agent' as const

declare module '@deepseek-ai/cordis' {
  interface Context {
    /** The Dragon Engine bridge facade. */
    dragonBridge: DragonBridge
  }
}

/**
 * Facade that joins the index, roster, and policy services.
 *
 * The bridge does not own disk state; it depends on its sibling packages for
 * I/O and classification. Its only state is a cached asset list rebuilt by
 * `loadAll()`.
 */
export class DragonBridge extends Service {
  private readonly safeOnly: boolean
  private assets: readonly DragonAsset[] = []

  constructor(ctx: import('@deepseek-ai/cordis').Context, config: Partial<Config> = {}) {
    super(ctx, 'dragonBridge')
    this.safeOnly = config.safeOnly ?? false
  }

  /**
   * Refresh every upstream service and rebuild the cross-kind asset list.
   *
   * Skill and command / hook / plugin assets come from `ctx.dragonIndex`;
   * agent assets come from `ctx.agentRoster`. Each entry is classified by
   * `ctx.licensePolicy`. Returns the rebuilt list.
   */
  async loadAll(): Promise<readonly DragonAsset[]> {
    const skillIndex = this.ctx.dragonIndex
    const agentRoster = this.ctx.agentRoster
    const licensePolicy = this.ctx.licensePolicy

    await Promise.all([skillIndex.loadAll(), agentRoster.loadAll()])

    const merged: DragonAsset[] = []
    for (const kind of SKILL_INDEX_KINDS) {
      const entries = skillIndex.search({ kind })
      for (const entry of entries) {
        merged.push(wrapIndexEntry(entry, kind, licensePolicy))
      }
    }
    for (const role of agentRoster.roles) {
      merged.push(wrapAgentRole(role, licensePolicy))
    }

    this.assets = Object.freeze(merged)
    return this.assets
  }

  /** The currently cached cross-kind asset list. */
  get assets$(): readonly DragonAsset[] {
    return this.assets
  }

  /**
   * Filter the cached asset list.
   *
   * `safeOnly` (constructor flag) drops `artifact-only` and `reject` entries
   * from the default result set; explicit `decision` overrides it.
   *
   * @param query - filter criteria; missing fields do not restrict.
   * @returns matching assets, in the source-declared order.
   */
  search(query: BridgeSearchQuery = {}): readonly DragonAsset[] {
    const needle = query.text?.toLowerCase()
    const matched = this.assets.filter((asset) => {
      if (query.kind !== undefined && asset.kind !== query.kind) return false
      if (query.license !== undefined && asset.licenseTier !== query.license) return false
      if (query.decision !== undefined && asset.decision !== query.decision) return false
      if (this.safeOnly && query.decision === undefined && (asset.decision === 'artifact-only' || asset.decision === 'reject')) return false
      if (needle !== undefined && !matchesNeedle(asset, needle)) return false
      return true
    })
    return typeof query.limit === 'number' ? matched.slice(0, query.limit) : matched
  }

  /** Return every asset the policy resolves to `allow`. */
  allowed(): readonly DragonAsset[] {
    return this.assets.filter(asset => asset.decision === 'allow')
  }

  /** Return every asset the policy resolves to `attribute`. */
  attributed(): readonly DragonAsset[] {
    return this.assets.filter(asset => asset.decision === 'attribute')
  }

  /** Return every asset the policy resolves to `artifact-only`. */
  artifactOnly(): readonly DragonAsset[] {
    return this.assets.filter(asset => asset.decision === 'artifact-only')
  }

  /** Return every asset the policy resolves to `reject`. */
  rejected(): readonly DragonAsset[] {
    return this.assets.filter(asset => asset.decision === 'reject')
  }
}

function wrapIndexEntry(
  entry: AssetIndexEntry,
  kind: DragonAsset['kind'],
  licensePolicy: import('@deepseek-ai/dsh-experimental-license-policy').default,
): DragonAsset {
  const evaluation = licensePolicy.evaluate(entry.license ?? null)
  return Object.freeze({
    source: entry,
    kind,
    licenseTier: evaluation.tier,
    licenseEvaluation: evaluation,
    decision: evaluation.decision,
  })
}

function wrapAgentRole(
  role: AgentRole,
  licensePolicy: import('@deepseek-ai/dsh-experimental-license-policy').default,
): DragonAsset {
  const evaluation = licensePolicy.evaluate(role.license ?? null)
  return Object.freeze({
    source: role,
    kind: AGENT_ROLE_KIND,
    licenseTier: evaluation.tier,
    licenseEvaluation: evaluation,
    decision: evaluation.decision,
  })
}

function matchesNeedle(asset: DragonAsset, needle: string): boolean {
  if (asset.source.id.toLowerCase().includes(needle)) return true
  const description = describeSource(asset.source)
  if (description.toLowerCase().includes(needle)) return true
  return false
}

function describeSource(source: AssetIndexEntry | AgentRole): string {
  // Both AssetIndexEntry and AgentRole carry an optional description. The
  // bridge's matcher only needs a non-empty string to feed into the search
  // needle, so the empty-string fallback keeps the type contract intact
  // without a second-pass through the source object.
  const desc = (source as { description?: unknown }).description
  return typeof desc === 'string' ? desc : ''
}

export default DragonBridge
export type { BridgeSearchQuery, Config, DragonAsset } from './types'
