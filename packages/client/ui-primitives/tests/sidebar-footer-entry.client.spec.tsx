// @vitest-environment jsdom
import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { SidebarFooterEntry } from '@deepseek-ai/dsh-client-ui-primitives'

afterEach(cleanup)

describe('SidebarFooterEntry', () => {
  it('renders the labeled wide row and forwards clicks', () => {
    const onClick = vi.fn()
    render(
      <SidebarFooterEntry
        wide
        label="内容创作"
        ariaLabel="打开内容创作"
        icon={<svg data-testid="ic" />}
        onClick={onClick}
      />,
    )
    const button = screen.getByRole('button', { name: '打开内容创作' })
    expect(screen.getByText('内容创作')).toBeDefined()
    expect(screen.getByTestId('ic')).toBeDefined()
    fireEvent.click(button)
    expect(onClick).toHaveBeenCalledTimes(1)
  })

  it('renders the rail icon inside the tooltip wrapper without the visible label', () => {
    const onClick = vi.fn()
    render(
      <SidebarFooterEntry
        wide={false}
        label="内容创作"
        ariaLabel="打开内容创作"
        icon={<svg data-testid="ic" />}
        onClick={onClick}
      />,
    )
    expect(screen.getByRole('button', { name: '打开内容创作' })).toBeDefined()
    expect(screen.queryByText('内容创作')).toBeNull()
    fireEvent.click(screen.getByRole('button'))
    expect(onClick).toHaveBeenCalledTimes(1)
  })
})
