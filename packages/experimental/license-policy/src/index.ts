/**
 * Dragon Engine license policy service.
 *
 * Classifies one asset by its license tier and returns a decision that
 * downstream code (skill loaders, tool publishers, the dragon bridge) can
 * enforce at the boundary. This package owns no I/O — callers feed it the
 * license string they already discovered (frontmatter, LICENSE sniff, or
 * upstream metadata) and read back a typed decision.
 *
 * Tier → decision matrix (matches `dragon-assets/LICENSE-ATTRIBUTION.md`):
 *
 * | Tier         | Severity | Default decision | Notes |
 * |--------------|----------|------------------|-------|
 * | mit          | green    | allow            | zero red-line |
 * | apache-2.0   | green    | attribute        | NOTICE + Modified by |
 * | bsd-3-clause | green    | attribute        | no-author-endorsement |
 * | agpl-3.0     | red      | artifact-only    | red-line: no SaaS |
 * | noassertion  | black    | reject           | DSH governance baseline |
 * | unknown      | amber    | attribute        | unless `rejectUnknown` |
 *
 * @module @deepseek-ai/dsh-experimental-license-policy
 */

import { Service } from '@deepseek-ai/cordis'
import type {
  Config,
  LicenseDecision,
  LicenseEvaluation,
  LicenseSeverity,
  LicenseTier,
} from './types'

const DEFAULT_AGPL_ATTRIBUTION = [
  'WARNING: This asset is licensed under AGPL-3.0.',
  'Network deployment is PROHIBITED.',
  'Distribution must be under the same license with full source disclosure.',
  'See: https://www.gnu.org/licenses/agpl-3.0.html',
].join(' ')

declare module '@deepseek-ai/cordis' {
  interface Context {
    /** License policy evaluator, registered as a singleton per Context. */
    licensePolicy: LicensePolicy
  }
}

/**
 * Singleton license policy evaluator.
 *
 * One Service instance owns the tier-to-decision table and (optional)
 * AGPL attribution text. Pure: no I/O, no filesystem, no event subscription.
 */
export class LicensePolicy extends Service {
  private readonly rejectUnknown: boolean
  private readonly agplAttribution: string

  constructor(ctx: import('@deepseek-ai/cordis').Context, config: Partial<Config> = {}) {
    super(ctx, 'licensePolicy')
    this.rejectUnknown = config.rejectUnknown ?? false
    this.agplAttribution = config.agplAttribution ?? DEFAULT_AGPL_ATTRIBUTION
  }

  /** Whether unknown tiers are rejected by default. */
  get rejectsUnknown(): boolean {
    return this.rejectUnknown
  }

  /** The configured AGPL attribution text. */
  get agplNotice(): string {
    return this.agplAttribution
  }

  /**
   * Normalize an arbitrary license string to a {@link LicenseTier}.
   *
   * Accepts values lifted directly from frontmatter, package.json, or
   * upstream registry metadata. Matching is case-insensitive; whitespace and
   * surrounding `()` are stripped. `NOASSERTION`, `UNKNOWN`, and absent
   * values each map to a distinct tier rather than collapsing into `unknown`.
   *
   * @param raw - the license string discovered upstream.
   * @returns the normalized tier.
   */
  normalize(raw: string | null | undefined): LicenseTier {
    if (raw === null || raw === undefined) return 'unknown'
    const cleaned = raw.trim().toLowerCase().replace(/[()]/g, '')
    if (cleaned === '') return 'unknown'
    if (cleaned === 'noassertion' || cleaned === 'no-assertion') return 'noassertion'
    if (cleaned.includes('agpl')) return 'agpl-3.0'
    if (cleaned.includes('apache')) return 'apache-2.0'
    if (cleaned.includes('bsd-3') || cleaned.includes('bsd 3') || cleaned.includes('bsd_3')) return 'bsd-3-clause'
    if (cleaned.includes('bsd')) return 'unknown'
    if (cleaned.includes('mit')) return 'mit'
    return 'unknown'
  }

  /**
   * Evaluate one license tier and return the typed decision.
   * @param raw - the license string discovered upstream.
   * @returns the evaluation result.
   */
  evaluate(raw: string | null | undefined): LicenseEvaluation {
    const tier = this.normalize(raw)
    return this.evaluateTier(tier)
  }

  /**
   * Evaluate an already-normalized tier.
   * @param tier - the normalized license tier.
   * @returns the evaluation result.
   */
  evaluateTier(tier: LicenseTier): LicenseEvaluation {
    const severity = severityOf(tier)
    const decision = decisionFor(tier, this.rejectUnknown)
    switch (decision) {
      case 'allow':
        return { tier, severity, decision }
      case 'attribute':
        return { tier, severity, decision, attribution: attributionFor(tier) }
      case 'artifact-only':
        return {
          tier,
          severity,
          decision,
          attribution: this.agplAttribution,
          reason: 'AGPL-3.0 red-line: deliver as PNG / artifact only; never deploy as a network service.',
        }
      case 'reject':
        return {
          tier,
          severity,
          decision,
          reason: 'NOASSERTION rejected under DSH ecosystem governance baseline.',
        }
    }
  }

  /**
   * Convenience: assert the evaluation result is one of the allowed decisions.
   * @param raw - the license string discovered upstream.
   * @param allowed - the set of decisions the caller accepts.
   * @returns the evaluation result, throwing if it falls outside `allowed`.
   */
  assertAllowed(raw: string | null | undefined, allowed: readonly LicenseDecision[]): LicenseEvaluation {
    const evaluation = this.evaluate(raw)
    if (!allowed.includes(evaluation.decision)) {
      throw new Error(`licensePolicy: ${evaluation.tier} decision=${evaluation.decision} is not in the allowed set [${allowed.join(', ')}]`)
    }
    return evaluation
  }
}

function severityOf(tier: LicenseTier): LicenseSeverity {
  switch (tier) {
    case 'mit':
    case 'apache-2.0':
    case 'bsd-3-clause':
      return 'green'
    case 'agpl-3.0':
      return 'red'
    case 'noassertion':
      return 'black'
    case 'unknown':
      return 'amber'
  }
}

function decisionFor(tier: LicenseTier, rejectUnknown: boolean): LicenseDecision {
  switch (tier) {
    case 'mit':
      return 'allow'
    case 'apache-2.0':
    case 'bsd-3-clause':
      return 'attribute'
    case 'agpl-3.0':
      return 'artifact-only'
    case 'noassertion':
      return 'reject'
    case 'unknown':
      return rejectUnknown ? 'reject' : 'attribute'
  }
}

function attributionFor(tier: LicenseTier): string {
  switch (tier) {
    case 'apache-2.0':
      return 'Apache-2.0 attribution required: keep LICENSE + NOTICE; add a "Modifications by dragon-engine" segment.'
    case 'bsd-3-clause':
      return 'BSD-3-Clause attribution required: preserve copyright; do not use author names for endorsement.'
    case 'unknown':
      return 'Unknown license — confirm upstream before redistribution; add an attribution block as a precaution.'
    /* v8 ignore next -- LicenseTier is a closed union; `allow`/`artifact-only`/`reject` callers do not pass through attribution. */
    default:
      return ''
  }
}

export default LicensePolicy
export type { Config, LicenseDecision, LicenseEvaluation, LicenseSeverity, LicenseTier } from './types'
