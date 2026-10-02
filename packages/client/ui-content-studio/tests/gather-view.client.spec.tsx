// @vitest-environment jsdom
/**
 * The gather view surface: the material library renders through the reusable
 * SplitDetail layout, and every topic-bank entry answers under the reserved
 * `addToTopicBank` contract — the pending toast while no handler is plugged
 * in, the injected handler verbatim once the topic bank ships.
 */
import { act, cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import type { ComponentProps } from 'react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { createGatherController } from '../src/client/gather/gather-store.ts'
import type { GatherGateway, GatherMaterial } from '../src/client/gather/types.ts'
import { GatherView } from '../src/client/GatherView.tsx'
import { en } from '../src/client/locales.ts'

afterEach(() => {
  cleanup()
  window.localStorage.clear()
})

function material(id: string): GatherMaterial {
  return {
    id: id as GatherMaterial['id'],
    sourceId: 'source-1',
    sourceName: '源一',
    title: `素材 ${id}`,
    url: `https://example.com/${id}`,
    gatheredAt: '2026-09-25T00:00:00.000Z',
    status: 'unread',
  }
}

/** A controller over a stub gateway, with one theme holding two materials. */
async function harness() {
  const gateway: GatherGateway = {
    fetchFeed: vi.fn(),
    writeAsset: vi.fn(async () => ({ truncated: false })),
    readAsset: vi.fn(async () => ({})),
    readManifest: vi.fn(async (_theme: string) => ({
      manifest: { formatVersion: 0 as const, materials: [material('m-1'), material('m-2')] },
      problems: [],
    })),
    writeManifest: vi.fn(async (_theme: string, manifest: { formatVersion: 0; materials: readonly unknown[] }) => manifest as never),
    moveAsset: vi.fn(async () => undefined),
    deleteAsset: vi.fn(async () => undefined),
    processMaterial: vi.fn(),
  }
  const gather = createGatherController({
    gateway,
    listOutputs: async () => ({ root: '/outputs', projects: [{ topic: 'theme-a' }], problems: [] }),
    schedulePut: vi.fn(),
  })
  await gather.refreshThemes()
  await gather.selectTheme('theme-a')
  return { gather, gateway }
}

function renderGather(gather: ReturnType<typeof createGatherController>, addToTopicBank?: (materialId: string) => void) {
  const t = (key: keyof typeof en) => en[key]
  return render(
    <GatherView {...({ gather, onPushToCreate: vi.fn(), addToTopicBank, t } as unknown as ComponentProps<typeof GatherView>)} />,
  )
}

describe('GatherView', () => {
  it('renders material cards through the SplitDetail panes', async () => {
    const { gather } = await harness()
    renderGather(gather)
    await waitFor(() => {
      expect(screen.getByText('素材 m-1')).toBeTruthy()
    })
    expect(screen.getByText('素材 m-2')).toBeTruthy()
    // The detail region is the SplitDetail pane with its accessible label.
    expect(screen.getByRole('region', { name: en['gather.detail.label'] })).toBeTruthy()
    expect(screen.queryByText(en['gather.materials.empty'])).toBeNull()
  })

  it('answers the topic-bank entry with the pending toast when no handler is injected', async () => {
    const { gather } = await harness()
    renderGather(gather)
    await waitFor(() => {
      expect(screen.getAllByText(en['gather.detail.topicBankShort']).length).toBeGreaterThan(0)
    })
    fireEvent.click(screen.getAllByText(en['gather.detail.topicBankShort'])[0]!)
    await waitFor(() => {
      expect(screen.getByText(en['gather.notice.topicBankPending'])).toBeTruthy()
    })
  })

  it('routes the topic-bank entry to the injected addToTopicBank handler with the material id', async () => {
    const { gather } = await harness()
    const addToTopicBank = vi.fn()
    renderGather(gather, addToTopicBank)
    await waitFor(() => {
      expect(screen.getAllByText(en['gather.detail.topicBankShort']).length).toBeGreaterThan(0)
    })
    await act(async () => {
      fireEvent.click(screen.getAllByText(en['gather.detail.topicBankShort'])[0]!)
    })
    expect(addToTopicBank).toHaveBeenCalledWith('m-1')
    // The injected handler replaces the toast: no pending notice appears.
    expect(screen.queryByText(en['gather.notice.topicBankPending'])).toBeNull()
  })

  it('shows the detail pane empty state until a material is selected', async () => {
    const { gather } = await harness()
    renderGather(gather)
    await waitFor(() => {
      expect(screen.getByText('素材 m-1')).toBeTruthy()
    })
    expect(screen.getByText(en['gather.detail.empty'])).toBeTruthy()
  })
})
