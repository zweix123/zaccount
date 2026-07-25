<script setup lang="ts">
import { shallowRef, useTemplateRef } from 'vue'

import type { EntryPayload, LedgerMeta, TransferPayload } from '@/types'

import EntryForm from './EntryForm.vue'
import TransferForm from './TransferForm.vue'

defineProps<{
  meta: LedgerMeta
  saving: boolean
}>()

const emit = defineEmits<{
  saveEntry: [payload: EntryPayload]
  saveTransfer: [payload: TransferPayload]
}>()

const mode = shallowRef<'entry' | 'transfer'>('entry')
const entryForm = useTemplateRef<InstanceType<typeof EntryForm>>('entryForm')
const transferForm =
  useTemplateRef<InstanceType<typeof TransferForm>>('transferForm')

function resetActiveForm(): void {
  if (mode.value === 'entry') entryForm.value?.resetAfterSave()
  else transferForm.value?.resetAfterSave()
}

defineExpose({ resetActiveForm })
</script>

<template>
  <section class="workspace">
    <header class="workspace-header">
      <div>
        <p class="eyebrow">新的资金变化</p>
        <h1>{{ mode === 'entry' ? '记一笔账' : '账户之间转账' }}</h1>
      </div>
      <div class="mode-switch">
        <button
          type="button"
          :class="{ active: mode === 'entry' }"
          @click="mode = 'entry'"
        >
          普通账目
        </button>
        <button
          type="button"
          :class="{ active: mode === 'transfer' }"
          @click="mode = 'transfer'"
        >
          账户转账
        </button>
      </div>
    </header>

    <div class="form-card">
      <EntryForm
        v-if="mode === 'entry'"
        ref="entryForm"
        :meta="meta"
        :saving="saving"
        @save="emit('saveEntry', $event)"
      />
      <TransferForm
        v-else
        ref="transferForm"
        :meta="meta"
        :saving="saving"
        @save="emit('saveTransfer', $event)"
      />
    </div>
  </section>
</template>

<style scoped>
.workspace {
  width: min(760px, 100%);
  margin: 0 auto;
}

.workspace-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 2rem;
  margin-bottom: 1.5rem;
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

.mode-switch {
  display: flex;
  gap: 0.25rem;
  padding: 0.25rem;
  border: 1px solid var(--rule);
  border-radius: 0.65rem;
  background: var(--surface);
}

.mode-switch button {
  padding: 0.55rem 0.7rem;
  border: 0;
  border-radius: 0.45rem;
  background: transparent;
  color: var(--muted);
  font: 0.8rem var(--font-body);
  cursor: pointer;
}

.mode-switch button.active {
  background: var(--ink);
  color: white;
}

.form-card {
  padding: clamp(1.25rem, 4vw, 2.5rem);
  border: 1px solid var(--rule);
  border-radius: 1.1rem;
  background: var(--surface);
  box-shadow: 0 24px 80px rgb(23 35 59 / 7%);
}

@media (max-width: 620px) {
  .workspace-header {
    align-items: flex-start;
    flex-direction: column;
    gap: 1rem;
  }
}
</style>
