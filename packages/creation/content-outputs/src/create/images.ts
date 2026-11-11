/**
 * Image generation for the create workbench: renders a storyboard's shots or
 * a cover plan's fields into asset images through the shared
 * `ctx.imageGeneration` service, and writes the produced bytes into the
 * theme's `assets/` directory.
 *
 * The caller owns the prompts (from the storyboard/cover parsers) and the
 * theme root; this module only turns prompts into stored images. Nothing is
 * persisted beyond the image files themselves.
 */

import { resolveAssetPath } from '../gather/store.ts'
import { writeFileAtomic, withFileLock } from '@deepseek-ai/dsh-atomic-write'
import { mkdir } from 'node:fs/promises'
import { dirname } from 'node:path'
import type ImageGeneration from '@deepseek-ai/dsh-image-generation'
import type {
  CreateCoverImage, CreateCoverImageResult, CreateStoryboardImage, CreateStoryboardImages,
} from '../types.ts'

/** The file extension one media type stores under, so the bytes and the name agree. */
function extensionOf(mediaType: string): string {
  switch (mediaType) {
    case 'image/jpeg': return 'jpg'
    case 'image/webp': return 'webp'
    case 'image/gif': return 'gif'
    case 'image/png': return 'png'
    default: throw new Error(`image provider returned an unsupported media type: ${mediaType}`)
  }
}

/** The asset file stem of one storyboard shot image. */
function shotFileName(shot: number, mediaType: string): string {
  return `storyboard-shot-${String(shot).padStart(2, '0')}.${extensionOf(mediaType)}`
}

/** The asset file stem of the cover image. */
function coverFileName(mediaType: string): string {
  return `cover.${extensionOf(mediaType)}`
}

/**
 * Generate the storyboard shots' images from the parsed visuals and store
 * each under `assets/storyboard-shot-NN.png`.
 * @param imageGeneration - the image-generation service.
 * @param root - absolute outputs library root.
 * @param theme - outputs-project directory name.
 * @param visuals - the shot visuals, one per shot in document order.
 * @param signal - caller cancellation.
 * @returns the stored images.
 */
export async function generateStoryboardImages(
  imageGeneration: ImageGeneration,
  root: string,
  theme: string,
  visuals: readonly string[],
  signal?: AbortSignal,
): Promise<CreateStoryboardImages> {
  const images: CreateStoryboardImage[] = []
  for (let index = 0; index < visuals.length; index += 1) {
    const prompt = visuals[index]?.trim() ?? ''
    if (prompt.length === 0) continue
    const [produced] = await imageGeneration.generate({
      providerId: '', prompt, model: '', width: 0, height: 0, count: 1,
    }, signal)
    if (produced === undefined) continue
    const file = shotFileName(index + 1, produced.mediaType)
    await writeImageAsset(root, theme, file, produced.bytes)
    images.push({ file, shot: index + 1, mediaType: produced.mediaType, prompt })
  }
  return { images }
}

/**
 * Generate the cover image from a parsed cover plan and store it under
 * `assets/cover.<extension>` with the extension the produced bytes declare.
 * @param imageGeneration - the image-generation service.
 * @param root - absolute outputs library root.
 * @param theme - outputs-project directory name.
 * @param prompt - the composed cover prompt.
 * @param signal - caller cancellation.
 * @returns the stored cover image.
 */
export async function generateCoverImage(
  imageGeneration: ImageGeneration,
  root: string,
  theme: string,
  prompt: string,
  signal?: AbortSignal,
): Promise<CreateCoverImageResult> {
  const images: CreateCoverImage[] = []
  const trimmed = prompt.trim()
  if (trimmed.length > 0) {
    const [produced] = await imageGeneration.generate({
      providerId: '', prompt: trimmed, model: '', width: 0, height: 0, count: 1,
    }, signal)
    if (produced !== undefined) {
      const file = coverFileName(produced.mediaType)
      await writeImageAsset(root, theme, file, produced.bytes)
      images.push({ file, mediaType: produced.mediaType, prompt: trimmed })
    }
  }
  return { images }
}

/**
 * Write one image's bytes under the theme's `assets/` directory with an
 * atomic, locked commit, reusing the gather write face's guards.
 * @param root - absolute outputs library root.
 * @param theme - outputs-project directory name.
 * @param file - the plain asset file name.
 * @param bytes - the encoded image bytes.
 */
async function writeImageAsset(root: string, theme: string, file: string, bytes: Uint8Array): Promise<void> {
  const target = resolveAssetPath(root, theme, file)
  await mkdir(dirname(target), { recursive: true })
  await withFileLock(target, async () => {
    await writeFileAtomic(target, bytes, { mode: 0o600, dirMode: 0o700 })
  })
}
