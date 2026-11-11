/**
 * Synthetic prospect seed. The v0.1 default data source.
 *
 * The 30 prospect table mirrors `rehearsal/vertical.md` so that development
 * and rehearsal stay synchronized; switching to a real data source in v0.2
 * swaps this seed for an Apollo / LinkedIn / customs-data adapter without
 * changing any downstream tool.
 *
 * @module @deepseek-ai/dsh-lead-generation/synth/seed
 */
import type { Prospect } from '../state.ts'

interface SeedRow {
  readonly name: string
  readonly country: string
  readonly category: string
}

/**
 * Stable seed list. Order is part of the contract — `lg_prospect` indexes
 * into it, so reordering renumbers prospect ids and would break idempotent
 * task replay.
 */
const SEED: readonly SeedRow[] = [
  { name: 'PT Rumah Nyaman Indonesia', country: 'ID', category: 'home-storage' },
  { name: 'Bangkok Home Co., Ltd', country: 'TH', category: 'lighting' },
  { name: 'Cửa Hàng Tiện Ích', country: 'VN', category: 'kitchen' },
  { name: 'KL Living Essentials', country: 'MY', category: 'small-appliance' },
  { name: 'Manila Home Hub Inc', country: 'PH', category: 'home-textile' },
  { name: 'PT Sentosa Furnishing', country: 'ID', category: 'furniture' },
  { name: 'Chiang Mai Crafts', country: 'TH', category: 'handicraft' },
  { name: 'Saigon Tech Home', country: 'VN', category: 'smart-home' },
  { name: 'MyHome Mart Sdn Bhd', country: 'MY', category: 'home-mixed' },
  { name: 'Cebu Lifestyle Trading', country: 'PH', category: 'decor' },
  { name: 'PT Jaya Abadi Grosir', country: 'ID', category: 'home-wholesale' },
  { name: 'Bangkok Living Plus', country: 'TH', category: 'living-furniture' },
  { name: 'Vietnam Smart Kitchen', country: 'VN', category: 'kitchen-appliance' },
  { name: 'Penang Home Style', country: 'MY', category: 'home-textile' },
  { name: 'Davao Comfort Living', country: 'PH', category: 'bedding' },
  { name: 'PT Griya Sehat', country: 'ID', category: 'wellness-home' },
  { name: 'Pattaya Decor Co', country: 'TH', category: 'wall-art' },
  { name: 'Hanoi Living Hub', country: 'VN', category: 'lighting-appliance' },
  { name: 'JB Home Solutions', country: 'MY', category: 'smart-home' },
  { name: 'Quezon City Trading', country: 'PH', category: 'home-mixed' },
  { name: 'PT Sinar Jaya Living', country: 'ID', category: 'bath' },
  { name: 'Krabi Home Goods', country: 'TH', category: 'outdoor-furniture' },
  { name: 'Mekong Home Store', country: 'VN', category: 'kitchen' },
  { name: 'Sabah Living Co', country: 'MY', category: 'home-mixed' },
  { name: 'Iloilo Smart Home', country: 'PH', category: 'smart-home' },
  { name: 'PT Mitra Home', country: 'ID', category: 'home-accessory' },
  { name: 'Phuket Beach Home', country: 'TH', category: 'outdoor' },
  { name: 'Da Nang Living', country: 'VN', category: 'living-furniture' },
  { name: 'Kuching Home Mart', country: 'MY', category: 'home-mixed' },
  { name: 'Bacolod Comfort Hub', country: 'PH', category: 'home-textile' },
]

/**
 * Materialize the first `count` seed rows as `Prospect` records.
 * @param count - the requested count; clamped to [1, SEED.length].
 * @returns a deterministic array of prospects with stable three-digit ids.
 */
export function generateProspects(count: number): Prospect[] {
  const clamped = Math.max(1, Math.min(SEED.length, Math.floor(count)))
  return SEED.slice(0, clamped).map((row, index) => ({
    id: `p${String(index + 1).padStart(3, '0')}`,
    name: row.name,
    country: row.country,
    category: row.category,
  }))
}

/** Total seed rows available; useful for callers validating against the cap. */
export function seedCapacity(): number {
  return SEED.length
}
