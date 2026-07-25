<script setup lang="ts">
import type { Analysis } from '@/types'
import { formatMoney } from '@/utils'

defineProps<{
  analysis: Analysis
}>()
</script>

<template>
  <div class="summary-rail">
    <article class="summary-item income">
      <span>收入</span>
      <strong>{{ formatMoney(analysis.summary.income) }}</strong>
    </article>
    <article class="summary-item expense">
      <span>支出</span>
      <strong>{{ formatMoney(analysis.summary.expense) }}</strong>
    </article>
    <article class="summary-item net">
      <span>净变化</span>
      <strong>{{ formatMoney(analysis.summary.netChange) }}</strong>
    </article>
    <article class="summary-item count">
      <span>账目</span>
      <strong>{{ analysis.count }}</strong>
    </article>
  </div>
</template>

<style scoped>
.summary-rail {
  position: relative;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1px;
  overflow: hidden;
  border: 1px solid var(--rule);
  border-radius: 0.9rem;
  background: var(--rule);
}

.summary-rail::after {
  position: absolute;
  right: 0;
  bottom: 0;
  left: 0;
  height: 3px;
  background: linear-gradient(
    90deg,
    var(--income) 0 35%,
    var(--expense) 35% 70%,
    var(--blue) 70%
  );
  content: '';
}

.summary-item {
  display: grid;
  gap: 0.55rem;
  min-width: 0;
  padding: 1.1rem;
  background: var(--surface);
}

.summary-item span {
  color: var(--muted);
  font-size: 0.72rem;
}

.summary-item strong {
  overflow: hidden;
  color: var(--ink);
  font: 500 clamp(1rem, 2vw, 1.45rem) var(--font-data);
  letter-spacing: -0.04em;
  text-overflow: ellipsis;
}

.summary-item.income strong {
  color: var(--income);
}

.summary-item.expense strong {
  color: var(--expense);
}

@media (max-width: 700px) {
  .summary-rail {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
