<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'
import { Search, Bell, Menu, ChevronDown, Check, FileCheck2, PackageCheck, AlertCircle } from 'lucide-vue-next'
import { useSession, ROLES } from '@/composables/useSession'

defineEmits(['menu'])

const route = useRoute()
const { user, role, roleKey, setRole } = useSession()

const open = ref(null) // 'notif' | 'user' | null
const root = ref(null)
const toggle = (k) => (open.value = open.value === k ? null : k)
const onDoc = (e) => { if (root.value && !root.value.contains(e.target)) open.value = null }
onMounted(() => document.addEventListener('click', onDoc))
onBeforeUnmount(() => document.removeEventListener('click', onDoc))

const notifications = [
  { icon: FileCheck2, tone: 'info', title: 'MR-2026-0141 verified', text: 'Ready for purchase review', when: '12m' },
  { icon: AlertCircle, tone: 'warning', title: '3 ADVANCE requests due this week', text: 'Required dates approaching', when: '1h' },
  { icon: PackageCheck, tone: 'success', title: 'PO-2026-0088 received', text: 'Stock updated for 4 items', when: '1d' },
]
</script>

<template>
  <header class="hd" ref="root">
    <button class="icon-btn menu" aria-label="Open menu" @click="$emit('menu')"><Menu :size="20" /></button>

    <div class="crumb">
      <span class="crumb__root">MMS</span><span class="crumb__sep">/</span>
      <span class="crumb__cur">{{ route.meta.title }}</span>
    </div>

    <label class="search">
      <Search :size="15" />
      <input type="search" placeholder="Search requests, POs, materials…" />
      <kbd>⌘K</kbd>
    </label>

    <div class="hd__right">
      <div class="pop-wrap">
        <button class="icon-btn" :class="{ on: open === 'notif' }" aria-label="Notifications" @click.stop="toggle('notif')">
          <Bell :size="18" /><span class="dot" />
        </button>
        <Transition name="pop">
          <div v-if="open === 'notif'" class="pop pop--notif" @click.stop>
            <div class="pop__head"><strong>Notifications</strong><button class="link">Mark all read</button></div>
            <ul>
              <li v-for="n in notifications" :key="n.title">
                <span class="n-ic" :class="`tone-${n.tone}`"><component :is="n.icon" :size="15" /></span>
                <div><b>{{ n.title }}</b><small>{{ n.text }}</small></div>
                <time>{{ n.when }}</time>
              </li>
            </ul>
          </div>
        </Transition>
      </div>

      <span class="vr" />

      <div class="pop-wrap">
        <button class="user" @click.stop="toggle('user')">
          <span class="avatar">{{ user.initials }}</span>
          <span class="user__meta">
            <b>{{ user.name }}</b>
            <span class="role" :class="`tone-${role.tone}`"><i />{{ role.label }}</span>
          </span>
          <ChevronDown :size="14" class="chev" />
        </button>
        <Transition name="pop">
          <div v-if="open === 'user'" class="pop pop--user" @click.stop>
            <div class="pop__head"><strong>Demo role</strong><small>Switch to preview each experience</small></div>
            <button v-for="r in ROLES" :key="r.key" class="opt" @click="setRole(r.key); open = null">
              <span class="role" :class="`tone-${r.tone}`"><i />{{ r.label }}</span>
              <Check v-if="roleKey === r.key" :size="15" class="tick" />
            </button>
          </div>
        </Transition>
      </div>
    </div>
  </header>
</template>

<style scoped>
.hd {
  position: sticky; top: 0; z-index: 30; height: var(--header-h);
  display: flex; align-items: center; gap: 20px; padding: 0 32px;
  background: rgba(245, 246, 248, 0.78); backdrop-filter: saturate(1.4) blur(12px);
  border-bottom: 1px solid var(--c-border);
}
.icon-btn { position: relative; width: 36px; height: 36px; border: 1px solid transparent; border-radius: var(--radius); background: none; color: var(--c-text-2); display: grid; place-items: center; transition: background var(--t-fast), border-color var(--t-fast); }
.icon-btn:hover, .icon-btn.on { background: var(--c-surface); border-color: var(--c-border); }
.menu { display: none; margin-left: -8px; }
.dot { position: absolute; top: 8px; right: 9px; width: 8px; height: 8px; border-radius: 50%; background: var(--c-danger); box-shadow: 0 0 0 2px var(--c-bg); }

.crumb { display: flex; align-items: center; gap: 8px; font-size: 13px; white-space: nowrap; }
.crumb__root { color: var(--c-muted); }
.crumb__sep { color: var(--c-faint); }
.crumb__cur { font-weight: 600; }

.search {
  display: flex; align-items: center; gap: 8px; height: 36px; width: 360px; max-width: 100%;
  margin: 0 auto 0 24px; padding: 0 10px 0 12px; color: var(--c-muted);
  background: var(--c-surface); border: 1px solid var(--c-border); border-radius: var(--radius);
  box-shadow: var(--shadow-xs); transition: border-color var(--t-fast), box-shadow var(--t-fast);
}
.search:focus-within { border-color: var(--c-primary); box-shadow: 0 0 0 3px var(--c-primary-100); }
.search input { flex: 1; min-width: 0; border: 0; outline: 0; background: none; font: inherit; color: var(--c-text); }
kbd { font-family: var(--font-sans); font-size: 11px; color: var(--c-muted); border: 1px solid var(--c-border); border-bottom-width: 2px; border-radius: 5px; padding: 0 5px; background: var(--c-surface-2); }

.hd__right { display: flex; align-items: center; gap: 10px; }
.vr { width: 1px; height: 22px; background: var(--c-border-strong); }
.pop-wrap { position: relative; }

.user { display: flex; align-items: center; gap: 10px; padding: 4px 8px 4px 4px; border: 1px solid transparent; border-radius: var(--radius); background: none; text-align: left; transition: background var(--t-fast), border-color var(--t-fast); }
.user:hover { background: var(--c-surface); border-color: var(--c-border); }
.avatar { width: 32px; height: 32px; border-radius: 50%; display: grid; place-items: center; font-size: 12px; font-weight: 600; color: #fff; background: linear-gradient(140deg, #1c2540, #0e1320); box-shadow: 0 0 0 2px var(--c-surface), 0 0 0 3px var(--c-border); }
.user__meta { display: flex; flex-direction: column; line-height: 1.25; }
.user__meta b { font-size: 13px; font-weight: 600; }
.chev { color: var(--c-muted); }

.role { display: inline-flex; align-items: center; gap: 6px; font-size: 11.5px; font-weight: 500; color: var(--tone); }
.role i { width: 6px; height: 6px; border-radius: 50%; background: var(--tone); }
.tone-info { --tone: var(--c-info); --tone-bg: var(--c-info-bg); }
.tone-violet { --tone: var(--c-violet); --tone-bg: var(--c-violet-bg); }
.tone-success { --tone: var(--c-success); --tone-bg: var(--c-success-bg); }
.tone-warning { --tone: var(--c-warning); --tone-bg: var(--c-warning-bg); }

.pop { position: absolute; right: 0; top: calc(100% + 8px); background: var(--c-surface); border: 1px solid var(--c-border); border-radius: var(--radius-lg); box-shadow: var(--shadow-lg); overflow: hidden; transform-origin: top right; }
.pop--notif { width: 340px; }
.pop--user { width: 250px; }
.pop__head { display: flex; align-items: baseline; justify-content: space-between; gap: 8px; flex-wrap: wrap; padding: 12px 14px; border-bottom: 1px solid var(--c-border); }
.pop__head small { color: var(--c-muted); font-size: 12px; width: 100%; }
.link { border: 0; background: none; color: var(--c-primary); font-size: 12px; font-weight: 500; padding: 0; }
.pop li { display: grid; grid-template-columns: 30px 1fr auto; gap: 10px; padding: 11px 14px; align-items: start; transition: background var(--t-fast); }
.pop li + li { border-top: 1px solid var(--c-border); }
.pop li:hover { background: var(--c-surface-2); }
.pop li b { display: block; font-size: 13px; font-weight: 600; }
.pop li small { color: var(--c-muted); font-size: 12px; }
.pop li time { font-size: 11.5px; color: var(--c-faint); }
.n-ic { width: 30px; height: 30px; border-radius: 8px; display: grid; place-items: center; color: var(--tone); background: var(--tone-bg); }
.opt { display: flex; align-items: center; justify-content: space-between; width: 100%; padding: 10px 14px; border: 0; background: none; transition: background var(--t-fast); }
.opt:hover { background: var(--c-surface-2); }
.tick { color: var(--c-primary); }

.pop-enter-active, .pop-leave-active { transition: opacity var(--t-fast) var(--ease), transform var(--t-fast) var(--ease); }
.pop-enter-from, .pop-leave-to { opacity: 0; transform: translateY(-4px) scale(0.98); }

@media (max-width: 960px) {
  .hd { padding: 0 16px; gap: 12px; }
  .menu { display: grid; }
  .search, .crumb__root, .crumb__sep, .user__meta, .chev, .vr { display: none; }
  .crumb { margin-right: auto; }
  .pop--notif { position: fixed; right: 12px; left: 12px; width: auto; top: 68px; }
}
</style>
