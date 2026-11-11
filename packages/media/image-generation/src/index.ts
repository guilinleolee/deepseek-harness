/**
 * The image-generation capability: a provider registry behind one
 * provider-neutral service. A consumer names a provider route and a prompt;
 * the registered provider produces the images.
 *
 * The package also ships the OpenAI-compatible provider, because that wire
 * shape is what the hosted image models speak. Its endpoint and credential
 * are settings, so one provider serves every compatible service. That
 * provider stays registered for the whole lifetime of the service and reads
 * the settings live, so changing the endpoint reaches the next request
 * without a restart; a request made before an endpoint is configured fails
 * with `INVALID_REQUEST` naming the setting, which is what lets a caller
 * degrade to text.
 */

import { Service, type Context, type Volatile } from '@deepseek-ai/cordis'
import z from '@deepseek-ai/schemastery'
import { credentialRef } from '@deepseek-ai/dsh-credentials'
import type {} from '@deepseek-ai/dsh-credentials'
import { OPENAI_IMAGE_PROVIDER_ID, OpenAiImageProvider } from './openai.ts'
import { ImageGenerationError, assertImageRequest } from './types.ts'
import type {
  ImageGenerationProvider, ImageGenerationRequest, ImageGenerationResult, ImageProviderInfo,
} from './types.ts'

export * from './types.ts'
export {
  detectMediaType, generationsUrl, OPENAI_IMAGE_DEFAULT_MODEL, OPENAI_IMAGE_MAX_RESPONSE_BYTES,
  OPENAI_IMAGE_PROVIDER_ID, OPENAI_IMAGE_TIMEOUT_MS, OpenAiImageProvider, parseOpenAiImageResponse,
} from './openai.ts'

declare module '@deepseek-ai/cordis' {
  interface Context {
    /** The image-generation provider registry and service. */
    imageGeneration: ImageGeneration
  }
}

/** The connection and selection settings of the image-generation capability. */
export interface Config {
  /** The provider route used when a request names none. */
  defaultProvider: Volatile<string>
  /** The model used when a request names none; empty leaves the provider's own default. */
  defaultModel: Volatile<string>
  /** The image width used when a request names none; `0` leaves the provider's own default. */
  defaultWidth: Volatile<number>
  /** The image height used when a request names none; `0` leaves the provider's own default. */
  defaultHeight: Volatile<number>
  /**
   * The OpenAI-compatible API base including its path prefix;
   * `/images/generations` is appended. Empty leaves the bundled provider
   * without an endpoint, so every request fails until it is set.
   */
  baseURL: Volatile<string>
  /** The credential reference of the bundled provider; empty means no credential. */
  apiKeyEnv: Volatile<string>
}

/** The settings schema of the image-generation capability. */
export const Config = z.object({
  defaultProvider: z.string().default(OPENAI_IMAGE_PROVIDER_ID).volatile(),
  defaultModel: z.string().default('').volatile(),
  defaultWidth: z.number().step(1).min(0).default(0).volatile(),
  defaultHeight: z.number().step(1).min(0).default(0).volatile(),
  baseURL: z.string().default('').volatile(),
  apiKeyEnv: z.string().default('').role('credential-ref').volatile(),
})

/** One registered provider. */
interface Registration {
  readonly provider: ImageGenerationProvider
}

/** The image-generation service: the provider registry and the request path every consumer shares. */
export default class ImageGeneration extends Service {
  /** The settings schema of the capability. */
  static Config = Config

  /** The credential source of the bundled provider. */
  static inject = ['credentials']

  /** The provider routes registered in this composition. */
  private readonly providers = new Map<string, Registration>()
  /** The lifetime of the registry; a disposed service refuses new work. */
  private readonly lifetime = new AbortController()

  /**
   * @param ctx - the context exposing the credentials service.
   * @param config - the capability settings.
   */
  constructor(ctx: Context, private readonly config: Config) {
    super(ctx, 'imageGeneration')
    ctx.effect(() => () => {
      this.lifetime.abort(new Error('Image generation service disposed'))
      this.providers.clear()
    })
    ctx.effect(() => this.register({
      info: { id: OPENAI_IMAGE_PROVIDER_ID, name: 'OpenAI-compatible image API' },
      generate: async (request, signal) => this.generateOpenAi(request, signal),
    }))
  }

  /**
   * Register one provider; a duplicate route id fails without replacing the
   * original.
   * @param provider - the provider owned by the contributing fiber.
   * @returns the disposer that removes it.
   */
  register(provider: ImageGenerationProvider): () => void {
    this.lifetime.signal.throwIfAborted()
    if (this.providers.has(provider.info.id)) {
      throw new Error(`Image provider already registered: ${provider.info.id}`)
    }
    this.providers.set(provider.info.id, { provider })
    return () => { this.providers.delete(provider.info.id) }
  }

  /**
   * The registered provider routes, in registration order.
   * @returns the route identities and display names.
   */
  list(): readonly ImageProviderInfo[] {
    return [...this.providers.values()].map(registration => registration.provider.info)
  }

  /**
   * Produce images for one request. The request's empty provider, model, and
   * dimensions take the configured defaults before validation.
   * @param request - the request.
   * @param signal - caller cancellation.
   * @returns the produced images.
   * @throws an {@link ImageGenerationError} when no provider serves the route,
   *   the request violates the request contract, or the provider fails.
   */
  async generate(request: ImageGenerationRequest, signal?: AbortSignal): Promise<readonly ImageGenerationResult[]> {
    const configured = this.config.defaultProvider.get()
    const providerId = request.providerId.length > 0 ? request.providerId : configured
    const registration = this.providers.get(providerId)
    if (registration === undefined) {
      throw new ImageGenerationError(
        'NO_PROVIDER',
        `no image provider is registered for route "${providerId}"; registered routes: `
        + [...this.providers.keys()].join(', '),
      )
    }
    const resolved: ImageGenerationRequest = {
      providerId,
      prompt: request.prompt,
      model: request.model.length > 0 ? request.model : this.config.defaultModel.get(),
      width: request.width > 0 ? request.width : this.config.defaultWidth.get(),
      height: request.height > 0 ? request.height : this.config.defaultHeight.get(),
      count: request.count,
    }
    assertImageRequest(resolved)
    return registration.provider.generate(resolved, signal)
  }

  /** Send one request through the bundled OpenAI-compatible provider, reading its settings live. */
  private async generateOpenAi(
    request: ImageGenerationRequest, signal?: AbortSignal,
  ): Promise<readonly ImageGenerationResult[]> {
    const baseURL = this.config.baseURL.get().trim()
    if (baseURL.length === 0) {
      throw new ImageGenerationError(
        'INVALID_REQUEST',
        'the image provider has no endpoint; set this plugin\'s baseURL setting',
      )
    }
    const key = await this.resolveApiKey()
    return new OpenAiImageProvider({ baseURL, apiKey: key }).generate(request, signal)
  }

  /** The configured credential of the bundled provider; missing configuration fails loud. */
  private async resolveApiKey(): Promise<string> {
    const ref = this.config.apiKeyEnv.get().trim()
    if (ref.length === 0) {
      throw new ImageGenerationError('MISSING_CREDENTIAL', 'the image provider has no apiKeyEnv setting')
    }
    const resolved = await this.ctx.credentials.resolve(credentialRef(ref))
    if (resolved === undefined) {
      throw new ImageGenerationError(
        'MISSING_CREDENTIAL',
        `no credential stored for "${ref}"; store it through the credentials service`,
      )
    }
    return resolved.value
  }
}
