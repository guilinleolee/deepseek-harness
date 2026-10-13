/**
 * Dragon Bridge public types.
 *
 * @module @deepseek-ai/dsh-experimental-dragon-bridge
 */

import type { AssetIndexEntry } from '@deepseek-ai/dsh-experimental-skill-index'
import type { AgentRole } from '@deepseek-ai/dsh-experimental-agent-roster'
import type {
  LicenseDecision,
  LicenseEvaluation,
  LicenseTier,
} from '@deepseek-ai/dsh-experimental-license-policy'

/** Cross-kind entry that wraps either a skill, agent, command, hook, or plugin. */
export interface DragonAsset {
  /** The source asset; shape depends on `kind`. */
  readonly source: AssetIndexEntry | AgentRole
  /** Discriminator used by callers to narrow the union. */
  readonly kind: 'skill' | 'agent' | 'command' | 'hook' | 'plugin'
  /** Resolved license tier for this asset. */
  readonly licenseTier: LicenseTier
  /** Resolved license evaluation; mirrors the policy's verdict. */
  readonly licenseEvaluation: LicenseEvaluation
  /** Convenience: the decision applied to this asset. */
  readonly decision: LicenseDecision
}

/** Filter criteria for {@link DragonBridge.search}. */
export interface BridgeSearchQuery {
  /** Restrict to one asset kind; omitted matches every kind. */
  kind?: 'skill' | 'agent' | 'command' | 'hook' | 'plugin'
  /** Substring match against id, description, triggers, tags, upstream, display name. */
  text?: string
  /** Restrict to one license tier. */
  license?: LicenseTier
  /** Restrict to one decision; omitted matches every decision. */
  decision?: LicenseDecision
  /** Cap the result count; omitted returns every match. */
  limit?: number
}

/** Loaded configuration for {@link DragonBridge}. */
export interface Config {
  /** Filesystem root of the dragon-assets mirror; passed to skill-index and agent-roster. */
  dragonAssetsRoot?: string
  /** When true, decisions are filtered to `allow` + `attribute` only by default. */
  safeOnly?: boolean
}
