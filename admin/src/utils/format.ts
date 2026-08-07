export function centsToYuan(cents: number): string {
  return (cents / 100).toFixed(2)
}

export function formatSpecs(specs: Record<string, string> | null | undefined): string {
  if (!specs) return ''
  return Object.values(specs).join(' · ')
}
