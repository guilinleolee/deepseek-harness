/**
 * Sole import seam to the main customer-acquisition package; everything the
 * GEO module reuses (frozen v1 contract types, audit writer, red-line
 * constants, permission types) re-exports from here so the dependency stays
 * one-way and greppable.
 * @module @deepseek-ai/dsh-customer-acquisition-geo/main-package
 */

export * from '@deepseek-ai/dsh-customer-acquisition'
