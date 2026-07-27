<script setup lang="ts">
import { computed, shallowRef } from 'vue'

import type { LedgerEntry } from '@/types'
import { entryTypeTone, formatMoney } from '@/utils'

const props = defineProps<{
  entries: readonly LedgerEntry[]
}>()

const pageSize = 50
const visibleCount = shallowRef(pageSize)
const visibleEntries = computed(() => props.entries.slice(0, visibleCount.value))
const hasMore = computed(() => props.entries.length > visibleCount.value)
</script>

<template>
  <div class="table-shell">
    <div v-if="!entries.length" class="empty-state">
      <span class="empty-mark">○</span>
      <p>没有符合条件的账目，调整筛选后再看。</p>
    </div>

    <div v-else class="entry-list">
      <article
        v-for="entry in visibleEntries"
        :key="entry.rowNumber"
        class="entry-row"
      >
        <time class="entry-date" :datetime="entry.date">
          <strong>{{ entry.date.slice(8) }}</strong>
          <span>{{ entry.date.slice(0, 7) }}</span>
        </time>
        <div class="entry-main">
          <div class="entry-heading">
            <span
              class="type-dot"
              :class="entryTypeTone[entry.type]"
              aria-hidden="true"
            ></span>
            <strong>{{ entry.description || entry.categories.join(' / ') }}</strong>
          </div>
          <div class="entry-meta">
            <span>{{ entry.account }}</span>
            <span>{{ entry.type }}</span>
            <span>{{ entry.categories.join(' / ') }}</span>
            <span v-for="tag in entry.tags" :key="tag" class="tag">
              #{{ tag }}
            </span>
          </div>
        </div>
        <data
          class="entry-amount"
          :class="entryTypeTone[entry.type]"
          :value="entry.amount"
        >
          {{ entry.type === '支出' || entry.type === '转出' ? '−' : '+' }}
          {{ formatMoney(entry.amount) }}
        </data>
      </article>
    </div>

    <button
      v-if="hasMore"
      class="more-button"
      type="button"
      @click="visibleCount += pageSize"
    >
      再显示 {{ Math.min(pageSize, entries.length - visibleCount) }} 条
    </button>
  </div>
</template>

<style scoped>
.table-shell {
  overflow: hidden;
  border: 1px solid var(--rule);
  border-radius: 0.9rem;
  background: var(--surface);
}

.entry-row {
  display: grid;
  grid-template-columns: 4.2rem minmax(0, 1fr) auto;
  align-items: center;
  gap: 1rem;
  padding: 0.9rem 1.1rem;
  border-bottom: 1px solid var(--rule);
}

.entry-row:last-child {
  border-bottom: 0;
}

.entry-date {
  display: grid;
  font-family: var(--font-data);
}

.entry-date strong {
  font-size: 1.2rem;
}

.entry-date span {
  color: var(--muted);
  font-size: 0.65rem;
}

.entry-main {
  min-width: 0;
}

.entry-heading {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.entry-heading strong {
  overflow: hidden;
  font-size: 0.9rem;
  font-weight: 550;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.type-dot {
  flex: none;
  width: 0.48rem;
  height: 0.48rem;
  border-radius: 50%;
  background: var(--blue);
}

.type-dot.positive,
.type-dot.initial,
.type-dot.transfer-in {
  background: var(--income);
}

.type-dot.negative,
.type-dot.transfer-out {
  background: var(--expense);
}

.entry-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem 0.65rem;
  margin-top: 0.25rem;
  color: var(--muted);
  font-size: 0.7rem;
}

.tag {
  color: var(--blue);
}

.entry-amount {
  font: 500 0.9rem var(--font-data);
  white-space: nowrap;
}

.entry-amount.positive,
.entry-amount.initial,
.entry-amount.transfer-in {
  color: var(--income);
}

.entry-amount.negative,
.entry-amount.transfer-out {
  color: var(--expense);
}

.more-button {
  width: 100%;
  padding: 0.85rem;
  border: 0;
  border-top: 1px solid var(--rule);
  background: var(--paper);
  color: var(--blue);
  font: 0.8rem var(--font-body);
  cursor: pointer;
}

.empty-state {
  display: grid;
  place-items: center;
  min-height: 14rem;
  color: var(--muted);
}

.empty-state p {
  margin: 0;
}

.empty-mark {
  font-size: 2rem;
}

@media (max-width: 600px) {
  .entry-row {
    grid-template-columns: 3.2rem minmax(0, 1fr);
  }

  .entry-amount {
    grid-column: 2;
  }
}
</style>
