<script setup lang="ts">
import type { LedgerEntry, LedgerFilters, LedgerMeta } from '@/types'

import EntryTable from './EntryTable.vue'
import LedgerFiltersComponent from './LedgerFilters.vue'

defineProps<{
  entries: readonly LedgerEntry[]
  filters: LedgerFilters
  meta: LedgerMeta
}>()

const emit = defineEmits<{
  applyFilters: [filters: LedgerFilters]
}>()
</script>

<template>
  <section class="workspace">
    <header class="workspace-header">
      <div>
        <p class="eyebrow">完整账本</p>
        <h1>账目与凭据</h1>
      </div>
      <p class="entry-count">{{ entries.length }} 条账目</p>
    </header>
    <LedgerFiltersComponent
      :filters="filters"
      :meta="meta"
      @apply="emit('applyFilters', $event)"
    />
    <EntryTable :entries="entries" />
  </section>
</template>

<style scoped>
.workspace {
  display: grid;
  gap: 1rem;
}

.workspace-header {
  display: flex;
  align-items: end;
  justify-content: space-between;
}

.workspace-header h1 {
  margin: 0.2rem 0 0;
  font: 500 clamp(2rem, 4vw, 3.2rem) / 1.15 var(--font-display);
}

.eyebrow {
  margin: 0;
  color: var(--blue);
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.entry-count {
  margin: 0;
  color: var(--muted);
  font: 0.75rem var(--font-data);
}
</style>
