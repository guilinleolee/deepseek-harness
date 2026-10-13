/**
 * Dragon Engine agent role types.
 *
 * Roles follow the upstream dragon-engine 00-99 numbering scheme:
 *
 * | Family | Range | Example |
 * |---|---|---|
 * | core | 00-09 | 00-analyst, 01-investigator, 02-architect, 03-builder, 04-validator |
 * | platform | 10-19 | 10-02-ai-researcher, 13-designer, 14-product-manager |
 * | data | 16-19 | 16-devops, 16-monitor, 17-data-analyst |
 * | business | 22-25 | 22-brand-planner, 25-marketing-strategy-planner |
 * | finance | 28-29 | 28-copywriter, 28-10-finance-data-base, 28-trend-forecast |
 * | social | 31-35 | 35-06-blogger-distiller, 35-marketing-automation |
 * | sales | 38-40 | 38-pr-communications, 40-customer-success |
 * | commerce | 45-47 | 45-ecommerce, 47-event-planner |
 * | finance-2 | 60-89 | 64-algo-trader, 73-compliance-master, 80-cfo |
 * | hr | 90-99 | 90-hr-director, 93-recruiter, 99-employee-relations |
 *
 * @module @deepseek-ai/dsh-experimental-agent-roster
 */

/** Family bucket, used to group roles for selection without parsing the id. */
export type AgentFamily =
  | 'core'
  | 'platform'
  | 'data'
  | 'business'
  | 'finance'
  | 'social'
  | 'sales'
  | 'commerce'
  | 'finance-2'
  | 'hr'
  | 'unknown'

/** Stable identifier matching the source markdown filename basename (without `.md`). */
export type AgentId = string

/** One registered agent role in the dragon-engine mirror. */
export interface AgentRole {
  /** Stable identifier — typically `${family-prefix}-${slug}`. */
  readonly id: AgentId
  /** Family bucket the role belongs to. */
  readonly family: AgentFamily
  /** Two-digit numeric prefix used in upstream 00-99 ordering. */
  readonly numericPrefix: string
  /** Display name, human-readable. */
  readonly displayName: string
  /** Chinese display name when the source markdown provides one. */
  readonly displayNameZh?: string
  /** Short description taken from the first paragraph of the source markdown. */
  readonly description: string
  /** Capability keywords for routing. */
  readonly capabilities: readonly string[]
  /** Optional upstream license tier (mirrors the asset index convention). */
  readonly license?: string
  /** Absolute path inside `dragon-assets/agents/` for the source markdown. */
  readonly path: string
}

/** Filter criteria for {@link AgentRoster.search}. */
export interface RoleSearchQuery {
  /** Restrict to one family bucket. */
  family?: AgentFamily
  /** Substring match against id, displayName, description, capabilities. */
  text?: string
  /** Restrict to one license tier. */
  license?: string
  /** Cap the result count; omitted returns every match. */
  limit?: number
}

/** Base configuration shared by all dragon-assets service families. */
export interface Config {
  /**
   * Filesystem root for the dragon-assets mirror; consumed by services that
   * read files out of the mirror.
   */
  dragonAssetsRoot?: string
}
