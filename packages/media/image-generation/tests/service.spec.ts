/** Provider routing, registration lifetimes, and degradation when the capability is unconfigured. */
import { Context } from '@deepseek-ai/cordis'
import { describe, expect, it, vi } from 'vitest'
import ImageGeneration from '../src/index.ts'
import { OPENAI_IMAGE_PROVIDER_ID } from '../src/openai.ts'
import { ImageGenerationError } from '../src/types.ts'
import type { ImageGenerationProvider, ImageGenerationRequest } from '../src/types.ts'
import { liveConfig } from '../../../settings/settings/tests/live-config.ts'

function request(overrides: Partial<ImageGenerationRequest> = {}): ImageGenerationRequest {
  return { providerId: '', prompt: '一只猫', model: '', width: 0, height: 0, count: 1, ...overrides }
}

/** A provider stand-in recording every request it receives. */
function provider(id = OPENAI_IMAGE_PROVIDER_ID): { provider: ImageGenerationProvider; seen: ImageGenerationRequest[] } {
  const seen: ImageGenerationRequest[] = []
  return {
    seen,
    provider: {
      info: { id, name: id },
      generate: async (incoming) => {
        seen.push(incoming)
        return [{ bytes: Uint8Array.from([0x89, 0x50]), mediaType: 'image/png', model: incoming.model }]
      },
    },
  }
}

/** A context with a credentials service answering the given values by reference name. */
function credentialsContext(values: Record<string, string> = {}): Context {
  const ctx = new Context()
  ctx.provide('credentials', {
    resolve: vi.fn(async (ref: string) => (values[ref] === undefined ? undefined : { value: values[ref] })),
  } as never)
  return ctx
}

describe('ImageGeneration registry', () => {
  it('registers the bundled provider and lists it', async () => {
    const ctx = credentialsContext()
    const fiber = ctx.plugin(ImageGeneration, {})
    await ctx.fiber.await()
    expect(ctx.imageGeneration.list()).toEqual([{ id: OPENAI_IMAGE_PROVIDER_ID, name: 'OpenAI-compatible image API' }])
    await fiber.dispose()
  })

  it('rejects a duplicate route without replacing the original', async () => {
    const ctx = credentialsContext()
    const fiber = ctx.plugin(ImageGeneration, {})
    await ctx.fiber.await()
    const original = provider()
    expect(() => ctx.imageGeneration.register(original.provider)).toThrow('already registered')
    await fiber.dispose()
  })

  it('removes a provider when its own disposer runs', async () => {
    const ctx = credentialsContext()
    const fiber = ctx.plugin(ImageGeneration, {})
    await ctx.fiber.await()
    const extra = provider('other')
    const dispose = ctx.imageGeneration.register(extra.provider)
    expect(ctx.imageGeneration.list().map(info => info.id)).toEqual([OPENAI_IMAGE_PROVIDER_ID, 'other'])
    dispose()
    expect(ctx.imageGeneration.list().map(info => info.id)).toEqual([OPENAI_IMAGE_PROVIDER_ID])
    await fiber.dispose()
  })

  it('refuses registration once the service is disposed', async () => {
    const ctx = credentialsContext()
    const fiber = ctx.plugin(ImageGeneration, {})
    await ctx.fiber.await()
    const service = ctx.imageGeneration
    await fiber.dispose()
    // The context no longer exposes the service, and the retained instance
    // refuses new work instead of registering into a dead registry.
    expect(ctx.get('imageGeneration')).toBeUndefined()
    expect(() => service.register(provider('late').provider)).toThrow('disposed')
  })

  it('routes by request provider, then by the configured default', async () => {
    const ctx = credentialsContext()
    const fiber = ctx.plugin(ImageGeneration, { defaultProvider: 'custom' })
    await ctx.fiber.await()
    const custom = provider('custom')
    ctx.imageGeneration.register(custom.provider)
    await ctx.imageGeneration.generate(request({ model: 'm' }))
    expect(custom.seen).toHaveLength(1)
    expect(custom.seen[0]?.providerId).toBe('custom')
    await fiber.dispose()
  })

  it('rejects an unknown route and names the registered ones', async () => {
    const ctx = credentialsContext()
    const fiber = ctx.plugin(ImageGeneration, {})
    await ctx.fiber.await()
    await expect(ctx.imageGeneration.generate(request({ providerId: 'nope' })))
      .rejects.toThrow(`no image provider is registered for route "nope"; registered routes: ${OPENAI_IMAGE_PROVIDER_ID}`)
    await fiber.dispose()
  })

  it('resolves the configured model and dimensions before validation', async () => {
    const ctx = credentialsContext()
    const fiber = ctx.plugin(ImageGeneration, { defaultModel: 'configured', defaultWidth: 512, defaultHeight: 768 })
    await ctx.fiber.await()
    const custom = provider('other')
    ctx.imageGeneration.register(custom.provider)
    await ctx.imageGeneration.generate(request({ providerId: 'other' }))
    expect(custom.seen[0]).toMatchObject({ model: 'configured', width: 512, height: 768 })
    await fiber.dispose()
  })

  it('keeps a stated request value over the configured default', async () => {
    const ctx = credentialsContext()
    const fiber = ctx.plugin(ImageGeneration, { defaultModel: 'configured', defaultWidth: 512, defaultHeight: 768 })
    await ctx.fiber.await()
    const custom = provider('explicit')
    ctx.imageGeneration.register(custom.provider)
    await ctx.imageGeneration.generate(request({ providerId: 'explicit', model: 'stated', width: 256, height: 256 }))
    expect(custom.seen[0]).toMatchObject({ model: 'stated', width: 256, height: 256 })
    await fiber.dispose()
  })

  it('validates the resolved request before reaching the provider', async () => {
    const ctx = credentialsContext()
    const fiber = ctx.plugin(ImageGeneration, {})
    await ctx.fiber.await()
    const custom = provider('other')
    ctx.imageGeneration.register(custom.provider)
    await expect(ctx.imageGeneration.generate(request({ providerId: 'other', prompt: '  ' })))
      .rejects.toThrow('non-empty prompt')
    expect(custom.seen).toHaveLength(0)
    await fiber.dispose()
  })
})

describe('bundled provider configuration', () => {
  it('fails loud without an endpoint instead of silently degrading', async () => {
    const ctx = credentialsContext({ IMAGE_API_KEY: 'k' })
    const fiber = ctx.plugin(ImageGeneration, { apiKeyEnv: 'IMAGE_API_KEY' })
    await ctx.fiber.await()
    const error = await ctx.imageGeneration.generate(request()).catch((cause: unknown) => cause)
    expect(error).toBeInstanceOf(ImageGenerationError)
    expect((error as ImageGenerationError).code).toBe('INVALID_REQUEST')
    expect((error as Error).message).toContain('baseURL')
    await fiber.dispose()
  })

  it('fails loud without a credential reference', async () => {
    const ctx = credentialsContext()
    const fiber = ctx.plugin(ImageGeneration, { baseURL: 'https://api.example.com/v1' })
    await ctx.fiber.await()
    const error = await ctx.imageGeneration.generate(request()).catch((cause: unknown) => cause)
    expect((error as ImageGenerationError).code).toBe('MISSING_CREDENTIAL')
    expect((error as Error).message).toContain('apiKeyEnv')
    await fiber.dispose()
  })

  it('fails loud when the referenced credential is not stored', async () => {
    const ctx = credentialsContext()
    const fiber = ctx.plugin(ImageGeneration, { baseURL: 'https://api.example.com/v1', apiKeyEnv: 'MISSING' })
    await ctx.fiber.await()
    const error = await ctx.imageGeneration.generate(request()).catch((cause: unknown) => cause)
    expect((error as ImageGenerationError).code).toBe('MISSING_CREDENTIAL')
    expect((error as Error).message).toContain('MISSING')
    await fiber.dispose()
  })

  it('reads the endpoint and credential live, so a settings change reaches the next request', async () => {
    const ctx = credentialsContext({ FIRST: 'k1', SECOND: 'k2' })
    const calls: { url: string; init: RequestInit | undefined }[] = []
    const fetchImpl: typeof fetch = async (input, init) => {
      calls.push({ url: typeof input === 'string' ? input : input instanceof URL ? input.href : input.url, init })
      return new Response(JSON.stringify({
        data: [{ b64_json: Buffer.from([0x89, 0x50]).toString('base64') }],
      }), { status: 200 })
    }
    const original = globalThis.fetch
    globalThis.fetch = fetchImpl
    try {
      const live = await liveConfig(ctx, ImageGeneration, { baseURL: 'https://first.example/v1', apiKeyEnv: 'FIRST' })
      await ctx.imageGeneration.generate(request())
      expect(calls[0]?.url).toBe('https://first.example/v1/images/generations')
      await live.update({ baseURL: 'https://second.example/v1', apiKeyEnv: 'SECOND' })
      await ctx.imageGeneration.generate(request())
      expect(calls[1]?.url).toBe('https://second.example/v1/images/generations')
      expect((calls[1]?.init?.headers as Record<string, string>).Authorization).toBe('Bearer k2')
    } finally {
      globalThis.fetch = original
    }
  })
})
