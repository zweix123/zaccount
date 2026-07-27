<script setup lang="ts">
import { reactive, watch } from 'vue'

import type { LedgerFilters, LedgerMeta } from '@/types'
import { emptyFilters } from '@/types'

const props = defineProps<{
  filters: LedgerFilters
  meta: LedgerMeta
}>()

const emit = defineEmits<{
  apply: [filters: LedgerFilters]
}>()

const draft = reactive<LedgerFilters>({ ...props.filters })

watch(
  () => props.filters,
  (value) => Object.assign(draft, value),
)

const firstLevelCategories = Object.values(props.meta.categoryTree).flatMap(
  (node) => Object.keys(node),
)
const categories = [...new Set(firstLevelCategories)].sort()

function apply(): void {
  emit('apply', { ...draft })
}

function clear(): void {
  Object.assign(draft, emptyFilters())
  apply()
}
</script>

<template>
  <form class="filters" aria-label="账目筛选" @submit.prevent="apply">
    <label class="search-field">
      <span class="visually-hidden">搜索描述</span>
      <span aria-hidden="true">⌕</span>
      <input v-model="draft.query" placeholder="搜索描述" />
    </label>

    <div class="filter-row">
      <label>
        <span>开始</span>
        <input v-model="draft.startDate" type="date" />
      </label>
      <label>
        <span>结束</span>
        <input v-model="draft.endDate" type="date" />
      </label>
      <label>
        <span>账户</span>
        <select v-model="draft.account">
          <option value="">全部账户</option>
          <option
            v-for="account in meta.accounts"
            :key="account"
            :value="account"
          >
            {{ account }}
          </option>
        </select>
      </label>
      <label>
        <span>类型</span>
        <select v-model="draft.type">
          <option value="">全部类型</option>
          <option value="初始">初始</option>
          <option value="收入">收入</option>
          <option value="支出">支出</option>
          <option value="转入">转入</option>
          <option value="转出">转出</option>
        </select>
      </label>
      <label>
        <span>类别</span>
        <select v-model="draft.category">
          <option value="">全部类别</option>
          <option
            v-for="category in categories"
            :key="category"
            :value="category"
          >
            {{ category }}
          </option>
        </select>
      </label>
      <label>
        <span>标签</span>
        <select v-model="draft.tag">
          <option value="">全部标签</option>
          <option v-for="tag in meta.tags" :key="tag" :value="tag">
            {{ tag }}
          </option>
        </select>
      </label>
    </div>

    <div class="filter-actions">
      <button class="clear-button" type="button" @click="clear">清除</button>
      <button class="apply-button" type="submit">应用筛选</button>
    </div>
  </form>
</template>

<style scoped>
.filters {
  display: grid;
  gap: 1rem;
  padding: 1.1rem;
  border: 1px solid var(--rule);
  border-radius: 0.9rem;
  background: var(--surface);
}

.search-field {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.6rem 0.75rem;
  border: 1px solid var(--rule);
  border-radius: 0.6rem;
}

.search-field input {
  width: 100%;
  border: 0;
  outline: 0;
  background: transparent;
  color: var(--ink);
  font: inherit;
}

.filter-row {
  display: grid;
  grid-template-columns: repeat(6, minmax(110px, 1fr));
  gap: 0.65rem;
}

.filter-row label {
  display: grid;
  gap: 0.3rem;
}

.filter-row span {
  color: var(--muted);
  font-size: 0.68rem;
}

.filter-row input,
.filter-row select {
  min-width: 0;
  padding: 0.55rem;
  border: 1px solid var(--rule);
  border-radius: 0.5rem;
  background: white;
  color: var(--ink);
  font: 0.78rem var(--font-body);
}

.filter-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.6rem;
}

.filter-actions button {
  padding: 0.55rem 0.9rem;
  border-radius: 0.5rem;
  font: 0.78rem var(--font-body);
  cursor: pointer;
}

.clear-button {
  border: 1px solid var(--rule);
  background: white;
  color: var(--muted);
}

.apply-button {
  border: 1px solid var(--ink);
  background: var(--ink);
  color: white;
}

@media (max-width: 1100px) {
  .filter-row {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 580px) {
  .filter-row {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
