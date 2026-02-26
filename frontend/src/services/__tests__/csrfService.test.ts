import { describe, it, expect, beforeEach, vi } from 'vitest'
import { csrfService } from '../csrfService'

describe('CSRFService', () => {
  beforeEach(() => {
    csrfService.clearToken()
  })

  it('should fetch token on first call', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      headers: {
        get: vi.fn().mockReturnValue('test-token')
      }
    })

    global.fetch = mockFetch

    const token = await csrfService.getToken()

    expect(token).toBe('test-token')
    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('/health'),
      expect.objectContaining({ credentials: 'include' })
    )
  })

  it('should reuse token on subsequent calls', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      headers: {
        get: vi.fn().mockReturnValue('test-token')
      }
    })

    global.fetch = mockFetch

    await csrfService.getToken()
    await csrfService.getToken()

    expect(mockFetch).toHaveBeenCalledTimes(1)
  })

  it('should handle CSRF errors', async () => {
    const mockFetch = vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        headers: { get: vi.fn().mockReturnValue('test-token') }
      })
      .mockResolvedValueOnce({
        ok: true,
        headers: { get: vi.fn().mockReturnValue('new-token') }
      })

    global.fetch = mockFetch

    await csrfService.getToken()
    await csrfService.handleCSRFError()

    expect(mockFetch).toHaveBeenCalledTimes(2)
  })
})
