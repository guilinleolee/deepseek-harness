/**
 * Generic `{{variable}}` rendering for user-authored template bodies.
 *
 * The scoring templates use a fixed four-placeholder vocabulary
 * (`{{lead}}` / `{{icp_profile}}` / `{{dimensions}}` / `{{knowledge}}`) and
 * are rendered by `scoring/prompt.ts`. Copy templates are different: their
 * bodies are authored by the operator and may name any variable — including
 * Chinese ones such as `{{公司名称}}`. Reusing the scoring renderer for copy
 * silently blanked every such variable, so the model received a body with
 * holes in it (`您好，我是，专注帮门店…`) and then guessed the missing facts.
 *
 * This module is the copy-side contract:
 * - a variable with a value is substituted;
 * - a variable without a value is **left in place** and reported, so the
 *   caller can tell the model which slots to skip instead of shipping a
 *   silently mangled body.
 * @module @deepseek-ai/dsh-customer-acquisition/templates/render
 */

/** `{{name}}` where name is an ASCII identifier or a run of Chinese characters. */
const PLACEHOLDER = /\{\{\s*([A-Za-z_][A-Za-z0-9_]*|[一-鿿]+)\s*\}\}/gu

/** One render pass: the substituted body plus the slots that stayed open. */
export interface VariableRenderResult {
  /** The body with every resolvable placeholder substituted. */
  text: string
  /** Placeholder names left in place because no value was available. */
  unresolved: string[]
}

/**
 * Substitute `{{variable}}` placeholders in a template body.
 * @param body - the authored template body.
 * @param values - variable name → value; an empty or absent value leaves the
 *   placeholder in place instead of deleting it.
 * @returns the rendered text and the names of the placeholders left open.
 */
export function renderVariables(body: string, values: Record<string, string>): VariableRenderResult {
  const unresolved = new Set<string>()
  const text = body.replace(PLACEHOLDER, (match, name: string) => {
    const value = values[name]
    if (typeof value === 'string' && value.length > 0) return value
    unresolved.add(name)
    return match
  })
  return { text, unresolved: [...unresolved] }
}
