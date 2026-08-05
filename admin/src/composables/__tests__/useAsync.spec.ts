import { describe, expect, it } from 'vitest'
import { useAsync } from '../useAsync'

describe('useAsync', () => {
  it('sets loading during run and returns result', async () => {
    const { loading, run } = useAsync(async () => 42)
    const promise = run()
    expect(loading.value).toBe(true)
    await expect(promise).resolves.toBe(42)
    expect(loading.value).toBe(false)
  })

  it('records error message on failure', async () => {
    const { error, run } = useAsync(async () => {
      throw new Error('boom')
    })
    await run()
    expect(error.value).toBeTruthy()
  })
})
