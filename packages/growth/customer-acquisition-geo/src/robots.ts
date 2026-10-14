/**
 * Minimal robots.txt interpretation for the GEO crawler (red line 1: a
 * `Disallow`ed path is never fetched). Supports the subset the crawler
 * actually needs: agent-group blocks, `Disallow` lines, and the `*` / `$`
 * path wildcards. Unknown directives are ignored, per the robots exclusion
 * standard's tolerance rule.
 * @module @deepseek-ai/dsh-customer-acquisition-geo/robots
 */

/** The crawler identifies itself so site owners can target it specifically. */
export const GEO_USER_AGENT = 'dsh-geo-diagnostic'

/** One `Disallow` rule. */
export interface DisallowRule {
  /** Raw pattern as written in robots.txt. */
  readonly pattern: string
}

/** The disallow rules applying to one crawl. */
export interface RobotsRules {
  /** Matching rules; empty means nothing is disallowed. */
  readonly rules: readonly DisallowRule[]
}

/** The rule set used when robots.txt is absent, unreadable, or allows all. */
export const ALLOW_ALL_ROBOTS: RobotsRules = { rules: [] }

/**
 * Parse robots.txt text into the rules applying to the GEO agent. A group
 * whose `User-agent` matches the crawler's own name wins; otherwise the `*`
 * group applies. Consecutive `User-agent` lines share one group (the
 * standard's agent-stack form).
 * @param text - the raw robots.txt body, or `undefined` when the fetch failed.
 * @param userAgent - the agent name to match.
 * @returns the applicable disallow rules; never `undefined`.
 */
export function parseRobots(text: string | undefined, userAgent: string = GEO_USER_AGENT): RobotsRules {
  if (text === undefined) return ALLOW_ALL_ROBOTS
  const collected = new Map<string, DisallowRule[]>()
  let groupAgents: string[] = []
  let groupHasRule = false
  for (const raw of text.split(/\r?\n/)) {
    const comment = raw.indexOf('#')
    const line = (comment === -1 ? raw : raw.slice(0, comment)).trim()
    if (line.length === 0) continue
    const separator = line.indexOf(':')
    if (separator === -1) continue
    const field = line.slice(0, separator).trim().toLowerCase()
    const value = line.slice(separator + 1).trim()
    if (field === 'user-agent') {
      // A User-agent line after rules starts a fresh group; before any rule it
      // extends the current group's agent stack.
      if (groupHasRule) {
        groupAgents = []
        groupHasRule = false
      }
      groupAgents.push(value.toLowerCase())
    } else if (field === 'disallow' && groupAgents.length > 0) {
      for (const agent of groupAgents) {
        const rules = collected.get(agent)
        if (rules === undefined) collected.set(agent, [{ pattern: value }])
        else rules.push({ pattern: value })
      }
      groupHasRule = true
    }
  }
  const own = collected.get(userAgent.toLowerCase())
  if (own !== undefined && own.length > 0) return { rules: own }
  const wildcard = collected.get('*')
  if (wildcard !== undefined && wildcard.length > 0) return { rules: wildcard }
  return ALLOW_ALL_ROBOTS
}

/**
 * Match one path against a robots pattern: `*` spans any run, `$` anchors the
 * end; otherwise the pattern is a plain prefix.
 * @param path - the URL path (with query) to test.
 * @param pattern - the raw `Disallow` pattern.
 * @returns true when the pattern covers the path.
 */
function matchesPattern(path: string, pattern: string): boolean {
  if (pattern === '') return false
  const anchored = pattern.endsWith('$')
  const body = anchored ? pattern.slice(0, -1) : pattern
  const source = body.split('*').map(seg => seg.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('.*')
  return new RegExp(`^${source}${anchored ? '$' : ''}`).test(path)
}

/**
 * Whether a URL is disallowed for the GEO agent under the parsed rules.
 * @param url - the candidate URL.
 * @param robots - the applicable rules.
 * @returns true when the URL must be skipped.
 */
export function isDisallowed(url: string, robots: RobotsRules): boolean {
  const { pathname, search } = new URL(url)
  return robots.rules.some(rule => matchesPattern(`${pathname}${search}`, rule.pattern))
}
