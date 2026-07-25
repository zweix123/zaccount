<script setup lang="ts">
import { computed, reactive, useTemplateRef } from 'vue'

import type { LedgerMeta, TransferPayload } from '@/types'
import { splitTags, todayLocal } from '@/utils'

const props = defineProps<{
  meta: LedgerMeta
  saving: boolean
}>()

const emit = defineEmits<{
  save: [payload: TransferPayload]
}>()

const amountInput = useTemplateRef<HTMLInputElement>('transferAmount')
const draft = reactive({
  date: todayLocal(),
  source: props.meta.accounts[0] ?? '',
  destination: props.meta.accounts[1] ?? '',
  amount: '',
  tags: '',
  description: '',
})

const canSave = computed(
  () =>
    Number(draft.amount) > 0 &&
    Boolean(draft.source) &&
    Boolean(draft.destination) &&
    draft.source !== draft.destination,
)

function submit(): void {
  if (!canSave.value) return
  emit('save', {
    date: draft.date,
    source_account: draft.source,
    destination_account: draft.destination,
    amount: Number(draft.amount),
    tags: splitTags(draft.tags),
    description: draft.description.trim(),
  })
}

function swapAccounts(): void {
  ;[draft.source, draft.destination] = [draft.destination, draft.source]
}

function resetAfterSave(): void {
  draft.amount = ''
  draft.description = ''
  amountInput.value?.focus()
}

defineExpose({ resetAfterSave })
</script>

<template>
  <form class="transfer-form" @submit.prevent="submit">
    <div class="route">
      <label class="account-stop">
        <span class="field-label">从账户</span>
        <select v-model="draft.source" required>
          <option
            v-for="account in meta.accounts"
            :key="account"
            :value="account"
          >
            {{ account }}
          </option>
        </select>
      </label>
      <button
        class="swap"
        type="button"
        aria-label="交换转出和转入账户"
        @click="swapAccounts"
      >
        ⇄
      </button>
      <label class="account-stop">
        <span class="field-label">到账户</span>
        <select v-model="draft.destination" required>
          <option
            v-for="account in meta.accounts"
            :key="account"
            :value="account"
          >
            {{ account }}
          </option>
        </select>
      </label>
    </div>

    <p v-if="draft.source === draft.destination" class="inline-error">
      转出账户和转入账户需要不同。
    </p>

    <label class="amount-field">
      <span class="field-label">转账金额</span>
      <span class="amount-shell">
        <span class="currency">¥</span>
        <input
          ref="transferAmount"
          v-model="draft.amount"
          class="amount-input"
          inputmode="decimal"
          min="0.01"
          step="0.01"
          type="number"
          placeholder="0.00"
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
        <span class="field-label">标签</span>
        <input v-model="draft.tags" placeholder="可选，逗号分隔" />
      </label>
      <label class="field field-wide">
        <span class="field-label">描述</span>
        <input v-model="draft.description" placeholder="这次转账的用途" />
      </label>
    </div>

    <div class="pair-note">
      <span class="pair-dot out"></span>
      自动写入“转出 / 内转”
      <span class="pair-line"></span>
      <span class="pair-dot in"></span>
      自动写入“转入 / 内转”
    </div>

    <button
      class="primary-action"
      type="submit"
      :disabled="!canSave || saving"
    >
      <span>{{ saving ? '正在保存' : '保存转账' }}</span>
      <span aria-hidden="true">→</span>
    </button>
  </form>
</template>

<style scoped>
.transfer-form {
  display: grid;
  gap: 1.5rem;
}

.route {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: end;
  gap: 1rem;
  padding: 1rem;
  border: 1px solid var(--rule);
  border-radius: 0.85rem;
  background: var(--paper);
}

.account-stop {
  display: grid;
  gap: 0.5rem;
}

.account-stop select {
  min-width: 0;
  padding: 0.7rem;
  border: 1px solid var(--rule);
  border-radius: 0.55rem;
  background: white;
  color: var(--ink);
  font: inherit;
}

.swap {
  width: 2.4rem;
  height: 2.4rem;
  border: 1px solid var(--rule);
  border-radius: 50%;
  background: white;
  color: var(--blue);
  cursor: pointer;
}

.field-label {
  color: var(--muted);
  font-size: 0.74rem;
  letter-spacing: 0.08em;
}

.inline-error {
  margin: -0.8rem 0 0;
  color: var(--expense);
  font-size: 0.8rem;
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

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}

.field {
  display: grid;
  gap: 0.4rem;
}

.field-wide {
  grid-column: 1 / -1;
}

.field input {
  padding: 0.72rem 0;
  border: 0;
  border-bottom: 1px solid var(--rule);
  outline: 0;
  background: transparent;
  color: var(--ink);
  font: inherit;
}

.pair-note {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  color: var(--muted);
  font-size: 0.78rem;
}

.pair-dot {
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 50%;
}

.pair-dot.out {
  background: var(--expense);
}

.pair-dot.in {
  background: var(--income);
}

.pair-line {
  flex: 1;
  height: 1px;
  background: var(--rule);
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
  .route {
    grid-template-columns: 1fr;
  }

  .swap {
    justify-self: center;
    transform: rotate(90deg);
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .field-wide {
    grid-column: auto;
  }
}
</style>
