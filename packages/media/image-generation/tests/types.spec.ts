import { describe, expect, it } from 'vitest'
import {
  IMAGE_MAX_COUNT, IMAGE_MAX_PROMPT_CHARS, ImageGenerationError, assertImageRequest,
} from '../src/types.ts'
import type { ImageGenerationRequest } from '../src/types.ts'

function request(overrides: Partial<ImageGenerationRequest> = {}): ImageGenerationRequest {
  return { providerId: 'openai-compatible', prompt: '一只猫', model: '', width: 0, height: 0, count: 1, ...overrides }
}

describe('assertImageRequest', () => {
  it('accepts a minimal request', () => {
    expect(assertImageRequest(request())).toEqual(request())
  })

  it('rejects an empty prompt', () => {
    expect(() => assertImageRequest(request({ prompt: '   ' }))).toThrow('non-empty prompt')
  })

  it('rejects a prompt past the cap', () => {
    const prompt = 'x'.repeat(IMAGE_MAX_PROMPT_CHARS + 1)
    expect(() => assertImageRequest(request({ prompt }))).toThrow(`${IMAGE_MAX_PROMPT_CHARS}-character cap`)
    expect(assertImageRequest(request({ prompt: 'x'.repeat(IMAGE_MAX_PROMPT_CHARS) })).prompt).toHaveLength(IMAGE_MAX_PROMPT_CHARS)
  })

  it('rejects counts outside the accepted range', () => {
    expect(() => assertImageRequest(request({ count: 0 }))).toThrow(`between 1 and ${IMAGE_MAX_COUNT}`)
    expect(() => assertImageRequest(request({ count: IMAGE_MAX_COUNT + 1 }))).toThrow('between 1 and')
    expect(() => assertImageRequest(request({ count: 1.5 }))).toThrow('between 1 and')
  })

  it('treats a zero side as the provider default and bounds a stated one', () => {
    expect(assertImageRequest(request({ width: 0, height: 0 }))).toEqual(request())
    expect(() => assertImageRequest(request({ width: 10, height: 10 }))).toThrow('pixels')
    expect(() => assertImageRequest(request({ width: 4096, height: 4096 }))).toThrow('pixels')
    expect(() => assertImageRequest(request({ width: 512, height: 0.5 }))).toThrow('pixels')
  })
})

describe('ImageGenerationError', () => {
  it('carries its code and name', () => {
    const error = new ImageGenerationError('NO_PROVIDER', 'nothing registered')
    expect(error.code).toBe('NO_PROVIDER')
    expect(error.name).toBe('ImageGenerationError')
    expect(error.message).toBe('nothing registered')
    expect(error).toBeInstanceOf(Error)
  })
})
