/**
 * The OpenAI-compatible image provider: one POST to
 * `{baseURL}/images/generations` carrying the prompt, and a response whose
 * `data` array carries either inline base64 bytes or a URL to fetch.
 *
 * The wire shape is the de-facto standard shared by the hosted image models,
 * so one provider serves them; the endpoint and the credential are
 * configuration, never code.
 */

import { ImageGenerationError } from './types.ts'
import type {
  ImageGenerationProvider, ImageGenerationRequest, ImageGenerationResult, ImageProviderInfo,
} from './types.ts'

/** The route key of the OpenAI-compatible provider. */
export const OPENAI_IMAGE_PROVIDER_ID = 'openai-compatible'

/** The provider's default model when a request names none. */
export const OPENAI_IMAGE_DEFAULT_MODEL = 'gpt-image-1'

/** How long one generation request may take before it is abandoned. */
export const OPENAI_IMAGE_TIMEOUT_MS = 120_000

/** The largest response body one generation accepts. */
export const OPENAI_IMAGE_MAX_RESPONSE_BYTES = 64 * 1024 * 1024

/** The endpoint facts and credential of one generation request. */
export interface OpenAiImageConnection {
  /** The API base including its path prefix; `/images/generations` is appended. */
  readonly baseURL: string
  /** The credential sent as a bearer token. */
  readonly apiKey: string
  /** The fetch implementation; the global one by default. */
  readonly fetchImpl?: typeof fetch
}

/** One entry of the response `data` array. */
interface OpenAiImageEntry {
  readonly b64_json?: string
  readonly url?: string
}

/** The response body of one generation request. */
interface OpenAiImageResponse {
  readonly data?: readonly OpenAiImageEntry[]
}

/**
 * Join the API base with the generations path.
 * @param baseURL - the API base including its path prefix, with or without a trailing slash.
 * @returns the absolute generations endpoint URL.
 */
export function generationsUrl(baseURL: string): string {
  return `${baseURL.replace(/\/+$/u, '')}/images/generations`
}

/**
 * Read the media type a byte prefix declares; the provider's own type field
 * wins, and the prefix is the fallback for a response that omits it.
 * @param mediaType - the type the provider declared.
 * @param bytes - the encoded image bytes.
 * @returns the media type to record.
 */
export function detectMediaType(mediaType: string | undefined, bytes: Uint8Array): string {
  if (mediaType !== undefined && mediaType.trim().length > 0) return mediaType.trim()
  if (bytes[0] === 0x89 && bytes[1] === 0x50) return 'image/png'
  if (bytes[0] === 0xff && bytes[1] === 0xd8) return 'image/jpeg'
  if (bytes[0] === 0x52 && bytes[1] === 0x49) return 'image/webp'
  return 'application/octet-stream'
}

/**
 * Decode one base64 payload into bytes.
 * @param encoded - the base64 text.
 * @returns the decoded bytes.
 * @throws an {@link ImageGenerationError} when the payload is not base64.
 */
export function decodeBase64(encoded: string): Uint8Array {
  try {
    return new Uint8Array(Buffer.from(encoded, 'base64'))
  } catch {
    throw new ImageGenerationError('PROVIDER_FAILED', 'image provider returned a payload that is not base64')
  }
}

/**
 * Parse one response body into the produced images.
 * @param body - the parsed response body.
 * @param model - the model the request named.
 * @returns the produced images.
 * @throws an {@link ImageGenerationError} when the body carries no usable image.
 */
export function parseOpenAiImageResponse(body: unknown, model: string): ImageGenerationResult[] {
  const record = body as OpenAiImageResponse | null
  const entries = record?.data ?? []
  if (entries.length === 0) {
    throw new ImageGenerationError('PROVIDER_FAILED', 'image provider returned no image data')
  }
  const results: ImageGenerationResult[] = []
  for (const entry of entries) {
    if (typeof entry.b64_json === 'string' && entry.b64_json.length > 0) {
      const bytes = decodeBase64(entry.b64_json)
      results.push({ bytes, mediaType: detectMediaType(undefined, bytes), model })
      continue
    }
    if (typeof entry.url === 'string' && entry.url.length > 0) {
      throw new ImageGenerationError(
        'PROVIDER_FAILED',
        'image provider answered with a URL instead of image bytes; the URL fetch is not supported',
      )
    }
  }
  if (results.length === 0) {
    throw new ImageGenerationError('PROVIDER_FAILED', 'image provider returned no usable image entry')
  }
  return results
}

/** The OpenAI-compatible image provider. */
export class OpenAiImageProvider implements ImageGenerationProvider {
  /** The provider's route identity and display name. */
  readonly info: ImageProviderInfo = {
    id: OPENAI_IMAGE_PROVIDER_ID,
    name: 'OpenAI-compatible image API',
  }

  /**
   * @param connection - the endpoint and credential the provider authenticates with.
   */
  constructor(private readonly connection: OpenAiImageConnection) {}

  /**
   * Produce the images of one request.
   * @param request - the validated request.
   * @param signal - caller cancellation.
   * @returns the produced images.
   */
  async generate(request: ImageGenerationRequest, signal?: AbortSignal): Promise<readonly ImageGenerationResult[]> {
    const fetchImpl = this.connection.fetchImpl ?? fetch
    const model = request.model.length > 0 ? request.model : OPENAI_IMAGE_DEFAULT_MODEL
    const body: Record<string, unknown> = {
      model,
      prompt: request.prompt,
      n: request.count,
    }
    if (request.width > 0) body.size = `${request.width}x${request.height}`
    const deadline = AbortSignal.timeout(OPENAI_IMAGE_TIMEOUT_MS)
    const combined = signal === undefined ? deadline : AbortSignal.any([signal, deadline])
    let response: Response
    try {
      response = await fetchImpl(generationsUrl(this.connection.baseURL), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.connection.apiKey}`,
        },
        body: JSON.stringify(body),
        signal: combined,
      })
    } catch (error) {
      if (signal?.aborted === true) {
        throw new ImageGenerationError('ABORTED', 'image generation was aborted')
      }
      if (deadline.aborted) {
        throw new ImageGenerationError(
          'PROVIDER_FAILED',
          `image provider did not answer within ${OPENAI_IMAGE_TIMEOUT_MS} ms`,
        )
      }
      throw new ImageGenerationError(
        'PROVIDER_FAILED',
        `image provider request failed: ${error instanceof Error ? error.message : String(error)}`,
      )
    }
    if (!response.ok) {
      throw new ImageGenerationError(
        'PROVIDER_FAILED',
        `image provider answered HTTP ${response.status}`,
      )
    }
    const declaredLength = Number(response.headers.get('content-length') ?? '0')
    if (Number.isFinite(declaredLength) && declaredLength > OPENAI_IMAGE_MAX_RESPONSE_BYTES) {
      throw new ImageGenerationError(
        'PROVIDER_FAILED',
        `image provider response exceeds the ${OPENAI_IMAGE_MAX_RESPONSE_BYTES}-byte cap`,
      )
    }
    let text: string
    try {
      text = await response.text()
    } catch {
      throw new ImageGenerationError('PROVIDER_FAILED', 'image provider response body could not be read')
    }
    if (Buffer.byteLength(text) > OPENAI_IMAGE_MAX_RESPONSE_BYTES) {
      throw new ImageGenerationError(
        'PROVIDER_FAILED',
        `image provider response exceeds the ${OPENAI_IMAGE_MAX_RESPONSE_BYTES}-byte cap`,
      )
    }
    let parsed: unknown
    try {
      parsed = JSON.parse(text)
    } catch {
      throw new ImageGenerationError('PROVIDER_FAILED', 'image provider returned a body that is not JSON')
    }
    return parseOpenAiImageResponse(parsed, model)
  }
}
