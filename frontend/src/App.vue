<script setup lang="ts">
import { computed, onMounted, reactive, shallowRef, useTemplateRef } from 'vue'

import AnalysisWorkspace from '@/components/analysis/AnalysisWorkspace.vue'
import EntryWorkspace from '@/components/entry/EntryWorkspace.vue'
import LedgerWorkspace from '@/components/ledger/LedgerWorkspace.vue'
import AppNavigation, {
  type ViewName,
} from '@/components/shell/AppNavigation.vue'
import { useLedger } from '@/composables/useLedger'
import type { EntryPayload, LedgerFilters, TransferPayload } from '@/types'
import { emptyFilters } from '@/types'
import { filterEntries } from '@/utils'

const {
  entries,
  meta,
  analysis,
  loading,
  saving,
  error,
  ready,
  refresh,
  refreshAnalysis,
  saveEntry,
  saveTransfer,
  clearError,
} = useLedger()

const activeView = shallowRef<ViewName>('entry')
const filters = reactive<LedgerFilters>(emptyFilters())
const notice = shallowRef('')
const entryWorkspace =
  useTemplateRef<InstanceType<typeof EntryWorkspace>>('entryWorkspace')
const visibleEntries = computed(() => filterEntries(entries.value, filters))

onMounted(refresh)

async function handleEntry(payload: EntryPayload): Promise<void> {
  if (await saveEntry(payload)) {
    await refreshAnalysis(filters)
    entryWorkspace.value?.resetActiveForm()
    showNotice('账目已保存，账本与分析已经更新。')
  }
}

async function handleTransfer(payload: TransferPayload): Promise<void> {
  if (await saveTransfer(payload)) {
    await refreshAnalysis(filters)
    entryWorkspace.value?.resetActiveForm()
    showNotice('转账已成对保存，两个账户已经同步更新。')
  }
}

async function applyFilters(next: LedgerFilters): Promise<void> {
  Object.assign(filters, next)
  await refreshAnalysis(filters)
}

function showNotice(message: string): void {
  notice.value = message
  window.setTimeout(() => {
    if (notice.value === message) notice.value = ''
  }, 3600)
}
</script>

<template>
  <div class="app-shell">
    <aside class="sidebar">
      <header class="brand">
        <span class="brand-mark" aria-hidden="true">Z</span>
        <div>
          <strong>Zaccount</strong>
          <small>私人账本</small>
        </div>
      </header>
      <AppNavigation
        :active-view="activeView"
        @navigate="activeView = $event"
      />
      <footer v-if="meta" class="data-location" :title="meta.dataFile">
        <span class="status-dot"></span>
        <span>本地数据</span>
        <small>{{ meta.dataFile }}</small>
      </footer>
    </aside>

    <main class="content">
      <div v-if="loading" class="loading-state">
        <span class="loading-rule"></span>
        <p>正在校验账本…</p>
      </div>

      <div v-else-if="error && !ready" class="fatal-state" role="alert">
        <span>!</span>
        <h1>账本没有打开</h1>
        <p>{{ error }}</p>
        <button type="button" @click="refresh()">重新尝试</button>
      </div>

      <template v-else-if="meta && analysis">
        <EntryWorkspace
          v-if="activeView === 'entry'"
          ref="entryWorkspace"
          :meta="meta"
          :saving="saving"
          @save-entry="handleEntry"
          @save-transfer="handleTransfer"
        />
        <LedgerWorkspace
          v-else-if="activeView === 'ledger'"
          :entries="visibleEntries"
          :filters="filters"
          :meta="meta"
          @apply-filters="applyFilters"
        />
        <AnalysisWorkspace
          v-else
          :analysis="analysis"
          :filters="filters"
          :meta="meta"
          @apply-filters="applyFilters"
        />
      </template>
    </main>

    <div v-if="error && ready" class="toast error-toast" role="alert">
      <span>{{ error }}</span>
      <button type="button" aria-label="关闭错误" @click="clearError">×</button>
    </div>
    <div v-if="notice" class="toast success-toast" role="status">
      <span>{{ notice }}</span>
    </div>
  </div>
</template>

<style scoped>
.app-shell {
  min-height: 100vh;
}

.sidebar {
  position: fixed;
  inset: 0 auto 0 0;
  z-index: 5;
  display: flex;
  flex-direction: column;
  width: 220px;
  padding: 1.4rem 1rem;
  border-right: 1px solid var(--rule);
  background: rgb(244 246 250 / 92%);
  backdrop-filter: blur(18px);
}

.brand {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  margin: 0.2rem 0 2rem;
  padding: 0 0.6rem;
}

.brand-mark {
  display: grid;
  width: 2rem;
  height: 2rem;
  place-items: center;
  border-radius: 0.55rem 0.55rem 0.55rem 0;
  background: var(--blue);
  color: white;
  font: 600 1rem var(--font-display);
}

.brand div {
  display: grid;
}

.brand strong {
  font: 600 0.95rem var(--font-data);
  letter-spacing: -0.04em;
}

.brand small {
  color: var(--muted);
  font-size: 0.64rem;
}

.data-location {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 0.1rem 0.45rem;
  margin-top: auto;
  padding: 0.7rem;
  color: var(--muted);
  font-size: 0.72rem;
}

.data-location small {
  grid-column: 2;
  overflow: hidden;
  font-size: 0.58rem;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.status-dot {
  width: 0.48rem;
  height: 0.48rem;
  margin-top: 0.25rem;
  border-radius: 50%;
  background: var(--income);
  box-shadow: 0 0 0 3px rgb(35 134 116 / 12%);
}

.content {
  min-height: 100vh;
  margin-left: 220px;
  padding: clamp(1.25rem, 4vw, 3.5rem);
}

.loading-state,
.fatal-state {
  display: grid;
  min-height: 70vh;
  place-items: center;
  align-content: center;
  color: var(--muted);
}

.loading-rule {
  width: 8rem;
  height: 2px;
  overflow: hidden;
  background: var(--rule);
}

.loading-rule::after {
  display: block;
  width: 45%;
  height: 100%;
  background: var(--blue);
  animation: loading 1s ease-in-out infinite alternate;
  content: '';
}

.fatal-state span {
  display: grid;
  width: 2.4rem;
  height: 2.4rem;
  place-items: center;
  border-radius: 50%;
  background: var(--expense);
  color: white;
}

.fatal-state h1 {
  margin: 1rem 0 0.2rem;
  color: var(--ink);
  font: 500 2rem var(--font-display);
}

.fatal-state p {
  max-width: 35rem;
  text-align: center;
}

.fatal-state button {
  padding: 0.6rem 0.9rem;
  border: 0;
  border-radius: 0.5rem;
  background: var(--ink);
  color: white;
  cursor: pointer;
}

.toast {
  position: fixed;
  right: 1.25rem;
  bottom: 1.25rem;
  z-index: 10;
  display: flex;
  align-items: center;
  gap: 1rem;
  max-width: min(28rem, calc(100vw - 2.5rem));
  padding: 0.8rem 1rem;
  border-radius: 0.65rem;
  color: white;
  box-shadow: 0 14px 50px rgb(23 35 59 / 20%);
  font-size: 0.8rem;
}

.error-toast {
  background: var(--expense);
}

.success-toast {
  background: var(--income);
}

.toast button {
  border: 0;
  background: transparent;
  color: white;
  font-size: 1.1rem;
  cursor: pointer;
}

@keyframes loading {
  to {
    transform: translateX(125%);
  }
}

@media (max-width: 760px) {
  .sidebar {
    inset: auto 0 0;
    width: auto;
    padding: 0.5rem;
    border-top: 1px solid var(--rule);
    border-right: 0;
  }

  .brand,
  .data-location {
    display: none;
  }

  .content {
    margin-left: 0;
    padding-bottom: 5.5rem;
  }

  .toast {
    bottom: 5rem;
  }
}

@media (prefers-reduced-motion: reduce) {
  .loading-rule::after {
    animation: none;
  }
}
</style>
