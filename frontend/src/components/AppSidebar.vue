<script setup>
import { RouterLink } from 'vue-router'
import {
  LayoutDashboard, FileText, ShieldCheck, ShoppingCart, PackageCheck, Boxes,
  PanelLeftClose, PanelLeftOpen, X, HelpCircle, Hexagon,
} from 'lucide-vue-next'
import { navItems } from '@/router'

defineProps({ collapsed: Boolean, mobileOpen: Boolean })
defineEmits(['toggle', 'close'])

const icons = { LayoutDashboard, FileText, ShieldCheck, ShoppingCart, PackageCheck, Boxes }

const groups = [
  { label: 'Overview', items: navItems.slice(0, 1) },
  { label: 'Procure', items: navItems.slice(1, 4) },
  { label: 'Fulfil', items: navItems.slice(4) },
]
</script>

<template>
  <aside class="sb" :class="{ 'is-collapsed': collapsed, 'is-open': mobileOpen }">
    <div class="sb__brand">
      <div class="logo"><Hexagon :size="18" :stroke-width="2.4" /></div>
      <div class="brand-text">
        <strong>MMS</strong>
        <span>Material Management</span>
      </div>
      <button class="icon-btn mobile-only" aria-label="Close menu" @click="$emit('close')"><X :size="18" /></button>
    </div>

    <nav class="sb__nav">
      <div v-for="g in groups" :key="g.label" class="group">
        <div class="group__label">{{ g.label }}</div>
        <RouterLink
          v-for="item in g.items" :key="item.path" :to="item.path"
          class="item" active-class="is-active" exact-active-class="is-active"
          :title="collapsed ? item.label : undefined"
          @click="$emit('close')"
        >
          <span class="item__bar" />
          <component :is="icons[item.icon]" :size="18" :stroke-width="1.8" class="item__icon" />
          <span class="item__label">{{ item.label }}</span>
          <span v-if="item.badge" class="item__badge num">{{ item.badge }}</span>
        </RouterLink>
      </div>
    </nav>

    <div class="sb__foot">
      <a class="item" href="#" title="Help"><HelpCircle :size="18" :stroke-width="1.8" class="item__icon" /><span class="item__label">Help &amp; docs</span></a>
      <button class="item collapse" @click="$emit('toggle')" :title="collapsed ? 'Expand' : 'Collapse'">
        <component :is="collapsed ? PanelLeftOpen : PanelLeftClose" :size="18" :stroke-width="1.8" class="item__icon" />
        <span class="item__label">Collapse</span>
      </button>
    </div>
  </aside>
</template>

<style scoped>
.sb {
  position: fixed; inset: 0 auto 0 0; width: var(--sb-width);
  background: var(--sb-bg); color: var(--sb-text);
  display: flex; flex-direction: column; z-index: 50;
  border-right: 1px solid var(--sb-border);
  transition: width var(--t-base) var(--ease), transform var(--t-base) var(--ease);
  overflow: hidden;
}
.sb.is-collapsed { width: var(--sb-width-collapsed); }

.sb__brand { height: var(--header-h); display: flex; align-items: center; gap: 12px; padding: 0 18px; border-bottom: 1px solid var(--sb-border); }
.logo {
  flex: none; width: 32px; height: 32px; border-radius: 8px; display: grid; place-items: center; color: #fff;
  background: linear-gradient(140deg, #4a68ff 0%, #2a43c7 100%);
  box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.12) inset, 0 4px 12px rgba(53, 82, 230, 0.45);
}
.brand-text { display: flex; flex-direction: column; line-height: 1.15; white-space: nowrap; }
.brand-text strong { color: #fff; font-size: 15px; letter-spacing: 0.02em; }
.brand-text span { font-size: 11px; color: var(--sb-text); }

.sb__nav { flex: 1; overflow-y: auto; padding: 14px 10px; }
.group + .group { margin-top: 18px; }
.group__label { padding: 0 10px 6px; font-size: 10.5px; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; color: #5d667a; white-space: nowrap; }

.item {
  position: relative; display: flex; align-items: center; gap: 12px; width: 100%;
  height: 38px; padding: 0 10px; border: 0; background: none; border-radius: var(--radius);
  color: var(--sb-text); font-size: 13.5px; font-weight: 500; text-align: left; white-space: nowrap;
  transition: background var(--t-fast) var(--ease), color var(--t-fast) var(--ease);
}
.item + .item { margin-top: 2px; }
.item:hover { background: var(--sb-hover); color: #d6dbe6; }
.item.is-active { background: var(--sb-active); color: var(--sb-text-active); }
.item__icon { flex: none; transition: color var(--t-fast); }
.item.is-active .item__icon { color: #8da2ff; }
.item__bar { position: absolute; left: -10px; top: 9px; bottom: 9px; width: 3px; border-radius: 0 3px 3px 0; background: #6b86ff; opacity: 0; transform: scaleY(0.4); transition: all var(--t-base) var(--ease); }
.item.is-active .item__bar { opacity: 1; transform: none; }
.item__badge {
  margin-left: auto; min-width: 22px; height: 20px; padding: 0 6px; border-radius: 10px;
  display: grid; place-items: center; font-size: 11px; font-weight: 600;
  background: rgba(255, 255, 255, 0.09); color: #c5ccdb;
}
.item.is-active .item__badge { background: var(--c-primary); color: #fff; }

.sb__foot { padding: 10px; border-top: 1px solid var(--sb-border); }

.icon-btn { margin-left: auto; width: 32px; height: 32px; border: 0; border-radius: 8px; background: none; color: var(--sb-text); display: grid; place-items: center; }
.icon-btn:hover { background: var(--sb-hover); }
.mobile-only { display: none; }

/* Collapsed rail */
.sb.is-collapsed .brand-text, .sb.is-collapsed .item__label, .sb.is-collapsed .item__badge, .sb.is-collapsed .group__label { display: none; }
.sb.is-collapsed .sb__brand { justify-content: center; padding: 0; }
.sb.is-collapsed .item { justify-content: center; padding: 0; }
.sb.is-collapsed .group + .group { margin-top: 10px; padding-top: 10px; border-top: 1px solid var(--sb-border); }
.sb.is-collapsed .item__bar { left: -10px; }

@media (max-width: 960px) {
  .sb, .sb.is-collapsed { width: 272px; transform: translateX(-100%); }
  .sb.is-open { transform: none; box-shadow: var(--shadow-lg); }
  .sb.is-collapsed .brand-text, .sb.is-collapsed .item__label, .sb.is-collapsed .group__label { display: revert; }
  .sb.is-collapsed .item__badge { display: grid; }
  .sb.is-collapsed .sb__brand { justify-content: flex-start; padding: 0 18px; }
  .sb.is-collapsed .item { justify-content: flex-start; padding: 0 10px; }
  .mobile-only { display: grid; }
  .collapse { display: none; }
}
</style>
