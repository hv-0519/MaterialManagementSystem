<script setup>
import { ref, onMounted, computed } from 'vue'
import { RouterLink } from 'vue-router'
import {
  ClipboardList, ClipboardCheck, ShieldCheck, CircleCheckBig, ShoppingCart,
  PackageCheck, Boxes, Plus, ArrowRight, Inbox,
} from 'lucide-vue-next'
import StatCard from '@/components/StatCard.vue'
import PipelineStrip from '@/components/PipelineStrip.vue'
import TypeTag from '@/components/TypeTag.vue'
import { getDashboardSummary } from '@/services/dashboard'
import { useSession } from '@/composables/useSession'

const { user, role, roleKey } = useSession()
const data = ref(null)
onMounted(async () => { data.value = await getDashboardSummary() })

const greeting = computed(() => {
  const h = new Date().getHours()
  return h < 12 ? 'Good morning' : h < 17 ? 'Good afternoon' : 'Good evening'
})

// What each role should look at first
const focus = computed(() => ({
  receiver: { key: 'request', title: 'Requests waiting for verification', cta: 'Verify requests', to: '/requests' },
  supervisor: { key: 'review', title: 'Verified requests awaiting your decision', cta: 'Open approval queue', to: '/approval' },
  admin: { key: '', title: 'Latest requests across the workflow', cta: 'View all requests', to: '/requests' },
}[roleKey.value]))

const stock = computed(() => {
  const i = data.value?.inventory
  if (!i) return []
  return [
    { label: 'Healthy', n: i.healthy, c: 'var(--c-success)' },
    { label: 'Low', n: i.low, c: 'var(--c-warning)' },
    { label: 'Out of stock', n: i.out, c: 'var(--c-danger)' },
  ]
})
</script>

<template>
  <div class="dash">
    <!-- Page header -->
    <header class="pg-head">
      <div>
        <p class="eyebrow">{{ role.label }} workspace</p>
        <h1>{{ greeting }}, {{ user.name.split(' ')[0] }}</h1>
        <p class="sub">Here's where every material request stands across the procurement workflow.</p>
      </div>
      <RouterLink to="/requests/new" class="btn btn--primary"><Plus :size="16" />New Material Request</RouterLink>
    </header>

    <!-- Loading skeleton -->
    <template v-if="!data">
      <div class="skel-flow skeleton" />
      <div class="grid-top">
        <div class="skel-card skeleton" style="height: 196px" />
        <div class="skel-card skeleton" /><div class="skel-card skeleton" />
      </div>
      <div class="grid-sm"><div v-for="n in 4" :key="n" class="skel-card skeleton" style="height: 118px" /></div>
      <div class="grid-bot">
        <div class="skel-card skeleton" style="height: 300px" /><div class="skel-card skeleton" style="height: 300px" />
      </div>
    </template>

    <template v-else>
      <!-- Pipeline -->
      <section class="panel flow-panel enter" style="--d: 0ms">
        <div class="panel__head">
          <h2>Workflow pipeline</h2>
          <span class="legend">Live count at each stage</span>
        </div>
        <PipelineStrip :counts="data.counts" :inventory-in="data.inventory.skus" :highlight="focus.key" />
      </section>

      <!-- Primary cards: hierarchy -->
      <div class="grid-top">
        <StatCard class="enter" style="--d: 40ms"
          variant="featured" label="Pending Verification" :value="data.counts.pendingVerification"
          :icon="ClipboardList" tone="warning" :trend="data.trend.pendingVerification"
          hint="Needs receiver action" to="/requests" />
        <StatCard class="enter" style="--d: 80ms"
          label="Pending Purchase Approval" :value="data.counts.pendingApproval"
          :icon="ShieldCheck" tone="violet" hint="Verified, awaiting supervisor" to="/approval" />
        <StatCard class="enter" style="--d: 120ms"
          label="Approved Requests" :value="data.counts.approved" :delta="12"
          :icon="CircleCheckBig" tone="success" :trend="data.trend.approved" hint="vs. last month" to="/requests" />
      </div>

      <!-- Secondary cards -->
      <div class="grid-sm">
        <StatCard class="enter" style="--d: 160ms" variant="compact" label="Verified Requests" :value="data.counts.verified"
          :icon="ClipboardCheck" tone="info" hint="Awaiting review" />
        <StatCard class="enter" style="--d: 190ms" variant="compact" label="Purchase Orders" :value="data.counts.poCreated"
          :icon="ShoppingCart" tone="primary" :trend="data.trend.purchaseOrders" to="/purchase-orders" />
        <StatCard class="enter" style="--d: 220ms" variant="compact" label="Materials Received" :value="data.counts.received"
          :icon="PackageCheck" tone="accent" :trend="data.trend.received" to="/receiving" />
        <div class="panel stock enter" style="--d: 250ms">
          <div class="stock__top">
            <span class="ic"><Boxes :size="17" :stroke-width="1.9" /></span>
            <span class="lbl">Inventory / Stock</span>
            <RouterLink to="/inventory" class="more"><ArrowRight :size="15" /></RouterLink>
          </div>
          <div class="stock__val"><b class="num">{{ data.inventory.skus }}</b><span>SKUs</span></div>
          <div class="bar">
            <i v-for="s in stock" :key="s.label" :style="{ flex: s.n, background: s.c }" :title="`${s.label}: ${s.n}`" />
          </div>
          <div class="keys">
            <span v-for="s in stock" :key="s.label"><i :style="{ background: s.c }" />{{ s.label }} <b class="num">{{ s.n }}</b></span>
          </div>
        </div>
      </div>

      <!-- Attention + activity -->
      <div class="grid-bot">
        <section class="panel enter" style="--d: 290ms">
          <div class="panel__head">
            <h2>{{ focus.title }}</h2>
            <RouterLink :to="focus.to" class="head-link">{{ focus.cta }}<ArrowRight :size="14" /></RouterLink>
          </div>
          <ul v-if="data.attention.length" class="queue">
            <li v-for="r in data.attention" :key="r.id" :class="`tone-${r.tone}`">
              <span class="pip" />
              <div class="q-main">
                <div class="q-title"><span class="id num">{{ r.id }}</span><TypeTag :type="r.type" /></div>
                <div class="q-mat">{{ r.material }} <span class="qty num">Â· {{ r.qty }}</span></div>
              </div>
              <span class="q-note">{{ r.note }}</span>
              <ArrowRight :size="15" class="q-go" />
            </li>
          </ul>
          <div v-else class="empty"><Inbox :size="26" :stroke-width="1.4" /><b>You're all caught up</b><span>No requests need your attention right now.</span></div>
        </section>

        <section class="panel enter" style="--d: 330ms">
          <div class="panel__head"><h2>Recent activity</h2></div>
          <ol class="feed">
            <li v-for="a in data.activity" :key="a.target + a.when" :class="`t-${a.tone}`">
              <span class="node" />
              <p><b>{{ a.who }}</b> {{ a.action }} <span class="id num">{{ a.target }}</span></p>
              <time>{{ a.when }}</time>
            </li>
          </ol>
        </section>
      </div>
    </template>
  </div>
</template>

<style scoped>
.dash { display: flex; flex-direction: column; gap: 20px; }

.pg-head { display: flex; align-items: flex-end; justify-content: space-between; gap: 16px; flex-wrap: wrap; margin-bottom: 4px; }
.pg-head h1 { font-size: 26px; font-weight: 650; letter-spacing: -0.025em; margin: 4px 0 4px; }
.pg-head .sub { color: var(--c-muted); }

.panel { background: var(--c-surface); border: 1px solid var(--c-border); border-radius: var(--radius-lg); box-shadow: var(--shadow-xs); padding: 18px; }
.panel__head { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 14px; }
.panel__head h2 { font-size: 14px; font-weight: 600; }
.legend { font-size: 12px; color: var(--c-muted); }
.head-link { display: inline-flex; align-items: center; gap: 4px; font-size: 12.5px; font-weight: 500; color: var(--c-primary); }
.head-link:hover { text-decoration: underline; }
.flow-panel { padding-bottom: 14px; }

.grid-top { display: grid; grid-template-columns: 1.4fr 1fr 1fr; gap: 16px; }
.grid-top > :first-child { grid-row: span 1; }
.grid-sm { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
.grid-bot { display: grid; grid-template-columns: 1.6fr 1fr; gap: 16px; }

/* Entrance */
.enter { animation: rise 380ms var(--ease) both; animation-delay: var(--d, 0ms); }
@keyframes rise { from { opacity: 0; transform: translateY(8px); } }

/* Skeletons */
.skel-flow { height: 118px; border-radius: var(--radius-lg); }
.skel-card { height: 160px; border-radius: var(--radius-lg); }

/* Stock panel */
.stock { display: flex; flex-direction: column; gap: 10px; padding: 14px 16px; }
.stock__top { display: flex; align-items: center; gap: 10px; }
.stock .ic { width: 30px; height: 30px; border-radius: 8px; display: grid; place-items: center; color: var(--c-secondary); background: #eceef3; }
.lbl { font-size: 13px; font-weight: 500; color: var(--c-text-2); }
.more { margin-left: auto; color: var(--c-faint); display: grid; }
.more:hover { color: var(--c-primary); }
.stock__val { display: flex; align-items: baseline; gap: 6px; }
.stock__val b { font-size: 24px; font-weight: 650; letter-spacing: -0.03em; }
.stock__val span { font-size: 12px; color: var(--c-muted); }
.bar { display: flex; gap: 3px; height: 6px; }
.bar i { border-radius: 3px; min-width: 4px; }
.keys { display: flex; flex-wrap: wrap; gap: 4px 12px; font-size: 11.5px; color: var(--c-muted); }
.keys span { display: inline-flex; align-items: center; gap: 5px; }
.keys i { width: 6px; height: 6px; border-radius: 50%; }
.keys b { color: var(--c-text); font-weight: 600; }

/* Queue */
.tone-warning { --tone: var(--c-warning); } .tone-info { --tone: var(--c-info); } .tone-violet { --tone: var(--c-violet); }
.queue li {
  display: grid; grid-template-columns: 10px 1fr auto 16px; align-items: center; gap: 14px;
  padding: 12px 10px; margin: 0 -10px; border-radius: var(--radius); cursor: pointer;
  transition: background var(--t-fast);
}
.queue li + li { border-top: 1px solid var(--c-border); }
.queue li:hover { background: var(--c-surface-2); }
.pip { width: 8px; height: 8px; border-radius: 50%; background: var(--tone); box-shadow: 0 0 0 3px color-mix(in srgb, var(--tone) 18%, transparent); }
.q-title { display: flex; align-items: center; gap: 8px; }
.id { font-family: var(--font-mono); font-size: 12px; font-weight: 600; color: var(--c-text-2); }
.q-mat { font-size: 13.5px; margin-top: 2px; }
.qty { color: var(--c-muted); }
.q-note { font-size: 12px; color: var(--c-muted); white-space: nowrap; }
.q-go { color: var(--c-faint); transition: transform var(--t-fast), color var(--t-fast); }
.queue li:hover .q-go { transform: translateX(3px); color: var(--c-primary); }

.empty { display: flex; flex-direction: column; align-items: center; gap: 4px; padding: 36px 0; color: var(--c-muted); text-align: center; }
.empty b { color: var(--c-text); margin-top: 6px; }

/* Activity timeline */
.feed { position: relative; margin: 0; padding: 0; list-style: none; }
.feed::before { content: ''; position: absolute; left: 4px; top: 8px; bottom: 8px; width: 1px; background: var(--c-border); }
.feed li { position: relative; display: grid; grid-template-columns: 1fr auto; gap: 2px 10px; padding: 9px 0 9px 22px; }
.node { position: absolute; left: 0; top: 14px; width: 9px; height: 9px; border-radius: 50%; background: var(--c-surface); border: 2px solid var(--n); }
.t-info { --n: var(--c-info); } .t-success { --n: var(--c-success); } .t-primary { --n: var(--c-primary); }
.t-danger { --n: var(--c-danger); } .t-accent { --n: var(--c-accent); }
.feed p { font-size: 13px; color: var(--c-text-2); }
.feed p b { color: var(--c-text); font-weight: 600; }
.feed time { font-size: 11.5px; color: var(--c-faint); white-space: nowrap; }

@media (max-width: 1200px) {
  .grid-top { grid-template-columns: 1fr 1fr; }
  .grid-top > :first-child { grid-column: span 2; }
  .grid-sm { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 960px) { .grid-bot { grid-template-columns: 1fr; } }
@media (max-width: 640px) {
  .grid-top, .grid-sm { grid-template-columns: 1fr; }
  .grid-top > :first-child { grid-column: auto; }
  .q-note { display: none; }
  .queue li { grid-template-columns: 10px 1fr 16px; }
  .pg-head h1 { font-size: 22px; }
}
</style>

