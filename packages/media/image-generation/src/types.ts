/**
 * Wire vocabulary of the image-generation capability: the request a consumer
 * sends, the provider contract that answers it, the produced image, and the
 * failures one call reports. Client-safe by construction — no Node or
 * filesystem imports.
 */

/** The largest prompt one request carries; the provider truncates beyond it. */
export const IMAGE_MAX_PROMPT_CHARS = 4_000

/** The largest images one request produces. */
export const IMAGE_MAX_COUNT = 4

/** The pixel bounds one request's width and height stay inside. */
export const IMAGE_MIN_SIDE = 64
/** The pixel bounds one request's width and height stay inside. */
export const IMAGE_MAX_SIDE = 2_048

/** One image request. */
export interface ImageGenerationRequest {
  /** The provider route; the capability's configured default when empty. */
  readonly providerId: string
  /** The text prompt the provider renders. */
  readonly prompt: string
  /** The provider's model id; the provider's default when empty. */
  readonly model: string
  /** Requested image width in pixels; the provider's default when zero. */
  readonly width: number
  /** Requested image height in pixels; the provider's default when zero. */
  readonly height: number
  /** How many images one call produces. */
  readonly count: number
}

/** One produced image. */
export interface ImageGenerationResult {
  /** The encoded image bytes. */
  readonly bytes: Uint8Array
  /** The media type of the bytes (`image/png`, `image/jpeg`, `image/webp`). */
  readonly mediaType: string
  /** The model that produced the image. */
  readonly model: string
}

/** Display metadata of one registered provider. */
export interface ImageProviderInfo {
  /** The provider route key a request names. */
  readonly id: string
  /** Human-readable provider name for selectors and diagnostics. */
  readonly name: string
}

/** A provider of image generation. */
export interface ImageGenerationProvider {
  /** The provider's route identity and display name. */
  readonly info: ImageProviderInfo
  /**
   * Produce the images of one request.
   * @param request - the validated request.
   * @param signal - caller cancellation.
   * @returns the produced images, at least one.
   */
  generate(request: ImageGenerationRequest, signal?: AbortSignal): Promise<readonly ImageGenerationResult[]>
}

/** Why one generation call failed. */
export type ImageGenerationErrorCode =
  /** No provider is registered under the requested route. */
  | 'NO_PROVIDER'
  /** The provider has no credential configured. */
  | 'MISSING_CREDENTIAL'
  /** The request violates the request contract. */
  | 'INVALID_REQUEST'
  /** The provider answered with a failure. */
  | 'PROVIDER_FAILED'
  /** The call was aborted. */
  | 'ABORTED'

/** One failed generation call. */
export class ImageGenerationError extends Error {
  /** Why the call failed. */
  readonly code: ImageGenerationErrorCode

  /**
   * @param code - why the call failed.
   * @param message - the failure detail.
   */
  constructor(code: ImageGenerationErrorCode, message: string) {
    super(message)
    this.name = 'ImageGenerationError'
    this.code = code
  }
}

/**
 * Validate one request against the request contract.
 * @param request - the raw request.
 * @returns the validated request.
 * @throws an {@link ImageGenerationError} naming the violated rule.
 */
export function assertImageRequest(request: ImageGenerationRequest): ImageGenerationRequest {
  if (request.prompt.trim().length === 0) {
    throw new ImageGenerationError('INVALID_REQUEST', 'image generation needs a non-empty prompt')
  }
  if (request.prompt.length > IMAGE_MAX_PROMPT_CHARS) {
    throw new ImageGenerationError(
      'INVALID_REQUEST',
      `image generation prompt exceeds the ${IMAGE_MAX_PROMPT_CHARS}-character cap`,
    )
  }
  if (!Number.isInteger(request.count) || request.count < 1 || request.count > IMAGE_MAX_COUNT) {
    throw new ImageGenerationError(
      'INVALID_REQUEST',
      `image generation count must be between 1 and ${IMAGE_MAX_COUNT}`,
    )
  }
  for (const side of [request.width, request.height]) {
    if (side === 0) continue
    if (!Number.isInteger(side) || side < IMAGE_MIN_SIDE || side > IMAGE_MAX_SIDE) {
      throw new ImageGenerationError(
        'INVALID_REQUEST',
        `image generation side must be 0 or between ${IMAGE_MIN_SIDE} and ${IMAGE_MAX_SIDE} pixels`,
      )
    }
  }
  return request
}
