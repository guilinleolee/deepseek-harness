/**
 * Image generation for the create workbench: renders a storyboard's shots, an
 * article's inline figures, or a cover plan's fields into asset images through
 * the shared `ctx.imageGeneration` service, and writes the produced bytes into
 * the theme's `assets/` directory. A read face hands a stored image back to
 * the browser for display.
 *
 * The caller owns the prompts (from the storyboard, figure, and cover parsers)
 * and the theme root; this module only turns prompts into stored images and
 * stored images into display reads. Every face takes a subset of the parsed
 * targets, so redrawing one image costs one call. Nothing is persisted beyond
 * the image files.
 */

import { resolveAssetPath } from '../gather/store.ts'
import { writeFileAtomic, withFileLock } from '@deepseek-ai/dsh-atomic-write'
import { mkdir, readFile } from 'node:fs/promises'
import { dirname } from 'node:path'
import type ImageGeneration from '@deepseek-ai/dsh-image-generation'
import type {
  CreateCoverImage, CreateCoverImageResult, CreateFigureImages, CreateImageRead, CreateStoryboardImages,
} from '../types.ts'

/** The hard byte cap on one image read; generated images sit far below it. */
export const CREATE_MAX_IMAGE_BYTES = 4 * 1024 * 1024

/**
 * The file extension one media type stores under, so the bytes and the name agree.
 * @param mediaType - the media type the produced bytes carry.
 * @returns the extension.
 * @throws when the provider answered with a non-image media type.
 */
export function extensionOf(mediaType: string): string {
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

/** The asset file stem of one article figure image. */
function figureFileName(figure: number, mediaType: string): string {
  return `figure-${String(figure).padStart(2, '0')}.${extensionOf(mediaType)}`
}

/** The asset file stem of the cover image. */
function coverFileName(mediaType: string): string {
  return `cover.${extensionOf(mediaType)}`
}

/** One numbered render target: the 1-based position its file name carries, and its brief. */
export interface CreateRenderTarget {
  /** The 1-based position in the source document. */
  readonly index: number
  /** The visual brief the provider renders; an empty brief is skipped. */
  readonly prompt: string
}

/**
 * Render one numbered target set into `assets/<prefix>-NN.<extension>` files,
 * the extension following the produced bytes' media type.
 * @param imageGeneration - the image-generation service.
 * @param root - absolute outputs library root.
 * @param theme - outputs-project directory name.
 * @param targets - the numbered briefs to render.
 * @param fileOf - the asset file stem builder for this target family.
 * @param signal - caller cancellation.
 * @returns the stored images in target order.
 */
async function renderNumberedImages(
  imageGeneration: ImageGeneration,
  root: string,
  theme: string,
  targets: readonly CreateRenderTarget[],
  fileOf: (index: number, mediaType: string) => string,
  signal?: AbortSignal,
): Promise<{ file: string; index: number; mediaType: string; prompt: string }[]> {
  const images: { file: string; index: number; mediaType: string; prompt: string }[] = []
  for (const target of targets) {
    const prompt = target.prompt.trim()
    if (prompt.length === 0) continue
    const [produced] = await imageGeneration.generate({
      providerId: '', prompt, model: '', width: 0, height: 0, count: 1,
    }, signal)
    if (produced === undefined) continue
    const file = fileOf(target.index, produced.mediaType)
    await writeImageAsset(root, theme, file, produced.bytes)
    images.push({ file, index: target.index, mediaType: produced.mediaType, prompt })
  }
  return images
}

/**
 * Generate the storyboard shots' images and store each under
 * `assets/storyboard-shot-NN.<extension>`. Passing a subset of the parsed
 * shots redraws exactly those shots, so one changed shot costs one image.
 * @param imageGeneration - the image-generation service.
 * @param root - absolute outputs library root.
 * @param theme - outputs-project directory name.
 * @param shots - the numbered shot briefs to render, in document order.
 * @param signal - caller cancellation.
 * @returns the stored images.
 */
export async function generateStoryboardImages(
  imageGeneration: ImageGeneration,
  root: string,
  theme: string,
  shots: readonly CreateRenderTarget[],
  signal?: AbortSignal,
): Promise<CreateStoryboardImages> {
  const rendered = await renderNumberedImages(imageGeneration, root, theme, shots, shotFileName, signal)
  return { images: rendered.map(image => ({ file: image.file, shot: image.index, mediaType: image.mediaType, prompt: image.prompt })) }
}

/**
 * Generate the article figures' images and store each under
 * `assets/figure-NN.<extension>`.
 * @param imageGeneration - the image-generation service.
 * @param root - absolute outputs library root.
 * @param theme - outputs-project directory name.
 * @param figures - the numbered figure briefs to render, in document order.
 * @param signal - caller cancellation.
 * @returns the stored images.
 */
export async function generateFigureImages(
  imageGeneration: ImageGeneration,
  root: string,
  theme: string,
  figures: readonly CreateRenderTarget[],
  signal?: AbortSignal,
): Promise<CreateFigureImages> {
  const rendered = await renderNumberedImages(imageGeneration, root, theme, figures, figureFileName, signal)
  return { images: rendered.map(image => ({ file: image.file, figure: image.index, mediaType: image.mediaType, prompt: image.prompt })) }
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

/**
 * The media type one stored asset file's byte prefix declares. The prefix is
 * the only trusted source: an extension can name anything.
 * @param file - the asset file name, for the error message only.
 * @param bytes - the file's first bytes.
 * @returns the declared media type.
 * @throws when the prefix is not a supported raster image.
 */
function sniffImageMediaType(file: string, bytes: Uint8Array): string {
  if (bytes[0] === 0x89 && bytes[1] === 0x50) return 'image/png'
  if (bytes[0] === 0xff && bytes[1] === 0xd8) return 'image/jpeg'
  if (bytes[0] === 0x52 && bytes[1] === 0x49) return 'image/webp'
  if (bytes[0] === 0x47 && bytes[1] === 0x49) return 'image/gif'
  throw new Error(`create asset ${file} is not a supported raster image`)
}

/**
 * Read one generated image asset back for display. Only raster images inside
 * the theme's `assets/` directory are served, under a hard byte cap; every
 * other name or shape rejects.
 * @param root - absolute outputs library root.
 * @param theme - outputs-project directory name.
 * @param file - the plain asset file name the generation pass stored.
 * @returns the media type and base64 bytes.
 */
export async function readCreateImageFile(root: string, theme: string, file: string): Promise<CreateImageRead> {
  const target = resolveAssetPath(root, theme, file)
  const bytes = await readFile(target)
  if (bytes.byteLength > CREATE_MAX_IMAGE_BYTES) {
    throw new Error(`create asset ${file} exceeds the ${CREATE_MAX_IMAGE_BYTES}-byte read cap`)
  }
  const mediaType = sniffImageMediaType(file, bytes)
  return { mediaType, base64: bytes.toString('base64') }
}
