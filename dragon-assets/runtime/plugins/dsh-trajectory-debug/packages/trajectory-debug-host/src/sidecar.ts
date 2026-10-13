/**
 * Sidecar store: debug metadata that must NEVER enter the session log.
 *
 * Holds fork variants and re-run experiments. Two backends:
 * - {@link MemorySidecar} — per-process memory (default);
 * - {@link FileSidecar} — one JSON file per session, written atomically
 *   (tmp + rename), surviving host restarts.
 *
 * Both implement {@link Sidecar}. The `ctx.storage` domain integration is a
 * later milestone; this interim design keeps the same interface so swapping
 * the backend does not touch the provider.
 *
 * The sidecar is keyed by session id; sessions themselves are unaffected
 * (event-sourcing invariant). When a session is deleted the sidecar files
 * are cleaned by `disposeSession`.
 *
 * @module dsh-trajectory-debug-host/sidecar
 */

import { existsSync, mkdirSync, readFileSync, renameSync, rmSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'
import type {
  ExperimentId,
  ExperimentRecord,
  SessionId,
  Variant,
  VariantId,
} from 'dsh-trajectory-debug'

/** Backend-neutral sidecar surface. */
export interface Sidecar {
  addVariant(variant: Variant): void
  getVariant(id: VariantId): Variant | undefined
  listVariants(sessionId: SessionId): Variant[]
  newVariantId(): VariantId
  addExperiment(record: ExperimentRecord): void
  listExperiments(sessionId: SessionId): ExperimentRecord[]
  newExperimentId(): ExperimentId
  /** Drop all metadata for one session (called on session disposal). */
  disposeSession(sessionId: SessionId): void
}

export class MemorySidecar implements Sidecar {
  protected readonly variants = new Map<VariantId, Variant>()
  protected readonly variantsBySession = new Map<SessionId, VariantId[]>()
  protected readonly experiments = new Map<ExperimentId, ExperimentRecord>()
  protected readonly experimentsBySession = new Map<SessionId, ExperimentId[]>()
  protected variantSeq = 0
  protected experimentSeq = 0

  addVariant(variant: Variant): void {
    this.variants.set(variant.id, variant)
    const list = this.variantsBySession.get(variant.sessionId) ?? []
    list.push(variant.id)
    this.variantsBySession.set(variant.sessionId, list)
  }

  getVariant(id: VariantId): Variant | undefined {
    return this.variants.get(id)
  }

  listVariants(sessionId: SessionId): Variant[] {
    return (this.variantsBySession.get(sessionId) ?? [])
      .map((id) => this.variants.get(id))
      .filter((v): v is Variant => v !== undefined)
  }

  newVariantId(): VariantId {
    return `variant-${++this.variantSeq}` as VariantId
  }

  addExperiment(record: ExperimentRecord): void {
    this.experiments.set(record.id, record)
    const list = this.experimentsBySession.get(record.sessionId) ?? []
    list.push(record.id)
    this.experimentsBySession.set(record.sessionId, list)
  }

  listExperiments(sessionId: SessionId): ExperimentRecord[] {
    return (this.experimentsBySession.get(sessionId) ?? [])
      .map((id) => this.experiments.get(id))
      .filter((e): e is ExperimentRecord => e !== undefined)
  }

  newExperimentId(): ExperimentId {
    return `experiment-${++this.experimentSeq}` as ExperimentId
  }

  disposeSession(sessionId: SessionId): void {
    for (const id of this.variantsBySession.get(sessionId) ?? []) this.variants.delete(id)
    for (const id of this.experimentsBySession.get(sessionId) ?? []) this.experiments.delete(id)
    this.variantsBySession.delete(sessionId)
    this.experimentsBySession.delete(sessionId)
  }
}

interface SessionSidecarData {
  variants: Variant[]
  experiments: ExperimentRecord[]
}

/**
 * JSON-file-backed sidecar: one file per session under `root`, written
 * atomically (tmp + rename). Survives host restarts; state is plain JSON.
 */
export class FileSidecar implements Sidecar {
  private readonly cache = new Map<string, SessionSidecarData>()
  private variantSeq = 0
  private experimentSeq = 0

  constructor(private readonly root: string) {
    mkdirSync(root, { recursive: true })
  }

  addVariant(variant: Variant): void {
    this.data(variant.sessionId).variants.push(variant)
    this.save(variant.sessionId)
  }

  getVariant(id: VariantId): Variant | undefined {
    for (const data of this.cache.values()) {
      const found = data.variants.find((v) => v.id === id)
      if (found !== undefined) return found
    }
    return undefined
  }

  listVariants(sessionId: SessionId): Variant[] {
    return this.data(sessionId).variants
  }

  newVariantId(): VariantId {
    return `variant-${++this.variantSeq}` as VariantId
  }

  addExperiment(record: ExperimentRecord): void {
    this.data(record.sessionId).experiments.push(record)
    this.save(record.sessionId)
  }

  listExperiments(sessionId: SessionId): ExperimentRecord[] {
    return this.data(sessionId).experiments
  }

  newExperimentId(): ExperimentId {
    return `experiment-${++this.experimentSeq}` as ExperimentId
  }

  disposeSession(sessionId: SessionId): void {
    this.cache.delete(sessionId)
    const file = this.path(sessionId)
    if (existsSync(file)) rmSync(file)
  }

  private data(sessionId: SessionId): SessionSidecarData {
    let data = this.cache.get(sessionId)
    if (data === undefined) {
      const file = this.path(sessionId)
      data = existsSync(file)
        ? (JSON.parse(readFileSync(file, 'utf8')) as SessionSidecarData)
        : { variants: [], experiments: [] }
      this.cache.set(sessionId, data)
    }
    return data
  }

  private save(sessionId: SessionId): void {
    const data = this.cache.get(sessionId)
    if (data === undefined) return
    const file = this.path(sessionId)
    const tmp = `${file}.tmp`
    writeFileSync(tmp, JSON.stringify(data))
    renameSync(tmp, file) // atomic publish
  }

  private path(sessionId: SessionId): string {
    return join(this.root, `${sessionId.replace(/[^a-zA-Z0-9_-]/g, '_')}.json`)
  }
}
