<script setup>
import { ref, computed, onMounted } from 'vue'
import {
  Search, RefreshCw, CheckCircle2, Clock3, FileText, Package,
  Plus, X, CalendarDays, ArrowUpDown, SlidersHorizontal
} from 'lucide-vue-next'
import api from '@/services/api'

const requests = ref([])
const materials = ref([])
const loading = ref(true)
const loadingMaterials = ref(false)
const verifying = ref(null)
const saving = ref(false)
const error = ref('')
const success = ref('')
const search = ref('')
const activeStatus = ref('ALL')
const typeFilter = ref('ALL')
const dateFilter = ref('')
const sortDirection = ref('desc')
const showModal = ref(false)
const page = ref(1)
const pageSize = 8

const form = ref({
  material_id: '',
  quantity: '',
  request_type: 'NEW',
  required_date: '',
  remarks: ''
})

async function loadRequests() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.get('/material-requests')
    requests.value = Array.isArray(data) ? data : []
  } catch (err) {
    console.error(err)
    error.value = 'Unable to load material requests. Check that the backend is running.'
  } finally {
    loading.value = false
  }
}

async function loadMaterials() {
  loadingMaterials.value = true
  try {
    const { data } = await api.get('/materials')
    materials.value = Array.isArray(data) ? data : []
  } catch (err) {
    console.error(err)
    error.value = err.response?.data?.detail || 'Unable to load materials.'
  } finally {
    loadingMaterials.value = false
  }
}

async function verifyRequest(id) {
  verifying.value = id
  error.value = ''
  success.value = ''
  try {
    await api.put(`/material-requests/${id}/verify`)
    success.value = 'Material request verified successfully.'
    await loadRequests()
  } catch (err) {
    console.error(err)
    error.value = err.response?.data?.detail || 'Unable to verify this request.'
  } finally {
    verifying.value = null
  }
}

function openModal() {
  error.value = ''
  success.value = ''
  form.value = {
    material_id: '',
    quantity: '',
    request_type: 'NEW',
    required_date: '',
    remarks: ''
  }
  showModal.value = true
  if (!materials.value.length) loadMaterials()
}

function closeModal() {
  if (!saving.value) showModal.value = false
}

async function createRequest() {
  error.value = ''
  success.value = ''

  if (!form.value.material_id || !form.value.quantity || Number(form.value.quantity) <= 0) {
    error.value = 'Select a material and enter a quantity greater than zero.'
    return
  }

  saving.value = true
  try {
    await api.post('/material-requests', {
      material_id: Number(form.value.material_id),
      quantity: Number(form.value.quantity),
      request_type: form.value.request_type,
      required_date: form.value.required_date || null,
      remarks: form.value.remarks.trim() || null
    })
    showModal.value = false
    success.value = 'Material request created successfully.'
    activeStatus.value = 'ALL'
    search.value = ''
    typeFilter.value = 'ALL'
    dateFilter.value = ''
    page.value = 1
    await loadRequests()
  } catch (err) {
    console.error(err)
    error.value = err.response?.data?.detail || 'Unable to create the material request.'
  } finally {
    saving.value = false
  }
}

const statusOptions = [
  { label: 'All Requests', value: 'ALL' },
  { label: 'Pending Verification', value: 'PENDING_VERIFICATION' },
  { label: 'Verified', value: 'VERIFIED' },
  { label: 'Approved', value: 'APPROVED' },
  { label: 'Rejected', value: 'REJECTED' },
  { label: 'PO Created', value: 'PO_CREATED' },
  { label: 'Received', value: 'RECEIVED' }
]

function statusMatches(r, selected) {
  if (selected === 'ALL') return true
  const status = String(r.status || '').toUpperCase()
  const approval = String(r.approval_status || '').toUpperCase()

  if (selected === 'APPROVED') return approval === 'APPROVED' || status === 'APPROVED'
  if (selected === 'REJECTED') return approval === 'REJECTED' || status === 'REJECTED'
  if (selected === 'PO_CREATED') return status === 'PO_CREATED' || status === 'PO CREATED'
  if (selected === 'RECEIVED') return status === 'RECEIVED'
  return status === selected
}

const counts = computed(() => ({
  ALL: requests.value.length,
  PENDING_VERIFICATION: requests.value.filter(r => statusMatches(r, 'PENDING_VERIFICATION')).length,
  VERIFIED: requests.value.filter(r => statusMatches(r, 'VERIFIED')).length,
  APPROVED: requests.value.filter(r => statusMatches(r, 'APPROVED')).length,
  REJECTED: requests.value.filter(r => statusMatches(r, 'REJECTED')).length,
  PO_CREATED: requests.value.filter(r => statusMatches(r, 'PO_CREATED')).length,
  RECEIVED: requests.value.filter(r => statusMatches(r, 'RECEIVED')).length
}))

const filteredRequests = computed(() => {
  const q = search.value.trim().toLowerCase()
  const result = requests.value.filter(r => {
    const matchesSearch = !q || [
      r.request_no, r.material_name, r.request_type, r.status,
      r.created_by_username, r.remarks
    ].filter(Boolean).some(v => String(v).toLowerCase().includes(q))

    const matchesStatus = statusMatches(r, activeStatus.value)
    const matchesType = typeFilter.value === 'ALL' ||
      String(r.request_type || '').toUpperCase() === typeFilter.value
    const matchesDate = !dateFilter.value || String(r.required_date || '').slice(0, 10) === dateFilter.value

    return matchesSearch && matchesStatus && matchesType && matchesDate
  })

  return result.sort((a, b) => {
    const compare = String(a.created_at || a.request_no || '').localeCompare(
      String(b.created_at || b.request_no || '')
    )
    return sortDirection.value === 'desc' ? -compare : compare
  })
})

const totalPages = computed(() => Math.max(1, Math.ceil(filteredRequests.value.length / pageSize)))
const paginatedRequests = computed(() => {
  const start = (page.value - 1) * pageSize
  return filteredRequests.value.slice(start, start + pageSize)
})

function setStatus(status) {
  activeStatus.value = status
  page.value = 1
}

function clearFilters() {
  search.value = ''
  activeStatus.value = 'ALL'
  typeFilter.value = 'ALL'
  dateFilter.value = ''
  page.value = 1
}

function statusLabel(status) {
  const labels = {
    PENDING_VERIFICATION: 'Pending Verification',
    VERIFIED: 'Verified',
    APPROVED: 'Approved',
    REJECTED: 'Rejected',
    PO_CREATED: 'PO Created',
    RECEIVED: 'Received'
  }
  return labels[String(status || '').toUpperCase()] || status || 'Unknown'
}

function statusClass(status) {
  const value = String(status || '').toUpperCase()
  if (value === 'PENDING_VERIFICATION') return 'pending'
  if (value === 'VERIFIED' || value === 'APPROVED') return 'verified'
  if (value === 'REJECTED') return 'rejected'
  if (value === 'RECEIVED') return 'received'
  return 'other'
}

function formatDate(value) {
  if (!value) return '—'
  const date = new Date(String(value).slice(0, 10) + 'T00:00:00')
  if (Number.isNaN(date.getTime())) return String(value)
  return date.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })
}

onMounted(loadRequests)
</script>

<template>
  <div class="requests-page">
    <header class="page-head">
      <div>
        <p class="eyebrow">PROCUREMENT WORKFLOW</p>
        <h1>Material Requests</h1>
        <p class="sub">Track, review and verify material requirements across the procurement workflow.</p>
      </div>
      <div class="head-actions">
        <button class="refresh-btn" @click="loadRequests" :disabled="loading" title="Refresh requests">
          <RefreshCw :size="16" :class="{ spin: loading }" /> Refresh
        </button>
        <button class="add-btn" @click="openModal">
          <Plus :size="17" /> Add Material Request
        </button>
      </div>
    </header>

    <div v-if="error" class="notice error-box">
      <span>{{ error }}</span>
      <button @click="error = ''" aria-label="Dismiss error"><X :size="16" /></button>
    </div>
    <div v-if="success" class="notice success-box">
      <CheckCircle2 :size="17" /><span>{{ success }}</span>
      <button @click="success = ''" aria-label="Dismiss message"><X :size="16" /></button>
    </div>


    <section class="panel">
      <div class="panel-head">
        <div>
          <h2>Request Queue</h2>
          <p>Live records from your material management database</p>
        </div>
        <div class="result-count">{{ filteredRequests.length }} requests</div>
      </div>

      <div class="status-tabs">
        <button v-for="item in statusOptions" :key="item.value"
          :class="{ active: activeStatus === item.value }"
          @click="setStatus(item.value)">
          {{ item.label }} <span class="tab-count">{{ counts[item.value] }}</span>
        </button>
      </div>

      <div class="filter-panel">
        <label class="search">
          <Search :size="17" />
          <input v-model="search" type="search" placeholder="Search request number or material..." @input="page = 1" />
        </label>
        <label class="filter-control">
          <SlidersHorizontal :size="15" />
          <select v-model="typeFilter" @change="page = 1" aria-label="Filter by request type">
            <option value="ALL">All types</option>
            <option value="NEW">New</option>
            <option value="ADVANCE">Advance</option>
          </select>
        </label>
        <label class="filter-control date-filter">
          <CalendarDays :size="15" />
          <input type="date" v-model="dateFilter" @change="page = 1" aria-label="Filter by required date" />
        </label>
        <button class="clear-btn" @click="clearFilters">Clear filters</button>
      </div>

      <div v-if="loading" class="loading">
        <RefreshCw :size="22" class="spin" />
        <strong>Loading material requests...</strong>
      </div>

      <div v-else-if="!filteredRequests.length" class="empty">
        <Package :size="30" />
        <strong>No material requests found</strong>
        <span>Try changing your filters, or add a material request.</span>
        <button class="add-btn small" @click="openModal"><Plus :size="15" /> Add Material Request</button>
      </div>

      <div v-else class="table-wrap">
        <table>
          <thead>
            <tr>
              <th><button class="sort-btn" @click="sortDirection = sortDirection === 'desc' ? 'asc' : 'desc'">Request No. <ArrowUpDown :size="13" /></button></th>
              <th>Material</th>
              <th>Quantity</th>
              <th>Type</th>
              <th>Required Date</th>
              <th>Created By</th>
              <th>Status</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="request in paginatedRequests" :key="request.id">
              <td><span class="request-no">{{ request.request_no }}</span></td>
              <td>
                <div class="material">
                  <span class="material-icon"><Package :size="16" /></span>
                  <div><strong>{{ request.material_name || 'Material' }}</strong><small>{{ request.unit || 'Unit not specified' }}</small></div>
                </div>
              </td>
              <td class="quantity">{{ request.quantity }} {{ request.unit || '' }}</td>
              <td><span class="type" :class="String(request.request_type || '').toLowerCase()">{{ request.request_type }}</span></td>
              <td>{{ formatDate(request.required_date) }}</td>
              <td>{{ request.created_by_username || '—' }}</td>
              <td><span class="status" :class="statusClass(request.status)"><i />{{ statusLabel(request.status) }}</span></td>
              <td>
                <button v-if="request.status === 'PENDING_VERIFICATION'" class="verify-btn"
                  :disabled="verifying === request.id" @click="verifyRequest(request.id)">
                  <RefreshCw v-if="verifying === request.id" :size="14" class="spin" />
                  <CheckCircle2 v-else :size="14" />
                  {{ verifying === request.id ? 'Verifying...' : 'Verify' }}
                </button>
                <span v-else class="verified-label"><CheckCircle2 :size="15" /> {{ statusLabel(request.status) }}</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <footer v-if="!loading && filteredRequests.length" class="pagination">
        <span>Showing {{ (page - 1) * pageSize + 1 }}–{{ Math.min(page * pageSize, filteredRequests.length) }} of {{ filteredRequests.length }} requests</span>
        <div class="page-buttons">
          <button :disabled="page <= 1" @click="page--">Previous</button>
          <span>Page {{ page }} of {{ totalPages }}</span>
          <button :disabled="page >= totalPages" @click="page++">Next</button>
        </div>
      </footer>
    </section>

    <div v-if="showModal" class="modal-backdrop" @click.self="closeModal">
      <section class="request-modal" role="dialog" aria-modal="true" aria-labelledby="modal-title">
        <header class="modal-head">
          <div><p class="eyebrow">PROCUREMENT WORKFLOW</p><h2 id="modal-title">Add Material Request</h2><p>Create a new requirement for receiver verification.</p></div>
          <button class="close-btn" @click="closeModal" :disabled="saving" aria-label="Close"><X :size="20" /></button>
        </header>
        <form @submit.prevent="createRequest">
          <div v-if="error" class="modal-error">{{ error }}</div>
          <div class="form-grid">
            <label class="field full">
              <span>Material <b>*</b></span>
              <select v-model="form.material_id" required :disabled="loadingMaterials">
                <option value="" disabled>{{ loadingMaterials ? 'Loading materials...' : 'Select a material' }}</option>
                <option v-for="material in materials" :key="material.id" :value="String(material.id)">
                  {{ material.material_name }}{{ material.unit ? ' (' + material.unit + ')' : '' }}
                </option>
              </select>
            </label>
            <label class="field">
              <span>Quantity <b>*</b></span>
              <input v-model="form.quantity" type="number" min="0.01" step="any" placeholder="Enter quantity" required />
            </label>
            <label class="field">
              <span>Request Type <b>*</b></span>
              <select v-model="form.request_type" required>
                <option value="NEW">New Request</option>
                <option value="ADVANCE">Advance Request</option>
              </select>
            </label>
            <label class="field full">
              <span>Required Date</span>
              <input v-model="form.required_date" type="date" />
            </label>
            <label class="field full">
              <span>Remarks</span>
              <textarea v-model="form.remarks" rows="3" maxlength="1000" placeholder="Add any notes about this requirement..."></textarea>
            </label>
          </div>
          <div class="modal-actions">
            <button type="button" class="cancel-btn" @click="closeModal" :disabled="saving">Cancel</button>
            <button type="submit" class="add-btn" :disabled="saving || loadingMaterials || !materials.length">
              <RefreshCw v-if="saving" :size="16" class="spin" />
              <Plus v-else :size="16" />
              {{ saving ? 'Creating...' : 'Create Request' }}
            </button>
          </div>
        </form>
      </section>
    </div>
  </div>
</template>

<style scoped>
.requests-page{display:flex;flex-direction:column;gap:17px;color:var(--c-text)}
.page-head{display:flex;align-items:flex-end;justify-content:space-between;gap:18px;flex-wrap:wrap}
.eyebrow{font-size:11px;letter-spacing:.1em;font-weight:750;color:var(--c-muted);margin:0 0 7px}
.page-head h1{font-size:28px;font-weight:750;letter-spacing:-.035em;margin:0 0 7px}
.sub{font-size:14px;color:var(--c-muted);margin:0}
.head-actions{display:flex;gap:9px;align-items:center}
.refresh-btn,.add-btn,.verify-btn,.cancel-btn,.clear-btn,.page-buttons button{display:inline-flex;align-items:center;justify-content:center;gap:8px;border-radius:7px;padding:10px 13px;font-size:13px;font-weight:700;cursor:pointer;transition:background .2s,border-color .2s,transform .2s}
.refresh-btn{border:1px solid var(--c-border);background:var(--c-surface);color:var(--c-text-2)}
.refresh-btn:hover{background:var(--c-surface-2)}
.add-btn{border:1px solid #c77d2e;background:#c77d2e;color:#fff}
.add-btn:hover:not(:disabled){background:#ae6823;transform:translateY(-1px)}
.add-btn:disabled,.refresh-btn:disabled{opacity:.6;cursor:wait}
.add-btn.small{margin-top:8px;padding:8px 11px}
.summary-row{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}
.summary-card{display:flex;align-items:center;gap:13px;text-align:left;padding:18px;background:var(--c-surface);border:1px solid var(--c-border);border-radius:10px;box-shadow:var(--shadow-xs);cursor:pointer;color:var(--c-text);transition:border-color .2s,transform .2s}
.summary-card:hover{transform:translateY(-2px);border-color:var(--c-border-strong)}
.summary-card.selected{border-color:#c77d2e}
.summary-copy{display:flex;flex-direction:column;gap:4px}
.summary-copy>span{font-size:13px;color:var(--c-muted);font-weight:600}
.summary-copy strong{font-size:27px;font-weight:750;line-height:1.2}
.summary-icon{width:39px;height:39px;border-radius:9px;display:grid;place-items:center;flex:none}
.summary-icon.warning{color:var(--c-warning);background:var(--c-warning-bg)}
.summary-icon.success{color:var(--c-success);background:var(--c-success-bg)}
.summary-icon.info{color:var(--c-info);background:var(--c-info-bg)}
.panel{background:var(--c-surface);border:1px solid var(--c-border);border-radius:10px;box-shadow:var(--shadow-xs);overflow:hidden}
.panel-head{display:flex;align-items:center;justify-content:space-between;gap:14px;padding:20px 21px 17px}
.panel-head h2{font-size:17px;font-weight:750;margin:0 0 4px}
.panel-head p{font-size:13px;color:var(--c-muted);margin:0}
.result-count{font-size:12px;font-weight:700;color:var(--c-muted);background:var(--c-surface-2);padding:7px 10px;border-radius:6px;white-space:nowrap}
.status-tabs{display:flex;gap:3px;overflow-x:auto;padding:0 18px;border-bottom:1px solid var(--c-border)}
.status-tabs button{display:flex;align-items:center;gap:7px;white-space:nowrap;padding:13px 11px 12px;border:0;border-bottom:2px solid transparent;background:transparent;color:var(--c-muted);font:inherit;font-size:12px;font-weight:650;cursor:pointer}
.status-tabs button:hover{color:var(--c-text)}
.status-tabs button.active{color:#c77d2e;border-bottom-color:#c77d2e}
.tab-count{font-size:10px;padding:2px 6px;border-radius:5px;background:var(--c-surface-2);color:var(--c-muted)}
.status-tabs button.active .tab-count{background:#f8ead9;color:#a8621d}
.filter-panel{display:flex;align-items:center;gap:10px;flex-wrap:wrap;padding:12px 18px;border-bottom:1px solid var(--c-border);background:var(--c-surface)}
.search{display:flex;align-items:center;gap:9px;width:min(340px,100%);height:39px;padding:0 11px;border:1px solid var(--c-border);border-radius:7px;color:var(--c-muted);background:var(--c-bg)}
.search:focus-within,.filter-control:focus-within{border-color:#c77d2e;box-shadow:0 0 0 3px #c77d2e20}
.search input{width:100%;min-width:0;border:0;outline:0;background:transparent;color:var(--c-text);font:inherit;font-size:13px}
.filter-control{display:flex;align-items:center;gap:7px;height:39px;padding:0 10px;border:1px solid var(--c-border);border-radius:7px;color:var(--c-muted);background:var(--c-bg)}
.filter-control select,.filter-control input{max-width:160px;border:0;outline:0;background:transparent;color:var(--c-text);font:inherit;font-size:12px}
.clear-btn{padding:8px 10px;border:0;background:transparent;color:var(--c-muted);font-size:12px}
.clear-btn:hover{color:#c77d2e}
.table-wrap{width:100%;overflow-x:auto}
table{width:100%;min-width:1000px;border-collapse:collapse;text-align:left}
th{padding:12px 15px;background:var(--c-surface-2);border-bottom:1px solid var(--c-border);color:var(--c-muted);font-size:11px;font-weight:750;text-transform:uppercase;letter-spacing:.045em;white-space:nowrap}
td{padding:14px 15px;border-bottom:1px solid var(--c-border);font-size:13px;color:var(--c-text-2);white-space:nowrap}
tbody tr:hover{background:var(--c-surface-2)}
.request-no{font-family:var(--font-mono,monospace);font-size:12px;font-weight:750;color:var(--c-text)}
.material{display:flex;align-items:center;gap:9px}
.material-icon{width:33px;height:33px;border-radius:8px;display:grid;place-items:center;color:#c77d2e;background:#fbf0e2;flex:none}
.material div{display:flex;flex-direction:column;gap:3px}
.material strong{font-weight:700;color:var(--c-text)}
.material small{font-size:11px;color:var(--c-muted)}
.quantity{font-weight:700}
.type,.status{display:inline-flex;align-items:center;gap:6px;font-size:11px;font-weight:750;border-radius:20px;padding:5px 9px}
.type.new{color:var(--c-info);background:var(--c-info-bg)}
.type.advance{color:var(--c-violet);background:var(--c-violet-bg)}
.status.pending{color:var(--c-warning);background:var(--c-warning-bg)}
.status.verified,.status.received{color:var(--c-success);background:var(--c-success-bg)}
.status.rejected{color:var(--c-danger);background:var(--c-danger-bg)}
.status.other{color:var(--c-muted);background:var(--c-surface-2)}
.status i{width:6px;height:6px;border-radius:50%;background:currentColor;flex:none}
.verify-btn{padding:7px 10px;color:white;background:#c77d2e;border:1px solid #c77d2e;font-size:12px}
.verify-btn:hover:not(:disabled){background:#ae6823}
.verify-btn:disabled{opacity:.6;cursor:wait}
.verified-label{display:inline-flex;align-items:center;gap:5px;color:var(--c-success);font-size:12px;font-weight:650}
.sort-btn{display:inline-flex;align-items:center;gap:6px;border:0;background:transparent;color:inherit;font:inherit;text-transform:inherit;letter-spacing:inherit;cursor:pointer;padding:0}
.pagination{display:flex;justify-content:space-between;align-items:center;gap:12px;padding:13px 18px;color:var(--c-muted);font-size:12px;flex-wrap:wrap}
.page-buttons{display:flex;align-items:center;gap:10px}
.page-buttons button{padding:7px 10px;border:1px solid var(--c-border);background:var(--c-surface);color:var(--c-text-2);font-size:12px}
.page-buttons button:disabled{opacity:.4;cursor:not-allowed}
.loading,.empty{min-height:240px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px;color:var(--c-muted);font-size:13px}
.empty strong{color:var(--c-text);font-size:15px}
.notice{display:flex;align-items:center;gap:9px;padding:12px 14px;border:1px solid;border-radius:8px;font-size:13px;font-weight:600}
.notice button{margin-left:auto;display:grid;place-items:center;border:0;background:transparent;color:inherit;cursor:pointer}
.error-box{color:var(--c-danger);background:var(--c-danger-bg);border-color:var(--c-danger)}
.success-box{color:var(--c-success);background:var(--c-success-bg);border-color:var(--c-success)}
.spin{animation:spin .8s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.modal-backdrop{position:fixed;inset:0;z-index:1000;background:#101923a8;display:flex;align-items:center;justify-content:center;padding:20px;backdrop-filter:blur(3px)}
.request-modal{width:min(560px,100%);max-height:calc(100vh - 40px);overflow-y:auto;background:var(--c-surface);border:1px solid var(--c-border);border-radius:12px;box-shadow:var(--shadow-lg);color:var(--c-text)}
.modal-head{display:flex;justify-content:space-between;align-items:flex-start;gap:14px;padding:23px 24px 19px;border-bottom:1px solid var(--c-border)}
.modal-head h2{font-size:21px;font-weight:750;margin:0 0 5px}
.modal-head p:not(.eyebrow){font-size:13px;color:var(--c-muted);margin:0}
.close-btn{display:grid;place-items:center;width:34px;height:34px;border:1px solid var(--c-border);border-radius:7px;background:var(--c-surface);color:var(--c-muted);cursor:pointer}
.form-grid{display:grid;grid-template-columns:1fr 1fr;gap:17px;padding:22px 24px}
.field{display:flex;flex-direction:column;gap:7px;min-width:0}
.field.full{grid-column:1/-1}
.field>span{font-size:13px;font-weight:700;color:var(--c-text-2)}
.field b{color:#c77d2e}
.field input,.field select,.field textarea{width:100%;box-sizing:border-box;padding:10px 11px;border:1px solid var(--c-border);border-radius:7px;background:var(--c-bg);color:var(--c-text);font:inherit;font-size:13px;outline:0}
.field input:focus,.field select:focus,.field textarea:focus{border-color:#c77d2e;box-shadow:0 0 0 3px #c77d2e20}
.field textarea{resize:vertical}
.modal-actions{display:flex;justify-content:flex-end;gap:9px;padding:16px 24px 22px;border-top:1px solid var(--c-border)}
.cancel-btn{border:1px solid var(--c-border);background:var(--c-surface);color:var(--c-text-2)}
.cancel-btn:hover{background:var(--c-surface-2)}
.modal-error{margin:16px 24px 0;padding:10px 12px;border-radius:7px;background:var(--c-danger-bg);color:var(--c-danger);font-size:12px}
@media(max-width:1000px){.summary-row{grid-template-columns:1fr 1fr}.summary-card:last-child{grid-column:1/-1}.filter-panel{align-items:stretch}.search{width:100%;flex-basis:100%}}
@media(max-width:650px){.requests-page{gap:16px}.page-head{align-items:flex-start;flex-direction:column}.page-head h1{font-size:24px}.head-actions{width:100%}.head-actions button{flex:1}.summary-row{grid-template-columns:1fr}.summary-card:last-child{grid-column:auto}.panel-head{padding:16px;align-items:flex-start}.status-tabs{padding:0 10px}.filter-panel{padding:12px}.filter-control{flex:1;min-width:0}.filter-control select,.filter-control input{width:100%;min-width:0}.pagination{padding:13px}.form-grid{grid-template-columns:1fr;padding:18px}.field.full{grid-column:auto}.modal-head{padding:19px}.modal-actions{padding:15px 18px 19px}}

/* Material type dropdown: readable dark options */
.requests-page .filter-control select {
  color-scheme: dark !important;
  background: #111a24 !important;
  color: #e8edf5 !important;
}

.requests-page .filter-control select option {
  background-color: #1b2735 !important;
  color: #e8edf5 !important;
}
</style>


/* Fix native filter dropdown contrast */
.requests-page .filter-control select {
  color-scheme: dark;
  background-color: #111a24;
  color: #e8edf5;
}

.requests-page .filter-control select option {
  background-color: #1b2735;
  color: #e8edf5;
}

.requests-page .filter-control select option:checked {
  background-color: #30465d;
  color: #ffffff;
}

