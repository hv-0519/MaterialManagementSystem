<script setup>
import { ref, onMounted, computed } from 'vue'
import { RouterLink } from 'vue-router'
import {
  ClipboardList, ShieldCheck, CircleCheckBig, ShoppingCart,
  PackageCheck, Boxes, ArrowRight, Clock3, Check, CalendarDays
} from 'lucide-vue-next'
import TypeTag from '@/components/TypeTag.vue'
import { getDashboardSummary } from '@/services/dashboard'
import { useSession } from '@/composables/useSession'

const { user, role, roleKey } = useSession()
const data = ref(null)
const loadError = ref(false)

onMounted(async () => {
  try {
    data.value = await getDashboardSummary()
  } catch (error) {
    console.error('Dashboard loading failed:', error)
    loadError.value = true
  }
})

const greeting = computed(() => {
  const h = new Date().getHours()
  return h < 12 ? 'Good morning' : h < 17 ? 'Good afternoon' : 'Good evening'
})

const firstName = computed(() => user?.value?.name?.split(' ')[0] || user?.name?.split(' ')[0] || 'there')

const focus = computed(() => ({
  receiver: { title: 'Requests needing verification', to: '/requests', cta: 'Open requests' },
  supervisor: { title: 'Verified requests awaiting your decision', to: '/approval', cta: 'Review queue' },
  admin: { title: 'Requests across the workflow', to: '/requests', cta: 'View requests' }
}[roleKey.value] || { title: 'Requests across the workflow', to: '/requests', cta: 'View requests' }))

const cards = computed(() => {
  const c = data.value?.counts || {}
  return [
    { label: 'Approved requests', value: c.approved ?? 0, icon: CircleCheckBig, tone: 'green', to: '/requests' },
    { label: 'Purchase orders', value: c.poCreated ?? 0, icon: ShoppingCart, tone: 'blue', to: '/purchase-orders' },
    { label: 'Materials received', value: c.received ?? 0, icon: PackageCheck, tone: 'orange', to: '/receiving' },
    { label: 'Inventory items', value: data.value?.inventory?.skus ?? 0, icon: Boxes, tone: 'navy', to: '/inventory' }
  ]
})
</script>

<template>
  <div class="claude-dashboard">
    <header class="welcome">
      <div>
        <p class="eyebrow">{{ role.label }} workspace</p>
        <h1>{{ greeting }}, {{ firstName }}</h1>
        <p class="subtitle">Here's what needs attention across the material request pipeline today.</p>
      </div>
      <RouterLink to="/requests/new" class="new-request">
        <span>＋</span> New Material Request
      </RouterLink>
    </header>

    <div v-if="!data && !loadError" class="loading-panel">Loading dashboard data…</div>
    <div v-else-if="loadError" class="error-panel">
      Could not load dashboard data. Check that the backend is running, then refresh this page.
    </div>

    <template v-else-if="data">
      <section class="hero-grid">
        <article class="approval-hero">
          <p>Pending purchase approval</p>
          <strong>{{ data.counts.pendingApproval ?? 0 }}</strong>
          <div class="hero-foot">
            <span class="orange-dot"></span>
            Verified requests waiting for supervisor review
          </div>
          <div class="hero-line"><i></i></div>
          <RouterLink to="/approval" class="hero-link">Review queue <ArrowRight :size="16" /></RouterLink>
        </article>

        <div class="side-stats">
          <RouterLink to="/requests" class="side-stat">
            <div>
              <span>Pending verification</span>
              <strong>{{ data.counts.pendingVerification ?? 0 }}</strong>
            </div>
            <span class="icon-box orange"><Clock3 :size="19" /></span>
          </RouterLink>
          <RouterLink to="/approval" class="side-stat">
            <div>
              <span>Verified requests</span>
              <strong>{{ data.counts.verified ?? 0 }}</strong>
            </div>
            <span class="icon-box green"><Check :size="19" /></span>
          </RouterLink>
        </div>
      </section>

      <section class="metric-grid">
        <RouterLink v-for="card in cards" :key="card.label" :to="card.to" class="metric-card">
          <span class="icon-box" :class="card.tone"><component :is="card.icon" :size="19" /></span>
          <strong>{{ card.value }}</strong>
          <span class="metric-label">{{ card.label }}</span>
          <span class="metric-arrow"><ArrowRight :size="15" /></span>
        </RouterLink>
      </section>

      <section class="review-section">
        <div class="section-heading">
          <div>
            <h2>{{ focus.title }}</h2>
            <p>Live requests requiring attention in the workflow</p>
          </div>
          <RouterLink :to="focus.to" class="view-all">{{ focus.cta }} <ArrowRight :size="15" /></RouterLink>
        </div>

        <div v-if="data.attention?.length" class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Request No.</th>
                <th>Material</th>
                <th>Type</th>
                <th>Quantity</th>
                <th>Workflow status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="request in data.attention" :key="request.id">
                <td class="request-id">{{ request.id }}</td>
                <td class="material-cell">{{ request.material }}</td>
                <td><TypeTag :type="request.type" /></td>
                <td>{{ request.qty }}</td>
                <td>
                  <span class="status-pill" :class="'status-' + request.tone">
                    <i></i>{{ request.note }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else class="empty-state">
          <ClipboardList :size="25" />
          <strong>No requests need attention</strong>
          <span>There are currently no requests in the attention list.</span>
        </div>
      </section>

      <section class="inventory-note">
        <CalendarDays :size="18" />
        <span>Inventory overview</span>
        <strong>{{ data.inventory.skus }} tracked items</strong>
        <span class="stock-good">Healthy {{ data.inventory.healthy }}</span>
        <span class="stock-low">Low {{ data.inventory.low }}</span>
        <span class="stock-out">Out of stock {{ data.inventory.out }}</span>
        <RouterLink to="/inventory">View inventory <ArrowRight :size="14" /></RouterLink>
      </section>
    </template>
  </div>
</template>

<style scoped>
.claude-dashboard{display:flex;flex-direction:column;gap:24px;color:#192b40}
.welcome{display:flex;align-items:flex-end;justify-content:space-between;gap:18px;flex-wrap:wrap}
.eyebrow{font-size:12px;text-transform:uppercase;letter-spacing:.09em;color:#7a8798;font-weight:700;margin-bottom:8px}
.welcome h1{font-size:25px;font-weight:700;letter-spacing:-.035em;margin:0 0 6px}
.subtitle{font-size:13.5px;color:#758397;margin:0}
.new-request{display:inline-flex;align-items:center;gap:8px;padding:11px 15px;background:#c77d2e;color:white;border-radius:7px;font-size:13px;font-weight:650;text-decoration:none;box-shadow:0 2px 5px #c77d2e25}
.new-request span{font-size:19px;line-height:14px}
.hero-grid{display:grid;grid-template-columns:1.25fr 1fr;gap:16px}
.approval-hero{background:#203d59;color:white;border-radius:11px;padding:27px 29px;min-height:245px;display:flex;flex-direction:column;align-items:flex-start;position:relative;overflow:hidden}
.approval-hero:after{content:"";position:absolute;width:150px;height:150px;right:-45px;top:-45px;border-radius:50%;background:#c77d2e22;filter:blur(20px)}
.approval-hero>p{font-size:13px;color:#d4dfeb;margin:0 0 8px}
.approval-hero>strong{font-size:47px;line-height:1.2;font-weight:700;letter-spacing:-.04em}
.hero-foot{display:flex;align-items:center;gap:8px;font-size:12px;color:#d8e1eb;margin-top:7px}
.orange-dot{height:6px;width:6px;background:#e8a04e;border-radius:50%;flex:none}
.hero-line{height:2px;width:100%;background:#ffffff25;margin:24px 0 18px}
.hero-line i{display:block;width:25%;height:100%;background:#e8a04e}
.hero-link{display:inline-flex;align-items:center;gap:8px;padding:9px 12px;border:1px solid #ffffff35;background:#ffffff12;border-radius:6px;color:white;text-decoration:none;font-size:12px;font-weight:650}
.side-stats{display:grid;grid-template-rows:1fr 1fr;gap:12px}
.side-stat{background:white;border:1px solid #dfe5ec;border-radius:10px;padding:21px 18px;display:flex;align-items:center;justify-content:space-between;gap:15px;text-decoration:none;color:inherit;min-height:105px}
.side-stat>div{display:flex;flex-direction:column;gap:6px}
.side-stat span:not(.icon-box){font-size:12.5px;color:#69798e}
.side-stat strong{font-size:25px;line-height:1.2;color:#15263b}
.icon-box{width:37px;height:37px;border-radius:8px;display:inline-flex;align-items:center;justify-content:center;flex:none}
.orange{background:#fbf0e2;color:#c77d2e}.green{background:#e6f4ed;color:#26965d}.blue{background:#e8f1fa;color:#4188b7}.navy{background:#edf0f4;color:#294965}
.metric-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:13px}
.metric-card{position:relative;display:flex;flex-direction:column;align-items:flex-start;gap:8px;background:white;border:1px solid #dfe5ec;border-radius:10px;padding:17px 18px;text-decoration:none;color:inherit;min-height:143px;box-shadow:0 1px 2px #17283b08}
.metric-card>strong{font-size:27px;line-height:1.2;font-weight:700;letter-spacing:-.035em;margin-top:3px}
.metric-label{font-size:12.5px;color:#5e7087}
.metric-arrow{position:absolute;right:16px;top:18px;color:#99a7b8;opacity:0}
.metric-card:hover .metric-arrow{opacity:1}
.review-section{background:white;border:1px solid #dfe5ec;border-radius:10px;overflow:hidden}
.section-heading{display:flex;align-items:center;justify-content:space-between;gap:15px;padding:20px 20px 16px}
.section-heading h2{font-size:15px;font-weight:700;margin:0 0 5px}
.section-heading p{font-size:12px;color:#7b899b;margin:0}
.view-all{display:inline-flex;align-items:center;gap:6px;font-size:12px;color:#b46e27;text-decoration:none;font-weight:650;white-space:nowrap}
.table-wrap{width:100%;overflow-x:auto}
table{border-collapse:collapse;width:100%;font-size:12.5px;text-align:left}
thead{background:#f0f2f5;color:#748297}
th{font-size:11px;font-weight:650;padding:12px 17px;white-space:nowrap}
td{padding:14px 17px;border-top:1px solid #e4e8ee;color:#52647a;white-space:nowrap}
.request-id{font-family:var(--font-mono,monospace);font-size:11.5px;color:#4c6178}
.material-cell{font-weight:600;color:#1d3046}
.status-pill{display:inline-flex;align-items:center;gap:6px;max-width:280px;white-space:normal;font-size:11px;line-height:1.4;padding:5px 9px;border-radius:20px;background:#f0f2f5;color:#596a7e}
.status-pill i{width:6px;height:6px;border-radius:50%;background:currentColor;flex:none}
.status-warning{background:#fbf0e2;color:#b66d20}.status-info{background:#e8f1fa;color:#347da9}.status-violet{background:#f0eaff;color:#7550bb}
.empty-state{display:flex;flex-direction:column;align-items:center;gap:8px;padding:35px 15px;color:#8491a2}
.empty-state strong{font-size:13px;color:#33475d}.empty-state span{font-size:12px}
.inventory-note{display:flex;align-items:center;gap:13px;flex-wrap:wrap;padding:15px 17px;background:#fff;border:1px solid #dfe5ec;border-radius:9px;color:#718096;font-size:12px}
.inventory-note>svg{color:#c77d2e}.inventory-note>strong{color:#263c53}.stock-good{color:#278755}.stock-low{color:#b87826}.stock-out{color:#bf5555}
.inventory-note>a{margin-left:auto;display:inline-flex;align-items:center;gap:5px;color:#b46e27;text-decoration:none;font-weight:650}
.loading-panel,.error-panel{padding:25px;background:white;border:1px solid #dfe5ec;border-radius:9px;color:#69798e;font-size:13px}
.error-panel{color:#a33b3b;background:#fff8f7}
@media(max-width:1050px){.metric-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.hero-grid{grid-template-columns:1fr}}
@media(max-width:600px){.welcome h1{font-size:22px}.metric-grid{grid-template-columns:1fr 1fr}.metric-card{padding:14px;min-height:130px}.section-heading{align-items:flex-start;flex-direction:column}.inventory-note{gap:9px}.inventory-note>a{margin-left:0}.approval-hero{padding:22px}.side-stat{padding:16px}}
</style>
