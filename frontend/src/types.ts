export type EntryType = '初始' | '收入' | '支出' | '转入' | '转出'

export interface LedgerEntry {
  rowNumber: number
  date: string
  account: string
  type: EntryType
  amount: number
  categories: readonly string[]
  tags: readonly string[]
  description: string
}

export interface CategoryNode {
  [key: string]: CategoryNode
}
export type CategoryTree = Record<EntryType, CategoryNode>

export interface LedgerMeta {
  accounts: readonly string[]
  tags: readonly string[]
  categoryTree: CategoryTree
  dataFile: string
}

export interface LabeledAmount {
  label: string
  amount: number
}

export interface Analysis {
  count: number
  summary: {
    income: number
    expense: number
    netChange: number
  }
  accounts: readonly LabeledAmount[]
  monthlyExpense: readonly LabeledAmount[]
  categoryExpense: readonly LabeledAmount[]
  tagExpense: readonly LabeledAmount[]
}

export interface Bootstrap {
  entries: LedgerEntry[]
  meta: LedgerMeta
  analysis: Analysis
}

export interface EntryPayload {
  date: string
  account: string
  type: EntryType
  amount: number
  categories: string[]
  tags: string[]
  description: string
}

export interface TransferPayload {
  date: string
  source_account: string
  destination_account: string
  amount: number
  tags: string[]
  description: string
}

export interface LedgerFilters {
  startDate: string
  endDate: string
  account: string
  type: '' | EntryType
  category: string
  tag: string
  query: string
}

export const emptyFilters = (): LedgerFilters => ({
  startDate: '',
  endDate: '',
  account: '',
  type: '',
  category: '',
  tag: '',
  query: '',
})
