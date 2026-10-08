<script setup>
import { ArrowUpRight, ArrowDownRight } from 'lucide-vue-next'
import Sparkline from './Sparkline.vue'

defineProps({
  label: { type: String, required: true },
  value: { type: [Number, String], required: true },
  icon: { type: Object, required: true },
  tone: { type: String, default: 'primary' }, // primary|info|violet|success|warning|accent
  hint: { type: String, default: '' },
  delta: { type: Number, default: null },
  trend: { type: Array, default: null },
  variant: { type: String, default: 'default' }, // default | featured | compact
  to: { type: String, default: null },
})
</script>

<template>
  <component
    :is="to ? 'RouterLink' : 'div'" :to="to"
    class="card" :class="[`tone-${tone}`, `v-${variant}`]"
  >
    <div class="top">
      <span class="ic"><component :is="icon" :size="variant === 'featured' ? 20 : 17" :stroke-width="1.9" /></span>
      <span class="label">{{ label }}</span>
      <ArrowUpRight v-if="to" :size="15" class="go" />
    </div>

    <div class="mid">
      <span class="value num">{{ value }}</span>
      <span v-if="delta !== null" class="delta num" :class="delta >= 0 ? 'up' : 'down'">
        <component :is="delta >= 0 ? ArrowUpRight : ArrowDownRight" :size="13" />{{ Math.abs(delta) }}%
      </span>
    </div>

    <div class="bot">
      <span class="hint">{{ hint }}</span>
      <Sparkline v-if="trend?.length" :data="trend" color="var(--tone)" :width="variant === 'featured' ? 150 : 96" :height="variant === 'featured' ? 44 : 30" />
    </div>
  </component>
</template>

<style scoped>
.tone-primary { --tone: var(--c-primary); --tone-bg: var(--c-primary-50); }
.tone-info { --tone: var(--c-info); --tone-bg: var(--c-info-bg); }
.tone-violet { --tone: var(--c-violet); --tone-bg: var(--c-violet-bg); }
.tone-success { --tone: var(--c-success); --tone-bg: var(--c-success-bg); }
.tone-warning { --tone: var(--c-warning); --tone-bg: var(--c-warning-bg); }
.tone-accent { --tone: var(--c-accent); --tone-bg: var(--c-accent-50); }

.card {
  position: relative; display: flex; flex-direction: column; gap: 14px; padding: 18px;
  background: var(--c-surface); border: 1px solid var(--c-border); border-radius: var(--radius-lg);
  box-shadow: var(--shadow-xs); color: inherit;
  transition: box-shadow var(--t-base) var(--ease), transform var(--t-base) var(--ease), border-color var(--t-base);
}
a.card:hover { box-shadow: var(--shadow-md); transform: translateY(-2px); border-color: var(--c-border-strong); }
.top { display: flex; align-items: center; gap: 10px; }
.ic { width: 30px; height: 30px; border-radius: 8px; display: grid; place-items: center; color: var(--tone); background: var(--tone-bg); }
.label { font-size: 13px; font-weight: 500; color: var(--c-text-2); }
.go { margin-left: auto; color: var(--c-faint); transition: color var(--t-fast), transform var(--t-fast); }
a.card:hover .go { color: var(--tone); transform: translate(2px, -2px); }

.mid { display: flex; align-items: baseline; gap: 10px; }
.value { font-size: 30px; font-weight: 650; letter-spacing: -0.03em; line-height: 1; }
.delta { display: inline-flex; align-items: center; gap: 1px; font-size: 12px; font-weight: 600; padding: 2px 6px 2px 4px; border-radius: 99px; }
.delta.up { color: var(--c-success); background: var(--c-success-bg); }
.delta.down { color: var(--c-danger); background: var(--c-danger-bg); }

.bot { display: flex; align-items: flex-end; justify-content: space-between; gap: 12px; margin-top: auto; }
.hint { font-size: 12px; color: var(--c-muted); }

/* Featured: the one that needs action first */
.v-featured {
  padding: 22px; gap: 18px; overflow: hidden;
  background:
    radial-gradient(120% 90% at 100% 0%, color-mix(in srgb, var(--tone) 14%, transparent) 0%, transparent 60%),
    var(--c-surface);
  border-color: color-mix(in srgb, var(--tone) 28%, var(--c-border));
}
.v-featured .value { font-size: 52px; }
.v-featured .label { font-size: 14px; font-weight: 600; color: var(--c-text); }
.v-featured .ic { width: 36px; height: 36px; border-radius: 10px; }
.v-featured .hint { font-size: 13px; }

.v-compact { padding: 14px 16px; gap: 10px; }
.v-compact .value { font-size: 24px; }
</style>

