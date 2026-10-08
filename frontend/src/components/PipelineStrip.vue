<script setup>
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import { ChevronRight } from 'lucide-vue-next'

// Compact end-to-end flow: counts of work sitting at each stage.
const props = defineProps({
  counts: { type: Object, required: true },
  inventoryIn: { type: Number, default: 0 },
  highlight: { type: String, default: '' }, // stage key to emphasise for current role
})

const stages = computed(() => [
  { key: 'request',  label: 'Request',      value: props.counts.pendingVerification, sub: 'pending verification', to: '/requests' },
  { key: 'verify',   label: 'Verified',     value: props.counts.verified,           sub: 'by receiver',         to: '/requests' },
  { key: 'review',   label: 'Review',       value: props.counts.pendingApproval,    sub: 'awaiting approval',   to: '/approval' },
  { key: 'po',       label: 'Purchase Order', value: props.counts.poCreated,        sub: 'open orders',         to: '/purchase-orders' },
  { key: 'receive',  label: 'Receiving',    value: props.counts.received,           sub: 'goods received',      to: '/receiving' },
  { key: 'stock',    label: 'Inventory',    value: props.inventoryIn,               sub: 'SKUs tracked',        to: '/inventory' },
])
</script>

<template>
  <div class="flow">
    <template v-for="(s, i) in stages" :key="s.key">
      <RouterLink :to="s.to" class="stage" :class="{ hot: highlight === s.key }">
        <span class="step num">{{ String(i + 1).padStart(2, '0') }}</span>
        <span class="name">{{ s.label }}</span>
        <span class="count num">{{ s.value }}</span>
        <span class="sub">{{ s.sub }}</span>
        <span class="rail"><i :style="{ width: Math.min(100, s.value * 4) + '%' }" /></span>
      </RouterLink>
      <ChevronRight v-if="i < stages.length - 1" :size="16" class="sep" />
    </template>
  </div>
</template>

<style scoped>
.flow { display: flex; align-items: stretch; gap: 4px; overflow-x: auto; padding: 2px; }
.sep { flex: none; align-self: center; color: var(--c-faint); }
.stage {
  flex: 1 1 0; min-width: 132px; display: flex; flex-direction: column; gap: 2px; padding: 12px 14px;
  border-radius: var(--radius); border: 1px solid transparent; transition: background var(--t-fast), border-color var(--t-fast);
}
.stage:hover { background: var(--c-surface-2); border-color: var(--c-border); }
.stage.hot { background: var(--c-primary-50); border-color: var(--c-primary-100); }
.step { font-size: 11px; font-weight: 600; color: var(--c-faint); letter-spacing: 0.04em; }
.stage.hot .step { color: var(--c-primary); }
.name { font-size: 12.5px; font-weight: 600; color: var(--c-text-2); }
.count { font-size: 24px; font-weight: 650; letter-spacing: -0.03em; line-height: 1.25; }
.sub { font-size: 11.5px; color: var(--c-muted); }
.rail { height: 3px; margin-top: 8px; border-radius: 3px; background: var(--c-border); overflow: hidden; }
.rail i { display: block; height: 100%; border-radius: 3px; background: var(--c-border-strong); transition: width 600ms var(--ease); }
.stage.hot .rail i { background: var(--c-primary); }
</style>
