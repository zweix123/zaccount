<script setup lang="ts">
import type { Analysis, LedgerFilters, LedgerMeta } from '@/types'

import LedgerFiltersComponent from '../ledger/LedgerFilters.vue'
import MonthlyTrend from './MonthlyTrend.vue'
import RankedBars from './RankedBars.vue'
import SummaryRail from './SummaryRail.vue'

defineProps<{
  analysis: Analysis
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
        <p class="eyebrow">资金全景</p>
        <h1>看见钱的去向</h1>
      </div>
      <p>所有图表使用同一组筛选条件。</p>
    </header>

    <LedgerFiltersComponent
      :filters="filters"
      :meta="meta"
      @apply="emit('applyFilters', $event)"
    />
    <SummaryRail :analysis="analysis" />
    <MonthlyTrend :values="analysis.monthlyExpense" />
    <div class="analysis-grid">
      <RankedBars
        title="一级类别"
        eyebrow="支出结构"
        :values="analysis.categoryExpense"
        tone="coral"
      />
      <RankedBars
        title="标签排行"
        eyebrow="灵活标记"
        :values="analysis.tagExpense"
      />
      <RankedBars
        class="account-bars"
        title="账户资金变化"
        eyebrow="资金所在"
        :values="analysis.accounts"
        tone="teal"
        :limit="20"
      />
    </div>
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
  gap: 2rem;
}

.workspace-header h1 {
  margin: 0.2rem 0 0;
  font: 500 clamp(2rem, 4vw, 3.2rem) / 1.15 var(--font-display);
}

.workspace-header > p {
  max-width: 20rem;
  margin: 0;
  color: var(--muted);
  font-size: 0.78rem;
  text-align: right;
}

.eyebrow {
  margin: 0;
  color: var(--blue);
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.analysis-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}

.account-bars {
  grid-column: 1 / -1;
}

@media (max-width: 760px) {
  .workspace-header {
    align-items: start;
    flex-direction: column;
    gap: 0.6rem;
  }

  .workspace-header > p {
    text-align: left;
  }

  .analysis-grid {
    grid-template-columns: 1fr;
  }

  .account-bars {
    grid-column: auto;
  }
}
</style>
