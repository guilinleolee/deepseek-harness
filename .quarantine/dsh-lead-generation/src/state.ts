/**
 * Task state machine and atomic persistence.
 *
 * Tasks are addressed by their deterministic identifier, which is the
 * SHA-256 hex digest of `(industry|region|count)`. Two callers asking for
 * the same triple land on the same task — the storage layer does the lookup.
 *
 * @module @deepseek-ai/dsh-lead-generation/state
 */
import { createHash } from 'node:crypto'
import { probe, readWholeText, resolveLocalTarget, writeFileAtomic } from '@deepseek-ai/dsh-fs-local'
import process from 'node:process'

/** The ordered pipeline stages. The last entry is terminal. */
export type Stage = 'parsing' | 'prospecting' | 'research' | 'scoring' | 'drafting' | 'closed'

const STAGE_ORDER: readonly Stage[] = [
  'parsing', 'prospecting', 'research', 'scoring', 'drafting', 'closed',
]

/** A prospect produced by the prospecting stage. */
export interface Prospect {
  readonly id: string
  readonly name: string
  readonly country: string
  readonly category: string
}

/** A company dossier produced by the research stage. */
export interface Dossier {
  readonly sizeBand: string
  readonly platforms: readonly string[]
  readonly teamSize: number
}

/** A score produced by the scoring stage. */
export interface Score {
  readonly total: number
  readonly tier: 'A' | 'B' | 'C' | 'D'
}

/** A draft produced by the drafting stage. */
export interface Draft {
  readonly prospectId: string
  readonly subject: string
  readonly body: string
  readonly draftHash: string
}

/** The persistent task record stored on disk as one JSON object. */
export interface Task {
  readonly taskId: string
  readonly industry: string
  readonly region: string
  readonly count: number
  readonly stage: Stage
  readonly prospects: Prospect[]
  readonly dossiers: Record<string, Dossier>
  readonly scores: Record<string, Score>
  readonly drafts: Record<string, Draft>
  readonly createdAt: string
  readonly updatedAt: string
}

/** Empty task at stage `parsing` with no downstream artifacts yet. */
function emptyTask(taskId: string, industry: string, region: string, count: number, now: string): Task {
  return {
    taskId,
    industry,
    region,
    count,
    stage: 'parsing',
    prospects: [],
    dossiers: {},
    scores: {},
    drafts: {},
    createdAt: now,
    updatedAt: now,
  }
}

/** Deterministic task identifier for the (industry, region, count) triple. */
export function computeTaskId(industry: string, region: string, count: number): string {
  const digest = createHash('sha256')
    .update(`${industry}|${region}|${count}`, 'utf8')
    .digest('hex')
  return digest.slice(0, 16)
}

/** Hex SHA-256 of a draft body, prefixed for log readability. */
export function computeDraftHash(body: string): string {
  return 'sha256:' + createHash('sha256').update(body, 'utf8').digest('hex')
}

/**
 * Entry assertion for every downstream tool. Refuses if the task is not
 * currently in the required stage.
 * @param task - the loaded task.
 * @param expectedStage - the stage the calling tool requires.
 * @throws when the task is at a different stage; the message names both.
 */
export function assertStage(task: Task, expectedStage: Stage): void {
  if (task.stage !== expectedStage) {
    throw new Error(
      `task ${task.taskId} expected stage ${expectedStage}, currently ${task.stage}`,
    )
  }
}

/**
 * Return the stage immediately following the current one. Throws at the
 * terminal `closed` stage — the model must not skip the gate.
 */
export function nextStage(current: Stage): Stage {
  const idx = STAGE_ORDER.indexOf(current)
  if (idx < 0) throw new Error(`unknown stage: ${current}`)
  if (idx === STAGE_ORDER.length - 1) {
    throw new Error(`task already at terminal stage: ${current}`)
  }
  const next = STAGE_ORDER[idx + 1]
  if (next === undefined) throw new Error(`stage order broken at ${current}`)
  return next
}

/**
 * Persistent task storage keyed by deterministic taskId.
 *
 * Backed by a single JSON file at `storagePath`. Reads are race-tolerant
 * (a missing file is the empty state); writes are whole-file atomic.
 */
export class TaskState {
  constructor(private readonly storagePath: string) {}

  /** Resolve and load one task by id; `undefined` when the file is absent. */
  async load(taskId: string): Promise<Task | undefined> {
    const target = await resolveLocalTarget(process.cwd(), this.taskPath(taskId))
    const info = await probe(target.targetKey)
    if (info === null) return undefined
    const text = await readWholeText(target)
    try {
      const parsed = JSON.parse(text) as Task
      return parsed
    } catch (cause) {
      throw new Error(`task ${taskId} storage corrupted: ${String(cause)}`)
    }
  }

  /** Persist the task atomically. The caller owns the `updatedAt` stamp. */
  async save(task: Task): Promise<void> {
    const target = this.taskPath(task.taskId)
    const body = JSON.stringify(task, null, 2)
    await writeFileAtomic(target, body, undefined, undefined)
  }

  /**
   * Idempotent task creation.
   *
   * If a task with the same `(industry, region, count)` already exists,
   * return it unchanged. Otherwise create a fresh `parsing`-stage record
   * and persist it before returning.
   */
  async createOrLoad(args: { industry: string; region: string; count: number }): Promise<Task> {
    const taskId = computeTaskId(args.industry, args.region, args.count)
    const existing = await this.load(taskId)
    if (existing !== undefined) return existing
    const now = new Date().toISOString()
    const task = emptyTask(taskId, args.industry, args.region, args.count, now)
    await this.save(task)
    return task
  }

  private taskPath(taskId: string): string {
    // Per-task files keep concurrent readers from racing on a single JSON
    // document; the parent storagePath is a directory, not a file.
    return `${this.storagePath}/${taskId}.json`
  }
}
