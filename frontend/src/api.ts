import type {
  Analysis,
  Bootstrap,
  EntryPayload,
  LedgerFilters,
  TransferPayload,
} from './types'

async function request<T>(url: string, init?: RequestInit): Promise<T> {
  const response = await fetch(url, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...init?.headers,
    },
  })
  if (!response.ok) {
    const body = (await response.json().catch(() => ({}))) as { detail?: string }
    throw new Error(body.detail ?? `请求失败（${response.status}）`)
  }
  return response.json() as Promise<T>
}

export function loadBootstrap(): Promise<Bootstrap> {
  return request('/api/bootstrap')
}

export function loadAnalysis(filters: LedgerFilters): Promise<Analysis> {
  const params = new URLSearchParams()
  const fields: [string, string][] = [
    ['start_date', filters.startDate],
    ['end_date', filters.endDate],
    ['account', filters.account],
    ['type', filters.type],
    ['category', filters.category],
    ['tag', filters.tag],
    ['query', filters.query],
  ]
  fields.forEach(([key, value]) => value && params.set(key, value))
  return request(`/api/analysis?${params.toString()}`)
}

export function createEntry(payload: EntryPayload): Promise<unknown> {
  return request('/api/entries', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function createTransfer(payload: TransferPayload): Promise<unknown> {
  return request('/api/transfers', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}
