import type { EntryType, LedgerEntry, LedgerFilters } from './types'

export const entryTypeTone: Record<EntryType, string> = {
  收入: 'positive',
  支出: 'negative',
  转入: 'transfer-in',
  转出: 'transfer-out',
}

export function formatMoney(amount: number): string {
  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: 'CNY',
    minimumFractionDigits: 2,
  }).format(amount)
}

export function filterEntries(
  entries: readonly LedgerEntry[],
  filters: LedgerFilters,
): LedgerEntry[] {
  const query = filters.query.trim().toLocaleLowerCase()
  return entries.filter((entry) => {
    if (filters.startDate && entry.date < filters.startDate) return false
    if (filters.endDate && entry.date > filters.endDate) return false
    if (filters.account && entry.account !== filters.account) return false
    if (filters.type && entry.type !== filters.type) return false
    if (filters.category && !entry.categories.includes(filters.category)) {
      return false
    }
    if (filters.tag && !entry.tags.includes(filters.tag)) return false
    if (query && !entry.description.toLocaleLowerCase().includes(query)) {
      return false
    }
    return true
  })
}

export function todayLocal(): string {
  const now = new Date()
  const offset = now.getTimezoneOffset() * 60_000
  return new Date(now.getTime() - offset).toISOString().slice(0, 10)
}

export function splitTags(value: string): string[] {
  return [...new Set(value.split(',').map((tag) => tag.trim()).filter(Boolean))]
}
