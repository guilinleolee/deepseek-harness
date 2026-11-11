/**
 * Parsers for the two structured creation documents: the storyboard and the
 * cover plan. Both are model-generated markdown with a fixed field
 * vocabulary, and both are read back into structured facts the workbench
 * renders and the image providers consume.
 *
 * The parsers are tolerant by design: a field the model omitted reads as
 * empty or null rather than rejecting the whole document, because a partially
 * conforming draft is still the user's draft. Client-safe by construction —
 * no Node or filesystem imports.
 */

/** One shot of a storyboard. */
export interface CreateStoryboardShot {
  /** The shot's 1-based position in the storyboard. */
  readonly index: number
  /** The role the heading gave the shot (the hook, the payoff); empty when unlabelled. */
  readonly label: string
  /** The visual brief — what the frame shows. An image provider renders this. */
  readonly visual: string
  /** The spoken line of the shot; empty when the shot carries none. */
  readonly line: string
  /** The shot duration in seconds; null when the model gave none. */
  readonly seconds: number | null
}

/** One cover plan: the text fields a cover image is built from. */
export interface CreateCoverPlan {
  readonly title: string
  readonly subtitle: string
  readonly composition: string
  readonly palette: string
  readonly style: string
}

/** The heading line that opens one section of a generated document. */
const HEADING = /^#{1,6}\s*(.*)$/u

/** The label and duration a storyboard heading carries: `镜头 2 · 冲突（5s）`. */
const SHOT_HEADING = /镜头\s*(\d+)\s*[·・:：]?\s*(.*?)\s*(?:[（(]\s*(\d+)\s*s?\s*[）)])?\s*$/u

/** The seconds a shot body states on its `时长` line. */
const DURATION_LINE = /(\d+(?:\.\d+)?)\s*(?:秒|s\b)?/iu

/**
 * Split a generated document into its heading sections.
 * @param text - the document text.
 * @returns the heading label and body of each section, in document order.
 */
function splitSections(text: string): { heading: string; body: string }[] {
  const sections: { heading: string; body: string }[] = []
  let heading = ''
  let body: string[] = []
  for (const line of text.split('\n')) {
    const match = HEADING.exec(line.trim())
    if (match === null) {
      body.push(line)
      continue
    }
    if (heading.length > 0 || body.some(entry => entry.trim().length > 0)) {
      sections.push({ heading, body: body.join('\n') })
    }
    heading = match[1]?.trim() ?? ''
    body = []
  }
  if (heading.length > 0 || body.some(entry => entry.trim().length > 0)) {
    sections.push({ heading, body: body.join('\n') })
  }
  return sections
}

/**
 * Read one labelled field out of a section body. A label matches only when
 * the line continues with a separator, so `画面` never claims the line of
 * `画面提示`.
 * @param body - the section body.
 * @param labels - the accepted field labels, in priority order.
 * @returns the field text, or an empty string when the section carries none.
 */
function fieldValue(body: string, labels: readonly string[]): string {
  for (const line of body.split('\n')) {
    const trimmed = line.trim()
    for (const label of labels) {
      if (!trimmed.startsWith(label)) continue
      const rest = trimmed.slice(label.length)
      if (rest.length > 0 && !rest.startsWith('：') && !rest.startsWith(':')) continue
      return rest.replace(/^[：:]\s*/u, '').trim()
    }
  }
  return ''
}

/**
 * Parse the duration a section states, preferring the body over the heading.
 * @param body - the section body.
 * @param headingSeconds - the seconds the heading carries, or null.
 * @returns the duration in seconds, or null when neither states one.
 */
function durationOf(body: string, headingSeconds: number | null): number | null {
  const stated = fieldValue(body, ['时长'])
  if (stated.length > 0) {
    const match = DURATION_LINE.exec(stated)
    if (match !== null) {
      const seconds = Number.parseFloat(match[1] ?? '')
      if (Number.isFinite(seconds) && seconds > 0) return seconds
    }
  }
  return headingSeconds
}

/**
 * Parse a generated storyboard into its shots. A section counts as a shot
 * when its heading names a 镜头 or its body carries a 画面 line; the shots
 * come back in document order with a 1-based index.
 * @param text - the storyboard document.
 * @returns the parsed shots; empty when the document carries none.
 */
export function parseCreateStoryboard(text: string): CreateStoryboardShot[] {
  const shots: CreateStoryboardShot[] = []
  for (const section of splitSections(text)) {
    const headingMatch = SHOT_HEADING.exec(section.heading)
    const visual = fieldValue(section.body, ['画面', '画面提示', '镜头提示'])
    if (headingMatch === null && visual.length === 0) continue
    const headingSeconds = headingMatch?.[3] === undefined ? null : Number.parseInt(headingMatch[3], 10)
    const label = (headingMatch?.[2] ?? '').replace(/[（(]\s*\d+\s*s?\s*[）)]\s*$/u, '').trim()
    shots.push({
      index: shots.length + 1,
      label,
      visual,
      line: fieldValue(section.body, ['台词', '旁白', '文案']),
      seconds: durationOf(section.body, headingSeconds !== null && Number.isFinite(headingSeconds) ? headingSeconds : null),
    })
  }
  return shots
}

/**
 * Parse a generated cover plan into its fields. A field the document omits
 * reads as an empty string; the plan's title falls back to the first heading
 * so a plan written without the 主标题 line still names its cover.
 * @param text - the cover document.
 * @returns the parsed plan.
 */
export function parseCreateCoverPlan(text: string): CreateCoverPlan {
  const sections = splitSections(text)
  const body = sections.map(section => section.body).join('\n')
  const title = fieldValue(body, ['主标题'])
  const firstHeading = sections.find(section => section.heading.length > 0)?.heading ?? ''
  return {
    title: title.length > 0 ? title : firstHeading,
    subtitle: fieldValue(body, ['副标题']),
    composition: fieldValue(body, ['构图']),
    palette: fieldValue(body, ['配色']),
    style: fieldValue(body, ['画面风格', '风格']),
  }
}
