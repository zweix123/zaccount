<script setup lang="ts">
export type ViewName = 'entry' | 'ledger' | 'analysis'

defineProps<{
  activeView: ViewName
}>()

const emit = defineEmits<{
  navigate: [view: ViewName]
}>()

const items: { view: ViewName; label: string; mark: string }[] = [
  { view: 'entry', label: '记一笔', mark: '+' },
  { view: 'ledger', label: '账目', mark: '≡' },
  { view: 'analysis', label: '分析', mark: '⌁' },
]
</script>

<template>
  <nav class="navigation" aria-label="主要功能">
    <button
      v-for="item in items"
      :key="item.view"
      class="navigation-item"
      :class="{ active: item.view === activeView }"
      type="button"
      @click="emit('navigate', item.view)"
    >
      <span class="navigation-mark" aria-hidden="true">{{ item.mark }}</span>
      <span>{{ item.label }}</span>
    </button>
  </nav>
</template>

<style scoped>
.navigation {
  display: grid;
  gap: 0.45rem;
}

.navigation-item {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  width: 100%;
  padding: 0.75rem 0.9rem;
  border: 0;
  border-radius: 0.7rem;
  background: transparent;
  color: var(--muted);
  font: inherit;
  text-align: left;
  cursor: pointer;
  transition:
    color 160ms ease,
    background 160ms ease;
}

.navigation-item:hover {
  color: var(--ink);
  background: rgb(255 255 255 / 68%);
}

.navigation-item.active {
  color: white;
  background: var(--ink);
}

.navigation-mark {
  display: grid;
  place-items: center;
  width: 1.7rem;
  height: 1.7rem;
  border: 1px solid currentColor;
  border-radius: 50%;
  font-family: var(--font-data);
  line-height: 1;
}

@media (max-width: 760px) {
  .navigation {
    grid-template-columns: repeat(3, 1fr);
  }

  .navigation-item {
    justify-content: center;
    padding: 0.6rem;
  }

  .navigation-mark {
    display: none;
  }
}
</style>
