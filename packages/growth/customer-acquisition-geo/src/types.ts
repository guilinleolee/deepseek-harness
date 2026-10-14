/**
 * Wire and tool value types for the GEO module. Storage record types live in
 * the main package's data contract; everything here is the plain projection
 * the model sees — no branded ids, no readonly aliases — so the tool output
 * schemas and the values stay in one type family.
 * @module @deepseek-ai/dsh-customer-acquisition-geo/types
 */

/** Canonical return value of `customer_acquisition_geo_scan`. */
export interface GeoScanValue {
  readonly scan_id: string
  readonly score: number
  readonly findings_count: number
  readonly pages_fetched: number
  readonly robots_skipped_paths: string[]
  readonly llms_txt: string
  readonly report_md: string
}

/** One row of `customer_acquisition_geo_history`. */
export interface GeoHistoryItem {
  readonly scan_id: string
  readonly report_id: string
  readonly url: string
  readonly status: string
  readonly score: number
  readonly pages_fetched: number
  readonly started_at: number
}

/** History list request mirrors the manifest's filter set. */
export interface GeoHistoryRequest {
  url_filter?: string
  from?: number
  to?: number
  limit?: number
  offset?: number
}

/** One finding projected to the wire. */
export interface GeoFindingValue {
  readonly id: string
  readonly category: string
  readonly severity: string
  readonly title: string
  readonly detail: string
  readonly evidence_page?: string
}

/** Canonical return value of `customer_acquisition_geo_report_get`. */
export interface GeoReportValue {
  readonly report: {
    readonly id: string
    readonly scan_id: string
    readonly url: string
    readonly score: number
    readonly findings: GeoFindingValue[]
    readonly llms_txt: string
    readonly report_md: string
    readonly robots_skipped_paths: string[]
    readonly created_at: number
  }
}

/** Canonical return value of `customer_acquisition_geo_compare`. */
export interface GeoCompareValue {
  readonly score_a: number
  readonly score_b: number
  readonly score_delta: number
  readonly resolved: string[]
  readonly introduced: string[]
  readonly summary_md: string
}
