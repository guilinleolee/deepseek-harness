# Platform services

English | [中文](platform-services.zh.md)

The product-platform services layered on the harness core: quantitative research, customer acquisition with its GEO diagnosis module, and the dragon-assets bridge stack. Each service owns its durable state through the [storage-domain](../architecture.md) seam, and every model- or browser-facing method resolves its operator per call through the `permissionContext` seam rather than caching an identity.

Source: [`packages/quant/quant-research/src/service.ts`](../../packages/quant/quant-research/src/service.ts), [`packages/growth/customer-acquisition/src/service.ts`](../../packages/growth/customer-acquisition/src/service.ts), [`packages/growth/customer-acquisition-geo/src/service.ts`](../../packages/growth/customer-acquisition-geo/src/service.ts), [`packages/experimental/dragon-bridge/src/index.ts`](../../packages/experimental/dragon-bridge/src/index.ts)

## Quant research

[`@deepseek-ai/dsh-quant-research`](../../packages/quant/quant-research) owns virtual trading accounts, research notes, and persisted backtest snapshots. The remote face reads account summaries, note and snapshot lists, and one snapshot's equity curve; ids are branded and an unknown id rejects with a friendly error.

Source: [`packages/quant/quant-research/src/service.ts`](../../packages/quant/quant-research/src/service.ts)

## Customer acquisition

[`@deepseek-ai/dsh-customer-acquisition`](../../packages/growth/customer-acquisition) owns the lead ledger, scoring runs, nurture copy, SOP tasks, global settings, and the audit log. It is the single owner of the frozen v1 domain; the module services (ledger, scoring, content, SOP) borrow its tables, and both the browser Remote face and the model tools serve reads through one authority.

Source: [`packages/growth/customer-acquisition/src/service.ts`](../../packages/growth/customer-acquisition/src/service.ts)

## GEO diagnosis

[`@deepseek-ai/dsh-customer-acquisition-geo`](../../packages/growth/customer-acquisition-geo) runs bounded website scans, scores each report, and serves history, single-report, and cross-report comparison reads. A failed denial audit never un-denies the call: the auditor warns and continues.

Source: [`packages/growth/customer-acquisition-geo/src/service.ts`](../../packages/growth/customer-acquisition-geo/src/service.ts)

## Dragon assets bridge

The dragon-assets stack turns the `dragon-assets/` mirror into a licensed, searchable catalog. [`@deepseek-ai/dsh-experimental-agent-roster`](../../packages/experimental/agent-roster) parses the agent-role markdowns, [`@deepseek-ai/dsh-experimental-skill-index`](../../packages/experimental/skill-index) indexes skills and command assets, [`@deepseek-ai/dsh-experimental-license-policy`](../../packages/experimental/license-policy) classifies each asset into an `allow` / `attribute` / `artifact-only` / `reject` tier, and [`@deepseek-ai/dsh-experimental-dragon-bridge`](../../packages/experimental/dragon-bridge) merges both sources into one cross-kind, license-annotated asset list.

Source: [`packages/experimental/dragon-bridge/src/index.ts`](../../packages/experimental/dragon-bridge/src/index.ts)

<!-- BEGIN GENERATED cordis-surface (gen-cordis-catalog.ts) — do not edit between markers -->

<a id="cordis-surface"></a>

## Cordis API

Generated from source by `scripts/gen-cordis-catalog.ts` (verified fresh by `pnpm run verify-cordis-catalog` in doc-sync; regenerate with `pnpm run gen-cordis-catalog`) — the language sides differ only in locale-specific paired document paths. Signature blocks use a `ts cordis-catalog` fence and keep the original source JSDoc; dispatch modes are defined in the [primer](../cordis-primer.md#dispatch-modes), and the framework-inherited `ctx` API lives in [cordis-api/inherited.md](../cordis-api/inherited.md).

<a id="ctxagentroster--agentroster"></a>

### `ctx.agentRoster` — `AgentRoster`

Read-only registry over the `dragon-assets/agents/` source markdowns.

One service instance owns one snapshot; call `loadAll()` after upstream mirror changes to refresh.

```ts cordis-catalog
/**
 * Walk the `agents/` mirror and parse every markdown file into a role.
 * @returns the loaded roster, sorted by numeric prefix then id.
 */
async loadAll(): Promise<readonly AgentRole[]>

/**
 * Filter the cached roster.
 * @param query - filter criteria; missing fields do not restrict.
 * @returns matching roles, sorted as the source roster declared them.
 */
search(query: RoleSearchQuery = {}): readonly AgentRole[]

/**
 * Exact-id lookup against the cached roster.
 * @param id - the role identifier (without `.md`).
 * @returns the matching role, or `undefined` if none.
 */
get(id: AgentId): AgentRole | undefined

/** Return every role belonging to one family bucket.
 * @param family - the family bucket to select.
 * @returns every cached role in that family, in roster order. */
byFamily(family: AgentFamily): readonly AgentRole[]
```

Source: [`packages/experimental/agent-roster/src/index.ts`](../../packages/experimental/agent-roster/src/index.ts)

<a id="ctxcustomeracquisition--customeracquisitionservice"></a>

### `ctx.customerAcquisition` — `CustomerAcquisitionService`

Storage-backed customer-acquisition service. The domain opens once at service init and closes with the owning fiber; every read is synchronous from memory, every write durable-first.

```ts cordis-catalog
/** Authoritative audit handle, valid after init; a miss is a broken lifecycle.
 * @returns the durable audit-log table handle. */
requireAuditTable(): AuditTable

/**
 * Authoritative domain, valid after init; a miss is a broken lifecycle.
 * Open to the P1 module services (lead ledger, scoring), which borrow the
 * domain's tables — the P0 service stays its single owner and closer.
 * @returns the open frozen v1 domain.
 */
requireDomain(): Domain<typeof customerAcquisitionDomainSpec>

/** Current settings, projected to the exact-optional wire shape.
 * @returns the current global settings. */
getSettings(): SettingsValue

/**
 * Merge a partial settings update, validate referenced templates exist,
 * persist, and audit. Referencing an unknown profile or template fails
 * loud with a friendly error instead of storing a dangling id.
 * @param patch - fields to change; omitted fields keep their value.
 * @param operator - the caller's resolved operator.
 * @param channel - which surface performed the write.
 * @returns the settings after the write.
 */
async updateSettings( patch: SettingsPatchInput, operator: ResolvedOperator, channel: OperatorChannel, ): Promise<SettingsValue>

/**
 * Filter the audit log for list and export faces.
 * @param request - filters plus paging bounds.
 * @returns the matching page, newest first, with the unfiltered total.
 */
listAudit(request: AuditListRequest): AuditListValue

/**
 * All audit records matching the filter, unpaged — the export face.
 * @param filter - filters without paging bounds.
 * @returns every matching record, newest first.
 */
exportAudit(filter: Omit<AuditListRequest, 'limit' | 'offset'>): AuditListValue['items']

/** Read face for the browser panel.
 * @returns the current settings wrapped for the wire. */
@Remote('getSettings') getSettingsRemote(): Promise<SettingsSnapshotValue>

/** Write face for the browser panel; resolves the web operator per call.
 * @param patch - fields to change; omitted fields keep their value.
 * @returns the settings after the write. */
@Remote('updateSettings') async updateSettingsRemote(patch: SettingsPatchInput): Promise<SettingsSnapshotValue>

/** Audit read face for the browser panel.
 * @param request - filters plus paging bounds.
 * @returns the matching page, newest first, with the unfiltered total. */
@Remote('listAuditLogs') async listAuditLogs(request: AuditListRequest): Promise<AuditListValue>

/**
 * Dashboard read face: the seven overview metrics through the same
 * aggregation the model tool serves. Resolves the web operator per call so
 * `lead_scope=own` panels never see another operator's leads.
 * @param request - overview scope and lead-scope selection.
 * @returns the dashboard overview for the resolved operator.
 */
@Remote('getOverview') async getOverviewRemote(request: OverviewRequest): Promise<OverviewValue>

/** Lead list read face; the ledger's list scope applies unchanged.
 * @param request - filters plus paging bounds; omitted filters select every visible lead.
 * @returns the matching page with the unfiltered total. */
@Remote('listLeads') async listLeadsRemote(request?: LeadListRequest): Promise<LeadListValue>

/** Score-run history read face across the operator's visible leads, newest first.
 * @param request - optional lead filter and page size.
 * @returns the matching runs with the unfiltered total. */
@Remote('listScoreRuns') async listScoreRunsRemote(request?: { lead_id?: string; limit?: number }): Promise<{ items: ScoreRun[]; total: number }>

/** ICP profile read face for the scoring page.
 * @param enabled_only - when true, only enabled profiles.
 * @returns every matching ICP profile. */
@Remote('listIcpProfiles') async listIcpProfilesRemote(enabled_only?: boolean): Promise<IcpProfileValue[]>

/** Score-template read face for the scoring page.
 * @param enabled_only - when true, only enabled templates.
 * @returns every matching score template. */
@Remote('listScoreTemplates') async listScoreTemplatesRemote(enabled_only?: boolean): Promise<ScoreTemplateValue[]>

/** GEO scan-history read face: every scan joined with its report's score.
 * @param limit - maximum rows to return; omit to return all.
 * @returns the scan rows, newest first, with the unfiltered total. */
@Remote('listGeoScans') async listGeoScansRemote(limit?: number): Promise<GeoScanListValue>

/** One full GEO report for the diagnosis page.
 * @param reportId - the report to read.
 * @returns the stored report; rejects for an unknown id. */
@Remote('getGeoReport') getGeoReportRemote(reportId: string): Promise<GeoReport>

/** Generated-copy read face across the operator's visible leads, newest first.
 * @param request - optional lead filter and page size.
 * @returns the matching copies with the unfiltered total. */
@Remote('listGeneratedContents') async listGeneratedContentsRemote( request?: { lead_id?: string; limit?: number }, ): Promise<{ items: GeneratedContent[]; total: number }>

/** Copy-template read face for the templates page.
 * @param filters - optional template type and enabled filter.
 * @returns every matching copy template. */
@Remote('listContentTemplates') async listContentTemplatesRemote(filters?: { type?: string; enabled_only?: boolean }): Promise<ContentTemplate[]>

/** SOP task read face; the service's lead-visibility scope applies unchanged.
 * @param request - lead and status filters plus paging bounds.
 * @returns the matching task page with the unfiltered total. */
@Remote('listSopTasks') async listSopTasksRemote( request?: { lead_id?: string; status?: 'pending' | 'done' | 'deferred' | 'dropped'; limit?: number; offset?: number }, ): Promise<{ items: SopTask[]; total: number }>

/** SOP-template read face for the templates page.
 * @param enabled_only - when true, only enabled templates.
 * @returns every matching SOP template. */
@Remote('listSopTemplates') async listSopTemplatesRemote(enabled_only?: boolean): Promise<SopTemplate[]>

/**
 * Record one compliance denial (red lines 1-3 enforcement, red line 6
 * coverage). The operator resolves best-effort: a denial must be recorded
 * even when the caller carried no agent identity.
 * @param toolName - the denied tool.
 * @param reason - the friendly denial reason.
 * @param request - the operator reference when known.
 * @returns resolution after the audit record is durable.
 */
async recordComplianceDeny( toolName: string, reason: string, request: OperatorRequest, ): Promise<void>
```

Types: [Domain](storage.md)

Source: [`packages/growth/customer-acquisition/src/service.ts`](../../packages/growth/customer-acquisition/src/service.ts)

<a id="ctxdragonbridge--dragonbridge"></a>

### `ctx.dragonBridge` — `DragonBridge`

Facade that joins the index, roster, and policy services.

The bridge does not own disk state; it depends on its sibling packages for I/O and classification. Its only state is a cached asset list rebuilt by `loadAll()`.

```ts cordis-catalog
/**
 * Refresh every upstream service and rebuild the cross-kind asset list.
 *
 * Skill and command / hook / plugin assets come from `ctx.dragonIndex`;
 * agent assets come from `ctx.agentRoster`. Each entry is classified by
 * `ctx.licensePolicy`.
 * @returns the rebuilt frozen asset list.
 */
async loadAll(): Promise<readonly DragonAsset[]>

/**
 * Filter the cached asset list.
 *
 * `safeOnly` (constructor flag) drops `artifact-only` and `reject` entries
 * from the default result set; explicit `decision` overrides it.
 *
 * @param query - filter criteria; missing fields do not restrict.
 * @returns matching assets, in the source-declared order.
 */
search(query: BridgeSearchQuery = {}): readonly DragonAsset[]

/** Return every asset the policy resolves to `allow`.
 * @returns the cached assets whose policy decision is `allow`. */
allowed(): readonly DragonAsset[]

/** Return every asset the policy resolves to `attribute`.
 * @returns the cached assets whose policy decision is `attribute`. */
attributed(): readonly DragonAsset[]

/** Return every asset the policy resolves to `artifact-only`.
 * @returns the cached assets whose policy decision is `artifact-only`. */
artifactOnly(): readonly DragonAsset[]

/** Return every asset the policy resolves to `reject`.
 * @returns the cached assets whose policy decision is `reject`. */
rejected(): readonly DragonAsset[]
```

Source: [`packages/experimental/dragon-bridge/src/index.ts`](../../packages/experimental/dragon-bridge/src/index.ts)

<a id="ctxdragonindex--dragonassetindex"></a>

### `ctx.dragonIndex` — `DragonAssetIndex`

Read-only registry over the `dragon-assets/index/*.jsonl` snapshots.

One service instance owns one snapshot. Callers can refresh the snapshot by calling `loadAll()` again; the registry exposes the current snapshot via the `snapshot` accessor.

```ts cordis-catalog
/**
 * Read every jsonl file into one snapshot and cache it.
 * @returns the loaded snapshot.
 */
async loadAll(): Promise<IndexSnapshot>

/**
 * Filter the cached snapshot.
 * @param query - filter criteria; missing fields do not restrict.
 * @returns matching entries, ordered as the source jsonl declared them.
 */
search(query: SearchQuery = {}): readonly AssetIndexEntry[]

/**
 * Exact-id lookup against the cached snapshot.
 * @param id - the asset identifier to resolve.
 * @param kind - optional kind disambiguator; omitted matches the first entry of any kind.
 * @returns the matching entry, or `undefined` if none.
 */
get(id: string, kind?: AssetKind): AssetIndexEntry | undefined
```

Source: [`packages/experimental/skill-index/src/index.ts`](../../packages/experimental/skill-index/src/index.ts)

<a id="ctxgeodiagnosis--geodiagnosisservice"></a>

### `ctx.geoDiagnosis` — `GeoDiagnosisService`

Storage-backed GEO diagnosis service. The domain comes from the main plugin's service; the web capability performs every fetch.

```ts cordis-catalog
/**
 * Run one bounded serial scan: record the running scan, crawl the seed's
 * origin, analyze, persist the report, and close the scan. Fetch failures
 * on individual pages degrade the report; a total failure marks the scan
 * `failed` and rethrows friendly.
 * @param input - the gated scan input (URL, optional page cap).
 * @param operator - the caller's resolved operator, for the audit write.
 * @returns the canonical scan value.
 */
async runScan(input: ScanInput, operator: ResolvedOperator): Promise<GeoScanValue>

/**
 * List scans joined with their reports, newest first, optionally filtered
 * by URL prefix and time window.
 * @param request - filters plus paging bounds.
 * @returns the matching page with the unfiltered total.
 */
listHistory(request: GeoHistoryRequest): { items: GeoHistoryItem[]; total: number }

/**
 * Read one full report with its scan's URL.
 * @param reportId - the report id.
 * @returns the projected report.
 */
getReport(reportId: string): GeoReportValue

/**
 * Compare two reports of the same site: score movement, resolved and newly
 * introduced shortcomings, and a Markdown summary.
 * @param reportAId - the baseline report id.
 * @param reportBId - the comparison report id.
 * @returns the comparison value.
 */
compareReports(reportAId: string, reportBId: string): GeoCompareValue
```

Source: [`packages/growth/customer-acquisition-geo/src/service.ts`](../../packages/growth/customer-acquisition-geo/src/service.ts)

<a id="ctxlicensepolicy--licensepolicy"></a>

### `ctx.licensePolicy` — `LicensePolicy`

Singleton license policy evaluator.

One Service instance owns the tier-to-decision table and (optional) AGPL attribution text. Pure: no I/O, no filesystem, no event subscription.

```ts cordis-catalog
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
normalize(raw: string | null | undefined): LicenseTier

/**
 * Evaluate one license tier and return the typed decision.
 * @param raw - the license string discovered upstream.
 * @returns the evaluation result.
 */
evaluate(raw: string | null | undefined): LicenseEvaluation

/**
 * Evaluate an already-normalized tier.
 * @param tier - the normalized license tier.
 * @returns the evaluation result.
 */
evaluateTier(tier: LicenseTier): LicenseEvaluation

/**
 * Convenience: assert the evaluation result is one of the allowed decisions.
 * @param raw - the license string discovered upstream.
 * @param allowed - the set of decisions the caller accepts.
 * @returns the evaluation result, throwing if it falls outside `allowed`.
 */
assertAllowed(raw: string | null | undefined, allowed: readonly LicenseDecision[]): LicenseEvaluation
```

Source: [`packages/experimental/license-policy/src/index.ts`](../../packages/experimental/license-policy/src/index.ts)

<a id="ctxquantresearch--quantresearchservice"></a>

### `ctx.quantResearch` — `QuantResearchService`

Storage-backed quant-research Remote service. Opens the domain at init, serves read-only account data to the browser panel.

```ts cordis-catalog
/** Authoritative domain, valid after init; a miss is a broken lifecycle.
 * @returns the open durable domain. */
requireDomain(): QuantDomain

/**
 * List all virtual accounts, projected to wire summaries.
 * @returns every account summary, sorted by name.
 */
@Remote('listAccounts') async listAccountsRemote(): Promise<AccountListValue>

/**
 * Read one account's full state.
 * @param ref - the account by id or by unique name.
 * @returns the account's wire summary; rejects when neither id nor name matches.
 */
@Remote('getAccountState') async getAccountStateRemote(ref: AccountRef): Promise<AccountSummaryValue>

/**
 * List research notes, newest first, projected to wire summaries.
 * @returns every note summary, newest first.
 */
@Remote('listNotes') async listNotesRemote(): Promise<NoteListValue>

/**
 * List persisted backtest snapshots, newest first, without equity points.
 * @returns every snapshot summary, newest first.
 */
@Remote('listResultSnapshots') async listResultSnapshotsRemote(): Promise<SnapshotListValue>

/**
 * Read one snapshot's equity curve.
 * @param ref - the snapshot id to read.
 * @returns the snapshot's equity curve; rejects for an unknown id.
 */
@Remote('getEquityCurve') async getEquityCurveRemote(ref: { result_id: string }): Promise<EquityCurveValue>
```

Source: [`packages/quant/quant-research/src/service.ts`](../../packages/quant/quant-research/src/service.ts)
<!-- END GENERATED cordis-surface -->
