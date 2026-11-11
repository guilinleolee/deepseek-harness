import { describe, expect, it } from 'vitest'
import {
  OPENAI_IMAGE_DEFAULT_MODEL, OpenAiImageProvider, detectMediaType, generationsUrl, parseOpenAiImageResponse,
} from '../src/openai.ts'
import type { ImageGenerationRequest } from '../src/types.ts'

const PNG_BYTES = Uint8Array.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a])
const JPEG_BYTES = Uint8Array.from([0xff, 0xd8, 0xff, 0xe0])

/** Encode bytes as the base64 the wire carries. */
function b64(bytes: Uint8Array): string {
  return Buffer.from(bytes).toString('base64')
}

function request(overrides: Partial<ImageGenerationRequest> = {}): ImageGenerationRequest {
  return { providerId: 'openai-compatible', prompt: '一只猫', model: '', width: 0, height: 0, count: 1, ...overrides }
}

/** The absolute URL of one fetch input, never the object's default stringification. */
function fetchInputUrl(input: string | URL | Request): string {
  if (typeof input === 'string') return input
  if (input instanceof URL) return input.href
  return input.url
}

/** The request body of one recorded call as text. */
function bodyText(init: RequestInit | undefined): string {
  const body = init?.body
  if (typeof body === 'string') return body
  if (body === null || body === undefined) return ''
  throw new Error('the recorded call body is not a string')
}

/** A fetch stand-in that records the call and answers with one canned response. */
function stubFetch(response: Response | (() => Response)): { calls: { url: string; init: RequestInit }[]; fetchImpl: typeof fetch } {
  const calls: { url: string; init: RequestInit }[] = []
  const fetchImpl: typeof fetch = async (input, init) => {
    calls.push({ url: fetchInputUrl(input), init: init ?? {} })
    return typeof response === 'function' ? response() : response
  }
  return { calls, fetchImpl }
}

describe('generationsUrl', () => {
  it('appends the generations path and tolerates a trailing slash', () => {
    expect(generationsUrl('https://api.example.com/v1')).toBe('https://api.example.com/v1/images/generations')
    expect(generationsUrl('https://api.example.com/v1/')).toBe('https://api.example.com/v1/images/generations')
    expect(generationsUrl('https://api.example.com/v1///')).toBe('https://api.example.com/v1/images/generations')
  })
})

describe('detectMediaType', () => {
  it('prefers the declared type and otherwise reads the byte prefix', () => {
    expect(detectMediaType('image/webp', PNG_BYTES)).toBe('image/webp')
    expect(detectMediaType(undefined, PNG_BYTES)).toBe('image/png')
    expect(detectMediaType(undefined, JPEG_BYTES)).toBe('image/jpeg')
    expect(detectMediaType(undefined, Uint8Array.from([0x52, 0x49, 0x46, 0x46]))).toBe('image/webp')
    expect(detectMediaType(undefined, Uint8Array.from([0x00, 0x00]))).toBe('application/octet-stream')
    expect(detectMediaType('  ', PNG_BYTES)).toBe('image/png')
  })
})

describe('parseOpenAiImageResponse', () => {
  it('decodes every base64 entry into bytes', () => {
    const results = parseOpenAiImageResponse(
      { data: [{ b64_json: b64(PNG_BYTES) }, { b64_json: b64(JPEG_BYTES) }] },
      'gpt-image-1',
    )
    expect(results).toHaveLength(2)
    expect(results[0]?.mediaType).toBe('image/png')
    expect(results[0]?.model).toBe('gpt-image-1')
    expect(Math.round(results[1]?.mediaType === 'image/jpeg' ? 1 : 0)).toBe(1)
  })

  it('rejects a URL entry instead of fetching it', () => {
    expect(() => parseOpenAiImageResponse({ data: [{ url: 'https://cdn.example.com/a.png' }] }, 'm'))
      .toThrow('URL instead of image bytes')
  })

  it('rejects an empty or missing data array', () => {
    expect(() => parseOpenAiImageResponse({ data: [] }, 'm')).toThrow('no image data')
    expect(() => parseOpenAiImageResponse({}, 'm')).toThrow('no image data')
    expect(() => parseOpenAiImageResponse(null, 'm')).toThrow('no image data')
  })

  it('rejects a body whose entries are all unusable', () => {
    expect(() => parseOpenAiImageResponse({ data: [{ b64_json: '' }] }, 'm')).toThrow('no usable image entry')
  })
})

describe('OpenAiImageProvider', () => {
  it('posts the request body with the bearer credential and returns the images', async () => {
    const stub = stubFetch(new Response(JSON.stringify({ data: [{ b64_json: b64(PNG_BYTES) }] }), { status: 200 }))
    const provider = new OpenAiImageProvider({ baseURL: 'https://api.example.com/v1', apiKey: 'sk-test', fetchImpl: stub.fetchImpl })
    const images = await provider.generate(request({ width: 1024, height: 1024, count: 2 }))
    expect(images).toHaveLength(1)
    const call = stub.calls[0]
    expect(call?.url).toBe('https://api.example.com/v1/images/generations')
    expect((call?.init.headers as Record<string, string>).Authorization).toBe('Bearer sk-test')
    expect(JSON.parse(bodyText(call?.init))).toEqual({
      model: OPENAI_IMAGE_DEFAULT_MODEL, prompt: '一只猫', n: 2, size: '1024x1024',
    })
  })

  it('omits the size when no dimension is stated and honours a stated model', async () => {
    const stub = stubFetch(new Response(JSON.stringify({ data: [{ b64_json: b64(PNG_BYTES) }] }), { status: 200 }))
    const provider = new OpenAiImageProvider({ baseURL: 'https://x/v1', apiKey: 'k', fetchImpl: stub.fetchImpl })
    await provider.generate(request({ model: 'custom-image', count: 1 }))
    const body = JSON.parse(bodyText(stub.calls[0]?.init)) as Record<string, unknown>
    expect(body).not.toHaveProperty('size')
    expect(body.model).toBe('custom-image')
  })

  it('reports the HTTP status when the provider refuses', async () => {
    const stub = stubFetch(new Response('nope', { status: 429 }))
    const provider = new OpenAiImageProvider({ baseURL: 'https://x/v1', apiKey: 'k', fetchImpl: stub.fetchImpl })
    await expect(provider.generate(request())).rejects.toThrow('HTTP 429')
  })

  it('reports a non-JSON body instead of throwing a parse error', async () => {
    const stub = stubFetch(new Response('<html>bad gateway</html>', { status: 200 }))
    const provider = new OpenAiImageProvider({ baseURL: 'https://x/v1', apiKey: 'k', fetchImpl: stub.fetchImpl })
    await expect(provider.generate(request())).rejects.toThrow('not JSON')
  })

  it('reports a transport failure as a provider failure', async () => {
    const stub = stubFetch(() => { throw new Error('ECONNREFUSED') })
    const provider = new OpenAiImageProvider({ baseURL: 'https://x/v1', apiKey: 'k', fetchImpl: stub.fetchImpl })
    await expect(provider.generate(request())).rejects.toThrow('ECONNREFUSED')
  })

  it('reports an abort as an aborted call', async () => {
    const controller = new AbortController()
    controller.abort()
    const stub = stubFetch(() => { throw new Error('aborted') })
    const provider = new OpenAiImageProvider({ baseURL: 'https://x/v1', apiKey: 'k', fetchImpl: stub.fetchImpl })
    await expect(provider.generate(request(), controller.signal)).rejects.toThrow('aborted')
  })
})
