/**
 * Wire value types shared by the Remote service and the browser panel.
 * Plain projections — no branded ids, no readonly aliases — so the Remote
 * client and the panel stay in one type family (the customer-acquisition
 * types-subpath pattern).
 * @module @deepseek-ai/dsh-quant-research/types
 */

/** Account summary projected to the wire (no internal bookkeeping fields). */
export interface AccountSummaryValue {
  account_id: string
  name: string
  cash: number
  initial_cash: number
  equity: number
  positions: { symbol: string; shares: number; avg_cost: number; market_value: number }[]
}

/** Research-note summary projected to the wire. */
export interface NoteSummaryValue {
  note_id: string
  title: string
  body: string
  symbol: string | null
  tags: string[]
  created_at: number
}

/** The account-list projection. */
export interface AccountListValue {
  accounts: AccountSummaryValue[]
}

/** The note-list projection. */
export interface NoteListValue {
  notes: NoteSummaryValue[]
}

/** Reference for one account lookup: by id or by name. */
export interface AccountRef {
  account_id?: string
  name?: string
}
