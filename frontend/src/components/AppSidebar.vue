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
  background: #203d59; color: #dbe5ef;
  display: flex; flex-direction: column; z-index: 50;
  border-right: 1px solid #294966;
  transition: width var(--t-base) var(--ease), transform var(--t-base) var(--ease);
  overflow: hidden;
}
.sb.is-collapsed { width: var(--sb-width-collapsed); }
.sb__brand {
  height: var(--header-h); min-height: 80px; display: flex; align-items: center;
  gap: 11px; padding: 0 20px; border-bottom: 1px solid #ffffff17;
}
.logo {
  flex: none; width: 32px; height: 32px; border-radius: 8px;
  display: grid; place-items: center; color: #203d59;
  background: #d58a35; box-shadow: none;
}
.brand-text { display: flex; flex-direction: column; line-height: 1.2; white-space: nowrap; gap: 3px; }
.brand-text strong { color: #fff; font-size: 15px; letter-spacing: -.01em; }
.brand-text span { font-size: 11px; color: #b8c9da; }
.sb__nav { flex: 1; overflow-y: auto; padding: 14px 11px; }
.group + .group { margin-top: 18px; }
.group__label {
  padding: 0 10px 7px; font-size: 10px; font-weight: 650;
  letter-spacing: .1em; text-transform: uppercase; color: #9cb1c7; white-space: nowrap;
}
.item {
  position: relative; display: flex; align-items: center; gap: 10px; width: 100%;
  min-height: 40px; padding: 0 12px; border: 0; background: transparent;
  border-radius: 6px; color: #d3dfeb; font-size: 13px; font-weight: 550;
  text-align: left; white-space: nowrap; text-decoration: none;
  transition: background .16s ease, color .16s ease;
}
.item + .item { margin-top: 4px; }
.item:hover { background: #ffffff12; color: #fff; }
.item.is-active { background: #ffffff20; color: #fff; }
.item__icon { flex: none; color: #c2d0df; transition: color .16s ease; }
.item.is-active .item__icon { color: #e09a48; }
.item__bar { position: absolute; left: -11px; top: 8px; bottom: 8px; width: 3px; border-radius: 0 3px 3px 0; background: #e09a48; opacity: 0; }
.item.is-active .item__bar { opacity: 1; }
.item__badge {
  margin-left: auto; min-width: 22px; height: 20px; padding: 0 6px;
  border-radius: 10px; display: grid; place-items: center; font-size: 11px;
  font-weight: 600; background: #ffffff18; color: #fff;
}
.item.is-active .item__badge { background: #d58a35; color: #203d59; }
.sb__foot { padding: 10px 11px; border-top: 1px solid #ffffff17; }
.icon-btn {
  margin-left: auto; width: 32px; height: 32px; border: 0; border-radius: 8px;
  background: none; color: #d3dfeb; display: grid; place-items: center;
}
.icon-btn:hover { background: #ffffff12; }
.mobile-only { display: none; }
.sb.is-collapsed .brand-text, .sb.is-collapsed .item__label,
.sb.is-collapsed .item__badge, .sb.is-collapsed .group__label { display: none; }
.sb.is-collapsed .sb__brand { justify-content: center; padding: 0; }
.sb.is-collapsed .item { justify-content: center; padding: 0; }
.sb.is-collapsed .group + .group { margin-top: 10px; padding-top: 10px; border-top: 1px solid #ffffff17; }
.sb.is-collapsed .item__bar { left: -11px; }
@media (max-width: 960px) {
  .sb, .sb.is-collapsed { width: 272px; transform: translateX(-100%); }
  .sb.is-open { transform: none; box-shadow: var(--shadow-lg); }
  .sb.is-collapsed .brand-text, .sb.is-collapsed .item__label,
  .sb.is-collapsed .group__label { display: revert; }
  .sb.is-collapsed .item__badge { display: grid; }
  .sb.is-collapsed .sb__brand { justify-content: flex-start; padding: 0 20px; }
  .sb.is-collapsed .item { justify-content: flex-start; padding: 0 12px; }
  .mobile-only { display: grid; }
  .collapse { display: none; }
}
</style>

