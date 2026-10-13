/**
 * Dragon Engine license policy types.
 *
 * Six license tiers, matching `dragon-engine memory/agpl-attribution-statements.md`
 * and the upstream DSH ecosystem license policy (`dsh-ecosystem-license-policy`).
 *
 * @module @deepseek-ai/dsh-experimental-license-policy
 */

/** License tier classification for a single asset. */
export type LicenseTier =
  /** MIT — zero red-line. */
  | 'mit'
  /** Apache-2.0 — NOTICE + "Modified by" segment required. */
  | 'apache-2.0'
  /** BSD-3-Clause — copyright + no-author-endorsement required. */
  | 'bsd-3-clause'
  /** AGPL-3.0 — red-line: only PNG / artifact delivery, no SaaS. */
  | 'agpl-3.0'
  /** NOASSERTION — blacklisted under DSH governance baseline. */
  | 'noassertion'
  /** Unrecognized or absent license marker. */
  | 'unknown'

/** Severity classification derived from the tier. */
export type LicenseSeverity = 'green' | 'amber' | 'red' | 'black'

/** Decision returned by {@link LicensePolicy.evaluate}. */
export type LicenseDecision =
  /** Asset may be loaded and surfaced to the model. */
  | 'allow'
  /** Asset may be loaded but must carry an attribution block. */
  | 'attribute'
  /** Asset may be loaded only as a local artifact (no network distribution). */
  | 'artifact-only'
  /** Asset must not be loaded; reject at the boundary. */
  | 'reject'

/** Result of evaluating one asset's license tier. */
export interface LicenseEvaluation {
  /** The detected tier. */
  readonly tier: LicenseTier
  /** The severity bucket. */
  readonly severity: LicenseSeverity
  /** The decision applied to this asset. */
  readonly decision: LicenseDecision
  /** Required attribution string when decision is `attribute`. */
  readonly attribution?: string
  /** Reason text suitable for log/audit when decision is `artifact-only` or `reject`. */
  readonly reason?: string
}

/** Configuration for {@link LicensePolicy}. */
export interface Config {
  /**
   * Treat `unknown` as `reject` instead of `allow`. Default `false`: unknown
   * assets pass through with attribution but no network deployment.
   */
  rejectUnknown?: boolean
  /**
   * Override the default AGPL attribution text. The placeholder string is
   * supplied by `dragon-assets/LICENSE-ATTRIBUTION.md` §三.
   */
  agplAttribution?: string
}
