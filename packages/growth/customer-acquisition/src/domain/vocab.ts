/**
 * Known-value vocabularies for the domain's open enums (data contract §2.3).
 * The durable schema stores these fields as plain non-empty strings so new
 * values never require a domain version bump; UI dropdowns and tool
 * descriptions render this list, and unknown stored values fall through and
 * display verbatim.
 * @module @deepseek-ai/dsh-customer-acquisition/domain/vocab
 */

/** Where a lead came from. */
export const KNOWN_LEAD_SOURCES = ['manual', 'form', 'chat', 'email', 'referral', 'geo_scan'] as const

/** Nurture-copy types; extended values are allowed and rendered verbatim. */
export const KNOWN_CONTENT_TYPES = [
  'wecom_first_touch',
  'sms_followup',
  'email_drip',
  'short_video_script',
  'xiaohongshu_post',
  'website_product_intro',
  'customer_case',
] as const

/** Company-size buckets. */
export const KNOWN_COMPANY_SIZES = ['1-10', '11-50', '51-200', '201-1000', '1000+'] as const

/** Comma-joined forms reused inside tool descriptions. */
export const LEAD_SOURCES_HINT = KNOWN_LEAD_SOURCES.join('/')
export const CONTENT_TYPES_HINT = KNOWN_CONTENT_TYPES.join('/')
export const COMPANY_SIZES_HINT = KNOWN_COMPANY_SIZES.join('/')

/**
 * Fold one free-text industry name to its comparison form: trim, drop every
 * whitespace run, and lowercase. `industry` is open free text on both leads and
 * templates, so the same industry reaches storage as `B2B工厂商贸` from a lead
 * and `B2B 工厂商贸` from a seeded template; comparing raw strings would read
 * that stray space as a different industry and mis-route the template.
 * @param industry - the raw stored value, possibly undefined.
 * @returns the folded comparison key; empty when there is nothing to compare.
 */
export function normalizeIndustry(industry: string | undefined): string {
  if (industry === undefined) return ''
  return industry.replace(/\s+/g, '').toLowerCase()
}
