<script setup lang="ts">
import { computed } from 'vue'

import type { LabeledAmount } from '@/types'
import { formatMoney } from '@/utils'

const props = withDefaults(
  defineProps<{
    title: string
    eyebrow: string
    values: readonly LabeledAmount[]
    tone?: 'blue' | 'coral' | 'teal'
    limit?: number
  }>(),
  {
    tone: 'blue',
    limit: 8,
  },
)

const visible = computed(() => props.values.slice(0, props.limit))
const maximum = computed(() => Math.max(...visible.value.map((item) => item.amount), 1))
</script>

<template>
  <article class="bars-card">
    <header class="card-header">
      <p>{{ eyebrow }}</p>
      <h2>{{ title }}</h2>
    </header>
    <div v-if="visible.length" class="bars">
      <div v-for="item in visible" :key="item.label" class="bar-row">
        <div class="bar-label">
          <span>{{ item.label }}</span>
          <strong>{{ formatMoney(item.amount) }}</strong>
        </div>
        <div class="bar-track">
          <span
            class="bar-fill"
            :class="tone"
            :style="{ width: `${(item.amount / maximum) * 100}%` }"
          ></span>
        </div>
      </div>
    </div>
    <p v-else class="empty">当前筛选没有可展示的数据。</p>
  </article>
</template>

<style scoped>
.bars-card {
  padding: 1.2rem;
  border: 1px solid var(--rule);
  border-radius: 0.9rem;
  background: var(--surface);
}

.card-header p,
.card-header h2 {
  margin: 0;
}

.card-header p {
  color: var(--blue);
  font-size: 0.68rem;
  letter-spacing: 0.12em;
}

.card-header h2 {
  margin-top: 0.25rem;
  font: 500 1.2rem var(--font-display);
}

.bars {
  display: grid;
  gap: 0.9rem;
  margin-top: 1.2rem;
}

.bar-label {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  font-size: 0.78rem;
}

.bar-label strong {
  font: 500 0.72rem var(--font-data);
}

.bar-track {
  height: 0.38rem;
  margin-top: 0.35rem;
  overflow: hidden;
  border-radius: 999px;
  background: var(--paper);
}

.bar-fill {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: var(--blue);
  transform-origin: left;
  animation: grow 500ms ease both;
}

.bar-fill.coral {
  background: var(--expense);
}

.bar-fill.teal {
  background: var(--income);
}

.empty {
  display: grid;
  min-height: 10rem;
  place-items: center;
  color: var(--muted);
}

@keyframes grow {
  from {
    transform: scaleX(0);
  }
}

@media (prefers-reduced-motion: reduce) {
  .bar-fill {
    animation: none;
  }
}
</style>
