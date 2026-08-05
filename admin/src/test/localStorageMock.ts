export function installLocalStorageMock(): void {
  class LocalStorageMock {
    private store: Record<string, string> = {}

    getItem(key: string): string | null {
      return key in this.store ? this.store[key] : null
    }

    setItem(key: string, value: string): void {
      this.store[key] = String(value)
    }

    removeItem(key: string): void {
      delete this.store[key]
    }

    clear(): void {
      this.store = {}
    }
  }

  globalThis.localStorage = new LocalStorageMock() as unknown as Storage
}
