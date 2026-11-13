import { describe, expect, it, vi } from 'vitest'
import { mkdtempSync, mkdirSync, rmSync, writeFileSync, existsSync, readFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import type ImageGeneration from '@deepseek-ai/dsh-image-generation'
import { CREATE_MAX_IMAGE_BYTES, generateCoverImage, generateStoryboardImages, readCreateImageFile } from '../src/create/images.ts'

/** A stand-in image generation service returning one PNG per call. */
function imageGeneration(): { service: ImageGeneration; generate: ReturnType<typeof vi.fn> } {
  const generate = vi.fn(async (_request: { prompt: string }) => [{
    bytes: Uint8Array.from([0x89, 0x50, 0x4e, 0x47]),
    mediaType: 'image/png',
    model: 'test-model',
  }])
  return { service: { generate } as unknown as ImageGeneration, generate }
}

function themeDir(): string {
  return mkdtempSync(join(tmpdir(), 'dsh-create-images-'))
}

describe('generateStoryboardImages', () => {
  it('renders each non-empty visual into an ordered asset file', async () => {
    const root = themeDir()
    const theme = 'topic'
    try {
      const stub = imageGeneration()
      const result = await generateStoryboardImages(stub.service, root, theme, ['画面一', '  ', '画面三'])
      expect(result.images).toHaveLength(2)
      expect(result.images[0]).toMatchObject({ file: 'storyboard-shot-01.png', shot: 1, prompt: '画面一' })
      expect(result.images[1]).toMatchObject({ file: 'storyboard-shot-03.png', shot: 3, prompt: '画面三' })
      expect(stub.generate).toHaveBeenCalledTimes(2)
      expect(existsSync(join(root, theme, 'assets', 'storyboard-shot-01.png'))).toBe(true)
      expect(existsSync(join(root, theme, 'assets', 'storyboard-shot-03.png'))).toBe(true)
      // Bytes landed on disk unchanged.
      expect(readFileSync(join(root, theme, 'assets', 'storyboard-shot-01.png'))).toEqual(Buffer.from([0x89, 0x50, 0x4e, 0x47]))
    } finally {
      rmSync(root, { recursive: true, force: true })
    }
  })

  it('renders nothing when every visual is empty', async () => {
    const root = themeDir()
    try {
      const stub = imageGeneration()
      const result = await generateStoryboardImages(stub.service, root, 'topic', ['  ', ''])
      expect(result.images).toEqual([])
      expect(stub.generate).not.toHaveBeenCalled()
    } finally {
      rmSync(root, { recursive: true, force: true })
    }
  })
})

describe('generateCoverImage', () => {
  it('renders the cover prompt into cover.png', async () => {
    const root = themeDir()
    const theme = 'topic'
    try {
      const stub = imageGeneration()
      const result = await generateCoverImage(stub.service, root, theme, '删掉一半效率工具，深蓝主色')
      expect(result.images).toHaveLength(1)
      expect(result.images[0]).toMatchObject({ file: 'cover.png', prompt: '删掉一半效率工具，深蓝主色' })
      expect(existsSync(join(root, theme, 'assets', 'cover.png'))).toBe(true)
    } finally {
      rmSync(root, { recursive: true, force: true })
    }
  })

  it('renders nothing for an empty prompt', async () => {
    const root = themeDir()
    try {
      const stub = imageGeneration()
      const result = await generateCoverImage(stub.service, root, 'topic', '  ')
      expect(result.images).toEqual([])
      expect(stub.generate).not.toHaveBeenCalled()
    } finally {
      rmSync(root, { recursive: true, force: true })
    }
  })

  it('names the file by the media type the bytes carry, not by a fixed .png', async () => {
    const root = themeDir()
    const theme = 'topic'
    try {
      const generate = vi.fn(async () => [{
        bytes: Uint8Array.from([0xff, 0xd8, 0xff, 0xe0]),
        mediaType: 'image/jpeg',
        model: 'test-model',
      }])
      const service = { generate } as unknown as ImageGeneration
      const result = await generateCoverImage(service, root, theme, '封面提示词')
      expect(result.images[0]).toMatchObject({ file: 'cover.jpg', mediaType: 'image/jpeg' })
      expect(existsSync(join(root, theme, 'assets', 'cover.jpg'))).toBe(true)
      expect(existsSync(join(root, theme, 'assets', 'cover.png'))).toBe(false)
    } finally {
      rmSync(root, { recursive: true, force: true })
    }
  })
})

describe('readCreateImageFile', () => {
  /** A theme directory with one image written by hand. */
  function themeWithImage(name: string, bytes: Uint8Array): string {
    const root = mkdtempSync(join(tmpdir(), 'dsh-create-read-'))
    mkdirSync(join(root, 'topic', 'assets'), { recursive: true })
    writeFileSync(join(root, 'topic', 'assets', name), bytes)
    return root
  }

  it('reads a stored png back with its sniffed media type and base64 bytes', async () => {
    const root = themeWithImage('cover.png', Uint8Array.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a]))
    try {
      const read = await readCreateImageFile(root, 'topic', 'cover.png')
      expect(read.mediaType).toBe('image/png')
      expect(Buffer.from(read.base64, 'base64')).toEqual(Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a]))
    } finally {
      rmSync(root, { recursive: true, force: true })
    }
  })

  it('rejects a file whose bytes are not a raster image, whatever the extension claims', async () => {
    const root = themeWithImage('cover.png', Uint8Array.from([0x3c, 0x68, 0x74, 0x6d, 0x6c]))
    try {
      await expect(readCreateImageFile(root, 'topic', 'cover.png')).rejects.toThrow('not a supported raster image')
    } finally {
      rmSync(root, { recursive: true, force: true })
    }
  })

  it('rejects a read past the byte cap', async () => {
    const root = mkdtempSync(join(tmpdir(), 'dsh-create-read-'))
    try {
      mkdirSync(join(root, 'topic', 'assets'), { recursive: true })
      writeFileSync(join(root, 'topic', 'assets', 'cover.png'), Buffer.alloc(CREATE_MAX_IMAGE_BYTES + 1, 0x89))
      await expect(readCreateImageFile(root, 'topic', 'cover.png')).rejects.toThrow('read cap')
    } finally {
      rmSync(root, { recursive: true, force: true })
    }
  })
})
