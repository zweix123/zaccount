<script setup lang="ts">
import { computed } from 'vue'

import type { LabeledAmount } from '@/types'
import { formatMoney } from '@/utils'

const props = defineProps<{
  values: readonly LabeledAmount[]
}>()

const width = 720
const height = 250
const padding = { top: 24, right: 20, bottom: 42, left: 20 }
const chartValues = computed(() => props.values.slice(-18))
const maxAmount = computed(() =>
  Math.max(...chartValues.value.map((item) => item.amount), 1),
)
const points = computed(() =>
  chartValues.value.map((item, index) => {
    const count = Math.max(chartValues.value.length - 1, 1)
    const x =
      padding.left +
      (index / count) * (width - padding.left - padding.right)
    const y =
      padding.top +
      (1 - item.amount / maxAmount.value) *
        (height - padding.top - padding.bottom)
    return { ...item, x, y }
  }),
)
const line = computed(() =>
  points.value.map((point) => `${point.x},${point.y}`).join(' '),
)
const area = computed(() => {
  if (!points.value.length) return ''
  const bottom = height - padding.bottom
  return `${padding.left},${bottom} ${line.value} ${
    points.value.at(-1)?.x ?? padding.left
  },${bottom}`
})
</script>

<template>
  <article class="trend-card">
    <header class="card-header">
      <div>
        <p>资金刻度</p>
        <h2>月度支出走势</h2>
      </div>
      <span>最近 {{ chartValues.length }} 个月</span>
    </header>
    <div v-if="chartValues.length" class="chart-wrap">
      <svg
        class="trend"
        :viewBox="`0 0 ${width} ${height}`"
        role="img"
        aria-label="月度支出折线图"
      >
        <defs>
          <linearGradient id="area-fill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#de6255" stop-opacity="0.22" />
            <stop offset="100%" stop-color="#de6255" stop-opacity="0" />
          </linearGradient>
        </defs>
        <line
          v-for="index in 4"
          :key="index"
          class="grid-line"
          :x1="padding.left"
          :x2="width - padding.right"
          :y1="padding.top + ((index - 1) / 3) * (height - padding.top - padding.bottom)"
          :y2="padding.top + ((index - 1) / 3) * (height - padding.top - padding.bottom)"
        />
        <polygon :points="area" fill="url(#area-fill)" />
        <polyline class="trend-line" :points="line" />
        <g v-for="(point, index) in points" :key="point.label">
          <circle class="trend-point" :cx="point.x" :cy="point.y" r="4">
            <title>{{ point.label }}：{{ formatMoney(point.amount) }}</title>
          </circle>
          <text
            v-if="index === 0 || index === points.length - 1 || index % 3 === 0"
            class="axis-label"
            :x="point.x"
            :y="height - 16"
            text-anchor="middle"
          >
            {{ point.label.slice(2) }}
          </text>
        </g>
      </svg>
    </div>
    <p v-else class="empty">当前筛选没有支出数据。</p>
  </article>
</template>

<style scoped>
.trend-card {
  padding: 1.2rem;
  border: 1px solid var(--rule);
  border-radius: 0.9rem;
  background: var(--surface);
}

.card-header {
  display: flex;
  align-items: start;
  justify-content: space-between;
}

.card-header p,
.card-header h2 {
  margin: 0;
}

.card-header p {
  color: var(--expense);
  font-size: 0.68rem;
  letter-spacing: 0.12em;
}

.card-header h2 {
  margin-top: 0.25rem;
  font: 500 1.2rem var(--font-display);
}

.card-header span {
  color: var(--muted);
  font: 0.68rem var(--font-data);
}

.chart-wrap {
  overflow-x: auto;
}

.trend {
  display: block;
  width: 100%;
  min-width: 560px;
  margin-top: 0.6rem;
}

.grid-line {
  stroke: var(--rule);
  stroke-dasharray: 2 6;
}

.trend-line {
  fill: none;
  stroke: var(--expense);
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-width: 3;
}

.trend-point {
  fill: white;
  stroke: var(--expense);
  stroke-width: 3;
}

.axis-label {
  fill: var(--muted);
  font: 11px var(--font-data);
}

.empty {
  display: grid;
  min-height: 14rem;
  place-items: center;
  color: var(--muted);
}
</style>
