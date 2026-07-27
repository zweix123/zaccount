<script setup lang="ts">
import { computed, reactive, useTemplateRef } from 'vue'

import type {
  CategoryNode,
  EntryPayload,
  EntryType,
  LedgerMeta,
} from '@/types'
import { splitTags, todayLocal } from '@/utils'

const props = defineProps<{
  meta: LedgerMeta
  saving: boolean
}>()

const emit = defineEmits<{
  save: [payload: EntryPayload]
}>()

const amountInput = useTemplateRef<HTMLInputElement>('amountInput')
const draft = reactive({
  date: todayLocal(),
  account: props.meta.accounts[0] ?? '',
  type: '支出' as EntryType,
  amount: '',
  category0: '',
  category1: '',
  tags: '',
  description: '',
})

const types: EntryType[] = ['支出', '收入', '初始', '转出', '转入']
const rootCategories = computed(() =>
  Object.keys(props.meta.categoryTree[draft.type] ?? {}),
)
const childCategories = computed(() => {
  const root = props.meta.categoryTree[draft.type]?.[draft.category0]
  return root ? Object.keys(root as CategoryNode) : []
})
const canSave = computed(
  () =>
    Number(draft.amount) > 0 &&
    Boolean(draft.account.trim()) &&
    (draft.type === '初始' || Boolean(draft.category0)),
)

function selectType(type: EntryType): void {
  draft.type = type
  draft.category0 = ''
  draft.category1 = ''
}

function handleRootCategory(): void {
  draft.category1 = ''
}

function submit(): void {
  if (!canSave.value) return
  const categories =
    draft.type === '初始'
      ? []
      : [draft.category0, draft.category1].filter(Boolean)
  emit('save', {
    date: draft.date,
    account: draft.account,
    type: draft.type,
    amount: Number(draft.amount),
    categories,
    tags: splitTags(draft.tags),
    description: draft.description.trim(),
  })
}

function resetAfterSave(): void {
  draft.amount = ''
  draft.description = ''
  amountInput.value?.focus()
}

defineExpose({ resetAfterSave })
</script>

<template>
  <form class="entry-form" @submit.prevent="submit">
    <div class="type-switch" aria-label="账目类型">
      <button
        v-for="type in types"
        :key="type"
        class="type-button"
        :class="[`type-${type}`, { active: draft.type === type }]"
        type="button"
        @click="selectType(type)"
      >
        {{ type }}
      </button>
    </div>

    <label class="amount-field">
      <span class="field-label">金额</span>
      <span class="amount-shell">
        <span class="currency">¥</span>
        <input
          ref="amountInput"
          v-model="draft.amount"
          class="amount-input"
          data-testid="amount-input"
          inputmode="decimal"
          min="0.01"
          step="0.01"
          type="number"
          placeholder="0.00"
          autofocus
          required
        />
      </span>
    </label>

    <div class="form-grid">
      <label class="field">
        <span class="field-label">日期</span>
        <input v-model="draft.date" type="date" required />
      </label>

      <label class="field">
        <span class="field-label">账户</span>
        <input
          v-model="draft.account"
          data-testid="account-input"
          list="account-options"
          placeholder="选择或输入账户"
          required
        />
        <datalist id="account-options">
          <option v-for="account in meta.accounts" :key="account" :value="account" />
        </datalist>
      </label>

      <label v-if="draft.type !== '初始'" class="field">
        <span class="field-label">一级类别</span>
        <select
          v-model="draft.category0"
          data-testid="category-root"
          required
          @change="handleRootCategory"
        >
          <option value="" disabled>选择类别</option>
          <option
            v-for="category in rootCategories"
            :key="category"
            :value="category"
          >
            {{ category }}
          </option>
        </select>
      </label>

      <label v-if="childCategories.length" class="field">
        <span class="field-label">细分类别</span>
        <select v-model="draft.category1">
          <option value="">仅使用一级类别</option>
          <option
            v-for="category in childCategories"
            :key="category"
            :value="category"
          >
            {{ category }}
          </option>
        </select>
      </label>

      <label class="field">
        <span class="field-label">标签</span>
        <input
          v-model="draft.tags"
          list="tag-options"
          placeholder="旅行, 聚餐"
        />
        <datalist id="tag-options">
          <option v-for="tag in meta.tags" :key="tag" :value="tag" />
        </datalist>
      </label>

      <label class="field field-wide">
        <span class="field-label">描述</span>
        <input v-model="draft.description" placeholder="这笔钱发生了什么？" />
      </label>
    </div>

    <button
      class="primary-action"
      data-testid="save-entry"
      type="submit"
      :disabled="!canSave || saving"
    >
      <span>{{ saving ? '正在保存' : '保存账目' }}</span>
      <span aria-hidden="true">→</span>
    </button>
  </form>
</template>

<style scoped>
.entry-form {
  display: grid;
  gap: 1.5rem;
}

.type-switch {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 0.35rem;
  padding: 0.3rem;
  border: 1px solid var(--rule);
  border-radius: 0.8rem;
  background: var(--paper);
}

.type-button {
  padding: 0.65rem;
  border: 0;
  border-radius: 0.55rem;
  background: transparent;
  color: var(--muted);
  font: inherit;
  cursor: pointer;
}

.type-button.active {
  color: white;
  box-shadow: 0 6px 16px rgb(23 35 59 / 16%);
}

.type-支出.active {
  background: var(--expense);
}

.type-收入.active {
  background: var(--income);
}

.type-初始.active {
  background: var(--blue);
}

.type-转出.active,
.type-转入.active {
  background: var(--blue);
}

.amount-field {
  display: grid;
  gap: 0.3rem;
  padding: 1rem 0 0.8rem;
  border-bottom: 1px solid var(--ink);
}

.amount-shell {
  display: flex;
  align-items: baseline;
  gap: 0.55rem;
}

.currency {
  color: var(--muted);
  font: 1.3rem var(--font-data);
}

.amount-input {
  min-width: 0;
  width: 100%;
  padding: 0;
  border: 0;
  outline: 0;
  background: transparent;
  color: var(--ink);
  font: 500 clamp(2.7rem, 7vw, 5.2rem) / 1 var(--font-data);
  letter-spacing: -0.06em;
}

.amount-input::placeholder {
  color: #c7cedb;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}

.field,
.field-label {
  display: grid;
}

.field {
  gap: 0.4rem;
}

.field-wide {
  grid-column: 1 / -1;
}

.field-label {
  color: var(--muted);
  font-size: 0.74rem;
  letter-spacing: 0.08em;
}

.field input,
.field select {
  width: 100%;
  padding: 0.72rem 0;
  border: 0;
  border-bottom: 1px solid var(--rule);
  border-radius: 0;
  outline: 0;
  background: transparent;
  color: var(--ink);
  font: inherit;
}

.field input:focus,
.field select:focus {
  border-color: var(--blue);
}

.primary-action {
  display: flex;
  justify-content: space-between;
  padding: 0.95rem 1.1rem;
  border: 0;
  border-radius: 0.75rem;
  background: var(--ink);
  color: white;
  font: 600 0.95rem var(--font-body);
  cursor: pointer;
}

.primary-action:disabled {
  cursor: not-allowed;
  opacity: 0.42;
}

@media (max-width: 560px) {
  .form-grid {
    grid-template-columns: 1fr;
  }

  .field-wide {
    grid-column: auto;
  }
}
</style>
