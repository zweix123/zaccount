import { computed, readonly, shallowRef } from 'vue'

import {
  createEntry,
  createTransfer,
  loadAnalysis,
  loadBootstrap,
} from '@/api'
import type {
  Analysis,
  EntryPayload,
  LedgerEntry,
  LedgerFilters,
  LedgerMeta,
  TransferPayload,
} from '@/types'

export function useLedger() {
  const entries = shallowRef<LedgerEntry[]>([])
  const meta = shallowRef<LedgerMeta | null>(null)
  const analysis = shallowRef<Analysis | null>(null)
  const loading = shallowRef(true)
  const saving = shallowRef(false)
  const error = shallowRef('')

  const ready = computed(() => meta.value !== null && analysis.value !== null)

  async function refresh(showLoading = true): Promise<void> {
    if (showLoading) loading.value = true
    error.value = ''
    try {
      const result = await loadBootstrap()
      entries.value = result.entries
      meta.value = result.meta
      analysis.value = result.analysis
    } catch (cause) {
      error.value = messageFrom(cause)
    } finally {
      if (showLoading) loading.value = false
    }
  }

  async function refreshAnalysis(filters: LedgerFilters): Promise<void> {
    error.value = ''
    try {
      analysis.value = await loadAnalysis(filters)
    } catch (cause) {
      error.value = messageFrom(cause)
    }
  }

  async function saveEntry(payload: EntryPayload): Promise<boolean> {
    return save(async () => createEntry(payload))
  }

  async function saveTransfer(payload: TransferPayload): Promise<boolean> {
    return save(async () => createTransfer(payload))
  }

  async function save(action: () => Promise<unknown>): Promise<boolean> {
    saving.value = true
    error.value = ''
    try {
      await action()
      await refresh(false)
      return true
    } catch (cause) {
      error.value = messageFrom(cause)
      return false
    } finally {
      saving.value = false
    }
  }

  function clearError(): void {
    error.value = ''
  }

  return {
    entries: readonly(entries),
    meta: readonly(meta),
    analysis: readonly(analysis),
    loading: readonly(loading),
    saving: readonly(saving),
    error: readonly(error),
    ready,
    refresh,
    refreshAnalysis,
    saveEntry,
    saveTransfer,
    clearError,
  }
}

function messageFrom(cause: unknown): string {
  return cause instanceof Error ? cause.message : '发生未知错误'
}
